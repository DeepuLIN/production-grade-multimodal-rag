import fitz
import base64
from openai import OpenAI
import os
import re

from app.storage.s3 import upload_image_file, upload_table_image_file


client = OpenAI(
    api_key=os.getenv("OPEN_ROUTER_API_KEY"),
    base_url=os.getenv("OPEN_ROUTER_BASE_URL", "https://openrouter.ai/api/v1"),
)


def extract_embedded_pdf_images(pdf_bytes: bytes, document_id: str):
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")

    results = []
    image_index = 0

    for page_index in range(len(doc)):
        page = doc[page_index]
        page_number = page_index + 1

        images = page.get_images(full=True)

        if not images:
            continue

        # Store one page preview only if the page contains real embedded images.
        pix = page.get_pixmap(dpi=200)
        image_bytes = pix.tobytes("png")

        image_s3_key = upload_image_file(
            document_id=document_id,
            page=page_number,
            image_index=image_index,
            file_bytes=image_bytes,
        )

        image_index += 1

        page_text = page.get_text("text") or ""

        caption = (
            f"Page {page_number} contains {len(images)} embedded image(s)/figure(s).\n\n"
            f"Visible/nearby page text:\n{page_text[:1200]}"
        )

        figure_number = extract_figure_number(page_text)

        print(
            f"🖼️ EMBEDDED IMAGE PAGE STORED | "
            f"page={page_number} | "
            f"embedded_images={len(images)} | "
            f"key={image_s3_key}"
        )

        results.append(
            {
                "caption": caption,
                "page": page_number,
                "image_s3_key": image_s3_key,
                "chunk_type": "figure",
                "figure_number": figure_number,
            }
        )

    doc.close()
    return results




def extract_figure_number(caption: str | None) -> int | None:
    if not caption:
        return None

    lowered = caption.lower()

    if (
        "not visible" in lowered
        or "no visible figure" in lowered
        or "no visible figures" in lowered
    ):
        return None

    match = re.search(
        r"\b(?:Figure|Fig\.?)\s*(\d+)\b",
        caption,
        flags=re.IGNORECASE,
    )

    if not match:
        return None

    return int(match.group(1))



# -----------------------------
# RENDER PAGE AS IMAGE
# -----------------------------
def render_pages(pdf_bytes: bytes):
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")

    pages = []

    for page_index in range(len(doc)):
        page = doc[page_index]

        pix = page.get_pixmap(dpi=200)
        img_bytes = pix.tobytes("png")

        pages.append(
            {
                "page": page_index + 1,
                "image_bytes": img_bytes,
            }
        )

    return pages


# -----------------------------
# CONVERT TABLE ROWS TO MARKDOWN
# -----------------------------
def table_rows_to_markdown(rows: list[list]) -> str:
    if not rows:
        return ""

    cleaned_rows = [
        [str(cell or "").replace("\n", " ").strip() for cell in row]
        for row in rows
    ]

    header = cleaned_rows[0]
    body = cleaned_rows[1:]

    if not header:
        return ""

    markdown = "| " + " | ".join(header) + " |\n"
    markdown += "| " + " | ".join(["---"] * len(header)) + " |\n"

    for row in body:
        while len(row) < len(header):
            row.append("")

        markdown += "| " + " | ".join(row[: len(header)]) + " |\n"

    return markdown


# -----------------------------
# DETECT REAL TABLE LABEL FROM PAGE TEXT
# -----------------------------
def detect_visible_table_label(
    page_text: str,
    fallback_caption: str,
) -> str:
    if not page_text:
        return fallback_caption

    matches = re.findall(
        r"(Table\s+\d+[:.\-\s][\s\S]{0,300}?)(?=\n[A-Z][a-z]|\n\d+\.|\nFigure\s+\d+|\Z)",
        page_text,
        flags=re.IGNORECASE,
    )

    if matches:
        return " ".join(matches[0].split())

    simple_matches = re.findall(
        r"(Table\s+\d+[:.\-\s][^\n]{0,200})",
        page_text,
        flags=re.IGNORECASE,
    )

    if simple_matches:
        return " ".join(simple_matches[0].split())

    return fallback_caption


# -----------------------------
# EXTRACT TABLES
# -----------------------------
def extract_pdf_tables(pdf_bytes: bytes, document_id: str):
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")

    results = []

    for page_index in range(len(doc)):
        page = doc[page_index]
        page_number = page_index + 1
        page_text = page.get_text("text") or ""

        try:
            table_finder = page.find_tables()
            tables = table_finder.tables or []

            for table_index, table in enumerate(tables):
                try:
                    rows = table.extract()
                    table_markdown = table_rows_to_markdown(rows)

                    pix = page.get_pixmap(dpi=200)
                    table_bytes = pix.tobytes("png")

                  

                    table_s3_key = upload_table_image_file(
                        document_id=document_id,
                        page=page_number,
                        table_index=table_index,
                        file_bytes=table_bytes,
                    )

                    fallback_caption = (
                        f"Extracted table {table_index + 1} on page {page_number}"
                    )

                    caption = detect_visible_table_label(
                        page_text=page_text,
                        fallback_caption=fallback_caption,
                    )

                    print(
                        f"📊 TABLE STORED | "
                        f"page={page_number} | "
                        f"table={table_index} | "
                        f"caption={caption[:100]} | "
                        f"key={table_s3_key}"
                    )

                    results.append(
                        {
                            "chunk_type": "table",
                            "page": page_number,
                            "table_index": table_index,
                            "caption": caption,
                            "table_markdown": table_markdown,
                            "image_s3_key": table_s3_key,
                        }
                    )

                except Exception as table_error:
                    print(
                        f"⚠️ table extraction failed | "
                        f"page={page_number} | "
                        f"table={table_index} | "
                        f"error={table_error}"
                    )

        except Exception as e:
            print(f"⚠️ no tables extracted on page {page_number}: {e}")

    return results


# -----------------------------
# CAPTION PAGE IMAGE
# -----------------------------
def caption_image(image_bytes: bytes) -> str:
    image_base64 = base64.b64encode(image_bytes).decode()

    response = client.chat.completions.create(
        model="openai/gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are creating visual metadata for a multimodal RAG system. "
                    "Extract visible figure numbers, table numbers, equation numbers, captions, titles, labels, diagrams, charts, and page layout. "
                    "Be precise and do not invent figure numbers that are not visible."
                ),
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": (
                            "Describe this PDF page for visual RAG indexing.\n\n"
                            "Return structured Markdown with exactly these sections:\n\n"
                            "### Figures\n"
                            "- List every visible figure number such as Figure 1, Figure 2, Fig. 3, etc.\n"
                            "- Include the figure title/caption if visible.\n"
                            "- Describe what each figure shows.\n\n"
                            "### Tables\n"
                            "- List every visible table number such as Table 1, Table 2, etc.\n"
                            "- Include the table title/caption if visible.\n\n"
                            "### Equations\n"
                            "- List every visible equation number such as Equation (1), (2), (3), etc.\n"
                            "- Briefly describe what the equation represents.\n"
                            "- If possible, rewrite visible equations in clean LaTeX.\n\n"
                            "### Page Summary\n"
                            "- Briefly summarize the page content for retrieval.\n\n"
                            "Important: If a figure/table/equation number is visible, mention it explicitly."
                        ),
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{image_base64}"
                        },
                    },
                ],
            },
        ],
        temperature=0.1,
    )

    return response.choices[0].message.content or ""


# -----------------------------
# MAIN PIPELINE
# -----------------------------
def process_pdf_images(
    pdf_bytes: bytes,
    document_id: str,
    caption_pages: bool = False,
):
    results = []

    # Always extract/crop tables cheaply with PyMuPDF
    table_results = extract_pdf_tables(
        pdf_bytes=pdf_bytes,
        document_id=document_id,
    )

    print(f"📊 TABLES FOUND: {len(table_results)}")
    results.extend(table_results)

    # Skip expensive page-level LLM captioning by default
    if not caption_pages:
        embedded_image_results = extract_embedded_pdf_images(
            pdf_bytes=pdf_bytes,
            document_id=document_id,
        )

        print(f"🖼️ EMBEDDED IMAGE PAGES FOUND: {len(embedded_image_results)}")

        results.extend(embedded_image_results)
        return results

    pages = render_pages(pdf_bytes)

    for image_index, p in enumerate(pages):
        try:
            image_s3_key = upload_image_file(
                document_id=document_id,
                page=p["page"],
                image_index=image_index,
                file_bytes=p["image_bytes"],
            )

            print(
                f"🖼️ IMAGE STORED | page={p['page']} | key={image_s3_key}"
            )

            caption = caption_image(p["image_bytes"])

            print(
                f"📝 IMAGE CAPTION | page={p['page']} | "
                f"{(caption or '')[:120]}"
            )
            figure_number = extract_figure_number(caption)
            results.append(
                {
                    "caption": caption or "",
                    "page": p["page"],
                    "image_s3_key": image_s3_key,
                    "chunk_type": "figure",
                    "figure_number": figure_number,
                }
            )

        except Exception as e:
            print("❌ vision error:", e)

    return results




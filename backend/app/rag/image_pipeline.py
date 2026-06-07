import fitz
import base64
from openai import OpenAI
import os

from app.storage.s3 import upload_image_file


client = OpenAI(
    api_key=os.getenv("OPEN_ROUTER_API_KEY"),
    base_url=os.getenv("OPEN_ROUTER_BASE_URL", "https://openrouter.ai/api/v1"),
)


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
# CAPTION
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
def process_pdf_images(pdf_bytes: bytes, document_id: str):
    pages = render_pages(pdf_bytes)

    results = []

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

            results.append(
                {
                    "caption": caption or "",
                    "page": p["page"],
                    "image_s3_key": image_s3_key,
                    "chunk_type": "figure",
                }
            )

        except Exception as e:
            print("❌ vision error:", e)

    return results
import base64
import fitz

from openai import OpenAI
from app.core.config import (
    MAX_PDF_PAGES,
    OCR_MODEL,
    OPEN_ROUTER_API_KEY,
    OPEN_ROUTER_BASE_URL,
)

from app.rag.math_normalizer import normalize_math


def extract_text_with_pymupdf(file_bytes: bytes) -> str:
    pdf = fitz.open(stream=file_bytes, filetype="pdf")
    pages = []

    for page_index, page in enumerate(pdf):
        if page_index >= MAX_PDF_PAGES:
            break

        text = page.get_text("text") or ""

        if text.strip():
            pages.append(f"\n\n## Page {page_index + 1}\n\n{text.strip()}")

    pdf.close()
    return "\n".join(pages).strip()


def is_good_pdf_text(text: str) -> bool:
    if not text:
        return False

    clean = text.strip()

    if len(clean) < 500:
        return False

    alpha_count = sum(c.isalpha() for c in clean)
    alpha_ratio = alpha_count / max(len(clean), 1)

    return alpha_ratio > 0.25


async def extract_text_from_bytes(
    file_bytes: bytes,
    filename: str,
    content_type: str,
) -> str:
    if not file_bytes:
        raise ValueError("No file bytes provided")

    is_pdf = content_type == "application/pdf" or filename.lower().endswith(".pdf")

    if is_pdf:
        cheap_text = extract_text_with_pymupdf(file_bytes)

        if is_good_pdf_text(cheap_text):
            print("✅ Using cheap PyMuPDF text extraction")
            return normalize_math(cheap_text)

        print("⚠️ PyMuPDF text weak/empty. Falling back to LLM OCR.")

    if not OPEN_ROUTER_API_KEY:
        raise RuntimeError("OPEN_ROUTER_API_KEY is missing")

    content_items = [
        {
            "type": "text",
            "text": (
               "IMPORTANT:\n"
               "- Convert ALL math into LaTeX ($...$ or $$...$$)\n"
               "- Never use square brackets for equations\n"
               "- Preserve structure (tables, headings, diagrams)\n"
               "- Preserve COMPLETE equations from beginning to end\n"
               "- If an equation spans multiple lines, combine it into one complete LaTeX block\n"
               "- Never leave dangling LaTeX delimiters such as \\left or \\right without brackets\n"
               "- Output clean Markdown only\n"
            ),
        }
    ]

    if is_pdf:
        pdf = fitz.open(stream=file_bytes, filetype="pdf")

        for page_index, page in enumerate(pdf):
            if page_index >= MAX_PDF_PAGES:
                break

            pix = page.get_pixmap(dpi=200)
            image_bytes = pix.tobytes("png")
            image_base64 = base64.b64encode(image_bytes).decode("utf-8")

            content_items.append(
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/png;base64,{image_base64}"
                    },
                }
            )

        pdf.close()

    else:
        safe_content_type = content_type or "image/jpeg"
        image_base64 = base64.b64encode(file_bytes).decode("utf-8")

        content_items.append(
            {
                "type": "image_url",
                "image_url": {
                    "url": f"data:{safe_content_type};base64,{image_base64}"
                },
            }
        )

    client = OpenAI(
        api_key=OPEN_ROUTER_API_KEY,
        base_url=OPEN_ROUTER_BASE_URL,
        timeout=60,
    )

    response = client.chat.completions.create(
        model=OCR_MODEL,
        stream=False,
        max_tokens=4000,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a high-accuracy OCR engine.\n"
                    "STRICT RULES:\n"
                    "- NEVER output equations in [ ]\n"
                    "- ALWAYS use LaTeX\n"
                    "- Preserve reading order\n"
                    "- Output structured Markdown only\n"
                ),
            },
            {
                "role": "user",
                "content": content_items,
            },
        ],
    )

    output = response.choices[0].message.content or ""
    return normalize_math(output)
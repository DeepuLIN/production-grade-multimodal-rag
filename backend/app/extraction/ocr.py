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


async def extract_text_from_bytes(
    file_bytes: bytes,
    filename: str,
    content_type: str,
) -> str:

    if not OPEN_ROUTER_API_KEY:
        raise RuntimeError("OPEN_ROUTER_API_KEY is missing")

    if not file_bytes:
        raise ValueError("No file bytes provided")

    content_items = [
        {
            "type": "text",
            "text": (
                "Extract all visible text.\n"
                "IMPORTANT:\n"
                "- Convert ALL math into LaTeX ($...$ or $$...$$)\n"
                "- Never use square brackets for equations\n"
                "- Preserve structure (tables, headings, diagrams)\n"
                "- Output clean Markdown only\n"
            ),
        }
    ]

    # PDF handling
    if content_type == "application/pdf" or filename.lower().endswith(".pdf"):
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

    # image handling
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

    # 🔥 FINAL NORMALIZATION
    output = normalize_math(output)

    return output
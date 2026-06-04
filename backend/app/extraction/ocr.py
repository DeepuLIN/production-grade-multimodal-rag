import base64
import fitz

from fastapi import UploadFile
from openai import OpenAI
from app.rag.chunker import chunk_text
from app.core.config import (
    MAX_PDF_PAGES,
    OCR_MODEL,
    OPEN_ROUTER_API_KEY,
    OPEN_ROUTER_BASE_URL,
)


async def extract_text_from_upload(file: UploadFile) -> str:
    if not OPEN_ROUTER_API_KEY:
        raise RuntimeError("OPEN_ROUTER_API_KEY is missing")

    file_bytes = await file.read()

    if not file_bytes:
        raise ValueError("No file uploaded")

    content_items = [
        {
            "type": "text",
            "text": (
               "Extract all visible text from this file. "
                "Preserve headings, paragraphs, equations, tables, and figure labels. "
                "If there are figures, diagrams, charts, or images, extract any visible text, labels, legends, captions, and axis names. "
                "Do not summarize or explain the figure. "
                "Return only the extracted text."
            ),
        }
    ]

    if file.content_type == "application/pdf":
        pdf = fitz.open(stream=file_bytes, filetype="pdf")

        for page_index, page in enumerate(pdf):
            if page_index >= MAX_PDF_PAGES:
                break

            pix = page.get_pixmap(dpi=200)
            image_bytes = pix.tobytes("png")
            image_base64 = base64.b64encode(image_bytes).decode("utf-8")

            content_items.append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/png;base64,{image_base64}"
                },
            })

        pdf.close()

    else:
        content_type = file.content_type or "image/jpeg"
        image_base64 = base64.b64encode(file_bytes).decode("utf-8")

        content_items.append({
            "type": "image_url",
            "image_url": {
                "url": f"data:{content_type};base64,{image_base64}"
            },
        })

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
                    "You are a high-accuracy OCR engine. Extract all visible text from images or PDF pages. "
                    "Preserve reading order, headings, bullet points, equations, symbols, and line breaks. "
                    "Do not summarize. Do not explain. Do not add missing text. "
                    "If the image contains diagrams, extract labels and nearby text clearly."
                ),
            },
            {
                "role": "user",
                "content": content_items,
            },
        ],
    )

    return response.choices[0].message.content or ""
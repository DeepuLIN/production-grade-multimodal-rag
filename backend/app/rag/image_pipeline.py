import fitz
import base64
from openai import OpenAI
import os

client = OpenAI(
    api_key=os.getenv("OPEN_ROUTER_API_KEY"),
    base_url=os.getenv("OPEN_ROUTER_BASE_URL", "https://openrouter.ai/api/v1")
)


# -----------------------------
# RENDER PAGE AS IMAGE (FIX)
# -----------------------------
def render_pages(pdf_bytes: bytes):
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")

    pages = []

    for page_index in range(len(doc)):
        page = doc[page_index]

        pix = page.get_pixmap(dpi=200)  # IMPORTANT

        img_bytes = pix.tobytes("png")

        pages.append({
            "page": page_index + 1,
            "image_bytes": img_bytes
        })

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
                "content": "Describe technical diagrams clearly for search indexing."
            },
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Describe this page."},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{image_base64}"
                        }
                    }
                ]
            }
        ],
        temperature=0.2,
    )

    return response.choices[0].message.content


# -----------------------------
# MAIN PIPELINE
# -----------------------------
def process_pdf_images(pdf_bytes: bytes, document_id: str):

    pages = render_pages(pdf_bytes)

    results = []

    for p in pages:
        try:
            caption = caption_image(p["image_bytes"])

            results.append({
                "caption": caption,
                "page": p["page"]
            })

        except Exception as e:
            print("❌ vision error:", e)

    return results
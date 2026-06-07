from app.extraction.ocr import extract_text_from_bytes
from app.rag.image_pipeline import process_pdf_images
from app.rag.chunker import chunk_text
from app.rag.vector_store import upsert_chunks
from app.rag.text_cleaner import clean_ocr_text
from app.rag.markdown_builder import build_markdown_document
from app.rag.markdown_chunker import chunk_markdown
from app.storage.s3 import upload_ocr_json


async def process_uploaded_document(
    document_id: str,
    filename: str,
    content_type: str,
    file_bytes: bytes,
    user_id: str,
    clerk_user_id: str,
    project_id: str,
):
    raw_text = await extract_text_from_bytes(
        file_bytes=file_bytes,
        filename=filename,
        content_type=content_type,
    )

    cleaned_text_only = clean_ocr_text(raw_text)

    if not cleaned_text_only:
        raise ValueError("OCR returned empty text.")

    image_data = process_pdf_images(file_bytes, document_id)

    print(f"🖼️ IMAGES FOUND: {len(image_data)}")

    rag_text = build_markdown_document(
        filename=filename,
        text=cleaned_text_only,
        image_data=image_data,
    )

    text_chunks = chunk_markdown(rag_text)

    chunks = [
        {"chunk_type": "text", "text": chunk}
        for chunk in text_chunks
    ]

    for img in image_data:
        print(
            f"📦 FIGURE CHUNK CREATED | "
            f"page={img['page']} | "
            f"has_key={bool(img.get('image_s3_key'))}"
        )

        chunks.append(
            {
                "chunk_type": "figure",
                "text": (
                    f"Visual source on page {img['page']}.\n"
                    f"This is a page-level visual chunk extracted from the PDF.\n"
                    f"If the caption mentions Figure, Fig., Table, Equation, diagram, chart, or architecture, "
                    f"use this chunk for visual/figure-related questions.\n\n"
                    f"Visual caption metadata:\n{img['caption']}"
                ),
                "caption": img["caption"],
                "page": img["page"],
                "image_s3_key": img.get("image_s3_key"),
            }
        )

    print(f"📚 TOTAL CHUNKS: {len(chunks)}")
    print(
        f"📚 TEXT CHUNKS: {len(text_chunks)} | "
        f"FIGURE CHUNKS: {len(image_data)}"
    )

    stored_count = upsert_chunks(
        document_id=document_id,
        chunks=chunks,
        metadata={
            "user_id": user_id,
            "clerk_user_id": clerk_user_id,
            "project_id": project_id,
            "document_id": document_id,
            "filename": filename,
            "content_type": content_type,
            "image_data": image_data,
        },
    )

    ocr_key = upload_ocr_json(
        document_id=document_id,
        filename=filename,
        content_type=content_type,
        extracted_text=rag_text,
    )

    return {
        "document_id": document_id,
        "filename": filename,
        "content_type": content_type,
        "cleaned_text": cleaned_text_only,
        "rag_text": rag_text,
        "preview": rag_text[:1000],
        "text_length": len(cleaned_text_only),
        "rag_text_length": len(rag_text),
        "chunks_created": len(chunks),
        "chunks_stored_in_qdrant": stored_count,
        "images_found": len(image_data),
        "ocr_key": ocr_key,
    }


def process_document_text(
    document_id: str,
    text: str,
    metadata: dict | None = None,
):
    """
    TEXT → CHUNKS → QDRANT
    Used for simple text ingestion.
    """

    chunks = chunk_text(text)

    if not chunks:
        return {
            "document_id": document_id,
            "chunks_created": 0,
            "chunks_stored": 0,
            "status": "empty_text",
        }

    stored_count = upsert_chunks(
        document_id=document_id,
        chunks=chunks,
        metadata=metadata or {},
    )

    return {
        "document_id": document_id,
        "chunks_created": len(chunks),
        "chunks_stored": stored_count,
        "status": "indexed",
    }
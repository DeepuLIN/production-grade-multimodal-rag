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

    print(f"🖼️ VISUAL ITEMS FOUND: {len(image_data)}")

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

    figure_count = 0
    table_count = 0

    for item in image_data:
        chunk_type = item.get("chunk_type", "figure")

        if chunk_type == "table":
            table_count += 1

            print(
                f"📦 TABLE CHUNK CREATED | "
                f"page={item.get('page')} | "
                f"has_key={bool(item.get('image_s3_key'))}"
            )

            chunks.append(
                {
                    "chunk_type": "table",
                    "text": (
                        f"Table source on page {item.get('page')}.\n"
                        f"This is a table-level chunk extracted from the PDF.\n"
                        f"Use this chunk for questions about tables, rows, columns, values, comparisons, "
                        f"metrics, results, measurements, or tabular data.\n\n"
                        f"Table caption:\n{item.get('caption', '')}\n\n"
                        f"Table Markdown:\n{item.get('table_markdown', '')}"
                    ),
                    "caption": item.get("caption"),
                    "page": item.get("page"),
                    "image_s3_key": item.get("image_s3_key"),
                    "table_markdown": item.get("table_markdown"),
                }
            )

            continue

        figure_count += 1

        print(
            f"📦 FIGURE CHUNK CREATED | "
            f"page={item.get('page')} | "
            f"has_key={bool(item.get('image_s3_key'))}"
        )

        chunks.append(
            {
                "chunk_type": "figure",
                "text": (
                    f"Visual source on page {item.get('page')}.\n"
                    f"This is a page-level visual chunk extracted from the PDF.\n"
                    f"If the caption mentions Figure, Fig., Table, Equation, diagram, chart, or architecture, "
                    f"use this chunk for visual/figure-related questions.\n\n"
                    f"Visual caption metadata:\n{item.get('caption', '')}"
                ),
                "caption": item.get("caption"),
                "page": item.get("page"),
                "image_s3_key": item.get("image_s3_key"),
            }
        )

    print(f"📚 TOTAL CHUNKS: {len(chunks)}")
    print(
        f"📚 TEXT CHUNKS: {len(text_chunks)} | "
        f"FIGURE CHUNKS: {figure_count} | "
        f"TABLE CHUNKS: {table_count}"
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
        "visual_items_found": len(image_data),
        "figures_found": figure_count,
        "tables_found": table_count,
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
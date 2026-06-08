import re

from app.extraction.ocr import extract_text_from_bytes
from app.rag.image_pipeline import process_pdf_images
from app.rag.chunker import chunk_text
from app.rag.vector_store import upsert_chunks
from app.rag.text_cleaner import clean_ocr_text
from app.rag.markdown_builder import build_markdown_document
from app.rag.markdown_chunker import chunk_markdown
from app.storage.s3 import upload_ocr_json
from app.rag.document_summary import generate_document_summary, SUMMARY_MODEL


def extract_page_from_chunk(chunk: str) -> int | None:
    match = re.search(r"(?:###|##)\s*Page\s+(\d+)", chunk, flags=re.IGNORECASE)

    if not match:
        return None

    return int(match.group(1))


async def process_uploaded_document(
    document_id: str,
    filename: str,
    content_type: str,
    file_bytes: bytes,
    user_id: str,
    clerk_user_id: str,
    project_id: str,
    processing_mode: str = "auto",
):
    raw_text = await extract_text_from_bytes(
        file_bytes=file_bytes,
        filename=filename,
        content_type=content_type,
    )

    cleaned_text_only = clean_ocr_text(raw_text)

    if not cleaned_text_only:
        raise ValueError("OCR returned empty text.")

    caption_pages = processing_mode in ["auto", "visual_heavy", "handwritten"]

    print("PROCESSING MODE:", processing_mode)
    print("CAPTION PAGES:", caption_pages)

    image_data = process_pdf_images(
        pdf_bytes=file_bytes,
        document_id=document_id,
        caption_pages=caption_pages,
    )

    print(f"VISUAL ITEMS FOUND: {len(image_data)}")

    rag_text = build_markdown_document(
        filename=filename,
        text=cleaned_text_only,
        image_data=image_data,
    )

    document_summary = generate_document_summary(
        text=rag_text,
        filename=filename,
    )

    print(f"DOCUMENT SUMMARY CREATED | {document_summary[:120]}")

    text_chunks = chunk_markdown(rag_text)

    page_image_map = {
        item.get("page"): item.get("image_s3_key")
        for item in image_data
        if item.get("chunk_type") == "figure"
        and item.get("page") is not None
        and item.get("image_s3_key")
    }

    chunks = []

    for chunk in text_chunks:
        page = extract_page_from_chunk(chunk)

        chunks.append(
            {
                "chunk_type": "text",
                "text": chunk,
                "page": page,
                "image_s3_key": page_image_map.get(page),
            }
        )

    figure_count = 0
    table_count = 0

    for item in image_data:
        chunk_type = item.get("chunk_type", "figure")

        if chunk_type == "table":
            table_count += 1

            print(
                f"TABLE CHUNK CREATED | "
                f"page={item.get('page')} | "
                f"has_key={bool(item.get('image_s3_key'))}"
            )

            chunks.append(
                {
                    "chunk_type": "table",
                    "text": (
                        f"Table source on page {item.get('page')}.\n"
                        f"This is a page-level table source extracted from the PDF.\n"
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
            f"FIGURE CHUNK CREATED | "
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

    print(f"TOTAL CHUNKS: {len(chunks)}")
    print(
        f"TEXT CHUNKS: {len(text_chunks)} | "
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
            "document_summary": document_summary,
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
        "summary": document_summary,
        "summary_model": SUMMARY_MODEL,
        "extraction_method": processing_mode,
        "ocr_key": ocr_key,
    }


def process_document_text(
    document_id: str,
    text: str,
    metadata: dict | None = None,
):
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
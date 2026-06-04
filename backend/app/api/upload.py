import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, UploadFile, HTTPException
from sqlalchemy.orm import Session

from app.extraction.ocr import extract_text_from_upload
from app.storage.s3 import upload_original_file, upload_ocr_json
from app.rag.image_pipeline import process_pdf_images
from app.rag.chunker import chunk_text
from app.rag.vector_store import upsert_chunks
from app.rag.text_cleaner import clean_ocr_text
from app.rag.markdown_builder import build_markdown_document
from app.rag.markdown_chunker import chunk_markdown
from app.auth.clerk import get_current_user
from app.db.database import get_db
from app.db import crud, schemas, models

router = APIRouter()

MAX_PDF_BYTES = 50 * 1024 * 1024
MAX_IMAGE_BYTES = 10 * 1024 * 1024

ALLOWED_EXTENSIONS = {".pdf", ".png", ".jpg", ".jpeg", ".webp"}

ALLOWED_CONTENT_TYPES = {
    "application/pdf",
    "image/png",
    "image/jpeg",
    "image/webp",
}


def validate_upload_file(
    filename: str,
    content_type: str,
    file_bytes: bytes,
) -> None:
    suffix = Path(filename).suffix.lower()
    size_bytes = len(file_bytes)

    if suffix not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"File type '{suffix or 'unknown'}' is not allowed. Allowed types: PDF, PNG, JPG, JPEG, WEBP.",
        )

    if content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Content type '{content_type}' is not allowed.",
        )

    if suffix == ".pdf":
        if size_bytes > MAX_PDF_BYTES:
            raise HTTPException(
                status_code=413,
                detail="PDF exceeds 50 MB limit.",
            )

    if suffix in {".png", ".jpg", ".jpeg", ".webp"}:
        if size_bytes > MAX_IMAGE_BYTES:
            raise HTTPException(
                status_code=413,
                detail="Image exceeds 10 MB limit.",
            )


@router.get("/api")
def api_status():
    return {"status": "api route works"}


@router.post("/")
@router.post("/api")
@router.post("/upload")
@router.post("/api/upload")
async def upload_document(
    file: UploadFile = File(...),
    project_id: str | None = Form(None),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    try:
        document_id = str(uuid.uuid4())

        if project_id:
            user_projects = crud.get_user_projects(
                db=db,
                user_id=current_user.id,
            )

            project = next(
                (p for p in user_projects if p.id == project_id),
                None,
            )

            if not project:
                raise HTTPException(
                    status_code=404,
                    detail="Project not found for current user",
                )
        else:
            project = crud.get_default_project(
                db=db,
                user_id=current_user.id,
            )

        file_bytes = await file.read()

        if not file_bytes:
            raise HTTPException(
                status_code=400,
                detail="No file uploaded.",
            )

        filename = file.filename or "uploaded_file"
        content_type = file.content_type or "application/octet-stream"

        validate_upload_file(
            filename=filename,
            content_type=content_type,
            file_bytes=file_bytes,
        )

        original_key = upload_original_file(
            document_id=document_id,
            filename=filename,
            file_bytes=file_bytes,
            content_type=content_type,
        )

        await file.seek(0)

        raw_text = await extract_text_from_upload(file)

        print("===== OCR OUTPUT =====")
        print(raw_text[:1000])

        cleaned_text_only = clean_ocr_text(raw_text)

        print("===== CLEANED TEXT =====")
        print(cleaned_text_only[:1000])

        if not cleaned_text_only:
            raise HTTPException(
                status_code=422,
                detail="OCR returned empty text.",
            )

        image_data = process_pdf_images(file_bytes, document_id)

        print("===== IMAGE PIPELINE OUTPUT =====")
        print(image_data)

        rag_text = build_markdown_document(
            filename=filename,
            text=cleaned_text_only,
            image_data=image_data,
        )

        print("===== MARKDOWN RAG TEXT =====")
        print(rag_text[:1000])

        image_captions = []
        for img in image_data:
            caption = img.get("caption", "")
            page = img.get("page", "unknown")

            if caption:
                image_captions.append(f"[PAGE {page}] {caption}")

        if rag_text.strip().startswith("#"):
            print("🔥 Using Markdown Chunker")
            chunks = chunk_markdown(rag_text)
        else:
            print("🔥 Using Text Chunker")
            chunks = chunk_text(rag_text)

        print("===== CHUNKS =====")
        print(f"Total chunks: {len(chunks)}")

        for i, c in enumerate(chunks[:3]):
            print(f"\n--- CHUNK {i} ---")
            print(c)

        stored_count = upsert_chunks(
            document_id=document_id,
            chunks=chunks,
            metadata={
                "user_id": current_user.id,
                "clerk_user_id": current_user.clerk_user_id,
                "project_id": project.id,
                "document_id": document_id,
                "filename": filename,
                "content_type": content_type,
                "image_data": image_data,
            },
        )

        print("🔥 UPLOAD RESPONSE DOCUMENT ID:", document_id)
        print("🔥 POSTGRES DOCUMENT ID WILL BE:", document_id)
        print("🔥 PROJECT ID:", project.id)
        print("🔥 USER ID:", current_user.id)

        ocr_key = upload_ocr_json(
            document_id=document_id,
            filename=filename,
            content_type=content_type,
            extracted_text=rag_text,
        )

        document = crud.create_document(
            db=db,
            document=schemas.DocumentCreate(
                id=document_id,
                user_id=current_user.id,
                project_id=project.id,
                filename=filename,
                content_type=content_type,
                s3_original_path=original_key,
                s3_ocr_path=ocr_key,
            ),
        )

        print("🔥 POSTGRES SAVED DOCUMENT ID:", document.id)

        return {
            "success": True,
            "document_id": document.id,
            "project_id": project.id,
            "user_id": current_user.id,
            "clerk_user_id": current_user.clerk_user_id,
            "filename": filename,
            "content_type": content_type,
            "extracted_text": cleaned_text_only,
            "cleaned_text": cleaned_text_only,
            "rag_text": rag_text,
            "preview": rag_text[:1000],
            "text_length": len(cleaned_text_only),
            "rag_text_length": len(rag_text),
            "top_matches": [],
            "rag": {
                "chunks_created": len(chunks),
                "chunks_stored_in_qdrant": stored_count,
            },
            "image_pipeline": {
                "images_found": len(image_data),
                "captions_extracted": len(image_captions),
            },
            "storage": {
                "saved": True,
                "original_file": original_key,
                "ocr_result": ocr_key,
            },
            "postgres": {
                "document_saved": True,
                "document_id": document.id,
                "project_id": document.project_id,
            },
        }

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
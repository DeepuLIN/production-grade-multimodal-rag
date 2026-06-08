import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, UploadFile, HTTPException
from sqlalchemy.orm import Session

from app.storage.s3 import upload_original_file
from app.rag.pipeline import process_uploaded_document
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
            detail=(
                f"File type '{suffix or 'unknown'}' is not allowed. "
                "Allowed types: PDF, PNG, JPG, JPEG, WEBP."
            ),
        )

    if content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Content type '{content_type}' is not allowed.",
        )

    if suffix == ".pdf" and size_bytes > MAX_PDF_BYTES:
        raise HTTPException(
            status_code=413,
            detail="PDF exceeds 50 MB limit.",
        )

    if suffix in {".png", ".jpg", ".jpeg", ".webp"} and size_bytes > MAX_IMAGE_BYTES:
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
    processing_mode: str = Form("auto"),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    document_id = str(uuid.uuid4())

    try:
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

        document = crud.create_document(
            db=db,
            document=schemas.DocumentCreate(
                id=document_id,
                user_id=current_user.id,
                project_id=project.id,
                filename=filename,
                content_type=content_type,
                s3_original_path=original_key,
                s3_ocr_path=None,
                status="processing",
            ),
        )

        print("🔥 POSTGRES CREATED DOCUMENT ID:", document.id)

        result = await process_uploaded_document(
            document_id=document_id,
            filename=filename,
            content_type=content_type,
            file_bytes=file_bytes,
            user_id=current_user.id,
            clerk_user_id=current_user.clerk_user_id,
            project_id=project.id,
            processing_mode=processing_mode,
        )

        crud.update_document_storage(
            db=db,
            document_id=document_id,
            s3_ocr_path=result["ocr_key"],
        )
        crud.update_document_summary(
            db=db,
            document_id=document_id,
            summary=result.get("summary"),
            summary_model=result.get("summary_model"),
            extraction_method=result.get("extraction_method"),
        )

        crud.update_document_status(
            db=db,
            document_id=document_id,
            status="completed",
        )

        print("🔥 POSTGRES COMPLETED DOCUMENT ID:", document.id)

        return {
            "success": True,
            "document_id": document.id,
            "project_id": project.id,
            "user_id": current_user.id,
            "clerk_user_id": current_user.clerk_user_id,
            "filename": filename,
            "content_type": content_type,
            "status": "completed",
            "preview": result["preview"],
            "text_length": result["text_length"],
            "rag_text_length": result["rag_text_length"],
            "top_matches": [],
            "rag": {
                "chunks_created": result["chunks_created"],
                "chunks_stored_in_qdrant": result["chunks_stored_in_qdrant"],
            },
            "image_pipeline": {
                "images_found": result.get("images_found", 0),
                "visual_items_found": result.get("visual_items_found", 0),
                "figures_found": result.get("figures_found", 0),
                "tables_found": result.get("tables_found", 0),
            },

            "document_summary": {
                "summary": result.get("summary"),
                "summary_model": result.get("summary_model"),
                "extraction_method": result.get("extraction_method"),
            },
            "storage": {
                "saved": True,
                "original_file": original_key,
                "ocr_result": result["ocr_key"],
            },
            "postgres": {
                "document_saved": True,
                "document_id": document.id,
                "project_id": document.project_id,
            },
        }

    except HTTPException as e:
        try:
            crud.update_document_status(
                db=db,
                document_id=document_id,
                status="failed",
                error_message=str(e.detail),
            )
        except Exception:
            pass

        raise

    except Exception as e:
        try:
            crud.update_document_status(
                db=db,
                document_id=document_id,
                status="failed",
                error_message=str(e),
            )
        except Exception:
            pass

        raise HTTPException(
            status_code=500,
            detail=str(e),
        )
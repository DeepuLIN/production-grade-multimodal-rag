from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth.clerk import get_current_user
from app.db.database import get_db
from app.db import crud, models
from app.rag.vector_store import delete_document_chunks
from app.storage.s3 import delete_s3_object

router = APIRouter(prefix="/documents", tags=["documents"])


@router.get("")
def list_documents(
    project_id: str | None = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    documents = crud.get_user_documents(
        db=db,
        user_id=current_user.id,
        project_id=project_id,
    )

    return {
        "documents": [
            {
                "id": document.id,
                "user_id": document.user_id,
                "project_id": document.project_id,
                "filename": document.filename,
                "content_type": document.content_type,
                "s3_original_path": document.s3_original_path,
                "s3_ocr_path": document.s3_ocr_path,
                "created_at": document.created_at,
            }
            for document in documents
        ]
    }


@router.get("/{document_id}")
def get_document(
    document_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    document = crud.get_document_for_user(
        db=db,
        user_id=current_user.id,
        document_id=document_id,
    )

    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    return {
        "id": document.id,
        "user_id": document.user_id,
        "project_id": document.project_id,
        "filename": document.filename,
        "content_type": document.content_type,
        "s3_original_path": document.s3_original_path,
        "s3_ocr_path": document.s3_ocr_path,
        "created_at": document.created_at,
    }


@router.delete("/{document_id}")
def delete_document(
    document_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    document = crud.get_document_for_user(
        db=db,
        user_id=current_user.id,
        document_id=document_id,
    )

    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    filename = document.filename
    s3_original_path = document.s3_original_path
    s3_ocr_path = document.s3_ocr_path

    print("\n🔥 DELETE REQUEST")
    print("user_id:", current_user.id)
    print("document_id:", document_id)
    print("filename:", filename)

    # -----------------------------
    # QDRANT DELETE
    # -----------------------------
    qdrant_deleted = False
    try:
        qdrant_deleted = delete_document_chunks(
            user_id=str(current_user.id),
            document_id=str(document_id),
        )
        print("🔥 QDRANT DELETE:", qdrant_deleted)
    except Exception as e:
        print("⚠️ Qdrant delete failed:", str(e))

    # -----------------------------
    # S3 DELETE (ORIGINAL)
    # -----------------------------
    s3_original_deleted = False
    try:
        s3_original_deleted = delete_s3_object(s3_original_path)
        print("🔥 S3 ORIGINAL DELETE:", s3_original_deleted)
    except Exception as e:
        print("⚠️ S3 original delete failed:", str(e))

    # -----------------------------
    # S3 DELETE (OCR)
    # -----------------------------
    s3_ocr_deleted = False
    try:
        s3_ocr_deleted = delete_s3_object(s3_ocr_path)
        print("🔥 S3 OCR DELETE:", s3_ocr_deleted)
    except Exception as e:
        print("⚠️ S3 OCR delete failed:", str(e))

    # -----------------------------
    # POSTGRES DELETE
    # -----------------------------
    crud.delete_document_for_user(
        db=db,
        user_id=current_user.id,
        document_id=document_id,
    )

    return {
        "success": True,
        "deleted_document_id": document_id,  # 🔥 SSTA ID
        "filename": filename,
        "qdrant_deleted": qdrant_deleted,
        "s3_original_deleted": s3_original_deleted,
        "s3_ocr_deleted": s3_ocr_deleted,
        "postgres_deleted": True,
    }
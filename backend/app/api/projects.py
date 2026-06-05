from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth.clerk import get_current_user
from app.db.database import get_db
from app.db import crud, schemas, models
from app.rag.vector_store import delete_document_chunks
from app.storage.s3 import delete_s3_object

router = APIRouter(prefix="/projects", tags=["projects"])


@router.get("")
def list_projects(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    projects = crud.get_user_projects(
        db=db,
        user_id=current_user.id,
    )

    return {
        "projects": [
            {
                "id": project.id,
                "name": project.name,
                "user_id": project.user_id,
                "created_at": project.created_at,
            }
            for project in projects
        ]
    }


@router.post("")
def create_project(
    payload: schemas.ProjectCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    project = crud.create_project(
        db=db,
        user_id=current_user.id,
        name=payload.name,
    )

    return {
        "id": project.id,
        "name": project.name,
        "user_id": project.user_id,
        "created_at": project.created_at,
    }


@router.delete("/{project_id}")
def delete_project(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    project = crud.get_project_for_user(
        db=db,
        user_id=current_user.id,
        project_id=project_id,
    )

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    documents = crud.get_user_documents(
        db=db,
        user_id=current_user.id,
        project_id=project_id,
    )

    deleted_documents = []

    for document in documents:
        try:
            delete_document_chunks(
                user_id=str(current_user.id),
                document_id=str(document.id),
            )
        except Exception as e:
            print("⚠️ Qdrant delete failed:", str(e))

        try:
            delete_s3_object(document.s3_original_path)
        except Exception as e:
            print("⚠️ S3 original delete failed:", str(e))

        try:
            delete_s3_object(document.s3_ocr_path)
        except Exception as e:
            print("⚠️ S3 OCR delete failed:", str(e))

        deleted_documents.append(document.id)

    crud.delete_project_for_user(
        db=db,
        user_id=current_user.id,
        project_id=project_id,
    )

    return {
        "success": True,
        "deleted_project_id": project_id,
        "deleted_documents": deleted_documents,
    }
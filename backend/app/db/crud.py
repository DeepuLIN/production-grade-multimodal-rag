from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.db import models, schemas

def get_or_create_user(
    db: Session,
    clerk_user_id: str,
    email: str | None = None,
) -> models.User:
    user = (
        db.query(models.User)
        .filter(models.User.clerk_user_id == clerk_user_id)
        .first()
    )

    if user:
        return user

    user = models.User(
        clerk_user_id=clerk_user_id,
        email=email,
    )

    try:
        db.add(user)
        db.commit()
        db.refresh(user)

        create_project(
            db=db,
            user_id=user.id,
            name="Default Project",
        )

        return user

    except IntegrityError:
        db.rollback()

        user = (
            db.query(models.User)
            .filter(models.User.clerk_user_id == clerk_user_id)
            .first()
        )

        if not user:
            raise

        return user


def create_project(
    db: Session,
    user_id: str,
    name: str,
) -> models.Project:
    project = models.Project(
        user_id=user_id,
        name=name,
    )

    db.add(project)
    db.commit()
    db.refresh(project)

    return project


def get_user_projects(
    db: Session,
    user_id: str,
) -> list[models.Project]:
    return (
        db.query(models.Project)
        .filter(models.Project.user_id == user_id)
        .order_by(models.Project.created_at.desc())
        .all()
    )


def get_default_project(
    db: Session,
    user_id: str,
) -> models.Project:
    project = (
        db.query(models.Project)
        .filter(models.Project.user_id == user_id)
        .order_by(models.Project.created_at.asc())
        .first()
    )

    if project:
        return project

    return create_project(
        db=db,
        user_id=user_id,
        name="Default Project",
    )


def create_document(
    db: Session,
    document: schemas.DocumentCreate,
) -> models.Document:
    db_document = models.Document(**document.model_dump())

    db.add(db_document)
    db.commit()
    db.refresh(db_document)

    return db_document


def update_document_storage(
    db: Session,
    document_id: str,
    s3_original_path: str | None = None,
    s3_ocr_path: str | None = None,
) -> models.Document | None:
    document = (
        db.query(models.Document)
        .filter(models.Document.id == document_id)
        .first()
    )

    if not document:
        return None

    if s3_original_path is not None:
        document.s3_original_path = s3_original_path

    if s3_ocr_path is not None:
        document.s3_ocr_path = s3_ocr_path

    db.commit()
    db.refresh(document)

    return document



def update_document_status(
    db: Session,
    document_id: str,
    status: str,
    error_message: str | None = None,
) -> models.Document | None:
    document = (
        db.query(models.Document)
        .filter(models.Document.id == document_id)
        .first()
    )

    if not document:
        return None

    document.status = status
    document.error_message = error_message

    db.commit()
    db.refresh(document)

    return document


def get_user_documents(
    db: Session,
    user_id: str,
    project_id: str | None = None,
) -> list[models.Document]:
    query = db.query(models.Document).filter(models.Document.user_id == user_id)

    if project_id:
        query = query.filter(models.Document.project_id == project_id)

    return query.order_by(models.Document.created_at.desc()).all()


def get_document_for_user(
    db: Session,
    user_id: str,
    document_id: str,
) -> models.Document | None:
    return (
        db.query(models.Document)
        .filter(
            models.Document.user_id == user_id,
            models.Document.id == document_id,
        )
        .first()
    )


def delete_document_for_user(
    db: Session,
    user_id: str,
    document_id: str,
) -> models.Document | None:
    document = get_document_for_user(
        db=db,
        user_id=user_id,
        document_id=document_id,
    )

    if not document:
        return None

    db.delete(document)
    db.commit()

    return document


def get_project_for_user(
    db: Session,
    user_id: str,
    project_id: str,
) -> models.Project | None:
    return (
        db.query(models.Project)
        .filter(
            models.Project.user_id == user_id,
            models.Project.id == project_id,
        )
        .first()
    )


def delete_project_for_user(
    db: Session,
    user_id: str,
    project_id: str,
) -> models.Project | None:
    project = get_project_for_user(
        db=db,
        user_id=user_id,
        project_id=project_id,
    )

    if not project:
        return None

    db.delete(project)
    db.commit()

    return project


def update_document_summary(
    db: Session,
    document_id: str,
    summary: str | None = None,
    summary_model: str | None = None,
    extraction_method: str | None = None,
) -> models.Document | None:
    document = (
        db.query(models.Document)
        .filter(models.Document.id == document_id)
        .first()
    )

    if not document:
        return None

    if summary is not None:
        document.summary = summary

    if summary_model is not None:
        document.summary_model = summary_model

    if extraction_method is not None:
        document.extraction_method = extraction_method

    db.commit()
    db.refresh(document)

    return document

def get_project_document_summaries(
    db: Session,
    user_id: str,
    project_id: str,
) -> list[dict]:
    documents = (
        db.query(models.Document)
        .filter(
            models.Document.user_id == user_id,
            models.Document.project_id == project_id,
            models.Document.status == "completed",
            models.Document.summary.isnot(None),
        )
        .order_by(models.Document.created_at.asc())
        .all()
    )

    return [
        {
            "document_id": doc.id,
            "filename": doc.filename,
            "summary": doc.summary,
            "summary_model": doc.summary_model,
            "extraction_method": doc.extraction_method,
        }
        for doc in documents
    ]
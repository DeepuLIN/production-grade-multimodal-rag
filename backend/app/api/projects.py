from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth.clerk import get_current_user
from app.db.database import get_db
from app.db import crud, schemas, models

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
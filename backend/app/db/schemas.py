from datetime import datetime
from pydantic import BaseModel


class UserCreate(BaseModel):
    clerk_user_id: str
    email: str | None = None


class UserOut(BaseModel):
    id: str
    clerk_user_id: str
    email: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class ProjectCreate(BaseModel):
    name: str = "Default Project"


class ProjectOut(BaseModel):
    id: str
    user_id: str
    name: str
    created_at: datetime

    model_config = {"from_attributes": True}


# -------------------------
# DOCUMENTS
# -------------------------

class DocumentCreate(BaseModel):
    id: str
    user_id: str
    project_id: str
    filename: str
    content_type: str | None = None
    s3_original_path: str | None = None
    s3_ocr_path: str | None = None
    status: str = "processing"
    error_message: str | None = None


class DocumentOut(BaseModel):
    id: str
    user_id: str
    project_id: str
    filename: str
    content_type: str | None = None
    s3_original_path: str | None = None
    s3_ocr_path: str | None = None
    status: str
    error_message: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}
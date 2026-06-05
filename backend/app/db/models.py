import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


# -------------------------
# USERS
# -------------------------

class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(
        String,
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )

    clerk_user_id: Mapped[str] = mapped_column(
        String,
        unique=True,
        index=True,
        nullable=False,
    )

    email: Mapped[str | None] = mapped_column(
        String,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    projects = relationship(
        "Project",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    documents = relationship(
        "Document",
        back_populates="user",
        cascade="all, delete-orphan",
    )


# -------------------------
# PROJECTS
# -------------------------

class Project(Base):
    __tablename__ = "projects"

    id: Mapped[str] = mapped_column(
        String,
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )

    user_id: Mapped[str] = mapped_column(
        String,
        ForeignKey("users.id"),
        index=True,
        nullable=False,
    )

    name: Mapped[str] = mapped_column(
        String,
        default="Default Project",
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    user = relationship(
        "User",
        back_populates="projects",
    )

    documents = relationship(
        "Document",
        back_populates="project",
        cascade="all, delete-orphan",
    )


# -------------------------
# DOCUMENTS
# -------------------------

class Document(Base):
    __tablename__ = "documents"

    # IMPORTANT:
    # Upload pipeline provides the ID.
    # Do NOT auto-generate a UUID here.
    id: Mapped[str] = mapped_column(
        String,
        primary_key=True,
    )

    user_id: Mapped[str] = mapped_column(
        String,
        ForeignKey("users.id"),
        index=True,
        nullable=False,
    )

    project_id: Mapped[str] = mapped_column(
        String,
        ForeignKey("projects.id"),
        index=True,
        nullable=False,
    )

    filename: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )

    content_type: Mapped[str | None] = mapped_column(
        String,
        nullable=True,
    )

    s3_original_path: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    s3_ocr_path: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    status: Mapped[str] = mapped_column(
        String,
        default="processing",
        nullable=False,
    )

    error_message: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    user = relationship(
        "User",
        back_populates="documents",
    )

    project = relationship(
        "Project",
        back_populates="documents",
    )
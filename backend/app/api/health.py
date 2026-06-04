import os
import boto3
from fastapi import APIRouter
from sqlalchemy import text

from app.db.database import engine

router = APIRouter()


@router.get("/")
@router.get("/api")
@router.get("/health")
@router.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "service": "Multimodal RAG API",
    }


@router.get("/health/db")
@router.get("/api/health/db")
def health_db():
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return {"status": "healthy", "service": "database"}
    except Exception as e:
        return {
            "status": "unhealthy",
            "service": "database",
            "error": str(e),
        }


@router.get("/health/qdrant")
@router.get("/api/health/qdrant")
def health_qdrant():
    try:
        from app.rag.vector_store import search_chunks

        search_chunks("health check", top_k=1)

        return {"status": "healthy", "service": "qdrant"}
    except Exception as e:
        return {
            "status": "unhealthy",
            "service": "qdrant",
            "error": str(e),
        }


@router.get("/health/s3")
@router.get("/api/health/s3")
def health_s3():
    try:
        bucket_name = os.getenv("S3_BUCKET_NAME")
        if not bucket_name:
            return {
                "status": "unhealthy",
                "service": "s3",
                "error": "S3_BUCKET_NAME is not configured",
            }

        s3 = boto3.client("s3")
        s3.head_bucket(Bucket=bucket_name)

        return {
            "status": "healthy",
            "service": "s3",
            "bucket": bucket_name,
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "service": "s3",
            "error": str(e),
        }
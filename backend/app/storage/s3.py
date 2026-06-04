import json
from datetime import datetime, timezone

import boto3

from app.core.config import AWS_REGION, S3_BUCKET_NAME


def get_s3_client():
    if not S3_BUCKET_NAME:
        raise RuntimeError("S3_BUCKET_NAME is missing")

    return boto3.client("s3", region_name=AWS_REGION)


def upload_original_file(
    document_id: str,
    filename: str,
    file_bytes: bytes,
    content_type: str,
):
    s3 = get_s3_client()

    key = f"uploads/{document_id}/{filename}"

    s3.put_object(
        Bucket=S3_BUCKET_NAME,
        Key=key,
        Body=file_bytes,
        ContentType=content_type or "application/octet-stream",
    )

    return key


def upload_ocr_json(
    document_id: str,
    filename: str,
    content_type: str,
    extracted_text: str,
):
    s3 = get_s3_client()

    key = f"ocr/{document_id}/ocr.json"

    payload = {
        "document_id": document_id,
        "filename": filename,
        "content_type": content_type,
        "text_length": len(extracted_text),
        "extracted_text": extracted_text,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    s3.put_object(
        Bucket=S3_BUCKET_NAME,
        Key=key,
        Body=json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8"),
        ContentType="application/json",
    )

    return key


def upload_chunks(document_id: str, chunks: list[str]):
    s3 = get_s3_client()

    key = f"chunks/{document_id}/chunks.json"

    body = {
        "document_id": document_id,
        "chunks": chunks,
        "count": len(chunks),
    }

    s3.put_object(
        Bucket=S3_BUCKET_NAME,
        Key=key,
        Body=json.dumps(body).encode("utf-8"),
        ContentType="application/json",
    )

    return key


def upload_image_file(
    document_id: str,
    page: int,
    image_index: int,
    file_bytes: bytes,
):
    s3 = get_s3_client()

    key = f"images/{document_id}/page_{page}_img_{image_index}.png"

    s3.put_object(
        Bucket=S3_BUCKET_NAME,
        Key=key,
        Body=file_bytes,
        ContentType="image/png",
    )

    return key


def delete_s3_object(key: str | None) -> bool:
    if not key:
        return False

    try:
        s3 = get_s3_client()

        s3.delete_object(
            Bucket=S3_BUCKET_NAME,
            Key=key,
        )

        print(f"✅ Deleted S3 object: {key}")
        return True

    except Exception as e:
        print(f"⚠️ Failed to delete S3 object {key}: {e}")
        return False
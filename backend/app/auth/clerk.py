from fastapi import Depends, HTTPException, Request
from sqlalchemy.orm import Session
import base64
import json
import os

from app.db.database import get_db
from app.db import crud, models


def enforce_allowed_user(clerk_user_id: str | None, email: str | None):
    allowed_emails = {
        e.strip().lower()
        for e in os.getenv("ALLOWED_EMAILS", "").split(",")
        if e.strip()
    }

    allowed_user_ids = {
        u.strip()
        for u in os.getenv("ALLOWED_CLERK_USER_IDS", "").split(",")
        if u.strip()
    }

    if not allowed_emails and not allowed_user_ids:
        return

    if email and email.lower() in allowed_emails:
        return

    if clerk_user_id and clerk_user_id in allowed_user_ids:
        return

    raise HTTPException(
        status_code=403,
        detail="Private demo access only.",
    )


def decode_jwt_payload_unsafe(token: str) -> dict:
    """
    DEV ONLY:
    Decodes JWT payload without signature verification.

    Before production:
    Replace with Clerk JWKS verification.
    """
    try:
        parts = token.split(".")

        if len(parts) != 3:
            raise ValueError("Invalid JWT format")

        payload = parts[1]

        # Add base64 padding if missing
        payload += "=" * (-len(payload) % 4)

        decoded = base64.urlsafe_b64decode(
            payload.encode("utf-8")
        )

        return json.loads(decoded.decode("utf-8"))

    except Exception as e:
        raise HTTPException(
            status_code=401,
            detail=f"Invalid Clerk token payload: {e}",
        )


def get_clerk_user_from_request(request: Request) -> dict:
    auth_header = request.headers.get("authorization")

    print("\n========== AUTH DEBUG ==========")
    print("AUTH HEADER PRESENT:", bool(auth_header))
    print(
        "AUTH HEADER:",
        auth_header[:50] if auth_header else None,
    )

    if not auth_header or not auth_header.lower().startswith("bearer "):
        raise HTTPException(
            status_code=401,
            detail="Missing Clerk authorization token",
        )

    token = auth_header.split(" ", 1)[1]

    payload = decode_jwt_payload_unsafe(token)

    clerk_user_id = payload.get("sub")
    email = payload.get("email") or payload.get(
        "primary_email_address"
    )

    print("JWT sub:", clerk_user_id)
    print("JWT email:", email)
    print("JWT payload keys:", list(payload.keys()))

    if not clerk_user_id:
        raise HTTPException(
            status_code=401,
            detail="Clerk token missing sub",
        )

    return {
        "clerk_user_id": clerk_user_id,
        "email": email,
    }


def get_current_user(
    request: Request,
    db: Session = Depends(get_db),
) -> models.User:

    clerk_data = get_clerk_user_from_request(request)

    # Restrict demo access
    enforce_allowed_user(
        clerk_data.get("clerk_user_id"),
        clerk_data.get("email"),
    )

    user = crud.get_or_create_user(
        db=db,
        clerk_user_id=clerk_data["clerk_user_id"],
        email=clerk_data.get("email"),
    )

    print("POSTGRES USER ID:", user.id)
    print("POSTGRES CLERK USER:", user.clerk_user_id)
    print("POSTGRES EMAIL:", user.email)
    print("================================\n")

    return user
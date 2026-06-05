import os
from dotenv import load_dotenv

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

# -------------------------
# ROUTERS
# -------------------------
from app.api.health import router as health_router
from app.api.upload import router as upload_router
from app.api.search import router as search_router
from app.api.ask import router as ask_router
from app.api.projects import router as projects_router
from app.api.documents import router as documents_router

# -------------------------
# DB (optional init)
# -------------------------
from app.db.database import Base, engine
from app.db import models

app = FastAPI(title="Multimodal RAG API")

# -------------------------
# CORS (FIXED - ENV DRIVEN)
# -------------------------
cors_origins_raw = os.getenv("BACKEND_CORS_ORIGINS", "")

allowed_origins = [
    origin.strip()
    for origin in cors_origins_raw.split(",")
    if origin.strip()
]

# Fallback for local dev
if not allowed_origins:
    allowed_origins = [
        "http://localhost:3000",
        "http://localhost:3001",
    ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------
# CREATE TABLES (OK for dev, consider Alembic later)
# -------------------------
Base.metadata.create_all(bind=engine)

# -------------------------
# ROOT
# -------------------------
@app.get("/")
def root():
    return {"status": "backend running"}

# -------------------------
# ROUTERS
# -------------------------
app.include_router(health_router)
app.include_router(upload_router)
app.include_router(search_router)
app.include_router(ask_router)
app.include_router(projects_router)
app.include_router(documents_router)
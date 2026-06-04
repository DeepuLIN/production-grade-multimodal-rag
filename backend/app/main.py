import os

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

from app.api.health import router as health_router
from app.api.upload import router as upload_router
from app.api.search import router as search_router
from app.api.ask import router as ask_router
from app.api.projects import router as projects_router
from app.api.documents import router as documents_router

from app.db.database import Base, engine
from app.db import models


app = FastAPI(title="Multimodal RAG API")

# -------------------------
# CORS
# -------------------------
cors_origins_raw = os.getenv(
    "BACKEND_CORS_ORIGINS",
    "http://localhost:3000,http://127.0.0.1:3000",
)

allow_all_origins = cors_origins_raw.strip() == "*"

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://project-bs0el.vercel.app",
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)
# -------------------------
# CREATE TABLES
# -------------------------
Base.metadata.create_all(bind=engine)


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
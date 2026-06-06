import os
from pathlib import Path

# -------------------------
# PATHS
# -------------------------
BASE_DIR = Path(__file__).resolve().parents[3]

UPLOAD_DIR = BASE_DIR / "data" / "uploads"
CHROMA_DIR = BASE_DIR / "data" / "chroma"

# -------------------------
# DATABASE
# -------------------------
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://rag_user:rag_password@localhost:5432/multimodal_rag",
)

# -------------------------
# AWS / STORAGE
# -------------------------
AWS_REGION = os.getenv(
    "AWS_REGION",
    "eu-central-1",
)

S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")

# -------------------------
# HUGGINGFACE
# -------------------------
#HF_TOKEN = os.getenv("HF_TOKEN")


# -------------------------
# SQS
# -------------------------
SQS_QUEUE_URL = os.getenv("SQS_QUEUE_URL")

# -------------------------
# OPENROUTER
# -------------------------
OPEN_ROUTER_API_KEY = os.getenv("OPEN_ROUTER_API_KEY")

OPEN_ROUTER_BASE_URL = os.getenv(
    "OPEN_ROUTER_BASE_URL",
    "https://openrouter.ai/api/v1",
)

# -------------------------
# CLERK
# -------------------------
CLERK_JWKS_URL = os.getenv("CLERK_JWKS_URL")

# -------------------------
# PDF SETTINGS
# -------------------------
MAX_PDF_PAGES = int(
    os.getenv("MAX_PDF_PAGES", "10")
)

# -------------------------
# MODELS
# -------------------------
OCR_MODEL = os.getenv(
    "OCR_MODEL",
    "openai/gpt-4o-mini",
)

CHAT_MODEL = os.getenv(
    "CHAT_MODEL",
    "meta-llama/llama-3.1-70b-instruct",
)

# -------------------------
# RERANKING
# -------------------------
ENABLE_RERANKING = os.getenv(
    "ENABLE_RERANKING",
    "true",
).lower() == "true"

RERANK_MODEL = os.getenv(
    "RERANK_MODEL",
    "openai/gpt-4o-mini",
)
from sqlalchemy import create_engine, text

DATABASE_URL = "postgresql://rag_user:rag_password@localhost:5432/multimodal_rag"

engine = create_engine(DATABASE_URL)

print("🔥 Cleaning Postgres documents table...")

with engine.begin() as conn:
    conn.execute(text("DELETE FROM documents;"))

print("✅ Postgres cleaned")
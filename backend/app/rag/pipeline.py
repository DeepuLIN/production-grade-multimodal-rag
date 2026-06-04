from app.rag.chunker import chunk_text
from app.rag.embeddings import embed_texts
from app.rag.vector_store import upsert_chunks


def process_document(document_id: str, text: str, metadata: dict = None):
    """
    FULL RAG INGESTION PIPELINE
    OCR TEXT → CHUNKS → EMBEDDINGS → QDRANT
    """

    # 1. Chunking
    chunks = chunk_text(text)

    if not chunks:
        return {
            "document_id": document_id,
            "chunks": 0,
            "status": "empty_text"
        }

    # 2. Embeddings
    embeddings = embed_texts(chunks)

    # 3. Store in Qdrant
    stored_count = upsert_chunks(
        document_id=document_id,
        chunks=chunks,
        metadata=metadata or {}
    )

    return {
        "document_id": document_id,
        "chunks": stored_count,
        "status": "indexed"
    }
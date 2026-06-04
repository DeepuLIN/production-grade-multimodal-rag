from typing import Dict, Any, List

from app.rag.embeddings import embed_texts
from app.rag.vector_store import query_vector_store


def retrieve_context(
    document_id: str,
    question: str,
    top_k: int = 5,
) -> List[Dict[str, Any]]:
    query_embedding = embed_texts([question])[0]

    results = query_vector_store(
        document_id=document_id,
        query_embedding=query_embedding,
        top_k=top_k,
    )

    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0]

    contexts = []

    for doc, metadata, distance in zip(documents, metadatas, distances):
        contexts.append(
            {
                "text": doc,
                "metadata": metadata,
                "distance": distance,
            }
        )

    return contexts
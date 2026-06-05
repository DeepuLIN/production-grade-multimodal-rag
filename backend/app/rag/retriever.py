from typing import Dict, Any, List

from app.rag.vector_store import search_chunks


def retrieve_context(
    document_id: str,
    question: str,
    top_k: int = 5,
) -> List[Dict[str, Any]]:

    results = search_chunks(
        query=question,
        top_k=top_k,
        document_id=document_id,
    )

    return results.get("merged_results", [])
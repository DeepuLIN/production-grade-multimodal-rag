from fastapi import APIRouter, Depends, HTTPException, Query

from app.rag.vector_store import search_chunks
from app.auth.clerk import get_current_user
from app.db import models

router = APIRouter()


@router.get("/api/search")
def search(
    query: str = Query(..., description="User search query"),
    project_id: str | None = Query(None),
    document_id: str | None = Query(None),
    top_k: int = Query(5),
    current_user: models.User = Depends(get_current_user),
):
    try:
        if not query:
            raise ValueError("Query cannot be empty")

        results = search_chunks(
            query=query,
            top_k=top_k,
            user_id=current_user.id,
            project_id=project_id,
            document_id=document_id,
        )

        vector_results = results.get("vector_results", [])

        return {
            "query": query,
            "user_id": current_user.id,
            "project_id": project_id,
            "document_id": document_id,
            "results": results,
            "count": len(vector_results),
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
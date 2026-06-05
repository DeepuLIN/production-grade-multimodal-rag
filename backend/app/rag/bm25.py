from rank_bm25 import BM25Okapi
from typing import List, Dict, Any

from app.rag.filters import (
    match_document_filter,
    match_user_filter,
    match_project_filter,
)


class BM25Index:
    def __init__(self):
        self.items: List[Dict[str, Any]] = []
        self.tokenized_chunks: List[List[str]] = []
        self.bm25 = None

    def build(self, items: List[Dict[str, Any]]):
        if not items:
            self.items = []
            self.tokenized_chunks = []
            self.bm25 = None
            return

        self.items = items
        self.tokenized_chunks = [
            item["text"].lower().split()
            for item in items
        ]
        self.bm25 = BM25Okapi(self.tokenized_chunks)

    def add(self, items: List[Dict[str, Any]]):
        self.build(self.items + items)

    def search(
        self,
        query: str,
        top_k: int = 5,
        user_id: str | None = None,
        project_id: str | None = None,
        document_id: str | None = None,
    ) -> List[Dict[str, Any]]:

        if not self.bm25:
            return []

        tokenized_query = query.lower().split()
        scores = self.bm25.get_scores(tokenized_query)

        results = []

        for idx, score in enumerate(scores):
            item = self.items[idx]
            metadata = item.get("metadata", {})

            # 🧠 CONSISTENT FILTERING (SSTA FIX)
            if not match_user_filter(metadata, user_id):
                continue

            if not match_project_filter(metadata, project_id):
                continue

            if not match_document_filter(metadata, document_id):
                continue

            results.append({
                "text": item["text"],
                "bm25_score": float(score),
                "chunk_index": metadata.get("chunk_index", idx),
                "document_id": metadata.get("document_id"),
                "qdrant_document_id": metadata.get("qdrant_document_id"),
                "project_id": metadata.get("project_id"),
                "user_id": metadata.get("user_id"),
                "filename": metadata.get("filename"),
            })

        results.sort(key=lambda x: x["bm25_score"], reverse=True)
        return results[:top_k]
    

bm25_index = BM25Index()
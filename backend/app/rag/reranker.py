import json
from typing import Any, Dict, List

from openai import OpenAI

from app.core.config import (
    OPEN_ROUTER_API_KEY,
    OPEN_ROUTER_BASE_URL,
    RERANK_MODEL,
)


def rerank_chunks(
    query: str,
    chunks: List[Dict[str, Any]],
    top_k: int = 5,
) -> List[Dict[str, Any]]:
    if not chunks:
        return []

    if not OPEN_ROUTER_API_KEY:
        return chunks[:top_k]

    candidates = chunks[:20]

    candidate_text = "\n\n".join(
        (
            f"ID: {i}\n"
            f"TYPE: {item.get('chunk_type', 'text')}\n"
            f"PAGE: {item.get('page')}\n"
            f"VISUAL_BOOST: {item.get('visual_boost', False)}\n"
            f"TEXT:\n{item.get('text', '')[:1500]}"
        )
        for i, item in enumerate(candidates)
    )

    client = OpenAI(
        api_key=OPEN_ROUTER_API_KEY,
        base_url=OPEN_ROUTER_BASE_URL,
        timeout=45,
    )

    try:
        response = client.chat.completions.create(
            model=RERANK_MODEL,
            temperature=0,
            max_tokens=500,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a strict retrieval reranker for a RAG system. "
                        "Rank chunks ONLY by how directly they answer the user query. "
                        "Exact mentions of query concepts, acronyms, technologies, projects, figure numbers, table numbers, and equations are more important than general topical similarity. "
                        "If the query asks about a figure, fig., diagram, image, chart, table, equation, formula, architecture, or visual element, prefer chunks with TYPE: figure when relevant. "
                        "If the query mentions a specific figure number such as Figure 1, Figure 2, Fig. 3, or Figure 4, prefer chunks that explicitly mention that exact figure number. "
                        "If a TYPE: figure chunk and a TYPE: text chunk both answer the query, rank the TYPE: figure chunk higher for visual questions. "
                        "Do NOT rank a chunk highly just because it is broadly related. "
                        "Return ONLY valid JSON like: "
                        "{\"ranked_ids\":[0,2,1]}"
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        f"Query:\n{query}\n\n"
                        f"Candidate chunks:\n{candidate_text}\n\n"
                        f"Return the top {top_k} most relevant IDs."
                    ),
                },
            ],
        )

        raw = response.choices[0].message.content or ""
        parsed = json.loads(raw)
        ranked_ids = parsed.get("ranked_ids", [])

        reranked = []

        for rank, idx in enumerate(ranked_ids):
            if isinstance(idx, int) and 0 <= idx < len(candidates):
                item = candidates[idx].copy()
                item["rerank_rank"] = rank + 1
                reranked.append(item)

        if reranked:
            return reranked[:top_k]

    except Exception as e:
        print("⚠️ RERANK FAILED:", str(e))

    return chunks[:top_k]
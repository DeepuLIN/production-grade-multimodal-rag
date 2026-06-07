from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from openai import OpenAI
import os
import json
from app.rag.math_normalizer import normalize_math
from app.rag.vector_store import search_chunks
from app.core.config import CHAT_MODEL
from app.auth.clerk import get_current_user
from app.db import models
from app.storage.s3 import get_presigned_url

router = APIRouter()


class AskRequest(BaseModel):
    query: str | None = None
    question: str | None = None
    doc_filter: str = "all"
    project_id: str | None = None
    document_id: str | None = None
    top_k: int = 5
    rewrite: bool = False


class MatchOut(BaseModel):
    rank: int

    source: str
    filename: str | None = None
    page: int | None = 1

    # Retrieval Inspector Scores
    vector_score: float | None = None
    bm25_score: float | None = None
    rrf_score: float | None = None

    # Retrieval Inspector Ranks
    vector_rank: int | None = None
    bm25_rank: int | None = None

    text: str

    document_id: str | None = None
    project_id: str | None = None
    user_id: str | None = None

    chunk_index: int | None = None
        # V2 visual/table fields
    chunk_type: str = "text"
    caption: str | None = None
    image_s3_key: str | None = None
    image_url: str | None = None
    table_markdown: str | None = None



class AskResponse(BaseModel):
    query: str
    rewritten_query: str
    answer: str
    top_matches: list[MatchOut]
    sources: dict
    filters: dict


class StreamTokenEvent(BaseModel):
    type: str = "token"
    content: str


class StreamSourcesEvent(BaseModel):
    type: str = "sources"
    query: str
    rewritten_query: str
    top_matches: list[MatchOut]
    filters: dict


class StreamDoneEvent(BaseModel):
    type: str = "done"


class StreamErrorEvent(BaseModel):
    type: str = "error"
    message: str


def sse_event(payload: BaseModel | dict) -> str:
    data = payload.model_dump() if isinstance(payload, BaseModel) else payload
    return f"data: {json.dumps(data, ensure_ascii=False)}\n\n"


def get_client():
    api_key = os.getenv("OPEN_ROUTER_API_KEY")
    base_url = os.getenv("OPEN_ROUTER_BASE_URL") or "https://openrouter.ai/api/v1"

    if not api_key:
        raise RuntimeError("OPEN_ROUTER_API_KEY is missing")

    print("🔥 OPENROUTER BASE URL:", base_url)
    print("🔥 CHAT MODEL:", CHAT_MODEL)

    return OpenAI(api_key=api_key, base_url=base_url)


def normalize_document_id(document_id: str | None):
    if document_id in [None, "", "all"]:
        return None
    return document_id


def should_skip_rewrite(query: str) -> bool:
    q = query.lower().strip()

    risky_terms = [
        
        "me",
        "my",
        "i ",
        "about me",
        "tell me about",
        "who am i",
        "what did i",
    ]

    return any(term in q for term in risky_terms)


def rewrite_query(client: OpenAI, query: str) -> str:
    if should_skip_rewrite(query):
        print("⚠️ Skipping query rewrite for personal/name query")
        return query

    response = client.chat.completions.create(
        model=CHAT_MODEL,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a conservative query rewriting system for private document search. "
                    "Rewrite the query into concise search keywords using ONLY entities and terms present in the query. "
                    "Do not add famous people, companies, books, external facts, or assumptions. "
                    "If unsure, return the original query. "
                    "Return ONLY keywords."
                ),
            },
            {
                "role": "user",
                "content": f"Rewrite this query without adding new entities:\n{query}",
            },
        ],
        temperature=0.0,
    )

    rewritten = response.choices[0].message.content.strip()

    original_tokens = set(query.lower().replace("?", "").replace(",", " ").split())
    rewritten_tokens = set(rewritten.lower().replace("?", "").replace(",", " ").split())
    new_tokens = rewritten_tokens - original_tokens

    if len(new_tokens) > 4:
        print("⚠️ Rewrite added too many new terms. Falling back to original query.")
        return query

    return rewritten


def get_search_query(client: OpenAI, user_query: str, rewrite: bool = False) -> str:
    if not rewrite:
        print("⚠️ Query rewrite disabled. Using original query.")
        return user_query

    return rewrite_query(client, user_query)


def normalize_matches(results: dict, top_k: int = 5) -> list[MatchOut]:
    top_matches: list[MatchOut] = []

    merged_results = results.get("merged_results") or []
    vector_results = results.get("vector_results") or []

    source_results = merged_results if merged_results else vector_results

    for idx, item in enumerate(source_results[:top_k]):
        text = item.get("text", "")

        if not text:
            continue

        image_s3_key = item.get("image_s3_key")
        image_url = get_presigned_url(image_s3_key) if image_s3_key else None
        print(
            f"📤 MATCH | "
            f"type={item.get('chunk_type')} | "
            f"page={item.get('page')} | "
            f"has_key={bool(image_s3_key)} | "
            f"has_url={bool(image_url)}"
        )

        top_matches.append(
            MatchOut(
                rank=idx + 1,
                source=item.get("filename") or "uploaded_document",
                filename=item.get("filename"),
                page=item.get("page", 1),
                vector_score=item.get("vector_score"),
                bm25_score=item.get("bm25_score"),
                vector_rank=item.get("vector_rank"),
                bm25_rank=item.get("bm25_rank"),
                rrf_score=item.get("rrf_score"),
                text=text,
                document_id=item.get("document_id"),
                project_id=item.get("project_id"),
                user_id=item.get("user_id"),
                chunk_index=item.get("chunk_index"),

                # V2 fields
                chunk_type=item.get("chunk_type", "text"),
                caption=item.get("caption"),
                image_s3_key=image_s3_key,
                image_url=image_url,
                table_markdown=item.get("table_markdown"),

                
            )

        )

    return top_matches

def build_context(results: dict, top_k: int = 8) -> str:
    context_parts = []

    merged_results = results.get("merged_results") or []
    vector_results = results.get("vector_results") or []

    source_results = merged_results if merged_results else vector_results

    for idx, item in enumerate(source_results[:top_k]):
        text = item.get("text")

        if not text:
            continue

        filename = item.get("filename") or "uploaded_document"
        chunk_index = item.get("chunk_index")

        context_parts.append(
            f"[SOURCE {idx + 1} | {filename} | chunk {chunk_index}]\n{text}"
        )

    return "\n\n---\n\n".join(context_parts)


def build_messages(context: str, user_query: str):
    return [
        {
            "role": "system",
            "content": (
                "You are a precise private document assistant. "
                "Answer ONLY using the provided context. "
                "If the context is insufficient, say you don't know. "
                "Do not use outside knowledge. "
                "Use clean Markdown. "
                "When possible, mention the source/chunk used. "
                "For mathematical expressions, equations, formulas, and scientific notation, use valid LaTeX syntax. "
                "For block equations, use $$ ... $$. "
                "For inline equations, use $ ... $. "
                "Ensure mathematical notation is complete, properly escaped, and compatible with standard Markdown math renderers. "
            ),
        },
        {
            "role": "user",
            "content": f"""
Context:
{context}

Question:
{user_query}

Answer clearly and concisely.
""",
        },
    ]


@router.post("/ask", response_model=AskResponse)
def ask(
    req: AskRequest,
    current_user: models.User = Depends(get_current_user),
):
    try:
        user_query = req.query or req.question

        if not user_query:
            raise HTTPException(status_code=400, detail="Missing query/question")

        document_id = normalize_document_id(req.document_id)

        print("\n🔥 ASK RAW REQUEST:", req.model_dump())
        print("🔥 ORIGINAL QUERY:", user_query)
        print("🔥 CURRENT USER:", current_user.id, current_user.clerk_user_id)
        print("🔥 PROJECT FILTER:", req.project_id)
        print("🔥 DOCUMENT FILTER:", document_id)

        client = get_client()
        rewritten_query = get_search_query(client, user_query, rewrite=req.rewrite)

        print("🔥 SEARCH QUERY:", rewritten_query)

        print("🔥 FINAL FILTERS:")
        print("user_id:", current_user.id)
        print("project_id:", req.project_id)
        print("document_id:", document_id)

        results = search_chunks(
            rewritten_query,
            top_k=max(req.top_k, 8),
            user_id=current_user.id,
            project_id=req.project_id,
            document_id=document_id,
        )

        if not isinstance(results, dict):
            raise RuntimeError(f"search_chunks returned non-dict result: {type(results)}")

        top_matches = normalize_matches(results, top_k=5)
        context = build_context(results, top_k=8)

        filters = {
            "user_id": current_user.id,
            "project_id": req.project_id,
            "document_id": document_id,
        }

        if not context:
            return AskResponse(
                query=user_query,
                rewritten_query=rewritten_query,
                answer="No relevant information found in your documents.",
                top_matches=top_matches,
                sources=results,
                filters=filters,
            )

        response = client.chat.completions.create(
            model=CHAT_MODEL,
            messages=build_messages(context, user_query),
            temperature=0.2,
        )

        answer = response.choices[0].message.content or ""
        answer = normalize_math(answer)

        return AskResponse(
            query=user_query,
            rewritten_query=rewritten_query,
            answer=answer,
            top_matches=top_matches,
            sources=results,
            filters=filters,
        )

    except Exception as e:
        print("❌ ASK ERROR:", str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/ask/stream")
def ask_stream(
    req: AskRequest,
    current_user: models.User = Depends(get_current_user),
):
    def generate():
        try:
            user_query = req.query or req.question

            if not user_query:
                yield sse_event(StreamErrorEvent(message="Missing query/question"))
                return

            document_id = normalize_document_id(req.document_id)

            print("\n🔥 STREAM ASK RAW REQUEST:", req.model_dump())
            print("🔥 STREAM ORIGINAL QUERY:", user_query)
            print("🔥 STREAM CURRENT USER:", current_user.id, current_user.clerk_user_id)
            print("🔥 STREAM PROJECT FILTER:", req.project_id)
            print("🔥 STREAM DOCUMENT FILTER:", document_id)

            client = get_client()
            rewritten_query = get_search_query(client, user_query, rewrite=req.rewrite)

            print("🔥 STREAM SEARCH QUERY:", rewritten_query)
            print("🔥 STREAM FINAL FILTERS:")
            print("user_id:", current_user.id)
            print("project_id:", req.project_id)
            print("document_id:", document_id)

            results = search_chunks(
                rewritten_query,
                top_k=max(req.top_k, 8),
                user_id=current_user.id,
                project_id=req.project_id,
                document_id=document_id,
            )

            if not isinstance(results, dict):
                yield sse_event(
                    StreamErrorEvent(
                        message=f"search_chunks returned non-dict result: {type(results)}"
                    )
                )
                return

            top_matches = normalize_matches(results, top_k=5)
            context = build_context(results, top_k=8)

            filters = {
                "user_id": current_user.id,
                "project_id": req.project_id,
                "document_id": document_id,
            }

            yield sse_event(
                StreamSourcesEvent(
                    query=user_query,
                    rewritten_query=rewritten_query,
                    top_matches=top_matches,
                    filters=filters,
                )
            )

            if not context:
                yield sse_event(
                    StreamTokenEvent(
                        content="No relevant information found in your documents."
                    )
                )
                yield sse_event(StreamDoneEvent())
                return

            stream = client.chat.completions.create(
                model=CHAT_MODEL,
                messages=build_messages(context, user_query),
                temperature=0.2,
                stream=True,
            )

            for chunk in stream:
                delta = chunk.choices[0].delta.content

                if delta:
                    yield sse_event(StreamTokenEvent(content=delta))

            yield sse_event(StreamDoneEvent())

        except Exception as e:
            print("❌ STREAM ASK ERROR:", str(e))
            yield sse_event(StreamErrorEvent(message=str(e)))

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        },
    )
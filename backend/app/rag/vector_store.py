import uuid
import os
from typing import List, Dict, Any
from app.rag.bm25 import bm25_index
from app.rag.embeddings import embed_texts
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams,
    PointStruct,
    Filter,
    FieldCondition,
    MatchValue,
    PayloadSchemaType,
    FilterSelector,
)

from app.rag.embeddings import embed_texts
from app.core.config import ENABLE_RERANKING, RERANK_MODEL
from app.rag.reranker import rerank_chunks


QDRANT_COLLECTION = os.getenv(
    "QDRANT_COLLECTION",
    "multimodal_rag_chunks_bedrock",
)

BEDROCK_EMBEDDING_DIMENSION = int(
    os.getenv("BEDROCK_EMBEDDING_DIMENSION", "1024")
)



def get_qdrant_client():
    qdrant_url = os.getenv("QDRANT_URL")
    qdrant_api_key = os.getenv("QDRANT_API_KEY")

    if not qdrant_url or not qdrant_api_key:
        raise Exception("❌ Missing QDRANT_URL or QDRANT_API_KEY")

    return QdrantClient(
        url=qdrant_url,
        api_key=qdrant_api_key,
    )


def create_collection(client: QdrantClient):
    try:
        collections = client.get_collections().collections
        names = [c.name for c in collections]

        if QDRANT_COLLECTION not in names:
            client.create_collection(
                collection_name=QDRANT_COLLECTION,
                vectors_config=VectorParams(
                    size=BEDROCK_EMBEDDING_DIMENSION,
                    distance=Distance.COSINE,
                ),
            )
            print("✅ Created Qdrant collection")

        for field_name in ["user_id", "project_id", "document_id"]:
            try:
                client.create_payload_index(
                    collection_name=QDRANT_COLLECTION,
                    field_name=field_name,
                    field_schema=PayloadSchemaType.KEYWORD,
                )
            except Exception as index_error:
                if "already exists" not in str(index_error).lower():
                    print(f"⚠️ Qdrant index warning for {field_name}: {index_error}")

    except Exception as e:
        print("❌ QDRANT create_collection error:", str(e))
        raise


def build_qdrant_filter(
    user_id: str | None = None,
    project_id: str | None = None,
    document_id: str | None = None,
):
    conditions = []

    if user_id:
        conditions.append(
            FieldCondition(
                key="user_id",
                match=MatchValue(value=str(user_id)),
            )
        )

    if project_id:
        conditions.append(
            FieldCondition(
                key="project_id",
                match=MatchValue(value=str(project_id)),
            )
        )

    if document_id:
        conditions.append(
            FieldCondition(
                key="document_id",
                match=MatchValue(value=str(document_id)),
            )
        )

    if not conditions:
        return None

    return Filter(must=conditions)


def upsert_chunks(
    document_id: str,
    chunks: List[str],
    metadata: Dict[str, Any] | None = None,
) -> int:
    if not chunks:
        return 0

    try:
        client = get_qdrant_client()
        create_collection(client)

        embeddings = embed_texts(chunks)

        if not embeddings:
            raise Exception("❌ Embeddings returned empty")

        metadata = metadata or {}

        real_document_id = str(metadata.get("document_id") or document_id)
        real_project_id = str(metadata.get("project_id") or "")
        real_user_id = str(metadata.get("user_id") or "")

        print("🔥 UPSERT USER:", real_user_id)
        print("🔥 UPSERT PROJECT:", real_project_id)
        print("🔥 UPSERT DOCUMENT:", real_document_id)
        print("🔥 UPSERT CHUNKS:", len(chunks))

        points = []

        for i, (chunk, vector) in enumerate(zip(chunks, embeddings)):
            payload = {
                **metadata,
                "user_id": real_user_id,
                "project_id": real_project_id,
                "document_id": real_document_id,
                
                "chunk_index": i,
                "text": chunk,
            }

            points.append(
                PointStruct(
                    id=str(uuid.uuid4()),
                    vector=vector,
                    payload=payload,
                )
            )

        client.upsert(
            collection_name=QDRANT_COLLECTION,
            points=points,
        )

        print(f"✅ Upserted {len(points)} chunks to Qdrant")

        bm25_items = []

        for i, chunk in enumerate(chunks):
            bm25_items.append(
                {
                    "text": chunk,
                    "metadata": {
                        **metadata,
                        "user_id": real_user_id,
                        "project_id": real_project_id,
                        "document_id": real_document_id,
                        
                        "chunk_index": i,
                    },
                }
            )

        # ensure metadata consistency before indexing
        for item in bm25_items:
            item["metadata"]["document_id"] = real_document_id
            item["metadata"]["user_id"] = real_user_id
            item["metadata"]["project_id"] = real_project_id

        bm25_index.add(bm25_items)
        print("✅ BM25 index updated")
        print("🔥 BM25 TOTAL ITEMS:", len(bm25_index.items))

        return len(points)

    except Exception as e:
        print("❌ UPSERT FAILED:", str(e))
        raise

def debug_sample_payloads(client: QdrantClient):
    try:
        points, _ = client.scroll(
            collection_name=QDRANT_COLLECTION,
            limit=5,
            with_payload=True,
            with_vectors=False,
        )

        print("🔥 QDRANT SAMPLE PAYLOADS:")
        for p in points:
            payload = p.payload or {}
            print({
                "user_id": payload.get("user_id"),
                "project_id": payload.get("project_id"),
                "document_id": payload.get("document_id"),
                "document_id": payload.get("document_id"),
                "filename": payload.get("filename"),
            })

    except Exception as e:
        print("⚠️ QDRANT SAMPLE DEBUG FAILED:", str(e))




def rrf_merge(vector_results, bm25_results, k: int = 60):
    scores = {}
    items = {}

    def make_key(item):
        return (
            item.get("document_id"),
            item.get("chunk_index"),
            item.get("text"),
        )

    for rank, item in enumerate(vector_results):
        text = item.get("text")
        if not text:
            continue

        key = make_key(item)
        scores[key] = scores.get(key, 0) + 1 / (k + rank + 1)

        merged_item = item.copy()
        merged_item["vector_rank"] = rank + 1
        merged_item["bm25_rank"] = None
        merged_item.setdefault("bm25_score", None)

        items[key] = merged_item

    for rank, item in enumerate(bm25_results):
        text = item.get("text")
        if not text:
            continue

        key = make_key(item)
        scores[key] = scores.get(key, 0) + 1 / (k + rank + 1)

        if key in items:
            items[key]["bm25_score"] = item.get("bm25_score")
            items[key]["bm25_rank"] = rank + 1
        else:
            merged_item = item.copy()
            merged_item["bm25_rank"] = rank + 1
            merged_item["vector_rank"] = None
            merged_item.setdefault("vector_score", None)
            items[key] = merged_item

    merged = []

    for key, score in sorted(scores.items(), key=lambda x: x[1], reverse=True):
        merged_item = items[key]
        merged_item["rrf_score"] = float(score)
        merged.append(merged_item)

    return merged


def debug_qdrant_counts(
    client: QdrantClient,
    qdrant_filter,
):
    try:
        count_all = client.count(
            collection_name=QDRANT_COLLECTION,
            exact=True,
        )

        print("🔥 QDRANT TOTAL CHUNKS:", count_all.count)

        if qdrant_filter:
            count_filtered = client.count(
                collection_name=QDRANT_COLLECTION,
                count_filter=qdrant_filter,
                exact=True,
            )
            print("🔥 QDRANT FILTERED CHUNKS:", count_filtered.count)
        else:
            print("🔥 QDRANT FILTERED CHUNKS: no filter")

    except Exception as e:
        print("⚠️ QDRANT COUNT DEBUG FAILED:", str(e))





def rebuild_bm25_from_qdrant(
    client: QdrantClient,
    user_id: str | None = None,
    project_id: str | None = None,
    document_id: str | None = None,
):
    qdrant_filter = build_qdrant_filter(
        user_id=user_id,
        project_id=project_id,
        document_id=document_id,
    )

    points, _ = client.scroll(
        collection_name=QDRANT_COLLECTION,
        scroll_filter=qdrant_filter,
        limit=1000,
        with_payload=True,
        with_vectors=False,
    )

    bm25_items = []

    for p in points:
        payload = p.payload or {}
        text = payload.get("text")

        if not text:
            continue

        bm25_items.append(
            {
                "text": text,
                "metadata": {
                    "user_id": payload.get("user_id"),
                    "project_id": payload.get("project_id"),
                    "document_id": payload.get("document_id"),
                    "filename": payload.get("filename"),
                    "chunk_index": payload.get("chunk_index"),
                },
            }
        )

    bm25_index.add(bm25_items)

    print("✅ Rebuilt BM25 from Qdrant")
    print("🔥 BM25 REBUILT ITEMS:", len(bm25_index.items))



def search_chunks(
    query: str,
    top_k: int = 5,
    user_id: str | None = None,
    project_id: str | None = None,
    document_id: str | None = None,
):
    try:
        client = get_qdrant_client()
        create_collection(client)

        candidate_k = max(top_k * 4, 20)

        print("🔥 SEARCH QUERY:", query)
        print("🔥 TOP_K:", top_k)
        print("🔥 CANDIDATE_K:", candidate_k)

        qdrant_filter = build_qdrant_filter(
            user_id=user_id,
            project_id=project_id,
            document_id=document_id,
        )

        debug_qdrant_counts(client, qdrant_filter)
        debug_sample_payloads(client)

        query_vector = embed_texts([query])[0]

        vector_response = client.query_points(
            collection_name=QDRANT_COLLECTION,
            query=query_vector,
            query_filter=qdrant_filter,
            limit=candidate_k,
            with_payload=True,
        )

        vector_results = []

        for r in vector_response.points:
            payload = r.payload or {}

            vector_results.append(
                {
                    "vector_score": float(r.score),
                    "text": payload.get("text"),
                    "document_id": payload.get("document_id"),
                    "project_id": payload.get("project_id"),
                    "user_id": payload.get("user_id"),
                    "filename": payload.get("filename"),
                    "chunk_index": payload.get("chunk_index"),
                }
            )

        print("🔥 BM25 TOTAL ITEMS BEFORE SEARCH:", len(bm25_index.items))
        print("🔥 BM25 INDEX EXISTS BEFORE SEARCH:", bm25_index.bm25 is not None)

        if not bm25_index.bm25 or len(bm25_index.items) == 0:
            print("⚠️ BM25 empty. Rebuilding from Qdrant...")
            rebuild_bm25_from_qdrant(
                client=client,
                user_id=user_id,
                project_id=project_id,
                document_id=document_id,
            )

        print("🔥 BM25 TOTAL ITEMS AFTER REBUILD CHECK:", len(bm25_index.items))
        print("🔥 BM25 INDEX EXISTS AFTER REBUILD CHECK:", bm25_index.bm25 is not None)

        bm25_results = bm25_index.search(
            query=query,
            top_k=candidate_k,
            user_id=user_id,
            project_id=project_id,
            document_id=document_id,
        )

        print("\n🔥 VECTOR RESULTS:", len(vector_results))
        print("🔥 BM25 RESULTS:", len(bm25_results))
        print("🔥 FILTER USER:", user_id)
        print("🔥 FILTER PROJECT:", project_id)
        print("🔥 FILTER DOCUMENT:", document_id)

        if vector_results:
            print("🔥 FIRST VECTOR DOC:", vector_results[0].get("document_id"))
            print("🔥 FIRST VECTOR FILE:", vector_results[0].get("filename"))
            print("🔥 FIRST VECTOR TEXT:", vector_results[0].get("text", "")[:200])

        if bm25_results:
            print("🔥 FIRST BM25 DOC:", bm25_results[0].get("document_id"))
            print("🔥 FIRST BM25 FILE:", bm25_results[0].get("filename"))
            print("🔥 FIRST BM25 TEXT:", bm25_results[0].get("text", "")[:200])

        vector_results = [v for v in vector_results if v.get("text")]
        bm25_results = [b for b in bm25_results if b.get("text")]

        merged = rrf_merge(vector_results, bm25_results)

        print("\n🔥 RRF RESULTS:", len(merged))
        print("🔥 RERANKING ENABLED:", ENABLE_RERANKING)

        if merged:
            print("🔥 FIRST RRF TEXT:", merged[0].get("text", "")[:200])

        if ENABLE_RERANKING:
            final_results = rerank_chunks(
                query=query,
                chunks=merged,
                top_k=top_k,
            )

            final_results = final_results[:top_k]

            print("🔥 FINAL RESULTS AFTER RERANK:", len(final_results))

            if final_results:
                print(
                    "🔥 FIRST RERANKED CHUNK:",
                    final_results[0].get("text", "")[:200],
                )
                print(
                    "🔥 FIRST RERANK RANK:",
                    final_results[0].get("rerank_rank"),
                )
        else:
            final_results = merged[:top_k]
            print("⚠️ RERANKING DISABLED, USING RRF ONLY")

        return {
            "merged_results": final_results,
            "vector_results": vector_results[:candidate_k],
            "bm25_results": bm25_results[:candidate_k],
            "rrf_results": merged[:candidate_k],
            "reranking": {
                "enabled": ENABLE_RERANKING,
                "applied": ENABLE_RERANKING and len(final_results) > 0,
                "model": RERANK_MODEL,
                "candidate_k": candidate_k,
            },
        }

    except Exception as e:
        print("❌ SEARCH FAILED:", str(e))
        return {
            "merged_results": [],
            "vector_results": [],
            "bm25_results": [],
            "rrf_results": [],
            "reranking": {
                "enabled": False,
                "applied": False,
                "model": None,
                "error": str(e),
            },
        }


def delete_document_chunks(
    user_id: str,
    document_id: str,
) -> bool:
    try:
        client = get_qdrant_client()
        create_collection(client)

        qdrant_filter = build_qdrant_filter(
            user_id=str(user_id),
            document_id=str(document_id),
        )

        client.delete(
            collection_name=QDRANT_COLLECTION,
            points_selector=FilterSelector(
                filter=qdrant_filter,
            ),
        )

        print(f"✅ Deleted Qdrant chunks for document_id={document_id}")
        return True

    except Exception as e:
        print("❌ QDRANT DELETE FAILED:", str(e))
        raise
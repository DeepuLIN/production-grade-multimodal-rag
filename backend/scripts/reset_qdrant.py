from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PayloadSchemaType

QDRANT_URL = "http://localhost:6333"
COLLECTION_NAME = "notevision_chunks"

client = QdrantClient(url=QDRANT_URL)

print("🔥 Deleting Qdrant collection:", COLLECTION_NAME)

try:
    client.delete_collection(collection_name=COLLECTION_NAME)
    print("✅ Deleted")
except Exception as e:
    print("⚠️ Delete skipped:", e)

print("🔥 Recreating collection:", COLLECTION_NAME)

client.create_collection(
    collection_name=COLLECTION_NAME,
    vectors_config=VectorParams(
        size=384,
        distance=Distance.COSINE,
    ),
)

for field in ["user_id", "project_id", "document_id"]:
    client.create_payload_index(
        collection_name=COLLECTION_NAME,
        field_name=field,
        field_schema=PayloadSchemaType.KEYWORD,
    )

print("✅ Recreated successfully")
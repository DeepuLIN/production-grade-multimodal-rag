import json
import os
from typing import List

import boto3


AWS_REGION = os.getenv(
    "AWS_REGION",
    os.getenv("DEFAULT_AWS_REGION", "eu-central-1"),
)

BEDROCK_EMBEDDING_MODEL = os.getenv(
    "BEDROCK_EMBEDDING_MODEL",
    "amazon.titan-embed-text-v2:0",
)

BEDROCK_EMBEDDING_DIMENSION = int(
    os.getenv("BEDROCK_EMBEDDING_DIMENSION", "1024")
)

_client = None


def get_bedrock_client():
    global _client

    if _client is None:
        _client = boto3.client(
            "bedrock-runtime",
            region_name=AWS_REGION,
        )

    return _client


def embed_text(text: str) -> List[float]:
    if not text:
        return [0.0] * BEDROCK_EMBEDDING_DIMENSION

    client = get_bedrock_client()

    response = client.invoke_model(
        modelId=BEDROCK_EMBEDDING_MODEL,
        body=json.dumps(
            {
                "inputText": text,
                "dimensions": BEDROCK_EMBEDDING_DIMENSION,
                "normalize": True,
            }
        ),
        accept="application/json",
        contentType="application/json",
    )

    body = json.loads(response["body"].read())

    return body["embedding"]


def embed_texts(texts: List[str]) -> List[List[float]]:
    if not texts:
        return []

    return [embed_text(text) for text in texts]
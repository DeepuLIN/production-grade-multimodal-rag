from typing import List, Dict, Any

from openai import OpenAI

from app.core.config import (
    CHAT_MODEL,
    OPEN_ROUTER_API_KEY,
    OPEN_ROUTER_BASE_URL,
)


def generate_answer(question: str, contexts: List[Dict[str, Any]]) -> str:
    if not OPEN_ROUTER_API_KEY:
        raise RuntimeError("OPEN_ROUTER_API_KEY is missing")

    context_text = "\n\n".join(
        [
            f"Source {i + 1}:\n{item['text']}"
            for i, item in enumerate(contexts)
        ]
    )

    client = OpenAI(
        api_key=OPEN_ROUTER_API_KEY,
        base_url=OPEN_ROUTER_BASE_URL,
        timeout=60,
    )

    response = client.chat.completions.create(
        model=CHAT_MODEL,
        max_tokens=1000,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a helpful document question-answering assistant. "
                    "Answer only using the provided context. "
                    "If the answer is not present in the context, say you do not know."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Context:\n{context_text}\n\n"
                    f"Question:\n{question}"
                ),
            },
        ],
    )

    return response.choices[0].message.content or ""
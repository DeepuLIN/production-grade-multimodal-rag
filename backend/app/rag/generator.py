from typing import List, Dict, Any
from openai import OpenAI

from app.core.config import (
    CHAT_MODEL,
    OPEN_ROUTER_API_KEY,
    OPEN_ROUTER_BASE_URL,
)

from app.rag.math_normalizer import normalize_math


def generate_answer(question: str, contexts: List[Dict[str, Any]]) -> str:
    if not OPEN_ROUTER_API_KEY:
        raise RuntimeError("OPEN_ROUTER_API_KEY is missing")

    # build context
    context_text = "\n\n".join(
        f"Source {i + 1}:\n{item['text']}"
        for i, item in enumerate(contexts)
    )

    # 🔥 normalize BEFORE LLM
    context_text = normalize_math(context_text)

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
                    "You are a precise document QA assistant.\n"
                    "STRICT RULES:\n"
                    "- NEVER output equations in [ ]\n"
                    "- ALWAYS use LaTeX\n"
                    "- Preserve reading order\n"
                    "- Preserve complete equations from beginning to end\n"
                    "- If an equation spans multiple lines, combine it into one complete LaTeX block\n"
                    "- Never leave dangling LaTeX delimiters such as \\left or \\right without brackets\n"
                    "- Output structured Markdown only\n"
                ),
            },
            {
                "role": "user",
                "content": f"Context:\n{context_text}\n\nQuestion:\n{question}",
            },
        ],
    )

    output = response.choices[0].message.content or ""

    # 🔥 FINAL SAFETY PASS
    output = normalize_math(output)

    return output
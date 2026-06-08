from openai import OpenAI

from app.core.config import (
    OPEN_ROUTER_API_KEY,
    OPEN_ROUTER_BASE_URL,
)

SUMMARY_MODEL = "meta-llama/llama-3.1-70b-instruct"


def generate_document_summary(
    text: str,
    filename: str,
) -> str:
    """
    Generates a concise document-level summary
    once during ingestion.
    """

    if not text:
        return ""

    client = OpenAI(
        api_key=OPEN_ROUTER_API_KEY,
        base_url=OPEN_ROUTER_BASE_URL,
        timeout=120,
    )

    truncated_text = text[:20000]

    response = client.chat.completions.create(
        model=SUMMARY_MODEL,
        temperature=0.1,
        max_tokens=500,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are an expert research assistant.\n"
                    "Generate a concise document summary.\n"
                    "Focus on:\n"
                    "- Main topic\n"
                    "- Key contributions\n"
                    "- Important findings\n"
                    "- Conclusions\n"
                    "Keep the summary around 100-150 words."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Filename: {filename}\n\n"
                    f"Document Content:\n\n"
                    f"{truncated_text}"
                ),
            },
        ],
    )

    return response.choices[0].message.content or ""


def generate_cross_document_summary(
    summaries: list[dict],
    query: str | None = None,
) -> str:
    if not summaries:
        return "No document summaries available."

    combined = "\n\n".join(
        [
            f"Document: {s['filename']}\n{s['summary']}"
            for s in summaries
            if s.get("summary")
        ]
    )

    q = (query or "").lower()

    is_compare = any(
        term in q
        for term in ["compare", "comparison", "similarities", "differences", "versus", " vs "]
    )

    if is_compare:
        instruction = (
            "Compare the provided documents only using the supplied summaries.\n"
            "Identify main topics, similarities, differences, document-specific strengths, "
            "and overall conclusions.\n"
            "Do not add outside knowledge."
        )
    else:
        instruction = (
            "Summarize the provided documents only using the supplied summaries.\n"
            "Give a clear project-level overview.\n"
            "Summarize each document briefly, then mention common themes if they are clearly supported.\n"
            "Do not compare unless the user explicitly asks for comparison.\n"
            "Do not add outside knowledge."
        )

    client = OpenAI(
        api_key=OPEN_ROUTER_API_KEY,
        base_url=OPEN_ROUTER_BASE_URL,
        timeout=120,
    )

    response = client.chat.completions.create(
        model=SUMMARY_MODEL,
        temperature=0.1,
        max_tokens=1000,
        messages=[
            {
                "role": "system",
                "content": instruction,
            },
            {
                "role": "user",
                "content": (
                    f"User request:\n{query or 'Summarize the uploaded documents.'}\n\n"
                    f"Available document summaries:\n\n{combined}"
                ),
            },
        ],
    )

    return response.choices[0].message.content or ""
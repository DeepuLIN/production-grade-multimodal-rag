from typing import List


def chunk_text(text: str, chunk_size: int = 800, overlap: int = 120) -> List[str]:
    cleaned = " ".join(text.split())

    if not cleaned:
        return []

    chunks = []
    start = 0

    while start < len(cleaned):
        end = start + chunk_size
        chunk = cleaned[start:end]

        if chunk.strip():
            chunks.append(chunk.strip())

        start = end - overlap

        if start >= len(cleaned):
            break

    return chunks
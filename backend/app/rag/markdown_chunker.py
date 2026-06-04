import re
from typing import List


MAX_CHUNK_SIZE = 1200
CHUNK_OVERLAP = 200


def _split_large_section(
    text: str,
    max_chunk_size: int = MAX_CHUNK_SIZE,
    overlap: int = CHUNK_OVERLAP,
) -> List[str]:
    """
    Fallback splitter for very large markdown sections.
    """

    if len(text) <= max_chunk_size:
        return [text.strip()]

    chunks = []
    start = 0

    while start < len(text):
        end = start + max_chunk_size
        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        start = end - overlap

    return chunks


def chunk_markdown(
    markdown_text: str,
    max_chunk_size: int = MAX_CHUNK_SIZE,
    overlap: int = CHUNK_OVERLAP,
) -> List[str]:
    """
    Markdown-aware chunking.

    Splits on:
    # Heading
    ## Heading
    ### Heading

    Preserves section structure before size-based splitting.
    """

    if not markdown_text:
        return []

    # -------------------------
    # Split by markdown headers
    # -------------------------

    pattern = r"(?=^#{1,6}\s)"
    sections = re.split(pattern, markdown_text, flags=re.MULTILINE)

    sections = [
        section.strip()
        for section in sections
        if section.strip()
    ]

    final_chunks = []

    for section in sections:

        # Small section → keep intact
        if len(section) <= max_chunk_size:
            final_chunks.append(section)
            continue

        # Large section → split further
        section_chunks = _split_large_section(
            section,
            max_chunk_size=max_chunk_size,
            overlap=overlap,
        )

        final_chunks.extend(section_chunks)

    return final_chunks
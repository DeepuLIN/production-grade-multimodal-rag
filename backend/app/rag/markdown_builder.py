from typing import Any


def build_markdown_document(
    filename: str,
    text: str,
    image_data: list[dict[str, Any]] | None = None,
) -> str:
    image_data = image_data or []

    parts = [
        f"# {filename}",
        "",
        "## Extracted Text",
        "",
        text.strip(),
    ]

    if image_data:
        parts.extend(["", "## Image / Page Captions", ""])

        for img in image_data:
            page = img.get("page", "unknown")
            caption = img.get("caption", "").strip()

            if caption:
                parts.extend([
                    f"### Page {page}",
                    "",
                    caption,
                    "",
                ])

    return "\n".join(parts).strip()
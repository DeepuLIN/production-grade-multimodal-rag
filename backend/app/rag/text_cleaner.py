import re


def clean_ocr_text(text: str) -> str:
    if not text:
        return ""

    # fix broken line hyphenation
    text = re.sub(r"-\n", "", text)

    # normalize newlines
    text = text.replace("\r", "\n")

    # remove excessive whitespace
    text = re.sub(r"\s+", " ", text)

    # fix weird spacing around symbols
    text = re.sub(r"\s+([,.;:])", r"\1", text)

    return text.strip()
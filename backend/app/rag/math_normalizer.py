import re


def normalize_math(text: str) -> str:
    """
    Normalizes common OCR/LLM math formatting issues.
    - Converts [ equation ] to $$ equation $$
    - Fixes broken LaTeX delimiters like \\left without bracket
    - Cleans spacing around display math
    """

    def bracket_replacer(match):
        content = match.group(1).strip()

        is_math = any(
            sym in content
            for sym in [
                "=",
                "_",
                "^",
                "\\frac",
                "\\sum",
                "\\cdot",
                "\\sqrt",
                "\\lambda",
                "\\hat",
            ]
        )

        if is_math:
            return f"\n\n$$\n{content}\n$$\n\n"

        return match.group(0)

    text = re.sub(r"\[\s*([\s\S]*?)\s*\]", bracket_replacer, text)

    # Fix common broken LaTeX from OCR/LLM output
    text = re.sub(r"\\left\s*\n?\s*\+", r"+", text)
    text = re.sub(r"\\right\s*\n?\s*\+", r"+", text)

    text = re.sub(r"\\left\s*$", r"", text, flags=re.MULTILINE)
    text = re.sub(r"\\right\s*$", r"", text, flags=re.MULTILINE)

    # If \left is followed directly by expression text, make it \left(
    text = re.sub(r"\\left\s+(?=[A-Za-z0-9\\(])", r"\\left(", text)

    # If \right is dangling before line/end, make it \right)
    text = re.sub(r"\\right\s*(?=\n|\$)", r"\\right)", text)

    # Clean display math spacing
    text = re.sub(r"\$\$\s+", "$$\n", text)
    text = re.sub(r"\s+\$\$", "\n$$", text)

    return text
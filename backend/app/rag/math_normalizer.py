import re


def normalize_math(text: str) -> str:
    """
    Converts OCR-style bracket math into LaTeX.
    [ equation ] → $$ equation $$
    """

    def replacer(match):
        content = match.group(1)

        # detect math-like expressions
        if any(sym in content for sym in ["=", "_", "^", "\\frac", "\\sum", "\\cdot"]):
            return f"$$ {content} $$"

        return match.group(0)

    # convert [ ... ] → $$ ... $$
    text = re.sub(r"\[\s*([\s\S]*?)\s*\]", replacer, text)

    return text
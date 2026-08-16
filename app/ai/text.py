import re


def normalise_text(text: str) -> str:
    text = text.replace("\x00", " ")
    text = re.sub(r"\s+", " ", text).strip()
    return text


def safe_excerpt(text: str, limit: int = 340) -> str:
    text = normalise_text(text)
    if len(text) <= limit:
        return text
    return text[: limit - 1].rstrip() + "…"

import re

def sanitize_text(text: str) -> str:
    # Industry standard: Basic strip and lowercase, let LLM handle nuance
    text = text.lower().strip()
    return re.sub(r"[^\w\s]", "", text)
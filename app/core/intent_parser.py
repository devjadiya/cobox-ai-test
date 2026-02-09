from app.llm.openai_client import parse_intent as ai_parse

def parse_intent(text: str):
    return ai_parse(text)

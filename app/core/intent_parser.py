# app/core/intent_parser.py
from app.llm.openai_client import generate_spatial_layout

def parse_intent(text: str):
    """Bridge to the LLM Spatial Engine."""
    return generate_spatial_layout(text)
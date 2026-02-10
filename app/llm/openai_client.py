# app/llm/openai_client.py
import json
from openai import OpenAI
from app.settings import settings

client = OpenAI(api_key=settings.OPENAI_API_KEY)

def generate_spatial_layout(text: str):
    """Extracts high-level architectural plan, leaves math to Python."""
    
    SYSTEM_PROMPT = """
    You are a Lead Level Designer. Analyze the prompt and extract construction parameters.
    
    OUTPUT JSON SCHEMA:
    {
      "layout": {
        "buildings": [{"floors": 2}, {"floors": 5}, {"floors": 1}], 
        "road_style": "loop", 
        "forest_density": "high"
      },
      "environment": {
        "Brightness": 10.0,
        "TimeOfDay": 14.0,
        "Density": 0.05
      }
    }
    
    RULES:
    - If user asks for "City", generate 10+ buildings in the list.
    - If "Cyberpunk", set TimeOfDay to 20.0 (Night).
    - If "Forest", set forest_density to "high".
    """
    
    try:
        response = client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"Create Blueprint for: {text}"}
            ],
            response_format={"type": "json_object"},
            max_tokens=1000
        )
        return json.loads(response.choices[0].message.content)
    except Exception:
        # Robust Fallback
        return {
            "layout": {
                "buildings": [{"floors": 2}, {"floors": 2}, {"floors": 3}], 
                "road_style": "loop"
            },
            "environment": {"Brightness": 10}
        }
# app/llm/openai_client.py
import json
from openai import OpenAI
from app.settings import settings

client = OpenAI(api_key=settings.OPENAI_API_KEY)

def generate_spatial_layout(text: str):
    """
    Asks GPT for a structural blueprint and a road navigation path.
    """
    SYSTEM_PROMPT = """
    You are a Senior Level Designer. Create a scene blueprint in JSON.
    
    1. ROAD PATH: Return a list of moves for a single connected road.
       Valid moves: "straight", "turn", "ramp", "bridge".
       Example: ["straight", "straight", "turn", "ramp", "straight", "bridge", "turn"]
       
    2. BUILDINGS: List of building footprints (floors: 1-6).
    
    3. FOREST: Density level (low/medium/high).
    
    OUTPUT SCHEMA:
    {
      "road_path": ["straight", "turn", ...],
      "buildings": [{"floors": 3}, {"floors": 5}],
      "forest": "high"
    }
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
        # Fallback path if AI fails
        return {
            "road_path": ["straight", "straight", "turn", "straight", "ramp", "turn", "straight"],
            "buildings": [{"floors": 2}, {"floors": 4}, {"floors": 3}],
            "forest": "high"
        }
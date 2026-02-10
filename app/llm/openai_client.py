# app/llm/openai_client.py
import json
import logging
from openai import OpenAI
from app.settings import settings

client = OpenAI(api_key=settings.OPENAI_API_KEY)
logger = logging.getLogger("cobox-ai.llm")

def generate_spatial_layout(text: str):
    """
    Translates user text into a strict Construction Blueprint.
    """
    SYSTEM_PROMPT = """
    You are a Technical Level Designer for a Racing Game.
    Convert the user's prompt into a structural JSON blueprint.
    
    ASSET LIBRARY (Strict):
    - Roads: "straight", "turn_90", "turn_slight", "curve_sharp", "ramp_gentle", "ramp_steep", "bridge_start", "loop_360", "u_turn", "mercedes", "splitter"
    - Buildings: List of floor counts (e.g. [2, 5, 1]).
    
    LOGIC RULES:
    1. If user asks for "Roads Only", return "buildings": [].
    2. If user asks for "Complex Road", generates a list of 20-30 road segments mixing straights, turns, and ramps.
    3. If user asks for "Circular/Loop", include "turn_90" or "loop_360".
    
    OUTPUT SCHEMA:
    {
      "layout": {
        "buildings": [int, int, ...],  // Array of floor counts. Empty if no buildings requested.
        "road_sequence": [str, str, ...], // List of asset keys from library above
        "forest_density": 0.0 - 1.0
      },
      "environment": {
        "time": float, // 0-24
        "brightness": float // 0-10
      }
    }
    """
    
    try:
        response = client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT}, 
                {"role": "user", "content": f"Generate Blueprint: {text}"}
            ],
            response_format={"type": "json_object"},
            max_tokens=2000
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        logger.error(f"LLM Error: {e}")
        # Minimal Fallback (Safe Mode)
        return {
            "layout": {
                "buildings": [],
                "road_sequence": ["straight", "straight", "turn_90", "straight"],
                "forest_density": 0.1
            },
            "environment": {"time": 12.0, "brightness": 10.0}
        }
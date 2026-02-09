# app/llm/openai_client.py

import json
import logging
from typing import Dict, Any

from openai import OpenAI
from app.settings import settings

# --------------------------------------------------
# LOGGING
# --------------------------------------------------
logger = logging.getLogger("cobox-ai.llm")

# --------------------------------------------------
# CLIENT INIT
# --------------------------------------------------
if not settings.OPENAI_API_KEY:
    raise RuntimeError("OPENAI_API_KEY missing in .env")

client = OpenAI(api_key=settings.OPENAI_API_KEY)
MODEL = settings.OPENAI_MODEL

# --------------------------------------------------
# JSON SAFE EXTRACTOR
# --------------------------------------------------
def _safe_json(text: str) -> Dict[str, Any]:
    """
    Extract JSON safely even if model wraps text.
    """
    try:
        return json.loads(text)
    except Exception:
        start = text.find("{")
        end = text.rfind("}") + 1
        if start == -1 or end == -1:
            raise ValueError("Model did not return JSON")
        return json.loads(text[start:end])

# --------------------------------------------------
# INTENT PARSER
# --------------------------------------------------
def parse_intent(text: str) -> Dict[str, Any]:
    """
    Convert user prompt into structured scene intent.
    """

    SYSTEM_PROMPT = """
You are an AI Game Scene Planner for a 3D Unreal-like engine.

STRICT RULES:
- Return ONLY valid JSON.
- No markdown.
- No explanations.
- No comments.
- No trailing commas.

Scene Types:
city, building, track, open_world, interior, custom

Objects Allowed:
building, road, tree, door, vehicle, decor, water, bridge, terrain, light

Output Schema:
{
  "scene_type": "string",
  "objects": [
    {"type": "building", "count": 3},
    {"type": "road", "count": 1}
  ],
  "notes": "optional string",
  "allow_physics": false,
  "allow_ai_agents": false,
  "allow_multiplayer": false
}

Guidelines:
- Count range: 1-50
- Cyberpunk → more lights & decor
- Forest → more trees
- Track → more roads
- Interior → more doors & walls
"""

    try:
        response = client.chat.completions.create(
            model=MODEL,
            temperature=0.2,
            max_tokens=400,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": text},
            ],
        )

        raw = response.choices[0].message.content
        intent = _safe_json(raw)

        logger.info("Intent parsed: %s", intent)
        return intent

    except Exception as e:
        logger.error("Intent parsing failed: %s", e)
        # Fallback
        return {
            "scene_type": "custom",
            "objects": [{"type": "decor", "count": 5}],
            "notes": "fallback",
            "allow_physics": False,
            "allow_ai_agents": False,
            "allow_multiplayer": False,
        }

# --------------------------------------------------
# SCENE ENHANCER
# --------------------------------------------------
def enhance_scene(scene_json: Dict[str, Any], user_text: str) -> Dict[str, Any]:
    """
    Improve visual richness without breaking structure.
    """

    SYSTEM_PROMPT = """
You are a 3D Game Scene Enhancer.

Rules:
- Do NOT delete existing actors.
- Only ADD decor, lights, trees, props.
- Keep structure identical.
- Return FULL valid JSON.
- No markdown.
"""

    try:
        response = client.chat.completions.create(
            model=MODEL,
            temperature=0.6,
            max_tokens=1500,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": f"User Prompt: {user_text}\nScene JSON:\n{json.dumps(scene_json)}",
                },
            ],
        )

        raw = response.choices[0].message.content
        enhanced = _safe_json(raw)

        logger.info("Scene enhanced")
        return enhanced

    except Exception as e:
        logger.error("Enhancement failed: %s", e)
        return scene_json

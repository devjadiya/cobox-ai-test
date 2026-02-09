# app/core/intent_parser.py
import re
from typing import Dict, Any

def parse_intent(text: str) -> Dict[str, Any]:
    """Senior Level Entity Extraction and Theme Mapping."""
    text = text.lower()
    
    intent = {
        "theme": "generic",
        "objects": [],
        "environment": {"foliage_density": 0, "has_water": False}
    }

    # 1. Theme Detection
    if any(word in text for word in ["green", "forest", "nature", "jungle"]):
        intent["theme"] = "nature"
        intent["environment"]["foliage_density"] = 50
    elif any(word in text for word in ["cyber", "neon", "sci-fi", "city"]):
        intent["theme"] = "cyberpunk"
        intent["environment"]["foliage_density"] = 10

    # 2. Entity Extraction (Regex for "N items")
    patterns = {
        "building": r"(\d+)\s*(building|house|home|structure)",
        "road": r"(\d+)\s*(road|track|street|path)",
        "tree": r"(\d+)\s*(tree|bush|plant|greenery)",
        "vehicle": r"(\d+)\s*(car|vehicle|truck|automobile)"
    }

    for obj_type, pattern in patterns.items():
        match = re.search(pattern, text)
        if match:
            intent["objects"].append({"type": obj_type, "count": int(match.group(1))})
        elif obj_type in text:
            # Default if no number mentioned
            intent["objects"].append({"type": obj_type, "count": 5 if obj_type != "vehicle" else 1})

    # 3. Fallback for "Green Surroundings" or "Trees"
    if "green" in text or "tree" in text:
        if not any(obj["type"] == "tree" for obj in intent["objects"]):
            intent["objects"].append({"type": "tree", "count": 40})

    return intent
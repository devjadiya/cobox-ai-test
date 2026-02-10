# app/core/road_logic.py
import random

# --- CONNECTIVITY RULES ---
TYPE_SOLID = "Solid" # Standard connection (02, 03, 04, etc.)
TYPE_PIN = "Pin"     # Socket connection (11, 14)

# --- THE 25 ASSETS (Source of Truth) ---
ROAD_DB = {
    # --- SOLID STRAIGHTS ---
    "BP_RaceTrack_Wb_02": {"type": TYPE_SOLID, "tags": ["straight", "basic"], "len": 900, "curve": 0, "z": 0},
    "BP_RaceTrack_Wb_03": {"type": TYPE_SOLID, "tags": ["straight", "bump"], "len": 900, "curve": 0, "z": 0},
    "BP_RaceTrack_Wb_05": {"type": TYPE_SOLID, "tags": ["straight", "wide"], "len": 900, "curve": 0, "z": 0},
    "BP_RaceTrack_Wb_06": {"type": TYPE_SOLID, "tags": ["straight", "gap"], "len": 900, "curve": 0, "z": 0},
    "BP_RaceTrack_Wb_07": {"type": TYPE_SOLID, "tags": ["straight", "s_bend"], "len": 1200, "curve": 0, "z": 0},
    "BP_RaceTrack_Wb_17": {"type": TYPE_SOLID, "tags": ["straight", "long_bump"], "len": 1200, "curve": 0, "z": 0},
    
    # --- SOLID TURNS ---
    "BP_RaceTrack_Wb_04": {"type": TYPE_SOLID, "tags": ["turn", "90"], "len": 900, "curve": 90, "z": 0},
    "BP_RaceTrack_Wb_12": {"type": TYPE_SOLID, "tags": ["turn", "slight"], "len": 900, "curve": 15, "z": 0},
    "BP_RaceTrack_Wb_13": {"type": TYPE_SOLID, "tags": ["turn", "sharp"], "len": 900, "curve": 90, "z": 0},
    "BP_RaceTrack_Wb_18": {"type": TYPE_SOLID, "tags": ["turn", "u_turn"], "len": 900, "curve": 180, "z": 0},

    # --- SOLID ELEVATION (Ramps/Hills) ---
    "BP_RaceTrack_Wb_08": {"type": TYPE_SOLID, "tags": ["ramp", "gentle"], "len": 900, "curve": 0, "z": 200},
    "BP_RaceTrack_Wb_09": {"type": TYPE_SOLID, "tags": ["ramp", "steep"], "len": 900, "curve": 0, "z": 400},
    "BP_RaceTrack_Wb_15": {"type": TYPE_SOLID, "tags": ["ramp", "spiral"], "len": 1200, "curve": 45, "z": 300},
    "BP_RaceTrack_Wb_16": {"type": TYPE_SOLID, "tags": ["ramp", "spiral_steep"], "len": 1200, "curve": 90, "z": 600},
    "BP_RaceTrack_Wb_19": {"type": TYPE_SOLID, "tags": ["ramp", "down"], "len": 1200, "curve": 90, "z": -400},
    "BP_RaceTrack_Wb_20": {"type": TYPE_SOLID, "tags": ["loop"], "len": 2000, "curve": 0, "z": 800}, # 360 Loop
    "BP_RaceTrack_Wb_21": {"type": TYPE_SOLID, "tags": ["hill", "down"], "len": 1200, "curve": 0, "z": -200},

    # --- BRIDGE & SPECIALS ---
    "BP_RaceTrack_Wb_10": {"type": TYPE_SOLID, "tags": ["bridge", "start"], "len": 1200, "curve": 0, "z": 100},
    "BP_RaceTrack_Wb_25": {"type": TYPE_SOLID, "tags": ["bridge", "segment"], "len": 1200, "curve": 0, "z": 0},
    "BP_RaceTrack_Wb_22": {"type": TYPE_SOLID, "tags": ["split"], "len": 1200, "curve": 0, "z": 0},
    "BP_RaceTrack_Wb_23": {"type": TYPE_SOLID, "tags": ["junction", "mercedes"], "len": 1200, "curve": 0, "z": 0},

    # --- PINS (Socket Connectors) ---
    "BP_RaceTrack_Wb_11": {"type": TYPE_PIN, "tags": ["connector"], "len": 600, "curve": 0, "z": 0},
    "BP_RaceTrack_Wb_14": {"type": TYPE_PIN, "tags": ["turn", "t_junction"], "len": 900, "curve": 90, "z": 0},

    # --- CAPS/DEAD ENDS ---
    "BP_RaceTrack_Wb_01": {"type": TYPE_SOLID, "tags": ["cap", "dead_end"], "len": 300, "curve": 0, "z": 0},
    "BP_RaceTrack_Wb_24": {"type": TYPE_SOLID, "tags": ["cap", "return"], "len": 900, "curve": 180, "z": 0},
}

def resolve_next_asset(current_type: str, intent: str) -> dict:
    """
    Selects the best asset ID based on current connection type and AI intent.
    intent: 'straight', 'turn', 'ramp', 'bridge'
    """
    candidates = []
    
    # 1. Filter by Connection Compatibility
    for aid, data in ROAD_DB.items():
        if data["type"] == current_type:
            candidates.append(aid)
            
    # 2. Filter by Intent
    best_matches = []
    for aid in candidates:
        tags = ROAD_DB[aid]["tags"]
        if intent == "turn" and "turn" in tags: best_matches.append(aid)
        elif intent == "ramp" and "ramp" in tags: best_matches.append(aid)
        elif intent == "bridge" and "bridge" in tags: best_matches.append(aid)
        elif intent == "straight" and "straight" in tags: best_matches.append(aid)
    
    # Fallback to any valid connector if specific intent fails
    if not best_matches: 
        # Prefer basic straight/connector to avoid getting stuck
        defaults = [k for k in candidates if "straight" in ROAD_DB[k]["tags"]]
        return ROAD_DB[defaults[0] if defaults else candidates[0]]
    
    selected_id = random.choice(best_matches)
    return {"id": selected_id, **ROAD_DB[selected_id]}
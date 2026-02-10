# app/core/road_logic.py
import random
from typing import List, Dict

# --- CONNECTION TYPES ---
TYPE_SOLID = "solid"  # Standard connection (Assets 01-10, 12, 13, 17-25)
TYPE_PIN = "pin"      # Socket connection (Assets 11, 14)

# --- ASSET DEFINITIONS (The 25 Assets) ---
ROAD_ASSETS = {
    # --- BASICS (Solid) ---
    "straight": {
        "id": "BP_RaceTrack_Wb_02", 
        "type": TYPE_SOLID, 
        "length": 900, 
        "curve": 0,
        "z_change": 0
    },
    "curve_slight": {
        "id": "BP_RaceTrack_Wb_12", 
        "type": TYPE_SOLID, 
        "length": 900, 
        "curve": 15,
        "z_change": 0
    },
    "curve_sharp": {
        "id": "BP_RaceTrack_Wb_13", 
        "type": TYPE_SOLID, 
        "length": 900, 
        "curve": 90,
        "z_change": 0
    },
    "turn_90": {
        "id": "BP_RaceTrack_Wb_04", 
        "type": TYPE_SOLID, 
        "length": 900, 
        "curve": 90,
        "z_change": 0
    },
    "u_turn": {
        "id": "BP_RaceTrack_Wb_18", 
        "type": TYPE_SOLID, 
        "length": 900, 
        "curve": 180,
        "z_change": 0
    },
    
    # --- COMPLEX / PINS ---
    "junction_pin": {
        "id": "BP_RaceTrack_Wb_11", 
        "type": TYPE_PIN, 
        "length": 600, 
        "curve": 0,
        "z_change": 0
    },
    "t_junction_left": {
        "id": "BP_RaceTrack_Wb_14", 
        "type": TYPE_PIN, 
        "length": 900, 
        "curve": 90,
        "z_change": 0
    },

    # --- ELEVATION (Ramps & Spirals) ---
    "ramp_gentle": {
        "id": "BP_RaceTrack_Wb_08", 
        "type": TYPE_SOLID, 
        "length": 900, 
        "curve": 0,
        "z_change": 200 
    },
    "ramp_steep": {
        "id": "BP_RaceTrack_Wb_09", 
        "type": TYPE_SOLID, 
        "length": 900, 
        "curve": 0,
        "z_change": 400
    },
    "spiral_up": {
        "id": "BP_RaceTrack_Wb_15", 
        "type": TYPE_SOLID, 
        "length": 1200, 
        "curve": 45, 
        "z_change": 300
    },
    "spiral_steep": {
        "id": "BP_RaceTrack_Wb_16", 
        "type": TYPE_SOLID, 
        "length": 1200, 
        "curve": 90, 
        "z_change": 600
    },
    "loop_360": {
        "id": "BP_RaceTrack_Wb_20", 
        "type": TYPE_SOLID, 
        "length": 2000, 
        "curve": 0, 
        "z_change": 800 # High elevation change
    },

    # --- SPECIALS ---
    "bridge_start": {
        "id": "BP_RaceTrack_Wb_10", 
        "type": TYPE_SOLID, 
        "length": 1200, 
        "curve": 0,
        "z_change": 100
    },
    "bridge_connector": {
        "id": "BP_RaceTrack_Wb_25", 
        "type": TYPE_SOLID, 
        "length": 1200, 
        "curve": 0,
        "z_change": 0
    },
    "mercedes_junction": {
        "id": "BP_RaceTrack_Wb_23", 
        "type": TYPE_SOLID, 
        "length": 1200, 
        "curve": 0,
        "z_change": 0
    },
    "bump_long": {
        "id": "BP_RaceTrack_Wb_17", 
        "type": TYPE_SOLID, 
        "length": 1200, 
        "curve": 0,
        "z_change": 0
    },

    # --- CAPS ---
    "dead_end": {
        "id": "BP_RaceTrack_Wb_01", 
        "type": TYPE_SOLID, 
        "length": 300, 
        "curve": 0,
        "z_change": 0
    },
    "return_loop": {
        "id": "BP_RaceTrack_Wb_24", 
        "type": TYPE_SOLID, 
        "length": 900, 
        "curve": 180,
        "z_change": 0
    }
}

# --- LOGIC SOLVER ---

def get_next_piece(current_type: str, intent: str = "straight") -> dict:
    """Decides the next piece based on connection type compatibility."""
    options = []
    
    # 1. Filter by Type Compatibility (Solid connects to Solid, Pin to Pin)
    for key, data in ROAD_ASSETS.items():
        if data["type"] == current_type:
            options.append(key)
    
    # 2. Filter by Intent (Turn, Climb, or Straight)
    if intent == "turn":
        # Look for curves
        valid = [k for k in options if ROAD_ASSETS[k]["curve"] != 0]
        if valid: return ROAD_ASSETS[random.choice(valid)]
    
    elif intent == "climb":
        # Look for positive Z change
        valid = [k for k in options if ROAD_ASSETS[k]["z_change"] > 0]
        if valid: return ROAD_ASSETS[random.choice(valid)]
        
    # Default: Straight/Forward (Zero curve, Zero Z)
    valid = [k for k in options if ROAD_ASSETS[k]["curve"] == 0 and ROAD_ASSETS[k]["z_change"] == 0]
    
    # Fallback if no specific straight piece matches criteria
    if not valid: return ROAD_ASSETS["straight"]
    
    return ROAD_ASSETS[random.choice(valid)]

def generate_road_sequence(steps: int, loop: bool = False) -> List[Dict]:
    """Generates a connected list of road assets."""
    sequence = []
    
    # Always start with a solid straight piece
    current_piece = ROAD_ASSETS["straight"]
    sequence.append(current_piece)
    
    for i in range(steps):
        next_type = current_piece["type"]
        
        # Define intent based on step count
        intent = "straight"
        if i % 6 == 0: intent = "turn"   # Turn every 6 segments
        elif i == 3: intent = "climb"    # Climb early on
        
        # Get next compatible piece
        next_piece = get_next_piece(next_type, intent)
        sequence.append(next_piece)
        
        current_piece = next_piece

    # Cap the end
    if loop:
        sequence.append(ROAD_ASSETS["return_loop"])
    else:
        sequence.append(ROAD_ASSETS["dead_end"])
        
    return sequence
# app/core/scene_compiler.py
import random
import math

# ==============================================================================
# 1. ASSET DATABASE (Strict "Pin" vs "Solid" Definitions)
# ==============================================================================
TYPE_SOLID = 0
TYPE_PIN = 1

ROAD_DB = {
    # --- SOLID GROUP (Connects to Solid) ---
    "straight":         {"id": "BP_RaceTrack_Wb_02", "type": TYPE_SOLID, "len": 900, "curve": 0, "z": 0},
    "straight_bump":    {"id": "BP_RaceTrack_Wb_03", "type": TYPE_SOLID, "len": 900, "curve": 0, "z": 0},
    "turn_90":          {"id": "BP_RaceTrack_Wb_04", "type": TYPE_SOLID, "len": 900, "curve": 90, "z": 0},
    "turn_slight":      {"id": "BP_RaceTrack_Wb_12", "type": TYPE_SOLID, "len": 900, "curve": 15, "z": 0},
    "ramp_gentle":      {"id": "BP_RaceTrack_Wb_08", "type": TYPE_SOLID, "len": 900, "curve": 0, "z": 200},
    "ramp_steep":       {"id": "BP_RaceTrack_Wb_09", "type": TYPE_SOLID, "len": 900, "curve": 0, "z": 400},
    "bridge_start":     {"id": "BP_RaceTrack_Wb_10", "type": TYPE_SOLID, "len": 1200, "curve": 0, "z": 100},
    "bridge_segment":   {"id": "BP_RaceTrack_Wb_25", "type": TYPE_SOLID, "len": 1200, "curve": 0, "z": 0},
    "loop_360":         {"id": "BP_RaceTrack_Wb_20", "type": TYPE_SOLID, "len": 2000, "curve": 0, "z": 800},
    "u_turn":           {"id": "BP_RaceTrack_Wb_18", "type": TYPE_SOLID, "len": 900, "curve": 180, "z": 0},
    "mercedes":         {"id": "BP_RaceTrack_Wb_23", "type": TYPE_SOLID, "len": 1200, "curve": 0, "z": 0},
    "splitter":         {"id": "BP_RaceTrack_Wb_22", "type": TYPE_SOLID, "len": 1200, "curve": 0, "z": 0},
    "return_loop":      {"id": "BP_RaceTrack_Wb_24", "type": TYPE_SOLID, "len": 900, "curve": 180, "z": 0},
    
    # --- PIN GROUP (Connects to Pin) ---
    "pin_t_junction":   {"id": "BP_RaceTrack_Wb_14", "type": TYPE_PIN, "len": 900, "curve": 90, "z": 0}, 
    
    # --- ADAPTER (The Magic Piece) ---
    # Asset 11 connects Solid to Pin (or Pin to Solid).
    "adapter_pin":      {"id": "BP_RaceTrack_Wb_11", "type": TYPE_PIN, "len": 600, "curve": 0, "z": 0}, 
}

BUILDING_DB = {
    "floor": [{"class": f"BP_FloorAsset_Wb_{str(i).zfill(2)}_C", "path": f"/WorldBuilder/Core/Actors/Placeable/Library/Floor/BP_FloorAsset_Wb_{str(i).zfill(2)}.BP_FloorAsset_Wb_{str(i).zfill(2)}_C"} for i in range(1, 12)],
    "wall": [{"class": f"BP_WallAsset_Wb_{str(i).zfill(2)}_C", "path": f"/WorldBuilder/Core/Actors/Placeable/Library/Wall/BP_WallAsset_Wb_{str(i).zfill(2)}.BP_WallAsset_Wb_{str(i).zfill(2)}_C"} for i in range(1, 13)],
    "ceiling": [{"class": "BP_CeilingAsset_Wb_01_C", "path": "/WorldBuilder/Core/Actors/Placeable/Library/Ceiling/BP_CeilingAsset_Wb_01.BP_CeilingAsset_Wb_01_C"}],
    "decor": [{"class": f"BP_DecorAsset_Wb_{str(i).zfill(2)}_C", "path": f"/WorldBuilder/Core/Actors/Placeable/Library/Decors/BP_DecorAsset_Wb_{str(i).zfill(2)}.BP_DecorAsset_Wb_{str(i).zfill(2)}_C"} for i in range(1, 34)]
}

# ==============================================================================
# 2. CORE COMPILER
# ==============================================================================
GRID_UNIT = 600.0
WALL_OFFSET = 300.0
FLOOR_HEIGHT = 400.0

def _actor(asset_id, x, y, z, yaw=0.0):
    """Generates valid JSON for an actor."""
    # Auto-resolve path based on ID logic
    if "BP_RaceTrack" in asset_id:
        c_path = f"/WorldBuilder/Core/Actors/Placeable/Library/Tracks/{asset_id}.{asset_id}_C"
    else:
        # Fallback for manual building assets passed as dicts
        return None 

    return {
        "AssetClass": f"{asset_id}_C",
        "AssetClassPath": c_path,
        "Transform": {
            "Location": {"X": float(x), "Y": float(y), "Z": float(z)},
            "Rotation": {"Pitch": 0.0, "Yaw": float(yaw), "Roll": 0.0},
            "Scale": {"X": 1.0, "Y": 1.0, "Z": 1.0}
        },
        "OcaData": {"CollisionProfile": "BlockAllDynamic", "Physics": False, "Shadow": True}
    }

def _building_actor(asset_data, x, y, z, yaw=0.0):
    """Specific helper for building parts which have complex paths."""
    return {
        "AssetClass": asset_data["class"],
        "AssetClassPath": asset_data["path"],
        "Transform": {
            "Location": {"X": float(x), "Y": float(y), "Z": float(z)},
            "Rotation": {"Pitch": 0.0, "Yaw": float(yaw), "Roll": 0.0},
            "Scale": {"X": 1.0, "Y": 1.0, "Z": 1.0}
        },
        "OcaData": {"CollisionProfile": "BlockAllDynamic", "Physics": False, "Shadow": True}
    }

def compile_scene(blueprint: dict) -> dict:
    placeables = []
    
    # 1. EXTRACT AI INTENT
    layout = blueprint.get("layout", {})
    building_list = layout.get("buildings", [])
    road_intents = layout.get("road_sequence", [])
    
    # Grid tracker
    occupied_grid = set()
    def mark_grid(gx, gy, radius=1):
        for i in range(-radius, radius+1):
            for j in range(-radius, radius+1):
                occupied_grid.add((int(gx)+i, int(gy)+j))

    # ---------------------------------------------------------
    # PART A: DYNAMIC BUILDINGS (Only if requested)
    # ---------------------------------------------------------
    cursor_x, cursor_y = 0, 0
    
    if building_list:
        for floors in building_list:
            # Spiral Search
            while (cursor_x, cursor_y) in occupied_grid:
                cursor_x += 2
                if cursor_x > 10: 
                    cursor_x = 0
                    cursor_y += 2
            
            mark_grid(cursor_x, cursor_y, radius=2)
            
            # Draw Building
            bx, by = cursor_x * GRID_UNIT, cursor_y * GRID_UNIT
            for f in range(floors):
                z = f * FLOOR_HEIGHT
                placeables.append(_building_actor(BUILDING_DB["floor"][4], bx, by, z))
                placeables.append(_building_actor(BUILDING_DB["wall"][1], bx+300, by, z, 90))
                placeables.append(_building_actor(BUILDING_DB["wall"][1], bx-300, by, z, 270))
                placeables.append(_building_actor(BUILDING_DB["wall"][1], bx, by+300, z, 0))
                placeables.append(_building_actor(BUILDING_DB["wall"][1], bx, by-300, z, 180))
            
            placeables.append(_building_actor(BUILDING_DB["ceiling"][0], bx, by, floors * FLOOR_HEIGHT))

    # ---------------------------------------------------------
    # PART B: DYNAMIC ROAD (The Socket Solver)
    # ---------------------------------------------------------
    rx, ry, rz = (cursor_x + 6) * GRID_UNIT, 0, 0
    r_yaw = 0.0
    
    # Start with a safe solid piece if list is empty
    if not road_intents: road_intents = ["straight", "straight", "turn_90"]
    
    # State Tracking
    current_connector_type = TYPE_SOLID # We assume we start on solid ground
    
    for intent in road_intents:
        # 1. Lookup Asset Logic
        # Does the requested intent exist in our DB?
        target_key = intent if intent in ROAD_DB else "straight"
        target_data = ROAD_DB[target_key]
        
        # 2. SOCKET CHECK (The Fix)
        # If types mismatch (e.g. Current is Solid, Target is Pin), we MUST inject an adapter.
        if current_connector_type != target_data["type"]:
            # Inject Adapter (Asset 11)
            adapter = ROAD_DB["adapter_pin"]
            placeables.append(_actor(adapter["id"], rx, ry, rz, r_yaw))
            
            # Move cursor past adapter
            rad = math.radians(r_yaw)
            rx += math.cos(rad) * adapter["len"]
            ry += math.sin(rad) * adapter["len"]
            
            # Update state (Adapter switches the type)
            current_connector_type = target_data["type"] 

        # 3. Place The Actual Requested Piece
        placeables.append(_actor(target_data["id"], rx, ry, rz, r_yaw))
        
        # Mark grid
        gx, gy = int(rx/GRID_UNIT), int(ry/GRID_UNIT)
        mark_grid(gx, gy, radius=2)
        
        # 4. Move Cursor
        rad = math.radians(r_yaw)
        length = target_data["len"]
        
        rx += math.cos(rad) * length
        ry += math.sin(rad) * length
        rz += target_data["z"]
        r_yaw += target_data["curve"]
        
        # Update type for next loop
        current_connector_type = target_data["type"]

    # ---------------------------------------------------------
    # PART C: DYNAMIC FOREST
    # ---------------------------------------------------------
    density = layout.get("forest_density", 0.1)
    
    if density > 0.0:
        for fx in range(-40, 40):
            for fy in range(-40, 40):
                if (fx, fy) not in occupied_grid:
                    if random.random() < density:
                        tx = (fx * GRID_UNIT) + random.uniform(-200, 200)
                        ty = (fy * GRID_UNIT) + random.uniform(-200, 200)
                        tree = random.choice(BUILDING_DB["decor"])
                        placeables.append(_building_actor(tree, tx, ty, 0, random.uniform(0, 360)))

    # ---------------------------------------------------------
    # PART D: ENVIRONMENT
    # ---------------------------------------------------------
    env = blueprint.get("environment", {})
    return {
        "PlaceableAssets": [p for p in placeables if p is not None],
        "GeometryAssets": [],
        "Text3DActors": [],
        "Foliage": [],
        "DefaultProperties": {
            "Brightness": env.get("brightness", 10.0),
            "Temperature": 46.6,
            "TimeOfDay": env.get("time", 14.0),
            "SunAngle": 0,
            "Density": 0.04,
            "Height": 0.2
        }
    }
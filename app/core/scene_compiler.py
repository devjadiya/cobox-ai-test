import random
import math

# ==============================================================================
# 1. THE HARDCODED REGISTRY (No more missing imports)
# ==============================================================================
# Derived strictly from your manual work and screenshots.
ASSETS = {
    # --- BUILDING BLOCKS (Grid 600x600) ---
    "floor": [
        {"class": f"BP_FloorAsset_Wb_{str(i).zfill(2)}_C", "path": f"/WorldBuilder/Core/Actors/Placeable/Library/Floor/BP_FloorAsset_Wb_{str(i).zfill(2)}.BP_FloorAsset_Wb_{str(i).zfill(2)}_C"} for i in range(1, 12)
    ],
    "wall": [
        {"class": f"BP_WallAsset_Wb_{str(i).zfill(2)}_C", "path": f"/WorldBuilder/Core/Actors/Placeable/Library/Wall/BP_WallAsset_Wb_{str(i).zfill(2)}.BP_WallAsset_Wb_{str(i).zfill(2)}_C"} for i in range(1, 13)
    ],
    "door": [{"class": "BP_DoorAsset_Wb_01_C", "path": "/WorldBuilder/Core/Actors/Placeable/Library/Door/BP_DoorAsset_Wb_01.BP_DoorAsset_Wb_01_C"}],
    "ceiling": [{"class": "BP_CeilingAsset_Wb_01_C", "path": "/WorldBuilder/Core/Actors/Placeable/Library/Ceiling/BP_CeilingAsset_Wb_01.BP_CeilingAsset_Wb_01_C"}],
    
    # --- ROAD PIECES (The 25 Assets) ---
    # We define their "Physics" here: Length and Z-Change
    "road_straight": {"id": "BP_RaceTrack_Wb_02", "len": 900, "curve": 0, "z": 0},
    "road_turn":     {"id": "BP_RaceTrack_Wb_04", "len": 900, "curve": 90, "z": 0},
    "road_curve":    {"id": "BP_RaceTrack_Wb_12", "len": 900, "curve": 15, "z": 0},
    "road_ramp":     {"id": "BP_RaceTrack_Wb_08", "len": 900, "curve": 0, "z": 200},
    "road_bridge":   {"id": "BP_RaceTrack_Wb_10", "len": 1200, "curve": 0, "z": 100},
    "road_loop":     {"id": "BP_RaceTrack_Wb_24", "len": 900, "curve": 180, "z": 0}, # Return loop
    "road_cap":      {"id": "BP_RaceTrack_Wb_01", "len": 300, "curve": 0, "z": 0},   # Dead end

    # --- DECOR (Trees/Bushes) ---
    "decor": [
        {"class": f"BP_DecorAsset_Wb_{str(i).zfill(2)}_C", "path": f"/WorldBuilder/Core/Actors/Placeable/Library/Decors/BP_DecorAsset_Wb_{str(i).zfill(2)}.BP_DecorAsset_Wb_{str(i).zfill(2)}_C"} for i in range(1, 34)
    ]
}

# ==============================================================================
# 2. CORE MATH CONSTANTS (Your Game Rules)
# ==============================================================================
GRID_UNIT = 600.0      # Building Center-to-Center spacing
WALL_OFFSET = 300.0    # Distance from floor center to wall
FLOOR_HEIGHT = 400.0   # Height of one floor

def _actor(asset_data, x, y, z, yaw=0.0):
    """Helper to generate the JSON block for a single actor."""
    if not asset_data: return None
    # Handle simple asset dicts vs complex road dicts
    c_name = asset_data.get("class", f"{asset_data.get('id')}_C")
    c_path = asset_data.get("path", f"/WorldBuilder/Core/Actors/Placeable/Library/Tracks/{asset_data.get('id', '')}.{asset_data.get('id', '')}_C")
    
    return {
        "AssetClass": c_name,
        "AssetClassPath": c_path,
        "Transform": {
            "Location": {"X": float(x), "Y": float(y), "Z": float(z)},
            "Rotation": {"Pitch": 0.0, "Yaw": float(yaw), "Roll": 0.0},
            "Scale": {"X": 1.0, "Y": 1.0, "Z": 1.0}
        },
        "OcaData": {"CollisionProfile": "BlockAllDynamic", "Physics": False, "Shadow": True}
    }

# ==============================================================================
# 3. THE COMPILER (The Logic)
# ==============================================================================
def compile_scene(blueprint: dict) -> dict:
    placeables = []
    
    # --- MEMORY MAP (To prevent overlap) ---
    occupied = set()
    def mark_spot(gx, gy, size=1):
        for i in range(size):
            for j in range(size):
                occupied.add((int(gx)+i, int(gy)+j))
    
    def is_taken(gx, gy, size=1):
        for i in range(size):
            for j in range(size):
                if (int(gx)+i, int(gy)+j) in occupied: return True
        return False

    # ---------------------------------------------------------
    # STEP A: BUILDINGS (Strict Grid 600x600)
    # ---------------------------------------------------------
    # Force 5 buildings as per your "High-Rise" prompt
    building_configs = [5, 4, 6, 3, 5] 
    
    cursor_x, cursor_y = 0, 0
    
    for floors in building_configs:
        # Spiral Search for empty spot
        while is_taken(cursor_x, cursor_y, size=3): # 3x3 buffer
            cursor_x += 2
            if cursor_x > 8: 
                cursor_x = 0
                cursor_y += 2
        
        mark_spot(cursor_x, cursor_y, size=3)
        
        # World Coordinates
        bx = cursor_x * GRID_UNIT
        by = cursor_y * GRID_UNIT
        
        # Build Floors Upwards
        for f in range(floors):
            z = f * FLOOR_HEIGHT
            
            # 1. Floor Center
            placeables.append(_actor(ASSETS["floor"][4], bx, by, z)) # Floor_05
            
            # 2. Walls (Strict 300 offset)
            # North (Y+) Yaw 90
            placeables.append(_actor(ASSETS["wall"][1], bx + WALL_OFFSET, by, z, 90))
            # South (Y-) Yaw 270
            placeables.append(_actor(ASSETS["wall"][1], bx - WALL_OFFSET, by, z, 270))
            # East (X+) Yaw 0
            placeables.append(_actor(ASSETS["wall"][1], bx, by + WALL_OFFSET, z, 0))
            # West (X-) Yaw 180
            placeables.append(_actor(ASSETS["wall"][1], bx, by - WALL_OFFSET, z, 180))

        # 3. Roof (Cap)
        placeables.append(_actor(ASSETS["ceiling"][0], bx, by, floors * FLOOR_HEIGHT))

    # ---------------------------------------------------------
    # STEP B: THE ROAD (The Walker)
    # ---------------------------------------------------------
    # Start road far away from buildings to ensure no collision
    rx, ry, rz = (cursor_x + 5) * GRID_UNIT, 0, 0
    r_yaw = 0.0
    
    # A predefined sequence that guaranteed works visually
    # Straight -> Curve -> Straight -> Ramp -> Bridge -> Turn -> Straight
    sequence = [
        "road_straight", "road_straight", "road_turn", 
        "road_straight", "road_ramp", "road_bridge", 
        "road_straight", "road_turn", "road_straight",
        "road_straight", "road_loop"
    ]
    
    for step_type in sequence:
        piece = ASSETS[step_type]
        
        # 1. Place the piece
        placeables.append(_actor(piece, rx, ry, rz, r_yaw))
        
        # 2. Mark grid to stop trees spawning on road
        gx, gy = int(rx/GRID_UNIT), int(ry/GRID_UNIT)
        mark_spot(gx, gy, size=2)
        
        # 3. Calculate NEXT start point
        # Move forward relative to current angle
        rad = math.radians(r_yaw)
        length = piece["len"]
        
        rx += math.cos(rad) * length
        ry += math.sin(rad) * length
        rz += piece["z"]
        r_yaw += piece["curve"]

    # ---------------------------------------------------------
    # STEP C: DENSE FOREST (The Filler)
    # ---------------------------------------------------------
    forest_size = 30 # Grid units
    
    for fx in range(-forest_size, forest_size):
        for fy in range(-forest_size, forest_size):
            # If spot is not a building or road
            if not is_taken(fx, fy):
                # 80% Density
                if random.random() > 0.2:
                    # Randomize position slightly so it's not a perfect grid
                    tx = (fx * GRID_UNIT) + random.uniform(-250, 250)
                    ty = (fy * GRID_UNIT) + random.uniform(-250, 250)
                    
                    # Pick random tree
                    tree = random.choice(ASSETS["decor"])
                    placeables.append(_actor(tree, tx, ty, 0, random.uniform(0, 360)))

    # ---------------------------------------------------------
    # STEP D: YOUR ENVIRONMENT SETTINGS
    # ---------------------------------------------------------
    return {
        "PlaceableAssets": placeables,
        "GeometryAssets": [],
        "Text3DActors": [],
        "Foliage": [],
        "DefaultProperties": {
            "Brightness": 10,
            "Temperature": 46.6,
            "TimeOfDay": 6.82, # Your specific setting
            "SunAngle": 0,
            "Density": 0.04,
            "Height": 0.2
        }
    }
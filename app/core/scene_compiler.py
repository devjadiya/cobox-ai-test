# app/core/scene_compiler.py
import random
import math

# ==============================================================================
# 1. ASSET DATABASE (The 25 Pieces with STRICT Connector Rules)
# ==============================================================================
# TYPE: 0 = Solid, 1 = Pin (Holes)
# CURVE: Degrees of rotation
# Z: Elevation change
ROAD_DB = {
    # --- SOLID BASICS (Type 0) ---
    "Straight_Basic":   {"id": "BP_RaceTrack_Wb_02", "type": 0, "len": 900, "curve": 0, "z": 0},
    "Straight_Bump":    {"id": "BP_RaceTrack_Wb_03", "type": 0, "len": 900, "curve": 0, "z": 0},
    "Straight_Wide":    {"id": "BP_RaceTrack_Wb_05", "type": 0, "len": 900, "curve": 0, "z": 0},
    "Straight_Gap":     {"id": "BP_RaceTrack_Wb_06", "type": 0, "len": 900, "curve": 0, "z": 0},
    "Straight_S_Bend":  {"id": "BP_RaceTrack_Wb_07", "type": 0, "len": 1200, "curve": 0, "z": 0},
    "Straight_Long":    {"id": "BP_RaceTrack_Wb_17", "type": 0, "len": 1200, "curve": 0, "z": 0},
    
    # --- SOLID TURNS (Type 0) ---
    "Turn_90":          {"id": "BP_RaceTrack_Wb_04", "type": 0, "len": 900, "curve": 90, "z": 0},
    "Turn_Slight":      {"id": "BP_RaceTrack_Wb_12", "type": 0, "len": 900, "curve": 15, "z": 0},
    "Turn_Sharp":       {"id": "BP_RaceTrack_Wb_13", "type": 0, "len": 900, "curve": 90, "z": 0},
    "Turn_U":           {"id": "BP_RaceTrack_Wb_18", "type": 0, "len": 900, "curve": 180, "z": 0},

    # --- SOLID RAMPS (Type 0) ---
    "Ramp_Gentle":      {"id": "BP_RaceTrack_Wb_08", "type": 0, "len": 900, "curve": 0, "z": 200},
    "Ramp_Steep":       {"id": "BP_RaceTrack_Wb_09", "type": 0, "len": 900, "curve": 0, "z": 400},
    "Spiral_Up":        {"id": "BP_RaceTrack_Wb_15", "type": 0, "len": 1200, "curve": 45, "z": 300},
    "Spiral_Steep":     {"id": "BP_RaceTrack_Wb_16", "type": 0, "len": 1200, "curve": 90, "z": 600},
    "Spiral_Down":      {"id": "BP_RaceTrack_Wb_19", "type": 0, "len": 1200, "curve": 90, "z": -400},
    "Loop_360":         {"id": "BP_RaceTrack_Wb_20", "type": 0, "len": 2000, "curve": 0, "z": 800},
    "Hill_Down":        {"id": "BP_RaceTrack_Wb_21", "type": 0, "len": 1200, "curve": 0, "z": -200},

    # --- SPECIALS (Type 0) ---
    "Bridge_Start":     {"id": "BP_RaceTrack_Wb_10", "type": 0, "len": 1200, "curve": 0, "z": 100},
    "Bridge_Segment":   {"id": "BP_RaceTrack_Wb_25", "type": 0, "len": 1200, "curve": 0, "z": 0},
    "Splitter":         {"id": "BP_RaceTrack_Wb_22", "type": 0, "len": 1200, "curve": 0, "z": 0},
    "Mercedes":         {"id": "BP_RaceTrack_Wb_23", "type": 0, "len": 1200, "curve": 0, "z": 0},
    "Return_Loop":      {"id": "BP_RaceTrack_Wb_24", "type": 0, "len": 900, "curve": 180, "z": 0},

    # --- PIN CONNECTORS (Type 1 - THE TROUBLEMAKERS) ---
    "Pin_Connector":    {"id": "BP_RaceTrack_Wb_11", "type": 1, "len": 600, "curve": 0, "z": 0},
    "Pin_T_Left":       {"id": "BP_RaceTrack_Wb_14", "type": 1, "len": 900, "curve": 90, "z": 0}, # Force Left Turn
}

# --- BUILDING ASSETS (Your specific preferences) ---
BUILDING_DB = {
    "floor": [{"class": f"BP_FloorAsset_Wb_{str(i).zfill(2)}_C", "path": f"/WorldBuilder/Core/Actors/Placeable/Library/Floor/BP_FloorAsset_Wb_{str(i).zfill(2)}.BP_FloorAsset_Wb_{str(i).zfill(2)}_C"} for i in range(1, 12)],
    "wall": [{"class": f"BP_WallAsset_Wb_{str(i).zfill(2)}_C", "path": f"/WorldBuilder/Core/Actors/Placeable/Library/Wall/BP_WallAsset_Wb_{str(i).zfill(2)}.BP_WallAsset_Wb_{str(i).zfill(2)}_C"} for i in range(1, 13)],
    "ceiling": [{"class": "BP_CeilingAsset_Wb_01_C", "path": "/WorldBuilder/Core/Actors/Placeable/Library/Ceiling/BP_CeilingAsset_Wb_01.BP_CeilingAsset_Wb_01_C"}],
    "decor": [{"class": f"BP_DecorAsset_Wb_{str(i).zfill(2)}_C", "path": f"/WorldBuilder/Core/Actors/Placeable/Library/Decors/BP_DecorAsset_Wb_{str(i).zfill(2)}.BP_DecorAsset_Wb_{str(i).zfill(2)}_C"} for i in range(1, 34)]
}

# ==============================================================================
# 2. THE COMPILER
# ==============================================================================
GRID_UNIT = 600.0
WALL_OFFSET = 300.0
FLOOR_HEIGHT = 400.0

def _actor(asset, x, y, z, yaw=0.0):
    if not asset: return None
    # Handle Road Logic Dicts vs Registry Dicts
    if "class" in asset:
        c_name = asset["class"]
        c_path = asset["path"]
    else:
        # Construct path for road pieces
        c_name = f"{asset['id']}_C"
        c_path = f"/WorldBuilder/Core/Actors/Placeable/Library/Tracks/{asset['id']}.{asset['id']}_C"

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

def compile_scene(blueprint: dict) -> dict:
    placeables = []
    occupied_grid = set()

    def mark_grid(gx, gy, radius=1):
        for i in range(-radius, radius+1):
            for j in range(-radius, radius+1):
                occupied_grid.add((int(gx)+i, int(gy)+j))

    # ---------------------------------------------------------
    # PART A: BUILDINGS (The Anchor)
    # ---------------------------------------------------------
    # Hardcode a safe grid layout for 5 buildings so they NEVER overlap
    # (0,0), (0, 3), (3, 0), (-3, 0), (0, -3)
    building_coords = [(0,0), (0,4), (4,0), (-4,0), (0,-4)]
    
    for i, (bx_grid, by_grid) in enumerate(building_coords):
        mark_grid(bx_grid, by_grid, radius=2) # Reserve space
        
        world_x = bx_grid * GRID_UNIT
        world_y = by_grid * GRID_UNIT
        floors = random.randint(2, 6) # Varied height

        # Recursive Construction
        for f in range(floors):
            z = f * FLOOR_HEIGHT
            # Floor (Asset 05 preferred)
            placeables.append(_actor(BUILDING_DB["floor"][4], world_x, world_y, z))
            
            # Walls
            wall_asset = BUILDING_DB["wall"][1] # Asset 02 preferred
            placeables.append(_actor(wall_asset, world_x + WALL_OFFSET, world_y, z, 90))
            placeables.append(_actor(wall_asset, world_x - WALL_OFFSET, world_y, z, 270))
            placeables.append(_actor(wall_asset, world_x, world_y + WALL_OFFSET, z, 0))
            placeables.append(_actor(wall_asset, world_x, world_y - WALL_OFFSET, z, 180))

        # Roof
        placeables.append(_actor(BUILDING_DB["ceiling"][0], world_x, world_y, floors * FLOOR_HEIGHT))

    # ---------------------------------------------------------
    # PART B: THE ROAD (The Graph Solver)
    # ---------------------------------------------------------
    # Start the road far out so it doesn't clip buildings
    rx, ry, rz = 6000.0, 0.0, 0.0
    r_yaw = 0.0
    
    # We define a "Safe Sequence" that mixes Solids and Pins correctly
    # Pattern: Solid -> Solid -> Solid -> Pin_Adapter -> Pin_Turn -> Pin_Adapter -> Solid
    
    road_plan = [
        "Straight_Basic", "Straight_Basic", "Straight_Basic", # Speed up
        "Bridge_Start", "Bridge_Segment", "Bridge_Segment", # Go up
        "Ramp_Gentle", # Go higher
        "Turn_90", "Straight_Basic", "Turn_90", # Turn around
        "Hill_Down", "Straight_Basic", # Go down
        "Pin_Connector", "Pin_T_Left", "Pin_Connector", # THE PIN SECTION (11 -> 14 -> 11)
        "Straight_Basic", "Return_Loop" # End
    ]

    for move_name in road_plan:
        piece = ROAD_DB[move_name]
        
        # 1. Place Piece
        placeables.append(_actor(piece, rx, ry, rz, r_yaw))
        
        # 2. Reserve Grid (So trees don't spawn on road)
        gx, gy = int(rx/GRID_UNIT), int(ry/GRID_UNIT)
        mark_grid(gx, gy, radius=2)

        # 3. Calculate Exit Point
        rad = math.radians(r_yaw)
        length = piece["len"]
        
        rx += math.cos(rad) * length
        ry += math.sin(rad) * length
        rz += piece["z"]
        r_yaw += piece["curve"]

    # ---------------------------------------------------------
    # PART C: DENSE FOREST (The Filler)
    # ---------------------------------------------------------
    # We fill a massive area (100x100 grid)
    for fx in range(-50, 50):
        for fy in range(-50, 50):
            # Optimization: Only check if it's NOT in the center building/road zone
            if (fx, fy) not in occupied_grid:
                # 60% Density
                if random.random() > 0.4:
                    tx = (fx * GRID_UNIT) + random.uniform(-200, 200)
                    ty = (fy * GRID_UNIT) + random.uniform(-200, 200)
                    
                    # Random tree
                    tree = random.choice(BUILDING_DB["decor"])
                    placeables.append(_actor(tree, tx, ty, 0, random.uniform(0, 360)))

    return {
        "PlaceableAssets": [p for p in placeables if p is not None],
        "GeometryAssets": [],
        "Text3DActors": [],
        "Foliage": [],
        "DefaultProperties": {
            "Brightness": 10.0,
            "Temperature": 46.6,
            "TimeOfDay": 6.82,
            "SunAngle": 0,
            "Density": 0.04,
            "Height": 0.2
        }
    }
# app/core/scene_compiler.py
import random
from typing import Dict, List
from app.core.asset_registry import get_asset_by_category

# Calibration based on SavedGen.json
GRID_SNAP = 600.0  

def _generate_actor(asset_meta: Dict, x, y, z, yaw=0.0):
    return {
        "AssetClass": asset_meta["class"],
        "AssetClassPath": asset_meta["path"],
        "Transform": {
            "Location": {"X": float(x), "Y": float(y), "Z": float(z)},
            "Rotation": {"Pitch": 0.0, "Yaw": float(yaw), "Roll": 0.0},
            "Scale": {"X": 1.0, "Y": 1.0, "Z": 1.0}
        },
        "OcaData": {"CollisionProfile": "BlockAllDynamic", "Physics": False, "Shadow": True}
    }

def compile_scene(intent: Dict) -> Dict:
    placeables = []
    
    # Extract counts
    counts = {obj["type"]: obj["count"] for obj in intent["objects"]}
    theme = intent["theme"]

    # 1. ZONE: BUILDINGS & ROADS (The Core City)
    building_count = counts.get("building", 0)
    for i in range(building_count):
        bx = i * 1500.0 # Wide spacing for "Surroundings"
        by = 0.0
        
        # Floor
        floor = get_asset_by_category("floor", i)
        placeables.append(_generate_actor(floor, bx, by, 0))
        
        # Snapped Walls (4-sided box)
        wall_configs = [(300,0,90), (-300,0,270), (0,300,0), (0,-300,180)]
        for ox, oy, yaw in wall_configs:
            wall = get_asset_by_category("wall", random.randint(0, 10))
            placeables.append(_generate_actor(wall, bx + ox, by + oy, 0, yaw))

    # 2. ENTITY: VEHICLES (Mapping "Car" to appropriate Decor if car mesh missing)
    # Based on SavedGen.json, we'll use specific 'Decor' indices that look like props/vehicles
    vehicle_count = counts.get("vehicle", 0)
    for v in range(vehicle_count):
        # Place car on a "road" area
        placeables.append(_generate_actor(get_asset_by_category("decor", 10), 0, v * -400, 20))

    # 3. ZONE: GREEN SURROUNDINGS (Foliage Scatter)
    tree_count = counts.get("tree", 20)
    for t in range(tree_count):
        # Logic: Don't place trees inside buildings. 
        # Scatter them in a ring around the building zone.
        angle = random.uniform(0, 6.28)
        radius = random.uniform(2000, 6000)
        tx = radius * 1.5 * (1 if random.random() > 0.5 else -1)
        ty = radius * 1.5 * (1 if random.random() > 0.5 else -1)
        
        tree_idx = random.randint(0, 32)
        # Force nature-looking assets if theme is nature
        if theme == "nature":
             tree_idx = random.choice([1, 2, 5, 8, 12, 15]) # Assumes these are trees in your 33 assets
             
        tree = get_asset_by_category("decor", tree_idx)
        placeables.append(_generate_actor(tree, tx, ty, 0, random.uniform(0, 360)))

    return {
        "PlaceableAssets": placeables,
        "DefaultProperties": {
            "Brightness": 12.0 if theme == "nature" else 8.0,
            "Temperature": 55.0,
            "TimeOfDay": 10.0 if theme == "nature" else 19.0, # Day vs Night
            "SunAngle": 0.0, "Density": 0.04, "Height": 0.2
        }
    }
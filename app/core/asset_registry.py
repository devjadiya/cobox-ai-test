# app/core/asset_registry.py
import hashlib

ASSETS = {
    "floor": [{"class": f"BP_FloorAsset_Wb_{str(i).zfill(2)}_C", "path": f"/WorldBuilder/Core/Actors/Placeable/Library/Floor/BP_FloorAsset_Wb_{str(i).zfill(2)}.BP_FloorAsset_Wb_{str(i).zfill(2)}_C"} for i in range(1, 12)],
    "wall": [{"class": f"BP_WallAsset_Wb_{str(i).zfill(2)}_C", "path": f"/WorldBuilder/Core/Actors/Placeable/Library/Wall/BP_WallAsset_Wb_{str(i).zfill(2)}.BP_WallAsset_Wb_{str(i).zfill(2)}_C"} for i in range(1, 13)],
    "decor": [{"class": f"BP_DecorAsset_Wb_{str(i).zfill(2)}_C", "path": f"/WorldBuilder/Core/Actors/Placeable/Library/Decors/BP_DecorAsset_Wb_{str(i).zfill(2)}.BP_DecorAsset_Wb_{str(i).zfill(2)}_C"} for i in range(1, 34)],
    "track": [{"class": f"BP_RaceTrack_Wb_{str(i).zfill(2)}_C", "path": f"/WorldBuilder/Core/Actors/Placeable/Library/Tracks/BP_RaceTrack_Wb_{str(i).zfill(2)}.BP_RaceTrack_Wb_{str(i).zfill(2)}_C"} for i in range(1, 26)]
}

def get_production_assets():
    processed = {cat: [] for cat in ASSETS.keys()}
    for category, items in ASSETS.items():
        for item in items:
            asset_id = hashlib.sha1(item["path"].encode()).hexdigest()[:12]
            processed[category].append({
                "id": asset_id, "category": category, "blueprint": item["path"],
                "class": item["class"], "path": item["path"], "snap": True
            })
    return processed

def get_asset_by_category(category: str, index: int = 0):
    # SMARTER PICKING: Map "tree" or "car" type requests to Decor list
    if category in ["tree", "vehicle", "greenery"]:
        cat_list = ASSETS["decor"]
    else:
        cat_list = ASSETS.get(category, ASSETS["decor"])
    return cat_list[index % len(cat_list)]
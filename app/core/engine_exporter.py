# app/core/engine_exporter.py

from typing import Dict, List


def export_to_engine(scene: Dict) -> Dict:
    placeables = []
    foliage_map = {}

    for actor in scene["actors"]:
        blueprint = actor["blueprint"]

        asset_class = blueprint.split(".")[-1].replace("_C'", "_C")
        asset_path = blueprint.split("'")[1]

        loc = actor["transform"]["location"]
        rot = actor["transform"]["rotation"]
        scl = actor["transform"]["scale"]

        if actor["category"] in ["tree", "decor"]:
            # FOLIAGE GROUPING
            key = asset_class
            foliage_map.setdefault(key, {
                "StaticMesh": asset_class,
                "StaticMeshPath": asset_path,
                "Instances": []
            })

            foliage_map[key]["Instances"].append({
                "Location": {"X": loc["x"], "Y": loc["y"], "Z": loc["z"]},
                "Rotation": {"Pitch": rot["pitch"], "Yaw": rot["yaw"], "Roll": rot["roll"]},
                "Scale": {"X": scl["x"], "Y": scl["y"], "Z": scl["z"]}
            })

        else:
            placeables.append({
                "AssetClass": asset_class,
                "AssetClassPath": asset_path,
                "Transform": {
                    "Location": {"X": loc["x"], "Y": loc["y"], "Z": loc["z"]},
                    "Rotation": {"Pitch": rot["pitch"], "Yaw": rot["yaw"], "Roll": rot["roll"]},
                    "Scale": {"X": scl["x"], "Y": scl["y"], "Z": scl["z"]}
                },
                "OcaData": {
                    "CollisionProfile": "BlockAllDynamic",
                    "Physics": False,
                    "Shadow": True
                }
            })

    lighting = scene["lighting"]
    fog = scene["fog"]

    return {
        "PlaceableAssets": placeables,
        "GeometryAssets": [],
        "Text3DActors": [],
        "Foliage": list(foliage_map.values()),
        "DefaultProperties": {
            "Brightness": lighting["brightness"] * 9.3,
            "Temperature": lighting["temperature"] / 1.6,
            "TimeOfDay": lighting["time_of_day"],
            "SunAngle": lighting["sun_angle"],
            "Density": fog["density"],
            "Height": fog["height"]
        }
    }

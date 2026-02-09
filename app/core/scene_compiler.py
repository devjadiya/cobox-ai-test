import uuid
import random
import math
from typing import Dict, List


def _uid(prefix: str) -> str:
    return f"{prefix}-{uuid.uuid4().hex[:8]}"


# -------------------------------------------------
# ACTOR FACTORY
# -------------------------------------------------
def _actor(asset: Dict, category: str, x: int, y: int, z: int,
           yaw: int = 0, scale: float = 1.0) -> Dict:
    return {
        "actor_id": _uid("actor"),
        "asset_id": asset["id"],
        "name": category,
        "category": category,
        "blueprint": asset["blueprint"],
        "transform": {
            "location": {"x": x, "y": y, "z": z},
            "rotation": {"pitch": 0, "yaw": yaw, "roll": 0},
            "scale": {"x": scale, "y": scale, "z": scale},
        },
        "physics": {
            "enabled": False,
            "collidable": True,
            "gravity": False,
        },
        "visibility": {
            "visible": True,
            "hidden_in_game": False,
        },
    }


# -------------------------------------------------
# MAIN COMPILER
# -------------------------------------------------
def compile_scene(intent: Dict, assets: List[Dict]) -> Dict:

    scene_id = _uid("scene")

    scene = {
        "scene_id": scene_id,
        "scene_type": intent.get("scene_type", "generic"),
        "lighting": {
            "brightness": random.randint(8, 14),
            "temperature": random.uniform(35, 60),
            "time_of_day": random.uniform(5, 18),
            "sun_angle": random.randint(0, 360),
        },
        "fog": {
            "density": 0.02,
            "ray_density": 0.02,
            "height": 0.2,
        },
        "actors": [],
        "rules": {
            "allow_physics": False,
            "allow_ai_agents": False,
            "allow_multiplayer": False,
        },
    }

    # -----------------------------
    # ASSET LOOKUP
    # -----------------------------
    asset_lookup = {}
    for asset in assets:
        asset_lookup.setdefault(asset["category"], []).append(asset)

    def pick(cat):
        pool = asset_lookup.get(cat, [])
        return random.choice(pool) if pool else None

    # -----------------------------
    # BUILDINGS
    # -----------------------------
    building_count = 0
    for obj in intent.get("objects", []):
        if obj["type"] == "building":
            building_count += obj.get("count", 1)

    if building_count > 0:
        rows = math.ceil(math.sqrt(building_count))
        spacing = 8000
        idx = 0

        for r in range(rows):
            for c in range(rows):
                if idx >= building_count:
                    break

                base_x = r * spacing
                base_y = c * spacing
                floors_count = random.randint(1, 3)
                yaw = random.choice([0, 90, 180, 270])

                for f in range(floors_count):
                    z = f * 400

                    floor_asset = pick("floor")
                    if floor_asset:
                        scene["actors"].append(
                            _actor(floor_asset, "floor", base_x, base_y, z, yaw)
                        )

                    # walls
                    for dx, dy in [(600, 0), (-600, 0), (0, 600), (0, -600)]:
                        wall_asset = pick("wall")
                        if wall_asset:
                            scene["actors"].append(
                                _actor(
                                    wall_asset,
                                    "wall",
                                    base_x + dx,
                                    base_y + dy,
                                    z,
                                    yaw,
                                )
                            )

                ceiling_asset = pick("ceiling")
                if ceiling_asset:
                    scene["actors"].append(
                        _actor(
                            ceiling_asset,
                            "ceiling",
                            base_x,
                            base_y,
                            floors_count * 400,
                            yaw,
                        )
                    )

                door_asset = pick("door")
                if door_asset:
                    side = random.choice([(650, 0), (-650, 0), (0, 650), (0, -650)])
                    scene["actors"].append(
                        _actor(
                            door_asset,
                            "door",
                            base_x + side[0],
                            base_y + side[1],
                            0,
                            yaw,
                        )
                    )

                idx += 1

    # -----------------------------
    # ROADS / TRACKS
    # -----------------------------
    for obj in intent.get("objects", []):
        if obj["type"] in ["road", "track"]:
            track_asset = pick("track")
            if track_asset:
                for i in range(3):
                    scene["actors"].append(
                        _actor(track_asset, "track", i * 6000, -8000, 0)
                    )

    # -----------------------------
    # TREES / FOLIAGE
    # -----------------------------
    tree_assets = asset_lookup.get("tree") or asset_lookup.get("decor", [])
    if tree_assets:
        for _ in range(80):
            asset = random.choice(tree_assets)
            scene["actors"].append(
                _actor(
                    asset,
                    "tree",
                    random.randint(-20000, 20000),
                    random.randint(-20000, 20000),
                    0,
                    random.randint(0, 360),
                    random.uniform(0.8, 1.3),
                )
            )

    # -----------------------------
    # DECOR
    # -----------------------------
    decor_assets = asset_lookup.get("decor", [])
    for _ in range(40):
        if decor_assets:
            asset = random.choice(decor_assets)
            scene["actors"].append(
                _actor(
                    asset,
                    "decor",
                    random.randint(-15000, 15000),
                    random.randint(-15000, 15000),
                    0,
                    random.randint(0, 360),
                )
            )

    # -----------------------------
    # EXPORT
    # -----------------------------
    from app.core.engine_exporter import export_to_engine

    return export_to_engine(scene)

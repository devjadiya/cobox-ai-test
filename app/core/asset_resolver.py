# app/core/asset_resolver.py

from typing import Dict, List
import itertools


def resolve_assets(intent: Dict, asset_index: Dict[str, List[dict]]) -> List[Dict]:
    resolved: List[Dict] = []

    def cycle(category: str):
        assets = asset_index.get(category, [])
        return itertools.cycle(assets) if assets else None

    floor_it = cycle("floor")
    wall_it = cycle("wall")
    ceiling_it = cycle("ceiling")
    door_it = cycle("door")
    track_it = cycle("track")
    tree_it = cycle("tree")

    for obj in intent.get("objects", []):
        t = obj["type"]
        count = obj.get("count", 1)

        # 🏢 BUILDINGS (COMPOSITE)
        if t == "building":
            for _ in range(count):
                if floor_it:
                    resolved.append(next(floor_it))
                if wall_it:
                    for _ in range(4):
                        resolved.append(next(wall_it))
                if ceiling_it:
                    resolved.append(next(ceiling_it))
                if door_it:
                    resolved.append(next(door_it))

        # 🛣 ROADS
        elif t == "road" and track_it:
            for _ in range(count):
                resolved.append(next(track_it))

        # 🌳 TREES
        elif t == "tree" and tree_it:
            for _ in range(count):
                resolved.append(next(tree_it))

        # 🚪 DOORS (STANDALONE)
        elif t == "door" and door_it:
            for _ in range(count):
                resolved.append(next(door_it))

    return resolved

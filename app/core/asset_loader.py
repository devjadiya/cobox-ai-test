# app/core/asset_loader.py

import csv
import hashlib
from pathlib import Path
from typing import Dict, List

ASSET_CSV_PATH = Path("app/assets/library.csv")


def _make_id(value: str) -> str:
    return hashlib.sha1(value.encode("utf-8")).hexdigest()[:12]


def load_asset_index() -> Dict[str, List[dict]]:
    """
    Loads Unreal assets and builds a semantic index.

    Logical categories:
    - floor, wall, ceiling, door
    - track  -> road
    - decor  -> tree / decor
    """

    index: Dict[str, List[dict]] = {
        "floor": [],
        "wall": [],
        "ceiling": [],
        "door": [],
        "track": [],
        "decor": [],
    }

    with open(ASSET_CSV_PATH, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        for row in reader:
            blueprint = row.get("AssetToPlace", "").strip()
            if not blueprint:
                continue

            path = blueprint.lower()

            if "/floor/" in path:
                category = "floor"
            elif "/wall/" in path:
                category = "wall"
            elif "/ceiling/" in path:
                category = "ceiling"
            elif "/door/" in path:
                category = "door"
            elif "/tracks/" in path:
                category = "track"
            else:
                category = "decor"

            asset = {
                "id": _make_id(blueprint),
                "category": category,
                "blueprint": blueprint,
                "snap": row.get("bWillSnapToGrid") == "True",
                "foliage": row.get("bIsFoliageMesh") == "True",
                "meta": {
                    "raw": row
                }
            }

            index[category].append(asset)

    return index


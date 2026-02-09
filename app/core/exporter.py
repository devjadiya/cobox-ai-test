import json
from pathlib import Path
from datetime import datetime

EXPORT_DIR = Path("exports")
EXPORT_DIR.mkdir(exist_ok=True)

def export_scene(scene: dict) -> str:
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_path = EXPORT_DIR / f"scene_{ts}.json"

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(scene, f, indent=2)

    return str(file_path)

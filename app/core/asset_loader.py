# app/core/asset_loader.py

from typing import Dict, List
from app.core.asset_registry import get_production_assets

def load_asset_index() -> Dict[str, List[dict]]:
    """Production Proxy: Loads from memory registry instead of CSV."""
    return get_production_assets()
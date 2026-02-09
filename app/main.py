# app/main.py
from fastapi import FastAPI
import logging
from app.api.routes import router
from app.core.asset_registry import get_production_assets

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("cobox-ai")

app = FastAPI(title="Cobox AI Production Service", version="0.6.0")

# Global production registry
app.state.asset_index = get_production_assets()

app.include_router(router)

@app.get("/health")
def health():
    return {"status": "ok", "production_mode": True, "assets_loaded": True}
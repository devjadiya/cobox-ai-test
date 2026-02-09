# app/main.py

from fastapi import FastAPI
import logging
from app.core.asset_loader import load_asset_index
from app.api.routes import router

# --------------------------------------------------
# Logging
# --------------------------------------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("cobox-ai")

# --------------------------------------------------
# App
# --------------------------------------------------
app = FastAPI(
    title="Cobox AI Command Service",
    version="0.3.0",
    description="AI → Scene → Unreal pipeline"
)

# --------------------------------------------------
# Startup
# --------------------------------------------------
@app.on_event("startup")
def startup():
    app.state.asset_index = load_asset_index()
    logger.info("[startup] Assets loaded")

# --------------------------------------------------
# Routers
# --------------------------------------------------
app.include_router(router)

# --------------------------------------------------
# Health
# --------------------------------------------------
@app.get("/health")
def health():
    return {"status": "ok"}

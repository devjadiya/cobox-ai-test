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
# Lazy Loading Logic
# --------------------------------------------------
# We initialize this to None so the server starts instantly.
app.state.asset_index = None

def get_assets():
    """Helper to load assets only when needed."""
    if app.state.asset_index is None:
        logger.info("[lazy-load] Loading assets from CSV...")
        app.state.asset_index = load_asset_index()
        logger.info("[lazy-load] Assets loaded successfully")
    return app.state.asset_index

# --------------------------------------------------
# Health Check (Triggers Load)
# --------------------------------------------------
@app.get("/health")
def health():
    # Calling get_assets() here ensures the index is ready for other routes
    get_assets() 
    return {"status": "ok"}

# --------------------------------------------------
# Routers
# --------------------------------------------------
# Note: Ensure your routes.py also calls get_assets() if it 
# accesses request.app.state.asset_index directly.
app.include_router(router)
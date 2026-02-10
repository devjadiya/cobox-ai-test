# app/main.py
from fastapi import FastAPI
from app.api.routes import router
from app.core.asset_registry import get_production_assets

app = FastAPI(title="Cobox AI Game Gen", version="1.0.0")

# Load Assets
app.state.asset_index = get_production_assets()

app.include_router(router)

@app.get("/health")
def health():
    return {"status": "ready", "assets": len(app.state.asset_index["floor"])}
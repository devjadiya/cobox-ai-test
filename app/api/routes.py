# app/api/routes.py

from fastapi import APIRouter, Request
from pydantic import BaseModel
from fastapi.responses import JSONResponse

# Existing Job Management Logic
from app.core.job_manager import create_job, update_job, log, JOBS, cancel
from app.middleware.sanitization import sanitize_text
from app.core.intent_parser import parse_intent
from app.core.scene_compiler import compile_scene

router = APIRouter(prefix="/ai")

class CommandRequest(BaseModel):
    text: str

# --------------------------------------------------
# ASYNC JOB MODE (For Complex Scenes)
# --------------------------------------------------
@router.post("/command")
async def ai_command(req: CommandRequest, request: Request):
    job_id = create_job()
    try:
        update_job(job_id, status="running")
        
        # 1. Clean and Log Input
        text = sanitize_text(req.text)
        log(job_id, f"Input Sanitized: {text}")

        # 2. Extract Intent (LLM/Regex)
        intent = parse_intent(text)
        log(job_id, "Intent Extracted")

        # 3. Generate Engine JSON (Registry-based)
        # Note: We no longer need resolve_assets as a separate step
        scene = compile_scene(intent)
        log(job_id, f"Scene Compiled: {len(scene['PlaceableAssets'])} actors generated")

        # 4. Save result for polling
        update_job(job_id, status="done", result=scene)

    except Exception as e:
        update_job(job_id, status="error")
        log(job_id, f"Fatal Error: {str(e)}")

    return {"job_id": job_id}

# --------------------------------------------------
# INSTANT MODE (Production Standard)
# --------------------------------------------------
@router.post("/instant")
async def instant(req: CommandRequest, request: Request):
    """Bypasses queuing for immediate game-ready JSON response."""
    try:
        text = sanitize_text(req.text)
        intent = parse_intent(text)
        scene = compile_scene(intent)
        return JSONResponse(content=scene)
    except Exception as e:
        return JSONResponse(
            status_code=500, 
            content={"error": "Instant generation failed", "details": str(e)}
        )

# --------------------------------------------------
# UTILITY ENDPOINTS (Existing functionality preserved)
# --------------------------------------------------
@router.get("/status/{job_id}")
def status(job_id: str):
    return JOBS.get(job_id, {"error": "not found"})

@router.get("/logs/{job_id}")
def logs(job_id: str):
    return JOBS.get(job_id, {}).get("logs", ["Job not found"])

@router.get("/result/{job_id}")
def result(job_id: str):
    job = JOBS.get(job_id)
    if not job:
        return {"error": "not found"}
    if job["status"] != "done":
        return {"status": job["status"]}
    return JSONResponse(content=job["result"])

@router.post("/cancel/{job_id}")
def cancel_job(job_id: str):
    cancel(job_id)
    return {"status": "cancelled"}
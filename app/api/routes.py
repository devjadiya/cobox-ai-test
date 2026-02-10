# app/api/routes.py
from fastapi import APIRouter, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from app.llm.openai_client import generate_spatial_layout
from app.core.scene_compiler import compile_scene
from app.core.job_manager import create_job, update_job, JOBS, cancel
from app.middleware.sanitization import sanitize_text

router = APIRouter(prefix="/ai")

class CommandRequest(BaseModel):
    text: str

async def generate_task(job_id: str, text: str):
    try:
        update_job(job_id, status="running")
        # 1. Get High-Level Plan (JSON)
        blueprint = generate_spatial_layout(sanitize_text(text))
        # 2. Execute Grid Math (Python)
        scene = compile_scene(blueprint)
        update_job(job_id, status="done", result=scene)
    except Exception as e:
        update_job(job_id, status="error")

@router.post("/instant")
async def instant(req: CommandRequest):
    # Synchronous flow for local testing
    blueprint = generate_spatial_layout(sanitize_text(req.text))
    scene = compile_scene(blueprint)
    return JSONResponse(content=scene)

@router.post("/command")
async def command(req: CommandRequest, bt: BackgroundTasks):
    job_id = create_job()
    bt.add_task(generate_task, job_id, req.text)
    return {"job_id": job_id}

# Keep existing status/result endpoints...
@router.get("/result/{job_id}")
def result(job_id: str):
    job = JOBS.get(job_id)
    return JSONResponse(content=job["result"]) if job and job["status"] == "done" else {"status": "processing"}
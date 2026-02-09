import uuid
from typing import Dict, Any

JOBS: Dict[str, Dict[str, Any]] = {}

def create_job() -> str:
    job_id = uuid.uuid4().hex
    JOBS[job_id] = {
        "status": "queued",
        "logs": [],
        "result": None,
        "cancelled": False
    }
    return job_id

def update_job(job_id, **kwargs):
    JOBS[job_id].update(kwargs)

def log(job_id, message):
    JOBS[job_id]["logs"].append(message)

def cancel(job_id):
    JOBS[job_id]["cancelled"] = True
    JOBS[job_id]["status"] = "cancelled"

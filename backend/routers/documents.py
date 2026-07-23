from __future__ import annotations

from fastapi import APIRouter

router = APIRouter()

# Full implementation in ticket #9 (FastAPI API design)


@router.post("/{job_id}/documents")
async def generate_documents(job_id: str, doc_type: str = "both"):
    return {"job_uuid": job_id, "status": "queued"}


@router.get("/{job_id}/documents")
async def list_documents(job_id: str):
    return {"job_uuid": job_id, "documents": []}

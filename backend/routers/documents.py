from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from backend.dependencies import get_config, get_job_service
from backend.schemas import DocumentGenerateRequest, DocumentItem, DocumentListResponse
from backend.services.jobs import JobDataService
from core.config import AppConfig
from core.storage import get_db_connection

router = APIRouter()

_VALID_DOC_TYPES = {"cv", "cover_letter", "both"}


@router.post("/{job_id}/documents")
async def generate_documents(
    job_id: str,
    body: DocumentGenerateRequest = DocumentGenerateRequest(),
    service: JobDataService = Depends(get_job_service),
):
    """Enqueue document generation for a job.

    Full implementation arrives in ticket #10 (DOCX generation).
    """
    if service.get_by_id(job_id) is None:
        raise HTTPException(status_code=404, detail="Job not found")
    if body.doc_type not in _VALID_DOC_TYPES:
        raise HTTPException(
            status_code=422,
            detail=f"doc_type must be one of {sorted(_VALID_DOC_TYPES)}",
        )
    return {"job_uuid": job_id, "doc_type": body.doc_type, "status": "queued"}


@router.get("/{job_id}/documents", response_model=DocumentListResponse)
async def list_documents(
    job_id: str,
    service: JobDataService = Depends(get_job_service),
    cfg: AppConfig = Depends(get_config),
):
    if service.get_by_id(job_id) is None:
        raise HTTPException(status_code=404, detail="Job not found")

    with get_db_connection(cfg.storage) as conn:
        rows = conn.execute(
            "SELECT id, doc_type, file_path, country_style, created_at "
            "FROM documents WHERE job_uuid = ? ORDER BY created_at DESC",
            (job_id,),
        ).fetchall()

    docs = [
        DocumentItem(
            id=row["id"],
            doc_type=row["doc_type"],
            file_path=row["file_path"],
            country_style=row["country_style"],
            created_at=row["created_at"],
        )
        for row in rows
    ]
    return DocumentListResponse(job_uuid=job_id, documents=docs)

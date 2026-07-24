from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from fastapi.responses import FileResponse

from backend.dependencies import get_config, get_doc_service, get_job_service
from backend.schemas import DocumentGenerateRequest, DocumentItem, DocumentListResponse
from backend.services.documents import DocumentService
from backend.services.jobs import JobDataService
from core.config import AppConfig
from core.storage import get_db_connection

router = APIRouter()

_VALID_DOC_TYPES = {"cv", "cover_letter", "both"}


@router.post("/{job_id}/documents")
async def generate_documents(
    job_id: str,
    background_tasks: BackgroundTasks,
    body: DocumentGenerateRequest = DocumentGenerateRequest(),
    service: JobDataService = Depends(get_job_service),
    doc_service: DocumentService = Depends(get_doc_service),
):
    """Enqueue DOCX generation for a job.

    Returns immediately; generation runs in the background.
    Poll GET /jobs/{id}/documents to check when files are ready.
    """
    job_row = service.get_by_id(job_id)
    if job_row is None:
        raise HTTPException(status_code=404, detail="Job not found")
    if body.doc_type not in _VALID_DOC_TYPES:
        raise HTTPException(
            status_code=422,
            detail=f"doc_type must be one of {sorted(_VALID_DOC_TYPES)}",
        )

    background_tasks.add_task(
        doc_service.generate_and_save, job_id, body.doc_type, job_row
    )
    return {
        "job_uuid": job_id,
        "doc_type": body.doc_type,
        "status": "generating",
        "hint": f"Poll GET /jobs/{job_id}/documents to check when files are ready.",
    }


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


@router.get("/{job_id}/documents/{doc_id}/download")
async def download_document(
    job_id: str,
    doc_id: int,
    service: JobDataService = Depends(get_job_service),
    cfg: AppConfig = Depends(get_config),
):
    """Download a generated DOCX file."""
    if service.get_by_id(job_id) is None:
        raise HTTPException(status_code=404, detail="Job not found")

    with get_db_connection(cfg.storage) as conn:
        row = conn.execute(
            "SELECT doc_type, file_path FROM documents WHERE id = ? AND job_uuid = ?",
            (doc_id, job_id),
        ).fetchone()

    if row is None:
        raise HTTPException(status_code=404, detail="Document not found")

    file_path = Path(row["file_path"])
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Document file missing from disk")

    suffix = "cover_letter" if row["doc_type"] == "cover_letter" else "cv"
    return FileResponse(
        path=str(file_path),
        filename=f"{suffix}_{job_id[:8]}.docx",
        media_type=(
            "application/vnd.openxmlformats-officedocument"
            ".wordprocessingml.document"
        ),
    )

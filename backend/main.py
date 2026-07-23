from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core.config import load_app
from core.storage import ensure_db_schema
from backend.routers import dashboard, documents, jobs

_app_config = load_app()


@asynccontextmanager
async def lifespan(app: FastAPI):
    ensure_db_schema(_app_config.storage)
    yield


app = FastAPI(title="Job Portal v2 API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=_app_config.backend.cors_origins or ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(jobs.router, prefix="/jobs", tags=["jobs"])
app.include_router(documents.router, prefix="/jobs", tags=["documents"])
app.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])

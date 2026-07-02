"""
Aletheia — AI Media Provenance Framework
Sprint 1: Media Registration Engine
Sprint 2: Provenance Embedding Engine

Entry point for the FastAPI application.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

from app.api.routes import registration, embedding
from app.database.connection import connect_to_mongo, close_mongo_connection
from app.core.config import settings

# ---------------------------------------------------------------------------
# Application factory
# ---------------------------------------------------------------------------

app = FastAPI(
    title="Aletheia — AI Media Provenance Framework",
    description="Sprint 1: Media Registration Engine | Sprint 2: Provenance Embedding Engine",
    version="2.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# ---------------------------------------------------------------------------
# CORS
# ---------------------------------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.ALLOWED_ORIGINS],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Lifespan events
# ---------------------------------------------------------------------------

@app.on_event("startup")
async def startup():
    await connect_to_mongo()


@app.on_event("shutdown")
async def shutdown():
    await close_mongo_connection()

# ---------------------------------------------------------------------------
# Ensure uploads directory exists (needed before StaticFiles mount)
# ---------------------------------------------------------------------------

os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

# ---------------------------------------------------------------------------
# Static file serving (uploaded images)
# ---------------------------------------------------------------------------

app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

# ---------------------------------------------------------------------------
# Routers
# ---------------------------------------------------------------------------

app.include_router(registration.router, prefix="/api", tags=["Registration"])
app.include_router(embedding.router,    prefix="/api", tags=["Embedding"])


# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------

@app.get("/api/health", tags=["Health"])
async def health():
    return {
        "status": "ok",
        "engines": ["Media Registration Engine", "Provenance Embedding Engine"],
        "version": "2.0",
    }

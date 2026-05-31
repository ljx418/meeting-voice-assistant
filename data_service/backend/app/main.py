"""Standalone FastAPI application for data_service."""

from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

_APP_DIR = Path(__file__).resolve().parent
_BACKEND_DIR = _APP_DIR.parent
load_dotenv(_BACKEND_DIR / ".env")
load_dotenv(_APP_DIR / ".env")

from app.api import api_router

_STATIC_ROOT = _APP_DIR / "static" / "knowledge_console"
_STATIC_ASSETS = _STATIC_ROOT / "assets"
_STATIC_INDEX = _STATIC_ROOT / "index.html"

app = FastAPI(
    title="data_service",
    version="0.1.0",
    description="Standalone personal knowledge data service.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root() -> dict:
    return {
        "service": "data_service",
        "docs": "/docs",
        "health": "/api/v1/health",
    }


app.include_router(api_router, prefix="/api")

app.mount(
    "/knowledge/assets",
    StaticFiles(directory=_STATIC_ASSETS, check_dir=False),
    name="knowledge_console_assets",
)


@app.get("/knowledge", include_in_schema=False)
@app.get("/knowledge/", include_in_schema=False)
@app.get("/knowledge/{path:path}", include_in_schema=False)
@app.head("/knowledge", include_in_schema=False)
@app.head("/knowledge/", include_in_schema=False)
@app.head("/knowledge/{path:path}", include_in_schema=False)
async def knowledge_console(path: str = "") -> FileResponse:
    if not _STATIC_INDEX.exists():
        from fastapi import HTTPException

        raise HTTPException(status_code=404, detail="Knowledge console is not built. Run `npm run build` in data_service/frontend.")
    return FileResponse(_STATIC_INDEX)

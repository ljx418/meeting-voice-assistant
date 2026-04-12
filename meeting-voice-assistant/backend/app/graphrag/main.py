from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.graphrag.api.v1.router import api_router
from app.graphrag.config import settings
from app.graphrag.storage.database import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database on startup."""
    await init_db()
    yield


app = FastAPI(
    title="GraphRAG Knowledge Service",
    version="1.0.0",
    description="GraphRAG-based knowledge management and query service",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")


@app.get("/")
async def root():
    return {"service": "GraphRAG Knowledge Service", "version": "1.0.0"}

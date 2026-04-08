from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.config import settings

app = FastAPI(
    title="GraphRAG Knowledge Service",
    version="1.0.0",
    description="GraphRAG-based knowledge management and query service",
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

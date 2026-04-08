from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.core.base import GraphEdge, GraphNode

router = APIRouter()


class GraphResponse(BaseModel):
    nodes: list[GraphNode]
    edges: list[GraphEdge]


class GraphQueryParams(BaseModel):
    namespace: str = "default"
    max_nodes: int = 100


@router.get("/", response_model=GraphResponse)
async def get_graph(params: GraphQueryParams) -> GraphResponse:
    raise HTTPException(status_code=501, detail="Not implemented")

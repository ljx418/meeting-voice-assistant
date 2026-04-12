from typing import Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from ...core.base import GraphEdge, GraphNode, GraphData
from ...core.registry import get_core

router = APIRouter()


class GraphNodeResponse(BaseModel):
    """Graph node response model for visualization."""
    id: str
    name: str
    type: str
    size: int = 10
    community_id: Optional[str] = None
    description: Optional[str] = None


class GraphEdgeResponse(BaseModel):
    """Graph edge response model for visualization."""
    source: str
    target: str
    relation: str


class GraphResponse(BaseModel):
    """Graph visualization response."""
    nodes: list[GraphNodeResponse]
    edges: list[GraphEdgeResponse]


@router.get("/", response_model=GraphResponse)
async def get_graph(
    max_nodes: int = Query(default=100, ge=10, le=500, description="Maximum number of nodes to return"),
) -> GraphResponse:
    """
    Get knowledge graph data for visualization.

    - **max_nodes**: Maximum number of nodes to return (10-500, default: 100)

    Returns nodes and edges for graph visualization.

    Note: Environment isolation is handled via separate GRAPHRAG_WORKSPACE directories.
    """
    try:
        graph_data: GraphData = await get_core().get_graph_data(max_nodes=max_nodes)

        # Convert GraphData to response format
        nodes = [
            GraphNodeResponse(
                id=node.node_id,
                name=node.label,
                type=node.node_type,
                size=node.size,
                community_id=node.attributes.get("community_id"),
                description=node.attributes.get("description"),
            )
            for node in graph_data.nodes
        ]

        edges = [
            GraphEdgeResponse(
                source=edge.source_id,
                target=edge.target_id,
                relation=edge.relationship,
            )
            for edge in graph_data.edges
        ]

        return GraphResponse(nodes=nodes, edges=edges)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get graph data: {str(e)}")

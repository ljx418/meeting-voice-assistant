"""Shared Graph Query contract for target HTTP and CLI surfaces."""

from __future__ import annotations

from typing import Any, Callable

from .graph_community_contract import _project_community
from .graph_neighbors_contract import _project_edge, _project_node
from .mcp_common import blocked as contract_blocked
from .mcp_common import bounded_int
from .mcp_common import envelope as contract_envelope


def graph_query_payload(
    service: Any,
    *,
    workspace_id: str,
    query: str | None = None,
    top_k: object = 10,
    include_nodes: bool = True,
    include_edges: bool = True,
    include_communities: bool = False,
    envelope: Callable[..., dict[str, Any]] = contract_envelope,
    blocked: Callable[..., dict[str, Any]] = contract_blocked,
) -> dict[str, Any]:
    normalized_query = str(query or "").strip()
    if not normalized_query:
        raise ValueError("q is required")
    normalized_top_k = bounded_int(top_k, default=10, minimum=1, maximum=50, field="top_k")

    response = service.query_graphrag(normalized_query, top_k=normalized_top_k)
    graph = dict((response.engine_payloads or {}).get("graphrag") or {})
    if graph.get("status") == "missing_db":
        return blocked(
            workspace_id=workspace_id,
            message="Graph query index is not available for this workspace",
            code="graph_query_unavailable",
            next_actions=["knowledge_build_start"],
        )

    node_lookup = {str(node.get("id") or node.get("node_id") or ""): node for node in list(graph.get("nodes") or [])}
    data: dict[str, Any] = {
        "query": normalized_query,
        "top_k": normalized_top_k,
        "answer": response.answer,
        "summary": response.answer,
    }
    if include_nodes:
        data["nodes"] = [_project_node(item) for item in list(graph.get("nodes") or [])[:normalized_top_k]]
    if include_edges:
        data["edges"] = [_project_edge(item) for item in list(graph.get("edges") or [])[:normalized_top_k]]
    if include_communities:
        data["communities"] = [
            _project_community(item, node_lookup=node_lookup, include_members=False)
            for item in list(graph.get("communities") or [])[:normalized_top_k]
        ]

    return envelope(
        workspace_id=workspace_id,
        artifact_refs=[{"type": "graph", "artifact_ref": f"graph://{workspace_id}/query"}],
        next_actions=["knowledge_graph_snapshot"],
        data=data,
    )

"""Shared Graph Session inspection contract for target HTTP and CLI surfaces."""

from __future__ import annotations

from typing import Any, Callable

from .graph_neighbors_contract import _project_edge, _project_node
from .mcp_common import blocked as contract_blocked
from .mcp_common import bounded_int
from .mcp_common import envelope as contract_envelope


def graph_session_payload(
    session_service: Any,
    *,
    workspace_id: str,
    session_id: str | None = None,
    limit: object = 20,
    include_nodes: bool = False,
    include_edges: bool = False,
    node_limit: object = 50,
    edge_limit: object = 100,
    envelope: Callable[..., dict[str, Any]] = contract_envelope,
    blocked: Callable[..., dict[str, Any]] = contract_blocked,
) -> dict[str, Any]:
    normalized_session_id = str(session_id or "").strip()
    normalized_limit = bounded_int(limit, default=20, minimum=1, maximum=100, field="limit")
    normalized_node_limit = bounded_int(node_limit, default=50, minimum=1, maximum=200, field="node_limit")
    normalized_edge_limit = bounded_int(edge_limit, default=100, minimum=1, maximum=500, field="edge_limit")

    if normalized_session_id:
        session = session_service.get_session(session_id=normalized_session_id)
        if not session:
            return blocked(
                workspace_id=workspace_id,
                message=f"Unknown session_id: {normalized_session_id}",
                code="unknown_session",
                next_actions=["knowledge_session_get"],
            )
        snapshot = session_service.graph_snapshot(
            scope="session",
            session_id=normalized_session_id,
            max_nodes=max(normalized_node_limit, normalized_edge_limit * 2, 200),
            include_communities=True,
            include_source_refs=False,
        )
        if snapshot.get("status") != "ok":
            return blocked(
                workspace_id=workspace_id,
                message=f"Session graph artifact is not available for session_id: {normalized_session_id}",
                code="session_graph_no_artifact",
                next_actions=["knowledge_session_build_start"],
                data={"session_id": normalized_session_id, "artifact_ref": _artifact_ref(workspace_id, normalized_session_id)},
            )
        summary = _project_session_summary(
            session=session,
            snapshot=snapshot,
            workspace_id=workspace_id,
            include_nodes=include_nodes,
            include_edges=include_edges,
            node_limit=normalized_node_limit,
            edge_limit=normalized_edge_limit,
        )
        return envelope(
            workspace_id=workspace_id,
            artifact_refs=[{"type": "session_graph", "session_id": normalized_session_id, "artifact_ref": _artifact_ref(workspace_id, normalized_session_id)}],
            next_actions=["knowledge_graph_snapshot"],
            data={"session": summary},
        )

    items = []
    for session in session_service.list_sessions(limit=normalized_limit):
        current_session_id = str(session.get("session_id") or "")
        if not current_session_id:
            continue
        snapshot = session_service.graph_snapshot(
            scope="session",
            session_id=current_session_id,
            max_nodes=200,
            include_communities=True,
            include_source_refs=False,
        )
        if snapshot.get("status") != "ok":
            continue
        items.append(
            _project_session_summary(
                session=session,
                snapshot=snapshot,
                workspace_id=workspace_id,
                include_nodes=False,
                include_edges=False,
                node_limit=0,
                edge_limit=0,
            )
        )
        if len(items) >= normalized_limit:
            break

    return envelope(
        workspace_id=workspace_id,
        artifact_refs=[{"type": "session_graph", "artifact_ref": f"graph-session://{workspace_id}/sessions"}],
        next_actions=["knowledge_graph_snapshot"],
        data={"limit": normalized_limit, "items": items},
    )


def _project_session_summary(
    *,
    session: dict[str, Any],
    snapshot: dict[str, Any],
    workspace_id: str,
    include_nodes: bool,
    include_edges: bool,
    node_limit: int,
    edge_limit: int,
) -> dict[str, Any]:
    session_id = str(session.get("session_id") or snapshot.get("session_id") or "")
    nodes = list(snapshot.get("nodes") or [])
    edges = list(snapshot.get("edges") or [])
    communities = list(snapshot.get("communities") or [])
    stats = dict(snapshot.get("stats") or {})
    payload = {
        "workspace_id": workspace_id,
        "session_id": session_id,
        "status": snapshot.get("status") or session.get("status") or "ok",
        "node_count": stats.get("node_count", len(nodes)),
        "edge_count": stats.get("edge_count", len(edges)),
        "community_count": stats.get("community_count", len(communities)),
        "artifact_ref": _artifact_ref(workspace_id, session_id),
        "created_at": session.get("created_at"),
        "updated_at": snapshot.get("updated_at") or session.get("updated_at"),
    }
    if include_nodes:
        payload["nodes"] = [_project_node(node) for node in nodes[:node_limit]]
        payload["node_limit"] = node_limit
        payload["nodes_truncated"] = len(nodes) > node_limit
    if include_edges:
        payload["edges"] = [_project_edge(edge) for edge in edges[:edge_limit]]
        payload["edge_limit"] = edge_limit
        payload["edges_truncated"] = len(edges) > edge_limit
    return payload


def _artifact_ref(workspace_id: str, session_id: str) -> str:
    return f"graph-session://{workspace_id}/{session_id}"

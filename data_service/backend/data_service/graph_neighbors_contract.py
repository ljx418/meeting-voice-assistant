"""Shared Graph Neighbors contract for target HTTP and CLI surfaces."""

from __future__ import annotations

from typing import Any, Callable

from .mcp_common import blocked as contract_blocked
from .mcp_common import bounded_int
from .mcp_common import envelope as contract_envelope


INTERNAL_GRAPH_KEYS = {
    "workspace_path",
    "root_path",
    "filesystem_path",
    "artifact_physical_path",
    "graphrag_cache_path",
    "cache_path",
    "physical_path",
    "internal_path",
    "debug_paths",
    "db_path",
    "path",
    "paths",
    "local_path",
    "source_path",
    "original_path",
}


def graph_neighbors_payload(
    service: Any,
    *,
    workspace_id: str,
    node_id: str | None = None,
    entity_id: str | None = None,
    depth: object = 1,
    max_nodes: object = 80,
    envelope: Callable[..., dict[str, Any]] = contract_envelope,
    blocked: Callable[..., dict[str, Any]] = contract_blocked,
) -> dict[str, Any]:
    root_node_id = _normalize_root_node(node_id=node_id, entity_id=entity_id)
    normalized_depth = bounded_int(depth, default=1, minimum=1, maximum=3, field="depth")
    normalized_max_nodes = bounded_int(max_nodes, default=80, minimum=1, maximum=500, field="max_nodes")

    snapshot = service.get_graph_snapshot(max_nodes=max(500, normalized_max_nodes * 3))
    nodes = list(snapshot.get("nodes") or [])
    edges = list(snapshot.get("edges") or [])
    if not nodes and not edges:
        return blocked(
            workspace_id=workspace_id,
            message="Graph snapshot is not available for this workspace",
            code="graph_snapshot_unavailable",
            next_actions=["knowledge_build_start"],
        )

    lookup = {str(node.get("id") or node.get("node_id") or ""): node for node in nodes}
    if root_node_id not in lookup:
        return blocked(
            workspace_id=workspace_id,
            message=f"Unknown graph node: {root_node_id}",
            code="unknown_graph_node",
            next_actions=["knowledge_graph_snapshot"],
        )

    visited = {root_node_id}
    frontier = {root_node_id}
    selected_edges: list[dict[str, Any]] = []
    truncated = False
    for _ in range(normalized_depth):
        next_frontier: set[str] = set()
        for edge in edges:
            source = str(edge.get("source") or edge.get("source_node_id") or "")
            target = str(edge.get("target") or edge.get("target_node_id") or "")
            if source in frontier or target in frontier:
                selected_edges.append(edge)
                next_frontier.update({source, target})
        next_frontier -= visited
        visited |= next_frontier
        frontier = next_frontier
        if len(visited) >= normalized_max_nodes:
            truncated = True
            break

    ordered_ids = [root_node_id] + [node_id for node_id in sorted(visited) if node_id != root_node_id]
    limited_ids = set(ordered_ids[:normalized_max_nodes])
    if len(visited) > len(limited_ids):
        truncated = True
    projected_nodes = [_project_node(lookup[node_id]) for node_id in ordered_ids if node_id in limited_ids and node_id in lookup]
    projected_edges = [
        _project_edge(edge)
        for edge in selected_edges
        if str(edge.get("source") or edge.get("source_node_id") or "") in limited_ids
        and str(edge.get("target") or edge.get("target_node_id") or "") in limited_ids
    ][: normalized_max_nodes * 3]

    payload = {
        "node_id": root_node_id,
        "entity_id": root_node_id if str(lookup[root_node_id].get("type") or lookup[root_node_id].get("node_type") or "") == "entity" else None,
        "depth": normalized_depth,
        "max_nodes": normalized_max_nodes,
        "truncated": truncated or len(projected_edges) < len(selected_edges),
        "nodes": projected_nodes,
        "edges": projected_edges,
    }
    return envelope(
        workspace_id=workspace_id,
        artifact_refs=[{"type": "graph", "artifact_ref": f"graph://{workspace_id}/neighbors/{root_node_id}"}],
        next_actions=["knowledge_graph_snapshot"],
        data=payload,
    )


def _normalize_root_node(*, node_id: str | None, entity_id: str | None) -> str:
    normalized_node = str(node_id or "").strip()
    normalized_entity = str(entity_id or "").strip()
    if not normalized_node and not normalized_entity:
        raise ValueError("node_id or entity_id is required")
    if normalized_node and normalized_entity:
        raise ValueError("node_id and entity_id are mutually exclusive")
    return normalized_node or normalized_entity


def _project_node(node: dict[str, Any]) -> dict[str, Any]:
    node_id = str(node.get("id") or node.get("node_id") or "")
    node_type = node.get("type") or node.get("node_type") or node.get("kind")
    return {
        "node_id": node_id,
        "entity_id": node_id if node_type == "entity" else None,
        "label": node.get("label") or node.get("name") or node_id,
        "name": node.get("name") or node.get("label") or node_id,
        "type": node_type,
        "kind": node_type,
        "summary": node.get("summary"),
        "score": node.get("score"),
        "metadata": _stable_metadata(node.get("metadata") or node.get("attributes") or node.get("metrics") or {}),
    }


def _project_edge(edge: dict[str, Any]) -> dict[str, Any]:
    source = str(edge.get("source") or edge.get("source_node_id") or "")
    target = str(edge.get("target") or edge.get("target_node_id") or "")
    relation = edge.get("relation") or edge.get("type") or edge.get("label")
    return {
        "edge_id": edge.get("id") or edge.get("edge_id") or f"{source}->{target}:{relation}",
        "source_node_id": source,
        "target_node_id": target,
        "relation": relation,
        "type": relation,
        "weight": edge.get("weight"),
        "evidence_count": edge.get("evidence_count"),
        "metadata": _stable_metadata(edge.get("metadata") or edge.get("attributes") or {}),
    }


def _stable_metadata(value: Any) -> Any:
    if isinstance(value, dict):
        return {
            key: _stable_metadata(item)
            for key, item in value.items()
            if key not in INTERNAL_GRAPH_KEYS and not _looks_like_path_key(key)
        }
    if isinstance(value, list):
        return [_stable_metadata(item) for item in value]
    return value


def _looks_like_path_key(key: str) -> bool:
    lowered = str(key).lower()
    return lowered.endswith("_path") or lowered.endswith("_paths") or "physical" in lowered or "cache" in lowered

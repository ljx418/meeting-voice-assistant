"""Shared Graph Community contract for target HTTP and CLI surfaces."""

from __future__ import annotations

from typing import Any, Callable

from .graph_neighbors_contract import INTERNAL_GRAPH_KEYS, _project_node
from .mcp_common import blocked as contract_blocked
from .mcp_common import bounded_int
from .mcp_common import envelope as contract_envelope


def graph_community_payload(
    service: Any,
    *,
    workspace_id: str,
    community_id: str | None = None,
    limit: object = 20,
    include_members: bool = False,
    envelope: Callable[..., dict[str, Any]] = contract_envelope,
    blocked: Callable[..., dict[str, Any]] = contract_blocked,
) -> dict[str, Any]:
    normalized_limit = bounded_int(limit, default=20, minimum=1, maximum=100, field="limit")
    normalized_community_id = str(community_id or "").strip()
    snapshot = service.get_graph_snapshot(max_nodes=500)
    communities = list(snapshot.get("communities") or [])
    if not communities:
        return blocked(
            workspace_id=workspace_id,
            message="Graph communities are not available for this workspace",
            code="graph_community_unavailable",
            next_actions=["knowledge_build_start"],
        )

    node_lookup = {str(node.get("id") or node.get("node_id") or ""): node for node in list(snapshot.get("nodes") or [])}
    if normalized_community_id:
        matched = next((item for item in communities if str(item.get("id") or item.get("community_id") or "") == normalized_community_id), None)
        if not matched:
            return blocked(
                workspace_id=workspace_id,
                message=f"Unknown graph community: {normalized_community_id}",
                code="unknown_graph_community",
                next_actions=["knowledge_graph_community"],
            )
        data = {
            "community_id": normalized_community_id,
            "community": _project_community(matched, node_lookup=node_lookup, include_members=include_members),
        }
        artifact_ref = f"graph://{workspace_id}/community/{normalized_community_id}"
    else:
        data = {
            "limit": normalized_limit,
            "items": [
                _project_community(item, node_lookup=node_lookup, include_members=include_members)
                for item in communities[:normalized_limit]
            ],
        }
        artifact_ref = f"graph://{workspace_id}/communities"

    return envelope(
        workspace_id=workspace_id,
        artifact_refs=[{"type": "graph", "artifact_ref": artifact_ref}],
        next_actions=["knowledge_graph_snapshot"],
        data=data,
    )


def _project_community(community: dict[str, Any], *, node_lookup: dict[str, dict[str, Any]], include_members: bool) -> dict[str, Any]:
    community_id = str(community.get("id") or community.get("community_id") or "")
    entity_ids = [str(item) for item in (community.get("entity_ids") or community.get("node_ids") or []) if str(item)]
    payload = {
        "community_id": community_id,
        "title": community.get("title") or community.get("label") or community_id,
        "summary": community.get("summary") or "",
        "entity_count": community.get("entity_count") or (community.get("stats") or {}).get("entity_count") or len(entity_ids),
        "relationship_count": community.get("relationship_count") or (community.get("stats") or {}).get("relationship_count") or 0,
        "score": community.get("score") or (community.get("stats") or {}).get("score"),
        "rank": community.get("rank"),
        "metadata": _stable_community_metadata(community.get("metadata") or community.get("attributes") or {}),
    }
    if include_members:
        payload["members"] = [
            _project_node(node_lookup[node_id])
            for node_id in entity_ids
            if node_id in node_lookup
        ]
    return payload


def _stable_community_metadata(value: Any) -> Any:
    if isinstance(value, dict):
        return {
            key: _stable_community_metadata(item)
            for key, item in value.items()
            if key not in INTERNAL_GRAPH_KEYS and not _looks_like_graph_internal_key(key)
        }
    if isinstance(value, list):
        return [_stable_community_metadata(item) for item in value]
    return value


def _looks_like_graph_internal_key(key: str) -> bool:
    lowered = str(key).lower()
    return (
        lowered.endswith("_path")
        or lowered.endswith("_paths")
        or "physical" in lowered
        or "cache" in lowered
        or "parquet" in lowered
        or "json_path" in lowered
        or "working_directory" in lowered
    )

"""Stable read-only Session query contract for target HTTP surfaces."""

from __future__ import annotations

from typing import Any, Callable

from .graph_neighbors_contract import _project_edge, _project_node
from .mcp_common import blocked as contract_blocked
from .mcp_common import bounded_int
from .mcp_common import envelope as contract_envelope

_MAX_QUERY_LENGTH = 4096
_MAX_TOP_K = 50
_INTERNAL_KEYS = {
    "workspace_path",
    "root_path",
    "filesystem_path",
    "session_storage_path",
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
_RAW_PAYLOAD_KEYS = {
    "raw_prompt",
    "raw_prompts",
    "prompt",
    "prompts",
    "raw_model_message",
    "raw_model_messages",
    "model_messages",
    "messages",
    "embedding",
    "embeddings",
    "embedding_vector",
    "vectors",
    "raw_response",
    "provider_response",
    "diagnostics",
    "details",
}


def query_session_payload(
    session_service: Any,
    *,
    workspace_id: str,
    session_id: str,
    query: Any,
    top_k: Any = 8,
    evidence_resolver: Callable[[str, int], list[dict[str, Any]]] | None = None,
    envelope: Callable[..., dict[str, Any]] = contract_envelope,
    blocked: Callable[..., dict[str, Any]] = contract_blocked,
) -> dict[str, Any]:
    normalized_query = str(query or "").strip()
    if not normalized_query:
        return blocked(
            workspace_id=workspace_id,
            message="query is required",
            code="invalid_session_query_request",
            next_actions=["knowledge_session_get"],
        )
    if len(normalized_query) > _MAX_QUERY_LENGTH:
        return blocked(
            workspace_id=workspace_id,
            message=f"query exceeds maximum length {_MAX_QUERY_LENGTH}",
            code="invalid_session_query_request",
            next_actions=["knowledge_session_get"],
        )
    try:
        normalized_top_k = bounded_int(top_k, default=8, minimum=1, maximum=_MAX_TOP_K, field="top_k")
    except ValueError as exc:
        return blocked(
            workspace_id=workspace_id,
            message=str(exc),
            code="invalid_session_query_request",
            next_actions=["knowledge_session_get"],
        )

    normalized_session_id = str(session_id or "").strip()
    session = session_service.get_session(session_id=normalized_session_id)
    if not session:
        return blocked(
            workspace_id=workspace_id,
            message=f"Unknown session_id: {normalized_session_id}",
            code="unknown_session_id",
            next_actions=["knowledge_session_list"],
        )
    if session.get("status") == "disposed":
        return blocked(
            workspace_id=workspace_id,
            message=f"Session is disposed: {normalized_session_id}",
            code="session_disposed",
            next_actions=["knowledge_session_create", "knowledge_session_list"],
        )

    try:
        payload = session_service.query_session(
            session_id=normalized_session_id,
            query=normalized_query,
            top_k=normalized_top_k,
            include_workspace_context=False,
            workspace_context=None,
        )
    except (KeyError, ValueError) as exc:
        return blocked(
            workspace_id=workspace_id,
            message=str(exc),
            code="session_query_blocked",
            next_actions=["knowledge_session_get"],
        )

    if payload.get("status") not in {None, "ok"}:
        return blocked(
            workspace_id=workspace_id,
            message=f"Session graph artifact is not available for session_id: {normalized_session_id}",
            code="session_graph_no_artifact",
            next_actions=["knowledge_session_build_start"],
            data={"session_id": normalized_session_id, "artifact_ref": _artifact_ref(workspace_id, normalized_session_id)},
        )

    evidence = _resolve_evidence_items(evidence_resolver, normalized_query, normalized_top_k)
    projected = _project_query_payload(
        payload,
        workspace_id=workspace_id,
        session_id=normalized_session_id,
        query=normalized_query,
        top_k=normalized_top_k,
        evidence=evidence,
    )
    return envelope(
        workspace_id=workspace_id,
        artifact_refs=[{"type": "session_graph", "session_id": normalized_session_id, "artifact_ref": _artifact_ref(workspace_id, normalized_session_id)}],
        next_actions=["knowledge_session_build_status", "knowledge_graph_session"],
        data=projected,
    )


def _project_query_payload(
    payload: dict[str, Any],
    *,
    workspace_id: str,
    session_id: str,
    query: str,
    top_k: int,
    evidence: list[dict[str, Any]],
) -> dict[str, Any]:
    session_payload = payload.get("session_payload") if isinstance(payload.get("session_payload"), dict) else {}
    graph_only = any(isinstance(session_payload.get(key), list) and session_payload.get(key) for key in ("nodes", "edges", "communities"))
    evidence_state = "has_evidence_span_ids" if evidence else "graph_only_no_evidence" if graph_only else "no_evidence_accepted"
    return {
        "workspace_id": workspace_id,
        "session_id": session_id,
        "query": query,
        "top_k": top_k,
        "answer": payload.get("answer"),
        "evidence": [_stable_value(item) for item in evidence[:top_k]],
        "evidence_refs": [_stable_value(item) for item in evidence[:top_k]],
        "evidence_state": evidence_state,
        "results": [_stable_value(_project_hit(item)) for item in list(payload.get("hits") or [])[:top_k]],
        "items": [_stable_value(_project_hit(item)) for item in list(payload.get("hits") or [])[:top_k]],
        "nodes": [_stable_value(_project_node(item)) for item in list(session_payload.get("nodes") or [])[:top_k]],
        "edges": [_stable_value(_project_edge(item)) for item in list(session_payload.get("edges") or [])[: top_k * 3]],
        "communities": [_project_community(item) for item in list(session_payload.get("communities") or [])[:top_k]],
        "artifact_ref": _artifact_ref(workspace_id, session_id),
    }


def _resolve_evidence_items(evidence_resolver: Callable[[str, int], list[dict[str, Any]]] | None, query: str, top_k: int) -> list[dict[str, Any]]:
    if evidence_resolver is None:
        return []
    try:
        resolved = evidence_resolver(query, top_k)
    except Exception:
        return []
    return [_stable_value(item) for item in list(resolved or []) if _is_resolvable_evidence_item(item)]


def _is_resolvable_evidence_item(item: Any) -> bool:
    if not isinstance(item, dict):
        return False
    return all(isinstance(item.get(key), str) and item.get(key) for key in ("source_id", "unit_id", "evidence_id"))


def _project_hit(hit: dict[str, Any]) -> dict[str, Any]:
    return {
        "title": hit.get("title"),
        "snippet": hit.get("snippet"),
        "source_id": hit.get("source"),
        "score": hit.get("score"),
        "kind": hit.get("kind"),
        "source_refs": _stable_value(hit.get("source_refs") or []),
    }


def _project_community(community: dict[str, Any]) -> dict[str, Any]:
    community_id = str(community.get("id") or community.get("community_id") or "")
    return {
        "community_id": community_id,
        "title": community.get("title") or community_id,
        "summary": community.get("summary"),
        "entity_count": community.get("entity_count") or len(community.get("entity_ids") or []),
        "relationship_count": community.get("relationship_count"),
        "score": community.get("score"),
        "rank": community.get("rank"),
        "metadata": _stable_value(community.get("metadata") or {}),
    }


def _artifact_ref(workspace_id: str, session_id: str) -> str:
    return f"graph-session://{workspace_id}/{session_id}"


def _stable_value(value: Any) -> Any:
    if isinstance(value, dict):
        return {
            key: _stable_value(item)
            for key, item in value.items()
            if str(key) not in _INTERNAL_KEYS and str(key) not in _RAW_PAYLOAD_KEYS and not _looks_like_path_key(str(key))
        }
    if isinstance(value, list):
        return [_stable_value(item) for item in value]
    return value


def _looks_like_path_key(key: str) -> bool:
    lowered = key.lower()
    return lowered.endswith("_path") or lowered.endswith("_paths") or "physical" in lowered or "cache" in lowered

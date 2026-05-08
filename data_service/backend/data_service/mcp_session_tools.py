"""Session-scoped MCP tool schemas and handlers."""

from __future__ import annotations

import json
import threading
from typing import Any, Callable

from .models import QueryMode
from .service import DataService
from .session_service import SESSION_BUILD_MODES, SESSION_TERMINAL_STATUSES, SessionKnowledgeService


SESSION_TOOL_NAMES = {
    "knowledge_session_create",
    "knowledge_session_get",
    "knowledge_session_list",
    "knowledge_session_close",
    "knowledge_session_delete",
    "knowledge_session_ingest",
    "knowledge_session_build_start",
    "knowledge_session_build_status",
    "knowledge_session_build_cancel",
    "knowledge_graph_snapshot",
    "knowledge_graph_neighbors",
    "knowledge_community_summary",
    "knowledge_session_query",
    "knowledge_actor_summary",
}

SESSION_TOOL_SPECS = [
    {
        "name": "knowledge_session_create",
        "description": "Create or reuse a scoped knowledge session inside a workspace",
        "inputSchema": {
            "type": "object",
            "properties": {
                "workspace": {"type": "string"},
                "workspace_id": {"type": "string"},
                "external_id": {"type": "string"},
                "session_type": {"type": "string"},
                "title": {"type": "string"},
                "ephemeral": {"type": "boolean", "default": False},
                "ttl_seconds": {"type": "integer"},
                "metadata": {"type": "object"},
            },
        },
    },
    {
        "name": "knowledge_session_get",
        "description": "Inspect one scoped knowledge session",
        "inputSchema": {
            "type": "object",
            "properties": {
                "workspace": {"type": "string"},
                "workspace_id": {"type": "string"},
                "session_id": {"type": "string"},
                "external_id": {"type": "string"},
            },
        },
    },
    {
        "name": "knowledge_session_list",
        "description": "List scoped knowledge sessions in a workspace",
        "inputSchema": {
            "type": "object",
            "properties": {
                "workspace": {"type": "string"},
                "workspace_id": {"type": "string"},
                "status": {"type": "string"},
                "session_type": {"type": "string"},
                "include_disposed": {"type": "boolean", "default": False},
                "limit": {"type": "integer", "default": 100},
            },
        },
    },
    {
        "name": "knowledge_session_close",
        "description": "Close or reopen a scoped knowledge session",
        "inputSchema": {
            "type": "object",
            "properties": {
                "workspace": {"type": "string"},
                "workspace_id": {"type": "string"},
                "session_id": {"type": "string"},
                "reopen": {"type": "boolean", "default": False},
            },
            "required": ["session_id"],
        },
    },
    {
        "name": "knowledge_session_delete",
        "description": "Dispose a session and remove session-scoped graph, sources, communities, summaries, and caches",
        "inputSchema": {
            "type": "object",
            "properties": {
                "workspace": {"type": "string"},
                "workspace_id": {"type": "string"},
                "session_id": {"type": "string"},
            },
            "required": ["session_id"],
        },
    },
    {
        "name": "knowledge_session_ingest",
        "description": "Ingest structured records into a scoped session",
        "inputSchema": {
            "type": "object",
            "properties": {
                "workspace": {"type": "string"},
                "workspace_id": {"type": "string"},
                "session_id": {"type": "string"},
                "source_type": {"type": "string"},
                "content_format": {"type": "string", "enum": ["text", "markdown", "turns", "json"]},
                "title": {"type": "string"},
                "records": {"type": "array", "items": {"type": "object"}},
                "content": {},
                "metadata": {"type": "object"},
                "related_source_ids": {"type": "array", "items": {"type": "string"}},
                "related_paths": {"type": "array", "items": {"type": "string"}},
                "auto_link": {"type": "boolean", "default": False},
                "allow_closed_write": {"type": "boolean", "default": False},
            },
            "required": ["session_id"],
        },
    },
    {
        "name": "knowledge_session_build_start",
        "description": "Start a session-scoped distill/graph/community build",
        "inputSchema": {
            "type": "object",
            "properties": {
                "workspace": {"type": "string"},
                "workspace_id": {"type": "string"},
                "session_id": {"type": "string"},
                "mode": {"type": "string", "enum": sorted(SESSION_BUILD_MODES)},
                "sync": {"type": "boolean", "default": False},
                "wait": {"type": "boolean", "default": False},
            },
            "required": ["session_id"],
        },
    },
    {
        "name": "knowledge_session_build_status",
        "description": "Poll a session-scoped build operation",
        "inputSchema": {
            "type": "object",
            "properties": {
                "workspace": {"type": "string"},
                "workspace_id": {"type": "string"},
                "session_id": {"type": "string"},
                "operation_id": {"type": "string"},
            },
            "required": ["session_id", "operation_id"],
        },
    },
    {
        "name": "knowledge_session_build_cancel",
        "description": "Cancel a session-scoped build operation",
        "inputSchema": {
            "type": "object",
            "properties": {
                "workspace": {"type": "string"},
                "workspace_id": {"type": "string"},
                "session_id": {"type": "string"},
                "operation_id": {"type": "string"},
                "reason": {"type": "string"},
            },
            "required": ["session_id", "operation_id"],
        },
    },
    {
        "name": "knowledge_graph_snapshot",
        "description": "Read a workspace or session graph snapshot",
        "inputSchema": {
            "type": "object",
            "properties": {
                "workspace": {"type": "string"},
                "workspace_id": {"type": "string"},
                "scope": {"type": "string", "enum": ["workspace", "session"], "default": "workspace"},
                "session_id": {"type": "string"},
                "max_nodes": {"type": "integer", "default": 200},
                "include_communities": {"type": "boolean", "default": True},
                "include_source_refs": {"type": "boolean", "default": True},
                "node_types": {"type": "array", "items": {"type": "string"}},
            },
        },
    },
    {
        "name": "knowledge_graph_neighbors",
        "description": "Read session graph neighbors for a node",
        "inputSchema": {
            "type": "object",
            "properties": {
                "workspace": {"type": "string"},
                "workspace_id": {"type": "string"},
                "session_id": {"type": "string"},
                "node_id": {"type": "string"},
                "depth": {"type": "integer", "default": 1},
                "max_nodes": {"type": "integer", "default": 80},
            },
            "required": ["session_id", "node_id"],
        },
    },
    {
        "name": "knowledge_community_summary",
        "description": "Read session community summaries",
        "inputSchema": {
            "type": "object",
            "properties": {
                "workspace": {"type": "string"},
                "workspace_id": {"type": "string"},
                "session_id": {"type": "string"},
                "community_id": {"type": "string"},
                "limit": {"type": "integer", "default": 20},
            },
            "required": ["session_id"],
        },
    },
    {
        "name": "knowledge_session_query",
        "description": "Query a scoped session graph and optionally include workspace context",
        "inputSchema": {
            "type": "object",
            "properties": {
                "workspace": {"type": "string"},
                "workspace_id": {"type": "string"},
                "session_id": {"type": "string"},
                "query": {"type": "string"},
                "top_k": {"type": "integer", "default": 8},
                "include_workspace_context": {"type": "boolean", "default": False},
            },
            "required": ["session_id", "query"],
        },
    },
    {
        "name": "knowledge_actor_summary",
        "description": "Summarize one actor inside a scoped session",
        "inputSchema": {
            "type": "object",
            "properties": {
                "workspace": {"type": "string"},
                "workspace_id": {"type": "string"},
                "scope": {"type": "string", "enum": ["session"], "default": "session"},
                "session_id": {"type": "string"},
                "actor_id": {"type": "string"},
                "include_units": {"type": "boolean", "default": True},
                "unit_types": {"type": "array", "items": {"type": "string"}},
            },
            "required": ["session_id", "actor_id"],
        },
    },
]


def handle_session_tool(
    name: str,
    arguments: dict[str, Any],
    *,
    service: DataService,
    workspace_id: str,
    envelope: Callable[..., dict[str, Any]],
    blocked: Callable[..., dict[str, Any]],
    bounded_int: Callable[..., int],
) -> dict[str, Any]:
    """Handle session-scoped MCP tools and return an envelope payload."""

    session_service = SessionKnowledgeService(service.workspace, workspace_id=workspace_id)

    def blocked_from_error(exc: Exception, *, session_id: str | None = None) -> dict[str, Any]:
        return blocked(
            workspace_id=workspace_id,
            message=str(exc),
            next_actions=["knowledge_session_get", "knowledge_session_list"],
            data={
                "error": {
                    "code": exc.__class__.__name__,
                    "message": str(exc),
                    "retryable": False,
                    **({"session_id": session_id} if session_id else {}),
                }
            },
        )

    try:
        if name == "knowledge_session_create":
            result = session_service.create_session(
                external_id=arguments.get("external_id"),
                session_type=str(arguments.get("session_type") or "generic"),
                title=str(arguments.get("title") or ""),
                ephemeral=bool(arguments.get("ephemeral", False)),
                ttl_seconds=arguments.get("ttl_seconds"),
                metadata=dict(arguments.get("metadata") or {}),
            )
            return envelope(
                workspace_id=workspace_id,
                status="ok",
                artifact_refs=[{"type": "session", "session_id": result["session"]["session_id"]}],
                next_actions=["knowledge_session_ingest", "knowledge_session_build_start"],
                data=result,
            )

        if name == "knowledge_session_get":
            session = session_service.get_session(
                session_id=arguments.get("session_id"),
                external_id=arguments.get("external_id"),
            )
            if not session:
                return blocked(
                    workspace_id=workspace_id,
                    message="Unknown session",
                    next_actions=["knowledge_session_create", "knowledge_session_list"],
                )
            return envelope(workspace_id=workspace_id, data={"session": session})

        if name == "knowledge_session_list":
            items = session_service.list_sessions(
                status=arguments.get("status"),
                session_type=arguments.get("session_type"),
                include_disposed=bool(arguments.get("include_disposed", False)),
                limit=bounded_int(arguments.get("limit"), default=100, minimum=1, maximum=500, field="limit"),
            )
            return envelope(workspace_id=workspace_id, data={"items": items})

        if name == "knowledge_session_close":
            session_id = str(arguments.get("session_id") or "")
            session = session_service.close_session(session_id, reopen=bool(arguments.get("reopen", False)))
            return envelope(
                workspace_id=workspace_id,
                status=session.get("status", "closed"),
                artifact_refs=[{"type": "session", "session_id": session_id}],
                next_actions=["knowledge_session_get", "knowledge_session_delete"],
                data={"session": session},
            )

        if name == "knowledge_session_delete":
            session_id = str(arguments.get("session_id") or "")
            session = session_service.delete_session(session_id)
            return envelope(
                workspace_id=workspace_id,
                status="disposed",
                artifact_refs=[{"type": "session", "session_id": session_id}],
                next_actions=["knowledge_session_list"],
                data={"session": session},
            )

        if name == "knowledge_session_ingest":
            session_id = str(arguments.get("session_id") or "")
            result = session_service.ingest(
                session_id=session_id,
                source_type=str(arguments.get("source_type") or "structured"),
                content_format=str(arguments.get("content_format") or "text"),
                title=str(arguments.get("title") or ""),
                records=list(arguments.get("records") or []),
                content=arguments.get("content"),
                metadata=dict(arguments.get("metadata") or {}),
                related_source_ids=[str(item) for item in (arguments.get("related_source_ids") or [])],
                related_paths=[str(item) for item in (arguments.get("related_paths") or [])],
                auto_link=bool(arguments.get("auto_link", False)),
                allow_closed_write=bool(arguments.get("allow_closed_write", False)),
            )
            source = result["source"]
            return envelope(
                workspace_id=workspace_id,
                artifact_refs=[{"type": "session_source", "session_id": session_id, "source_id": source["source_id"]}],
                next_actions=["knowledge_session_build_start"],
                data={
                    "session_id": session_id,
                    "source": {
                        "source_id": source["source_id"],
                        "title": source["title"],
                        "source_type": source["source_type"],
                        "content_format": source["content_format"],
                        "record_count": source["record_count"],
                    },
                },
            )

        if name == "knowledge_session_build_start":
            session_id = str(arguments.get("session_id") or "")
            operation = session_service.start_build(
                session_id=session_id,
                mode=str(arguments.get("mode") or "full"),
            )
            operation_id = operation["operation_id"]
            if bool(arguments.get("sync", False) or arguments.get("wait", False)):
                session_service.run_build(session_id, operation_id)
                operation = session_service.get_operation(session_id, operation_id) or operation
            else:
                threading.Thread(target=session_service.run_build, args=(session_id, operation_id), daemon=True).start()
            return _session_operation_envelope(envelope, workspace_id, session_id, operation_id, operation)

        if name == "knowledge_session_build_status":
            session_id = str(arguments.get("session_id") or "")
            operation_id = str(arguments.get("operation_id") or "")
            operation = session_service.get_operation(session_id, operation_id)
            if not operation:
                return blocked(
                    workspace_id=workspace_id,
                    operation_id=operation_id,
                    message=f"Unknown operation_id: {operation_id}",
                    next_actions=["knowledge_session_build_start"],
                )
            return _session_operation_envelope(envelope, workspace_id, session_id, operation_id, operation)

        if name == "knowledge_session_build_cancel":
            session_id = str(arguments.get("session_id") or "")
            operation_id = str(arguments.get("operation_id") or "")
            operation = session_service.cancel_operation(
                session_id,
                operation_id,
                reason=str(arguments.get("reason") or ""),
            )
            return _session_operation_envelope(envelope, workspace_id, session_id, operation_id, operation)

        if name == "knowledge_graph_snapshot":
            scope = str(arguments.get("scope") or "workspace")
            max_nodes = bounded_int(arguments.get("max_nodes"), default=200, minimum=1, maximum=1000, field="max_nodes")
            if scope == "session":
                payload = session_service.graph_snapshot(
                    scope="session",
                    session_id=arguments.get("session_id"),
                    max_nodes=max_nodes,
                    include_communities=bool(arguments.get("include_communities", True)),
                    include_source_refs=bool(arguments.get("include_source_refs", True)),
                    node_types=list(arguments.get("node_types") or []),
                )
                return envelope(workspace_id=workspace_id, status=payload.get("status", "ok"), data=payload)
            snapshot = service.get_graph_snapshot(max_nodes=max_nodes)
            return envelope(workspace_id=workspace_id, data={**snapshot, "scope": "workspace"})

        if name == "knowledge_graph_neighbors":
            session_id = str(arguments.get("session_id") or "")
            payload = session_service.graph_neighbors(
                session_id=session_id,
                node_id=str(arguments.get("node_id") or ""),
                depth=bounded_int(arguments.get("depth"), default=1, minimum=1, maximum=3, field="depth"),
                max_nodes=bounded_int(arguments.get("max_nodes"), default=80, minimum=1, maximum=500, field="max_nodes"),
            )
            return envelope(workspace_id=workspace_id, status=payload.get("status", "ok"), data=payload)

        if name == "knowledge_community_summary":
            session_id = str(arguments.get("session_id") or "")
            payload = session_service.community_summary(
                session_id=session_id,
                community_id=arguments.get("community_id"),
                limit=bounded_int(arguments.get("limit"), default=20, minimum=1, maximum=200, field="limit"),
            )
            return envelope(workspace_id=workspace_id, status=payload.get("status", "ok"), data=payload)

        if name == "knowledge_session_query":
            session_id = str(arguments.get("session_id") or "")
            include_workspace_context = bool(arguments.get("include_workspace_context", False))
            workspace_context = None
            if include_workspace_context:
                workspace_result = service.query(
                    str(arguments.get("query") or ""),
                    mode=QueryMode.HYBRID,
                    top_k=bounded_int(arguments.get("top_k"), default=8, minimum=1, maximum=50, field="top_k"),
                )
                workspace_context = {
                    "answer": workspace_result.answer,
                    "hits": [
                        {
                            "title": hit.title,
                            "snippet": hit.snippet,
                            "source": hit.source,
                            "score": hit.score,
                            "meta": hit.meta,
                        }
                        for hit in workspace_result.hits
                    ],
                }
            payload = session_service.query_session(
                session_id=session_id,
                query=str(arguments.get("query") or ""),
                top_k=bounded_int(arguments.get("top_k"), default=8, minimum=1, maximum=50, field="top_k"),
                include_workspace_context=include_workspace_context,
                workspace_context=workspace_context,
            )
            return envelope(workspace_id=workspace_id, status=payload.get("status", "ok"), data=payload)

        if name == "knowledge_actor_summary":
            session_id = str(arguments.get("session_id") or "")
            payload = session_service.actor_summary(
                session_id=session_id,
                actor_id=str(arguments.get("actor_id") or ""),
                include_units=bool(arguments.get("include_units", True)),
                unit_types=list(arguments.get("unit_types") or []),
            )
            return envelope(workspace_id=workspace_id, status=payload.get("status", "ok"), data=payload)
    except ValueError as exc:
        return blocked_from_error(exc, session_id=arguments.get("session_id"))

    raise ValueError(f"Unknown session tool: {name}")


def _session_operation_payload(operation: dict[str, Any]) -> dict[str, Any]:
    return {
        "mode": operation.get("mode"),
        "stage": operation.get("stage"),
        "progress": operation.get("progress", 0.0),
        "error": operation.get("error"),
        "retryable": operation.get("retryable", True),
        "artifacts": operation.get("artifacts", []),
        "results": operation.get("results", {}),
    }


def _session_operation_envelope(
    envelope: Callable[..., dict[str, Any]],
    workspace_id: str,
    session_id: str,
    operation_id: str,
    operation: dict[str, Any],
    *,
    warnings: list[str] | None = None,
) -> dict[str, Any]:
    status = operation.get("status", "queued")
    next_actions = ["knowledge_session_build_status"]
    if status not in SESSION_TERMINAL_STATUSES:
        next_actions.append("knowledge_session_build_cancel")
    return envelope(
        workspace_id=workspace_id,
        operation_id=operation_id,
        status=status,
        warnings=warnings,
        artifact_refs=operation.get("artifacts", []),
        next_actions=next_actions,
        data={"session_id": session_id, **_session_operation_payload(operation)},
    )

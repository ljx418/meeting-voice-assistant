"""MCP tools for V2.1 Code Graph assets."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Callable

from .code_assets.envelope import v2_error_envelope, v2_success_envelope
from .code_assets.graph.persistence import graph_artifact_refs
from .code_assets.graph.service import CodeGraphService, public_graph_payload, public_neighbors_payload


GRAPH_TOOL_NAMES = {
    "knowledge_code_graph_build",
    "knowledge_code_graph_snapshot",
    "knowledge_code_graph_neighbors",
    "knowledge_code_graph_mermaid",
}


GRAPH_TOOL_SPECS = [
    {
        "name": "knowledge_code_graph_build",
        "description": "Build a deterministic V2.1 Code Graph from accepted V2.0 and DevWiki artifacts",
        "inputSchema": {"type": "object", "properties": {"workspace_id": {"type": "string"}, "codebase_id": {"type": "string"}, "snapshot_id": {"type": "string"}}, "required": ["workspace_id", "codebase_id"]},
    },
    {
        "name": "knowledge_code_graph_snapshot",
        "description": "Read a persisted V2.1 Code Graph snapshot",
        "inputSchema": {"type": "object", "properties": {"workspace_id": {"type": "string"}, "codebase_id": {"type": "string"}}, "required": ["workspace_id", "codebase_id"]},
    },
    {
        "name": "knowledge_code_graph_neighbors",
        "description": "Read neighbors for one V2.1 Code Graph node",
        "inputSchema": {"type": "object", "properties": {"workspace_id": {"type": "string"}, "codebase_id": {"type": "string"}, "node_id": {"type": "string"}, "depth": {"type": "integer"}, "limit": {"type": "integer"}}, "required": ["workspace_id", "codebase_id", "node_id"]},
    },
    {
        "name": "knowledge_code_graph_mermaid",
        "description": "Read Mermaid export for a V2.1 Code Graph",
        "inputSchema": {"type": "object", "properties": {"workspace_id": {"type": "string"}, "codebase_id": {"type": "string"}}, "required": ["workspace_id", "codebase_id"]},
    },
]


def handle_graph_tool(name: str, arguments: dict[str, Any], *, blocked: Callable[..., dict[str, Any]], envelope: Callable[..., dict[str, Any]], ensure_workspace_meta: Callable[..., dict[str, Any]], resolve_workspace: Callable[[str | None, str | None], Path]) -> dict[str, Any]:
    if name not in GRAPH_TOOL_NAMES:
        raise ValueError(f"Unknown graph tool: {name}")
    workspace_path = resolve_workspace(arguments.get("workspace_id"), None)
    meta = ensure_workspace_meta(workspace_path)
    workspace_id = str(meta["workspace_id"])
    codebase_id = str(arguments.get("codebase_id") or "").strip()
    if not codebase_id:
        return blocked(workspace_id=workspace_id, message="codebase_id is required", next_actions=["knowledge_codebase_list"], code="invalid_codebase_id")
    service = CodeGraphService(workspace_path, workspace_id=workspace_id)
    snapshot_id = str(arguments.get("snapshot_id") or "").strip() or None
    try:
        if name == "knowledge_code_graph_build":
            graph = service.build_graph(codebase_id, snapshot_id=snapshot_id)
            refs = graph.get("artifact_refs", graph_artifact_refs(codebase_id))
            data = {"graph": {"summary": graph["summary"]}}
            return envelope(workspace_id=workspace_id, artifact_refs=refs, next_actions=["knowledge_code_graph_snapshot"], data=_with_v2(workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=str(graph["snapshot_id"]), data=data, artifact_refs=refs, next_actions=["knowledge_code_graph_snapshot"]))
        if name == "knowledge_code_graph_snapshot":
            graph = service.read_graph(codebase_id)
            refs = graph.get("artifact_refs", graph_artifact_refs(codebase_id))
            data = {"graph": public_graph_payload(graph)}
            return envelope(workspace_id=workspace_id, artifact_refs=refs, data=_with_v2(workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=str(graph["snapshot_id"]), data=data, artifact_refs=refs))
        if name == "knowledge_code_graph_mermaid":
            payload = service.read_mermaid(codebase_id)
            data = {"mermaid": payload}
            return envelope(workspace_id=workspace_id, artifact_refs=graph_artifact_refs(codebase_id), data=_with_v2(workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=str(payload["snapshot_id"]), data=data, artifact_refs=graph_artifact_refs(codebase_id)))
        payload = service.read_neighbors(codebase_id, str(arguments.get("node_id") or ""), depth=int(arguments.get("depth") or 1), limit=int(arguments.get("limit") or 100))
        data = {"neighbors": public_neighbors_payload(payload)}
        return envelope(workspace_id=workspace_id, data=_with_v2(workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=str(payload["snapshot_id"]), data=data, unresolved=payload.get("unresolved", [])))
    except FileNotFoundError as exc:
        return _blocked_v2(envelope, workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=snapshot_id, code=_graph_error_code(str(exc)), message=_graph_error_message(str(exc)), next_actions=["knowledge_devwiki_build", "knowledge_code_graph_build"])
    except ValueError as exc:
        return _blocked_v2(envelope, workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=snapshot_id, code=str(exc), message=str(exc), next_actions=["knowledge_code_graph_build"])


def _with_v2(*, workspace_id: str, data: dict[str, Any], codebase_id: str, snapshot_id: str | None, artifact_refs: list[dict[str, Any]] | None = None, unresolved: list[Any] | None = None, next_actions: list[str] | None = None) -> dict[str, Any]:
    payload = dict(data)
    payload["v2"] = v2_success_envelope(workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=snapshot_id, data=data, artifact_refs=artifact_refs, unresolved=unresolved, next_actions=next_actions)
    return payload


def _blocked_v2(envelope: Callable[..., dict[str, Any]], *, workspace_id: str, codebase_id: str, snapshot_id: str | None, code: str, message: str, next_actions: list[str] | None = None) -> dict[str, Any]:
    return envelope(workspace_id=workspace_id, status="blocked", warnings=[message], next_actions=next_actions, data={"error": {"code": code, "message": message, "retryable": False}, "v2": v2_error_envelope(workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=snapshot_id, code=code, message=message, next_actions=next_actions)})


def _graph_error_code(error: str) -> str:
    if "SNAPSHOT_NOT_FOUND" in error:
        return "SNAPSHOT_NOT_FOUND"
    if "V20_ARTIFACT_MISSING" in error:
        return "V20_ARTIFACT_MISSING"
    if "DEVWIKI" in error:
        return "DEVWIKI_NOT_FOUND"
    if "GRAPH_NODE_NOT_FOUND" in error:
        return "GRAPH_NODE_NOT_FOUND"
    if "CODE_GRAPH_NOT_FOUND" in error:
        return "CODE_GRAPH_NOT_FOUND"
    return "CODE_GRAPH_ERROR"


def _graph_error_message(error: str) -> str:
    if "V20_ARTIFACT_MISSING" in error:
        return "Required V2.0 artifact is missing; build V2.0 artifacts before Code Graph"
    if "DEVWIKI" in error:
        return "DevWiki artifacts are missing or stale; build DevWiki before Code Graph"
    if "GRAPH_NODE_NOT_FOUND" in error:
        return "Graph node not found"
    if "CODE_GRAPH_NOT_FOUND" in error:
        return "Code Graph has not been built"
    return error or "Code Graph request failed"

"""HTTP routes for V2.1 Code Graph code assets."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Optional

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from data_service.code_assets.envelope import v2_error_envelope, v2_success_envelope
from data_service.code_assets.graph.persistence import graph_artifact_refs
from data_service.code_assets.graph.service import CodeGraphService, public_graph_payload, public_neighbors_payload
from data_service.mcp_common import bounded_int, envelope
from data_service.mcp_workspace_runtime import WorkspaceRuntime

from .data_service import verify_knowledge_access


router = APIRouter(prefix="/workspaces", tags=["Project Intelligence Code Graph"], dependencies=[Depends(verify_knowledge_access)])


class GraphBuildRequest(BaseModel):
    snapshot_id: Optional[str] = Field(default=None)


def _runtime() -> WorkspaceRuntime:
    return WorkspaceRuntime(Path.cwd() / "workspace")


def _workspace_for(workspace_id: str) -> tuple[Path, dict[str, Any]]:
    runtime = _runtime()
    workspace = runtime.resolve_workspace(workspace_id, None)
    meta = runtime.ensure_workspace_meta(workspace)
    return workspace, meta


def _with_v2(*, workspace_id: str, data: dict[str, Any], codebase_id: str, snapshot_id: str | None, artifact_refs: list[dict[str, Any]] | None = None, unresolved: list[Any] | None = None, next_actions: list[str] | None = None) -> dict[str, Any]:
    payload = dict(data)
    payload["v2"] = v2_success_envelope(workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=snapshot_id, data=data, artifact_refs=artifact_refs, unresolved=unresolved, next_actions=next_actions)
    return payload


def _error(*, status_code: int, workspace_id: str, codebase_id: str, snapshot_id: str | None, error: str, next_actions: list[str] | None = None) -> JSONResponse:
    code = _graph_error_code(error)
    message = _graph_error_message(error)
    return JSONResponse(
        status_code=status_code,
        content={
            "detail": message,
            "v2": v2_error_envelope(workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=snapshot_id, code=code, message=message, next_actions=next_actions),
        },
    )


@router.post("/{workspace_id}/codebases/{codebase_id}/graph/build")
async def build_codebase_graph(workspace_id: str, codebase_id: str, request: GraphBuildRequest):
    workspace, meta = _workspace_for(workspace_id)
    service = CodeGraphService(workspace, workspace_id=str(meta["workspace_id"]))
    try:
        graph = service.build_graph(codebase_id, snapshot_id=request.snapshot_id)
    except FileNotFoundError as exc:
        return _error(status_code=404, workspace_id=str(meta["workspace_id"]), codebase_id=codebase_id, snapshot_id=request.snapshot_id, error=str(exc), next_actions=["knowledge_devwiki_build", "knowledge_code_graph_build"])
    refs = graph.get("artifact_refs", graph_artifact_refs(codebase_id))
    data = {"graph": {"summary": graph["summary"]}}
    return envelope(
        workspace_id=str(meta["workspace_id"]),
        artifact_refs=refs,
        next_actions=["knowledge_code_graph_snapshot", "knowledge_code_graph_neighbors"],
        data=_with_v2(workspace_id=str(meta["workspace_id"]), codebase_id=codebase_id, snapshot_id=str(graph["snapshot_id"]), data=data, artifact_refs=refs, next_actions=["knowledge_code_graph_snapshot", "knowledge_code_graph_neighbors"]),
    )


@router.get("/{workspace_id}/codebases/{codebase_id}/graph")
async def read_codebase_graph(workspace_id: str, codebase_id: str):
    workspace, meta = _workspace_for(workspace_id)
    service = CodeGraphService(workspace, workspace_id=str(meta["workspace_id"]))
    try:
        graph = service.read_graph(codebase_id)
    except FileNotFoundError as exc:
        return _error(status_code=404, workspace_id=str(meta["workspace_id"]), codebase_id=codebase_id, snapshot_id=None, error=str(exc), next_actions=["knowledge_code_graph_build"])
    refs = graph.get("artifact_refs", graph_artifact_refs(codebase_id))
    data = {"graph": public_graph_payload(graph)}
    return envelope(workspace_id=str(meta["workspace_id"]), artifact_refs=refs, data=_with_v2(workspace_id=str(meta["workspace_id"]), codebase_id=codebase_id, snapshot_id=str(graph["snapshot_id"]), data=data, artifact_refs=refs))


@router.get("/{workspace_id}/codebases/{codebase_id}/graph/neighbors")
async def read_codebase_graph_neighbors(workspace_id: str, codebase_id: str, node_id: str, depth: int = 1, limit: int = 100):
    workspace, meta = _workspace_for(workspace_id)
    service = CodeGraphService(workspace, workspace_id=str(meta["workspace_id"]))
    try:
        payload = service.read_neighbors(codebase_id, node_id, depth=bounded_int(depth, default=1, minimum=1, maximum=3, field="depth"), limit=bounded_int(limit, default=100, minimum=1, maximum=500, field="limit"))
    except FileNotFoundError as exc:
        return _error(status_code=404, workspace_id=str(meta["workspace_id"]), codebase_id=codebase_id, snapshot_id=None, error=str(exc), next_actions=["knowledge_code_graph_snapshot"])
    data = {"neighbors": public_neighbors_payload(payload)}
    return envelope(workspace_id=str(meta["workspace_id"]), data=_with_v2(workspace_id=str(meta["workspace_id"]), codebase_id=codebase_id, snapshot_id=str(payload["snapshot_id"]), data=data, unresolved=payload.get("unresolved", [])))


@router.get("/{workspace_id}/codebases/{codebase_id}/graph/mermaid")
async def read_codebase_graph_mermaid(workspace_id: str, codebase_id: str):
    workspace, meta = _workspace_for(workspace_id)
    service = CodeGraphService(workspace, workspace_id=str(meta["workspace_id"]))
    try:
        payload = service.read_mermaid(codebase_id)
    except FileNotFoundError as exc:
        return _error(status_code=404, workspace_id=str(meta["workspace_id"]), codebase_id=codebase_id, snapshot_id=None, error=str(exc), next_actions=["knowledge_code_graph_build"])
    data = {"mermaid": payload}
    return envelope(workspace_id=str(meta["workspace_id"]), artifact_refs=graph_artifact_refs(codebase_id), data=_with_v2(workspace_id=str(meta["workspace_id"]), codebase_id=codebase_id, snapshot_id=str(payload["snapshot_id"]), data=data, artifact_refs=graph_artifact_refs(codebase_id)))


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
    code = _graph_error_code(error)
    if code == "V20_ARTIFACT_MISSING":
        return "Required V2.0 artifact is missing; build V2.0 artifacts before Code Graph"
    if code == "DEVWIKI_NOT_FOUND":
        return "DevWiki artifacts are missing or stale; build DevWiki before Code Graph"
    if code == "GRAPH_NODE_NOT_FOUND":
        return "Graph node not found"
    if code == "CODE_GRAPH_NOT_FOUND":
        return "Code Graph has not been built"
    return error or "Code Graph request failed"

"""Target HTTP routes for V2 codebase assets."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from data_service.code_assets.envelope import v2_error_envelope, v2_success_envelope
from data_service.code_assets.context.persistence import context_artifact_refs
from data_service.code_assets.context.service import CodebaseAgentContextService, public_context_pack_payload
from data_service.code_assets.registry import CodebaseRegistry
from data_service.code_assets.inventory import CodebaseInventoryService, inventory_artifact_refs, public_inventory_payload
from data_service.code_assets.overview import CodebaseOverviewService, overview_artifact_refs, public_overview_payload
from data_service.code_assets.snapshot import CodebaseSnapshotService, public_snapshot
from data_service.code_assets.symbols import (
    CodebaseSymbolIndexService,
    public_import_payload,
    public_symbol_index_payload,
    public_symbol_payload,
    symbol_artifact_refs,
)
from data_service.code_assets.trace import (
    CodebaseTraceService,
    public_evidence_payload,
    public_trace_payload,
    public_trace_selection_payload,
    trace_artifact_refs,
)
from data_service.mcp_common import bounded_int, envelope
from data_service.mcp_workspace_runtime import WorkspaceRuntime

from .data_service import verify_knowledge_access


router = APIRouter(prefix="/workspaces", tags=["Project Intelligence"], dependencies=[Depends(verify_knowledge_access)])


class CodebaseImportRequest(BaseModel):
    path: str = Field(..., description="Local codebase root path")
    codebase_id: Optional[str] = Field(default=None, description="Optional stable codebase identifier")
    name: Optional[str] = Field(default=None, description="Optional display name")
    metadata: dict[str, Any] = Field(default_factory=dict)
    scan_policy: dict[str, Any] = Field(default_factory=dict)


class CodebaseArchiveRequest(BaseModel):
    reason: str = ""


class CodebaseSnapshotRequest(BaseModel):
    scan_policy: dict[str, Any] = Field(default_factory=dict)
    include_git: bool = True


class CodebaseInventoryRequest(BaseModel):
    snapshot_id: Optional[str] = Field(default=None, description="Optional snapshot identifier; defaults to latest")


class CodebaseSymbolBuildRequest(BaseModel):
    snapshot_id: Optional[str] = Field(default=None, description="Optional snapshot identifier; defaults to latest")


class CodebaseTraceBuildRequest(BaseModel):
    snapshot_id: Optional[str] = Field(default=None, description="Optional snapshot identifier; defaults to latest")


class CodebaseContextPackRequest(BaseModel):
    snapshot_id: Optional[str] = Field(default=None, description="Optional snapshot identifier; defaults to latest")
    mode: Optional[str] = Field(default=None, description="project_brief or task_context")
    task: Optional[str] = Field(default=None, description="Task text for task_context")
    format: str = Field(default="json", description="json or markdown")
    max_tokens: int = Field(default=16000, ge=256, le=200000)
    focus: dict[str, Any] = Field(default_factory=dict)
    include: list[str] = Field(default_factory=list)


def _runtime() -> WorkspaceRuntime:
    return WorkspaceRuntime(Path.cwd() / "workspace")


def _registry_for(workspace_id: str) -> tuple[WorkspaceRuntime, Path, dict[str, Any], CodebaseRegistry]:
    runtime = _runtime()
    workspace = runtime.resolve_workspace(workspace_id, None)
    meta = runtime.ensure_workspace_meta(workspace)
    registry = CodebaseRegistry(workspace, workspace_id=str(meta["workspace_id"]))
    return runtime, workspace, meta, registry


def _blocked(*, workspace_id: str, message: str, code: str, next_actions: list[str] | None = None) -> dict[str, Any]:
    v2 = v2_error_envelope(
        workspace_id=workspace_id,
        codebase_id=None,
        snapshot_id=None,
        code=code,
        message=message,
        next_actions=next_actions,
    )
    return envelope(
        workspace_id=workspace_id,
        status="blocked",
        warnings=[message],
        next_actions=next_actions,
        data={"error": {"code": code, "message": message, "retryable": False}, "v2": v2},
    )


def _blocked_from_error(*, workspace_id: str, error: str) -> dict[str, Any]:
    code = _error_code(error)
    return _blocked(
        workspace_id=workspace_id,
        message=_error_message(code, error),
        code=code,
        next_actions=["knowledge_codebase_import"],
    )


def _with_v2(
    *,
    workspace_id: str,
    data: dict[str, Any],
    codebase_id: str | None = None,
    snapshot_id: str | None = None,
    artifact_refs: list[dict[str, Any]] | None = None,
    warnings: list[Any] | None = None,
    unresolved: list[Any] | None = None,
    next_actions: list[str] | None = None,
) -> dict[str, Any]:
    payload = dict(data)
    payload["v2"] = v2_success_envelope(
        workspace_id=workspace_id,
        codebase_id=codebase_id,
        snapshot_id=snapshot_id,
        data=data,
        artifact_refs=artifact_refs,
        warnings=warnings,
        unresolved=unresolved,
        next_actions=next_actions,
    )
    return payload


def _http_v2_error(
    *,
    status_code: int,
    workspace_id: str,
    message: str,
    code: str,
    codebase_id: str | None = None,
    snapshot_id: str | None = None,
    next_actions: list[str] | None = None,
) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={
            "detail": message,
            "v2": v2_error_envelope(
                workspace_id=workspace_id,
                codebase_id=codebase_id,
                snapshot_id=snapshot_id,
                code=code,
                message=message,
                next_actions=next_actions,
            ),
        },
    )


@router.post("/{workspace_id}/codebases")
async def import_codebase(workspace_id: str, request: CodebaseImportRequest) -> dict[str, Any]:
    _runtime_obj, _workspace, meta, registry = _registry_for(workspace_id)
    if meta.get("status") == "archived":
        return _blocked(
            workspace_id=str(meta["workspace_id"]),
            message="Workspace is archived and cannot import codebases",
            code="workspace_archived",
            next_actions=["knowledge_workspace_describe"],
        )
    try:
        result = registry.import_codebase(
            path=request.path,
            codebase_id=request.codebase_id,
            name=request.name,
            metadata=request.metadata,
            scan_policy=request.scan_policy,
        )
    except ValueError as exc:
        return _blocked_from_error(workspace_id=str(meta["workspace_id"]), error=str(exc))

    asset = result["asset"]
    refs = [{"type": "codebase", "codebase_id": asset.codebase_id, "artifact_ref": f"codebase://{asset.codebase_id}"}]
    next_actions = ["knowledge_codebase_snapshot", "knowledge_project_inventory"]
    data = {"codebase": asset.public_dict(), "created": bool(result["created"])}
    return envelope(
        workspace_id=str(meta["workspace_id"]),
        artifact_refs=refs,
        next_actions=next_actions,
        data=_with_v2(
            workspace_id=str(meta["workspace_id"]),
            codebase_id=asset.codebase_id,
            data=data,
            artifact_refs=refs,
            next_actions=next_actions,
        ),
    )


@router.get("/{workspace_id}/codebases")
async def list_codebases(workspace_id: str, include_archived: bool = False, limit: int = 100) -> dict[str, Any]:
    _runtime_obj, _workspace, meta, registry = _registry_for(workspace_id)
    bounded_limit = bounded_int(limit, default=100, minimum=1, maximum=500, field="limit")
    items = [asset.public_dict() for asset in registry.list_codebases(include_archived=include_archived, limit=bounded_limit)]
    data = {"items": items, "count": len(items)}
    return envelope(
        workspace_id=str(meta["workspace_id"]),
        data=_with_v2(workspace_id=str(meta["workspace_id"]), data=data),
    )


@router.get("/{workspace_id}/codebases/{codebase_id}")
async def describe_codebase(workspace_id: str, codebase_id: str) -> dict[str, Any]:
    _runtime_obj, _workspace, meta, registry = _registry_for(workspace_id)
    try:
        asset = registry.describe(codebase_id)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=f"Unknown codebase_id: {codebase_id}") from exc
    except ValueError as exc:
        return _blocked_from_error(workspace_id=str(meta["workspace_id"]), error=str(exc))
    data = {"codebase": asset.public_dict()}
    return envelope(
        workspace_id=str(meta["workspace_id"]),
        data=_with_v2(workspace_id=str(meta["workspace_id"]), codebase_id=asset.codebase_id, data=data),
    )


@router.post("/{workspace_id}/codebases/{codebase_id}/archive")
async def archive_codebase(workspace_id: str, codebase_id: str, request: CodebaseArchiveRequest) -> dict[str, Any]:
    _runtime_obj, _workspace, meta, registry = _registry_for(workspace_id)
    if meta.get("status") == "archived":
        return _blocked(
            workspace_id=str(meta["workspace_id"]),
            message="Workspace is archived and cannot archive codebases",
            code="workspace_archived",
            next_actions=["knowledge_workspace_describe"],
        )
    try:
        asset = registry.archive(codebase_id, reason=request.reason)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=f"Unknown codebase_id: {codebase_id}") from exc
    except ValueError as exc:
        return _blocked_from_error(workspace_id=str(meta["workspace_id"]), error=str(exc))
    data = {"codebase": asset.public_dict()}
    return envelope(
        workspace_id=str(meta["workspace_id"]),
        data=_with_v2(workspace_id=str(meta["workspace_id"]), codebase_id=asset.codebase_id, data=data),
    )


@router.post("/{workspace_id}/codebases/{codebase_id}/snapshots")
async def create_codebase_snapshot(workspace_id: str, codebase_id: str, request: CodebaseSnapshotRequest) -> dict[str, Any]:
    _runtime_obj, workspace, meta, _registry = _registry_for(workspace_id)
    if meta.get("status") == "archived":
        return _blocked(
            workspace_id=str(meta["workspace_id"]),
            message="Workspace is archived and cannot create codebase snapshots",
            code="workspace_archived",
            next_actions=["knowledge_workspace_describe"],
        )
    service = CodebaseSnapshotService(workspace, workspace_id=str(meta["workspace_id"]))
    try:
        result = service.create_snapshot(codebase_id, scan_policy=request.scan_policy, include_git=request.include_git)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=f"Unknown codebase_id: {codebase_id}") from exc
    except ValueError as exc:
        return _blocked(
            workspace_id=str(meta["workspace_id"]),
            message=_snapshot_error_message(str(exc)),
            code=str(exc),
            next_actions=["knowledge_codebase_describe"],
        )
    snapshot = public_snapshot(result["snapshot"])
    next_actions = ["knowledge_project_inventory", "knowledge_code_symbol_search"]
    data = {"snapshot": snapshot}
    return envelope(
        workspace_id=str(meta["workspace_id"]),
        artifact_refs=snapshot["artifact_refs"],
        next_actions=next_actions,
        data=_with_v2(
            workspace_id=str(meta["workspace_id"]),
            codebase_id=codebase_id,
            snapshot_id=str(snapshot["snapshot_id"]),
            data=data,
            artifact_refs=snapshot["artifact_refs"],
            next_actions=next_actions,
        ),
    )


@router.get("/{workspace_id}/codebases/{codebase_id}/snapshots")
async def list_codebase_snapshots(workspace_id: str, codebase_id: str, limit: int = 100) -> dict[str, Any]:
    _runtime_obj, workspace, meta, _registry = _registry_for(workspace_id)
    service = CodebaseSnapshotService(workspace, workspace_id=str(meta["workspace_id"]))
    bounded_limit = bounded_int(limit, default=100, minimum=1, maximum=500, field="limit")
    try:
        items = service.list_snapshots(codebase_id, limit=bounded_limit)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=f"Unknown codebase_id: {codebase_id}") from exc
    data = {"items": items, "count": len(items)}
    return envelope(
        workspace_id=str(meta["workspace_id"]),
        data=_with_v2(workspace_id=str(meta["workspace_id"]), codebase_id=codebase_id, data=data),
    )


@router.get("/{workspace_id}/codebases/{codebase_id}/snapshots/{snapshot_id}")
async def describe_codebase_snapshot(workspace_id: str, codebase_id: str, snapshot_id: str) -> dict[str, Any]:
    _runtime_obj, workspace, meta, _registry = _registry_for(workspace_id)
    service = CodebaseSnapshotService(workspace, workspace_id=str(meta["workspace_id"]))
    try:
        snapshot = public_snapshot(service.read_snapshot(codebase_id, snapshot_id))
    except FileNotFoundError as exc:
        if str(exc) == codebase_id:
            raise HTTPException(status_code=404, detail=f"Unknown codebase_id: {codebase_id}") from exc
        raise HTTPException(status_code=404, detail=f"Unknown snapshot_id: {snapshot_id}") from exc
    data = {"snapshot": snapshot}
    return envelope(
        workspace_id=str(meta["workspace_id"]),
        artifact_refs=snapshot["artifact_refs"],
        data=_with_v2(
            workspace_id=str(meta["workspace_id"]),
            codebase_id=codebase_id,
            snapshot_id=str(snapshot["snapshot_id"]),
            data=data,
            artifact_refs=snapshot["artifact_refs"],
        ),
    )


@router.post("/{workspace_id}/codebases/{codebase_id}/inventory")
async def build_codebase_inventory(workspace_id: str, codebase_id: str, request: CodebaseInventoryRequest) -> dict[str, Any]:
    _runtime_obj, workspace, meta, _registry = _registry_for(workspace_id)
    if meta.get("status") == "archived":
        return _blocked(
            workspace_id=str(meta["workspace_id"]),
            message="Workspace is archived and cannot build codebase inventory",
            code="workspace_archived",
            next_actions=["knowledge_workspace_describe"],
        )
    service = CodebaseInventoryService(workspace, workspace_id=str(meta["workspace_id"]))
    try:
        result = service.build_inventory(codebase_id, snapshot_id=request.snapshot_id)
    except FileNotFoundError as exc:
        message = _inventory_not_found_detail(str(exc), codebase_id, request.snapshot_id)
        return _http_v2_error(
            status_code=404,
            workspace_id=str(meta["workspace_id"]),
            codebase_id=codebase_id,
            snapshot_id=request.snapshot_id,
            code=_inventory_error_code(str(exc)),
            message=message,
            next_actions=["knowledge_codebase_snapshot"],
        )
    except ValueError as exc:
        return _blocked(
            workspace_id=str(meta["workspace_id"]),
            message=_inventory_error_message(str(exc)),
            code=str(exc),
            next_actions=["knowledge_codebase_snapshot"],
        )
    payload = public_inventory_payload(result)
    refs = result["summary"].get("artifact_refs", inventory_artifact_refs(codebase_id, payload["snapshot_id"]))
    next_actions = ["knowledge_code_symbol_search", "knowledge_public_surface_trace"]
    data = {"inventory": payload}
    return envelope(
        workspace_id=str(meta["workspace_id"]),
        artifact_refs=refs,
        next_actions=next_actions,
        data=_with_v2(
            workspace_id=str(meta["workspace_id"]),
            codebase_id=codebase_id,
            snapshot_id=str(payload["snapshot_id"]),
            data=data,
            artifact_refs=refs,
            next_actions=next_actions,
        ),
    )


@router.get("/{workspace_id}/codebases/{codebase_id}/inventory")
async def read_codebase_inventory(workspace_id: str, codebase_id: str, snapshot_id: Optional[str] = None) -> dict[str, Any]:
    _runtime_obj, workspace, meta, _registry = _registry_for(workspace_id)
    service = CodebaseInventoryService(workspace, workspace_id=str(meta["workspace_id"]))
    try:
        result = service.read_inventory(codebase_id, snapshot_id=snapshot_id)
    except FileNotFoundError as exc:
        message = _inventory_not_found_detail(str(exc), codebase_id, snapshot_id)
        return _http_v2_error(
            status_code=404,
            workspace_id=str(meta["workspace_id"]),
            codebase_id=codebase_id,
            snapshot_id=snapshot_id,
            code=_inventory_error_code(str(exc)),
            message=message,
            next_actions=["knowledge_codebase_snapshot", "knowledge_project_inventory"],
        )
    payload = public_inventory_payload(result)
    refs = result["summary"].get("artifact_refs", inventory_artifact_refs(codebase_id, payload["snapshot_id"]))
    data = {"inventory": payload}
    return envelope(
        workspace_id=str(meta["workspace_id"]),
        artifact_refs=refs,
        data=_with_v2(
            workspace_id=str(meta["workspace_id"]),
            codebase_id=codebase_id,
            snapshot_id=str(payload["snapshot_id"]),
            data=data,
            artifact_refs=refs,
        ),
    )


@router.get("/{workspace_id}/codebases/{codebase_id}/surfaces")
async def read_codebase_surfaces(
    workspace_id: str,
    codebase_id: str,
    snapshot_id: Optional[str] = None,
    surface_type: Optional[str] = None,
) -> dict[str, Any]:
    _runtime_obj, workspace, meta, _registry = _registry_for(workspace_id)
    service = CodebaseInventoryService(workspace, workspace_id=str(meta["workspace_id"]))
    try:
        surfaces = service.read_surfaces(codebase_id, snapshot_id=snapshot_id, surface_type=surface_type)
        resolved_snapshot_id = snapshot_id or service._latest_snapshot_id(codebase_id)
    except FileNotFoundError as exc:
        message = _inventory_not_found_detail(str(exc), codebase_id, snapshot_id)
        return _http_v2_error(
            status_code=404,
            workspace_id=str(meta["workspace_id"]),
            codebase_id=codebase_id,
            snapshot_id=snapshot_id,
            code=_inventory_error_code(str(exc)),
            message=message,
            next_actions=["knowledge_project_inventory"],
        )
    except ValueError as exc:
        return _blocked(
            workspace_id=str(meta["workspace_id"]),
            message=_inventory_error_message(str(exc)),
            code=str(exc),
            next_actions=["knowledge_project_inventory"],
        )
    refs = inventory_artifact_refs(codebase_id, resolved_snapshot_id)
    data = {"snapshot_id": resolved_snapshot_id, "items": surfaces, "count": len(surfaces)}
    return envelope(
        workspace_id=str(meta["workspace_id"]),
        artifact_refs=refs,
        data=_with_v2(
            workspace_id=str(meta["workspace_id"]),
            codebase_id=codebase_id,
            snapshot_id=str(resolved_snapshot_id),
            data=data,
            artifact_refs=refs,
        ),
    )


@router.get("/{workspace_id}/codebases/{codebase_id}/capabilities")
async def read_codebase_capabilities(workspace_id: str, codebase_id: str, snapshot_id: Optional[str] = None) -> dict[str, Any]:
    _runtime_obj, workspace, meta, _registry = _registry_for(workspace_id)
    service = CodebaseInventoryService(workspace, workspace_id=str(meta["workspace_id"]))
    try:
        capabilities = service.read_capabilities(codebase_id, snapshot_id=snapshot_id)
        resolved_snapshot_id = snapshot_id or service._latest_snapshot_id(codebase_id)
    except FileNotFoundError as exc:
        message = _inventory_not_found_detail(str(exc), codebase_id, snapshot_id)
        return _http_v2_error(
            status_code=404,
            workspace_id=str(meta["workspace_id"]),
            codebase_id=codebase_id,
            snapshot_id=snapshot_id,
            code=_inventory_error_code(str(exc)),
            message=message,
            next_actions=["knowledge_project_inventory"],
        )
    refs = inventory_artifact_refs(codebase_id, resolved_snapshot_id)
    data = {"snapshot_id": resolved_snapshot_id, "items": capabilities, "count": len(capabilities)}
    return envelope(
        workspace_id=str(meta["workspace_id"]),
        artifact_refs=refs,
        data=_with_v2(
            workspace_id=str(meta["workspace_id"]),
            codebase_id=codebase_id,
            snapshot_id=str(resolved_snapshot_id),
            data=data,
            artifact_refs=refs,
        ),
    )


@router.post("/{workspace_id}/codebases/{codebase_id}/symbols")
async def build_codebase_symbols(workspace_id: str, codebase_id: str, request: CodebaseSymbolBuildRequest) -> dict[str, Any]:
    _runtime_obj, workspace, meta, _registry = _registry_for(workspace_id)
    if meta.get("status") == "archived":
        return _blocked(
            workspace_id=str(meta["workspace_id"]),
            message="Workspace is archived and cannot build codebase symbols",
            code="workspace_archived",
            next_actions=["knowledge_workspace_describe"],
        )
    service = CodebaseSymbolIndexService(workspace, workspace_id=str(meta["workspace_id"]))
    try:
        result = service.build_symbol_index(codebase_id, snapshot_id=request.snapshot_id)
    except FileNotFoundError as exc:
        message = _symbol_not_found_detail(str(exc), codebase_id, request.snapshot_id)
        return _http_v2_error(
            status_code=404,
            workspace_id=str(meta["workspace_id"]),
            codebase_id=codebase_id,
            snapshot_id=request.snapshot_id,
            code=_symbol_error_code(str(exc)),
            message=message,
            next_actions=["knowledge_codebase_snapshot", "knowledge_code_symbol_search"],
        )
    except ValueError as exc:
        return _blocked(
            workspace_id=str(meta["workspace_id"]),
            message=_symbol_error_message(str(exc)),
            code=str(exc),
            next_actions=["knowledge_codebase_snapshot"],
        )
    payload = public_symbol_index_payload(result)
    refs = result["summary"].get("artifact_refs", symbol_artifact_refs(codebase_id, payload["snapshot_id"]))
    next_actions = ["knowledge_public_surface_trace", "knowledge_agent_context_pack"]
    data = {"symbol_index": payload}
    return envelope(
        workspace_id=str(meta["workspace_id"]),
        artifact_refs=refs,
        next_actions=next_actions,
        data=_with_v2(
            workspace_id=str(meta["workspace_id"]),
            codebase_id=codebase_id,
            snapshot_id=str(payload["snapshot_id"]),
            data=data,
            artifact_refs=refs,
            next_actions=next_actions,
        ),
    )


@router.get("/{workspace_id}/codebases/{codebase_id}/symbols")
async def read_codebase_symbols(
    workspace_id: str,
    codebase_id: str,
    snapshot_id: Optional[str] = None,
    kind: Optional[str] = None,
    query: Optional[str] = None,
    limit: int = 50,
) -> dict[str, Any]:
    _runtime_obj, workspace, meta, _registry = _registry_for(workspace_id)
    service = CodebaseSymbolIndexService(workspace, workspace_id=str(meta["workspace_id"]))
    bounded_limit = bounded_int(limit, default=50, minimum=1, maximum=200, field="limit")
    try:
        symbols = service.read_symbols(codebase_id, snapshot_id=snapshot_id, kind=kind, query=query, limit=bounded_limit)
        resolved_snapshot_id = snapshot_id or service._latest_snapshot_id(codebase_id)
    except FileNotFoundError as exc:
        message = _symbol_not_found_detail(str(exc), codebase_id, snapshot_id)
        return _http_v2_error(
            status_code=404,
            workspace_id=str(meta["workspace_id"]),
            codebase_id=codebase_id,
            snapshot_id=snapshot_id,
            code=_symbol_error_code(str(exc)),
            message=message,
            next_actions=["knowledge_code_symbol_search"],
        )
    refs = symbol_artifact_refs(codebase_id, resolved_snapshot_id)
    data = {"snapshot_id": resolved_snapshot_id, "items": [public_symbol_payload(item) for item in symbols], "count": len(symbols)}
    return envelope(
        workspace_id=str(meta["workspace_id"]),
        artifact_refs=refs,
        data=_with_v2(
            workspace_id=str(meta["workspace_id"]),
            codebase_id=codebase_id,
            snapshot_id=str(resolved_snapshot_id),
            data=data,
            artifact_refs=refs,
        ),
    )


@router.get("/{workspace_id}/codebases/{codebase_id}/imports")
async def read_codebase_imports(workspace_id: str, codebase_id: str, snapshot_id: Optional[str] = None) -> dict[str, Any]:
    _runtime_obj, workspace, meta, _registry = _registry_for(workspace_id)
    service = CodebaseSymbolIndexService(workspace, workspace_id=str(meta["workspace_id"]))
    try:
        imports = service.read_imports(codebase_id, snapshot_id=snapshot_id)
        resolved_snapshot_id = snapshot_id or service._latest_snapshot_id(codebase_id)
    except FileNotFoundError as exc:
        message = _symbol_not_found_detail(str(exc), codebase_id, snapshot_id)
        return _http_v2_error(
            status_code=404,
            workspace_id=str(meta["workspace_id"]),
            codebase_id=codebase_id,
            snapshot_id=snapshot_id,
            code=_symbol_error_code(str(exc)),
            message=message,
            next_actions=["knowledge_code_symbol_search"],
        )
    refs = symbol_artifact_refs(codebase_id, resolved_snapshot_id)
    data = {"snapshot_id": resolved_snapshot_id, "items": [public_import_payload(item) for item in imports], "count": len(imports)}
    return envelope(
        workspace_id=str(meta["workspace_id"]),
        artifact_refs=refs,
        data=_with_v2(
            workspace_id=str(meta["workspace_id"]),
            codebase_id=codebase_id,
            snapshot_id=str(resolved_snapshot_id),
            data=data,
            artifact_refs=refs,
        ),
    )


@router.get("/{workspace_id}/codebases/{codebase_id}/symbols/{symbol_id}")
async def describe_codebase_symbol(workspace_id: str, codebase_id: str, symbol_id: str, snapshot_id: Optional[str] = None) -> dict[str, Any]:
    _runtime_obj, workspace, meta, _registry = _registry_for(workspace_id)
    service = CodebaseSymbolIndexService(workspace, workspace_id=str(meta["workspace_id"]))
    try:
        symbol = service.read_symbol(codebase_id, symbol_id, snapshot_id=snapshot_id)
        resolved_snapshot_id = snapshot_id or service._latest_snapshot_id(codebase_id)
    except FileNotFoundError as exc:
        message = _symbol_not_found_detail(str(exc), codebase_id, snapshot_id)
        return _http_v2_error(
            status_code=404,
            workspace_id=str(meta["workspace_id"]),
            codebase_id=codebase_id,
            snapshot_id=snapshot_id,
            code=_symbol_error_code(str(exc)),
            message=message,
            next_actions=["knowledge_code_symbol_search"],
        )
    refs = symbol_artifact_refs(codebase_id, resolved_snapshot_id)
    data = {"snapshot_id": resolved_snapshot_id, "symbol": public_symbol_payload(symbol)}
    return envelope(
        workspace_id=str(meta["workspace_id"]),
        artifact_refs=refs,
        data=_with_v2(
            workspace_id=str(meta["workspace_id"]),
            codebase_id=codebase_id,
            snapshot_id=str(resolved_snapshot_id),
            data=data,
            artifact_refs=refs,
        ),
    )


@router.post("/{workspace_id}/codebases/{codebase_id}/trace/build")
async def build_codebase_trace(workspace_id: str, codebase_id: str, request: CodebaseTraceBuildRequest) -> dict[str, Any]:
    _runtime_obj, workspace, meta, _registry = _registry_for(workspace_id)
    if meta.get("status") == "archived":
        return _blocked(
            workspace_id=str(meta["workspace_id"]),
            message="Workspace is archived and cannot build codebase trace",
            code="workspace_archived",
            next_actions=["knowledge_workspace_describe"],
        )
    service = CodebaseTraceService(workspace, workspace_id=str(meta["workspace_id"]))
    try:
        result = service.build_trace(codebase_id, snapshot_id=request.snapshot_id)
    except FileNotFoundError as exc:
        message = _trace_not_found_detail(str(exc), codebase_id, request.snapshot_id)
        return _http_v2_error(
            status_code=404,
            workspace_id=str(meta["workspace_id"]),
            codebase_id=codebase_id,
            snapshot_id=request.snapshot_id,
            code=_trace_error_code(str(exc)),
            message=message,
            next_actions=["knowledge_project_inventory", "knowledge_code_symbol_search", "knowledge_public_surface_trace"],
        )
    except ValueError as exc:
        return _blocked(
            workspace_id=str(meta["workspace_id"]),
            message=_trace_error_message(str(exc)),
            code=str(exc),
            next_actions=["knowledge_project_inventory", "knowledge_code_symbol_search"],
        )
    payload = public_trace_payload(result)
    refs = result["summary"].get("artifact_refs", trace_artifact_refs(codebase_id, payload["snapshot_id"]))
    next_actions = ["knowledge_project_overview", "knowledge_agent_context_pack"]
    data = {"trace": payload}
    return envelope(
        workspace_id=str(meta["workspace_id"]),
        artifact_refs=refs,
        next_actions=next_actions,
        data=_with_v2(
            workspace_id=str(meta["workspace_id"]),
            codebase_id=codebase_id,
            snapshot_id=str(payload["snapshot_id"]),
            data=data,
            artifact_refs=refs,
            next_actions=next_actions,
        ),
    )


@router.get("/{workspace_id}/codebases/{codebase_id}/trace/surface/{surface_id:path}")
async def read_codebase_surface_trace(workspace_id: str, codebase_id: str, surface_id: str, snapshot_id: Optional[str] = None) -> dict[str, Any]:
    _runtime_obj, workspace, meta, _registry = _registry_for(workspace_id)
    service = CodebaseTraceService(workspace, workspace_id=str(meta["workspace_id"]))
    try:
        selection = service.trace_surface(codebase_id, surface_id, snapshot_id=snapshot_id)
        resolved_snapshot_id = selection["snapshot_id"]
    except FileNotFoundError as exc:
        message = _trace_not_found_detail(str(exc), codebase_id, snapshot_id)
        return _http_v2_error(
            status_code=404,
            workspace_id=str(meta["workspace_id"]),
            codebase_id=codebase_id,
            snapshot_id=snapshot_id,
            code=_trace_error_code(str(exc)),
            message=message,
            next_actions=["knowledge_public_surface_trace"],
        )
    refs = trace_artifact_refs(codebase_id, resolved_snapshot_id)
    data = {"trace": public_trace_selection_payload(selection)}
    return envelope(
        workspace_id=str(meta["workspace_id"]),
        artifact_refs=refs,
        data=_with_v2(
            workspace_id=str(meta["workspace_id"]),
            codebase_id=codebase_id,
            snapshot_id=str(resolved_snapshot_id),
            data=data,
            artifact_refs=refs,
        ),
    )


@router.get("/{workspace_id}/codebases/{codebase_id}/trace/capability/{capability_id}")
async def read_codebase_capability_trace(workspace_id: str, codebase_id: str, capability_id: str, snapshot_id: Optional[str] = None) -> dict[str, Any]:
    _runtime_obj, workspace, meta, _registry = _registry_for(workspace_id)
    service = CodebaseTraceService(workspace, workspace_id=str(meta["workspace_id"]))
    try:
        selection = service.trace_capability(codebase_id, capability_id, snapshot_id=snapshot_id)
        resolved_snapshot_id = selection["snapshot_id"]
    except FileNotFoundError as exc:
        message = _trace_not_found_detail(str(exc), codebase_id, snapshot_id)
        return _http_v2_error(
            status_code=404,
            workspace_id=str(meta["workspace_id"]),
            codebase_id=codebase_id,
            snapshot_id=snapshot_id,
            code=_trace_error_code(str(exc)),
            message=message,
            next_actions=["knowledge_public_surface_trace"],
        )
    refs = trace_artifact_refs(codebase_id, resolved_snapshot_id)
    data = {"trace": public_trace_selection_payload(selection)}
    return envelope(
        workspace_id=str(meta["workspace_id"]),
        artifact_refs=refs,
        data=_with_v2(
            workspace_id=str(meta["workspace_id"]),
            codebase_id=codebase_id,
            snapshot_id=str(resolved_snapshot_id),
            data=data,
            artifact_refs=refs,
        ),
    )


@router.get("/{workspace_id}/codebases/{codebase_id}/trace/evidence")
async def read_codebase_trace_evidence(workspace_id: str, codebase_id: str, snapshot_id: Optional[str] = None, limit: int = 50) -> dict[str, Any]:
    _runtime_obj, workspace, meta, _registry = _registry_for(workspace_id)
    service = CodebaseTraceService(workspace, workspace_id=str(meta["workspace_id"]))
    bounded_limit = bounded_int(limit, default=50, minimum=1, maximum=500, field="limit")
    try:
        evidence = service.read_evidence(codebase_id, snapshot_id=snapshot_id, limit=bounded_limit)
        resolved_snapshot_id = snapshot_id or service._latest_snapshot_id(codebase_id)
    except FileNotFoundError as exc:
        message = _trace_not_found_detail(str(exc), codebase_id, snapshot_id)
        return _http_v2_error(
            status_code=404,
            workspace_id=str(meta["workspace_id"]),
            codebase_id=codebase_id,
            snapshot_id=snapshot_id,
            code=_trace_error_code(str(exc)),
            message=message,
            next_actions=["knowledge_public_surface_trace"],
        )
    refs = trace_artifact_refs(codebase_id, resolved_snapshot_id)
    data = {"snapshot_id": resolved_snapshot_id, "items": [public_evidence_payload(item) for item in evidence], "count": len(evidence)}
    return envelope(
        workspace_id=str(meta["workspace_id"]),
        artifact_refs=refs,
        data=_with_v2(
            workspace_id=str(meta["workspace_id"]),
            codebase_id=codebase_id,
            snapshot_id=str(resolved_snapshot_id),
            data=data,
            artifact_refs=refs,
        ),
    )


@router.get("/{workspace_id}/codebases/{codebase_id}/overview")
async def read_codebase_overview(workspace_id: str, codebase_id: str, snapshot_id: Optional[str] = None) -> dict[str, Any]:
    _runtime_obj, workspace, meta, _registry = _registry_for(workspace_id)
    service = CodebaseOverviewService(workspace, workspace_id=str(meta["workspace_id"]))
    try:
        overview = service.read_overview(codebase_id, snapshot_id=snapshot_id, build_if_missing=True)
    except FileNotFoundError as exc:
        message = _phase7_not_found_detail(str(exc), codebase_id, snapshot_id)
        return _http_v2_error(
            status_code=404,
            workspace_id=str(meta["workspace_id"]),
            codebase_id=codebase_id,
            snapshot_id=snapshot_id,
            code=_phase7_error_code(str(exc)),
            message=message,
            next_actions=_phase7_next_actions(str(exc)),
        )
    except ValueError as exc:
        return _blocked(
            workspace_id=str(meta["workspace_id"]),
            message=_phase7_error_message(str(exc)),
            code=str(exc),
            next_actions=["knowledge_codebase_describe"],
        )
    payload = public_overview_payload(overview)
    refs = payload.get("artifact_refs", overview_artifact_refs(codebase_id))
    next_actions = ["knowledge_agent_context_pack"]
    data = {"overview": payload}
    return envelope(
        workspace_id=str(meta["workspace_id"]),
        artifact_refs=refs,
        next_actions=next_actions,
        data=_with_v2(
            workspace_id=str(meta["workspace_id"]),
            codebase_id=codebase_id,
            snapshot_id=str(payload["snapshot_id"]),
            data=data,
            artifact_refs=refs,
            next_actions=next_actions,
        ),
    )


@router.post("/{workspace_id}/codebases/{codebase_id}/agent/context-pack")
async def create_codebase_context_pack(workspace_id: str, codebase_id: str, request: CodebaseContextPackRequest) -> dict[str, Any]:
    _runtime_obj, workspace, meta, _registry = _registry_for(workspace_id)
    service = CodebaseAgentContextService(workspace, workspace_id=str(meta["workspace_id"]))
    try:
        pack = service.create_pack(
            codebase_id,
            snapshot_id=request.snapshot_id,
            mode=request.mode,
            task=request.task,
            output_format=request.format,
            max_tokens=request.max_tokens,
            focus=request.focus,
            include=request.include,
        )
    except FileNotFoundError as exc:
        message = _phase7_not_found_detail(str(exc), codebase_id, request.snapshot_id)
        return _http_v2_error(
            status_code=404,
            workspace_id=str(meta["workspace_id"]),
            codebase_id=codebase_id,
            snapshot_id=request.snapshot_id,
            code=_phase7_error_code(str(exc)),
            message=message,
            next_actions=_phase7_next_actions(str(exc)),
        )
    except ValueError as exc:
        return _blocked(
            workspace_id=str(meta["workspace_id"]),
            message=_phase7_error_message(str(exc)),
            code=str(exc),
            next_actions=["knowledge_project_overview", "knowledge_agent_context_pack"],
        )
    payload = public_context_pack_payload(pack)
    refs = payload.get("artifact_refs", context_artifact_refs(codebase_id, str(payload["pack_id"])))
    data = {"context_pack": payload}
    return envelope(
        workspace_id=str(meta["workspace_id"]),
        artifact_refs=refs,
        data=_with_v2(
            workspace_id=str(meta["workspace_id"]),
            codebase_id=codebase_id,
            snapshot_id=str(payload["snapshot_id"]),
            data=data,
            artifact_refs=refs,
        ),
    )


@router.get("/{workspace_id}/codebases/{codebase_id}/agent/context-packs/{pack_id}")
async def read_codebase_context_pack(workspace_id: str, codebase_id: str, pack_id: str) -> dict[str, Any]:
    _runtime_obj, workspace, meta, _registry = _registry_for(workspace_id)
    service = CodebaseAgentContextService(workspace, workspace_id=str(meta["workspace_id"]))
    try:
        pack = service.read_pack(codebase_id, pack_id)
    except FileNotFoundError as exc:
        message = _phase7_not_found_detail(str(exc), codebase_id, None)
        return _http_v2_error(
            status_code=404,
            workspace_id=str(meta["workspace_id"]),
            codebase_id=codebase_id,
            snapshot_id=None,
            code=_phase7_error_code(str(exc)),
            message=message,
            next_actions=_phase7_next_actions(str(exc)),
        )
    payload = public_context_pack_payload(pack)
    refs = payload.get("artifact_refs", context_artifact_refs(codebase_id, pack_id))
    data = {"context_pack": payload}
    return envelope(
        workspace_id=str(meta["workspace_id"]),
        artifact_refs=refs,
        data=_with_v2(
            workspace_id=str(meta["workspace_id"]),
            codebase_id=codebase_id,
            snapshot_id=str(payload.get("snapshot_id") or ""),
            data=data,
            artifact_refs=refs,
        ),
    )


def _error_code(error: str) -> str:
    if error == "CODEBASE_PATH_NOT_ALLOWED":
        return "path_not_allowed"
    if error in {"CODEBASE_PATH_NOT_FOUND", "CODEBASE_PATH_NOT_DIRECTORY", "CODEBASE_ID_CONFLICT"}:
        return error
    if "codebase_id" in error.lower():
        return "INVALID_CODEBASE_ID"
    return "CODEBASE_IMPORT_FAILED"


def _error_message(code: str, error: str) -> str:
    if code == "path_not_allowed":
        return "Codebase path is outside allowed roots"
    if code == "CODEBASE_PATH_NOT_FOUND":
        return "Codebase path does not exist"
    if code == "CODEBASE_PATH_NOT_DIRECTORY":
        return "Codebase path is not a directory"
    if code == "CODEBASE_ID_CONFLICT":
        return "codebase_id already exists for a different root path"
    return error or "Codebase import failed"


def _snapshot_error_message(code: str) -> str:
    if code == "CODEBASE_NOT_ACTIVE":
        return "Codebase is not active"
    return code or "Codebase snapshot failed"


def _inventory_not_found_detail(error: str, codebase_id: str, snapshot_id: str | None) -> str:
    if "SNAPSHOT_NOT_FOUND" in error:
        return "No codebase snapshot exists; create one before inventory"
    if "INVENTORY_NOT_FOUND" in error:
        return f"Inventory not found for snapshot_id: {snapshot_id or 'latest'}"
    if error == codebase_id:
        return f"Unknown codebase_id: {codebase_id}"
    return error or "Inventory not found"


def _inventory_error_message(code: str) -> str:
    if code == "CODEBASE_NOT_ACTIVE":
        return "Codebase is not active"
    if code == "INVALID_SURFACE_TYPE":
        return "Invalid surface_type filter"
    return code or "Codebase inventory failed"


def _inventory_error_code(error: str) -> str:
    if "SNAPSHOT_NOT_FOUND" in error:
        return "SNAPSHOT_NOT_FOUND"
    if "INVENTORY_NOT_FOUND" in error:
        return "INVENTORY_NOT_FOUND"
    return "CODEBASE_NOT_FOUND"


def _symbol_not_found_detail(error: str, codebase_id: str, snapshot_id: str | None) -> str:
    if "SNAPSHOT_NOT_FOUND" in error:
        return "No codebase snapshot exists; create one before building symbols"
    if "SYMBOL_INDEX_NOT_FOUND" in error:
        return f"Symbol index not found for snapshot_id: {snapshot_id or 'latest'}"
    if "SYMBOL_NOT_FOUND" in error:
        return "Symbol not found"
    if error == codebase_id:
        return f"Unknown codebase_id: {codebase_id}"
    return error or "Symbol index not found"


def _symbol_error_message(code: str) -> str:
    if code == "CODEBASE_NOT_ACTIVE":
        return "Codebase is not active"
    return code or "Codebase symbol index failed"


def _symbol_error_code(error: str) -> str:
    if "SNAPSHOT_NOT_FOUND" in error:
        return "SNAPSHOT_NOT_FOUND"
    if "SYMBOL_INDEX_NOT_FOUND" in error:
        return "SYMBOL_INDEX_NOT_FOUND"
    if "SYMBOL_NOT_FOUND" in error:
        return "SYMBOL_NOT_FOUND"
    return "CODEBASE_NOT_FOUND"


def _trace_not_found_detail(error: str, codebase_id: str, snapshot_id: str | None) -> str:
    if "SNAPSHOT_NOT_FOUND" in error:
        return "No codebase snapshot exists; create one before building trace"
    if "NO_INVENTORY" in error:
        return "Inventory artifact not found; build inventory before trace"
    if "NO_SYMBOL_INDEX" in error:
        return "Symbol index artifact not found; build symbols before trace"
    if "TRACE_NOT_FOUND" in error:
        return f"Trace artifact not found for snapshot_id: {snapshot_id or 'latest'}"
    if "TRACE_SURFACE_NOT_FOUND" in error:
        return "Trace surface not found"
    if "TRACE_CAPABILITY_NOT_FOUND" in error:
        return "Trace capability not found"
    if error == codebase_id:
        return f"Unknown codebase_id: {codebase_id}"
    return error or "Trace not found"


def _trace_error_message(code: str) -> str:
    if code == "CODEBASE_NOT_ACTIVE":
        return "Codebase is not active"
    return code or "Codebase trace failed"


def _trace_error_code(error: str) -> str:
    if "SNAPSHOT_NOT_FOUND" in error:
        return "SNAPSHOT_NOT_FOUND"
    if "NO_INVENTORY" in error:
        return "INVENTORY_NOT_FOUND"
    if "NO_SYMBOL_INDEX" in error:
        return "SYMBOL_INDEX_NOT_FOUND"
    if "TRACE_NOT_FOUND" in error:
        return "TRACE_NOT_FOUND"
    if "TRACE_SURFACE_NOT_FOUND" in error:
        return "TRACE_SURFACE_NOT_FOUND"
    if "TRACE_CAPABILITY_NOT_FOUND" in error:
        return "TRACE_CAPABILITY_NOT_FOUND"
    return "CODEBASE_NOT_FOUND"


def _phase7_not_found_detail(error: str, codebase_id: str, snapshot_id: str | None) -> str:
    if "SNAPSHOT_NOT_FOUND" in error:
        return "No codebase snapshot exists; create one before overview or context pack"
    if "INVENTORY_NOT_FOUND" in error or "NO_INVENTORY" in error:
        return "Inventory artifact not found; build inventory before overview or context pack"
    if "SYMBOL_INDEX_NOT_FOUND" in error or "NO_SYMBOL_INDEX" in error:
        return "Symbol index artifact not found; build symbols before overview or context pack"
    if "TRACE_NOT_FOUND" in error:
        return f"Trace artifact not found for snapshot_id: {snapshot_id or 'latest'}"
    if "OVERVIEW_NOT_FOUND" in error:
        return "Project overview artifact not found"
    if "CONTEXT_PACK_NOT_FOUND" in error:
        return "Agent context pack artifact not found"
    if error == codebase_id:
        return f"Unknown codebase_id: {codebase_id}"
    return error or "Project intelligence artifact not found"


def _phase7_error_code(error: str) -> str:
    if "SNAPSHOT_NOT_FOUND" in error:
        return "SNAPSHOT_NOT_FOUND"
    if "INVENTORY_NOT_FOUND" in error or "NO_INVENTORY" in error:
        return "INVENTORY_NOT_FOUND"
    if "SYMBOL_INDEX_NOT_FOUND" in error or "NO_SYMBOL_INDEX" in error:
        return "SYMBOL_INDEX_NOT_FOUND"
    if "TRACE_NOT_FOUND" in error:
        return "TRACE_NOT_FOUND"
    if "OVERVIEW_NOT_FOUND" in error:
        return "OVERVIEW_NOT_FOUND"
    if "CONTEXT_PACK_NOT_FOUND" in error:
        return "CONTEXT_PACK_NOT_FOUND"
    return "CODEBASE_NOT_FOUND"


def _phase7_next_actions(error: str) -> list[str]:
    if "SNAPSHOT_NOT_FOUND" in error:
        return ["knowledge_codebase_snapshot"]
    if "INVENTORY_NOT_FOUND" in error or "NO_INVENTORY" in error:
        return ["knowledge_project_inventory"]
    if "SYMBOL_INDEX_NOT_FOUND" in error or "NO_SYMBOL_INDEX" in error:
        return ["knowledge_code_symbol_search"]
    if "TRACE_NOT_FOUND" in error:
        return ["knowledge_public_surface_trace"]
    if "CONTEXT_PACK_NOT_FOUND" in error:
        return ["knowledge_agent_context_pack"]
    return ["knowledge_codebase_describe"]


def _phase7_error_message(code: str) -> str:
    if code == "INVALID_CONTEXT_MODE":
        return "mode must be project_brief or task_context"
    if code == "INVALID_CONTEXT_FORMAT":
        return "format must be json or markdown"
    if code == "TASK_REQUIRED":
        return "task is required for task_context"
    if code == "CODEBASE_NOT_ACTIVE":
        return "Codebase is not active"
    return code or "Project intelligence context failed"

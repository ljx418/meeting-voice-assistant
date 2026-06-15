"""MCP tool schemas and handlers for V2 codebase assets."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Callable

from .code_assets.envelope import v2_error_envelope, v2_success_envelope
from .code_assets.context.persistence import context_artifact_refs
from .code_assets.context.service import CodebaseAgentContextService, public_context_pack_payload
from .code_assets.inventory import CodebaseInventoryService, inventory_artifact_refs, public_inventory_payload
from .code_assets.overview import CodebaseOverviewService, overview_artifact_refs, public_overview_payload
from .code_assets.registry import CodebaseRegistry
from .code_assets.snapshot import CodebaseSnapshotService, public_snapshot
from .code_assets.symbols import CodebaseSymbolIndexService, public_symbol_index_payload, symbol_artifact_refs
from .code_assets.trace import CodebaseTraceService, public_trace_selection_payload, trace_artifact_refs
from .mcp_code_devwiki_tools import DEVWIKI_TOOL_NAMES, DEVWIKI_TOOL_SPECS, handle_devwiki_tool
from .mcp_code_graph_tools import GRAPH_TOOL_NAMES, GRAPH_TOOL_SPECS, handle_graph_tool
from .mcp_code_quality_tools import QUALITY_TOOL_NAMES, QUALITY_TOOL_SPECS, handle_quality_tool
from .mcp_code_architecture_tools import ARCHITECTURE_TOOL_NAMES, ARCHITECTURE_TOOL_SPECS, handle_architecture_tool
from .mcp_code_doc_grounded_architecture_tools import DOC_GROUNDED_ARCHITECTURE_TOOL_NAMES, DOC_GROUNDED_ARCHITECTURE_TOOL_SPECS, handle_doc_grounded_architecture_tool
from .mcp_code_architecture_intent_tools import ARCHITECTURE_INTENT_TOOL_NAMES, ARCHITECTURE_INTENT_TOOL_SPECS, handle_architecture_intent_tool
from .mcp_code_coding_agent_tools import CODING_AGENT_TOOL_NAMES, CODING_AGENT_TOOL_SPECS, handle_coding_agent_tool
from .mcp_code_platform_tools import PLATFORM_TOOL_NAMES, PLATFORM_TOOL_SPECS, handle_platform_tool


CODE_TOOL_NAMES = {
    "knowledge_codebase_archive",
    "knowledge_codebase_describe",
    "knowledge_codebase_import",
    "knowledge_codebase_list",
    "knowledge_codebase_snapshot",
    "knowledge_code_symbol_search",
    "knowledge_agent_context_pack",
    "knowledge_public_surface_trace",
    "knowledge_project_overview",
    "knowledge_project_inventory",
} | DEVWIKI_TOOL_NAMES | GRAPH_TOOL_NAMES | QUALITY_TOOL_NAMES | ARCHITECTURE_TOOL_NAMES | DOC_GROUNDED_ARCHITECTURE_TOOL_NAMES | ARCHITECTURE_INTENT_TOOL_NAMES | CODING_AGENT_TOOL_NAMES | PLATFORM_TOOL_NAMES


CODE_TOOL_SPECS = [
    {
        "name": "knowledge_codebase_import",
        "description": "Import a local repository as a V2 codebase asset",
        "inputSchema": {
            "type": "object",
            "properties": {
                "workspace_id": {"type": "string"},
                "path": {"type": "string"},
                "codebase_id": {"type": "string"},
                "name": {"type": "string"},
                "metadata": {"type": "object"},
                "scan_policy": {"type": "object"},
            },
            "required": ["workspace_id", "path"],
        },
    },
    {
        "name": "knowledge_codebase_list",
        "description": "List V2 codebase assets for a managed workspace",
        "inputSchema": {
            "type": "object",
            "properties": {
                "workspace_id": {"type": "string"},
                "include_archived": {"type": "boolean", "default": False},
                "limit": {"type": "integer", "default": 100},
            },
            "required": ["workspace_id"],
        },
    },
    {
        "name": "knowledge_codebase_snapshot",
        "description": "Generate a deterministic repo snapshot for an imported V2 codebase asset",
        "inputSchema": {
            "type": "object",
            "properties": {
                "workspace_id": {"type": "string"},
                "codebase_id": {"type": "string"},
                "scan_policy": {"type": "object"},
                "include_git": {"type": "boolean", "default": True},
            },
            "required": ["workspace_id", "codebase_id"],
        },
    },
    {
        "name": "knowledge_codebase_describe",
        "description": "Describe one V2 codebase asset",
        "inputSchema": {
            "type": "object",
            "properties": {
                "workspace_id": {"type": "string"},
                "codebase_id": {"type": "string"},
            },
            "required": ["workspace_id", "codebase_id"],
        },
    },
    {
        "name": "knowledge_codebase_archive",
        "description": "Archive one V2 codebase asset",
        "inputSchema": {
            "type": "object",
            "properties": {
                "workspace_id": {"type": "string"},
                "codebase_id": {"type": "string"},
                "reason": {"type": "string"},
            },
            "required": ["workspace_id", "codebase_id"],
        },
    },
    {
        "name": "knowledge_project_inventory",
        "description": "Build or read deterministic public surface inventory for a V2 codebase snapshot",
        "inputSchema": {
            "type": "object",
            "properties": {
                "workspace_id": {"type": "string"},
                "codebase_id": {"type": "string"},
                "snapshot_id": {"type": "string"},
                "build": {"type": "boolean", "default": True},
            },
            "required": ["workspace_id", "codebase_id"],
        },
    },
    {
        "name": "knowledge_code_symbol_search",
        "description": "Build or search deterministic Python symbols for a V2 codebase snapshot",
        "inputSchema": {
            "type": "object",
            "properties": {
                "workspace_id": {"type": "string"},
                "codebase_id": {"type": "string"},
                "snapshot_id": {"type": "string"},
                "query": {"type": "string"},
                "kind": {"type": "string"},
                "limit": {"type": "integer", "default": 20},
                "build": {"type": "boolean", "default": False},
            },
            "required": ["workspace_id", "codebase_id"],
        },
    },
    {
        "name": "knowledge_public_surface_trace",
        "description": "Build or read V2 codebase public surface and capability evidence trace",
        "inputSchema": {
            "type": "object",
            "properties": {
                "workspace_id": {"type": "string"},
                "codebase_id": {"type": "string"},
                "snapshot_id": {"type": "string"},
                "surface_id": {"type": "string"},
                "capability": {"type": "string"},
                "build": {"type": "boolean", "default": False},
                "limit": {"type": "integer", "default": 50},
            },
            "required": ["workspace_id", "codebase_id"],
        },
    },
    {
        "name": "knowledge_project_overview",
        "description": "Generate or read an evidence-backed V2 project overview for a codebase snapshot",
        "inputSchema": {
            "type": "object",
            "properties": {
                "workspace_id": {"type": "string"},
                "codebase_id": {"type": "string"},
                "snapshot_id": {"type": "string"},
            },
            "required": ["workspace_id", "codebase_id"],
        },
    },
    {
        "name": "knowledge_agent_context_pack",
        "description": "Generate an evidence-backed V2 Agent Context Pack for project reading or a development task",
        "inputSchema": {
            "type": "object",
            "properties": {
                "workspace_id": {"type": "string"},
                "codebase_id": {"type": "string"},
                "snapshot_id": {"type": "string"},
                "mode": {"type": "string", "enum": ["project_brief", "task_context"]},
                "task": {"type": "string"},
                "format": {"type": "string", "enum": ["json", "markdown"], "default": "json"},
                "max_tokens": {"type": "integer", "default": 16000},
                "focus": {"type": "object"},
                "include": {"type": "array", "items": {"type": "string"}},
                "pack_id": {"type": "string"},
            },
            "required": ["workspace_id", "codebase_id"],
        },
    },
] + DEVWIKI_TOOL_SPECS + GRAPH_TOOL_SPECS + QUALITY_TOOL_SPECS + ARCHITECTURE_TOOL_SPECS + DOC_GROUNDED_ARCHITECTURE_TOOL_SPECS + ARCHITECTURE_INTENT_TOOL_SPECS + CODING_AGENT_TOOL_SPECS + PLATFORM_TOOL_SPECS


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


def _blocked_v2(
    envelope: Callable[..., dict[str, Any]],
    *,
    workspace_id: str,
    message: str,
    code: str,
    codebase_id: str | None = None,
    snapshot_id: str | None = None,
    next_actions: list[str] | None = None,
) -> dict[str, Any]:
    return envelope(
        workspace_id=workspace_id,
        status="blocked",
        warnings=[message],
        next_actions=next_actions,
        data={
            "error": {"code": code, "message": message, "retryable": False},
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


def handle_code_tool(
    name: str,
    arguments: dict[str, Any],
    *,
    blocked: Callable[..., dict[str, Any]],
    envelope: Callable[..., dict[str, Any]],
    ensure_workspace_meta: Callable[..., dict[str, Any]],
    resolve_workspace: Callable[[str | None, str | None], Path],
) -> dict[str, Any]:
    if name not in CODE_TOOL_NAMES:
        raise ValueError(f"Unknown code tool: {name}")
    if name in DEVWIKI_TOOL_NAMES:
        return handle_devwiki_tool(
            name,
            arguments,
            blocked=blocked,
            envelope=envelope,
            ensure_workspace_meta=ensure_workspace_meta,
            resolve_workspace=resolve_workspace,
        )
    if name in GRAPH_TOOL_NAMES:
        return handle_graph_tool(
            name,
            arguments,
            blocked=blocked,
            envelope=envelope,
            ensure_workspace_meta=ensure_workspace_meta,
            resolve_workspace=resolve_workspace,
        )
    if name in QUALITY_TOOL_NAMES:
        return handle_quality_tool(
            name,
            arguments,
            blocked=blocked,
            envelope=envelope,
            ensure_workspace_meta=ensure_workspace_meta,
            resolve_workspace=resolve_workspace,
        )
    if name in ARCHITECTURE_TOOL_NAMES:
        return handle_architecture_tool(
            name,
            arguments,
            blocked=blocked,
            envelope=envelope,
            ensure_workspace_meta=ensure_workspace_meta,
            resolve_workspace=resolve_workspace,
        )
    if name in DOC_GROUNDED_ARCHITECTURE_TOOL_NAMES:
        return handle_doc_grounded_architecture_tool(
            name,
            arguments,
            blocked=blocked,
            envelope=envelope,
            ensure_workspace_meta=ensure_workspace_meta,
            resolve_workspace=resolve_workspace,
        )
    if name in ARCHITECTURE_INTENT_TOOL_NAMES:
        return handle_architecture_intent_tool(
            name,
            arguments,
            blocked=blocked,
            envelope=envelope,
            ensure_workspace_meta=ensure_workspace_meta,
            resolve_workspace=resolve_workspace,
        )
    if name in CODING_AGENT_TOOL_NAMES:
        return handle_coding_agent_tool(
            name,
            arguments,
            blocked=blocked,
            envelope=envelope,
            ensure_workspace_meta=ensure_workspace_meta,
            resolve_workspace=resolve_workspace,
        )
    if name in PLATFORM_TOOL_NAMES:
        def _tool_specs_provider() -> list[dict[str, Any]]:
            from .mcp_tool_registry import all_tool_specs

            return all_tool_specs()

        return handle_platform_tool(
            name,
            arguments,
            blocked=blocked,
            envelope=envelope,
            ensure_workspace_meta=ensure_workspace_meta,
            resolve_workspace=resolve_workspace,
            tool_specs_provider=_tool_specs_provider,
        )

    workspace_path = resolve_workspace(arguments.get("workspace_id"), None)
    meta = ensure_workspace_meta(workspace_path)
    workspace_id = str(meta["workspace_id"])
    if meta.get("status") == "archived" and name in {"knowledge_codebase_import", "knowledge_codebase_archive"}:
        return blocked(
            workspace_id=workspace_id,
            message="Workspace is archived and cannot modify codebases",
            next_actions=["knowledge_workspace_describe"],
            code="workspace_archived",
        )

    registry = CodebaseRegistry(workspace_path, workspace_id=workspace_id)
    if name == "knowledge_codebase_list":
        try:
            limit = int(arguments.get("limit") if arguments.get("limit") is not None else 100)
        except (TypeError, ValueError):
            return _blocked_v2(
                envelope,
                workspace_id=workspace_id,
                message="limit must be an integer",
                next_actions=["knowledge_codebase_list"],
                code="INVALID_LIMIT",
            )
        limit = max(1, min(limit, 500))
        items = [
            asset.public_dict()
            for asset in registry.list_codebases(
                include_archived=bool(arguments.get("include_archived", False)),
                limit=limit,
            )
        ]
        data = {"items": items, "count": len(items)}
        return envelope(workspace_id=workspace_id, data=_with_v2(workspace_id=workspace_id, data=data))

    if name == "knowledge_codebase_snapshot":
        codebase_id = str(arguments.get("codebase_id") or "").strip()
        if not codebase_id:
            return blocked(
                workspace_id=workspace_id,
                message="codebase_id is required",
                next_actions=["knowledge_codebase_list"],
                code="invalid_codebase_id",
            )
        scan_policy = arguments.get("scan_policy") or {}
        if not isinstance(scan_policy, dict):
            return blocked(
                workspace_id=workspace_id,
                message="scan_policy must be an object",
                next_actions=["knowledge_codebase_snapshot"],
                code="invalid_scan_policy",
            )
        service = CodebaseSnapshotService(workspace_path, workspace_id=workspace_id)
        try:
            result = service.create_snapshot(
                codebase_id,
                scan_policy=scan_policy,
                include_git=bool(arguments.get("include_git", True)),
            )
        except FileNotFoundError:
            return blocked(
                workspace_id=workspace_id,
                message="Unknown codebase_id",
                next_actions=["knowledge_codebase_list"],
                code="codebase_not_found",
            )
        except ValueError as exc:
            return blocked(
                workspace_id=workspace_id,
                message=_snapshot_error_message(str(exc)),
                next_actions=["knowledge_codebase_describe"],
                code=str(exc),
            )
        snapshot = public_snapshot(result["snapshot"])
        next_actions = ["knowledge_project_inventory", "knowledge_code_symbol_search"]
        data = {"snapshot": snapshot}
        return envelope(
            workspace_id=workspace_id,
            artifact_refs=snapshot["artifact_refs"],
            next_actions=next_actions,
            data=_with_v2(
                workspace_id=workspace_id,
                codebase_id=codebase_id,
                snapshot_id=str(snapshot["snapshot_id"]),
                data=data,
                artifact_refs=snapshot["artifact_refs"],
                next_actions=next_actions,
            ),
        )

    if name == "knowledge_project_inventory":
        codebase_id = str(arguments.get("codebase_id") or "").strip()
        if not codebase_id:
            return blocked(
                workspace_id=workspace_id,
                message="codebase_id is required",
                next_actions=["knowledge_codebase_list"],
                code="invalid_codebase_id",
            )
        snapshot_id = str(arguments.get("snapshot_id") or "").strip() or None
        build = bool(arguments.get("build", True))
        service = CodebaseInventoryService(workspace_path, workspace_id=workspace_id)
        try:
            result = service.build_inventory(codebase_id, snapshot_id=snapshot_id) if build else service.read_inventory(codebase_id, snapshot_id=snapshot_id)
        except FileNotFoundError as exc:
            return _blocked_v2(
                envelope,
                workspace_id=workspace_id,
                message=_inventory_not_found_message(str(exc)),
                codebase_id=codebase_id,
                snapshot_id=snapshot_id,
                next_actions=["knowledge_codebase_snapshot"],
                code=_inventory_error_code(str(exc)),
            )
        except ValueError as exc:
            return blocked(
                workspace_id=workspace_id,
                message=_snapshot_error_message(str(exc)),
                next_actions=["knowledge_codebase_describe"],
                code=str(exc),
            )
        payload = public_inventory_payload(result)
        refs = result["summary"].get("artifact_refs", inventory_artifact_refs(codebase_id, payload["snapshot_id"]))
        next_actions = ["knowledge_code_symbol_search", "knowledge_public_surface_trace"]
        data = {"inventory": payload}
        return envelope(
            workspace_id=workspace_id,
            artifact_refs=refs,
            next_actions=next_actions,
            data=_with_v2(
                workspace_id=workspace_id,
                codebase_id=codebase_id,
                snapshot_id=str(payload["snapshot_id"]),
                data=data,
                artifact_refs=refs,
                next_actions=next_actions,
            ),
        )

    if name == "knowledge_code_symbol_search":
        codebase_id = str(arguments.get("codebase_id") or "").strip()
        if not codebase_id:
            return blocked(
                workspace_id=workspace_id,
                message="codebase_id is required",
                next_actions=["knowledge_codebase_list"],
                code="invalid_codebase_id",
            )
        snapshot_id = str(arguments.get("snapshot_id") or "").strip() or None
        try:
            limit = int(arguments.get("limit") if arguments.get("limit") is not None else 20)
        except (TypeError, ValueError):
            return _blocked_v2(
                envelope,
                workspace_id=workspace_id,
                message="limit must be an integer",
                codebase_id=codebase_id,
                snapshot_id=snapshot_id,
                next_actions=["knowledge_code_symbol_search"],
                code="INVALID_LIMIT",
            )
        limit = max(1, min(limit, 200))
        service = CodebaseSymbolIndexService(workspace_path, workspace_id=workspace_id)
        try:
            result = service.build_symbol_index(codebase_id, snapshot_id=snapshot_id) if bool(arguments.get("build", False)) else service.read_symbol_index(codebase_id, snapshot_id=snapshot_id)
            symbols = service.read_symbols(
                codebase_id,
                snapshot_id=str(result["summary"]["snapshot_id"]),
                kind=str(arguments.get("kind") or "").strip() or None,
                query=str(arguments.get("query") or "").strip() or None,
                limit=limit,
            )
        except FileNotFoundError as exc:
            return _blocked_v2(
                envelope,
                workspace_id=workspace_id,
                message=_symbol_not_found_message(str(exc)),
                codebase_id=codebase_id,
                snapshot_id=snapshot_id,
                next_actions=["knowledge_code_symbol_search", "knowledge_codebase_snapshot"],
                code=_symbol_error_code(str(exc)),
            )
        except ValueError as exc:
            return blocked(
                workspace_id=workspace_id,
                message=_snapshot_error_message(str(exc)),
                next_actions=["knowledge_codebase_describe"],
                code=str(exc),
            )
        payload = public_symbol_index_payload({"summary": result["summary"], "symbols": symbols, "imports": result.get("imports", [])})
        refs = result["summary"].get("artifact_refs", symbol_artifact_refs(codebase_id, payload["snapshot_id"]))
        next_actions = ["knowledge_public_surface_trace", "knowledge_agent_context_pack"]
        data = {"symbol_index": payload}
        return envelope(
            workspace_id=workspace_id,
            artifact_refs=refs,
            next_actions=next_actions,
            data=_with_v2(
                workspace_id=workspace_id,
                codebase_id=codebase_id,
                snapshot_id=str(payload["snapshot_id"]),
                data=data,
                artifact_refs=refs,
                next_actions=next_actions,
            ),
        )

    if name == "knowledge_public_surface_trace":
        codebase_id = str(arguments.get("codebase_id") or "").strip()
        if not codebase_id:
            return blocked(
                workspace_id=workspace_id,
                message="codebase_id is required",
                next_actions=["knowledge_codebase_list"],
                code="invalid_codebase_id",
            )
        snapshot_id = str(arguments.get("snapshot_id") or "").strip() or None
        surface_id = str(arguments.get("surface_id") or "").strip()
        capability = str(arguments.get("capability") or "").strip()
        if not bool(arguments.get("build", False)) and not surface_id and not capability:
            return _blocked_v2(
                envelope,
                workspace_id=workspace_id,
                message="surface_id or capability is required unless build=true",
                codebase_id=codebase_id,
                snapshot_id=snapshot_id,
                next_actions=["knowledge_public_surface_trace"],
                code="INVALID_TRACE_REQUEST",
            )
        service = CodebaseTraceService(workspace_path, workspace_id=workspace_id)
        try:
            if bool(arguments.get("build", False)):
                result = service.build_trace(codebase_id, snapshot_id=snapshot_id)
                resolved_snapshot_id = str(result["summary"]["snapshot_id"])
                if not surface_id and not capability:
                    refs = result["summary"].get("artifact_refs", trace_artifact_refs(codebase_id, resolved_snapshot_id))
                    next_actions = ["knowledge_project_overview", "knowledge_agent_context_pack"]
                    data = {"trace": {"summary": result["summary"]}}
                    return envelope(
                        workspace_id=workspace_id,
                        artifact_refs=refs,
                        next_actions=next_actions,
                        data=_with_v2(
                            workspace_id=workspace_id,
                            codebase_id=codebase_id,
                            snapshot_id=resolved_snapshot_id,
                            data=data,
                            artifact_refs=refs,
                            next_actions=next_actions,
                        ),
                    )
                snapshot_id = resolved_snapshot_id
            if surface_id:
                selection = service.trace_surface(codebase_id, surface_id, snapshot_id=snapshot_id)
            else:
                selection = service.trace_capability(codebase_id, capability, snapshot_id=snapshot_id)
        except FileNotFoundError as exc:
            return _blocked_v2(
                envelope,
                workspace_id=workspace_id,
                message=_trace_not_found_message(str(exc)),
                codebase_id=codebase_id,
                snapshot_id=snapshot_id,
                next_actions=["knowledge_project_inventory", "knowledge_code_symbol_search", "knowledge_public_surface_trace"],
                code=_trace_error_code(str(exc)),
            )
        except ValueError as exc:
            return blocked(
                workspace_id=workspace_id,
                message=_snapshot_error_message(str(exc)),
                next_actions=["knowledge_codebase_describe"],
                code=str(exc),
            )
        payload = public_trace_selection_payload(selection)
        refs = trace_artifact_refs(codebase_id, str(payload["snapshot_id"]))
        next_actions = ["knowledge_project_overview", "knowledge_agent_context_pack"]
        data = {"trace": payload}
        return envelope(
            workspace_id=workspace_id,
            artifact_refs=refs,
            next_actions=next_actions,
            data=_with_v2(
                workspace_id=workspace_id,
                codebase_id=codebase_id,
                snapshot_id=str(payload["snapshot_id"]),
                data=data,
                artifact_refs=refs,
                next_actions=next_actions,
            ),
        )

    if name == "knowledge_project_overview":
        codebase_id = str(arguments.get("codebase_id") or "").strip()
        if not codebase_id:
            return blocked(
                workspace_id=workspace_id,
                message="codebase_id is required",
                next_actions=["knowledge_codebase_list"],
                code="invalid_codebase_id",
            )
        snapshot_id = str(arguments.get("snapshot_id") or "").strip() or None
        service = CodebaseOverviewService(workspace_path, workspace_id=workspace_id)
        try:
            overview = service.read_overview(codebase_id, snapshot_id=snapshot_id, build_if_missing=True)
        except FileNotFoundError as exc:
            return _blocked_v2(
                envelope,
                workspace_id=workspace_id,
                message=_phase7_not_found_message(str(exc)),
                codebase_id=codebase_id,
                snapshot_id=snapshot_id,
                next_actions=_phase7_next_actions(str(exc)),
                code=_phase7_error_code(str(exc)),
            )
        except ValueError as exc:
            return blocked(
                workspace_id=workspace_id,
                message=_phase7_error_message(str(exc)),
                next_actions=["knowledge_codebase_describe"],
                code=str(exc),
            )
        payload = public_overview_payload(overview)
        refs = payload.get("artifact_refs", overview_artifact_refs(codebase_id))
        next_actions = ["knowledge_agent_context_pack"]
        data = {"overview": payload}
        return envelope(
            workspace_id=workspace_id,
            artifact_refs=refs,
            next_actions=next_actions,
            data=_with_v2(
                workspace_id=workspace_id,
                codebase_id=codebase_id,
                snapshot_id=str(payload["snapshot_id"]),
                data=data,
                artifact_refs=refs,
                next_actions=next_actions,
            ),
        )

    if name == "knowledge_agent_context_pack":
        codebase_id = str(arguments.get("codebase_id") or "").strip()
        if not codebase_id:
            return blocked(
                workspace_id=workspace_id,
                message="codebase_id is required",
                next_actions=["knowledge_codebase_list"],
                code="invalid_codebase_id",
            )
        snapshot_id = str(arguments.get("snapshot_id") or "").strip() or None
        service = CodebaseAgentContextService(workspace_path, workspace_id=workspace_id)
        pack_id = str(arguments.get("pack_id") or "").strip()
        try:
            if pack_id:
                pack = service.read_pack(codebase_id, pack_id)
            else:
                pack = service.create_pack(
                    codebase_id,
                    snapshot_id=snapshot_id,
                    mode=str(arguments.get("mode") or "").strip() or None,
                    task=str(arguments.get("task") or "").strip() or None,
                    output_format=str(arguments.get("format") or "json").strip() or "json",
                    max_tokens=int(arguments.get("max_tokens") or 16000),
                    focus=dict(arguments.get("focus") or {}),
                    include=list(arguments.get("include") or []),
                )
        except FileNotFoundError as exc:
            return _blocked_v2(
                envelope,
                workspace_id=workspace_id,
                message=_phase7_not_found_message(str(exc)),
                codebase_id=codebase_id,
                snapshot_id=snapshot_id,
                next_actions=_phase7_next_actions(str(exc)),
                code=_phase7_error_code(str(exc)),
            )
        except (TypeError, ValueError) as exc:
            code = str(exc) or "INVALID_CONTEXT_REQUEST"
            return _blocked_v2(
                envelope,
                workspace_id=workspace_id,
                message=_phase7_error_message(code),
                codebase_id=codebase_id,
                snapshot_id=snapshot_id,
                next_actions=["knowledge_project_overview", "knowledge_agent_context_pack"],
                code=code,
            )
        payload = public_context_pack_payload(pack)
        refs = payload.get("artifact_refs", context_artifact_refs(codebase_id, str(payload["pack_id"])))
        data = {"context_pack": payload}
        return envelope(
            workspace_id=workspace_id,
            artifact_refs=refs,
            data=_with_v2(
                workspace_id=workspace_id,
                codebase_id=codebase_id,
                snapshot_id=str(payload["snapshot_id"]),
                data=data,
                artifact_refs=refs,
            ),
        )

    if name == "knowledge_codebase_describe":
        codebase_id = str(arguments.get("codebase_id") or "").strip()
        if not codebase_id:
            return blocked(
                workspace_id=workspace_id,
                message="codebase_id is required",
                next_actions=["knowledge_codebase_list"],
                code="invalid_codebase_id",
            )
        try:
            asset = registry.describe(codebase_id)
        except FileNotFoundError:
            return _blocked_v2(
                envelope,
                workspace_id=workspace_id,
                message="Unknown codebase_id",
                codebase_id=codebase_id,
                next_actions=["knowledge_codebase_list"],
                code="CODEBASE_NOT_FOUND",
            )
        except ValueError as exc:
            return _blocked_from_error(blocked, envelope, workspace_id=workspace_id, error=str(exc))
        data = {"codebase": asset.public_dict()}
        return envelope(
            workspace_id=workspace_id,
            data=_with_v2(workspace_id=workspace_id, codebase_id=asset.codebase_id, data=data),
        )

    if name == "knowledge_codebase_archive":
        codebase_id = str(arguments.get("codebase_id") or "").strip()
        if not codebase_id:
            return blocked(
                workspace_id=workspace_id,
                message="codebase_id is required",
                next_actions=["knowledge_codebase_list"],
                code="invalid_codebase_id",
            )
        try:
            asset = registry.archive(codebase_id, reason=str(arguments.get("reason") or ""))
        except FileNotFoundError:
            return blocked(
                workspace_id=workspace_id,
                message="Unknown codebase_id",
                next_actions=["knowledge_codebase_list"],
                code="codebase_not_found",
            )
        except ValueError as exc:
            return _blocked_from_error(blocked, envelope, workspace_id=workspace_id, error=str(exc))
        data = {"codebase": asset.public_dict()}
        return envelope(
            workspace_id=workspace_id,
            data=_with_v2(workspace_id=workspace_id, codebase_id=asset.codebase_id, data=data),
        )

    path = str(arguments.get("path") or "").strip()
    if not path:
        return blocked(
            workspace_id=workspace_id,
            message="path is required",
            next_actions=["knowledge_codebase_import"],
            code="invalid_codebase_path",
        )

    try:
        result = registry.import_codebase(
            path=path,
            codebase_id=arguments.get("codebase_id"),
            name=arguments.get("name"),
            metadata=dict(arguments.get("metadata") or {}),
            scan_policy=dict(arguments.get("scan_policy") or {}),
        )
    except ValueError as exc:
        return _blocked_from_error(blocked, envelope, workspace_id=workspace_id, error=str(exc))

    asset = result["asset"]
    refs = [{"type": "codebase", "codebase_id": asset.codebase_id, "artifact_ref": f"codebase://{asset.codebase_id}"}]
    next_actions = ["knowledge_codebase_snapshot", "knowledge_project_inventory"]
    data = {"codebase": asset.public_dict(), "created": bool(result["created"])}
    return envelope(
        workspace_id=workspace_id,
        artifact_refs=refs,
        next_actions=next_actions,
        data=_with_v2(
            workspace_id=workspace_id,
            codebase_id=asset.codebase_id,
            data=data,
            artifact_refs=refs,
            next_actions=next_actions,
        ),
    )


def _blocked_from_error(
    blocked: Callable[..., dict[str, Any]],
    envelope: Callable[..., dict[str, Any]],
    *,
    workspace_id: str,
    error: str,
) -> dict[str, Any]:
    code = _error_code(error)
    if code == "path_not_allowed":
        return envelope(
            workspace_id=workspace_id,
            status="blocked",
            warnings=[_error_message(code, error)],
            next_actions=["knowledge_codebase_import"],
            data={"error": {"code": code, "message": _error_message(code, error), "retryable": False}},
        )
    return blocked(
        workspace_id=workspace_id,
        message=_error_message(code, error),
        next_actions=["knowledge_codebase_import"],
        code=code,
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
    if code == "INVALID_CODEBASE_ID":
        return error
    return error or "Codebase import failed"


def _snapshot_error_message(code: str) -> str:
    if code == "CODEBASE_NOT_ACTIVE":
        return "Codebase is not active"
    return code or "Codebase snapshot failed"


def _inventory_not_found_message(error: str) -> str:
    if "SNAPSHOT_NOT_FOUND" in error:
        return "No codebase snapshot exists; create one before inventory"
    if "INVENTORY_NOT_FOUND" in error:
        return "Inventory artifact not found"
    return "Unknown codebase_id or snapshot_id"


def _inventory_error_code(error: str) -> str:
    if "SNAPSHOT_NOT_FOUND" in error:
        return "SNAPSHOT_NOT_FOUND"
    if "INVENTORY_NOT_FOUND" in error:
        return "INVENTORY_NOT_FOUND"
    return "CODEBASE_NOT_FOUND"


def _symbol_not_found_message(error: str) -> str:
    if "SNAPSHOT_NOT_FOUND" in error:
        return "No codebase snapshot exists; create one before building symbols"
    if "SYMBOL_INDEX_NOT_FOUND" in error:
        return "Symbol index artifact not found"
    if "SYMBOL_NOT_FOUND" in error:
        return "Symbol not found"
    return "Unknown codebase_id or snapshot_id"


def _symbol_error_code(error: str) -> str:
    if "SNAPSHOT_NOT_FOUND" in error:
        return "SNAPSHOT_NOT_FOUND"
    if "SYMBOL_INDEX_NOT_FOUND" in error:
        return "SYMBOL_INDEX_NOT_FOUND"
    if "SYMBOL_NOT_FOUND" in error:
        return "SYMBOL_NOT_FOUND"
    return "CODEBASE_NOT_FOUND"


def _trace_not_found_message(error: str) -> str:
    if "SNAPSHOT_NOT_FOUND" in error:
        return "No codebase snapshot exists; create one before building trace"
    if "NO_INVENTORY" in error:
        return "Inventory artifact not found; build inventory before trace"
    if "NO_SYMBOL_INDEX" in error:
        return "Symbol index artifact not found; build symbols before trace"
    if "TRACE_NOT_FOUND" in error:
        return "Trace artifact not found"
    if "TRACE_SURFACE_NOT_FOUND" in error:
        return "Trace surface not found"
    if "TRACE_CAPABILITY_NOT_FOUND" in error:
        return "Trace capability not found"
    return "Unknown codebase_id or snapshot_id"


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


def _phase7_not_found_message(error: str) -> str:
    if "SNAPSHOT_NOT_FOUND" in error:
        return "No codebase snapshot exists; create one before overview or context pack"
    if "INVENTORY_NOT_FOUND" in error or "NO_INVENTORY" in error:
        return "Inventory artifact not found; build inventory before overview or context pack"
    if "SYMBOL_INDEX_NOT_FOUND" in error or "NO_SYMBOL_INDEX" in error:
        return "Symbol index artifact not found; build symbols before overview or context pack"
    if "TRACE_NOT_FOUND" in error:
        return "Trace artifact not found"
    if "OVERVIEW_NOT_FOUND" in error:
        return "Project overview artifact not found"
    if "CONTEXT_PACK_NOT_FOUND" in error:
        return "Agent context pack artifact not found"
    return "Unknown codebase_id or snapshot_id"


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
    if "invalid literal" in code.lower():
        return "max_tokens must be an integer"
    return code or "Project intelligence context failed"

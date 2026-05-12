"""Workspace lifecycle MCP tool schemas and handlers."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Callable

from .security import validate_workspace_path
from .service import DataService


WORKSPACE_TOOL_NAMES = {
    "knowledge_workspace_create",
    "knowledge_workspace_list",
    "knowledge_workspace_describe",
    "knowledge_workspace_archive",
}

WORKSPACE_TOOL_SPECS = [
    {
        "name": "knowledge_workspace_create",
        "description": "Create or register a managed knowledge workspace",
        "inputSchema": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "root": {"type": "string"},
                "owner": {"type": "string"},
                "tags": {"type": "array", "items": {"type": "string"}},
            },
            "required": ["name"],
        },
    },
    {
        "name": "knowledge_workspace_list",
        "description": "List managed knowledge workspaces under DATA_SERVICE_WORKSPACE_ROOT",
        "inputSchema": {
            "type": "object",
            "properties": {
                "owner": {"type": "string"},
                "tag": {"type": "string"},
                "limit": {"type": "integer", "default": 50},
            },
        },
    },
    {
        "name": "knowledge_workspace_describe",
        "description": "Describe one managed knowledge workspace",
        "inputSchema": {
            "type": "object",
            "properties": {
                "workspace_id": {"type": "string"},
                "workspace": {"type": "string"},
            },
        },
    },
    {
        "name": "knowledge_workspace_archive",
        "description": "Archive a managed knowledge workspace without deleting data",
        "inputSchema": {
            "type": "object",
            "properties": {
                "workspace_id": {"type": "string"},
                "reason": {"type": "string"},
            },
            "required": ["workspace_id"],
        },
    },
]


def handle_workspace_tool(
    name: str,
    arguments: dict[str, Any],
    *,
    bounded_int: Callable[..., int],
    envelope: Callable[..., dict[str, Any]],
    ensure_workspace_meta: Callable[..., dict[str, Any]],
    layout_payload: Callable[[DataService], dict[str, Any]],
    now: Callable[[], str],
    operations_dir: Callable[[Path], Path],
    read_json: Callable[[Path, Any], Any],
    resolve_workspace: Callable[[str | None, str | None], Path],
    slug: Callable[[object], str],
    workspace_meta_path: Callable[[Path], Path],
    workspace_root: Callable[[], Path],
    write_json: Callable[[Path, Any], None],
) -> dict[str, Any]:
    if name == "knowledge_workspace_create":
        workspace_name = str(arguments.get("name") or "").strip()
        if not workspace_name:
            raise ValueError("name is required")
        tags = [str(tag) for tag in (arguments.get("tags") or [])][:20]
        root_arg = str(arguments.get("root") or "").strip()
        root = validate_workspace_path(root_arg) if root_arg else workspace_root()
        workspace_id = slug(workspace_name)
        workspace_path = validate_workspace_path(root / workspace_id)
        meta = ensure_workspace_meta(
            workspace_path,
            name=workspace_name,
            owner=str(arguments.get("owner") or "") or None,
            tags=tags,
        )
        return envelope(
            workspace_id=meta["workspace_id"],
            artifact_refs=[{"type": "workspace", "path": meta["workspace_path"]}],
            next_actions=["knowledge_source_import", "knowledge_workspace_describe"],
            data={
                "workspace_path": meta["workspace_path"],
                "capabilities": {
                    "ingest": True,
                    "query": True,
                    "quality_feedback": True,
                    "build": True,
                },
            },
        )

    if name == "knowledge_workspace_list":
        root = workspace_root()
        limit = bounded_int(arguments.get("limit"), default=50, minimum=1, maximum=200, field="limit")
        owner = str(arguments.get("owner") or "").strip()
        tag = str(arguments.get("tag") or "").strip()
        items = []
        for meta_path in sorted(root.glob("*/.data_service_workspace.json"), key=lambda item: item.stat().st_mtime, reverse=True):
            meta = read_json(meta_path, {})
            if owner and meta.get("owner") != owner:
                continue
            if tag and tag not in meta.get("tags", []):
                continue
            items.append(
                {
                    "workspace_id": meta.get("workspace_id") or meta_path.parent.name,
                    "name": meta.get("name") or meta_path.parent.name,
                    "workspace_path": meta.get("workspace_path") or str(meta_path.parent),
                    "status": meta.get("status", "active"),
                    "updated_at": meta.get("updated_at"),
                    "tags": meta.get("tags", []),
                }
            )
            if len(items) >= limit:
                break
        return envelope(
            workspace_id="root",
            data={"items": items},
            next_actions=["knowledge_workspace_describe", "knowledge_workspace_create"],
        )

    if name == "knowledge_workspace_describe":
        workspace_path = resolve_workspace(arguments.get("workspace_id"), arguments.get("workspace"))
        meta = ensure_workspace_meta(workspace_path)
        target_service = DataService(workspace_path)
        target_service.ensure_layout()
        bundle = target_service.read_summary_bundle()
        latest_build = None
        operations = sorted(operations_dir(workspace_path).glob("*.json"), key=lambda item: item.stat().st_mtime, reverse=True)
        if operations:
            latest_build = read_json(operations[0], None)
        return envelope(
            workspace_id=meta["workspace_id"],
            artifact_refs=[{"type": "workspace", "path": meta["workspace_path"]}],
            next_actions=["knowledge_source_list", "knowledge_build_start", "knowledge_query"],
            data={
                "layout": layout_payload(target_service),
                "summary": bundle.get("summary_json", {}),
                "engines": {
                    "llmwiki": {"page_count": len(bundle.get("llmwiki_pages", []))},
                    "graphrag": bundle.get("graph_stats", {}),
                },
                "latest_build": latest_build,
                "quality": bundle.get("quality", {}),
            },
        )

    if name == "knowledge_workspace_archive":
        workspace_path = resolve_workspace(arguments.get("workspace_id"), None)
        meta = ensure_workspace_meta(workspace_path)
        meta["status"] = "archived"
        meta["archived_at"] = now()
        meta["archive_reason"] = str(arguments.get("reason") or "")
        meta["updated_at"] = meta["archived_at"]
        write_json(workspace_meta_path(workspace_path), meta)
        return envelope(
            workspace_id=meta["workspace_id"],
            artifact_refs=[{"type": "workspace", "path": meta["workspace_path"]}],
            next_actions=["knowledge_workspace_list"],
            data={"workspace": meta},
        )

    raise ValueError(f"Unknown workspace MCP tool: {name}")

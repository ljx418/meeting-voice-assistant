"""Source registry MCP tool schemas and handlers."""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any, Callable

from .security import validate_source_paths


SOURCE_STATUSES = ["active", "removed", "duplicate", "blocked"]
MAX_IMPORT_FILES = 50
MAX_IMPORT_FILE_BYTES = 10 * 1024 * 1024
MAX_IMPORT_TEXT_BYTES = 2 * 1024 * 1024

SOURCE_TOOL_NAMES = {
    "knowledge_source_import",
    "knowledge_source_list",
    "knowledge_source_remove",
}

SOURCE_TOOL_SPECS = [
    {
        "name": "knowledge_source_import",
        "description": "Import files or text payloads into a managed workspace source area",
        "inputSchema": {
            "type": "object",
            "properties": {
                "workspace_id": {"type": "string"},
                "paths": {"type": "array", "items": {"type": "string"}},
                "texts": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "title": {"type": "string"},
                            "content": {"type": "string"},
                            "metadata": {"type": "object"},
                        },
                    },
                },
                "metadata": {"type": "object"},
            },
            "required": ["workspace_id"],
        },
    },
    {
        "name": "knowledge_source_list",
        "description": "List imported sources for a managed workspace",
        "inputSchema": {
            "type": "object",
            "properties": {
                "workspace_id": {"type": "string"},
                "status": {"type": "string", "enum": SOURCE_STATUSES},
                "limit": {"type": "integer", "default": 100},
            },
            "required": ["workspace_id"],
        },
    },
    {
        "name": "knowledge_source_remove",
        "description": "Soft-remove one imported source from a managed workspace",
        "inputSchema": {
            "type": "object",
            "properties": {
                "workspace_id": {"type": "string"},
                "source_id": {"type": "string"},
                "reason": {"type": "string"},
            },
            "required": ["workspace_id", "source_id"],
        },
    },
]


def handle_source_tool(
    name: str,
    arguments: dict[str, Any],
    *,
    blocked: Callable[..., dict[str, Any]],
    bounded_int: Callable[..., int],
    envelope: Callable[..., dict[str, Any]],
    ensure_workspace_meta: Callable[..., dict[str, Any]],
    now: Callable[[], str],
    read_json: Callable[[Path, Any], Any],
    resolve_workspace: Callable[[str | None, str | None], Path],
    sources_manifest_path: Callable[[Path], Path],
    write_json: Callable[[Path, Any], None],
) -> dict[str, Any]:
    if name == "knowledge_source_import":
        workspace_path = resolve_workspace(arguments.get("workspace_id"), None)
        meta = ensure_workspace_meta(workspace_path)
        if meta.get("status") == "archived":
            return envelope(
                workspace_id=meta["workspace_id"],
                status="blocked",
                warnings=["Workspace is archived and cannot import sources"],
                next_actions=["knowledge_workspace_describe"],
            )

        paths = list(arguments.get("paths") or [])
        texts = list(arguments.get("texts") or [])
        if len(paths) + len(texts) > MAX_IMPORT_FILES:
            return blocked(
                workspace_id=meta["workspace_id"],
                message=f"source import count must be between 0 and {MAX_IMPORT_FILES}",
                next_actions=["knowledge_source_import"],
            )

        try:
            validated_paths = validate_source_paths(paths, workspace=workspace_path)
        except ValueError as exc:
            return blocked(
                workspace_id=meta["workspace_id"],
                message=str(exc),
                next_actions=["knowledge_source_import"],
            )

        manifest = read_json(sources_manifest_path(workspace_path), {"items": []})
        existing_by_sha = {item.get("sha256"): item for item in manifest.get("items", []) if item.get("sha256")}
        imported_dir = workspace_path / "sources" / "imported"
        imported_dir.mkdir(parents=True, exist_ok=True)
        sources = []

        def add_source(*, title: str, content: bytes, suffix: str, original_path: str | None, metadata: dict) -> dict:
            if len(content) > MAX_IMPORT_FILE_BYTES:
                raise ValueError(f"source is larger than {MAX_IMPORT_FILE_BYTES} bytes")
            sha256 = hashlib.sha256(content).hexdigest()
            duplicate = existing_by_sha.get(sha256)
            if duplicate:
                result = dict(duplicate)
                result["status"] = "duplicate"
                return result
            source_id = f"src_{sha256[:16]}"
            filename = f"{source_id}{suffix if suffix else '.txt'}"
            target = imported_dir / filename
            target.write_bytes(content)
            record = {
                "source_id": source_id,
                "sha256": sha256,
                "title": title or source_id,
                "status": "active",
                "path": str(target),
                "original_path": original_path,
                "metadata": metadata,
                "imported_at": now(),
                "low_signal": {},
                "ingest_status": "pending",
            }
            manifest.setdefault("items", []).append(record)
            existing_by_sha[sha256] = record
            return record

        for raw_path in validated_paths:
            source_path = Path(raw_path)
            if not source_path.is_file():
                return blocked(
                    workspace_id=meta["workspace_id"],
                    message=f"Source path is not a file: {source_path}",
                    next_actions=["knowledge_source_import"],
                )
            if source_path.stat().st_size > MAX_IMPORT_FILE_BYTES:
                return blocked(
                    workspace_id=meta["workspace_id"],
                    message=f"source file is larger than {MAX_IMPORT_FILE_BYTES} bytes",
                    next_actions=["knowledge_source_import"],
                )
            record = add_source(
                title=source_path.stem,
                content=source_path.read_bytes(),
                suffix=source_path.suffix,
                original_path=str(source_path),
                metadata=dict(arguments.get("metadata") or {}),
            )
            sources.append(record)

        for text_record in texts:
            title = str((text_record or {}).get("title") or "text-source").strip()
            content_text = str((text_record or {}).get("content") or "")
            content = content_text.encode("utf-8")
            if len(content) > MAX_IMPORT_TEXT_BYTES:
                return blocked(
                    workspace_id=meta["workspace_id"],
                    message=f"text source is larger than {MAX_IMPORT_TEXT_BYTES} bytes",
                    next_actions=["knowledge_source_import"],
                )
            record = add_source(
                title=title,
                content=content,
                suffix=".md",
                original_path=None,
                metadata={**dict(arguments.get("metadata") or {}), **dict((text_record or {}).get("metadata") or {})},
            )
            sources.append(record)

        write_json(sources_manifest_path(workspace_path), manifest)
        payload_sources = [
            {
                "source_id": item["source_id"],
                "sha256": item["sha256"],
                "title": item["title"],
                "status": "duplicate" if item.get("status") == "duplicate" else "imported",
                "path": item.get("path"),
            }
            for item in sources
        ]
        return envelope(
            workspace_id=meta["workspace_id"],
            artifact_refs=[{"type": "source", "source_id": item["source_id"]} for item in payload_sources],
            next_actions=["knowledge_build_start", "knowledge_source_list"],
            data={"sources": payload_sources},
        )

    if name == "knowledge_source_list":
        workspace_path = resolve_workspace(arguments.get("workspace_id"), None)
        meta = ensure_workspace_meta(workspace_path)
        limit = bounded_int(arguments.get("limit"), default=100, minimum=1, maximum=500, field="limit")
        status_filter = arguments.get("status")
        manifest = read_json(sources_manifest_path(workspace_path), {"items": []})
        items = []
        for item in manifest.get("items", []):
            status = item.get("status", "active")
            if status_filter and status != status_filter:
                continue
            items.append(
                {
                    "source_id": item.get("source_id"),
                    "sha256": item.get("sha256"),
                    "title": item.get("title"),
                    "status": status,
                    "low_signal": item.get("low_signal", {}),
                    "ingest_status": item.get("ingest_status"),
                }
            )
            if len(items) >= limit:
                break
        return envelope(workspace_id=meta["workspace_id"], data={"items": items})

    if name == "knowledge_source_remove":
        workspace_path = resolve_workspace(arguments.get("workspace_id"), None)
        meta = ensure_workspace_meta(workspace_path)
        if meta.get("status") == "archived":
            return envelope(
                workspace_id=meta["workspace_id"],
                status="blocked",
                warnings=["Workspace is archived and cannot remove sources"],
                next_actions=["knowledge_workspace_describe"],
            )
        source_id = str(arguments.get("source_id") or "").strip()
        manifest = read_json(sources_manifest_path(workspace_path), {"items": []})
        updated = None
        for item in manifest.get("items", []):
            if item.get("source_id") == source_id:
                item["status"] = "removed"
                item["removed_at"] = now()
                item["remove_reason"] = str(arguments.get("reason") or "")
                updated = item
                break
        if updated is None:
            return blocked(
                workspace_id=meta["workspace_id"],
                message=f"Unknown source_id: {source_id}",
                next_actions=["knowledge_source_list"],
            )
        write_json(sources_manifest_path(workspace_path), manifest)
        return envelope(
            workspace_id=meta["workspace_id"],
            artifact_refs=[{"type": "source", "source_id": source_id}],
            next_actions=["knowledge_source_list"],
            data={"source": updated},
        )

    raise ValueError(f"Unknown source MCP tool: {name}")

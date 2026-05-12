"""Workspace runtime helpers used by the MCP server."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from .mcp_common import now, read_json, write_json
from .security import validate_workspace_path
from .service import DataService


class WorkspaceRuntime:
    def __init__(self, default_workspace: Path, *, workspace_root: Path | None = None) -> None:
        self.default_workspace = default_workspace
        self._workspace_root = workspace_root

    def workspace_root(self) -> Path:
        configured = os.getenv("DATA_SERVICE_WORKSPACE_ROOT", "").strip()
        root = self._workspace_root or (Path(configured).expanduser() if configured else self.default_workspace.parent)
        resolved = validate_workspace_path(root)
        resolved.mkdir(parents=True, exist_ok=True)
        return resolved

    @staticmethod
    def workspace_meta_path(workspace: Path) -> Path:
        return workspace / ".data_service_workspace.json"

    @staticmethod
    def lifecycle_dir(workspace: Path) -> Path:
        return workspace / "lifecycle"

    def sources_manifest_path(self, workspace: Path) -> Path:
        return self.lifecycle_dir(workspace) / "sources.json"

    def operations_dir(self, workspace: Path) -> Path:
        return self.lifecycle_dir(workspace) / "operations"

    def operation_path(self, workspace: Path, operation_id: str) -> Path:
        return self.operations_dir(workspace) / f"{operation_id}.json"

    def workspace_id_for_path(self, path: Path) -> str:
        meta = read_json(self.workspace_meta_path(path), {})
        if meta.get("workspace_id"):
            return str(meta["workspace_id"])
        return path.name

    def resolve_workspace(self, identifier: str | None = None, workspace: str | None = None) -> Path:
        if workspace:
            return validate_workspace_path(workspace)
        if identifier:
            root = self.workspace_root()
            candidate = validate_workspace_path(root / str(identifier))
            try:
                candidate.relative_to(root)
            except ValueError as exc:
                raise ValueError("workspace_id is outside DATA_SERVICE_WORKSPACE_ROOT") from exc
            return candidate
        raise ValueError("workspace_id or workspace is required")

    def ensure_workspace_meta(
        self,
        workspace: Path,
        *,
        name: str | None = None,
        owner: str | None = None,
        tags: list[str] | None = None,
    ) -> dict[str, Any]:
        workspace.mkdir(parents=True, exist_ok=True)
        service = DataService(workspace)
        service.ensure_layout()
        meta_path = self.workspace_meta_path(workspace)
        existing = read_json(meta_path, {})
        current_time = now()
        meta = {
            "workspace_id": existing.get("workspace_id") or self.workspace_id_for_path(workspace),
            "name": name or existing.get("name") or workspace.name,
            "workspace_path": str(workspace),
            "owner": owner if owner is not None else existing.get("owner"),
            "tags": list(tags if tags is not None else existing.get("tags", [])),
            "status": existing.get("status", "active"),
            "created_at": existing.get("created_at", current_time),
            "updated_at": current_time,
        }
        write_json(meta_path, meta)
        return meta

    def workspace_id_for_service(self, service: DataService) -> str:
        return self.workspace_id_for_path(service.workspace)

    def is_workspace_archived(self, workspace: Path) -> bool:
        meta = read_json(self.workspace_meta_path(workspace), {})
        return meta.get("status") == "archived"

    @staticmethod
    def layout_payload(service: DataService) -> dict[str, Any]:
        layout = service.layout
        return {
            "workspace": str(layout.workspace),
            "row_manifest": str(layout.row_manifest),
            "llmwiki": {
                "raw": str(layout.raw_dir),
                "readable": str(layout.readable_dir),
                "normalized": str(layout.normalized_dir),
                "pages": str(layout.llmwiki_pages_dir),
                "state": str(layout.llmwiki_state_dir),
            },
            "graphrag": {
                "input": str(layout.graphrag_input_dir),
                "cache": str(layout.graphrag_cache_dir),
                "state": str(layout.graphrag_state_dir),
            },
            "summary": str(layout.summary_dir),
            "quality": str(layout.quality_dir),
        }

"""Registry operations for V2 codebase assets."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from data_service.mcp_common import now, read_json, write_json

from .artifacts import codebase_json_path, read_index, root_path_hash, write_index
from .models import CodebaseAsset, CodebaseStatus, default_codebase_id, merge_scan_policy, normalize_codebase_id
from .security import validate_codebase_root


class CodebaseRegistry:
    def __init__(self, workspace: Path, *, workspace_id: str) -> None:
        self.workspace = Path(workspace).expanduser().resolve()
        self.workspace_id = workspace_id

    def import_codebase(
        self,
        *,
        path: str,
        codebase_id: str | None = None,
        name: str | None = None,
        metadata: dict[str, Any] | None = None,
        scan_policy: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        root_path = validate_codebase_root(path, workspace=self.workspace)
        if not root_path.exists():
            raise ValueError("CODEBASE_PATH_NOT_FOUND")
        if not root_path.is_dir():
            raise ValueError("CODEBASE_PATH_NOT_DIRECTORY")

        index = read_index(self.workspace)
        digest = root_path_hash(root_path)
        duplicate = self._find_by_root_hash(index, digest)
        requested_id = normalize_codebase_id(codebase_id) if codebase_id else None
        if duplicate:
            asset = self.describe(str(duplicate["codebase_id"]))
            if requested_id and requested_id != asset.codebase_id:
                raise ValueError("CODEBASE_ID_CONFLICT")
            return {"asset": asset, "created": False}

        resolved_codebase_id = requested_id or default_codebase_id(root_path)
        existing = self._find_by_codebase_id(index, resolved_codebase_id)
        if existing and existing.get("root_path_hash") != digest:
            raise ValueError("CODEBASE_ID_CONFLICT")

        current_time = now()
        asset = CodebaseAsset(
            workspace_id=self.workspace_id,
            codebase_id=resolved_codebase_id,
            name=str(name or root_path.name),
            root_path=str(root_path),
            status=CodebaseStatus.ACTIVE.value,
            created_at=current_time,
            updated_at=current_time,
            metadata=dict(metadata or {}),
            scan_policy=merge_scan_policy(scan_policy),
        )
        self._write_asset(asset)
        items = [item for item in index.get("items", []) if item.get("codebase_id") != resolved_codebase_id]
        items.append(
            {
                "codebase_id": asset.codebase_id,
                "name": asset.name,
                "status": asset.status,
                "root_path_hash": digest,
                "created_at": asset.created_at,
                "updated_at": asset.updated_at,
            }
        )
        index["schema_version"] = "v2.0"
        index["items"] = sorted(items, key=lambda item: str(item.get("codebase_id") or ""))
        write_index(self.workspace, index)
        return {"asset": asset, "created": True}

    def list_codebases(self, *, include_archived: bool = False, limit: int = 100) -> list[CodebaseAsset]:
        index = read_index(self.workspace)
        items: list[CodebaseAsset] = []
        for item in index.get("items", []):
            codebase_id = str(item.get("codebase_id") or "")
            if not codebase_id:
                continue
            try:
                asset = self.describe(codebase_id)
            except FileNotFoundError:
                continue
            if not include_archived and asset.status == CodebaseStatus.ARCHIVED.value:
                continue
            items.append(asset)
            if len(items) >= limit:
                break
        return items

    def describe(self, codebase_id: str) -> CodebaseAsset:
        normalized_id = normalize_codebase_id(codebase_id)
        path = codebase_json_path(self.workspace, normalized_id)
        if not path.exists():
            raise FileNotFoundError(normalized_id)
        return CodebaseAsset.from_dict(read_json(path, {}))

    def archive(self, codebase_id: str, *, reason: str = "") -> CodebaseAsset:
        asset = self.describe(codebase_id)
        current_time = now()
        asset.status = CodebaseStatus.ARCHIVED.value
        asset.archived_at = current_time
        asset.archive_reason = reason
        asset.updated_at = current_time
        self._write_asset(asset)

        index = read_index(self.workspace)
        for item in index.get("items", []):
            if item.get("codebase_id") == asset.codebase_id:
                item["status"] = asset.status
                item["updated_at"] = asset.updated_at
        write_index(self.workspace, index)
        return asset

    def _write_asset(self, asset: CodebaseAsset) -> None:
        write_json(codebase_json_path(self.workspace, asset.codebase_id), asset.to_dict())

    @staticmethod
    def _find_by_root_hash(index: dict[str, Any], digest: str) -> dict[str, Any] | None:
        for item in index.get("items", []):
            if item.get("root_path_hash") == digest:
                return dict(item)
        return None

    @staticmethod
    def _find_by_codebase_id(index: dict[str, Any], codebase_id: str) -> dict[str, Any] | None:
        for item in index.get("items", []):
            if item.get("codebase_id") == codebase_id:
                return dict(item)
        return None

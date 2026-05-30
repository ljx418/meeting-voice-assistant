"""Models for V2 codebase assets."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "v2.0"


class CodebaseStatus(str, Enum):
    ACTIVE = "active"
    ARCHIVED = "archived"
    BLOCKED = "blocked"
    MISSING_PATH = "missing_path"
    PERMISSION_DENIED = "permission_denied"


DEFAULT_SCAN_POLICY = {
    "respect_gitignore": True,
    "include": [],
    "exclude": [".git/**", ".venv/**", "node_modules/**", "dist/**", "build/**", "__pycache__/**"],
    "max_file_size_mb": 2,
    "binary_policy": "skip",
}


def normalize_codebase_id(value: str) -> str:
    normalized = re.sub(r"[^A-Za-z0-9._-]+", "-", str(value or "").strip()).strip("-")
    if not normalized:
        raise ValueError("codebase_id is required")
    if len(normalized) > 96:
        normalized = normalized[:96].rstrip("-._")
    if not normalized:
        raise ValueError("codebase_id is invalid")
    return normalized


def default_codebase_id(root_path: Path) -> str:
    return normalize_codebase_id(f"codebase_{root_path.name}")


def merge_scan_policy(scan_policy: dict[str, Any] | None) -> dict[str, Any]:
    merged = dict(DEFAULT_SCAN_POLICY)
    if scan_policy:
        for key, value in scan_policy.items():
            if key in DEFAULT_SCAN_POLICY:
                merged[key] = value
    return merged


@dataclass
class CodebaseAsset:
    workspace_id: str
    codebase_id: str
    name: str
    root_path: str
    status: str = CodebaseStatus.ACTIVE.value
    created_at: str = ""
    updated_at: str = ""
    archived_at: str | None = None
    archive_reason: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)
    scan_policy: dict[str, Any] = field(default_factory=lambda: dict(DEFAULT_SCAN_POLICY))
    schema_version: str = SCHEMA_VERSION

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "CodebaseAsset":
        return cls(
            schema_version=str(payload.get("schema_version") or SCHEMA_VERSION),
            workspace_id=str(payload.get("workspace_id") or ""),
            codebase_id=str(payload.get("codebase_id") or ""),
            name=str(payload.get("name") or payload.get("codebase_id") or ""),
            root_path=str(payload.get("root_path") or ""),
            status=str(payload.get("status") or CodebaseStatus.ACTIVE.value),
            created_at=str(payload.get("created_at") or ""),
            updated_at=str(payload.get("updated_at") or ""),
            archived_at=payload.get("archived_at"),
            archive_reason=str(payload.get("archive_reason") or ""),
            metadata=dict(payload.get("metadata") or {}),
            scan_policy=merge_scan_policy(dict(payload.get("scan_policy") or {})),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "workspace_id": self.workspace_id,
            "codebase_id": self.codebase_id,
            "name": self.name,
            "root_path": self.root_path,
            "status": self.status,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "archived_at": self.archived_at,
            "archive_reason": self.archive_reason,
            "metadata": self.metadata,
            "scan_policy": self.scan_policy,
        }

    def public_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "workspace_id": self.workspace_id,
            "codebase_id": self.codebase_id,
            "name": self.name,
            "status": self.status,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "archived_at": self.archived_at,
            "archive_reason": self.archive_reason,
            "metadata": self.metadata,
            "scan_policy": self.scan_policy,
        }


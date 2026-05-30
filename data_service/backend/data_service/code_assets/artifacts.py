"""Artifact paths for V2 codebase assets."""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

from data_service.mcp_common import read_json, write_json


def codebase_assets_dir(workspace: Path) -> Path:
    return workspace / "assets" / "codebase"


def codebase_index_path(workspace: Path) -> Path:
    return codebase_assets_dir(workspace) / "index.json"


def codebase_dir(workspace: Path, codebase_id: str) -> Path:
    return codebase_assets_dir(workspace) / codebase_id


def codebase_json_path(workspace: Path, codebase_id: str) -> Path:
    return codebase_dir(workspace, codebase_id) / "codebase.json"


def root_path_hash(root_path: Path | str) -> str:
    return hashlib.sha256(str(Path(root_path).expanduser().resolve()).encode("utf-8")).hexdigest()


def read_index(workspace: Path) -> dict[str, Any]:
    return read_json(codebase_index_path(workspace), {"schema_version": "v2.0", "items": []})


def write_index(workspace: Path, index: dict[str, Any]) -> None:
    write_json(codebase_index_path(workspace), index)


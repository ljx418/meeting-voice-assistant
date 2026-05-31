"""Artifact paths for V2 codebase assets."""

from __future__ import annotations

import hashlib
import json
import os
import threading
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


def snapshots_dir(workspace: Path, codebase_id: str) -> Path:
    return codebase_dir(workspace, codebase_id) / "snapshots"


def snapshot_dir(workspace: Path, codebase_id: str, snapshot_id: str) -> Path:
    return snapshots_dir(workspace, codebase_id) / snapshot_id


def snapshot_json_path(workspace: Path, codebase_id: str, snapshot_id: str) -> Path:
    return snapshot_dir(workspace, codebase_id, snapshot_id) / "snapshot.json"


def snapshot_files_path(workspace: Path, codebase_id: str, snapshot_id: str) -> Path:
    return snapshot_dir(workspace, codebase_id, snapshot_id) / "files.jsonl"


def snapshot_stats_path(workspace: Path, codebase_id: str, snapshot_id: str) -> Path:
    return snapshot_dir(workspace, codebase_id, snapshot_id) / "stats.json"


def snapshot_warnings_path(workspace: Path, codebase_id: str, snapshot_id: str) -> Path:
    return snapshot_dir(workspace, codebase_id, snapshot_id) / "warnings.jsonl"


def root_path_hash(root_path: Path | str) -> str:
    return hashlib.sha256(str(Path(root_path).expanduser().resolve()).encode("utf-8")).hexdigest()


def read_index(workspace: Path) -> dict[str, Any]:
    return read_json(codebase_index_path(workspace), {"schema_version": "v2.0", "items": []})


def write_index(workspace: Path, index: dict[str, Any]) -> None:
    write_json(codebase_index_path(workspace), index)


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.with_name(f".{path.name}.{os.getpid()}.{threading.get_ident()}.tmp")
    tmp_path.write_text("".join(f"{json.dumps(row, ensure_ascii=False)}\n" for row in rows), encoding="utf-8")
    os.replace(tmp_path, path)


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            rows.append(json.loads(line))
    return rows

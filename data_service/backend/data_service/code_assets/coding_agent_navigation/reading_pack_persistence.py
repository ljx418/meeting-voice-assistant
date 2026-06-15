"""Persistence helpers for V2.34 module reading packs."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from data_service.mcp_common import read_json, write_json

from .persistence import task_navigation_dir


def reading_packs_dir(workspace: Path, codebase_id: str) -> Path:
    return task_navigation_dir(workspace, codebase_id) / "reading_packs"


def token_ledgers_dir(workspace: Path, codebase_id: str) -> Path:
    return task_navigation_dir(workspace, codebase_id) / "token_ledgers"


def reading_pack_json_path(workspace: Path, codebase_id: str, pack_id: str) -> Path:
    return reading_packs_dir(workspace, codebase_id) / f"{pack_id}.json"


def reading_pack_markdown_path(workspace: Path, codebase_id: str, pack_id: str) -> Path:
    return reading_packs_dir(workspace, codebase_id) / f"{pack_id}.md"


def token_ledger_path(workspace: Path, codebase_id: str, pack_id: str) -> Path:
    return token_ledgers_dir(workspace, codebase_id) / f"{pack_id}.json"


def reading_pack_artifact_refs(codebase_id: str, pack_id: str) -> list[dict[str, str]]:
    return [
        {"type": "module_reading_pack", "artifact_ref": f"coding-agent://{codebase_id}/task_navigation/reading_packs/{pack_id}.json"},
        {"type": "module_reading_pack_markdown", "artifact_ref": f"coding-agent://{codebase_id}/task_navigation/reading_packs/{pack_id}.md"},
        {"type": "token_ledger", "artifact_ref": f"coding-agent://{codebase_id}/task_navigation/token_ledgers/{pack_id}.json"},
    ]


def write_reading_pack(workspace: Path, codebase_id: str, pack: dict[str, Any], markdown: str, ledger: dict[str, Any]) -> None:
    pack_id = str(pack["pack_id"])
    write_json(reading_pack_json_path(workspace, codebase_id, pack_id), pack)
    path = reading_pack_markdown_path(workspace, codebase_id, pack_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(markdown, encoding="utf-8")
    write_json(token_ledger_path(workspace, codebase_id, pack_id), ledger)


def read_reading_pack(workspace: Path, codebase_id: str, pack_id: str) -> tuple[dict[str, Any], str, dict[str, Any]]:
    pack = read_json(reading_pack_json_path(workspace, codebase_id, pack_id), None)
    ledger = read_json(token_ledger_path(workspace, codebase_id, pack_id), None)
    md_path = reading_pack_markdown_path(workspace, codebase_id, pack_id)
    if not pack or not ledger or not md_path.exists():
        raise FileNotFoundError("READING_PACK_NOT_FOUND")
    return pack, md_path.read_text(encoding="utf-8"), ledger

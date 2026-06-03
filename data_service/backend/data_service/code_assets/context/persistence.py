"""Persistence helpers for V2 agent context packs."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from data_service.mcp_common import read_json, write_json

from ..artifacts import agent_context_dir, agent_context_path


def context_artifact_refs(codebase_id: str, pack_id: str) -> list[dict[str, str]]:
    return [{"type": "agent_context_pack", "artifact_ref": f"agent-context://{codebase_id}/{pack_id}"}]


def write_context_pack(workspace: Path, codebase_id: str, pack_id: str, payload: dict[str, Any]) -> None:
    agent_context_dir(workspace, codebase_id).mkdir(parents=True, exist_ok=True)
    write_json(agent_context_path(workspace, codebase_id, pack_id), payload)


def read_context_pack(workspace: Path, codebase_id: str, pack_id: str) -> dict[str, Any]:
    payload = read_json(agent_context_path(workspace, codebase_id, pack_id), None)
    if not payload:
        raise FileNotFoundError("CONTEXT_PACK_NOT_FOUND")
    return payload

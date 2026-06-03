"""Persistence helpers for V2.1 Code Graph."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from data_service.mcp_common import read_json, write_json

from ..artifacts import (
    code_graph_edges_path,
    code_graph_json_path,
    code_graph_mermaid_path,
    code_graph_nodes_path,
    code_graph_summary_path,
    read_jsonl,
    write_jsonl,
)


def graph_artifact_refs(codebase_id: str) -> list[dict[str, str]]:
    return [
        {"type": "code_graph", "artifact_ref": f"code-graph://{codebase_id}/graph.json"},
        {"type": "code_graph_nodes", "artifact_ref": f"code-graph://{codebase_id}/nodes.jsonl"},
        {"type": "code_graph_edges", "artifact_ref": f"code-graph://{codebase_id}/edges.jsonl"},
        {"type": "code_graph_summary", "artifact_ref": f"code-graph://{codebase_id}/summary.json"},
        {"type": "code_graph_mermaid", "artifact_ref": f"code-graph://{codebase_id}/mermaid/project.mmd"},
    ]


def write_graph(workspace: Path, codebase_id: str, graph: dict[str, Any], mermaid: str) -> None:
    write_json(code_graph_json_path(workspace, codebase_id), graph)
    write_jsonl(code_graph_nodes_path(workspace, codebase_id), graph["nodes"])
    write_jsonl(code_graph_edges_path(workspace, codebase_id), graph["edges"])
    write_json(code_graph_summary_path(workspace, codebase_id), graph["summary"])
    path = code_graph_mermaid_path(workspace, codebase_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(mermaid, encoding="utf-8")


def read_graph(workspace: Path, codebase_id: str) -> dict[str, Any]:
    payload = read_json(code_graph_json_path(workspace, codebase_id), None)
    if not payload:
        raise FileNotFoundError("CODE_GRAPH_NOT_FOUND")
    return payload


def read_nodes(workspace: Path, codebase_id: str) -> list[dict[str, Any]]:
    return read_jsonl(code_graph_nodes_path(workspace, codebase_id))


def read_edges(workspace: Path, codebase_id: str) -> list[dict[str, Any]]:
    return read_jsonl(code_graph_edges_path(workspace, codebase_id))


def read_summary(workspace: Path, codebase_id: str) -> dict[str, Any]:
    payload = read_json(code_graph_summary_path(workspace, codebase_id), None)
    if not payload:
        raise FileNotFoundError("CODE_GRAPH_NOT_FOUND")
    return payload


def read_mermaid(workspace: Path, codebase_id: str) -> str:
    path = code_graph_mermaid_path(workspace, codebase_id)
    if not path.exists():
        raise FileNotFoundError("CODE_GRAPH_NOT_FOUND")
    return path.read_text(encoding="utf-8")

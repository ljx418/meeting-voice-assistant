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


def inventory_surfaces_path(workspace: Path, codebase_id: str, snapshot_id: str) -> Path:
    return snapshot_dir(workspace, codebase_id, snapshot_id) / "surfaces.jsonl"


def inventory_capabilities_path(workspace: Path, codebase_id: str, snapshot_id: str) -> Path:
    return snapshot_dir(workspace, codebase_id, snapshot_id) / "capabilities.jsonl"


def inventory_alignment_path(workspace: Path, codebase_id: str, snapshot_id: str) -> Path:
    return snapshot_dir(workspace, codebase_id, snapshot_id) / "alignment_matrix.json"


def inventory_summary_path(workspace: Path, codebase_id: str, snapshot_id: str) -> Path:
    return snapshot_dir(workspace, codebase_id, snapshot_id) / "inventory_summary.json"


def symbols_path(workspace: Path, codebase_id: str, snapshot_id: str) -> Path:
    return snapshot_dir(workspace, codebase_id, snapshot_id) / "symbols.jsonl"


def imports_path(workspace: Path, codebase_id: str, snapshot_id: str) -> Path:
    return snapshot_dir(workspace, codebase_id, snapshot_id) / "imports.jsonl"


def symbol_summary_path(workspace: Path, codebase_id: str, snapshot_id: str) -> Path:
    return snapshot_dir(workspace, codebase_id, snapshot_id) / "symbol_summary.json"


def mappings_path(workspace: Path, codebase_id: str, snapshot_id: str) -> Path:
    return snapshot_dir(workspace, codebase_id, snapshot_id) / "mappings.jsonl"


def evidence_path(workspace: Path, codebase_id: str, snapshot_id: str) -> Path:
    return snapshot_dir(workspace, codebase_id, snapshot_id) / "evidence.jsonl"


def mapping_summary_path(workspace: Path, codebase_id: str, snapshot_id: str) -> Path:
    return snapshot_dir(workspace, codebase_id, snapshot_id) / "mapping_summary.json"


def trace_index_path(workspace: Path, codebase_id: str, snapshot_id: str) -> Path:
    return snapshot_dir(workspace, codebase_id, snapshot_id) / "trace_index.json"


def overview_path(workspace: Path, codebase_id: str) -> Path:
    return codebase_dir(workspace, codebase_id) / "overview.json"


def agent_context_dir(workspace: Path, codebase_id: str) -> Path:
    return codebase_dir(workspace, codebase_id) / "agent_context"


def agent_context_path(workspace: Path, codebase_id: str, pack_id: str) -> Path:
    return agent_context_dir(workspace, codebase_id) / f"{pack_id}.json"


def devwiki_dir(workspace: Path, codebase_id: str) -> Path:
    return codebase_dir(workspace, codebase_id) / "devwiki"


def devwiki_index_path(workspace: Path, codebase_id: str) -> Path:
    return devwiki_dir(workspace, codebase_id) / "index.json"


def devwiki_pages_dir(workspace: Path, codebase_id: str) -> Path:
    return devwiki_dir(workspace, codebase_id) / "pages"


def devwiki_page_json_path(workspace: Path, codebase_id: str, page_slug: str) -> Path:
    return devwiki_pages_dir(workspace, codebase_id) / f"{page_slug}.json"


def devwiki_page_markdown_path(workspace: Path, codebase_id: str, page_slug: str) -> Path:
    return devwiki_pages_dir(workspace, codebase_id) / f"{page_slug}.md"


def code_graph_dir(workspace: Path, codebase_id: str) -> Path:
    return codebase_dir(workspace, codebase_id) / "graph"


def code_graph_json_path(workspace: Path, codebase_id: str) -> Path:
    return code_graph_dir(workspace, codebase_id) / "graph.json"


def code_graph_nodes_path(workspace: Path, codebase_id: str) -> Path:
    return code_graph_dir(workspace, codebase_id) / "nodes.jsonl"


def code_graph_edges_path(workspace: Path, codebase_id: str) -> Path:
    return code_graph_dir(workspace, codebase_id) / "edges.jsonl"


def code_graph_summary_path(workspace: Path, codebase_id: str) -> Path:
    return code_graph_dir(workspace, codebase_id) / "summary.json"


def code_graph_mermaid_dir(workspace: Path, codebase_id: str) -> Path:
    return code_graph_dir(workspace, codebase_id) / "mermaid"


def code_graph_mermaid_path(workspace: Path, codebase_id: str, name: str = "project") -> Path:
    return code_graph_mermaid_dir(workspace, codebase_id) / f"{name}.mmd"


def code_quality_dir(workspace: Path, codebase_id: str) -> Path:
    return codebase_dir(workspace, codebase_id) / "quality"


def code_quality_feedback_path(workspace: Path, codebase_id: str) -> Path:
    return code_quality_dir(workspace, codebase_id) / "feedback.jsonl"


def code_quality_rules_path(workspace: Path, codebase_id: str) -> Path:
    return code_quality_dir(workspace, codebase_id) / "rules.jsonl"


def code_quality_reviews_path(workspace: Path, codebase_id: str) -> Path:
    return code_quality_dir(workspace, codebase_id) / "reviews.jsonl"


def code_quality_plan_path(workspace: Path, codebase_id: str) -> Path:
    return code_quality_dir(workspace, codebase_id) / "plan.json"


def code_quality_summary_path(workspace: Path, codebase_id: str) -> Path:
    return code_quality_dir(workspace, codebase_id) / "summary.json"


def architecture_dir(workspace: Path, codebase_id: str) -> Path:
    return codebase_dir(workspace, codebase_id) / "architecture"


def architecture_sources_path(workspace: Path, codebase_id: str) -> Path:
    return architecture_dir(workspace, codebase_id) / "sources.jsonl"


def architecture_design_nodes_path(workspace: Path, codebase_id: str) -> Path:
    return architecture_dir(workspace, codebase_id) / "design_nodes.jsonl"


def architecture_design_edges_path(workspace: Path, codebase_id: str) -> Path:
    return architecture_dir(workspace, codebase_id) / "design_edges.jsonl"


def architecture_model_path(workspace: Path, codebase_id: str) -> Path:
    return architecture_dir(workspace, codebase_id) / "model.json"


def architecture_alignment_path(workspace: Path, codebase_id: str) -> Path:
    return architecture_dir(workspace, codebase_id) / "alignment.json"


def architecture_findings_path(workspace: Path, codebase_id: str) -> Path:
    return architecture_dir(workspace, codebase_id) / "findings.jsonl"


def architecture_summary_path(workspace: Path, codebase_id: str) -> Path:
    return architecture_dir(workspace, codebase_id) / "summary.json"


def architecture_code_roles_path(workspace: Path, codebase_id: str) -> Path:
    return architecture_dir(workspace, codebase_id) / "code_roles.jsonl"


def architecture_code_layers_path(workspace: Path, codebase_id: str) -> Path:
    return architecture_dir(workspace, codebase_id) / "code_layers.jsonl"


def architecture_code_boundaries_path(workspace: Path, codebase_id: str) -> Path:
    return architecture_dir(workspace, codebase_id) / "code_boundaries.jsonl"


def architecture_pattern_candidates_path(workspace: Path, codebase_id: str) -> Path:
    return architecture_dir(workspace, codebase_id) / "pattern_candidates.jsonl"


def architecture_code_derived_model_path(workspace: Path, codebase_id: str) -> Path:
    return architecture_dir(workspace, codebase_id) / "code_derived_model.json"


def architecture_design_code_drift_path(workspace: Path, codebase_id: str) -> Path:
    return architecture_dir(workspace, codebase_id) / "design_code_drift.jsonl"


def architecture_views_dir(workspace: Path, codebase_id: str) -> Path:
    return architecture_dir(workspace, codebase_id) / "views"


def architecture_view_path(workspace: Path, codebase_id: str, view_id: str) -> Path:
    suffix = "html" if view_id.endswith(".html") else "mmd"
    name = view_id.rsplit(".", 1)[0]
    return architecture_views_dir(workspace, codebase_id) / f"{name}.{suffix}"


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

"""Persistence helpers for V2.36 task navigation closure artifacts."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from data_service.mcp_common import read_json, write_json

from .persistence import task_navigation_dir


def reports_dir(workspace: Path, codebase_id: str) -> Path:
    return task_navigation_dir(workspace, codebase_id) / "reports"


def closure_report_path(workspace: Path, codebase_id: str) -> Path:
    return reports_dir(workspace, codebase_id) / "task_navigation_report.json"


def closure_html_path(workspace: Path, codebase_id: str) -> Path:
    return reports_dir(workspace, codebase_id) / "task_navigation_report.html"


def closure_mermaid_path(workspace: Path, codebase_id: str) -> Path:
    return reports_dir(workspace, codebase_id) / "task_navigation_graph.mmd"


def closure_coverage_path(workspace: Path, codebase_id: str) -> Path:
    return task_navigation_dir(workspace, codebase_id) / "coverage_matrix.json"


def closure_governance_path(workspace: Path, codebase_id: str) -> Path:
    return task_navigation_dir(workspace, codebase_id) / "governance_targets.json"


def closure_audit_path(workspace: Path, codebase_id: str) -> Path:
    return task_navigation_dir(workspace, codebase_id) / "closure_audit_report.json"


def closure_artifact_refs(codebase_id: str) -> list[dict[str, str]]:
    return [
        {"type": "task_navigation_report", "artifact_ref": f"coding-agent://{codebase_id}/task_navigation/reports/task_navigation_report.json"},
        {"type": "task_navigation_report_html", "artifact_ref": f"coding-agent://{codebase_id}/task_navigation/reports/task_navigation_report.html"},
        {"type": "task_navigation_graph_mermaid", "artifact_ref": f"coding-agent://{codebase_id}/task_navigation/reports/task_navigation_graph.mmd"},
        {"type": "task_navigation_coverage_matrix", "artifact_ref": f"coding-agent://{codebase_id}/task_navigation/coverage_matrix.json"},
        {"type": "task_navigation_governance_targets", "artifact_ref": f"coding-agent://{codebase_id}/task_navigation/governance_targets.json"},
        {"type": "task_navigation_closure_audit", "artifact_ref": f"coding-agent://{codebase_id}/task_navigation/closure_audit_report.json"},
    ]


def write_closure_bundle(
    workspace: Path,
    codebase_id: str,
    report: dict[str, Any],
    html: str,
    mermaid: str,
    coverage: dict[str, Any],
    governance: dict[str, Any],
    audit: dict[str, Any],
) -> None:
    write_json(closure_report_path(workspace, codebase_id), report)
    write_json(closure_coverage_path(workspace, codebase_id), coverage)
    write_json(closure_governance_path(workspace, codebase_id), governance)
    write_json(closure_audit_path(workspace, codebase_id), audit)
    html_path = closure_html_path(workspace, codebase_id)
    html_path.parent.mkdir(parents=True, exist_ok=True)
    html_path.write_text(html, encoding="utf-8")
    closure_mermaid_path(workspace, codebase_id).write_text(mermaid, encoding="utf-8")


def read_closure_bundle(workspace: Path, codebase_id: str) -> tuple[dict[str, Any], str, str, dict[str, Any], dict[str, Any], dict[str, Any]]:
    report = read_json(closure_report_path(workspace, codebase_id), None)
    coverage = read_json(closure_coverage_path(workspace, codebase_id), None)
    governance = read_json(closure_governance_path(workspace, codebase_id), None)
    audit = read_json(closure_audit_path(workspace, codebase_id), None)
    html_path = closure_html_path(workspace, codebase_id)
    mermaid_path = closure_mermaid_path(workspace, codebase_id)
    if not report or not coverage or not governance or not audit or not html_path.exists() or not mermaid_path.exists():
        raise FileNotFoundError("TASK_NAVIGATION_CLOSURE_NOT_BUILT")
    return report, html_path.read_text(encoding="utf-8"), mermaid_path.read_text(encoding="utf-8"), coverage, governance, audit

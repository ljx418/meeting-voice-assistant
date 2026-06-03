"""Architecture alignment findings for V2.3."""

from __future__ import annotations

from typing import Any

from .model import ARCHITECTURE_SCHEMA_VERSION, stable_id


def build_findings(*, workspace_id: str, codebase_id: str, snapshot_id: str, design_nodes: list[dict[str, Any]], alignment: dict[str, Any]) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    design_by_id = {item["node_id"]: item for item in design_nodes}
    for item in alignment.get("unmatched_design", []):
        design = design_by_id.get(str(item.get("design_node_id")), {})
        findings.append(_finding(workspace_id, codebase_id, snapshot_id, "DESIGNED_NOT_FOUND_IN_CODE", target_id=str(item.get("design_node_id")), title=f"Design node has no code evidence: {item.get('label')}", severity="medium", evidence=design.get("evidence", []), needs_review=item.get("needs_review", [])))
    for item in design_nodes:
        if item.get("node_type") == "ForbiddenClaim":
            findings.append(_finding(workspace_id, codebase_id, snapshot_id, "UNSUPPORTED_CLAIM", target_id=item["node_id"], title=f"Forbidden architecture claim captured: {item.get('label')}", severity="high", evidence=item.get("evidence", []), needs_review=[{"code": "FORBIDDEN_CLAIM_REVIEW", "reason": "Forbidden or no-false-green architecture statement must remain visible."}]))
    for item in alignment.get("matches", []):
        if float(item.get("confidence") or 0) < 0.75:
            findings.append(_finding(workspace_id, codebase_id, snapshot_id, "LOW_CONFIDENCE_MAPPING", target_id=str(item.get("alignment_id")), title=f"Low confidence design-code mapping: {item.get('design_label')} -> {item.get('code_label')}", severity="low", evidence=item.get("evidence", []), needs_review=item.get("needs_review", [])))
    return findings


def _finding(workspace_id: str, codebase_id: str, snapshot_id: str, finding_type: str, *, target_id: str, title: str, severity: str, evidence: list[dict[str, Any]], needs_review: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "schema_version": ARCHITECTURE_SCHEMA_VERSION,
        "workspace_id": workspace_id,
        "codebase_id": codebase_id,
        "snapshot_id": snapshot_id,
        "finding_id": stable_id("archfinding", snapshot_id, finding_type, target_id),
        "finding_type": finding_type,
        "target_id": target_id,
        "title": title,
        "severity": severity,
        "evidence": list(evidence or []),
        "needs_review": list(needs_review or []),
        "confidence": 0.8,
    }

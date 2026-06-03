"""Design-code drift analysis for V2.4 architecture inference."""

from __future__ import annotations

import re
from typing import Any

from .model import stable_id


def build_design_code_drift(
    *,
    workspace_id: str,
    codebase_id: str,
    snapshot_id: str,
    design_nodes: list[dict[str, Any]],
    code_model: dict[str, Any],
) -> list[dict[str, Any]]:
    code_items = _code_items(code_model)
    findings: list[dict[str, Any]] = []
    if not design_nodes:
        return []
    matched_code_ids: set[str] = set()
    for node in design_nodes:
        label = str(node.get("label") or "")
        node_tokens = _tokens(label)
        matches = [(item, _overlap(node_tokens, item["tokens"])) for item in code_items]
        matches = [(item, score) for item, score in matches if score > 0]
        if not matches:
            findings.append(_finding(workspace_id, codebase_id, snapshot_id, "DESIGN_LAYER_MISSING_CODE", "medium", design_ref=_design_ref(node), code_ref=None, evidence=list(node.get("evidence") or []), confidence=0.7, needs_review=[{"reason": "no_code_token_match"}]))
            continue
        best, score = max(matches, key=lambda pair: pair[1])
        matched_code_ids.add(str(best["id"]))
        if score < 0.35:
            findings.append(_finding(workspace_id, codebase_id, snapshot_id, "LOW_CONFIDENCE_ROLE", "low", design_ref=_design_ref(node), code_ref=best["ref"], evidence=[*(node.get("evidence") or []), *best["evidence"][:3]], confidence=0.45, needs_review=[{"reason": "weak_design_code_token_overlap", "score": score}]))
    for item in code_items:
        if str(item["id"]) in matched_code_ids:
            continue
        if item["kind"] == "pattern":
            finding_type = "PATTERN_WITHOUT_DESIGN"
        else:
            finding_type = "CODE_LAYER_NOT_IN_DESIGN"
        findings.append(_finding(workspace_id, codebase_id, snapshot_id, finding_type, "low", design_ref=None, code_ref=item["ref"], evidence=item["evidence"][:5], confidence=0.55, needs_review=[{"reason": "code_item_not_matched_to_design"}]))
        if len(findings) >= 500:
            break
    return findings


def _code_items(code_model: dict[str, Any]) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for role in code_model.get("roles") or []:
        if float(role.get("confidence") or 0) < 0.8:
            continue
        items.append({"id": role.get("role_id"), "kind": "role", "tokens": _tokens(" ".join(str(role.get(key) or "") for key in ("role_type", "name", "path"))), "evidence": list(role.get("evidence") or []), "ref": {"type": "role", "id": role.get("role_id"), "role_type": role.get("role_type"), "path": role.get("path")}})
    for pattern in code_model.get("patterns") or []:
        if float(pattern.get("confidence") or 0) < 0.8:
            continue
        items.append({"id": pattern.get("pattern_id"), "kind": "pattern", "tokens": _tokens(" ".join(str(pattern.get(key) or "") for key in ("pattern_type", "name"))), "evidence": list(pattern.get("evidence") or []), "ref": {"type": "pattern", "id": pattern.get("pattern_id"), "pattern_type": pattern.get("pattern_type")}})
    return items


def _finding(workspace_id: str, codebase_id: str, snapshot_id: str, finding_type: str, severity: str, design_ref: dict[str, Any] | None, code_ref: dict[str, Any] | None, evidence: list[dict[str, Any]], confidence: float, needs_review: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "schema_version": "v2.4",
        "workspace_id": workspace_id,
        "codebase_id": codebase_id,
        "snapshot_id": snapshot_id,
        "finding_id": stable_id("archdrift", snapshot_id, finding_type, design_ref, code_ref),
        "finding_type": finding_type,
        "severity": severity,
        "design_ref": design_ref,
        "code_ref": code_ref,
        "evidence": list(evidence),
        "confidence": float(confidence),
        "needs_review": list(needs_review),
        "recommendation": "Review design-code alignment before treating this as an architecture fact.",
    }


def _design_ref(node: dict[str, Any]) -> dict[str, Any]:
    return {"type": "design_node", "id": node.get("node_id"), "node_type": node.get("node_type"), "label": node.get("label"), "source_path": node.get("source_path")}


def _tokens(value: str) -> set[str]:
    return {token for token in re.split(r"[^a-zA-Z0-9_]+", value.lower()) if len(token) >= 3}


def _overlap(left: set[str], right: set[str]) -> float:
    if not left or not right:
        return 0.0
    return len(left & right) / max(1, len(left | right))

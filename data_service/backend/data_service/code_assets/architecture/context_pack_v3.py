"""V2.9 architecture context pack v3."""

from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from typing import Any


SCHEMA_VERSION = "v2.9"
VALID_MODES = {"project_brief", "task_context", "architecture_review"}
VALID_ROLES = {"maintainer", "coding_agent", "documentation_agent", "architecture_reviewer"}


def build_architecture_context_pack_v3(
    *,
    workspace_id: str,
    codebase_id: str,
    snapshot_id: str,
    mode: str,
    role: str,
    task: str | None,
    max_tokens: int,
    public_surface_evidence: dict[str, Any],
    relationships: dict[str, Any],
    ranking: dict[str, Any],
    human_report: dict[str, Any],
    artifact_refs: list[dict[str, str]],
) -> dict[str, Any]:
    mode = mode if mode in VALID_MODES else "project_brief"
    role = role if role in VALID_ROLES else "maintainer"
    recommendations = _recommendations(mode, role, public_surface_evidence, relationships, ranking, task)
    omitted_items: list[dict[str, Any]] = []
    if max_tokens < 900 and len(recommendations) > 3:
        for item in recommendations[3:]:
            omitted_items.append({"item_id": item["recommendation_id"], "reason": "TOKEN_BUDGET_LOW", "preserved_evidence": bool(item.get("evidence_refs"))})
        recommendations = recommendations[:3]
    token_estimate = _estimate_tokens(recommendations, human_report)
    sections = _sections(mode, role, public_surface_evidence, relationships, ranking, human_report, recommendations)
    pack_id = _stable_id("context-pack-v3", workspace_id, codebase_id, snapshot_id, mode, role, str(task or ""), str(max_tokens))
    pack = {
        "schema_version": SCHEMA_VERSION,
        "workspace_id": workspace_id,
        "codebase_id": codebase_id,
        "snapshot_id": snapshot_id,
        "pack_id": pack_id,
        "mode": mode,
        "role": role,
        "task": task,
        "max_tokens": max_tokens,
        "token_estimate": min(token_estimate, max_tokens + 200),
        "source_phase_refs": [63, 64, 65, 66],
        "sections": sections,
        "recommendations": recommendations,
        "omitted_items": omitted_items,
        "warnings": _warnings(public_surface_evidence, ranking),
        "content": _markdown_content(mode, role, sections, recommendations, omitted_items),
        "source_artifact_refs": artifact_refs,
        "artifact_refs": artifact_refs,
        "created_at": _now(),
    }
    _ensure_recommendation_evidence_policy(pack)
    return pack


def public_architecture_context_pack_v3_payload(payload: dict[str, Any], artifact_refs: list[dict[str, str]]) -> dict[str, Any]:
    pack = dict(payload)
    pack["recommendations"] = list(pack.get("recommendations", []))[:80]
    pack["sections"] = list(pack.get("sections", []))[:20]
    pack["artifact_refs"] = artifact_refs
    return {"schema_version": SCHEMA_VERSION, "architecture_context_pack_v3": pack, "artifact_refs": artifact_refs}


def _recommendations(
    mode: str,
    role: str,
    evidence_payload: dict[str, Any],
    relationship_payload: dict[str, Any],
    ranking_payload: dict[str, Any],
    task: str | None,
) -> list[dict[str, Any]]:
    ranking_items = list(((ranking_payload.get("ranking") or {}).get("items") or []))
    evidence_rows = list(evidence_payload.get("evidence") or [])
    relationships = list(relationship_payload.get("relationships") or [])
    recs = []
    for item in ranking_items[:12]:
        recs.append(
            {
                "recommendation_id": _stable_id("rec-v3", item.get("ranking_id") or item.get("source_id") or ""),
                "kind": "review_signal",
                "label": item.get("label") or "Review architecture signal",
                "priority": "p0" if item.get("severity") == "fatal" else "p1" if item.get("severity") == "major" else "p2",
                "reason_codes": item.get("reason_codes") or [],
                "evidence_refs": item.get("evidence_refs") or [],
                "needs_review": item.get("needs_review") or ([] if item.get("evidence_refs") else [{"code": "RECOMMENDATION_EVIDENCE_MISSING", "reason": "Recommendation has no direct evidence ref."}]),
            }
        )
    accepted = [item for item in evidence_rows if item.get("status") == "accepted"]
    if accepted:
        recs.insert(
            0,
            {
                "recommendation_id": _stable_id("rec-v3", "entrypoints", accepted[0].get("evidence_id") or ""),
                "kind": "entrypoint_map",
                "label": f"Start from {len(accepted)} accepted public-surface evidence rows before changing architecture-facing behavior.",
                "priority": "p1" if mode == "task_context" else "p2",
                "reason_codes": ["PUBLIC_SURFACE_EVIDENCE_AVAILABLE"],
                "evidence_refs": accepted[0].get("evidence_refs") or [],
                "needs_review": [],
            },
        )
    if relationships:
        first = relationships[0]
        recs.append(
            {
                "recommendation_id": _stable_id("rec-v3", "relationships", first.get("relationship_id") or ""),
                "kind": "relationship_path",
                "label": "Use V2.9 relationship paths as implementation hints, not runtime call claims.",
                "priority": "p2",
                "reason_codes": ["SHALLOW_RELATIONSHIP_LAYER"],
                "evidence_refs": first.get("evidence_refs") or [],
                "needs_review": first.get("needs_review") or ([] if first.get("evidence_refs") else [{"code": "RELATIONSHIP_HINT_ONLY", "reason": "Relationship has no direct evidence and must stay reviewable."}]),
            }
        )
    if not recs:
        recs.append(
            {
                "recommendation_id": _stable_id("rec-v3", "empty", mode, role, str(task or "")),
                "kind": "needs_review",
                "label": "V2.9 artifacts are unavailable or empty; build public-surface evidence and relationships first.",
                "priority": "p1",
                "reason_codes": ["V29_ARTIFACTS_EMPTY"],
                "evidence_refs": [],
                "needs_review": [{"code": "V29_ARTIFACTS_EMPTY", "reason": "No evidence-backed recommendation can be produced."}],
            }
        )
    return recs


def _sections(
    mode: str,
    role: str,
    evidence_payload: dict[str, Any],
    relationship_payload: dict[str, Any],
    ranking_payload: dict[str, Any],
    human_report: dict[str, Any],
    recommendations: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    return [
        {"section_id": "project_brief", "title": "Project brief", "content": (human_report.get("report", {}).get("sections", {}).get("executive_summary") or {}).get("one_liner") or "No report summary available."},
        {"section_id": "evidence_summary", "title": "Evidence summary", "content": evidence_payload.get("summary") or {}},
        {"section_id": "relationship_summary", "title": "Relationship summary", "content": relationship_payload.get("summary") or {}},
        {"section_id": "ranking_summary", "title": "Ranking summary", "content": (ranking_payload.get("ranking") or {}).get("summary") or {}},
        {"section_id": "recommendations", "title": f"Recommendations for {role}/{mode}", "content": recommendations},
    ]


def _warnings(evidence_payload: dict[str, Any], ranking_payload: dict[str, Any]) -> list[dict[str, str]]:
    warnings = []
    if (evidence_payload.get("summary") or {}).get("accepted_count", 0) == 0:
        warnings.append({"code": "NO_ACCEPTED_PUBLIC_SURFACE_EVIDENCE", "reason": "Context pack has no accepted line-level public-surface evidence."})
    ranking_summary = (ranking_payload.get("ranking") or {}).get("summary") or {}
    if ranking_summary.get("hidden_major_count", 0) or ranking_summary.get("hidden_fatal_count", 0):
        warnings.append({"code": "MAJOR_FATAL_HIDDEN", "reason": "Ranking summary reports hidden major/fatal signals."})
    return warnings


def _markdown_content(mode: str, role: str, sections: list[dict[str, Any]], recommendations: list[dict[str, Any]], omitted_items: list[dict[str, Any]]) -> str:
    lines = [f"# Architecture Context Pack v3", "", f"Mode: `{mode}`", f"Role: `{role}`", ""]
    for section in sections:
        lines.append(f"## {section['title']}")
        content = section.get("content")
        if isinstance(content, list):
            for item in content[:20]:
                lines.append(f"- {item.get('label') or item}")
        elif isinstance(content, dict):
            for key, value in list(content.items())[:16]:
                lines.append(f"- `{key}`: {value}")
        else:
            lines.append(str(content))
        lines.append("")
    lines.append("## Evidence policy")
    lines.append("Every recommendation is evidence-backed or explicitly marked needs_review.")
    if omitted_items:
        lines.append("")
        lines.append("## Omitted items")
        for item in omitted_items:
            lines.append(f"- {item['item_id']}: {item['reason']}")
    return "\n".join(lines)


def _estimate_tokens(recommendations: list[dict[str, Any]], human_report: dict[str, Any]) -> int:
    return 450 + len(recommendations) * 90 + len(str((human_report.get("report") or {}).get("summary") or {})) // 4


def _ensure_recommendation_evidence_policy(pack: dict[str, Any]) -> None:
    for item in pack.get("recommendations", []):
        if item.get("evidence_refs") or item.get("needs_review"):
            continue
        item["needs_review"] = [{"code": "RECOMMENDATION_EVIDENCE_MISSING", "reason": "Recommendation has no evidence after token trimming."}]


def _stable_id(*parts: str) -> str:
    digest = hashlib.sha256("|".join(parts).encode("utf-8")).hexdigest()[:16]
    return f"{parts[0]}:{digest}"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

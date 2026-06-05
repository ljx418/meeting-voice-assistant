"""V2.9 architecture ranking calibration."""

from __future__ import annotations

import hashlib
from collections import Counter, defaultdict
from datetime import datetime, timezone
from typing import Any


SCHEMA_VERSION = "v2.9"
PINNED_SEVERITIES = {"fatal", "major"}
SEVERITY_WEIGHT = {"fatal": 100, "major": 85, "medium": 55, "minor": 30, "info": 10}


def build_ranking_calibration_v2(
    *,
    workspace_id: str,
    codebase_id: str,
    snapshot_id: str,
    public_surface_evidence: dict[str, Any],
    relationships: dict[str, Any],
    previous_ranking: dict[str, Any] | None,
    artifact_refs: list[dict[str, str]],
) -> dict[str, Any]:
    candidates = []
    candidates.extend(_evidence_candidates(public_surface_evidence.get("evidence", [])))
    candidates.extend(_relationship_candidates(relationships.get("relationships", [])))
    candidates.extend(_previous_ranking_candidates(previous_ranking or {}))
    ranked = [_rank(workspace_id, codebase_id, snapshot_id, item) for item in candidates]
    ranked = _dedupe_ranked(ranked)
    ranked.sort(key=lambda item: (-int(item.get("pinned", False)), -float(item.get("score") or 0), item.get("ranking_id") or ""))
    queue_items = [_queue_item(item) for item in ranked if item.get("pinned") or item.get("score", 0) >= 45 or item.get("needs_review")]
    major_fatal_input = [item for item in ranked if item.get("severity") in PINNED_SEVERITIES]
    visible_ids = {item["ranking_id"] for item in ranked[:200]}
    hidden_major = [item for item in major_fatal_input if item["ranking_id"] not in visible_ids]
    ranking = {
        "schema_version": SCHEMA_VERSION,
        "workspace_id": workspace_id,
        "codebase_id": codebase_id,
        "snapshot_id": snapshot_id,
        "ranking_id": _stable_id("ranking-v2", codebase_id, snapshot_id),
        "score_formula": {
            "severity": 30,
            "evidence_strength": 25,
            "relationship_depth": 15,
            "doc_code_drift": 10,
            "duplicate_group_size": 10,
            "staleness": 5,
            "human_priority": 5,
        },
        "items": ranked[:300],
        "summary": {
            "candidate_count": len(candidates),
            "ranked_count": len(ranked),
            "pinned_count": sum(1 for item in ranked if item.get("pinned")),
            "major_fatal_count": len(major_fatal_input),
            "hidden_major_count": sum(1 for item in hidden_major if item.get("severity") == "major"),
            "hidden_fatal_count": sum(1 for item in hidden_major if item.get("severity") == "fatal"),
            "input_top_n_major_count": sum(1 for item in major_fatal_input[:50] if item.get("severity") == "major"),
            "output_top_n_major_count": sum(1 for item in ranked[:50] if item.get("severity") == "major"),
            "duplicate_reduction_ratio": _duplicate_reduction_ratio(candidates, ranked),
            "reason_codes": sorted({code for item in ranked for code in item.get("reason_codes", [])}),
            "weak_evidence_promoted": False,
        },
        "blocked_by_major_findings": [item["ranking_id"] for item in ranked if item.get("pinned")],
        "source_artifact_refs": artifact_refs,
        "created_at": _now(),
    }
    queue = {
        "schema_version": SCHEMA_VERSION,
        "workspace_id": workspace_id,
        "codebase_id": codebase_id,
        "snapshot_id": snapshot_id,
        "queue_id": _stable_id("review-queue-v3", codebase_id, snapshot_id),
        "items": queue_items[:200],
        "summary": {
            "queue_count": len(queue_items[:200]),
            "p0_count": sum(1 for item in queue_items[:200] if item.get("priority") == "p0"),
            "p1_count": sum(1 for item in queue_items[:200] if item.get("priority") == "p1"),
            "p2_count": sum(1 for item in queue_items[:200] if item.get("priority") == "p2"),
            "reason_codes": sorted({code for item in queue_items[:200] for code in item.get("reason_codes", [])}),
        },
        "source_artifact_refs": artifact_refs,
        "created_at": _now(),
    }
    return {"schema_version": SCHEMA_VERSION, "ranking": ranking, "review_queue_v3": queue, "artifact_refs": artifact_refs}


def public_ranking_calibration_v2_payload(payload: dict[str, Any], artifact_refs: list[dict[str, str]]) -> dict[str, Any]:
    ranking = payload.get("ranking", {})
    queue = payload.get("review_queue_v3", {})
    return {
        "schema_version": SCHEMA_VERSION,
        "ranking": {**ranking, "items": list(ranking.get("items", []))[:120]},
        "review_queue_v3": {**queue, "items": list(queue.get("items", []))[:120]},
        "artifact_refs": artifact_refs,
    }


def _evidence_candidates(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    candidates = []
    for row in rows:
        if row.get("status") == "accepted":
            severity = "info"
            reason_codes = ["ACCEPTED_SURFACE_EVIDENCE"]
            needs_review = []
        elif row.get("status") == "blocked":
            severity = "major"
            reason_codes = ["BLOCKED_SURFACE_EVIDENCE"]
            needs_review = row.get("needs_review") or []
        else:
            severity = "medium"
            reason_codes = ["SURFACE_EVIDENCE_NEEDS_REVIEW"]
            needs_review = row.get("needs_review") or []
        candidates.append(
            {
                "item_type": "public_surface_evidence",
                "source_id": row.get("evidence_id") or row.get("surface_id"),
                "label": row.get("label") or row.get("surface_id") or "surface evidence",
                "severity": severity,
                "confidence": float(row.get("confidence") or 0.4),
                "evidence_refs": row.get("evidence_refs") or [],
                "needs_review": needs_review,
                "score_components": {"severity": SEVERITY_WEIGHT[severity], "evidence_strength": 90 if row.get("status") == "accepted" else 30, "relationship_depth": 0, "doc_code_drift": 0, "duplicate_group_size": 0, "staleness": 0, "human_priority": 0},
                "reason_codes": reason_codes,
            }
        )
    return candidates


def _relationship_candidates(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    candidates = []
    for row in rows:
        status = str(row.get("status") or "")
        severity = "info" if status == "accepted" else "medium"
        if row.get("semantic_claim") == "implementation_hint" and status != "accepted":
            severity = "medium"
        candidates.append(
            {
                "item_type": "code_relationship",
                "source_id": row.get("relationship_id"),
                "label": f"{row.get('relation_type')} {row.get('source_id')} -> {row.get('target_id')}",
                "severity": severity,
                "confidence": float(row.get("confidence") or 0.5),
                "evidence_refs": row.get("evidence_refs") or [],
                "needs_review": row.get("needs_review") or [],
                "score_components": {"severity": SEVERITY_WEIGHT[severity], "evidence_strength": 70 if row.get("evidence_refs") else 25, "relationship_depth": 30, "doc_code_drift": 0, "duplicate_group_size": 0, "staleness": 0, "human_priority": 0},
                "reason_codes": ["CODE_RELATIONSHIP", f"RELATION_{str(row.get('relation_type') or 'UNKNOWN').upper()}"],
            }
        )
    return candidates


def _previous_ranking_candidates(previous: dict[str, Any]) -> list[dict[str, Any]]:
    ranking = previous.get("ranking") if isinstance(previous.get("ranking"), dict) else previous
    items = list((ranking or {}).get("items", []))
    candidates = []
    for row in items[:200]:
        severity = str(row.get("severity") or "medium").lower()
        candidates.append(
            {
                "item_type": "prior_ranking_signal",
                "source_id": row.get("ranking_id") or row.get("source_id"),
                "label": row.get("label") or "prior ranking signal",
                "severity": severity if severity in SEVERITY_WEIGHT else "medium",
                "confidence": float(row.get("confidence") or 0.5),
                "evidence_refs": row.get("evidence_refs") or [],
                "needs_review": row.get("needs_review") or [],
                "score_components": {"severity": SEVERITY_WEIGHT.get(severity, 55), "evidence_strength": 40, "relationship_depth": 0, "doc_code_drift": 25 if row.get("item_type") == "doc_code_drift" else 0, "duplicate_group_size": 0, "staleness": 0, "human_priority": 20 if row.get("pinned") else 0},
                "reason_codes": ["PRIOR_RANKING_SIGNAL", *list(row.get("reason_codes") or [])[:3]],
            }
        )
    return candidates


def _rank(workspace_id: str, codebase_id: str, snapshot_id: str, item: dict[str, Any]) -> dict[str, Any]:
    components = dict(item.get("score_components") or {})
    score = min(100.0, round(sum(float(value) for value in components.values()) / max(1, len(components)) + float(item.get("confidence") or 0) * 10, 2))
    severity = str(item.get("severity") or "medium").lower()
    pinned = severity in PINNED_SEVERITIES
    if pinned:
        score = max(score, 85.0)
    ranking_id = _stable_id("ranking-v2-item", codebase_id, snapshot_id, str(item.get("item_type") or ""), str(item.get("source_id") or ""))
    return {
        "schema_version": SCHEMA_VERSION,
        "workspace_id": workspace_id,
        "codebase_id": codebase_id,
        "snapshot_id": snapshot_id,
        "ranking_id": ranking_id,
        "item_type": item.get("item_type"),
        "source_id": item.get("source_id"),
        "label": item.get("label"),
        "severity": severity,
        "score": score,
        "score_components": components,
        "reason_codes": list(dict.fromkeys(item.get("reason_codes") or [])),
        "confidence": float(item.get("confidence") or 0.5),
        "evidence_refs": item.get("evidence_refs") or [],
        "needs_review": item.get("needs_review") or [],
        "pinned": pinned,
        "blocked_by_major_findings": pinned,
    }


def _queue_item(item: dict[str, Any]) -> dict[str, Any]:
    severity = item.get("severity")
    priority = "p0" if severity == "fatal" else "p1" if severity == "major" else "p2"
    return {
        "queue_item_id": _stable_id("review-queue-v3-item", item.get("ranking_id") or ""),
        "ranking_id": item.get("ranking_id"),
        "priority": priority,
        "label": item.get("label"),
        "reason_codes": item.get("reason_codes") or [],
        "evidence_refs": item.get("evidence_refs") or [],
        "needs_review": item.get("needs_review") or [],
    }


def _dedupe_ranked(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_label: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for item in items:
        by_label[str(item.get("label") or item.get("source_id") or "")].append(item)
    result = []
    for _label, group in by_label.items():
        group.sort(key=lambda item: (-int(item.get("pinned", False)), -float(item.get("score") or 0)))
        primary = dict(group[0])
        if len(group) > 1:
            primary["duplicate_group_size"] = len(group)
            primary.setdefault("reason_codes", []).append("DUPLICATE_GROUP_REPRESENTATIVE")
        result.append(primary)
    return result


def _duplicate_reduction_ratio(candidates: list[dict[str, Any]], ranked: list[dict[str, Any]]) -> float:
    if not candidates:
        return 0.0
    return round(max(0, len(candidates) - len(ranked)) / len(candidates), 4)


def _stable_id(*parts: str) -> str:
    digest = hashlib.sha256("|".join(parts).encode("utf-8")).hexdigest()[:16]
    return f"{parts[0]}:{digest}"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

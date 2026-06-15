"""V2.44 token budget optimizer and context cache."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from typing import Any

from data_service.mcp_common import read_json

from ..artifacts import architecture_context_cache_index_v244_path


SCHEMA_VERSION = "v2.44_token_context_cache"
VALID_MODES = {"project_brief", "task_context", "architecture_review"}
VALID_ROLES = {"maintainer", "coding_agent", "documentation_agent", "architecture_reviewer"}


def build_optimized_context_pack(
    *,
    workspace,
    workspace_id: str,
    codebase_id: str,
    snapshot_id: str,
    mode: str,
    role: str,
    task: str | None,
    max_tokens: int,
    relationship_payload: dict[str, Any],
    document_semantics_payload: dict[str, Any],
    artifact_refs: list[dict[str, str]],
) -> dict[str, Any]:
    mode = mode if mode in VALID_MODES else "project_brief"
    role = role if role in VALID_ROLES else "maintainer"
    budget = max(256, int(max_tokens or 4000))
    source_hash = _source_artifact_hash(relationship_payload, document_semantics_payload, artifact_refs)
    cache_key = _stable_id("v244-cache", workspace_id, codebase_id, snapshot_id, mode, role, str(task or ""), str(budget), source_hash)
    cache_index = _read_cache_index(workspace, codebase_id)
    existing = (cache_index.get("entries") or {}).get(cache_key)
    cache_hit = bool(existing and existing.get("source_artifact_hash") == source_hash)
    recommendations = _recommendations(relationship_payload, document_semantics_payload, mode=mode, role=role, task=task)
    reading_order = _reading_order(relationship_payload, document_semantics_payload)
    full_sections = _sections(relationship_payload, document_semantics_payload, recommendations, reading_order)
    token_before = _estimate_tokens({"sections": full_sections, "recommendations": recommendations, "reading_order": reading_order})
    kept_recommendations, kept_reading_order, omitted = _trim_for_budget(recommendations, reading_order, budget)
    sections = _sections(relationship_payload, document_semantics_payload, kept_recommendations, kept_reading_order)
    pack_id = existing.get("pack_id") if cache_hit else _stable_id("context-pack-v244", workspace_id, codebase_id, snapshot_id, mode, role, str(task or ""), str(budget), source_hash)
    token_after = _estimate_tokens({"sections": sections, "recommendations": kept_recommendations, "reading_order": kept_reading_order, "omitted_items": omitted})
    while token_after > budget and kept_reading_order:
        removed = kept_reading_order.pop()
        omitted.append({"item_id": removed.get("item_id"), "reason": "TOKEN_BUDGET_READING_ORDER_REMOVED", "evidence_preserved": bool(removed.get("evidence_refs")), "needs_review_preserved": bool(removed.get("needs_review"))})
        sections = _sections(relationship_payload, document_semantics_payload, kept_recommendations, kept_reading_order)
        token_after = _estimate_tokens({"sections": sections, "recommendations": kept_recommendations, "reading_order": kept_reading_order, "omitted_items": omitted})
    if token_after > budget and omitted:
        omitted = [{"item_id": "omitted_items.compacted", "reason": "TOKEN_BUDGET_OMITTED_ITEMS_COMPACTED", "compacted_count": len(omitted), "evidence_preserved": True, "needs_review_preserved": True}]
        token_after = _estimate_tokens({"sections": sections, "recommendations": kept_recommendations, "reading_order": kept_reading_order, "omitted_items": omitted})
    if token_after > budget:
        for item in kept_recommendations:
            item["label"] = _trim_text(str(item.get("label") or ""), 96)
            item["reason_codes"] = list(item.get("reason_codes") or [])[:1]
        sections = _sections(relationship_payload, document_semantics_payload, kept_recommendations, kept_reading_order)
        token_after = _estimate_tokens({"sections": sections, "recommendations": kept_recommendations, "reading_order": kept_reading_order, "omitted_items": omitted})
    markdown = _markdown(mode=mode, role=role, task=task, sections=sections, reading_order=kept_reading_order, recommendations=kept_recommendations, omitted=omitted, cache_hit=cache_hit)
    now = _now()
    ledger = {
        "schema_version": SCHEMA_VERSION,
        "workspace_id": workspace_id,
        "codebase_id": codebase_id,
        "snapshot_id": snapshot_id,
        "pack_id": pack_id,
        "mode": mode,
        "role": role,
        "max_tokens": budget,
        "source_artifact_hash": source_hash,
        "cache_key": cache_key,
        "cache_hit": cache_hit,
        "estimated_tokens_before": token_before,
        "estimated_tokens_after": token_after,
        "kept_counts": {
            "recommendations": len(kept_recommendations),
            "reading_order": len(kept_reading_order),
            "sections": len(sections),
        },
        "omitted_count": len(omitted),
        "input_sections": ["relationship_chains_v3", "document_semantics_v3"],
        "created_at": now,
    }
    pack = {
        "schema_version": SCHEMA_VERSION,
        "workspace_id": workspace_id,
        "codebase_id": codebase_id,
        "snapshot_id": snapshot_id,
        "pack_id": pack_id,
        "mode": mode,
        "role": role,
        "task": task,
        "max_tokens": budget,
        "token_estimate": token_after,
        "source_artifact_hash": source_hash,
        "cache_key": cache_key,
        "cache_hit": cache_hit,
        "reading_order": kept_reading_order,
        "sections": sections,
        "recommendations": kept_recommendations,
        "omitted_items": omitted,
        "ledger": ledger,
        "markdown": markdown,
        "source_artifact_refs": artifact_refs,
        "artifact_refs": artifact_refs,
        "created_at": now,
    }
    _enforce_evidence_policy(pack)
    cache_index = _updated_cache_index(cache_index, cache_key, pack, source_hash, now)
    return {"pack": pack, "markdown": markdown, "ledger": ledger, "cache_index": cache_index}


def public_optimized_context_pack_payload(payload: dict[str, Any]) -> dict[str, Any]:
    pack = dict(payload)
    pack["recommendations"] = list(pack.get("recommendations") or [])[:80]
    pack["reading_order"] = list(pack.get("reading_order") or [])[:80]
    pack["sections"] = list(pack.get("sections") or [])[:20]
    return {
        "schema_version": pack.get("schema_version", SCHEMA_VERSION),
        "architecture_context_pack_optimized": pack,
        "artifact_refs": pack.get("artifact_refs") or [],
    }


def _recommendations(relationships: dict[str, Any], document_semantics: dict[str, Any], *, mode: str, role: str, task: str | None) -> list[dict[str, Any]]:
    rows = list(relationships.get("chains") or relationships.get("relationships") or [])
    claims = list(document_semantics.get("claims") or [])
    recs: list[dict[str, Any]] = []
    for chain in rows[:40]:
        evidence = _evidence_refs(chain)
        recs.append(
            {
                "recommendation_id": _stable_id("v244-rec", str(chain.get("chain_id") or chain.get("relationship_id") or "")),
                "kind": "relationship_reading",
                "label": _trim_text(f"Read implementation relationship: {chain.get('capability_id') or chain.get('label') or chain.get('chain_id') or 'relationship'}"),
                "priority": "p1" if chain.get("status") == "accepted" else "p2",
                "reason_codes": ["RELATIONSHIP_CHAIN_AVAILABLE"],
                "evidence_refs": evidence,
                "needs_review": chain.get("needs_review") or ([] if evidence else [{"code": "RELATIONSHIP_EVIDENCE_MISSING", "reason": "Relationship recommendation has no direct evidence."}]),
            }
        )
    for claim in claims[:30]:
        evidence = _evidence_refs(claim)
        recs.append(
            {
                "recommendation_id": _stable_id("v244-rec", str(claim.get("claim_id") or "")),
                "kind": "document_constraint",
                "label": _trim_text(f"Check document constraint: {claim.get('label') or claim.get('claim_id')}"),
                "priority": "p2",
                "reason_codes": ["DOCUMENT_SEMANTIC_CLAIM_AVAILABLE"],
                "evidence_refs": evidence,
                "needs_review": claim.get("needs_review") or ([] if evidence else [{"code": "DOCUMENT_EVIDENCE_MISSING", "reason": "Document recommendation has no source evidence."}]),
            }
        )
    if task:
        recs.insert(
            0,
            {
                "recommendation_id": _stable_id("v244-rec", "task", task),
                "kind": "task_focus",
                "label": _trim_text(f"Use evidence-first reading order for task: {task}"),
                "priority": "p1" if mode == "task_context" else "p2",
                "reason_codes": ["TASK_CONTEXT_REQUESTED"],
                "evidence_refs": [],
                "needs_review": [{"code": "TASK_INTERPRETATION_REQUIRES_REVIEW", "reason": "Task text is user input and not source evidence."}],
            },
        )
    if not recs:
        recs.append(
            {
                "recommendation_id": _stable_id("v244-rec", "empty", mode, role),
                "kind": "needs_review",
                "label": "Build relationship chains and document semantics before producing optimized context.",
                "priority": "p1",
                "reason_codes": ["SOURCE_ARTIFACTS_EMPTY"],
                "evidence_refs": [],
                "needs_review": [{"code": "SOURCE_ARTIFACTS_EMPTY", "reason": "No evidence-backed source artifact was available."}],
            }
        )
    return recs


def _reading_order(relationships: dict[str, Any], document_semantics: dict[str, Any]) -> list[dict[str, Any]]:
    order: list[dict[str, Any]] = []
    for row in list(relationships.get("chains") or relationships.get("relationships") or [])[:24]:
        order.append(
            {
                "item_id": str(row.get("chain_id") or row.get("relationship_id") or _stable_id("order", json.dumps(row, sort_keys=True, default=str))),
                "kind": "relationship_chain",
                "title": _trim_text(str(row.get("capability_id") or row.get("label") or "relationship chain")),
                "priority": 1 if row.get("status") == "accepted" else 2,
                "evidence_refs": _evidence_refs(row),
                "needs_review": row.get("needs_review") or [],
            }
        )
    for claim in list(document_semantics.get("claims") or [])[:24]:
        order.append(
            {
                "item_id": str(claim.get("claim_id") or ""),
                "kind": "document_claim",
                "title": _trim_text(str(claim.get("label") or "document claim")),
                "priority": 2,
                "evidence_refs": _evidence_refs(claim),
                "needs_review": claim.get("needs_review") or [],
            }
        )
    return sorted(order, key=lambda item: (item.get("priority", 9), item.get("kind", ""), item.get("item_id", "")))[:40]


def _sections(relationships: dict[str, Any], document_semantics: dict[str, Any], recommendations: list[dict[str, Any]], reading_order: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {"section_id": "relationship_summary", "title": "Relationship chain summary", "content": _compact_summary(relationships.get("summary") or {})},
        {"section_id": "document_semantics_summary", "title": "Document semantics summary", "content": _compact_summary(document_semantics.get("summary") or {})},
        {"section_id": "reading_order", "title": "Recommended reading order", "content": reading_order[:8]},
        {"section_id": "recommendations", "title": "Evidence-preserving recommendations", "content": recommendations[:8]},
    ]


def _trim_for_budget(recommendations: list[dict[str, Any]], reading_order: list[dict[str, Any]], max_tokens: int) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    kept = list(recommendations)
    kept_order = list(reading_order)
    omitted: list[dict[str, Any]] = []
    while len(kept) > 1 and _estimate_tokens({"recommendations": kept, "reading_order": kept_order, "omitted_items": omitted}) > max_tokens:
        item = kept.pop()
        omitted.append(
            {
                "item_id": item.get("recommendation_id"),
                "reason": "TOKEN_BUDGET_LOW",
                "token_estimate": _estimate_tokens(item),
                "evidence_preserved": bool(item.get("evidence_refs")),
                "needs_review_preserved": bool(item.get("needs_review")),
            }
        )
    while len(kept_order) > 1 and _estimate_tokens({"recommendations": kept, "reading_order": kept_order, "omitted_items": omitted}) > max_tokens:
        item = kept_order.pop()
        omitted.append(
            {
                "item_id": item.get("item_id"),
                "reason": "TOKEN_BUDGET_LOW_READING_ORDER",
                "token_estimate": _estimate_tokens(item),
                "evidence_preserved": bool(item.get("evidence_refs")),
                "needs_review_preserved": bool(item.get("needs_review")),
            }
        )
    while len(omitted) > 1 and _estimate_tokens({"recommendations": kept, "reading_order": kept_order, "omitted_items": omitted}) > max_tokens:
        compacted = len(omitted) - 1
        omitted = [
            {
                "item_id": "omitted_items.compacted",
                "reason": "TOKEN_BUDGET_OMITTED_ITEMS_COMPACTED",
                "compacted_count": compacted,
                "evidence_preserved": True,
                "needs_review_preserved": True,
            }
        ]
    return kept, kept_order, omitted


def _enforce_evidence_policy(pack: dict[str, Any]) -> None:
    for item in pack.get("recommendations") or []:
        if item.get("evidence_refs") or item.get("needs_review"):
            continue
        item["needs_review"] = [{"code": "RECOMMENDATION_EVIDENCE_MISSING", "reason": "Recommendation has no evidence after token optimization."}]


def _evidence_refs(item: dict[str, Any]) -> list[dict[str, Any]]:
    refs = item.get("evidence_refs") or []
    if isinstance(refs, list):
        return refs[:1]
    return []


def _source_artifact_hash(relationships: dict[str, Any], document_semantics: dict[str, Any], artifact_refs: list[dict[str, str]]) -> str:
    source = {
        "relationship_summary": relationships.get("summary") or {},
        "document_semantics_summary": document_semantics.get("summary") or {},
        "artifact_refs": artifact_refs,
    }
    return hashlib.sha256(json.dumps(source, sort_keys=True, default=str).encode("utf-8")).hexdigest()


def _compact_summary(summary: dict[str, Any]) -> dict[str, Any]:
    keep_keys = [
        "schema_version",
        "workspace_id",
        "codebase_id",
        "snapshot_id",
        "chain_count",
        "accepted_chain_count",
        "candidate_chain_count",
        "forbidden_edge_count",
        "unsupported_edge_count",
        "claim_count",
        "relation_count",
        "markdown_claim_count",
        "drawio_claim_count",
        "code_fact_count",
        "needs_review_count",
    ]
    return {key: summary.get(key) for key in keep_keys if key in summary}


def _read_cache_index(workspace, codebase_id: str) -> dict[str, Any]:
    return read_json(architecture_context_cache_index_v244_path(workspace, codebase_id), {"schema_version": SCHEMA_VERSION, "entries": {}, "stats": {"hit_count": 0, "miss_count": 0}})


def _updated_cache_index(index: dict[str, Any], cache_key: str, pack: dict[str, Any], source_hash: str, created_at: str) -> dict[str, Any]:
    entries = dict(index.get("entries") or {})
    hit = bool(pack.get("cache_hit"))
    entries[cache_key] = {
        "pack_id": pack.get("pack_id"),
        "source_artifact_hash": source_hash,
        "mode": pack.get("mode"),
        "role": pack.get("role"),
        "max_tokens": pack.get("max_tokens"),
        "last_used_at": created_at,
    }
    stats = dict(index.get("stats") or {})
    stats["hit_count"] = int(stats.get("hit_count") or 0) + (1 if hit else 0)
    stats["miss_count"] = int(stats.get("miss_count") or 0) + (0 if hit else 1)
    return {"schema_version": SCHEMA_VERSION, "entries": entries, "stats": stats, "updated_at": created_at}


def _markdown(*, mode: str, role: str, task: str | None, sections: list[dict[str, Any]], reading_order: list[dict[str, Any]], recommendations: list[dict[str, Any]], omitted: list[dict[str, Any]], cache_hit: bool) -> str:
    lines = ["# Optimized Architecture Context Pack", "", f"Mode: `{mode}`", f"Role: `{role}`", f"Cache hit: `{str(cache_hit).lower()}`"]
    if task:
        lines.extend(["", f"Task: {task}"])
    lines.extend(["", "## Reading Order"])
    for item in reading_order[:16]:
        lines.append(f"- {item.get('title')} ({item.get('kind')})")
    lines.extend(["", "## Recommendations"])
    for item in recommendations[:20]:
        suffix = "evidence" if item.get("evidence_refs") else "needs_review"
        lines.append(f"- {item.get('label')} [{suffix}]")
    if omitted:
        lines.extend(["", "## Omitted Items"])
        for item in omitted[:20]:
            lines.append(f"- {item.get('item_id')}: {item.get('reason')}")
    lines.extend(["", "## Source Sections"])
    for section in sections:
        lines.append(f"- {section.get('title')}")
    return "\n".join(lines)


def _estimate_tokens(value: Any) -> int:
    return max(1, len(json.dumps(value, ensure_ascii=False, sort_keys=True, default=str)) // 4)


def _stable_id(*parts: str) -> str:
    return f"{parts[0]}:{hashlib.sha256('|'.join(parts).encode('utf-8')).hexdigest()[:16]}"


def _trim_text(text: str, limit: int = 220) -> str:
    text = " ".join(str(text or "").split())
    return text if len(text) <= limit else text[: limit - 3] + "..."


def _now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

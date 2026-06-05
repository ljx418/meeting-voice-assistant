"""V2.8 architecture signal ranking and intent evidence."""

from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from typing import Any


SEVERITY_WEIGHT = {"fatal": 1.0, "major": 0.85, "medium": 0.55, "minor": 0.3, "info": 0.1}
PINNED_SEVERITIES = {"fatal", "major"}
DRAWIO_BLOCK_TYPES = {"diagram_node", "diagram_edge", "drawio_node", "drawio_edge"}


def build_signal_ranking(
    *,
    workspace_id: str,
    codebase_id: str,
    snapshot_id: str | None,
    documents: list[dict[str, Any]],
    claims: list[dict[str, Any]],
    quality_findings: list[dict[str, Any]],
    alignments: list[dict[str, Any]],
    drift: list[dict[str, Any]],
    graph_summary: dict[str, Any],
    code_fact_chains: dict[str, list[dict[str, Any]]],
    artifact_refs: list[dict[str, str]],
) -> dict[str, Any]:
    authority_by_doc = _authority_by_doc(documents)
    candidates: list[dict[str, Any]] = []
    candidates.extend(_finding_candidates(quality_findings, authority_by_doc))
    candidates.extend(_drift_candidates(drift))
    candidates.extend(_alignment_candidates(alignments))
    candidates.extend(_graph_candidates(graph_summary))
    candidates.extend(_chain_candidates(code_fact_chains.get("chains", [])))
    candidates.extend(_document_authority_candidates(documents))
    ranked = [_rank_candidate(workspace_id, codebase_id, snapshot_id, item) for item in candidates]
    ranked.sort(key=lambda item: (-int(item.get("pinned", False)), -float(item.get("score") or 0), item.get("ranking_id") or ""))
    queue_items = [_queue_item(item) for item in ranked if item.get("pinned") or item.get("score", 0) >= 45 or item.get("needs_review")]
    queue_items = queue_items[:200]
    ranking = {
        "schema_version": "v2.8",
        "workspace_id": workspace_id,
        "codebase_id": codebase_id,
        "snapshot_id": snapshot_id,
        "ranking_id": _stable_id("ranking", codebase_id, str(snapshot_id or "")),
        "score_formula": {
            "severity": 35,
            "evidence_density": 15,
            "drift_severity": 15,
            "centrality": 15,
            "document_authority": 10,
            "confidence": 10,
            "recency": 0,
        },
        "items": ranked[:300],
        "summary": {
            "candidate_count": len(candidates),
            "ranked_count": len(ranked),
            "pinned_count": sum(1 for item in ranked if item.get("pinned")),
            "major_fatal_count": sum(1 for item in ranked if str(item.get("severity") or "").lower() in PINNED_SEVERITIES),
            "needs_review_count": sum(1 for item in ranked if item.get("needs_review")),
            "top_score": ranked[0]["score"] if ranked else 0,
            "reason_codes": sorted({code for item in ranked for code in item.get("reason_codes", [])}),
            "weak_evidence_promoted": False,
        },
        "blocked_by_major_findings": [item["ranking_id"] for item in ranked if item.get("pinned")],
        "source_artifact_refs": artifact_refs,
        "created_at": _now(),
    }
    queue = {
        "schema_version": "v2.8",
        "workspace_id": workspace_id,
        "codebase_id": codebase_id,
        "snapshot_id": snapshot_id,
        "queue_id": _stable_id("review-queue-v2", codebase_id, str(snapshot_id or "")),
        "items": queue_items,
        "summary": {
            "queue_count": len(queue_items),
            "p0_count": sum(1 for item in queue_items if item.get("priority") == "p0"),
            "p1_count": sum(1 for item in queue_items if item.get("priority") == "p1"),
            "p2_count": sum(1 for item in queue_items if item.get("priority") == "p2"),
            "reason_codes": sorted({code for item in queue_items for code in item.get("reason_codes", [])}),
        },
        "source_artifact_refs": artifact_refs,
        "created_at": _now(),
    }
    return {"ranking": ranking, "review_queue_v2": queue, "artifact_refs": artifact_refs}


def build_intent_evidence(
    *,
    workspace_id: str,
    codebase_id: str,
    snapshot_id: str | None,
    documents: list[dict[str, Any]],
    claims: list[dict[str, Any]],
    quality_findings: list[dict[str, Any]],
    alignments: list[dict[str, Any]],
    drift: list[dict[str, Any]],
    code_fact_chains: dict[str, list[dict[str, Any]]],
    artifact_refs: list[dict[str, str]],
) -> dict[str, Any]:
    intents: list[dict[str, Any]] = []
    for claim in claims[:500]:
        intents.append(_documented_intent(workspace_id, codebase_id, snapshot_id, claim))
    for chain in code_fact_chains.get("chains", [])[:300]:
        intents.append(_code_observed_intent(workspace_id, codebase_id, snapshot_id, chain))
    for finding in quality_findings[:240]:
        if str(finding.get("severity") or "").lower() in PINNED_SEVERITIES or "conflict" in str(finding.get("finding_type") or ""):
            intents.append(_audit_intent(workspace_id, codebase_id, snapshot_id, finding))
    for item in [*alignments[:300], *drift[:300]]:
        if _is_mismatch(item):
            intents.append(_mismatch_intent(workspace_id, codebase_id, snapshot_id, item))
    intents.sort(key=lambda item: (item.get("intent_type") or "", item.get("intent_id") or ""))
    summary = {
        "schema_version": "v2.8",
        "workspace_id": workspace_id,
        "codebase_id": codebase_id,
        "snapshot_id": snapshot_id,
        "intent_count": len(intents),
        "intent_type_counts": _counts(intents, "intent_type"),
        "needs_review_count": sum(1 for item in intents if item.get("needs_review")),
        "drawio_review_count": sum(1 for item in intents if any(n.get("code") == "DRAWIO_ONLY_INTENT" for n in item.get("needs_review", []))),
        "pure_code_human_intent_claimed": False,
        "source_artifact_refs": artifact_refs,
        "created_at": _now(),
    }
    return {"summary": summary, "intents": intents, "artifact_refs": artifact_refs}


def public_signal_ranking_payload(payload: dict[str, Any], artifact_refs: list[dict[str, str]]) -> dict[str, Any]:
    ranking = payload.get("ranking", {})
    queue = payload.get("review_queue_v2", {})
    return {
        "schema_version": "v2.8",
        "ranking": {**ranking, "items": list(ranking.get("items", []))[:120]},
        "review_queue_v2": {**queue, "items": list(queue.get("items", []))[:120]},
        "artifact_refs": artifact_refs,
    }


def public_intent_evidence_payload(payload: dict[str, Any], artifact_refs: list[dict[str, str]]) -> dict[str, Any]:
    return {
        "schema_version": "v2.8",
        "summary": payload.get("summary", {}),
        "intents": list(payload.get("intents", []))[:180],
        "artifact_refs": artifact_refs,
    }


def _finding_candidates(findings: list[dict[str, Any]], authority_by_doc: dict[str, float]) -> list[dict[str, Any]]:
    candidates = []
    for item in findings:
        doc_id = str(item.get("doc_id") or item.get("document_id") or "")
        severity = str(item.get("severity") or "medium").lower()
        candidates.append(
            {
                "item_type": "quality_finding",
                "source_id": item.get("finding_id") or item.get("id") or item.get("claim_id") or _stable_id("finding", str(item)),
                "label": item.get("message") or item.get("label") or item.get("finding_type") or "quality finding",
                "severity": severity,
                "confidence": float(item.get("confidence") or 0.7),
                "evidence_refs": _refs(item),
                "source_refs": _source_refs(item),
                "needs_review": item.get("needs_review") or [],
                "components": {"severity": SEVERITY_WEIGHT.get(severity, 0.45), "authority": authority_by_doc.get(doc_id, 0.35), "confidence": float(item.get("confidence") or 0.7)},
                "reason_codes": ["QUALITY_FINDING", f"SEVERITY_{severity.upper()}"],
            }
        )
    return candidates


def _drift_candidates(drift: list[dict[str, Any]]) -> list[dict[str, Any]]:
    candidates = []
    for item in drift:
        severity = str(item.get("severity") or ("major" if str(item.get("drift_type") or "").endswith("mismatch") else "medium")).lower()
        candidates.append(
            {
                "item_type": "doc_code_drift",
                "source_id": item.get("drift_id") or item.get("alignment_id") or _stable_id("drift", str(item)),
                "label": item.get("label") or item.get("drift_type") or "doc-code drift",
                "severity": severity,
                "confidence": float(item.get("confidence") or 0.6),
                "evidence_refs": _refs(item),
                "source_refs": _source_refs(item),
                "needs_review": item.get("needs_review") or [],
                "components": {"severity": SEVERITY_WEIGHT.get(severity, 0.45), "drift": 1.0, "confidence": float(item.get("confidence") or 0.6)},
                "reason_codes": ["DOC_CODE_DRIFT", f"SEVERITY_{severity.upper()}"],
            }
        )
    return candidates


def _alignment_candidates(alignments: list[dict[str, Any]]) -> list[dict[str, Any]]:
    candidates = []
    for item in alignments:
        status = str(item.get("status") or "")
        if status == "matched":
            continue
        severity = "major" if status == "designed_not_found_in_code" else "medium"
        needs_review = item.get("needs_review") or [{"code": "ALIGNMENT_REVIEW_REQUIRED", "reason": f"Alignment status is {status or 'unknown'}."}]
        candidates.append(
            {
                "item_type": "alignment_gap",
                "source_id": item.get("alignment_id") or _stable_id("alignment", str(item)),
                "label": item.get("label") or item.get("claim_label") or status or "alignment gap",
                "severity": severity,
                "confidence": float(item.get("confidence") or 0.5),
                "evidence_refs": _refs(item),
                "source_refs": _source_refs(item),
                "needs_review": needs_review,
                "components": {"severity": SEVERITY_WEIGHT[severity], "confidence": float(item.get("confidence") or 0.5)},
                "reason_codes": ["ALIGNMENT_GAP", f"STATUS_{status.upper() or 'UNKNOWN'}"],
            }
        )
    return candidates


def _graph_candidates(graph_summary: dict[str, Any]) -> list[dict[str, Any]]:
    summary = graph_summary.get("summary", {})
    clusters = graph_summary.get("clusters", {})
    cluster_items = clusters.get("clusters", []) if isinstance(clusters, dict) else []
    candidates = []
    for cluster in cluster_items[:120]:
        needs_review_count = int(cluster.get("needs_review_count") or 0)
        if needs_review_count <= 0:
            continue
        candidates.append(
            {
                "item_type": "graph_cluster",
                "source_id": cluster.get("cluster_id") or _stable_id("cluster", str(cluster)),
                "label": cluster.get("label") or cluster.get("cluster_type") or "graph cluster",
                "severity": "medium",
                "confidence": float(cluster.get("confidence") or 0.6),
                "evidence_refs": cluster.get("evidence_refs") or [],
                "source_refs": [{"type": "graph_cluster", "cluster_id": cluster.get("cluster_id")}],
                "needs_review": [{"code": "CLUSTER_HAS_REVIEW_ITEMS", "reason": f"{needs_review_count} graph nodes need review."}],
                "components": {"centrality": min(1.0, float(cluster.get("node_count") or 0) / max(1, float(summary.get("node_count") or 100))), "confidence": float(cluster.get("confidence") or 0.6)},
                "reason_codes": ["GRAPH_CLUSTER_REVIEW"],
            }
        )
    return candidates


def _chain_candidates(chains: list[dict[str, Any]]) -> list[dict[str, Any]]:
    candidates = []
    for chain in chains:
        if chain.get("status") == "accepted" and not chain.get("needs_review"):
            continue
        candidates.append(
            {
                "item_type": "code_fact_chain",
                "source_id": chain.get("chain_id") or _stable_id("chain", str(chain)),
                "label": chain.get("chain_type") or "code fact chain",
                "severity": "medium",
                "confidence": float(chain.get("confidence") or 0.4),
                "evidence_refs": chain.get("evidence_refs") or [],
                "source_refs": [{"type": "code_fact_chain", "chain_id": chain.get("chain_id")}],
                "needs_review": chain.get("needs_review") or [{"code": "CHAIN_REVIEW_REQUIRED", "reason": "Code fact chain is not accepted."}],
                "components": {"confidence": float(chain.get("confidence") or 0.4)},
                "reason_codes": ["CODE_FACT_CHAIN_NEEDS_REVIEW"],
            }
        )
    return candidates


def _document_authority_candidates(documents: list[dict[str, Any]]) -> list[dict[str, Any]]:
    candidates = []
    for doc in documents:
        needs_review = list(doc.get("needs_review") or [])
        if doc.get("stale_hint"):
            needs_review.append({"code": "STALE_DOCUMENT", "reason": "Document has stale hint."})
        if not needs_review:
            continue
        candidates.append(
            {
                "item_type": "architecture_document",
                "source_id": doc.get("doc_id") or _stable_id("doc", str(doc.get("path") or doc)),
                "label": doc.get("path") or doc.get("title") or "architecture document",
                "severity": "medium",
                "confidence": float(doc.get("confidence") or 0.6),
                "evidence_refs": _refs(doc),
                "source_refs": [{"type": "architecture_document", "doc_id": doc.get("doc_id"), "path": doc.get("path")}],
                "needs_review": needs_review,
                "components": {"authority": _authority_score(doc), "confidence": float(doc.get("confidence") or 0.6)},
                "reason_codes": ["DOCUMENT_AUTHORITY_REVIEW"],
            }
        )
    return candidates


def _rank_candidate(workspace_id: str, codebase_id: str, snapshot_id: str | None, item: dict[str, Any]) -> dict[str, Any]:
    components = {
        "severity": float(item.get("components", {}).get("severity") or SEVERITY_WEIGHT.get(str(item.get("severity") or "").lower(), 0.35)) * 35,
        "evidence_density": min(1.0, len(item.get("evidence_refs") or []) / 3.0) * 15,
        "drift_severity": float(item.get("components", {}).get("drift") or 0) * 15,
        "centrality": float(item.get("components", {}).get("centrality") or 0) * 15,
        "document_authority": float(item.get("components", {}).get("authority") or 0.35) * 10,
        "confidence": float(item.get("components", {}).get("confidence") or item.get("confidence") or 0.5) * 10,
        "recency": 0,
    }
    score = round(sum(components.values()), 2)
    severity = str(item.get("severity") or "medium").lower()
    reason_codes = list(dict.fromkeys(item.get("reason_codes", []) + _component_reason_codes(components)))
    return {
        "ranking_id": _stable_id("rank", codebase_id, str(snapshot_id or ""), str(item.get("item_type")), str(item.get("source_id"))),
        "schema_version": "v2.8",
        "workspace_id": workspace_id,
        "codebase_id": codebase_id,
        "snapshot_id": snapshot_id,
        "item_type": item.get("item_type"),
        "source_id": item.get("source_id"),
        "label": item.get("label"),
        "severity": severity,
        "score": score,
        "score_components": components,
        "reason_codes": reason_codes,
        "pinned": severity in PINNED_SEVERITIES,
        "blocked_by_major_findings": severity in PINNED_SEVERITIES,
        "confidence": item.get("confidence"),
        "status": "needs_review" if item.get("needs_review") else "ranked",
        "evidence_refs": item.get("evidence_refs") or [],
        "source_refs": item.get("source_refs") or [],
        "needs_review": item.get("needs_review") or [],
    }


def _queue_item(item: dict[str, Any]) -> dict[str, Any]:
    priority = "p0" if item.get("pinned") else ("p1" if float(item.get("score") or 0) >= 60 else "p2")
    return {
        "queue_item_id": _stable_id("queue", item.get("ranking_id") or ""),
        "ranking_id": item.get("ranking_id"),
        "priority": priority,
        "item_type": item.get("item_type"),
        "source_id": item.get("source_id"),
        "label": item.get("label"),
        "score": item.get("score"),
        "reason_codes": item.get("reason_codes") or [],
        "evidence_refs": item.get("evidence_refs") or [],
        "source_refs": item.get("source_refs") or [],
        "needs_review": item.get("needs_review") or [],
    }


def _documented_intent(workspace_id: str, codebase_id: str, snapshot_id: str | None, claim: dict[str, Any]) -> dict[str, Any]:
    block_type = str(claim.get("source_block_type") or "")
    drawio_only = block_type in DRAWIO_BLOCK_TYPES
    needs_review = list(claim.get("needs_review") or [])
    if drawio_only:
        needs_review.append({"code": "DRAWIO_ONLY_INTENT", "reason": "Diagram-only intent requires supporting text or code evidence."})
    refs = _refs(claim)
    if not refs and not needs_review:
        needs_review.append({"code": "INTENT_EVIDENCE_MISSING", "reason": "Documented intent has no evidence reference."})
    return _intent(
        workspace_id,
        codebase_id,
        snapshot_id,
        "documented_intent",
        claim.get("claim_id") or _stable_id("claim", str(claim)),
        claim.get("label") or claim.get("text") or "documented intent",
        claim_refs=[{"claim_id": claim.get("claim_id"), "doc_id": claim.get("doc_id")}],
        code_refs=[],
        audit_refs=[],
        evidence_refs=refs,
        confidence=min(float(claim.get("confidence") or 0.7), 0.7 if drawio_only else 0.9),
        needs_review=needs_review,
    )


def _code_observed_intent(workspace_id: str, codebase_id: str, snapshot_id: str | None, chain: dict[str, Any]) -> dict[str, Any]:
    accepted = chain.get("status") == "accepted"
    needs_review = [] if accepted else list(chain.get("needs_review") or [{"code": "CODE_OBSERVED_REVIEW_REQUIRED", "reason": "Code fact chain is not accepted."}])
    refs = chain.get("evidence_refs") or []
    return _intent(
        workspace_id,
        codebase_id,
        snapshot_id,
        "code_observed" if accepted else "needs_review",
        chain.get("chain_id") or _stable_id("chain", str(chain)),
        chain.get("chain_type") or "code observed implementation",
        claim_refs=[],
        code_refs=[{"chain_id": chain.get("chain_id"), "chain_type": chain.get("chain_type"), "status": chain.get("status")}],
        audit_refs=[],
        evidence_refs=refs,
        confidence=float(chain.get("confidence") or (0.8 if accepted else 0.4)),
        needs_review=needs_review,
    )


def _audit_intent(workspace_id: str, codebase_id: str, snapshot_id: str | None, finding: dict[str, Any]) -> dict[str, Any]:
    refs = _refs(finding)
    needs_review = finding.get("needs_review") or ([] if refs else [{"code": "AUDIT_EVIDENCE_MISSING", "reason": "Audit finding lacks evidence references."}])
    return _intent(
        workspace_id,
        codebase_id,
        snapshot_id,
        "audit_accepted",
        finding.get("finding_id") or _stable_id("audit", str(finding)),
        finding.get("message") or finding.get("finding_type") or "audit accepted state",
        claim_refs=[{"claim_id": finding.get("claim_id"), "doc_id": finding.get("doc_id")}],
        code_refs=[],
        audit_refs=[{"finding_id": finding.get("finding_id"), "severity": finding.get("severity")}],
        evidence_refs=refs,
        confidence=float(finding.get("confidence") or 0.75),
        needs_review=needs_review,
    )


def _mismatch_intent(workspace_id: str, codebase_id: str, snapshot_id: str | None, item: dict[str, Any]) -> dict[str, Any]:
    refs = _refs(item)
    needs_review = item.get("needs_review") or ([] if refs else [{"code": "MISMATCH_EVIDENCE_MISSING", "reason": "Mismatch lacks direct evidence references."}])
    return _intent(
        workspace_id,
        codebase_id,
        snapshot_id,
        "mismatch",
        item.get("alignment_id") or item.get("drift_id") or _stable_id("mismatch", str(item)),
        item.get("label") or item.get("status") or item.get("drift_type") or "document-code mismatch",
        claim_refs=[{"claim_id": item.get("claim_id"), "doc_id": item.get("doc_id")}],
        code_refs=[{"surface_id": item.get("surface_id"), "symbol_id": item.get("symbol_id"), "path": item.get("path")}],
        audit_refs=[],
        evidence_refs=refs,
        confidence=float(item.get("confidence") or 0.55),
        needs_review=needs_review,
    )


def _intent(
    workspace_id: str,
    codebase_id: str,
    snapshot_id: str | None,
    intent_type: str,
    source_id: Any,
    label: Any,
    *,
    claim_refs: list[dict[str, Any]],
    code_refs: list[dict[str, Any]],
    audit_refs: list[dict[str, Any]],
    evidence_refs: list[dict[str, Any]],
    confidence: float,
    needs_review: list[dict[str, Any]],
) -> dict[str, Any]:
    if not evidence_refs and not claim_refs and not code_refs and not audit_refs and not needs_review:
        needs_review = [{"code": "INTENT_EVIDENCE_MISSING", "reason": "Intent has no supporting references."}]
    return {
        "intent_id": _stable_id("intent", codebase_id, str(intent_type), str(source_id)),
        "schema_version": "v2.8",
        "workspace_id": workspace_id,
        "codebase_id": codebase_id,
        "snapshot_id": snapshot_id,
        "intent_type": intent_type,
        "source_id": source_id,
        "label": label,
        "claim_refs": [ref for ref in claim_refs if any(ref.values())],
        "code_refs": [ref for ref in code_refs if any(ref.values())],
        "audit_refs": [ref for ref in audit_refs if any(ref.values())],
        "evidence_refs": evidence_refs[:8],
        "confidence": round(confidence, 2),
        "needs_review": needs_review,
        "created_at": _now(),
    }


def _is_mismatch(item: dict[str, Any]) -> bool:
    status = str(item.get("status") or "")
    drift_type = str(item.get("drift_type") or "")
    return status in {"designed_not_found_in_code", "weak_match", "unresolved"} or "mismatch" in drift_type or "not_documented" in drift_type


def _refs(item: dict[str, Any]) -> list[dict[str, Any]]:
    refs = item.get("evidence_refs") or item.get("evidence") or []
    if isinstance(refs, list) and refs:
        return [ref for ref in refs if isinstance(ref, dict)][:8]
    ref = {
        "doc_id": item.get("doc_id"),
        "claim_id": item.get("claim_id"),
        "path": item.get("path") or item.get("source_file"),
        "line_range": item.get("line_range"),
        "surface_id": item.get("surface_id"),
        "symbol_id": item.get("symbol_id"),
    }
    return [ref] if any(ref.values()) else []


def _source_refs(item: dict[str, Any]) -> list[dict[str, Any]]:
    refs = item.get("source_refs") or []
    if isinstance(refs, list) and refs:
        return [ref for ref in refs if isinstance(ref, dict)][:8]
    ref = {"path": item.get("path") or item.get("source_file"), "doc_id": item.get("doc_id"), "claim_id": item.get("claim_id")}
    return [ref] if any(ref.values()) else []


def _authority_by_doc(documents: list[dict[str, Any]]) -> dict[str, float]:
    return {str(doc.get("doc_id")): _authority_score(doc) for doc in documents if doc.get("doc_id")}


def _authority_score(doc: dict[str, Any]) -> float:
    role = str(doc.get("authority_role") or "").lower()
    level = str(doc.get("authority_level") or "").lower()
    score = 0.35
    if role == "target":
        score = 0.9
    elif role in {"acceptance_result", "audit_status"}:
        score = 0.85
    elif role == "implementation_plan":
        score = 0.7
    elif role == "historical_reference":
        score = 0.35
    if level == "primary":
        score = max(score, 0.85)
    elif level == "supporting":
        score = max(score, 0.6)
    elif level == "historical":
        score = min(score, 0.45)
    return score


def _component_reason_codes(components: dict[str, float]) -> list[str]:
    codes = []
    for key, value in sorted(components.items()):
        if value > 0:
            codes.append(f"{key.upper()}_{int(round(value))}")
    return codes


def _counts(items: list[dict[str, Any]], key: str) -> dict[str, int]:
    result: dict[str, int] = {}
    for item in items:
        value = str(item.get(key) or "unknown")
        result[value] = result.get(value, 0) + 1
    return dict(sorted(result.items()))


def _stable_id(*parts: str) -> str:
    return hashlib.sha256(":".join(parts).encode("utf-8")).hexdigest()[:20]


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()

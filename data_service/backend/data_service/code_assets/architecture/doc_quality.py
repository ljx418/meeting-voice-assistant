"""Document quality evaluation for V2.7 architecture documentation."""

from __future__ import annotations

from typing import Any

from data_service.mcp_common import now

from .doc_registry import SCHEMA_VERSION, stable_id


PRIMARY_TARGET_TYPES = {"prd", "target_architecture"}
IMPLEMENTED_WORDS = ("implemented", "accepted", "complete", "closure", "已完成", "已验收", "通过")
PENDING_WORDS = ("planned", "pending", "next", "待", "计划", "未完成")
ACCEPTED_LIKE_WORDS = ("implemented", "accepted", "complete", "passed", "ready", "verified", "已完成", "已验收", "通过")
IMPLEMENTATION_SCOPE_WORDS = ("implementation", "development", "phase", "milestone", "实现", "开发", "阶段")


def build_document_quality(
    *,
    workspace_id: str,
    codebase_id: str,
    snapshot_id: str,
    documents: list[dict[str, Any]],
    claims: list[dict[str, Any]],
    relations: list[dict[str, Any]],
) -> dict[str, Any]:
    created_at = now()
    findings: list[dict[str, Any]] = []
    docs_by_id = {str(item.get("doc_id")): item for item in documents}
    claims_by_id = {str(item.get("claim_id")): item for item in claims}
    claims_by_doc: dict[str, list[dict[str, Any]]] = {}
    for claim in claims:
        claims_by_doc.setdefault(str(claim.get("doc_id")), []).append(claim)

    for doc in documents:
        doc_id = str(doc.get("doc_id"))
        doc_claims = claims_by_doc.get(doc_id, [])
        if doc.get("stale_hint") and doc.get("authority_role") in {"target", "implementation_plan", "acceptance_result"}:
            findings.append(
                _finding(
                    workspace_id,
                    codebase_id,
                    snapshot_id,
                    "stale_document",
                    "major",
                    "architecture_doc",
                    doc_id,
                    doc,
                    None,
                    "Stale document has active authority metadata.",
                    "Mark the document historical or update supersession metadata.",
                    created_at,
                    confidence=0.85,
                )
            )
        if doc.get("doc_type") in PRIMARY_TARGET_TYPES and doc.get("authority_level") == "primary":
            if not any(claim.get("claim_type") == "acceptance_gate" for claim in doc_claims):
                findings.append(
                    _finding(
                        workspace_id,
                        codebase_id,
                        snapshot_id,
                        "missing_acceptance_gate",
                        "major",
                        "architecture_doc",
                        doc_id,
                        doc,
                        None,
                        "Primary target document has no extracted acceptance gate.",
                        "Add explicit acceptance criteria or verify extractor coverage.",
                        created_at,
                        confidence=0.8,
                    )
                )
        title = f"{doc.get('title') or ''} {doc.get('path') or ''}".lower()
        if any(word in title for word in ("target", "目标")) and any(word in title for word in ("current", "现状")):
            findings.append(
                _finding(
                    workspace_id,
                    codebase_id,
                    snapshot_id,
                    "missing_current_target_split",
                    "major",
                    "architecture_doc",
                    doc_id,
                    doc,
                    None,
                    "Document mixes current and target architecture hints.",
                    "Separate current-state observations from target-state claims.",
                    created_at,
                    confidence=0.65,
                )
            )

    for claim in claims:
        doc = docs_by_id.get(str(claim.get("doc_id")), {})
        label = str(claim.get("label") or "").lower()
        if not claim.get("evidence"):
            findings.append(
                _finding(
                    workspace_id,
                    codebase_id,
                    snapshot_id,
                    "missing_evidence",
                    "major",
                    "architecture_doc_claim",
                    str(claim.get("claim_id")),
                    doc,
                    claim,
                    "Architecture claim has no document evidence.",
                    "Attach source file evidence or mark the claim as unresolved.",
                    created_at,
                    confidence=0.9,
                )
            )
        confidence = float(claim.get("confidence") or 0)
        if confidence <= 0.65 or claim.get("needs_review"):
            findings.append(
                _finding(
                    workspace_id,
                    codebase_id,
                    snapshot_id,
                    "low_confidence_claim",
                    "minor",
                    "architecture_doc_claim",
                    str(claim.get("claim_id")),
                    doc,
                    claim,
                    "Architecture claim requires review before use as accepted architecture fact.",
                    "Review the source block and either strengthen evidence or keep it as needs_review.",
                    created_at,
                    confidence=max(confidence, 0.55),
                )
            )
        if _looks_strong_current_claim(label) and (confidence <= 0.7 or claim.get("needs_review") or claim.get("source_block_type") in {"diagram_node", "inferred"}):
            findings.append(
                _finding(
                    workspace_id,
                    codebase_id,
                    snapshot_id,
                    "unsupported_claim",
                    "major" if doc.get("authority_level") == "primary" else "minor",
                    "architecture_doc_claim",
                    str(claim.get("claim_id")),
                    doc,
                    claim,
                    "Strong architecture claim has weak or review-only support.",
                    "Keep the claim in review state until stronger document or acceptance evidence exists.",
                    created_at,
                    confidence=max(confidence, 0.55),
                )
            )
        if any(word in label for word in IMPLEMENTED_WORDS) and any(word in label for word in PENDING_WORDS):
            findings.append(
                _finding(
                    workspace_id,
                    codebase_id,
                    snapshot_id,
                    "status_conflict",
                    "major",
                    "architecture_doc_claim",
                    str(claim.get("claim_id")),
                    doc,
                    claim,
                    "Claim mixes accepted/implemented and pending/planned status language.",
                    "Split planning status from implementation evidence.",
                    created_at,
                    confidence=0.8,
                )
            )
        if _looks_overbroad(label):
            findings.append(
                _finding(
                    workspace_id,
                    codebase_id,
                    snapshot_id,
                    "overbroad_architecture_claim",
                    "major",
                    "architecture_doc_claim",
                    str(claim.get("claim_id")),
                    doc,
                    claim,
                    "Claim uses broad architecture wording that may overstate certainty.",
                    "Add concrete evidence, scope, or review status before treating it as accepted.",
                    created_at,
                    confidence=0.65,
                )
            )
        if claim.get("claim_type") in {"component", "system", "plane", "layer"} and not claim.get("scope_hint"):
            findings.append(
                _finding(
                    workspace_id,
                    codebase_id,
                    snapshot_id,
                    "scope_conflict",
                    "major",
                    "architecture_doc_claim",
                    str(claim.get("claim_id")),
                    doc,
                    claim,
                    "Architecture claim has no clear scope hint.",
                    "Attach a phase or scope hint to avoid cross-version confusion.",
                    created_at,
                    confidence=0.6,
                )
            )
        if _looks_implementation_scope_claim(label, str(claim.get("claim_type") or "")) and not _has_acceptance_gate_for_scope(claim, claims_by_doc.get(str(claim.get("doc_id")), [])):
            findings.append(
                _finding(
                    workspace_id,
                    codebase_id,
                    snapshot_id,
                    "missing_acceptance_gate",
                    "major",
                    "architecture_doc_claim",
                    str(claim.get("claim_id")),
                    doc,
                    claim,
                    "Implementation or development claim has no matching acceptance gate in its document scope.",
                    "Add an acceptance or exit gate claim for the same phase or scope.",
                    created_at,
                    confidence=0.75,
                )
            )
        if _looks_implementation_without_evidence(label) and not _has_acceptance_evidence(claim):
            findings.append(
                _finding(
                    workspace_id,
                    codebase_id,
                    snapshot_id,
                    "doc_code_mismatch",
                    "minor",
                    "architecture_doc_claim",
                    str(claim.get("claim_id")),
                    doc,
                    claim,
                    "Claim asserts implementation evidence but no acceptance or artifact reference is attached.",
                    "Attach implementation evidence or keep the claim as a document quality risk.",
                    created_at,
                    confidence=0.7,
                )
            )
        if _looks_owner_required(label) and not (claim.get("scope_hint") or doc.get("phase_hint")):
            findings.append(
                _finding(
                    workspace_id,
                    codebase_id,
                    snapshot_id,
                    "ambiguous_ownership",
                    "minor",
                    "architecture_doc_claim",
                    str(claim.get("claim_id")),
                    doc,
                    claim,
                    "Plan or action claim requires ownership but has no phase or scope authority.",
                    "Attach an owner, phase, or authoritative plan reference.",
                    created_at,
                    confidence=0.6,
                )
            )

    for relation in relations:
        from_id = str(relation.get("from_claim_id") or "")
        to_id = str(relation.get("to_claim_id") or "")
        if from_id not in claims_by_id or to_id not in claims_by_id:
            doc = docs_by_id.get(str(relation.get("source_doc_id")), {})
            findings.append(
                _finding(
                    workspace_id,
                    codebase_id,
                    snapshot_id,
                    "broken_document_relation",
                    "major",
                    "architecture_doc_relation",
                    str(relation.get("relation_id")),
                    doc,
                    relation,
                    "Document relation points to missing claim IDs.",
                    "Rebuild claim extraction or remove the unresolved relation.",
                    created_at,
                    confidence=0.95,
                )
            )

    findings = sorted(_dedupe(findings, "finding_id"), key=lambda item: (item["severity"], item["finding_type"], item["target_id"]))
    summary = _summary(workspace_id, codebase_id, snapshot_id, documents, claims, relations, findings, created_at)
    return {
        "schema_version": SCHEMA_VERSION,
        "workspace_id": workspace_id,
        "codebase_id": codebase_id,
        "snapshot_id": snapshot_id,
        "findings": findings,
        "summary": summary,
        "created_at": created_at,
    }


def public_document_quality_payload(payload: dict[str, Any], artifact_refs: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "schema_version": payload.get("schema_version", SCHEMA_VERSION),
        "workspace_id": payload.get("workspace_id"),
        "codebase_id": payload.get("codebase_id"),
        "snapshot_id": payload.get("snapshot_id"),
        "summary": payload.get("summary", {}),
        "findings": payload.get("findings", []),
        "artifact_refs": artifact_refs,
    }


def _finding(
    workspace_id: str,
    codebase_id: str,
    snapshot_id: str,
    finding_type: str,
    severity: str,
    target_type: str,
    target_id: str,
    doc: dict[str, Any],
    target: dict[str, Any] | None,
    title: str,
    recommendation: str,
    created_at: str,
    *,
    confidence: float,
) -> dict[str, Any]:
    doc_id = str(doc.get("doc_id") or target.get("doc_id") if target else doc.get("doc_id") or "")
    claim_id = str(target.get("claim_id") or "") if target and target_type == "architecture_doc_claim" else ""
    evidence = []
    if target and target.get("evidence"):
        evidence = list(target.get("evidence") or [])
    elif doc.get("evidence"):
        evidence = list(doc.get("evidence") or [])
    needs_review = [] if evidence else [{"code": "FINDING_NEEDS_EVIDENCE_REVIEW", "reason": "Finding target lacks direct evidence."}]
    return {
        "schema_version": SCHEMA_VERSION,
        "workspace_id": workspace_id,
        "codebase_id": codebase_id,
        "snapshot_id": snapshot_id,
        "finding_id": stable_id("archdocq", snapshot_id, finding_type, target_type, target_id, title),
        "finding_type": finding_type,
        "severity": severity,
        "target_type": target_type,
        "target_id": target_id,
        "doc_id": doc_id,
        "claim_id": claim_id,
        "title": title,
        "recommendation": recommendation,
        "evidence": evidence,
        "confidence": confidence,
        "needs_review": needs_review,
        "created_at": created_at,
    }


def _summary(
    workspace_id: str,
    codebase_id: str,
    snapshot_id: str,
    documents: list[dict[str, Any]],
    claims: list[dict[str, Any]],
    relations: list[dict[str, Any]],
    findings: list[dict[str, Any]],
    created_at: str,
) -> dict[str, Any]:
    severity_counts: dict[str, int] = {}
    finding_type_counts: dict[str, int] = {}
    for finding in findings:
        severity = str(finding.get("severity") or "info")
        finding_type = str(finding.get("finding_type") or "unknown")
        severity_counts[severity] = severity_counts.get(severity, 0) + 1
        finding_type_counts[finding_type] = finding_type_counts.get(finding_type, 0) + 1
    return {
        "schema_version": SCHEMA_VERSION,
        "workspace_id": workspace_id,
        "codebase_id": codebase_id,
        "snapshot_id": snapshot_id,
        "document_count": len(documents),
        "claim_count": len(claims),
        "relation_count": len(relations),
        "finding_count": len(findings),
        "severity_counts": dict(sorted(severity_counts.items())),
        "finding_type_counts": dict(sorted(finding_type_counts.items())),
        "needs_review_count": sum(1 for finding in findings if finding.get("needs_review")),
        "overall_status": _overall_status(severity_counts),
        "created_at": created_at,
    }


def _overall_status(severity_counts: dict[str, int]) -> str:
    if severity_counts.get("fatal", 0):
        return "blocked"
    if severity_counts.get("major", 0):
        return "needs_review"
    if severity_counts:
        return "review_recommended"
    return "high_quality"


def _looks_overbroad(label: str) -> bool:
    return any(phrase in label for phrase in ("complete architecture", "完整架构", "all capabilities", "全部能力", "fully implemented", "完整实现"))


def _looks_strong_current_claim(label: str) -> bool:
    return any(word in label for word in ACCEPTED_LIKE_WORDS) or any(phrase in label for phrase in ("current architecture", "target architecture", "ready", "verified"))


def _looks_implementation_scope_claim(label: str, claim_type: str) -> bool:
    if claim_type in {"milestone", "component", "runtime", "storage", "public_interface"} and any(word in label for word in IMPLEMENTATION_SCOPE_WORDS):
        return True
    return any(word in label for word in ("phase ", "implementation", "development plan", "开发计划", "实现计划"))


def _has_acceptance_gate_for_scope(claim: dict[str, Any], doc_claims: list[dict[str, Any]]) -> bool:
    scope = str(claim.get("scope_hint") or "").lower()
    for candidate in doc_claims:
        if candidate.get("claim_id") == claim.get("claim_id"):
            continue
        if candidate.get("claim_type") != "acceptance_gate":
            continue
        if not scope:
            return True
        candidate_scope = str(candidate.get("scope_hint") or "").lower()
        candidate_label = str(candidate.get("label") or "").lower()
        if scope == candidate_scope or scope in candidate_label:
            return True
    return False


def _looks_implementation_without_evidence(label: str) -> bool:
    return any(word in label for word in ACCEPTED_LIKE_WORDS) and any(word in label for word in ("artifact", "test", "evidence", "implementation", "实现", "证据", "测试"))


def _has_acceptance_evidence(claim: dict[str, Any]) -> bool:
    for item in list(claim.get("evidence") or []):
        text = " ".join(str(value).lower() for value in item.values())
        if any(token in text for token in ("acceptance", "audit", "test", "artifact", "evidence", "验收", "证据", "测试")):
            return True
    return False


def _looks_owner_required(label: str) -> bool:
    return any(word in label for word in ("owner", "ownership", "responsible", "负责人", "归属"))


def _dedupe(items: list[dict[str, Any]], key: str) -> list[dict[str, Any]]:
    seen = set()
    result = []
    for item in items:
        value = item[key]
        if value in seen:
            continue
        seen.add(value)
        result.append(item)
    return result

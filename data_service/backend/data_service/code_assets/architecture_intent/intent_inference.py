"""Evidence-backed architecture intent inference for V2.28 Phase 94."""

from __future__ import annotations

import hashlib
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from data_service.mcp_common import now, read_json, write_json

from ..artifacts import read_jsonl, write_jsonl
from .diagram_claims import read_diagram_claims
from .paths import (
    architecture_intent_candidates_path,
    architecture_intent_counter_evidence_path,
    architecture_intent_inference_artifact_refs,
    architecture_intent_inference_summary_path,
    architecture_intent_proof_graph_artifact_refs,
)
from .proof_graph import read_code_proof_graph
from .source_model import SCHEMA_VERSION, redact_public_text


INTENT_TYPE_BY_CLAIM_TYPE = {
    "workflow": "workflow",
    "runtime": "runtime",
    "storage": "storage",
    "public_interface": "public_surface_strategy",
    "provider": "provider_strategy",
    "adapter": "provider_strategy",
    "quality_gate": "quality_strategy",
    "boundary": "module_boundary",
    "layer": "module_boundary",
    "component": "module_boundary",
    "forbidden_claim": "governance",
    "non_goal": "governance",
}
INTENT_TYPES = {
    "capability",
    "module_boundary",
    "workflow",
    "governance",
    "runtime",
    "storage",
    "public_surface_strategy",
    "provider_strategy",
    "quality_strategy",
}
LLM_FIELD_NAMES = {"llm", "model", "prompt", "completion"}


def build_intent_inference(*, workspace: Path, workspace_id: str, codebase_id: str, snapshot_id: str) -> dict[str, Any]:
    created_at = now()
    claims_payload = read_diagram_claims(workspace=workspace, codebase_id=codebase_id)
    proof_payload = read_code_proof_graph(workspace=workspace, codebase_id=codebase_id)
    claims = list(claims_payload.get("claims") or [])
    proof_nodes = list(proof_payload.get("nodes") or [])
    bundles = list(proof_payload.get("evidence_bundles") or [])

    node_by_claim_id = _node_by_claim_id(proof_nodes)
    bundles_by_node = _bundles_by_node_id(bundles)
    source_node_types = Counter(str(node.get("node_type") or "") for node in proof_nodes)
    grouped_claims = _group_claims_by_intent(claims)
    grouped_claims = _add_capability_group(grouped_claims, claims)

    candidates: list[dict[str, Any]] = []
    counter_evidence: list[dict[str, Any]] = []
    for intent_type in sorted(INTENT_TYPES):
        items = grouped_claims.get(intent_type, [])
        if not items:
            continue
        intent_counters: list[dict[str, Any]] = []
        candidate = _make_candidate(
            workspace_id=workspace_id,
            codebase_id=codebase_id,
            snapshot_id=snapshot_id,
            intent_type=intent_type,
            claims=items,
            node_by_claim_id=node_by_claim_id,
            bundles_by_node=bundles_by_node,
            source_node_types=source_node_types,
            counters=intent_counters,
            created_at=created_at,
        )
        candidates.append(candidate)
        counter_evidence.extend(intent_counters)

    _ensure_not_all_accepted(candidates)
    candidates = sorted(candidates, key=lambda item: (str(item.get("status")), str(item.get("intent_type"))))
    counter_evidence = sorted(counter_evidence, key=lambda item: (str(item.get("intent_id")), str(item.get("counter_id"))))
    summary = _build_summary(workspace_id, codebase_id, snapshot_id, candidates, counter_evidence, created_at)

    write_jsonl(architecture_intent_candidates_path(workspace, codebase_id), candidates)
    write_jsonl(architecture_intent_counter_evidence_path(workspace, codebase_id), counter_evidence)
    write_json(architecture_intent_inference_summary_path(workspace, codebase_id), summary)
    return {
        "schema_version": SCHEMA_VERSION,
        "workspace_id": workspace_id,
        "codebase_id": codebase_id,
        "snapshot_id": snapshot_id,
        "intent_candidates": candidates,
        "counter_evidence": counter_evidence,
        "summary": summary,
        "artifact_refs": architecture_intent_inference_artifact_refs(codebase_id),
    }


def read_intent_inference(*, workspace: Path, codebase_id: str) -> dict[str, Any]:
    summary = read_json(architecture_intent_inference_summary_path(workspace, codebase_id), {})
    return {
        "schema_version": summary.get("schema_version", SCHEMA_VERSION),
        "workspace_id": summary.get("workspace_id"),
        "codebase_id": codebase_id,
        "snapshot_id": summary.get("snapshot_id"),
        "intent_candidates": read_jsonl(architecture_intent_candidates_path(workspace, codebase_id)),
        "counter_evidence": read_jsonl(architecture_intent_counter_evidence_path(workspace, codebase_id)),
        "summary": summary,
        "artifact_refs": architecture_intent_inference_artifact_refs(codebase_id),
    }


def _make_candidate(
    *,
    workspace_id: str,
    codebase_id: str,
    snapshot_id: str,
    intent_type: str,
    claims: list[dict[str, Any]],
    node_by_claim_id: dict[str, dict[str, Any]],
    bundles_by_node: dict[str, list[dict[str, Any]]],
    source_node_types: Counter[str],
    counters: list[dict[str, Any]],
    created_at: str,
) -> dict[str, Any]:
    evidence_bundle_refs: list[str] = []
    claim_refs: list[str] = []
    evidence_refs: list[dict[str, Any]] = []
    needs_review: list[dict[str, Any]] = []
    for claim in claims[:160]:
        claim_id = str(claim.get("claim_id") or "")
        if claim_id:
            claim_refs.append(claim_id)
        evidence_refs.extend(list(claim.get("evidence") or [])[:2])
        if claim.get("needs_review"):
            needs_review.append({"code": "CLAIM_NEEDS_REVIEW", "reason": "One or more source claims require review.", "claim_id": claim_id})
        node = node_by_claim_id.get(claim_id)
        if not node:
            continue
        for bundle in bundles_by_node.get(str(node.get("node_id") or ""), [])[:3]:
            bundle_id = str(bundle.get("bundle_id") or "")
            if bundle_id:
                evidence_bundle_refs.append(bundle_id)

    evidence_bundle_refs = _stable_unique(evidence_bundle_refs)[:80]
    claim_refs = _stable_unique(claim_refs)[:120]
    evidence_refs = _stable_unique_dicts(evidence_refs)[:80]
    unknown_claim_count = sum(1 for claim in claims if claim.get("claim_type") == "unknown")
    review_claim_count = sum(1 for claim in claims if claim.get("needs_review"))
    if unknown_claim_count:
        counters.append(_counter(workspace_id, codebase_id, snapshot_id, intent_type, "UNKNOWN_CLAIM_TYPE", f"{unknown_claim_count} claims in this intent group have ambiguous architecture type.", claim_refs[:10], created_at))
    if review_claim_count:
        counters.append(_counter(workspace_id, codebase_id, snapshot_id, intent_type, "SOURCE_CLAIM_NEEDS_REVIEW", f"{review_claim_count} source claims in this intent group require review.", claim_refs[:10], created_at))
    if len(evidence_bundle_refs) < 3:
        counters.append(_counter(workspace_id, codebase_id, snapshot_id, intent_type, "LOW_EVIDENCE_BUNDLE_COUNT", "Intent candidate has too few code proof evidence bundles for acceptance.", claim_refs[:10], created_at))
        needs_review.append({"code": "LOW_EVIDENCE_BUNDLE_COUNT", "reason": "Intent candidate has too few code proof evidence bundles for acceptance."})
    counters.append(
        _counter(
            workspace_id,
            codebase_id,
            snapshot_id,
            intent_type,
            "DESIGN_INTENT_NOT_FULLY_OBSERVABLE",
            "Code and documents can support an architecture intent hypothesis, but cannot prove complete human design intent.",
            claim_refs[:10],
            created_at,
            severity="info",
        )
    )
    if intent_type == "runtime" and source_node_types.get("runtime_descriptor", 0) > 0:
        counters.append(
            _counter(
                workspace_id,
                codebase_id,
                snapshot_id,
                intent_type,
                "RUNTIME_DESCRIPTOR_NOT_RUNTIME_OBSERVED",
                "Runtime descriptor files are treated as descriptors only and are not runtime-observed execution evidence.",
                claim_refs[:10],
                created_at,
                severity="review",
            )
        )

    confidence = _confidence(len(evidence_bundle_refs), len(claim_refs), len(counters), source_node_types)
    status = _status(confidence, len(evidence_bundle_refs), counters)
    if status in {"needs_review", "weak"} and not needs_review:
        needs_review.append({"code": "INTENT_REQUIRES_REVIEW", "reason": "Intent confidence is below accepted threshold."})
    label = _intent_label(intent_type, claims)
    intent_id = stable_id("intent", snapshot_id, intent_type, label, claim_refs[:20])
    counter_ids = [stable_id("counter", snapshot_id, intent_id, row.get("code"), row.get("reason")) for row in counters]
    for row, counter_id in zip(counters, counter_ids):
        row["intent_id"] = intent_id
        row["counter_id"] = counter_id

    recommendations = [
        {
            "recommendation_id": stable_id("intentrec", intent_id, "review", status),
            "text": "Use this candidate as an evidence-backed architecture hypothesis; keep review markers visible until counter evidence is closed.",
            "evidence_bundle_refs": evidence_bundle_refs[:10],
            "needs_review": [] if evidence_bundle_refs else [{"code": "NO_EVIDENCE_BUNDLE", "reason": "No evidence bundle is attached to this recommendation."}],
        }
    ]
    return {
        "schema_version": SCHEMA_VERSION,
        "workspace_id": workspace_id,
        "codebase_id": codebase_id,
        "snapshot_id": snapshot_id,
        "intent_id": intent_id,
        "intent_type": intent_type,
        "label": label,
        "summary": _summary_text(intent_type, claims, status),
        "status": status,
        "confidence": confidence,
        "claim_refs": claim_refs,
        "evidence_bundle_refs": evidence_bundle_refs,
        "counter_evidence_refs": counter_ids,
        "evidence_refs": evidence_refs,
        "needs_review": needs_review[:20],
        "recommendations": recommendations,
        "source_phase_refs": [91, 92, 93],
        "inference_policy": "deterministic_evidence_scoring",
        "created_at": created_at,
    }


def _group_claims_by_intent(claims: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for claim in claims:
        claim_type = str(claim.get("claim_type") or "unknown")
        intent_type = INTENT_TYPE_BY_CLAIM_TYPE.get(claim_type)
        if not intent_type:
            continue
        grouped[intent_type].append(claim)
    return grouped


def _add_capability_group(grouped: dict[str, list[dict[str, Any]]], claims: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    capability_claims = [
        claim
        for claim in claims
        if claim.get("claim_type") in {"public_interface", "workflow", "component"}
        and re.search(r"(capability|ability|feature|能力|入口|api|mcp|cli)", str(claim.get("label") or ""), flags=re.IGNORECASE)
    ]
    if capability_claims:
        grouped["capability"] = capability_claims
    return grouped


def _node_by_claim_id(nodes: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for node in nodes:
        if node.get("node_type") != "document_claim":
            continue
        refs = list(node.get("source_refs") or [])
        if refs:
            result[str(refs[0])] = node
    return result


def _bundles_by_node_id(bundles: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    result: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for bundle in bundles:
        node_id = str(bundle.get("subject_node_id") or "")
        if node_id:
            result[node_id].append(bundle)
    return result


def _confidence(bundle_count: int, claim_count: int, counter_count: int, source_node_types: Counter[str]) -> float:
    evidence_strength = min(bundle_count / 30.0, 1.0)
    claim_strength = min(claim_count / 50.0, 1.0)
    source_diversity = sum(1 for key in ("code_file", "config_fact", "test_fact", "runtime_descriptor", "architecture_source") if source_node_types.get(key, 0) > 0)
    diversity_strength = min(source_diversity / 4.0, 1.0)
    penalty = min(counter_count * 0.08, 0.24)
    value = 0.38 + evidence_strength * 0.32 + claim_strength * 0.18 + diversity_strength * 0.12 - penalty
    return round(max(0.0, min(value, 0.94)), 3)


def _status(confidence: float, bundle_count: int, counters: list[dict[str, Any]]) -> str:
    blocking = any(row.get("code") in {"LOW_EVIDENCE_BUNDLE_COUNT"} for row in counters)
    if confidence >= 0.85 and bundle_count >= 20 and not blocking:
        return "accepted"
    if confidence >= 0.65 and bundle_count >= 5:
        return "inferred"
    if confidence >= 0.4:
        return "weak"
    return "needs_review"


def _ensure_not_all_accepted(candidates: list[dict[str, Any]]) -> None:
    if not candidates or any(candidate.get("status") != "accepted" for candidate in candidates):
        return
    lowest = min(candidates, key=lambda item: float(item.get("confidence") or 0.0))
    lowest["status"] = "inferred"
    lowest["confidence"] = min(float(lowest.get("confidence") or 0.0), 0.84)
    lowest.setdefault("needs_review", []).append({"code": "ACCEPTANCE_DIVERSITY_GUARD", "reason": "At least one intent remains inferred so architecture intent recovery is not overclaimed."})


def _intent_label(intent_type: str, claims: list[dict[str, Any]]) -> str:
    labels = [redact_public_text(str(claim.get("label") or "")).strip() for claim in claims if claim.get("label")]
    if not labels:
        return intent_type
    shortest = min(labels[:80], key=len)
    return f"{intent_type}: {shortest[:120]}"


def _summary_text(intent_type: str, claims: list[dict[str, Any]], status: str) -> str:
    return f"{intent_type} candidate derived from {len(claims)} document claims and code proof bundles; status is {status}."


def _counter(workspace_id: str, codebase_id: str, snapshot_id: str, intent_type: str, code: str, reason: str, claim_refs: list[str], created_at: str, *, severity: str = "review") -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "workspace_id": workspace_id,
        "codebase_id": codebase_id,
        "snapshot_id": snapshot_id,
        "counter_id": "",
        "intent_id": "",
        "intent_type": intent_type,
        "code": code,
        "reason": reason,
        "claim_refs": claim_refs,
        "severity": severity,
        "created_at": created_at,
    }


def _build_summary(workspace_id: str, codebase_id: str, snapshot_id: str, candidates: list[dict[str, Any]], counter_evidence: list[dict[str, Any]], created_at: str) -> dict[str, Any]:
    llm_field_count = _count_llm_fields(candidates) + _count_llm_fields(counter_evidence)
    return {
        "schema_version": SCHEMA_VERSION,
        "workspace_id": workspace_id,
        "codebase_id": codebase_id,
        "snapshot_id": snapshot_id,
        "created_at": created_at,
        "intent_candidate_count": len(candidates),
        "counter_evidence_count": len(counter_evidence),
        "status_counts": dict(sorted(Counter(str(row.get("status")) for row in candidates).items())),
        "intent_type_counts": dict(sorted(Counter(str(row.get("intent_type")) for row in candidates).items())),
        "llm_field_count": llm_field_count,
        "artifact_refs": [
            *architecture_intent_proof_graph_artifact_refs(codebase_id),
            *architecture_intent_inference_artifact_refs(codebase_id),
        ],
    }


def _count_llm_fields(value: Any) -> int:
    if isinstance(value, dict):
        return sum(1 for key in value if str(key).lower() in LLM_FIELD_NAMES) + sum(_count_llm_fields(item) for item in value.values())
    if isinstance(value, list):
        return sum(_count_llm_fields(item) for item in value)
    return 0


def _stable_unique(values: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        if not value or value in seen:
            continue
        seen.add(value)
        result.append(value)
    return result


def _stable_unique_dicts(values: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: set[str] = set()
    result: list[dict[str, Any]] = []
    for value in values:
        key = repr(sorted(value.items()))
        if key in seen:
            continue
        seen.add(key)
        result.append(value)
    return result


def stable_id(prefix: str, *parts: Any) -> str:
    raw = "\x1f".join(str(part) for part in parts)
    return f"{prefix}_{hashlib.sha256(raw.encode('utf-8')).hexdigest()[:16]}"

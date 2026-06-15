"""Diagram/document claim to code proof verification for V2.29 Phase 95."""

from __future__ import annotations

import hashlib
import re
from collections import Counter
from pathlib import Path
from typing import Any

from data_service.mcp_common import now, read_json, write_json

from ..artifacts import read_jsonl, write_jsonl
from .diagram_claims import read_diagram_claims
from .intent_inference import read_intent_inference
from .paths import (
    architecture_intent_architecture_diff_path,
    architecture_intent_diagram_code_alignment_path,
    architecture_intent_inference_artifact_refs,
    architecture_intent_proof_graph_artifact_refs,
    architecture_intent_undocumented_code_facts_path,
    architecture_intent_verification_artifact_refs,
    architecture_intent_verification_summary_path,
)
from .proof_graph import read_code_proof_graph
from .source_model import SCHEMA_VERSION, redact_public_text


CODE_NODE_TYPES = {"code_file", "config_fact", "test_fact", "runtime_descriptor"}
TOKEN_ONLY_STRATEGY = "token_overlap_only"
ACCEPTED_CONFIDENCE_MIN = 0.80
BLOCKING_COUNTER_CODES = {"RUNTIME_DESCRIPTOR_NOT_RUNTIME_OBSERVED"}


def build_diagram_code_verification(*, workspace: Path, workspace_id: str, codebase_id: str, snapshot_id: str) -> dict[str, Any]:
    created_at = now()
    claims_payload = read_diagram_claims(workspace=workspace, codebase_id=codebase_id)
    proof_payload = read_code_proof_graph(workspace=workspace, codebase_id=codebase_id)
    intent_payload = read_intent_inference(workspace=workspace, codebase_id=codebase_id)
    claims = list(claims_payload.get("claims") or [])
    proof_nodes = list(proof_payload.get("nodes") or [])
    code_nodes = _prepared_code_nodes([node for node in proof_nodes if node.get("node_type") in CODE_NODE_TYPES])
    intent_counters = list(intent_payload.get("counter_evidence") or [])

    alignments: list[dict[str, Any]] = []
    accepted_code_node_ids: set[str] = set()
    for claim in claims:
        alignment = _verify_claim(
            workspace_id=workspace_id,
            codebase_id=codebase_id,
            snapshot_id=snapshot_id,
            claim=claim,
            code_nodes=code_nodes,
            intent_counters=intent_counters,
            created_at=created_at,
        )
        alignments.append(alignment)
        if alignment["match_status"] == "accepted" and alignment.get("matched_code_node_id"):
            accepted_code_node_ids.add(str(alignment["matched_code_node_id"]))

    undocumented = [
        _undocumented_code_fact(workspace_id, codebase_id, snapshot_id, node, created_at)
        for node in code_nodes
        if str(node.get("node_id") or "") not in accepted_code_node_ids
    ]
    alignments = sorted(alignments, key=lambda item: (str(item.get("match_status")), str(item.get("claim_id"))))
    undocumented = sorted(undocumented, key=lambda item: (str(item.get("node_type")), str(item.get("label"))))
    diff = _build_diff(workspace_id, codebase_id, snapshot_id, alignments, undocumented, created_at)
    summary = _build_summary(workspace_id, codebase_id, snapshot_id, alignments, undocumented, diff, created_at)

    write_jsonl(architecture_intent_diagram_code_alignment_path(workspace, codebase_id), alignments)
    write_jsonl(architecture_intent_undocumented_code_facts_path(workspace, codebase_id), undocumented)
    write_json(architecture_intent_architecture_diff_path(workspace, codebase_id), diff)
    write_json(architecture_intent_verification_summary_path(workspace, codebase_id), summary)
    return {
        "schema_version": SCHEMA_VERSION,
        "workspace_id": workspace_id,
        "codebase_id": codebase_id,
        "snapshot_id": snapshot_id,
        "alignments": alignments,
        "undocumented_code_facts": undocumented,
        "architecture_diff": diff,
        "summary": summary,
        "artifact_refs": architecture_intent_verification_artifact_refs(codebase_id),
    }


def read_diagram_code_verification(*, workspace: Path, codebase_id: str) -> dict[str, Any]:
    summary = read_json(architecture_intent_verification_summary_path(workspace, codebase_id), {})
    return {
        "schema_version": summary.get("schema_version", SCHEMA_VERSION),
        "workspace_id": summary.get("workspace_id"),
        "codebase_id": codebase_id,
        "snapshot_id": summary.get("snapshot_id"),
        "alignments": read_jsonl(architecture_intent_diagram_code_alignment_path(workspace, codebase_id)),
        "undocumented_code_facts": read_jsonl(architecture_intent_undocumented_code_facts_path(workspace, codebase_id)),
        "architecture_diff": read_json(architecture_intent_architecture_diff_path(workspace, codebase_id), {}),
        "summary": summary,
        "artifact_refs": architecture_intent_verification_artifact_refs(codebase_id),
    }


def _verify_claim(
    *,
    workspace_id: str,
    codebase_id: str,
    snapshot_id: str,
    claim: dict[str, Any],
    code_nodes: list[dict[str, Any]],
    intent_counters: list[dict[str, Any]],
    created_at: str,
) -> dict[str, Any]:
    best = _best_code_match(claim, code_nodes)
    document_evidence = list(claim.get("evidence") or [])
    counter_refs = _counter_refs_for_claim(claim, intent_counters)
    needs_review: list[dict[str, Any]] = []
    if claim.get("needs_review"):
        needs_review.append({"code": "SOURCE_CLAIM_NEEDS_REVIEW", "reason": "Source claim already requires review."})
    if not best:
        return _alignment(
            workspace_id=workspace_id,
            codebase_id=codebase_id,
            snapshot_id=snapshot_id,
            claim=claim,
            status="missing_code_evidence",
            strategy="none",
            code_node=None,
            document_evidence=document_evidence,
            code_evidence=[],
            counter_refs=counter_refs,
            confidence=0.0,
            needs_review=[*needs_review, {"code": "NO_CODE_EVIDENCE", "reason": "No code/config/test/runtime descriptor proof node matched this document claim."}],
            created_at=created_at,
        )
    strategy, code_node, confidence, reason = best
    code_evidence = list(code_node.get("evidence_refs") or [])
    status = _status_for_match(claim, strategy, confidence, document_evidence, code_evidence, counter_refs)
    if strategy == TOKEN_ONLY_STRATEGY:
        needs_review.append({"code": "TOKEN_OVERLAP_ONLY", "reason": "Token overlap is review-only and cannot be accepted."})
    if status != "accepted" and reason:
        needs_review.append({"code": "MATCH_BELOW_ACCEPTANCE_GATE", "reason": reason})
    if claim.get("claim_type") in {"forbidden_claim", "non_goal"} and code_evidence:
        status = "conflict"
        needs_review.append({"code": "NON_GOAL_HAS_CODE_EVIDENCE", "reason": "A forbidden/non-goal document claim has possible implementation evidence and requires review."})
    if claim.get("status_hint") == "historical":
        status = "stale"
        needs_review.append({"code": "HISTORICAL_DOCUMENT_CLAIM", "reason": "Claim appears to come from historical documentation."})
    return _alignment(
        workspace_id=workspace_id,
        codebase_id=codebase_id,
        snapshot_id=snapshot_id,
        claim=claim,
        status=status,
        strategy=strategy,
        code_node=code_node,
        document_evidence=document_evidence,
        code_evidence=code_evidence,
        counter_refs=counter_refs,
        confidence=confidence,
        needs_review=needs_review,
        created_at=created_at,
    )


def _best_code_match(claim: dict[str, Any], code_nodes: list[dict[str, Any]]) -> tuple[str, dict[str, Any], float, str] | None:
    expected = _expected_node_types(str(claim.get("claim_type") or ""))
    if not expected:
        return None
    claim_tokens = _tokens(str(claim.get("label") or ""))
    scored: list[tuple[float, str, dict[str, Any], str]] = []
    for node in code_nodes:
        node_type = str(node.get("node_type") or "")
        node_tokens = set(node.get("_tokens") or [])
        overlap = len(claim_tokens & node_tokens)
        if node_type not in expected and overlap == 0:
            continue
        if node_type in expected and overlap >= 1:
            strategy = "path_name_match"
            score = min(0.95, 0.82 + overlap * 0.03)
            reason = "Matched by expected proof node type and shared path/name token."
        elif node_type in expected:
            strategy = "claim_type_to_node_type"
            score = 0.81 if node_type in {"config_fact", "test_fact", "runtime_descriptor"} else 0.74
            reason = "Matched by claim type to proof node type taxonomy."
        elif overlap >= 2:
            strategy = TOKEN_ONLY_STRATEGY
            score = min(0.64, 0.42 + overlap * 0.05)
            reason = "Token overlap without stronger structural evidence."
        else:
            continue
        scored.append((score, strategy, node, reason))
    if not scored:
        return None
    score, strategy, node, reason = sorted(scored, key=lambda item: (-item[0], item[1], str(item[2].get("label"))))[0]
    return strategy, node, round(score, 3), reason


def _prepared_code_nodes(code_nodes: list[dict[str, Any]]) -> list[dict[str, Any]]:
    prepared = []
    for node in code_nodes:
        item = dict(node)
        item["_tokens"] = sorted(_tokens(str(node.get("label") or "")))
        prepared.append(item)
    return prepared


def _expected_node_types(claim_type: str) -> set[str]:
    if claim_type in {"public_interface", "workflow", "component", "boundary", "layer", "adapter", "provider"}:
        return {"code_file", "config_fact"}
    if claim_type == "quality_gate":
        return {"test_fact", "config_fact"}
    if claim_type == "storage":
        return {"config_fact", "code_file"}
    if claim_type == "runtime":
        return {"runtime_descriptor", "config_fact"}
    if claim_type in {"forbidden_claim", "non_goal"}:
        return {"code_file", "config_fact", "test_fact", "runtime_descriptor"}
    return set()


def _status_for_match(
    claim: dict[str, Any],
    strategy: str,
    confidence: float,
    document_evidence: list[dict[str, Any]],
    code_evidence: list[dict[str, Any]],
    counter_refs: list[str],
) -> str:
    if strategy == TOKEN_ONLY_STRATEGY:
        return "weak_match"
    if not document_evidence or not code_evidence:
        return "needs_review"
    if confidence >= ACCEPTED_CONFIDENCE_MIN and not _has_blocking_counter(counter_refs):
        return "accepted"
    if confidence >= 0.45:
        return "weak_match"
    return "needs_review"


def _alignment(
    *,
    workspace_id: str,
    codebase_id: str,
    snapshot_id: str,
    claim: dict[str, Any],
    status: str,
    strategy: str,
    code_node: dict[str, Any] | None,
    document_evidence: list[dict[str, Any]],
    code_evidence: list[dict[str, Any]],
    counter_refs: list[str],
    confidence: float,
    needs_review: list[dict[str, Any]],
    created_at: str,
) -> dict[str, Any]:
    claim_id = str(claim.get("claim_id") or "")
    code_node_id = str(code_node.get("node_id") or "") if code_node else None
    return {
        "schema_version": SCHEMA_VERSION,
        "workspace_id": workspace_id,
        "codebase_id": codebase_id,
        "snapshot_id": snapshot_id,
        "verification_id": stable_id("verify", snapshot_id, claim_id, code_node_id, status, strategy),
        "claim_id": claim_id,
        "claim_type": claim.get("claim_type"),
        "claim_label": redact_public_text(str(claim.get("label") or ""))[:500],
        "matched_code_node_id": code_node_id,
        "matched_code_node_type": code_node.get("node_type") if code_node else None,
        "matched_code_label": redact_public_text(str(code_node.get("label") or ""))[:500] if code_node else None,
        "match_status": status,
        "match_strategy": strategy,
        "document_evidence_refs": document_evidence,
        "code_evidence_refs": code_evidence,
        "counter_evidence_refs": counter_refs,
        "confidence": round(confidence, 3),
        "accepted_gate": {
            "document_evidence": bool(document_evidence),
            "code_evidence": bool(code_evidence),
            "not_token_only": strategy != TOKEN_ONLY_STRATEGY,
            "confidence_min": confidence >= ACCEPTED_CONFIDENCE_MIN,
            "no_blocking_counter": not _has_blocking_counter(counter_refs),
        },
        "needs_review": needs_review,
        "created_at": created_at,
    }


def _undocumented_code_fact(workspace_id: str, codebase_id: str, snapshot_id: str, node: dict[str, Any], created_at: str) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "workspace_id": workspace_id,
        "codebase_id": codebase_id,
        "snapshot_id": snapshot_id,
        "fact_id": stable_id("undocumented", snapshot_id, node.get("node_id")),
        "node_id": node.get("node_id"),
        "node_type": node.get("node_type"),
        "label": redact_public_text(str(node.get("label") or ""))[:500],
        "evidence_refs": list(node.get("evidence_refs") or []),
        "status": "undocumented_code_fact",
        "needs_review": [{"code": "NO_ACCEPTED_DOCUMENT_MATCH", "reason": "No accepted document/diagram claim matched this proof node."}],
        "created_at": created_at,
    }


def _build_diff(workspace_id: str, codebase_id: str, snapshot_id: str, alignments: list[dict[str, Any]], undocumented: list[dict[str, Any]], created_at: str) -> dict[str, Any]:
    status_counts = Counter(str(row.get("match_status") or "") for row in alignments)
    return {
        "schema_version": SCHEMA_VERSION,
        "workspace_id": workspace_id,
        "codebase_id": codebase_id,
        "snapshot_id": snapshot_id,
        "created_at": created_at,
        "target_claim_count": len(alignments),
        "accepted_count": status_counts.get("accepted", 0),
        "weak_match_count": status_counts.get("weak_match", 0),
        "missing_code_evidence_count": status_counts.get("missing_code_evidence", 0),
        "conflict_count": status_counts.get("conflict", 0),
        "stale_count": status_counts.get("stale", 0),
        "needs_review_count": status_counts.get("needs_review", 0),
        "undocumented_code_fact_count": len(undocumented),
        "status_counts": dict(sorted(status_counts.items())),
    }


def _build_summary(workspace_id: str, codebase_id: str, snapshot_id: str, alignments: list[dict[str, Any]], undocumented: list[dict[str, Any]], diff: dict[str, Any], created_at: str) -> dict[str, Any]:
    accepted_gate_violations = [
        row.get("verification_id")
        for row in alignments
        if row.get("match_status") == "accepted" and not all((row.get("accepted_gate") or {}).values())
    ]
    token_only_accepted_count = sum(1 for row in alignments if row.get("match_status") == "accepted" and row.get("match_strategy") == TOKEN_ONLY_STRATEGY)
    return {
        "schema_version": SCHEMA_VERSION,
        "workspace_id": workspace_id,
        "codebase_id": codebase_id,
        "snapshot_id": snapshot_id,
        "created_at": created_at,
        "verification_count": len(alignments),
        "undocumented_code_fact_count": len(undocumented),
        "status_counts": diff.get("status_counts", {}),
        "match_strategy_counts": dict(sorted(Counter(str(row.get("match_strategy") or "") for row in alignments).items())),
        "accepted_gate_violation_count": len(accepted_gate_violations),
        "token_only_accepted_count": token_only_accepted_count,
        "artifact_refs": [
            *architecture_intent_proof_graph_artifact_refs(codebase_id),
            *architecture_intent_inference_artifact_refs(codebase_id),
            *architecture_intent_verification_artifact_refs(codebase_id),
        ],
    }


def _counter_refs_for_claim(claim: dict[str, Any], counters: list[dict[str, Any]]) -> list[str]:
    claim_id = str(claim.get("claim_id") or "")
    refs = []
    for counter in counters:
        if counter.get("severity") == "info":
            continue
        if counter.get("code") not in BLOCKING_COUNTER_CODES:
            continue
        if claim_id and claim_id in set(str(ref) for ref in counter.get("claim_refs") or []):
            refs.append(str(counter.get("counter_id") or ""))
        elif counter.get("code") == "RUNTIME_DESCRIPTOR_NOT_RUNTIME_OBSERVED" and claim.get("claim_type") == "runtime":
            refs.append(str(counter.get("counter_id") or ""))
    return [ref for ref in refs if ref]


def _has_blocking_counter(counter_refs: list[str]) -> bool:
    return bool(counter_refs)


def _tokens(value: str) -> set[str]:
    value = redact_public_text(value).lower()
    raw = re.split(r"[^a-z0-9\u4e00-\u9fff]+", value)
    return {token for token in raw if len(token) >= 3 and token not in {"the", "and", "for", "with", "from", "this", "that"}}


def stable_id(prefix: str, *parts: Any) -> str:
    raw = "\x1f".join(str(part) for part in parts)
    return f"{prefix}_{hashlib.sha256(raw.encode('utf-8')).hexdigest()[:16]}"

"""Document-code alignment for V2.7 architecture documentation governance."""

from __future__ import annotations

import re
from collections import Counter
from typing import Any

from data_service.mcp_common import now

from .doc_registry import SCHEMA_VERSION, stable_id


MATCHED = "matched"
WEAK_MATCH = "weak_match"
DESIGNED_NOT_FOUND = "designed_not_found_in_code"
CODE_NOT_DOCUMENTED = "code_not_documented"
DOC_CLAIM_WITHOUT_EVIDENCE = "doc_claim_without_evidence"
STALE_DOC_CLAIM = "stale_doc_claim"
NEEDS_REVIEW = "needs_review"

TOKEN_OVERLAP_ONLY = "token_overlap_only"

ACCEPTED_MIN_CONFIDENCE = 0.80
MAX_CANDIDATES_PER_CLAIM = 40


def build_document_code_alignment(
    *,
    workspace_id: str,
    codebase_id: str,
    snapshot_id: str,
    claims: list[dict[str, Any]],
    quality: dict[str, Any] | None = None,
    code_facts: dict[str, list[dict[str, Any]] | dict[str, Any]] | None = None,
    quality_findings: list[dict[str, Any]] | None = None,
    surfaces: list[dict[str, Any]] | None = None,
    symbols: list[dict[str, Any]] | None = None,
    evidence: list[dict[str, Any]] | None = None,
    code_architecture: dict[str, Any] | None = None,
    taxonomy: dict[str, Any] | None = None,
) -> dict[str, Any]:
    created_at = now()
    if quality is None:
        quality = {"findings": quality_findings or []}
    if code_facts is None:
        code_architecture = code_architecture or {}
        code_facts = {
            "surfaces": surfaces or [],
            "symbols": symbols or [],
            "evidence": evidence or [],
            "roles": code_architecture.get("roles") or [],
            "boundaries": code_architecture.get("boundaries") or [],
            "taxonomy": taxonomy or {},
        }
    quality_by_claim, quality_by_doc = _quality_indexes(quality.get("findings", []))
    code_items = _code_items(code_facts)
    token_index = _token_index(code_items)
    matched_code_ids: set[str] = set()
    alignments: list[dict[str, Any]] = []
    drift: list[dict[str, Any]] = []

    for claim in claims:
        claim_id = str(claim.get("claim_id") or "")
        doc_id = str(claim.get("doc_id") or "")
        doc_evidence = list(claim.get("evidence") or [])
        quality_refs = [*_quality_refs(quality_by_claim.get(claim_id, [])), *_quality_refs(quality_by_doc.get(doc_id, []))]
        blocking_review = bool(claim.get("needs_review")) or any(ref.get("severity") in {"fatal", "major"} for ref in quality_refs)

        if not doc_evidence:
            row = _alignment_row(workspace_id, codebase_id, snapshot_id, claim, DOC_CLAIM_WITHOUT_EVIDENCE, "missing_document_evidence", 0.0, [], quality_refs, created_at, needs_review=[{"code": "DOCUMENT_EVIDENCE_REQUIRED", "reason": "Claim has no document evidence."}])
            alignments.append(row)
            drift.append(_drift_row(workspace_id, codebase_id, snapshot_id, "accepted_document_claim_without_code_evidence", claim_id, "architecture_doc_claim", DOC_CLAIM_WITHOUT_EVIDENCE, doc_evidence, [], "Attach document evidence before evaluating implementation alignment.", "major", row["needs_review"], created_at))
            continue

        if any(ref.get("finding_type") == "stale_document" for ref in quality_refs):
            row = _alignment_row(workspace_id, codebase_id, snapshot_id, claim, STALE_DOC_CLAIM, "stale_document_quality_finding", 0.0, [], quality_refs, created_at, needs_review=[{"code": "STALE_DOCUMENT_REVIEW_REQUIRED", "reason": "Claim belongs to a stale document."}])
            alignments.append(row)
            drift.append(_drift_row(workspace_id, codebase_id, snapshot_id, "stale_document_claim", claim_id, "architecture_doc_claim", STALE_DOC_CLAIM, doc_evidence, [], "Review stale document before using this claim as current architecture.", "major", row["needs_review"], created_at))
            continue

        candidate = _best_candidate(claim, code_items, token_index)
        if candidate:
            item, strategy, confidence = candidate
            matched_code_ids.add(str(item["code_ref"].get("id") or item["code_ref"].get("artifact_ref") or item["id"]))
            if strategy == TOKEN_OVERLAP_ONLY:
                status = WEAK_MATCH
                needs_review = [{"code": "TOKEN_OVERLAP_ONLY", "reason": "Textual overlap is not accepted implementation evidence."}]
            elif confidence >= ACCEPTED_MIN_CONFIDENCE and not blocking_review and item["evidence"]:
                status = MATCHED
                needs_review = []
            else:
                status = NEEDS_REVIEW if blocking_review else WEAK_MATCH
                needs_review = [{"code": "MATCH_REVIEW_REQUIRED", "reason": "Match lacks accepted confidence or has blocking review state."}]
            row = _alignment_row(workspace_id, codebase_id, snapshot_id, claim, status, strategy, confidence, item["evidence"], quality_refs, created_at, code_ref=item["code_ref"], needs_review=needs_review)
            alignments.append(row)
            if status != MATCHED:
                drift.append(_drift_row(workspace_id, codebase_id, snapshot_id, "weak_match_requiring_review", claim_id, "architecture_doc_claim", status, doc_evidence, item["evidence"], "Review weak document-code match before accepting implementation.", "minor", needs_review, created_at))
            continue

        row = _alignment_row(workspace_id, codebase_id, snapshot_id, claim, DESIGNED_NOT_FOUND, "no_code_evidence", 0.0, [], quality_refs, created_at, needs_review=[{"code": "DESIGN_NOT_FOUND_IN_CODE", "reason": "No deterministic code fact matched this document claim."}])
        alignments.append(row)
        drift.append(_drift_row(workspace_id, codebase_id, snapshot_id, "designed_claim_not_found_in_code", claim_id, "architecture_doc_claim", DESIGNED_NOT_FOUND, doc_evidence, [], "Implement, document as future scope, or mark the claim out of current implementation scope.", "major", row["needs_review"], created_at))

    for item in code_items:
        item_id = str(item["code_ref"].get("id") or item["code_ref"].get("artifact_ref") or item["id"])
        if item_id in matched_code_ids:
            continue
        row = _code_only_alignment_row(workspace_id, codebase_id, snapshot_id, item, created_at)
        alignments.append(row)
        drift.append(_drift_row(workspace_id, codebase_id, snapshot_id, CODE_NOT_DOCUMENTED, item_id, "code_fact", CODE_NOT_DOCUMENTED, [], item["evidence"], "Add or link documentation for this code fact if it is architecture-relevant.", "minor", row["needs_review"], created_at))
        if len([entry for entry in alignments if entry["status"] == CODE_NOT_DOCUMENTED]) >= 200:
            break

    alignments = sorted(_dedupe(alignments, "alignment_id"), key=lambda item: (item["status"], item["match_strategy"], item["claim_id"], str(item.get("code_refs"))))
    drift = sorted(_dedupe(drift, "drift_id"), key=lambda item: (item["severity"], item["drift_type"], item["target_id"]))
    summary = _summary(workspace_id, codebase_id, snapshot_id, alignments, drift, created_at)
    return {
        "schema_version": SCHEMA_VERSION,
        "workspace_id": workspace_id,
        "codebase_id": codebase_id,
        "snapshot_id": snapshot_id,
        "alignments": alignments,
        "drift": drift,
        "summary": summary,
        "created_at": created_at,
    }


def public_document_code_alignment_payload(payload: dict[str, Any], artifact_refs: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "schema_version": payload.get("schema_version", SCHEMA_VERSION),
        "workspace_id": payload.get("workspace_id"),
        "codebase_id": payload.get("codebase_id"),
        "snapshot_id": payload.get("snapshot_id"),
        "summary": payload.get("summary", {}),
        "alignments": payload.get("alignments", []),
        "drift": payload.get("drift", []),
        "artifact_refs": artifact_refs,
    }


def _quality_indexes(findings: list[dict[str, Any]]) -> tuple[dict[str, list[dict[str, Any]]], dict[str, list[dict[str, Any]]]]:
    by_claim: dict[str, list[dict[str, Any]]] = {}
    by_doc: dict[str, list[dict[str, Any]]] = {}
    for finding in findings:
        claim_id = str(finding.get("claim_id") or "")
        doc_id = str(finding.get("doc_id") or "")
        if claim_id:
            by_claim.setdefault(claim_id, []).append(finding)
        if doc_id:
            by_doc.setdefault(doc_id, []).append(finding)
    return by_claim, by_doc


def _quality_refs(findings: list[dict[str, Any]]) -> list[dict[str, Any]]:
    refs = []
    for finding in findings[:5]:
        refs.append({"finding_id": finding.get("finding_id"), "finding_type": finding.get("finding_type"), "severity": finding.get("severity")})
    return refs


def _code_items(code_facts: dict[str, list[dict[str, Any]] | dict[str, Any]]) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for surface in list(code_facts.get("surfaces") or []):
        surface_id = str(surface.get("surface_id") or "")
        capability_id = str(surface.get("capability_id") or "")
        label = " ".join(str(surface.get(key) or "") for key in ("surface_id", "surface_type", "method", "route", "route_path", "path", "tool_name", "command", "name", "source_file", "capability_id"))
        items.append(
            _code_item(
                "surface",
                surface_id,
                label,
                {
                    "type": "surface",
                    "id": surface_id,
                    "capability_id": capability_id,
                    "route_path": surface.get("route_path") or surface.get("path"),
                    "method": surface.get("method"),
                    "tool_name": surface.get("tool_name"),
                    "command": surface.get("command"),
                },
                _evidence(surface),
                capability_id=capability_id,
            )
        )
    for symbol in list(code_facts.get("symbols") or []):
        symbol_id = str(symbol.get("symbol_id") or "")
        label = " ".join(str(symbol.get(key) or "") for key in ("symbol_id", "qualified_name", "name", "kind", "signature", "path", "source_file"))
        items.append(_code_item("symbol", symbol_id, label, {"type": "symbol", "id": symbol_id, "kind": symbol.get("kind"), "qualified_name": symbol.get("qualified_name")}, _evidence(symbol)))
    for file_item in list(code_facts.get("files") or []):
        path = str(file_item.get("path") or "")
        if not path:
            continue
        items.append(_code_item("file", path, path, {"type": "snapshot_file", "id": path}, _evidence(file_item)))
    for role in list(code_facts.get("roles") or []):
        role_id = str(role.get("role_id") or "")
        label = " ".join(str(role.get(key) or "") for key in ("role_id", "role_type", "name", "path"))
        items.append(_code_item("v24_role", role_id, label, {"type": "v24_role", "id": role_id, "role_type": role.get("role_type")}, _evidence(role)))
    for boundary in list(code_facts.get("boundaries") or []):
        boundary_id = str(boundary.get("boundary_id") or "")
        label = " ".join(str(boundary.get(key) or "") for key in ("boundary_id", "boundary_type", "name"))
        items.append(_code_item("v24_boundary", boundary_id, label, {"type": "v24_boundary", "id": boundary_id, "boundary_type": boundary.get("boundary_type")}, _evidence(boundary)))
    taxonomy = code_facts.get("taxonomy") or {}
    if isinstance(taxonomy, dict):
        for collection_name in ("role_types", "layer_types", "boundary_types", "pattern_types"):
            for entry in list(taxonomy.get(collection_name) or []):
                if isinstance(entry, dict):
                    label = " ".join(str(entry.get(key) or "") for key in ("id", "name", "description", "label"))
                    entry_id = str(entry.get("id") or entry.get("name") or label)
                else:
                    label = str(entry)
                    entry_id = label
                if entry_id:
                    items.append(_code_item("v26_taxonomy", entry_id, label, {"type": "v26_taxonomy", "id": entry_id, "collection": collection_name}, [{"type": "architecture_taxonomy", "artifact_ref": "architecture_taxonomy.json"}]))
    return [item for item in items if item["tokens"]]


def _code_item(kind: str, item_id: str, label: str, code_ref: dict[str, Any], evidence: list[dict[str, Any]], *, capability_id: str = "") -> dict[str, Any]:
    return {"kind": kind, "id": item_id, "label": label, "tokens": _tokens(label), "code_ref": code_ref, "evidence": evidence, "capability_id": capability_id}


def _evidence(item: dict[str, Any]) -> list[dict[str, Any]]:
    evidence = list(item.get("evidence") or [])
    if evidence:
        return evidence[:5]
    source_file = item.get("source_file") or item.get("path")
    if source_file:
        return [{"type": "code_fact", "source_file": source_file, "repo_path": source_file, "line_range": item.get("line_range")}]
    return []


def _best_candidate(claim: dict[str, Any], code_items: list[dict[str, Any]], token_index: dict[str, list[dict[str, Any]]]) -> tuple[dict[str, Any], str, float] | None:
    label = str(claim.get("label") or "")
    claim_tokens = _tokens(label)
    if not claim_tokens:
        return None
    code_candidates = _candidate_code_items(label, claim_tokens, code_items, token_index)
    candidates: list[tuple[dict[str, Any], str, float]] = []
    for item in code_candidates:
        strategy, confidence = _strategy_and_confidence(claim, claim_tokens, item)
        if confidence > 0:
            candidates.append((item, strategy, confidence))
    if not candidates:
        return None
    return max(candidates, key=lambda entry: (entry[2], 0 if entry[1] == TOKEN_OVERLAP_ONLY else 1))


def _token_index(code_items: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    index: dict[str, list[dict[str, Any]]] = {}
    for item in code_items:
        if item["kind"] == "surface":
            index.setdefault("__surface_items__", []).append(item)
        for token in item["tokens"]:
            index.setdefault(token, []).append(item)
    return index


def _candidate_code_items(label: str, claim_tokens: set[str], code_items: list[dict[str, Any]], token_index: dict[str, list[dict[str, Any]]]) -> list[dict[str, Any]]:
    candidates: dict[str, dict[str, Any]] = {}
    for token in sorted(claim_tokens, key=lambda value: len(token_index.get(value, []))):
        items = token_index.get(token, [])
        if len(items) > 80:
            continue
        for item in items:
            candidates[str(item.get("id") or item.get("label"))] = item
            if len(candidates) >= MAX_CANDIDATES_PER_CLAIM:
                break
        if len(candidates) >= MAX_CANDIDATES_PER_CLAIM:
            break
    lower = label.lower()
    for item in token_index.get("__surface_items__", []):
        item_id = str(item.get("id") or "").lower()
        capability_id = str(item.get("capability_id") or "").lower()
        if (item_id and item_id in lower) or (capability_id and capability_id in lower.replace(" ", "_")):
            candidates[str(item.get("id") or item.get("label"))] = item
    values = list(candidates.values())
    values.sort(key=lambda item: (item["kind"] not in {"surface", "symbol", "v24_role", "v24_boundary", "v26_taxonomy"}, len(item["tokens"])))
    return values[:MAX_CANDIDATES_PER_CLAIM]


def _strategy_and_confidence(claim: dict[str, Any], claim_tokens: set[str], item: dict[str, Any]) -> tuple[str, float]:
    label = str(claim.get("label") or "").lower()
    claim_type = str(claim.get("claim_type") or "")
    item_id = str(item.get("id") or "").lower()
    capability_id = str(item.get("capability_id") or "").lower()
    code_ref = item.get("code_ref") or {}
    route_path = str(code_ref.get("route_path") or "").lower()
    tool_name = str(code_ref.get("tool_name") or "").lower()
    command = str(code_ref.get("command") or "").lower()
    qualified_name = str(code_ref.get("qualified_name") or "").lower()
    if item["kind"] == "surface" and (item_id and item_id.lower() in label):
        return "exact_surface_id", 0.95
    if item["kind"] == "surface" and route_path and route_path in label:
        return "exact_surface_id", 0.95
    if item["kind"] == "surface" and tool_name and tool_name in label:
        return "exact_surface_id", 0.95
    if item["kind"] == "surface" and command and command in label:
        return "exact_surface_id", 0.95
    if item["kind"] == "surface" and capability_id and capability_id in label.replace(" ", "_"):
        return "capability_id_match", 0.90
    if item["kind"] == "symbol" and (item_id and item_id.lower() in label):
        return "exact_symbol_id", 0.95
    if item["kind"] == "symbol" and qualified_name and _qualified_name_in_label(qualified_name, label):
        return "exact_symbol_id", 0.95
    if item["kind"] == "file" and item_id and item_id.lower() in label:
        return "path_and_line_evidence_match", 0.88
    if item["kind"] == "file" and any(str(ev.get("repo_path") or ev.get("path") or "").lower() == item_id for ev in list(claim.get("evidence") or [])):
        return "artifact_ref_match", 0.90
    if item["kind"] == "v24_role" and claim_type in {"component", "layer", "runtime", "storage", "governance_boundary"} and claim_tokens & item["tokens"]:
        return "v24_role_boundary_match", min(0.85, 0.80 + _overlap(claim_tokens, item["tokens"]) / 5)
    if item["kind"] == "v24_boundary" and claim_tokens & item["tokens"]:
        return "v24_role_boundary_match", min(0.85, 0.80 + _overlap(claim_tokens, item["tokens"]) / 5)
    if item["kind"] == "v26_taxonomy" and claim_tokens & item["tokens"]:
        return "v26_taxonomy_match", min(0.82, 0.78 + _overlap(claim_tokens, item["tokens"]) / 5)
    score = _overlap(claim_tokens, item["tokens"])
    if score >= 0.30:
        return TOKEN_OVERLAP_ONLY, min(0.79, max(0.40, score))
    return "", 0.0


def _alignment_row(
    workspace_id: str,
    codebase_id: str,
    snapshot_id: str,
    claim: dict[str, Any],
    status: str,
    match_strategy: str,
    confidence: float,
    code_evidence: list[dict[str, Any]],
    quality_refs: list[dict[str, Any]],
    created_at: str,
    *,
    code_ref: dict[str, Any] | None = None,
    needs_review: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    claim_id = str(claim.get("claim_id") or "")
    return {
        "schema_version": SCHEMA_VERSION,
        "workspace_id": workspace_id,
        "codebase_id": codebase_id,
        "snapshot_id": snapshot_id,
        "alignment_id": stable_id("archdocalign", snapshot_id, claim_id, status, match_strategy, code_ref),
        "claim_id": claim_id,
        "doc_id": claim.get("doc_id"),
        "claim_type": claim.get("claim_type"),
        "status": status,
        "match_strategy": match_strategy,
        "confidence": round(float(confidence), 3),
        "document_evidence": list(claim.get("evidence") or []),
        "code_evidence": code_evidence[:5],
        "code_refs": [code_ref] if code_ref else [],
        "quality_refs": quality_refs,
        "needs_review": list(needs_review or []),
        "created_at": created_at,
    }


def _code_only_alignment_row(workspace_id: str, codebase_id: str, snapshot_id: str, item: dict[str, Any], created_at: str) -> dict[str, Any]:
    code_ref = item["code_ref"]
    return {
        "schema_version": SCHEMA_VERSION,
        "workspace_id": workspace_id,
        "codebase_id": codebase_id,
        "snapshot_id": snapshot_id,
        "alignment_id": stable_id("archdocalign", snapshot_id, CODE_NOT_DOCUMENTED, code_ref),
        "claim_id": "",
        "doc_id": "",
        "claim_type": "",
        "status": CODE_NOT_DOCUMENTED,
        "match_strategy": "code_coverage",
        "confidence": 0.0,
        "document_evidence": [],
        "code_evidence": item["evidence"][:5],
        "code_refs": [code_ref],
        "quality_refs": [],
        "needs_review": [{"code": "CODE_NOT_DOCUMENTED", "reason": "Architecture-relevant code fact has no matched document claim."}],
        "created_at": created_at,
    }


def _drift_row(workspace_id: str, codebase_id: str, snapshot_id: str, drift_type: str, target_id: str, target_type: str, status: str, document_evidence: list[dict[str, Any]], code_evidence: list[dict[str, Any]], recommendation: str, severity: str, needs_review: list[dict[str, Any]], created_at: str) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "workspace_id": workspace_id,
        "codebase_id": codebase_id,
        "snapshot_id": snapshot_id,
        "drift_id": stable_id("archdocdrift", snapshot_id, drift_type, target_id, status),
        "drift_type": drift_type,
        "target_id": target_id,
        "target_type": target_type,
        "status": status,
        "document_evidence": document_evidence[:5],
        "code_evidence": code_evidence[:5],
        "recommendation": recommendation,
        "severity": severity,
        "needs_review": list(needs_review or []),
        "created_at": created_at,
    }


def _summary(workspace_id: str, codebase_id: str, snapshot_id: str, alignments: list[dict[str, Any]], drift: list[dict[str, Any]], created_at: str) -> dict[str, Any]:
    drift_type_counts = dict(sorted(Counter(item["drift_type"] for item in drift).items()))
    return {
        "schema_version": SCHEMA_VERSION,
        "workspace_id": workspace_id,
        "codebase_id": codebase_id,
        "snapshot_id": snapshot_id,
        "alignment_count": len(alignments),
        "drift_count": len(drift),
        "status_counts": dict(sorted(Counter(item["status"] for item in alignments).items())),
        "match_strategy_counts": dict(sorted(Counter(item["match_strategy"] for item in alignments).items())),
        "matched_count": sum(1 for item in alignments if item["status"] == MATCHED),
        "weak_match_count": sum(1 for item in alignments if item["status"] == WEAK_MATCH),
        "designed_not_found_count": sum(1 for item in alignments if item["status"] == DESIGNED_NOT_FOUND),
        "code_not_documented_count": sum(1 for item in alignments if item["status"] == CODE_NOT_DOCUMENTED),
        "drift_type_counts": drift_type_counts,
        "accepted_match_confidence_min": ACCEPTED_MIN_CONFIDENCE,
        "token_overlap_only_accepted": False,
        "created_at": created_at,
    }


def _tokens(value: str) -> set[str]:
    raw = re.findall(r"[A-Za-z][A-Za-z0-9_]{2,}|[\u4e00-\u9fff]{2,}", value)
    stop = {"the", "and", "for", "with", "current", "target", "complete", "phase", "plane", "architecture", "document", "code"}
    expanded: set[str] = set()
    for item in raw:
        normalized = item.lower()
        expanded.add(normalized)
        expanded.update(part.lower() for part in item.split("_") if len(part) >= 3)
        expanded.update(part.lower() for part in re.findall(r"[A-Z]?[a-z]+|[A-Z]+(?=[A-Z]|$)", item) if len(part) >= 3)
    return {item for item in expanded if item not in stop}


def _qualified_name_in_label(qualified_name: str, label: str) -> bool:
    if not qualified_name:
        return False
    if qualified_name in label:
        return True
    parts = [part for part in qualified_name.split(".") if part]
    for index in range(max(0, len(parts) - 3), len(parts)):
        suffix = ".".join(parts[index:])
        if "." in suffix and suffix in label:
            return True
    return False


def _overlap(left: set[str], right: set[str]) -> float:
    if not left or not right:
        return 0.0
    return len(left & right) / max(1, len(left | right))


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

"""Build V2.33 change impact and test selection artifacts."""

from __future__ import annotations

import hashlib
from typing import Any

from data_service.mcp_common import now


SCHEMA_VERSION = "v2.33"


def stable_id(prefix: str, *parts: Any) -> str:
    body = "\n".join(str(part) for part in parts if part is not None)
    return f"{prefix}_{hashlib.sha256(body.encode('utf-8')).hexdigest()[:16]}"


def build_impact_payloads(
    *,
    workspace_id: str,
    codebase_id: str,
    task_query: dict[str, Any],
    relationship_graph: dict[str, Any],
    max_items: int = 50,
) -> tuple[dict[str, Any], dict[str, Any]]:
    task_id = str(task_query.get("task_id") or stable_id("task", task_query.get("task")))
    snapshot_id = str(task_query.get("snapshot_id") or relationship_graph.get("snapshot_id") or "")
    candidates = list(task_query.get("matched_candidates") or [])
    relationships = list(relationship_graph.get("relationships") or [])
    candidate_keys = _candidate_keys(candidates)
    impacted_files: list[dict[str, Any]] = []
    impacted_symbols: list[dict[str, Any]] = []
    impacted_surfaces: list[dict[str, Any]] = []
    impacted_tests: list[dict[str, Any]] = []
    impacted_docs: list[dict[str, Any]] = []
    risk_items: list[dict[str, Any]] = []
    blockers: list[dict[str, Any]] = []

    for candidate in candidates:
        item = _impact_item(candidate, "direct_task_match")
        ctype = str(candidate.get("candidate_type") or "")
        if ctype == "surface":
            impacted_surfaces.append(item)
        elif ctype == "symbol":
            impacted_symbols.append(item)
        elif ctype == "test":
            impacted_tests.append(item)
        elif ctype == "doc":
            impacted_docs.append(item)
        else:
            impacted_files.append(item)
        if candidate.get("needs_review"):
            risk_items.append(_risk_item("needs_review_candidate", candidate, "Candidate requires review before editing."))

    for rel in relationships:
        if not _related_to_candidates(rel, candidate_keys):
            continue
        for ref_name in ["source_ref", "target_ref"]:
            ref = dict(rel.get(ref_name) or {})
            ref_type = str(ref.get("ref_type") or "")
            item = {
                "impact_ref": ref,
                "impact_type": "relationship_neighbor",
                "relationship_id": rel.get("relationship_id"),
                "relationship_type": rel.get("relationship_type"),
                "semantic_limit": rel.get("semantic_limit"),
                "confidence": rel.get("confidence"),
                "evidence_refs": list(rel.get("evidence_refs") or []),
                "needs_review": list(rel.get("needs_review") or []),
            }
            if ref_type == "surface":
                impacted_surfaces.append(item)
            elif ref_type == "symbol":
                impacted_symbols.append(item)
            elif ref_type == "test":
                impacted_tests.append(item)
            elif ref_type == "doc":
                impacted_docs.append(item)
            elif ref.get("path"):
                impacted_files.append(item)
        if rel.get("truth_status") != "accepted":
            risk_items.append(_risk_item("relationship_needs_review", rel, "Relationship is not accepted evidence."))
        if rel.get("relationship_type") == "module_imports_module":
            risk_items.append(_risk_item("static_reference_only", rel, "Import dependency is static reference, not runtime call."))

    suggested_tests = _suggest_tests(impacted_tests, candidates, relationships, max_items=max_items)
    if not suggested_tests:
        blockers.append(_blocker(codebase_id, snapshot_id, task_id, "TEST_EVIDENCE_UNAVAILABLE", "No deterministic test candidate could be selected."))
    if not any([impacted_files, impacted_symbols, impacted_surfaces, impacted_docs, impacted_tests]):
        blockers.append(_blocker(codebase_id, snapshot_id, task_id, "IMPACT_EVIDENCE_UNAVAILABLE", "No deterministic impact evidence could be selected."))

    impact = {
        "schema_version": SCHEMA_VERSION,
        "workspace_id": workspace_id,
        "codebase_id": codebase_id,
        "snapshot_id": snapshot_id,
        "created_at": now(),
        "impact_id": stable_id("impact", codebase_id, snapshot_id, task_id),
        "task_id": task_id,
        "task": task_query.get("task"),
        "task_type": task_query.get("task_type"),
        "impacted_files": _dedupe_items(impacted_files)[:max_items],
        "impacted_symbols": _dedupe_items(impacted_symbols)[:max_items],
        "impacted_surfaces": _dedupe_items(impacted_surfaces)[:max_items],
        "impacted_tests": _dedupe_items(impacted_tests)[:max_items],
        "impacted_docs": _dedupe_items(impacted_docs)[:max_items],
        "architecture_guardrails": [],
        "risk_items": _dedupe_items(risk_items)[:max_items],
        "suggested_tests": suggested_tests,
        "summary": {
            "impacted_file_count": len(_dedupe_items(impacted_files)),
            "impacted_symbol_count": len(_dedupe_items(impacted_symbols)),
            "impacted_surface_count": len(_dedupe_items(impacted_surfaces)),
            "impacted_test_count": len(_dedupe_items(impacted_tests)),
            "impacted_doc_count": len(_dedupe_items(impacted_docs)),
            "suggested_test_count": len(suggested_tests),
            "blocker_count": len(blockers),
        },
        "source_artifact_refs": list(task_query.get("artifact_refs") or []) + list(relationship_graph.get("artifact_refs") or []),
        "evidence_refs": sorted({ref for item in suggested_tests for ref in list(item.get("evidence_refs") or [])}),
        "warnings": [],
        "needs_review": sorted({review for item in risk_items for review in list(item.get("needs_review") or [])}),
        "blockers": blockers,
    }
    test_selection = {
        "schema_version": SCHEMA_VERSION,
        "workspace_id": workspace_id,
        "codebase_id": codebase_id,
        "snapshot_id": snapshot_id,
        "created_at": now(),
        "selection_id": stable_id("tests", codebase_id, snapshot_id, task_id),
        "task_id": task_id,
        "suggested_tests": suggested_tests,
        "summary": {"suggested_test_count": len(suggested_tests), "blocker_count": len(blockers)},
        "evidence_refs": impact["evidence_refs"],
        "warnings": [],
        "needs_review": [],
        "blockers": blockers,
    }
    return impact, test_selection


def public_impact_payload(payload: dict[str, Any]) -> dict[str, Any]:
    return dict(payload)


def public_test_selection_payload(payload: dict[str, Any]) -> dict[str, Any]:
    return dict(payload)


def _candidate_keys(candidates: list[dict[str, Any]]) -> set[str]:
    keys = set()
    for candidate in candidates:
        for field in ["candidate_id", "ref_id", "path"]:
            value = candidate.get(field)
            if value:
                keys.add(str(value))
    return keys


def _related_to_candidates(rel: dict[str, Any], keys: set[str]) -> bool:
    for ref_name in ["source_ref", "target_ref"]:
        ref = rel.get(ref_name) or {}
        if str(ref.get("ref_id") or "") in keys or str(ref.get("path") or "") in keys:
            return True
    return False


def _impact_item(candidate: dict[str, Any], impact_type: str) -> dict[str, Any]:
    return {
        "impact_ref": {"ref_type": candidate.get("candidate_type"), "ref_id": candidate.get("ref_id") or candidate.get("candidate_id"), "path": candidate.get("path")},
        "impact_type": impact_type,
        "confidence": candidate.get("score", 0.6),
        "evidence_refs": list(candidate.get("evidence_refs") or []),
        "needs_review": list(candidate.get("needs_review") or []),
        "reason_codes": list(candidate.get("reason_codes") or []),
    }


def _risk_item(code: str, source: dict[str, Any], message: str) -> dict[str, Any]:
    return {
        "risk_id": stable_id("risk", code, source.get("relationship_id") or source.get("candidate_id") or source.get("ref_id")),
        "severity": "medium" if code == "static_reference_only" else "low",
        "code": code,
        "message": message,
        "source_ref": source.get("source_ref") or {"ref_type": source.get("candidate_type"), "ref_id": source.get("ref_id"), "path": source.get("path")},
        "evidence_refs": list(source.get("evidence_refs") or []),
        "needs_review": list(source.get("needs_review") or []),
    }


def _suggest_tests(impacted_tests: list[dict[str, Any]], candidates: list[dict[str, Any]], relationships: list[dict[str, Any]], *, max_items: int) -> list[dict[str, Any]]:
    tests = []
    for item in impacted_tests:
        ref = item.get("impact_ref") or {}
        path = str(ref.get("path") or "")
        if not path:
            continue
        tests.append(_test_item(path, "relationship or task candidate references this test", item.get("evidence_refs") or [], item.get("needs_review") or [], item.get("relationship_id")))
    for candidate in candidates:
        if candidate.get("candidate_type") == "test":
            tests.append(_test_item(str(candidate.get("path") or ""), "task navigation matched this test candidate", candidate.get("evidence_refs") or [], candidate.get("needs_review") or [], candidate.get("candidate_id")))
    for rel in relationships:
        if rel.get("relationship_type") == "test_references_symbol":
            source = rel.get("source_ref") or {}
            tests.append(_test_item(str(source.get("path") or ""), "test reference relationship", rel.get("evidence_refs") or [], rel.get("needs_review") or [], rel.get("relationship_id")))
    return _dedupe_items([item for item in tests if item.get("path")])[:max_items]


def _test_item(path: str, reason: str, evidence_refs: list[str], needs_review: list[str], source_id: Any) -> dict[str, Any]:
    return {
        "test_ref": stable_id("test", path, source_id),
        "path": path,
        "reason": reason,
        "confidence": 0.75 if evidence_refs else 0.55,
        "evidence_refs": list(evidence_refs),
        "needs_review": list(needs_review) or ([] if evidence_refs else ["test recommendation has no direct line-level evidence"]),
        "source_id": source_id,
    }


def _blocker(codebase_id: str, snapshot_id: str, task_id: str, code: str, message: str) -> dict[str, Any]:
    return {"blocker_id": stable_id("impactblock", codebase_id, snapshot_id, task_id, code), "code": code, "message": message, "retryable": False}


def _dedupe_items(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen = set()
    result = []
    for item in items:
        key = json_key(item)
        if key in seen:
            continue
        seen.add(key)
        result.append(item)
    return result


def json_key(item: dict[str, Any]) -> str:
    ref = item.get("impact_ref") or {}
    return "|".join(str(value) for value in [item.get("path"), item.get("test_ref"), item.get("risk_id"), ref.get("ref_type"), ref.get("ref_id"), ref.get("path"), item.get("relationship_id")])

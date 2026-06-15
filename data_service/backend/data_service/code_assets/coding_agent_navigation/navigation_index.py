"""Build and query deterministic V2.31 task navigation indexes."""

from __future__ import annotations

import hashlib
from typing import Any

from data_service.mcp_common import now

from .task_taxonomy import classify_task, task_terms


SCHEMA_VERSION = "v2.31"


def stable_id(prefix: str, *parts: Any) -> str:
    body = "\n".join(str(part) for part in parts if part is not None)
    return f"{prefix}_{hashlib.sha256(body.encode('utf-8')).hexdigest()[:16]}"


def build_navigation_index_payload(
    *,
    workspace_id: str,
    codebase_id: str,
    snapshot_id: str,
    files: list[dict[str, Any]],
    surfaces: list[dict[str, Any]],
    symbols: list[dict[str, Any]],
    evidence: list[dict[str, Any]],
    overview: dict[str, Any] | None = None,
    architecture_report: dict[str, Any] | None = None,
) -> dict[str, Any]:
    evidence_by_path = _evidence_by_path(evidence)
    candidates: list[dict[str, Any]] = []
    blockers: list[dict[str, Any]] = []
    warnings: list[str] = []
    if not surfaces:
        blockers.append(
            {
                "code": "TASK_NAVIGATION_PUBLIC_SURFACES_UNAVAILABLE",
                "message": "No public surface inventory rows were available; navigation is based on files, symbols, tests and docs only.",
                "retryable": False,
            }
        )
        warnings.append("TASK_NAVIGATION_PUBLIC_SURFACES_UNAVAILABLE")
    for surface in surfaces:
        path = _path(surface)
        name = str(surface.get("name") or surface.get("surface_id") or surface.get("path") or surface.get("tool_name") or surface.get("command") or "")
        candidate = _candidate(
            candidate_type="surface",
            ref_id=str(surface.get("surface_id") or stable_id("surface", name, path)),
            label=name,
            path=path,
            terms=[name, str(surface.get("capability") or ""), str(surface.get("surface_type") or "")],
            evidence_refs=_refs_for(path, evidence_by_path, fallback=surface.get("evidence")),
            metadata={
                "surface_type": surface.get("surface_type"),
                "capability": surface.get("capability"),
                "method": surface.get("method"),
                "route": surface.get("path"),
            },
        )
        candidates.append(candidate)
    for symbol in symbols:
        path = _path(symbol)
        qname = str(symbol.get("qualified_name") or symbol.get("name") or "")
        candidate = _candidate(
            candidate_type="symbol",
            ref_id=str(symbol.get("symbol_id") or stable_id("symbol", qname, path)),
            label=qname,
            path=path,
            terms=[qname, str(symbol.get("kind") or ""), str(symbol.get("signature") or "")],
            evidence_refs=_refs_for(path, evidence_by_path),
            line_range=symbol.get("line_range"),
            metadata={"kind": symbol.get("kind"), "visibility": symbol.get("visibility")},
        )
        candidates.append(candidate)
    for file_item in files:
        path = _path(file_item)
        if not path:
            continue
        kind = _file_candidate_type(path)
        if kind not in {"test", "doc", "config", "entrypoint"}:
            continue
        candidate = _candidate(
            candidate_type=kind,
            ref_id=stable_id(kind, path),
            label=path,
            path=path,
            terms=[path, kind],
            evidence_refs=_refs_for(path, evidence_by_path),
            metadata={"language": file_item.get("language"), "loc": file_item.get("loc")},
        )
        candidates.append(candidate)
    source_artifact_refs = [
        {"type": "snapshot_files", "artifact_ref": f"snapshot-files://{codebase_id}/{snapshot_id}"},
        {"type": "inventory_surfaces", "artifact_ref": f"inventory-surfaces://{codebase_id}/{snapshot_id}"},
        {"type": "symbols", "artifact_ref": f"symbols://{codebase_id}/{snapshot_id}"},
    ]
    optional_sources = []
    if overview:
        optional_sources.append("overview")
    if architecture_report:
        optional_sources.append("architecture_intent_report")
    return {
        "schema_version": SCHEMA_VERSION,
        "workspace_id": workspace_id,
        "codebase_id": codebase_id,
        "snapshot_id": snapshot_id,
        "created_at": now(),
        "summary": {
            "candidate_count": len(candidates),
            "surface_candidate_count": sum(1 for item in candidates if item["candidate_type"] == "surface"),
            "symbol_candidate_count": sum(1 for item in candidates if item["candidate_type"] == "symbol"),
            "test_candidate_count": sum(1 for item in candidates if item["candidate_type"] == "test"),
            "doc_candidate_count": sum(1 for item in candidates if item["candidate_type"] == "doc"),
            "optional_source_count": len(optional_sources),
        },
        "candidates": candidates,
        "source_artifact_refs": source_artifact_refs,
        "artifact_refs": [{"type": "task_navigation_index", "artifact_ref": f"coding-agent://{codebase_id}/task_navigation/navigation_index.json"}],
        "warnings": warnings,
        "needs_review": [],
        "blockers": blockers,
    }


def build_task_query_payload(
    *,
    workspace_id: str,
    codebase_id: str,
    snapshot_id: str,
    task: str,
    index: dict[str, Any],
    limit: int = 25,
) -> dict[str, Any]:
    task_type, terms = classify_task(task)
    ranked: list[dict[str, Any]] = []
    for candidate in list(index.get("candidates") or []):
        score, reason_codes = _score_candidate(candidate, terms, task_type)
        if score <= 0:
            continue
        status = "accepted" if candidate.get("evidence_refs") and score >= 0.65 and "token_overlap_only" not in reason_codes else "needs_review"
        needs_review = list(candidate.get("needs_review") or [])
        if status != "accepted":
            needs_review.append("candidate requires review because match is weak or evidence is missing")
        item = dict(candidate)
        item.update(
            {
                "score": round(score, 3),
                "status": status,
                "reason_codes": sorted(set(reason_codes)),
                "needs_review": sorted(set(needs_review)),
            }
        )
        ranked.append(item)
    ranked.sort(key=lambda item: (-float(item["score"]), item["candidate_type"], item["path"], item["label"]))
    blockers = []
    if not ranked:
        blockers.append({"code": "TASK_NAVIGATION_NO_MATCH", "message": "No deterministic candidate matched this task.", "retryable": False})
    task_id = stable_id("tasknav", codebase_id, snapshot_id, task)
    selected = ranked[: max(1, min(int(limit or 25), 100))]
    accepted_count = sum(1 for item in selected if item.get("status") == "accepted")
    if task_type == "unknown":
        blockers.append({"code": "TASK_NAVIGATION_TASK_TYPE_UNRESOLVED", "message": "Task taxonomy could not classify this request; review candidate list manually.", "retryable": False})
    if selected and accepted_count == 0:
        blockers.append({"code": "TASK_NAVIGATION_ACCEPTED_EVIDENCE_UNAVAILABLE", "message": "Candidates were found but none reached accepted evidence confidence.", "retryable": False})
    return {
        "schema_version": SCHEMA_VERSION,
        "workspace_id": workspace_id,
        "codebase_id": codebase_id,
        "snapshot_id": snapshot_id,
        "task_id": task_id,
        "task": task,
        "task_type": task_type,
        "task_interpretation": {"summary": f"{task_type} task with {len(terms)} deterministic terms", "assumptions": [], "confidence": 0.8 if task_type != "unknown" else 0.45},
        "matched_candidates": selected,
        "matched_capabilities": _unique_metadata(selected, "capability"),
        "matched_surfaces": [item for item in selected if item.get("candidate_type") == "surface"][:20],
        "matched_symbols": [item for item in selected if item.get("candidate_type") == "symbol"][:20],
        "matched_tests": [item for item in selected if item.get("candidate_type") == "test"][:20],
        "matched_docs": [item for item in selected if item.get("candidate_type") == "doc"][:20],
        "summary": {
            "matched_count": len(selected),
            "accepted_count": accepted_count,
            "needs_review_count": sum(1 for item in selected if item.get("status") != "accepted"),
            "blocker_count": len(blockers),
        },
        "artifact_refs": [
            {"type": "task_navigation_index", "artifact_ref": f"coding-agent://{codebase_id}/task_navigation/navigation_index.json"},
            {"type": "task_navigation_query", "artifact_ref": f"coding-agent://{codebase_id}/task_navigation/task_queries/{task_id}.json"},
        ],
        "evidence_refs": sorted({ref for item in selected for ref in list(item.get("evidence_refs") or [])}),
        "needs_review": sorted({review for item in selected for review in list(item.get("needs_review") or [])}),
        "blockers": blockers,
    }


def public_navigation_index_payload(payload: dict[str, Any]) -> dict[str, Any]:
    result = dict(payload)
    result["candidates"] = list(payload.get("candidates") or [])[:200]
    return result


def public_task_query_payload(payload: dict[str, Any]) -> dict[str, Any]:
    return dict(payload)


def _candidate(
    *,
    candidate_type: str,
    ref_id: str,
    label: str,
    path: str,
    terms: list[str],
    evidence_refs: list[str],
    metadata: dict[str, Any],
    line_range: Any = None,
) -> dict[str, Any]:
    normalized_terms = sorted(set(term for value in terms for term in task_terms(str(value or ""))))
    return {
        "candidate_id": stable_id("cand", candidate_type, ref_id, path),
        "candidate_type": candidate_type,
        "ref_id": ref_id,
        "label": label,
        "path": path,
        "line_range": line_range,
        "terms": normalized_terms,
        "metadata": {key: value for key, value in metadata.items() if value not in (None, "", [])},
        "evidence_refs": evidence_refs,
        "needs_review": [] if evidence_refs else ["candidate has no line-level evidence"],
    }


def _score_candidate(candidate: dict[str, Any], terms: list[str], task_type: str) -> tuple[float, list[str]]:
    candidate_terms = set(candidate.get("terms") or [])
    query_terms = set(terms)
    reason_codes = []
    score = 0.0
    if task_type != "unknown":
        type_bonus = {
            "mcp_tool": {"surface", "symbol", "test"},
            "api": {"surface", "symbol", "test"},
            "cli": {"surface", "symbol", "test"},
            "workflow": {"symbol", "config", "test", "doc"},
            "provider": {"symbol", "test", "doc"},
            "snapshot": {"symbol", "config", "test", "doc"},
            "governance": {"surface", "symbol", "test", "doc"},
            "descriptor": {"symbol", "config", "doc", "test"},
            "entrypoint": {"surface", "symbol", "config", "doc"},
            "test": {"test", "symbol"},
            "docs": {"doc", "surface"},
            "architecture_review": {"doc", "surface", "symbol"},
        }.get(task_type, set())
        if candidate.get("candidate_type") in type_bonus:
            score += 0.2
            reason_codes.append(f"task_type_{task_type}")
    overlap = candidate_terms & query_terms
    if overlap:
        score += min(0.5, 0.12 * len(overlap))
        reason_codes.append("term_overlap")
    label = str(candidate.get("label") or "").lower()
    path = str(candidate.get("path") or "").lower()
    for term in query_terms:
        if term and term in label:
            score += 0.2
            reason_codes.append("label_match")
            break
    for term in query_terms:
        if term and term in path:
            score += 0.15
            reason_codes.append("path_match")
            break
    if candidate.get("evidence_refs"):
        score += 0.15
        reason_codes.append("has_evidence")
    if score > 0 and set(reason_codes).issubset({"term_overlap"}):
        reason_codes.append("token_overlap_only")
    return min(score, 1.0), reason_codes


def _path(item: dict[str, Any]) -> str:
    return str(item.get("path") or item.get("source_file") or item.get("file") or "")


def _file_candidate_type(path: str) -> str:
    lower = path.lower()
    if "/test" in lower or lower.startswith("test") or "_test." in lower or "tests/" in lower:
        return "test"
    if lower.endswith((".md", ".mdx", ".rst")) or "/docs/" in lower or lower.startswith("docs/"):
        return "doc"
    if lower.endswith((".toml", ".yaml", ".yml", ".json", ".ini", ".cfg")):
        return "config"
    if lower.endswith(("__main__.py", "main.py", "app.py")):
        return "entrypoint"
    return "file"


def _evidence_by_path(evidence: list[dict[str, Any]]) -> dict[str, list[str]]:
    values: dict[str, list[str]] = {}
    for row in evidence:
        path = _path(row)
        if not path:
            continue
        ref = str(row.get("evidence_id") or row.get("id") or stable_id("evidence", path, row.get("start_line"), row.get("end_line")))
        values.setdefault(path, []).append(ref)
    return values


def _refs_for(path: str, evidence_by_path: dict[str, list[str]], fallback: Any = None) -> list[str]:
    refs = list(evidence_by_path.get(path) or [])
    if isinstance(fallback, list):
        for item in fallback:
            if isinstance(item, dict):
                value = item.get("evidence_id") or item.get("id")
            else:
                value = item
            if value:
                refs.append(str(value))
    return sorted(set(refs))[:20]


def _unique_metadata(candidates: list[dict[str, Any]], key: str) -> list[str]:
    values = []
    for item in candidates:
        value = (item.get("metadata") or {}).get(key)
        if value and str(value) not in values:
            values.append(str(value))
    return values[:50]

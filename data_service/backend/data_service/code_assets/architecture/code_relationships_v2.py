"""V2.9 shallow code relationship layer."""

from __future__ import annotations

import hashlib
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import PurePosixPath
from typing import Any


SCHEMA_VERSION = "v2.9"
ALLOWED_RELATION_TYPES = {
    "capability_implemented_by",
    "surface_handled_by",
    "handler_uses_module",
    "module_referenced_by_test",
    "workflow_uses_step",
    "module_imports_module",
}
FORBIDDEN_RELATION_TYPES = {"runtime_calls", "data_flow", "control_flow", "type_inferred_dependency", "production_runtime_topology"}


def build_code_relationships_v2(
    *,
    workspace_id: str,
    codebase_id: str,
    snapshot_id: str,
    public_surface_evidence: dict[str, Any],
    symbols: list[dict[str, Any]],
    files: list[dict[str, Any]],
    imports: list[dict[str, Any]] | None,
    artifact_refs: list[dict[str, str]],
) -> dict[str, Any]:
    evidence_rows = list(public_surface_evidence.get("evidence", []))
    relationships: list[dict[str, Any]] = []
    relationships.extend(_surface_relationships(workspace_id, codebase_id, snapshot_id, evidence_rows, symbols))
    relationships.extend(_import_relationships(workspace_id, codebase_id, snapshot_id, imports or []))
    relationships.extend(_test_reference_relationships(workspace_id, codebase_id, snapshot_id, files))
    relationships = _dedupe(relationships)
    clusters = _clusters(workspace_id, codebase_id, snapshot_id, relationships, evidence_rows)
    relation_counts = Counter(item.get("relation_type") or "unknown" for item in relationships)
    status_counts = Counter(item.get("status") or "unknown" for item in relationships)
    unsupported = [item for item in relationships if item.get("relation_type") not in ALLOWED_RELATION_TYPES or item.get("relation_type") in FORBIDDEN_RELATION_TYPES]
    summary = {
        "schema_version": SCHEMA_VERSION,
        "workspace_id": workspace_id,
        "codebase_id": codebase_id,
        "snapshot_id": snapshot_id,
        "relationship_count": len(relationships),
        "cluster_count": len(clusters),
        "relation_type_counts": dict(sorted(relation_counts.items())),
        "status_counts": dict(sorted(status_counts.items())),
        "unsupported_relationship_count": len(unsupported),
        "forbidden_relationship_count": sum(1 for item in relationships if item.get("relation_type") in FORBIDDEN_RELATION_TYPES),
        "semantic_claims": sorted({str(item.get("semantic_claim") or "") for item in relationships if item.get("semantic_claim")}),
    }
    return {
        "schema_version": SCHEMA_VERSION,
        "workspace_id": workspace_id,
        "codebase_id": codebase_id,
        "snapshot_id": snapshot_id,
        "summary": summary,
        "relationships": relationships,
        "clusters": clusters,
        "source_artifact_refs": artifact_refs,
        "artifact_refs": artifact_refs,
        "created_at": _now(),
    }


def public_code_relationships_v2_payload(payload: dict[str, Any], artifact_refs: list[dict[str, str]]) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "summary": payload.get("summary", {}),
        "relationships": list(payload.get("relationships", []))[:260],
        "clusters": list(payload.get("clusters", []))[:80],
        "artifact_refs": artifact_refs,
    }


def _surface_relationships(workspace_id: str, codebase_id: str, snapshot_id: str, evidence_rows: list[dict[str, Any]], symbols: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_path = defaultdict(list)
    for symbol in symbols:
        by_path[str(symbol.get("path") or symbol.get("source_file") or "")].append(symbol)
    relationships: list[dict[str, Any]] = []
    for row in evidence_rows:
        surface_id = str(row.get("surface_id") or row.get("evidence_id") or "")
        capability_id = str(row.get("capability_id") or "unknown")
        evidence_refs = list(row.get("evidence_refs") or [])
        status = "accepted" if row.get("status") == "accepted" else "needs_review"
        relationships.append(
            _relationship(
                workspace_id,
                codebase_id,
                snapshot_id,
                relation_type="capability_implemented_by",
                source_id=f"capability:{capability_id}",
                target_id=surface_id,
                semantic_claim="implementation_hint",
                confidence=0.86 if status == "accepted" else 0.55,
                status=status,
                evidence_refs=evidence_refs,
                needs_review=[] if status == "accepted" else [{"code": "SURFACE_EVIDENCE_NOT_ACCEPTED", "reason": "Capability binding depends on non-accepted surface evidence."}],
            )
        )
        symbol_ref = _best_symbol(row, by_path)
        if symbol_ref:
            relationships.append(
                _relationship(
                    workspace_id,
                    codebase_id,
                    snapshot_id,
                    relation_type="surface_handled_by",
                    source_id=surface_id,
                    target_id=symbol_ref,
                    semantic_claim="deterministic_surface_binding",
                    confidence=0.9 if status == "accepted" else 0.6,
                    status=status,
                    evidence_refs=evidence_refs,
                    needs_review=[] if status == "accepted" else [{"code": "HANDLER_EVIDENCE_WEAK", "reason": "Handler binding is present but evidence is not accepted."}],
                )
            )
        else:
            relationships.append(
                _relationship(
                    workspace_id,
                    codebase_id,
                    snapshot_id,
                    relation_type="surface_handled_by",
                    source_id=surface_id,
                    target_id=f"file:{row.get('source_path') or 'unknown'}",
                    semantic_claim="implementation_hint",
                    confidence=0.58,
                    status="needs_review",
                    evidence_refs=evidence_refs,
                    needs_review=[{"code": "HANDLER_SYMBOL_NOT_FOUND", "reason": "Surface line evidence did not resolve to a symbol."}],
                )
            )
    return relationships


def _import_relationships(workspace_id: str, codebase_id: str, snapshot_id: str, imports: list[dict[str, Any]]) -> list[dict[str, Any]]:
    relationships = []
    for item in imports[:500]:
        source_id = str(item.get("from_module") or item.get("module") or item.get("path") or "")
        target_id = str(item.get("to_module") or item.get("name") or "")
        if not source_id or not target_id:
            continue
        relationships.append(
            _relationship(
                workspace_id,
                codebase_id,
                snapshot_id,
                relation_type="module_imports_module",
                source_id=f"module:{source_id}",
                target_id=f"module:{target_id}",
                semantic_claim="dependency_evidence",
                confidence=0.82,
                status="accepted",
                evidence_refs=[],
                needs_review=[],
            )
        )
    return relationships


def _test_reference_relationships(workspace_id: str, codebase_id: str, snapshot_id: str, files: list[dict[str, Any]]) -> list[dict[str, Any]]:
    source_files = [str(item.get("path") or "") for item in files if str(item.get("path") or "").endswith(".py") and "test" not in str(item.get("path") or "").lower()]
    test_files = [str(item.get("path") or "") for item in files if "test" in str(item.get("path") or "").lower()]
    relationships = []
    for test in test_files[:80]:
        test_stem = PurePosixPath(test).stem.replace("test_", "").replace("_test", "")
        match = next((path for path in source_files if test_stem and test_stem in PurePosixPath(path).stem), None)
        if not match:
            continue
        relationships.append(
            _relationship(
                workspace_id,
                codebase_id,
                snapshot_id,
                relation_type="module_referenced_by_test",
                source_id=f"module:{match}",
                target_id=f"test:{test}",
                semantic_claim="test_reference_evidence",
                confidence=0.72,
                status="needs_review",
                evidence_refs=[],
                needs_review=[{"code": "TEST_REFERENCE_HEURISTIC", "reason": "Test reference is filename-derived and not a runtime claim."}],
            )
        )
    return relationships


def _relationship(
    workspace_id: str,
    codebase_id: str,
    snapshot_id: str,
    *,
    relation_type: str,
    source_id: str,
    target_id: str,
    semantic_claim: str,
    confidence: float,
    status: str,
    evidence_refs: list[str],
    needs_review: list[dict[str, str]],
) -> dict[str, Any]:
    relationship_id = _stable_id("relationship-v2", codebase_id, snapshot_id, relation_type, source_id, target_id, semantic_claim)
    return {
        "schema_version": SCHEMA_VERSION,
        "workspace_id": workspace_id,
        "codebase_id": codebase_id,
        "snapshot_id": snapshot_id,
        "relationship_id": relationship_id,
        "relation_type": relation_type,
        "source_id": source_id,
        "target_id": target_id,
        "semantic_claim": semantic_claim,
        "status": status,
        "confidence": confidence,
        "evidence_refs": evidence_refs,
        "needs_review": needs_review,
    }


def _best_symbol(row: dict[str, Any], by_path: dict[str, list[dict[str, Any]]]) -> str | None:
    refs = list(row.get("symbol_refs") or [])
    if refs:
        return refs[0]
    path = str(row.get("source_path") or "")
    line_range = row.get("line_range") or []
    if not path or len(line_range) != 2:
        return None
    for symbol in by_path.get(path, []):
        raw = symbol.get("line_range") or []
        if len(raw) == 2 and int(raw[0]) <= int(line_range[0]) <= int(raw[1]):
            return str(symbol.get("symbol_id") or symbol.get("qualified_name") or symbol.get("name") or "")
    return None


def _clusters(workspace_id: str, codebase_id: str, snapshot_id: str, relationships: list[dict[str, Any]], evidence_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_capability: dict[str, list[str]] = defaultdict(list)
    for row in evidence_rows:
        capability = str(row.get("capability_id") or "unknown")
        by_capability[capability].append(str(row.get("surface_id") or row.get("evidence_id") or ""))
    clusters = []
    for capability, members in sorted(by_capability.items())[:120]:
        relationship_ids = [item["relationship_id"] for item in relationships if item.get("source_id") == f"capability:{capability}" or item.get("target_id") in members]
        clusters.append(
            {
                "schema_version": SCHEMA_VERSION,
                "workspace_id": workspace_id,
                "codebase_id": codebase_id,
                "snapshot_id": snapshot_id,
                "cluster_id": _stable_id("cluster-v2", codebase_id, snapshot_id, capability),
                "cluster_type": "capability_surface_cluster",
                "label": capability,
                "member_ids": sorted(set(members)),
                "relationship_ids": sorted(set(relationship_ids)),
                "confidence": 0.82 if members else 0.4,
                "needs_review": [] if members else [{"code": "CLUSTER_EMPTY", "reason": "No members resolved for capability."}],
            }
        )
    return clusters


def _dedupe(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen = set()
    result = []
    for item in items:
        key = item.get("relationship_id")
        if key in seen:
            continue
        seen.add(key)
        result.append(item)
    result.sort(key=lambda item: (item.get("relation_type") or "", item.get("relationship_id") or ""))
    return result


def _stable_id(*parts: str) -> str:
    digest = hashlib.sha256("|".join(parts).encode("utf-8")).hexdigest()[:16]
    return f"{parts[0]}:{digest}"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

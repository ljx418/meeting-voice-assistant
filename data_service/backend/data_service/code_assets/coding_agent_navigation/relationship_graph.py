"""Build V2.32 lightweight relationship graph artifacts."""

from __future__ import annotations

import ast
import hashlib
from pathlib import Path
from typing import Any

from data_service.mcp_common import now


SCHEMA_VERSION = "v2.32"

FORBIDDEN_RELATIONSHIP_TYPES = {
    "full_call_graph",
    "runtime_call_accepted",
    "data_flow",
    "control_flow",
    "runtime_topology",
    "type_inferred",
    "production_runtime_topology",
}


def stable_id(prefix: str, *parts: Any) -> str:
    body = "\n".join(str(part) for part in parts if part is not None)
    return f"{prefix}_{hashlib.sha256(body.encode('utf-8')).hexdigest()[:16]}"


def build_relationship_graph_payload(
    *,
    workspace_id: str,
    codebase_id: str,
    snapshot_id: str,
    repo_root: Path,
    surfaces: list[dict[str, Any]],
    symbols: list[dict[str, Any]],
    imports: list[dict[str, Any]],
    mappings: list[dict[str, Any]],
    evidence: list[dict[str, Any]],
    navigation_index: dict[str, Any],
) -> dict[str, Any]:
    evidence_by_id = {str(row.get("evidence_id")): row for row in evidence if row.get("evidence_id")}
    surfaces_by_id = {str(row.get("surface_id")): row for row in surfaces if row.get("surface_id")}
    symbols_by_id = {str(row.get("symbol_id")): row for row in symbols if row.get("symbol_id")}
    symbol_names_by_path = _symbols_by_path_and_name(symbols)
    relationships: list[dict[str, Any]] = []
    blockers: list[dict[str, Any]] = []
    warnings: list[str] = []
    if not surfaces:
        code = "RELATIONSHIP_PUBLIC_SURFACES_UNAVAILABLE"
        warnings.append(code)
        blockers.append(_blocker(codebase_id, snapshot_id, code, {"ref_type": "codebase", "ref_id": codebase_id, "path": ""}, "No public surface rows were available; graph excludes surface-to-handler relationships."))
    if not mappings:
        code = "RELATIONSHIP_SURFACE_MAPPINGS_UNAVAILABLE"
        warnings.append(code)
        blockers.append(_blocker(codebase_id, snapshot_id, code, {"ref_type": "codebase", "ref_id": codebase_id, "path": ""}, "No surface-to-symbol mappings were available; graph relies on symbols, imports, configs and tests."))
    if not imports:
        code = "RELATIONSHIP_IMPORTS_UNAVAILABLE"
        warnings.append(code)
        blockers.append(_blocker(codebase_id, snapshot_id, code, {"ref_type": "codebase", "ref_id": codebase_id, "path": ""}, "No import rows were available; graph excludes module import relationships."))

    for mapping in mappings:
        relation = str(mapping.get("relation") or "")
        from_id = str(mapping.get("from_id") or "")
        to_id = str(mapping.get("to_id") or "")
        if relation == "HANDLED_BY" and from_id in surfaces_by_id and to_id in symbols_by_id:
            surface = surfaces_by_id[from_id]
            symbol = symbols_by_id[to_id]
            relationships.append(
                _relationship(
                    workspace_id=workspace_id,
                    codebase_id=codebase_id,
                    snapshot_id=snapshot_id,
                    relationship_type="surface_handled_by",
                    source_ref=_surface_ref(surface),
                    target_ref=_symbol_ref(symbol),
                    confidence=float(mapping.get("confidence") or 0.9),
                    semantic_limit="registry_declared",
                    truth_status="accepted",
                    evidence_refs=_evidence_refs(mapping),
                    line_range=_line_range_from_evidence(mapping, evidence_by_id) or symbol.get("line_range"),
                    needs_review=[],
                    blockers=[],
                )
            )
        capability = str(mapping.get("capability_id") or "")
        if capability and capability != "unresolved" and from_id in surfaces_by_id:
            surface = surfaces_by_id[from_id]
            relationships.append(
                _relationship(
                    workspace_id=workspace_id,
                    codebase_id=codebase_id,
                    snapshot_id=snapshot_id,
                    relationship_type="capability_related_to_surface",
                    source_ref={"ref_type": "capability", "ref_id": capability, "path": ""},
                    target_ref=_surface_ref(surface),
                    confidence=0.85,
                    semantic_limit="static_reference",
                    truth_status="accepted",
                    evidence_refs=_evidence_refs(mapping) or _surface_line_refs(surface),
                    line_range=_line_range_from_evidence(mapping, evidence_by_id) or surface.get("line_range"),
                    needs_review=[],
                    blockers=[],
                )
            )

    for surface in surfaces:
        source_file = str(surface.get("source_file") or "")
        if not source_file:
            blockers.append(_blocker(codebase_id, snapshot_id, "SURFACE_SOURCE_FILE_MISSING", _surface_ref(surface), "Surface has no source file."))
            continue
        relationships.append(
            _relationship(
                workspace_id=workspace_id,
                codebase_id=codebase_id,
                snapshot_id=snapshot_id,
                relationship_type="registry_declared",
                source_ref={"ref_type": "file", "ref_id": stable_id("file", source_file), "path": source_file},
                target_ref=_surface_ref(surface),
                confidence=float(surface.get("confidence") or 0.8),
                semantic_limit="registry_declared",
                truth_status="accepted" if surface.get("line_range") else "needs_review",
                evidence_refs=_surface_line_refs(surface),
                line_range=surface.get("line_range"),
                needs_review=[] if surface.get("line_range") else ["surface declaration has no line range"],
                blockers=[],
            )
        )

    relationships.extend(_build_config_declared_relationships(workspace_id, codebase_id, snapshot_id, repo_root, list(navigation_index.get("candidates") or [])))

    for row in imports:
        source_path = str(row.get("path") or "")
        target_module = str(row.get("to_module") or row.get("name") or "")
        if not source_path or not target_module:
            blockers.append(_blocker(codebase_id, snapshot_id, "IMPORT_RELATION_UNRESOLVED", {"ref_type": "file", "ref_id": stable_id("import", row), "path": source_path}, "Import row missing source path or target module."))
            continue
        relationships.append(
            _relationship(
                workspace_id=workspace_id,
                codebase_id=codebase_id,
                snapshot_id=snapshot_id,
                relationship_type="module_imports_module",
                source_ref={"ref_type": "file", "ref_id": str(row.get("from_module") or stable_id("module", source_path)), "path": source_path},
                target_ref={"ref_type": "module", "ref_id": target_module, "path": ""},
                confidence=float(row.get("confidence") or 0.9),
                semantic_limit="static_reference",
                truth_status="accepted",
                evidence_refs=[str(row.get("import_id") or stable_id("import", source_path, target_module))],
                line_range=row.get("line_range"),
                needs_review=[],
                blockers=[],
            )
        )

    relationships.extend(_build_ast_relationships(repo_root, workspace_id, codebase_id, snapshot_id, symbols, symbol_names_by_path, blockers))
    relationships.extend(_build_test_reference_relationships(workspace_id, codebase_id, snapshot_id, list(navigation_index.get("candidates") or []), symbols))

    relationships = _dedupe_relationships(relationships)
    forbidden_count = sum(1 for row in relationships if row.get("relationship_type") in FORBIDDEN_RELATIONSHIP_TYPES)
    summary = {
        "relationship_count": len(relationships),
        "accepted_count": sum(1 for row in relationships if row.get("truth_status") == "accepted"),
        "needs_review_count": sum(1 for row in relationships if row.get("truth_status") == "needs_review"),
        "blocked_count": len(blockers),
        "forbidden_relationship_count": forbidden_count,
        "relationship_type_counts": _counts(relationships, "relationship_type"),
    }
    if not relationships:
        blockers.append(_blocker(codebase_id, snapshot_id, "RELATIONSHIP_GRAPH_EMPTY", {"ref_type": "codebase", "ref_id": codebase_id, "path": ""}, "No lightweight relationships could be built."))
        summary["blocked_count"] = len(blockers)
    return {
        "schema_version": SCHEMA_VERSION,
        "workspace_id": workspace_id,
        "codebase_id": codebase_id,
        "snapshot_id": snapshot_id,
        "created_at": now(),
        "summary": summary,
        "relationships": relationships,
        "relationship_blockers": blockers,
        "source_artifact_refs": [
            {"type": "inventory_surfaces", "artifact_ref": f"inventory-surfaces://{codebase_id}/{snapshot_id}"},
            {"type": "symbols", "artifact_ref": f"symbols://{codebase_id}/{snapshot_id}"},
            {"type": "imports", "artifact_ref": f"imports://{codebase_id}/{snapshot_id}"},
            {"type": "mappings", "artifact_ref": f"mappings://{codebase_id}/{snapshot_id}"},
            {"type": "task_navigation_index", "artifact_ref": f"coding-agent://{codebase_id}/task_navigation/navigation_index.json"},
        ],
        "evidence_refs": sorted({ref for row in relationships for ref in list(row.get("evidence_refs") or [])})[:500],
        "warnings": warnings,
        "needs_review": sorted({review for row in relationships for review in list(row.get("needs_review") or [])}),
        "blockers": blockers,
    }


def public_relationship_graph_payload(payload: dict[str, Any]) -> dict[str, Any]:
    result = dict(payload)
    result["relationships"] = list(payload.get("relationships") or [])[:500]
    result["relationship_blockers"] = list(payload.get("relationship_blockers") or [])[:200]
    return result


def _relationship(
    *,
    workspace_id: str,
    codebase_id: str,
    snapshot_id: str,
    relationship_type: str,
    source_ref: dict[str, Any],
    target_ref: dict[str, Any],
    confidence: float,
    semantic_limit: str,
    truth_status: str,
    evidence_refs: list[str],
    line_range: Any,
    needs_review: list[str],
    blockers: list[dict[str, Any]],
) -> dict[str, Any]:
    source_path = str(source_ref.get("path") or "")
    target_path = str(target_ref.get("path") or "")
    normalized_evidence = sorted(set(evidence_refs))[:20]
    normalized_needs_review = list(needs_review)
    normalized_truth_status = truth_status
    if truth_status == "accepted":
        missing = []
        if not (source_path or target_path):
            missing.append("repo-relative path")
        if not line_range:
            missing.append("line range")
        if not normalized_evidence:
            missing.append("evidence refs")
        if missing:
            normalized_truth_status = "needs_review"
            normalized_needs_review.append("accepted relationship missing " + ", ".join(missing))
    return {
        "schema_version": SCHEMA_VERSION,
        "workspace_id": workspace_id,
        "codebase_id": codebase_id,
        "snapshot_id": snapshot_id,
        "relationship_id": stable_id("rel", relationship_type, source_ref.get("ref_id"), target_ref.get("ref_id"), line_range),
        "relationship_type": relationship_type,
        "source_ref": source_ref,
        "target_ref": target_ref,
        "confidence": round(max(0.0, min(confidence, 1.0)), 3),
        "semantic_limit": semantic_limit,
        "truth_status": normalized_truth_status,
        "evidence_refs": normalized_evidence,
        "line_range": line_range,
        "needs_review": normalized_needs_review,
        "blockers": blockers,
    }


def _surface_ref(surface: dict[str, Any]) -> dict[str, Any]:
    return {"ref_type": "surface", "ref_id": str(surface.get("surface_id") or ""), "path": str(surface.get("source_file") or "")}


def _symbol_ref(symbol: dict[str, Any]) -> dict[str, Any]:
    return {"ref_type": "symbol", "ref_id": str(symbol.get("symbol_id") or ""), "path": str(symbol.get("path") or "")}


def _evidence_refs(mapping: dict[str, Any]) -> list[str]:
    return [str(item) for item in list(mapping.get("evidence_ids") or []) if item]


def _surface_line_refs(surface: dict[str, Any]) -> list[str]:
    line_range = surface.get("line_range")
    source_file = str(surface.get("source_file") or "")
    surface_id = str(surface.get("surface_id") or "")
    if not source_file or not line_range:
        return []
    return [stable_id("surface_line", surface_id, source_file, line_range)]


def _line_range_from_evidence(mapping: dict[str, Any], evidence_by_id: dict[str, dict[str, Any]]) -> Any:
    for evidence_id in _evidence_refs(mapping):
        row = evidence_by_id.get(evidence_id)
        if row:
            return [row.get("start_line"), row.get("end_line")]
    return None


def _symbols_by_path_and_name(symbols: list[dict[str, Any]]) -> dict[str, dict[str, dict[str, Any]]]:
    result: dict[str, dict[str, dict[str, Any]]] = {}
    for symbol in symbols:
        path = str(symbol.get("path") or "")
        name = str(symbol.get("name") or "").split(".")[-1]
        if path and name:
            result.setdefault(path, {})[name] = symbol
    return result


def _build_ast_relationships(
    repo_root: Path,
    workspace_id: str,
    codebase_id: str,
    snapshot_id: str,
    symbols: list[dict[str, Any]],
    symbol_names_by_path: dict[str, dict[str, dict[str, Any]]],
    blockers: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    relationships: list[dict[str, Any]] = []
    symbols_by_path = {}
    for symbol in symbols:
        if symbol.get("kind") in {"function", "method"} and symbol.get("path"):
            symbols_by_path.setdefault(str(symbol.get("path")), []).append(symbol)
    for path, path_symbols in list(symbols_by_path.items())[:300]:
        file_path = repo_root / path
        if not file_path.exists() or file_path.suffix != ".py":
            continue
        try:
            tree = ast.parse(file_path.read_text(encoding="utf-8"), filename=path)
        except (SyntaxError, UnicodeDecodeError, OSError) as exc:
            blockers.append(_blocker(codebase_id, snapshot_id, "AST_PARSE_UNAVAILABLE", {"ref_type": "file", "ref_id": stable_id("file", path), "path": path}, str(exc)))
            continue
        symbols_by_start = {int((symbol.get("line_range") or [0])[0] or 0): symbol for symbol in path_symbols}
        known_names = symbol_names_by_path.get(path, {})
        for node in ast.walk(tree):
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            source_symbol = symbols_by_start.get(int(getattr(node, "lineno", 0)))
            if not source_symbol:
                continue
            for child in ast.walk(node):
                if not isinstance(child, ast.Call):
                    continue
                if isinstance(child.func, ast.Name) and child.func.id in known_names:
                    target_symbol = known_names[child.func.id]
                    if target_symbol.get("symbol_id") == source_symbol.get("symbol_id"):
                        continue
                    relationships.append(
                        _relationship(
                            workspace_id=workspace_id,
                            codebase_id=codebase_id,
                            snapshot_id=snapshot_id,
                            relationship_type="direct_call_ast",
                            source_ref=_symbol_ref(source_symbol),
                            target_ref=_symbol_ref(target_symbol),
                            confidence=0.8,
                            semantic_limit="direct_syntax",
                            truth_status="accepted",
                            evidence_refs=[stable_id("astline", path, getattr(child, "lineno", 0), child.func.id)],
                            line_range=[getattr(child, "lineno", 0), getattr(child, "lineno", 0)],
                            needs_review=["direct AST syntax does not prove runtime dispatch"],
                            blockers=[],
                        )
                    )
                elif isinstance(child.func, ast.Attribute):
                    blockers.append(
                        _blocker(
                            codebase_id,
                            snapshot_id,
                            "DYNAMIC_ATTRIBUTE_CALL_UNRESOLVED",
                            _symbol_ref(source_symbol),
                            f"Attribute call `{child.func.attr}` requires runtime/type context.",
                        )
                    )
    return relationships[:5000]


def _build_test_reference_relationships(
    workspace_id: str,
    codebase_id: str,
    snapshot_id: str,
    candidates: list[dict[str, Any]],
    symbols: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    tests = [item for item in candidates if item.get("candidate_type") == "test"]
    relationships: list[dict[str, Any]] = []
    for test in tests[:300]:
        test_path = str(test.get("path") or "")
        if not test_path:
            continue
        normalized = test_path.lower().replace("_test", "").replace("test_", "")
        for symbol in symbols:
            symbol_path = str(symbol.get("path") or "")
            if not symbol_path or symbol_path == test_path:
                continue
            module_hint = Path(symbol_path).stem.lower()
            if module_hint and module_hint in normalized:
                relationships.append(
                    _relationship(
                        workspace_id=workspace_id,
                        codebase_id=codebase_id,
                        snapshot_id=snapshot_id,
                        relationship_type="test_references_symbol",
                        source_ref={"ref_type": "test", "ref_id": str(test.get("candidate_id") or stable_id("test", test_path)), "path": test_path},
                        target_ref=_symbol_ref(symbol),
                        confidence=0.65,
                        semantic_limit="test_reference",
                        truth_status="needs_review",
                        evidence_refs=list(test.get("evidence_refs") or []),
                        line_range=None,
                        needs_review=["test reference inferred from path naming; review before treating as coverage"],
                        blockers=[],
                    )
                )
                break
    return relationships


def _build_config_declared_relationships(
    workspace_id: str,
    codebase_id: str,
    snapshot_id: str,
    repo_root: Path,
    candidates: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    relationships: list[dict[str, Any]] = []
    for candidate in candidates:
        if candidate.get("candidate_type") != "config":
            continue
        path = str(candidate.get("path") or "")
        if not path:
            continue
        line_range = [1, 1] if (repo_root / path).exists() else None
        relationships.append(
            _relationship(
                workspace_id=workspace_id,
                codebase_id=codebase_id,
                snapshot_id=snapshot_id,
                relationship_type="config_declared",
                source_ref={"ref_type": "config", "ref_id": str(candidate.get("candidate_id") or stable_id("config", path)), "path": path},
                target_ref={"ref_type": "codebase", "ref_id": codebase_id, "path": ""},
                confidence=0.75,
                semantic_limit="config_declared",
                truth_status="accepted" if line_range else "needs_review",
                evidence_refs=list(candidate.get("evidence_refs") or []) or ([stable_id("config_line", path, line_range)] if line_range else []),
                line_range=line_range,
                needs_review=[] if line_range else ["config path could not be verified on disk"],
                blockers=[],
            )
        )
    return relationships


def _dedupe_relationships(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen = set()
    result = []
    for row in rows:
        key = str(row.get("relationship_id"))
        if key in seen:
            continue
        seen.add(key)
        result.append(row)
    return result


def _blocker(codebase_id: str, snapshot_id: str, code: str, ref: dict[str, Any], message: str) -> dict[str, Any]:
    return {
        "blocker_id": stable_id("relblock", codebase_id, snapshot_id, code, ref.get("ref_id"), message),
        "code": code,
        "message": message,
        "source_ref": ref,
        "retryable": False,
    }


def _counts(rows: list[dict[str, Any]], key: str) -> dict[str, int]:
    result: dict[str, int] = {}
    for row in rows:
        value = str(row.get(key) or "unknown")
        result[value] = result.get(value, 0) + 1
    return dict(sorted(result.items()))

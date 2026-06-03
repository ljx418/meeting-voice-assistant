"""Context selection from accepted V2 project intelligence artifacts."""

from __future__ import annotations

from typing import Any

from .ranker import keywords, rank_items, score_text


def select_context_items(
    *,
    overview: dict[str, Any],
    inventory: dict[str, Any],
    symbol_index: dict[str, Any],
    trace: dict[str, Any],
    mode: str,
    task: str | None,
    focus: dict[str, Any] | None,
    include: list[str] | None,
) -> dict[str, Any]:
    task_keywords = keywords(task)
    focus_values = _focus_values(focus)
    surfaces = inventory.get("surfaces", [])
    capabilities = inventory.get("capabilities", [])
    symbols = symbol_index.get("symbols", [])
    evidence = trace.get("evidence", [])
    evidence_by_capability = _evidence_by_capability(evidence)
    evidence_by_file = _evidence_by_file(evidence)

    selected_capabilities = _select_capabilities(capabilities, evidence_by_capability, task_keywords, focus_values, mode)
    selected_surfaces = _select_surfaces(surfaces, selected_capabilities, task_keywords, focus_values, mode)
    selected_symbols = _select_symbols(symbols, selected_surfaces, task_keywords, focus_values, mode)
    selected_files = _select_files(overview, selected_surfaces, selected_symbols, evidence_by_file)
    selected_evidence = _select_evidence(evidence, selected_capabilities, selected_surfaces, selected_symbols, limit=40)
    guidance = _guidance(mode, task, selected_capabilities, selected_surfaces, selected_symbols, selected_evidence)
    risks = _risks(overview)
    tests = _suggested_tests(symbols, selected_files, selected_evidence)
    next_steps = _next_steps(mode, selected_capabilities, selected_surfaces, selected_symbols, selected_evidence)
    sections = _sections(include)

    return {
        "sections": sections,
        "task_interpretation": _task_interpretation(mode, task, selected_capabilities),
        "relevant_capabilities": selected_capabilities,
        "relevant_public_surface": selected_surfaces,
        "relevant_files": selected_files,
        "relevant_symbols": selected_symbols,
        "implementation_guidance": guidance,
        "risks": risks,
        "suggested_tests": tests,
        "recommended_next_steps": next_steps,
        "evidence": selected_evidence,
    }


def _select_capabilities(
    capabilities: list[dict[str, Any]],
    evidence_by_capability: dict[str, list[dict[str, Any]]],
    task_keywords: set[str],
    focus_values: set[str],
    mode: str,
) -> list[dict[str, Any]]:
    ranked = rank_items(capabilities, task_keywords=task_keywords, focus_values=focus_values)
    if mode == "project_brief":
        ranked = sorted(ranked, key=lambda item: (-int(item.get("surface_count") or 0), str(item.get("capability_id") or "")))
    result = []
    for item in ranked[:10]:
        capability_id = str(item.get("capability_id") or "")
        surface_count = item.get("surface_count")
        if surface_count is None and isinstance(item.get("surface_counts"), dict):
            surface_count = sum(int(value or 0) for value in item["surface_counts"].values())
        result.append(
            {
                "capability_id": capability_id,
                "surface_count": surface_count or 0,
                "surface_types": item.get("surface_types", []) or sorted((item.get("surface_counts") or {}).keys()),
                "evidence": [_public_evidence(row) for row in evidence_by_capability.get(capability_id, [])[:3]],
                "needs_review": not bool(evidence_by_capability.get(capability_id)),
            }
        )
    return result


def _select_surfaces(
    surfaces: list[dict[str, Any]],
    capabilities: list[dict[str, Any]],
    task_keywords: set[str],
    focus_values: set[str],
    mode: str,
) -> list[dict[str, Any]]:
    capability_ids = {str(item.get("capability_id")) for item in capabilities}
    candidates = [item for item in surfaces if item.get("capability_id") in capability_ids]
    if mode == "task_context" and task_keywords:
        matched = [item for item in surfaces if score_text(" ".join(str(value) for value in item.values()), task_keywords) > 0]
        candidates = _dedupe([*matched, *candidates], "surface_id")
    ranked = rank_items(candidates, task_keywords=task_keywords, focus_values=focus_values)
    return [_public_surface(item) for item in ranked[:16]]


def _select_symbols(
    symbols: list[dict[str, Any]],
    surfaces: list[dict[str, Any]],
    task_keywords: set[str],
    focus_values: set[str],
    mode: str,
) -> list[dict[str, Any]]:
    surface_files = {str(item.get("source_file") or "") for item in surfaces}
    candidates = [item for item in symbols if str(item.get("path") or item.get("source_file") or "") in surface_files]
    if mode == "task_context" and task_keywords:
        candidates = _dedupe(
            [item for item in symbols if score_text(str(item.get("qualified_name") or ""), task_keywords) > 0] + candidates,
            "symbol_id",
        )
    ranked = rank_items(candidates, task_keywords=task_keywords, focus_values=focus_values)
    return [_public_symbol(item) for item in ranked[:20]]


def _select_files(
    overview: dict[str, Any],
    surfaces: list[dict[str, Any]],
    symbols: list[dict[str, Any]],
    evidence_by_file: dict[str, list[dict[str, Any]]],
) -> list[dict[str, Any]]:
    paths = []
    paths.extend(str(item.get("source_file") or "") for item in surfaces)
    paths.extend(str(item.get("source_file") or "") for item in symbols)
    paths.extend(str(item.get("source_file") or "") for item in overview.get("core_modules", [])[:8])
    result = []
    for path in [item for item in dict.fromkeys(paths) if item]:
        result.append(
            {
                "path": path,
                "evidence": [_public_evidence(row) for row in evidence_by_file.get(path, [])[:3]] or [{"source_file": path, "needs_review": True}],
            }
        )
    return result[:20]


def _select_evidence(
    evidence: list[dict[str, Any]],
    capabilities: list[dict[str, Any]],
    surfaces: list[dict[str, Any]],
    symbols: list[dict[str, Any]],
    *,
    limit: int,
) -> list[dict[str, Any]]:
    capability_ids = {str(item.get("capability_id")) for item in capabilities}
    surface_ids = {str(item.get("surface_id")) for item in surfaces}
    symbol_ids = {str(item.get("symbol_id")) for item in symbols}
    selected = [
        row
        for row in evidence
        if row.get("capability_id") in capability_ids or row.get("surface_id") in surface_ids or row.get("symbol_id") in symbol_ids
    ]
    return [_public_evidence(row) for row in selected[:limit]]


def _guidance(
    mode: str,
    task: str | None,
    capabilities: list[dict[str, Any]],
    surfaces: list[dict[str, Any]],
    symbols: list[dict[str, Any]],
    evidence: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    evidence_refs = _evidence_refs(evidence)
    if mode == "project_brief":
        return [
            _claim("Use the snapshot, inventory, symbols, and trace artifacts as the project fact base.", evidence_refs),
            _claim("Review public surfaces and capability alignment before changing cross-interface behavior.", evidence_refs),
        ]
    target = task or "development task"
    return [
        _claim(f"For `{target}`, start from the related public surfaces before editing implementation files.", evidence_refs),
        _claim("Update HTTP, MCP, CLI, and regression tests together when a public capability changes.", evidence_refs),
        _claim("Preserve evidence line ranges and rerun the V2 real-repo acceptance flow after implementation.", evidence_refs),
    ]


def _risks(overview: dict[str, Any]) -> list[dict[str, Any]]:
    risks = []
    for item in overview.get("known_risks", [])[:8]:
        risk = {
            "risk_id": item.get("risk_id"),
            "summary": item.get("summary"),
            "evidence": item.get("evidence", []),
            "needs_review": item.get("needs_review", False) or not bool(item.get("evidence")),
        }
        risks.append(risk)
    if not risks:
        risks.append({"risk_id": "needs_human_review", "summary": "No deterministic risk was selected; human review is still required.", "needs_review": True, "evidence": []})
    return risks


def _suggested_tests(symbols: list[dict[str, Any]], files: list[dict[str, Any]], evidence: list[dict[str, Any]]) -> list[dict[str, Any]]:
    evidence_refs = _evidence_refs(evidence)
    test_files = [item for item in symbols if str(item.get("path") or "").startswith("backend/tests/")]
    suggestions = []
    for item in test_files[:6]:
        suggestions.append(
            _claim(f"Run or extend `{item.get('path')}` for related backend coverage.", evidence_refs or item.get("evidence", []))
        )
    if not suggestions:
        paths = [item["path"] for item in files if str(item.get("path") or "").startswith("backend/tests/")]
        for path in paths[:3]:
            suggestions.append(_claim(f"Run or extend `{path}`.", evidence_refs))
    if not suggestions:
        suggestions.append(_claim("Run the V2 codebase regression tests for changed project-intelligence behavior.", evidence_refs))
    return suggestions


def _next_steps(
    mode: str,
    capabilities: list[dict[str, Any]],
    surfaces: list[dict[str, Any]],
    symbols: list[dict[str, Any]],
    evidence: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    evidence_refs = _evidence_refs(evidence)
    steps = [
        _claim("Inspect the selected files and symbols before editing.", evidence_refs),
        _claim("Check HTTP/MCP/CLI alignment for any changed public capability.", evidence_refs),
        _claim("Run targeted V2 tests and then the relevant V1 regression suite.", evidence_refs),
    ]
    if mode == "project_brief":
        steps.insert(0, _claim("Use the project overview as the first context block for downstream agents.", evidence_refs))
    return steps


def _task_interpretation(mode: str, task: str | None, capabilities: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "mode": mode,
        "task": task,
        "matched_capabilities": [item.get("capability_id") for item in capabilities[:6]],
        "needs_review": mode == "task_context" and not capabilities,
    }


def _sections(include: list[str] | None) -> list[str]:
    default = [
        "project_summary",
        "relevant_capabilities",
        "relevant_public_surface",
        "relevant_files",
        "relevant_symbols",
        "implementation_guidance",
        "risks",
        "suggested_tests",
        "recommended_next_steps",
        "evidence",
    ]
    return [item for item in default if not include or item in include]


def _evidence_by_capability(evidence: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    result: dict[str, list[dict[str, Any]]] = {}
    for row in evidence:
        result.setdefault(str(row.get("capability_id") or ""), []).append(row)
    return result


def _evidence_by_file(evidence: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    result: dict[str, list[dict[str, Any]]] = {}
    for row in evidence:
        result.setdefault(str(row.get("path") or row.get("source_file") or ""), []).append(row)
    return result


def _focus_values(focus: dict[str, Any] | None) -> set[str]:
    values = set()
    for value in (focus or {}).values():
        if isinstance(value, list):
            values.update(str(item) for item in value)
        elif value:
            values.add(str(value))
    return values


def _public_surface(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "surface_id": item.get("surface_id"),
        "surface_type": item.get("surface_type"),
        "name": item.get("name"),
        "capability_id": item.get("capability_id"),
        "source_file": item.get("source_file"),
        "line_range": item.get("line_range"),
        "stability": item.get("stability"),
    }


def _public_symbol(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "symbol_id": item.get("symbol_id"),
        "kind": item.get("kind"),
        "name": item.get("name"),
        "qualified_name": item.get("qualified_name"),
        "source_file": item.get("path") or item.get("source_file"),
        "line_range": item.get("line_range"),
        "signature": item.get("signature"),
    }


def _public_evidence(row: dict[str, Any]) -> dict[str, Any]:
    payload = dict(row)
    if "path" in payload:
        payload["source_file"] = payload.pop("path")
    return payload


def _evidence_refs(evidence: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return evidence[:5]


def _claim(summary: str, evidence: list[dict[str, Any]]) -> dict[str, Any]:
    return {"summary": summary, "evidence": evidence, "needs_review": not bool(evidence)}


def _dedupe(items: list[dict[str, Any]], key: str) -> list[dict[str, Any]]:
    seen = set()
    result = []
    for item in items:
        value = str(item.get(key) or "")
        if not value or value in seen:
            continue
        seen.add(value)
        result.append(item)
    return result

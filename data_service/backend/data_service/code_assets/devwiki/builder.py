"""Deterministic DevWiki page builder."""

from __future__ import annotations

from typing import Any

from .model import make_section, page_id
from .planner import PAGE_TITLES, required_pages


def build_pages(
    *,
    workspace_id: str,
    codebase_id: str,
    snapshot_id: str,
    overview: dict[str, Any],
    inventory: dict[str, Any],
    symbols: dict[str, Any],
    trace: dict[str, Any],
    created_at: str,
) -> list[dict[str, Any]]:
    pages = []
    for plan in required_pages():
        slug = plan["slug"]
        sections = _sections_for(slug, overview=overview, inventory=inventory, symbols=symbols, trace=trace)
        evidence = _dedupe_evidence([item for section in sections for item in section.get("evidence", [])])
        needs_review = [item for section in sections for item in section.get("needs_review", [])]
        page = {
            "schema_version": "v2.1",
            "workspace_id": workspace_id,
            "codebase_id": codebase_id,
            "snapshot_id": snapshot_id,
            "page_id": page_id(slug),
            "slug": slug,
            "title": PAGE_TITLES[slug],
            "sections": sections,
            "evidence": evidence,
            "needs_review": needs_review,
            "source_artifact_refs": _dedupe_refs([ref for section in sections for ref in section.get("source_artifact_refs", [])]),
            "stale": False,
            "confidence": _page_confidence(sections),
            "created_at": created_at,
            "updated_at": created_at,
        }
        pages.append(page)
    return pages


def _sections_for(
    slug: str,
    *,
    overview: dict[str, Any],
    inventory: dict[str, Any],
    symbols: dict[str, Any],
    trace: dict[str, Any],
) -> list[dict[str, Any]]:
    if slug == "project-overview":
        return _project_overview_sections(overview)
    if slug == "architecture":
        return _architecture_sections(overview, symbols, trace)
    if slug == "public-surface":
        return _surface_sections(inventory)
    if slug == "http-api":
        return _surface_type_sections(inventory, "http_api", "HTTP API")
    if slug == "mcp-tools":
        return _surface_type_sections(inventory, "mcp_tool", "MCP Tools")
    if slug == "cli":
        return _surface_type_sections(inventory, "cli_command", "CLI Commands")
    if slug == "storage":
        return _storage_sections(overview)
    if slug == "build-pipeline":
        return _build_pipeline_sections(overview, trace)
    if slug == "developer-onboarding":
        return _onboarding_sections(overview, inventory, symbols)
    return [_needs_review_section(slug, "No deterministic section planner exists for this page.")]


def _project_overview_sections(overview: dict[str, Any]) -> list[dict[str, Any]]:
    refs = list(overview.get("source_artifact_refs") or overview.get("artifact_refs") or [])
    evidence = _evidence(overview)
    return [
        make_section(
            section_id="project-one-liner",
            title="Project One-liner",
            body=str(overview.get("project_one_liner") or ""),
            generated_from="overview",
            source_artifact_refs=refs,
            evidence=evidence[:8],
            needs_review=_needs_review(overview),
            confidence=float(overview.get("confidence") or 0.8),
        ),
        make_section(
            section_id="entrypoints",
            title="Entrypoints",
            body=_list_body([_path_label(item) for item in list(overview.get("entrypoints") or [])[:12]]),
            generated_from="overview",
            source_artifact_refs=refs,
            evidence=_items_evidence(overview.get("entrypoints") or []) or evidence[:3],
            confidence=0.9,
        ),
        make_section(
            section_id="risks",
            title="Known Risks",
            body=_list_body([str(item.get("summary") or item.get("reason") or item) for item in list(overview.get("known_risks") or [])[:12]]),
            generated_from="overview",
            source_artifact_refs=refs,
            evidence=_items_evidence(overview.get("known_risks") or []) or evidence[:3],
            needs_review=_needs_review(overview),
            confidence=0.8,
        ),
    ]


def _architecture_sections(overview: dict[str, Any], symbols: dict[str, Any], trace: dict[str, Any]) -> list[dict[str, Any]]:
    symbol_summary = symbols.get("summary") or {}
    trace_summary = trace.get("summary") or {}
    refs = _dedupe_refs(list(overview.get("source_artifact_refs") or []) + list(symbol_summary.get("artifact_refs") or []) + list(trace_summary.get("artifact_refs") or []))
    core_modules = overview.get("core_modules") or []
    return [
        make_section(
            section_id="core-modules",
            title="Core Modules",
            body=_list_body([f"{item.get('qualified_name')} ({item.get('source_file')})" for item in core_modules[:12]]),
            generated_from="symbols",
            source_artifact_refs=refs,
            evidence=_items_evidence(core_modules) or _evidence(overview)[:5],
            confidence=0.85,
        ),
        make_section(
            section_id="dependency-shape",
            title="Dependency Shape",
            body=(
                f"Symbol index contains {symbol_summary.get('symbol_count', 0)} symbols and "
                f"{symbol_summary.get('import_count', 0)} imports; trace evidence contains "
                f"{trace_summary.get('evidence_count', 0)} evidence records."
            ),
            generated_from="symbols",
            source_artifact_refs=refs,
            evidence=_artifact_evidence_refs(refs),
            confidence=0.9,
        ),
    ]


def _surface_sections(inventory: dict[str, Any]) -> list[dict[str, Any]]:
    summary = inventory.get("summary") or {}
    capabilities = inventory.get("capabilities") or []
    refs = list(summary.get("artifact_refs") or [])
    return [
        make_section(
            section_id="surface-counts",
            title="Surface Counts",
            body=f"Detected {summary.get('surface_count', 0)} public surfaces across {summary.get('surface_counts', {})}.",
            generated_from="inventory",
            source_artifact_refs=refs,
            evidence=_artifact_evidence_refs(refs),
            needs_review=_unresolved_review(summary),
            confidence=0.95,
        ),
        make_section(
            section_id="capabilities",
            title="Capabilities",
            body=_list_body([f"{item.get('capability_id')}: {item.get('surface_count')} surfaces" for item in capabilities[:20]]),
            generated_from="inventory",
            source_artifact_refs=refs,
            evidence=_artifact_evidence_refs(refs),
            needs_review=_unresolved_review(summary),
            confidence=0.9,
        ),
    ]


def _surface_type_sections(inventory: dict[str, Any], surface_type: str, title: str) -> list[dict[str, Any]]:
    summary = inventory.get("summary") or {}
    refs = list(summary.get("artifact_refs") or [])
    surfaces = [item for item in inventory.get("surfaces", []) if item.get("surface_type") == surface_type]
    body_items = [_surface_label(item) for item in surfaces[:50]]
    section = make_section(
        section_id=surface_type,
        title=title,
        body=_list_body(body_items),
        generated_from="inventory",
        source_artifact_refs=refs,
        evidence=_surface_evidence(surfaces) or _artifact_evidence_refs(refs),
        needs_review=[] if surfaces else [{"code": "NO_SURFACES", "reason": f"No {surface_type} surfaces detected."}],
        confidence=0.95 if surfaces else 0.65,
    )
    return [section]


def _storage_sections(overview: dict[str, Any]) -> list[dict[str, Any]]:
    storage = overview.get("storage_summary") or {}
    refs = list(overview.get("artifact_refs") or [])
    return [
        make_section(
            section_id="artifact-layout",
            title="Artifact Layout",
            body=_list_body([f"{key}: {value}" for key, value in storage.items() if key != "evidence"]),
            generated_from="overview",
            source_artifact_refs=refs,
            evidence=list(storage.get("evidence") or []) or _artifact_evidence_refs(refs),
            confidence=0.9,
        )
    ]


def _build_pipeline_sections(overview: dict[str, Any], trace: dict[str, Any]) -> list[dict[str, Any]]:
    refs = _dedupe_refs(list(overview.get("source_artifact_refs") or []) + list((trace.get("summary") or {}).get("artifact_refs") or []))
    return [
        make_section(
            section_id="pipeline",
            title="Pipeline",
            body="Codebase import -> snapshot -> inventory -> symbol index -> evidence trace -> overview -> context pack -> DevWiki.",
            generated_from="overview",
            source_artifact_refs=refs,
            evidence=_artifact_evidence_refs(refs),
            confidence=0.85,
        )
    ]


def _onboarding_sections(overview: dict[str, Any], inventory: dict[str, Any], symbols: dict[str, Any]) -> list[dict[str, Any]]:
    refs = _dedupe_refs(list(overview.get("source_artifact_refs") or []) + list((inventory.get("summary") or {}).get("artifact_refs") or []) + list((symbols.get("summary") or {}).get("artifact_refs") or []))
    return [
        make_section(
            section_id="first-files",
            title="First Files To Read",
            body=_list_body([_path_label(item) for item in list(overview.get("entrypoints") or [])[:8]] + [str(item.get("source_file")) for item in list(overview.get("core_modules") or [])[:8]]),
            generated_from="overview",
            source_artifact_refs=refs,
            evidence=_items_evidence(overview.get("entrypoints") or []) + _items_evidence(overview.get("core_modules") or []),
            confidence=0.85,
        ),
        make_section(
            section_id="agent-actions",
            title="Agent Actions",
            body="Use project overview for orientation, public surface inventory for API/tool boundaries, symbols for implementation entry points, and trace for evidence.",
            generated_from="overview",
            source_artifact_refs=refs,
            evidence=_artifact_evidence_refs(refs),
            confidence=0.8,
        ),
    ]


def _needs_review_section(slug: str, reason: str) -> dict[str, Any]:
    return make_section(
        section_id=f"{slug}-needs-review",
        title="Needs Review",
        body=reason,
        generated_from="manual_rule",
        needs_review=[{"code": "SECTION_PLANNER_MISSING", "reason": reason}],
        confidence=0.2,
    )


def _surface_label(surface: dict[str, Any]) -> str:
    if surface.get("surface_type") == "http_api":
        return f"{surface.get('method')} {surface.get('path')} -> {surface.get('handler')}"
    if surface.get("surface_type") == "mcp_tool":
        return str(surface.get("tool_name") or surface.get("name") or surface.get("surface_id"))
    if surface.get("surface_type") == "cli_command":
        return str(surface.get("command") or surface.get("surface_id"))
    return str(surface.get("surface_id"))


def _path_label(item: dict[str, Any]) -> str:
    return f"{item.get('path') or item.get('source_file')} ({item.get('language') or item.get('qualified_name') or 'artifact'})"


def _list_body(items: list[str]) -> str:
    values = [str(item) for item in items if str(item or "").strip()]
    if not values:
        return "No deterministic items were available; see needs_review."
    return "\n".join(f"- {item}" for item in values)


def _evidence(payload: dict[str, Any]) -> list[dict[str, Any]]:
    return list(payload.get("evidence") or [])


def _needs_review(payload: dict[str, Any]) -> list[dict[str, Any]]:
    return list(payload.get("needs_review") or [])


def _items_evidence(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    result = []
    for item in items:
        result.extend(list(item.get("evidence") or []))
    return _dedupe_evidence(result)


def _surface_evidence(surfaces: list[dict[str, Any]]) -> list[dict[str, Any]]:
    evidence = []
    for item in surfaces[:30]:
        source_file = item.get("source_file")
        if source_file:
            evidence.append(
                {
                    "type": "source_file",
                    "path": source_file,
                    "line_range": item.get("line_range"),
                    "surface_id": item.get("surface_id"),
                    "extractor": "public_surface_inventory",
                    "confidence": item.get("confidence", 0.9),
                }
            )
    return evidence


def _artifact_evidence_refs(refs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [{"type": ref.get("type"), "artifact_ref": ref.get("artifact_ref"), "extractor": "artifact_ref"} for ref in refs[:12]]


def _unresolved_review(summary: dict[str, Any]) -> list[dict[str, Any]]:
    if int(summary.get("unresolved_count") or 0) <= 0:
        return []
    return [
        {
            "code": "UNRESOLVED_PUBLIC_SURFACES",
            "reason": "Inventory has public surfaces that require capability review.",
            "evidence": _artifact_evidence_refs(list(summary.get("artifact_refs") or [])),
        }
    ]


def _dedupe_refs(refs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen = set()
    result = []
    for ref in refs:
        key = (str(ref.get("type")), str(ref.get("artifact_ref")))
        if key in seen:
            continue
        seen.add(key)
        result.append(dict(ref))
    return result


def _dedupe_evidence(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen = set()
    result = []
    for item in items:
        key = (
            str(item.get("evidence_id") or ""),
            str(item.get("artifact_ref") or ""),
            str(item.get("path") or item.get("source_file") or ""),
            str(item.get("surface_id") or ""),
        )
        if key in seen:
            continue
        seen.add(key)
        result.append(dict(item))
    return result


def _page_confidence(sections: list[dict[str, Any]]) -> float:
    if not sections:
        return 0.0
    return round(sum(float(section.get("confidence") or 0) for section in sections) / len(sections), 3)

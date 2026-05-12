"""Shared Source Trace contract helpers for current HTTP and future MCP/CLI entrypoints."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .service import DataService


SOURCE_TRACE_LIMIT_MIN = 1
SOURCE_TRACE_LIMIT_MAX = 50
SOURCE_TRACE_LIMIT_DEFAULT = 12


def normalize_source_trace_limit(value: object, *, default: int = SOURCE_TRACE_LIMIT_DEFAULT) -> int:
    try:
        parsed = int(value if value is not None else default)
    except (TypeError, ValueError) as exc:
        raise ValueError("limit must be an integer") from exc
    if parsed < SOURCE_TRACE_LIMIT_MIN or parsed > SOURCE_TRACE_LIMIT_MAX:
        raise ValueError(f"limit must be between {SOURCE_TRACE_LIMIT_MIN} and {SOURCE_TRACE_LIMIT_MAX}")
    return parsed


def normalize_source_id(value: object) -> str:
    source_id = str(value or "").strip()
    if not source_id:
        raise ValueError("source_id is required")
    return source_id


def _markdown_title(path: Path) -> str:
    try:
        for line in path.read_text(encoding="utf-8").splitlines():
            stripped = line.strip()
            if stripped.startswith("#"):
                return stripped.lstrip("#").strip()
    except OSError:
        pass
    return path.stem


def _source_trace_terms(source: dict[str, Any], units: list[dict[str, Any]]) -> set[str]:
    terms: set[str] = set()
    for value in (source.get("source_id"), source.get("title"), source.get("path"), source.get("original_path")):
        text = str(value or "").strip()
        if text:
            terms.add(text)
            terms.add(Path(text).stem)
    for unit in units:
        text = str(unit.get("text") or "").strip()
        if text and len(text) <= 80:
            terms.add(text)
        for value in (unit.get("label"), unit.get("entity"), unit.get("theme"), unit.get("unit_id")):
            text = str(value or "").strip()
            if text:
                terms.add(text)
    return {term for term in terms if len(term) >= 2}


def _text_matches_terms(text: str, terms: set[str]) -> bool:
    lowered = text.lower()
    return any(term.lower() in lowered for term in terms if term)


def source_trace_payload(service: DataService, source_id: object, *, limit: object = SOURCE_TRACE_LIMIT_DEFAULT) -> dict[str, Any]:
    normalized_source_id = normalize_source_id(source_id)
    normalized_limit = normalize_source_trace_limit(limit)
    distill = service.read_distill_bundle(source_id=normalized_source_id, limit=normalized_limit)
    source = distill.get("source")
    if not source:
        raise KeyError(normalized_source_id)
    units = list(distill.get("units", []) or [])
    terms = _source_trace_terms(source, units)

    llmwiki_pages: list[dict[str, Any]] = []
    pages_dir = service.layout.llmwiki_pages_dir
    if pages_dir.exists():
        for page_path in sorted(pages_dir.glob("*.md")):
            try:
                body = page_path.read_text(encoding="utf-8")
            except OSError:
                body = ""
            title = _markdown_title(page_path)
            haystack = f"{page_path.stem}\n{title}\n{body}"
            if _text_matches_terms(haystack, terms):
                llmwiki_pages.append(
                    {
                        "slug": page_path.stem,
                        "title": title,
                        "path": str(page_path),
                        "matched": True,
                        "snippet": body[:320],
                    }
                )
            if len(llmwiki_pages) >= normalized_limit:
                break

    graph = service.get_graph_snapshot(max_nodes=300)
    graph_nodes = []
    for node in graph.get("nodes", []) or []:
        node_text = " ".join(str(node.get(key) or "") for key in ("id", "name", "label", "type", "node_type"))
        if _text_matches_terms(node_text, terms) or any(
            _text_matches_terms(str(unit.get("text", "")), {str(node.get("name") or node.get("label") or "")})
            for unit in units
        ):
            graph_nodes.append(node)
        if len(graph_nodes) >= normalized_limit:
            break
    node_ids = {str(node.get("id")) for node in graph_nodes}
    graph_edges = [
        edge
        for edge in graph.get("edges", []) or []
        if str(edge.get("source")) in node_ids or str(edge.get("target")) in node_ids
    ][:normalized_limit]
    graph_communities = [
        community
        for community in graph.get("communities", []) or []
        if node_ids.intersection({str(item) for item in community.get("entity_ids", []) or community.get("node_ids", []) or []})
        or _text_matches_terms(str(community.get("title") or community.get("summary") or ""), terms)
    ][:normalized_limit]

    return {
        "workspace": str(service.workspace),
        "source_id": normalized_source_id,
        "source": source,
        "distill": {
            "units": units,
            "unit_count": len(units),
            "provenance_summary": source.get("provenance_summary", {}),
            "profile_debug": source.get("profile_debug", {}),
        },
        "llmwiki": {
            "pages": llmwiki_pages,
            "page_count": len(llmwiki_pages),
        },
        "graphrag": {
            "nodes": graph_nodes,
            "edges": graph_edges,
            "communities": graph_communities,
            "node_count": len(graph_nodes),
            "edge_count": len(graph_edges),
            "community_count": len(graph_communities),
            "graph_model_version": graph.get("graph_model_version"),
        },
        "trace_summary": {
            "source_title": source.get("title") or normalized_source_id,
            "unit_count": len(units),
            "llmwiki_page_count": len(llmwiki_pages),
            "graph_node_count": len(graph_nodes),
            "graph_community_count": len(graph_communities),
        },
    }

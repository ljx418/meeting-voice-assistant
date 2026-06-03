"""Architecture model builder for V2.3."""

from __future__ import annotations

from collections import Counter
from typing import Any

from data_service.mcp_common import now

from .model import ARCHITECTURE_SCHEMA_VERSION, architecture_edge, architecture_node, stable_id


def build_architecture_model(*, workspace_id: str, codebase_id: str, snapshot_id: str, sources: list[dict[str, Any]], parsed_sources: list[dict[str, Any]]) -> dict[str, Any]:
    source_by_id = {str(source["source_id"]): source for source in sources}
    nodes: list[dict[str, Any]] = []
    edges: list[dict[str, Any]] = []
    raw_to_node_id: dict[tuple[str, str], str] = {}
    created_at = now()
    for parsed in parsed_sources:
        source_id = str(parsed.get("source_id") or "")
        source = source_by_id.get(source_id)
        if not source:
            continue
        rel = str(source["path"])
        if parsed.get("source_type") == "drawio":
            for diagram in parsed.get("diagrams", []):
                diagram_node = architecture_node(
                    workspace_id=workspace_id,
                    codebase_id=codebase_id,
                    snapshot_id=snapshot_id,
                    natural_id=f"{rel}:{diagram.get('diagram_id')}",
                    node_type="System",
                    label=str(diagram.get("name") or rel),
                    source_id=source_id,
                    source_path=rel,
                    evidence=_source_evidence(rel),
                    confidence=0.9,
                    data={"diagram_id": diagram.get("diagram_id")},
                )
                nodes.append(diagram_node)
                for raw in diagram.get("nodes", []):
                    item = architecture_node(
                        workspace_id=workspace_id,
                        codebase_id=codebase_id,
                        snapshot_id=snapshot_id,
                        natural_id=f"{rel}:{diagram.get('diagram_id')}:{raw.get('raw_id')}",
                        node_type=str(raw.get("node_type") or "Component"),
                        label=str(raw.get("label") or raw.get("raw_id")),
                        status=str(raw.get("status") or "unknown"),
                        source_id=source_id,
                        source_path=rel,
                        evidence=_source_evidence(rel),
                        confidence=0.85,
                        data={"raw_id": raw.get("raw_id"), "diagram_id": diagram.get("diagram_id")},
                    )
                    nodes.append(item)
                    raw_to_node_id[(source_id, str(raw.get("raw_id")))] = item["node_id"]
                    edges.append(
                        architecture_edge(
                            workspace_id=workspace_id,
                            codebase_id=codebase_id,
                            snapshot_id=snapshot_id,
                            relation="CONTAINS",
                            from_id=diagram_node["node_id"],
                            to_id=item["node_id"],
                            source_id=source_id,
                            evidence=_source_evidence(rel),
                            confidence=0.8,
                        )
                    )
                for raw_edge in diagram.get("edges", []):
                    from_id = raw_to_node_id.get((source_id, str(raw_edge.get("source"))))
                    to_id = raw_to_node_id.get((source_id, str(raw_edge.get("target"))))
                    if from_id and to_id:
                        edges.append(
                            architecture_edge(
                                workspace_id=workspace_id,
                                codebase_id=codebase_id,
                                snapshot_id=snapshot_id,
                                relation=_relation_from_label(str(raw_edge.get("label") or "")),
                                from_id=from_id,
                                to_id=to_id,
                                source_id=source_id,
                                evidence=_source_evidence(rel),
                                confidence=0.75,
                                data={"raw_id": raw_edge.get("raw_id")},
                            )
                        )
        else:
            parent_by_level: dict[int, str] = {}
            for raw in parsed.get("nodes", []):
                level = int(raw.get("level") or 1)
                item = architecture_node(
                    workspace_id=workspace_id,
                    codebase_id=codebase_id,
                    snapshot_id=snapshot_id,
                    natural_id=f"{rel}:heading:{raw.get('line_range', [''])[0]}:{raw.get('label')}",
                    node_type=str(raw.get("node_type") or "Component"),
                    label=str(raw.get("label") or ""),
                    source_id=source_id,
                    source_path=rel,
                    evidence=[{"type": "source_file", "path": rel, "line_range": raw.get("line_range"), "extractor": "markdown_architecture_parser"}],
                    confidence=0.7,
                    data={"heading_level": level},
                )
                nodes.append(item)
                parent_level = max([candidate for candidate in parent_by_level if candidate < level], default=0)
                if parent_level:
                    edges.append(architecture_edge(workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=snapshot_id, relation="CONTAINS", from_id=parent_by_level[parent_level], to_id=item["node_id"], source_id=source_id, evidence=item["evidence"], confidence=0.7))
                parent_by_level[level] = item["node_id"]
    nodes = _dedupe(nodes, "node_id")
    edges = _dedupe(edges, "edge_id")
    summary = _summary(workspace_id, codebase_id, snapshot_id, sources, nodes, edges, created_at)
    return {"schema_version": ARCHITECTURE_SCHEMA_VERSION, "workspace_id": workspace_id, "codebase_id": codebase_id, "snapshot_id": snapshot_id, "created_at": created_at, "updated_at": created_at, "sources": sources, "design_nodes": nodes, "design_edges": edges, "summary": summary, "source_artifact_refs": _source_refs(sources)}


def _source_evidence(path: str) -> list[dict[str, Any]]:
    return [{"type": "source_file", "path": path, "extractor": "architecture_model_builder"}]


def _relation_from_label(label: str) -> str:
    low = label.lower()
    if "govern" in low or "治理" in label:
        return "GOVERNED_BY"
    if "produce" in low or "输出" in label:
        return "PRODUCES"
    if "consume" in low or "输入" in label:
        return "CONSUMES"
    if "document" in low or "文档" in label:
        return "DOCUMENTS"
    if "conflict" in low or "禁止" in label:
        return "CONFLICTS_WITH"
    return "DEPENDS_ON"


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


def _summary(workspace_id: str, codebase_id: str, snapshot_id: str, sources: list[dict[str, Any]], nodes: list[dict[str, Any]], edges: list[dict[str, Any]], created_at: str) -> dict[str, Any]:
    return {
        "schema_version": ARCHITECTURE_SCHEMA_VERSION,
        "workspace_id": workspace_id,
        "codebase_id": codebase_id,
        "snapshot_id": snapshot_id,
        "created_at": created_at,
        "source_count": len(sources),
        "design_node_count": len(nodes),
        "design_edge_count": len(edges),
        "node_counts": dict(sorted(Counter(item.get("node_type") for item in nodes).items())),
        "edge_counts": dict(sorted(Counter(item.get("relation") for item in edges).items())),
    }


def _source_refs(sources: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [{"type": source.get("source_type"), "artifact_ref": f"architecture-source://{source.get('codebase_id')}/{source.get('path')}"} for source in sources]

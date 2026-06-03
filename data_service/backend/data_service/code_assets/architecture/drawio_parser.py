"""Drawio parser for V2.3 architecture sources."""

from __future__ import annotations

import html
import re
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any


def parse_drawio(path: Path, rel_path: str) -> dict[str, Any]:
    try:
        root = ET.fromstring(path.read_text(encoding="utf-8", errors="ignore"))
    except ET.ParseError as exc:
        raise ValueError(f"DRAWIO_PARSE_FAILED:{rel_path}:{exc}") from exc
    diagrams: list[dict[str, Any]] = []
    for diagram in root.findall(".//diagram"):
        diagram_id = diagram.attrib.get("id") or diagram.attrib.get("name") or rel_path
        name = diagram.attrib.get("name") or diagram_id
        cells = diagram.findall(".//mxCell")
        labels: dict[str, dict[str, Any]] = {}
        nodes: list[dict[str, Any]] = []
        edges: list[dict[str, Any]] = []
        for cell in cells:
            value = _clean_label(cell.attrib.get("value", ""))
            if cell.attrib.get("vertex") == "1" and value:
                item = {
                    "raw_id": cell.attrib.get("id"),
                    "label": value,
                    "style": cell.attrib.get("style", ""),
                    "status": _status_from_style(cell.attrib.get("style", ""), value),
                    "node_type": classify_label(value),
                    "diagram_id": diagram_id,
                    "diagram_name": name,
                }
                labels[str(item["raw_id"])] = item
                nodes.append(item)
            if cell.attrib.get("edge") == "1":
                edges.append(
                    {
                        "raw_id": cell.attrib.get("id"),
                        "source": cell.attrib.get("source"),
                        "target": cell.attrib.get("target"),
                        "label": value,
                        "style": cell.attrib.get("style", ""),
                        "diagram_id": diagram_id,
                        "diagram_name": name,
                    }
                )
        diagrams.append({"diagram_id": diagram_id, "name": name, "nodes": nodes, "edges": edges})
    return {"source_type": "drawio", "path": rel_path, "diagrams": diagrams}


def classify_label(label: str) -> str:
    low = label.lower()
    if "forbidden" in low or "禁止" in label or "不能" in label:
        return "ForbiddenClaim"
    if re.search(r"\bplane-\d+\b", low) or " layer" in low or "层" in label:
        return "Plane"
    if "bounded context" in low:
        return "BoundedContext"
    if "governance" in low or "policy" in low or "approval" in low or "治理" in label:
        return "GovernanceBoundary"
    if "adapter" in low or "bff" in low or "sdk" in low or "hooks" in low:
        return "Adapter"
    if "runtime" in low or "executor" in low:
        return "Runtime"
    if "store" in low or "artifact" in low or "asset" in low or "evidence" in low:
        return "Artifact"
    if "api" in low or "mcp" in low or "cli" in low or "interface" in low:
        return "Interface"
    if "capability" in low or "能力" in label:
        return "Capability"
    if re.search(r"\bv\d+|phase|阶段|complete|pass", low):
        return "Milestone"
    if "system" in low or "系统" in label:
        return "System"
    return "Component"


def _clean_label(value: str) -> str:
    value = html.unescape(value or "")
    value = re.sub(r"<br\s*/?>", " | ", value, flags=re.I)
    value = re.sub(r"<[^>]+>", "", value)
    value = re.sub(r"\s+", " ", value).strip()
    return value


def _status_from_style(style: str, label: str) -> str:
    low = f"{style} {label}".lower()
    if "#dcfce7" in low or "#16a34a" in low or "complete" in low or "pass" in low:
        return "accepted_or_new"
    if "#fffbeb" in low or "#f59e0b" in low or "需改" in label:
        return "changed_or_planned"
    if "#fef2f2" in low or "#dc2626" in low or "禁止" in label or "forbidden" in low:
        return "forbidden"
    if "#e2e8f0" in low or "废弃" in label or "deprecated" in low:
        return "deprecated"
    return "existing_or_unspecified"

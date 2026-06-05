"""Architecture document claim extraction for V2.7."""

from __future__ import annotations

import html
import re
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

from data_service.mcp_common import now

from .doc_registry import SCHEMA_VERSION, stable_id


_BULLET_RE = re.compile(r"^\s*(?:[-*+]|\d+[.)])\s+(.+?)\s*$")
_TABLE_RE = re.compile(r"^\s*\|(.+)\|\s*$")
_HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$")
_INTERFACE_RE = re.compile(r"\b(GET|POST|PUT|PATCH|DELETE)\s+(/[^\s`|]+)")
_MERMAID_EDGE_RE = re.compile(r"^\s*([A-Za-z0-9_.:-]+)(?:\[[^\]]+\])?\s*[-=.]+[>|-]\s*([A-Za-z0-9_.:-]+)")
_CLAIM_TYPES = {
    "system": ("system", "service", "platform", "product"),
    "plane": ("plane",),
    "layer": ("layer", "tier"),
    "bounded_context": ("bounded context", "context"),
    "component": ("component", "module", "service", "engine", "registry", "extractor", "evaluator", "model", "overlay"),
    "adapter": ("adapter",),
    "provider": ("provider",),
    "runtime": ("runtime", "process"),
    "storage": ("storage", "artifact", "persist", "database"),
    "artifact": ("artifact", "jsonl", "json", "html", "mermaid", "drawio"),
    "public_interface": ("api", "http", "mcp", "cli", "endpoint", "route", "command", "tool"),
    "governance_boundary": ("governance", "boundary", "quality"),
    "policy": ("policy", "rule", "must", "shall", "should", "forbid"),
    "milestone": ("phase", "milestone", "roadmap"),
    "acceptance_gate": ("acceptance", "验收", "exit", "gate"),
    "forbidden_claim": ("must not", "forbidden", "reject", "禁止", "不得", "不能"),
    "non_goal": ("out of scope", "non-goal", "not a", "不是"),
    "quality_gate": ("quality", "audit", "finding", "false"),
}


def build_document_claims(
    *,
    workspace_id: str,
    codebase_id: str,
    snapshot_id: str,
    root: Path,
    documents: list[dict[str, Any]],
    sources: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    created_at = now()
    claims: list[dict[str, Any]] = []
    relations: list[dict[str, Any]] = []
    for doc in documents:
        rel = str(doc.get("repo_path") or doc.get("path") or "")
        if not rel:
            continue
        path = root / rel
        if not path.exists():
            continue
        doc_type = str(doc.get("doc_type") or "")
        if doc_type == "drawio" or path.suffix.lower() == ".drawio":
            extracted = _extract_drawio_claims(workspace_id, codebase_id, snapshot_id, doc, path, created_at)
        elif path.suffix.lower() == ".mmd":
            extracted = _extract_mermaid_claims(workspace_id, codebase_id, snapshot_id, doc, path, created_at)
        else:
            extracted = _extract_markdown_claims(workspace_id, codebase_id, snapshot_id, doc, path, created_at)
        claims.extend(extracted["claims"])
        relations.extend(extracted["relations"])

    claims = sorted(_dedupe(claims, "claim_id"), key=lambda item: (str(item.get("source_path") or ""), str(item.get("line_range") or ""), str(item.get("label") or "")))
    relations = sorted(_dedupe(relations, "relation_id"), key=lambda item: (str(item.get("source_doc_id") or ""), str(item.get("relation_id") or "")))
    summary = _summary(workspace_id, codebase_id, snapshot_id, claims, relations, created_at)
    return {
        "schema_version": SCHEMA_VERSION,
        "workspace_id": workspace_id,
        "codebase_id": codebase_id,
        "snapshot_id": snapshot_id,
        "claims": claims,
        "relations": relations,
        "summary": summary,
        "sources": sources or [],
        "created_at": created_at,
    }


def public_document_claims_payload(payload: dict[str, Any], artifact_refs: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "schema_version": payload.get("schema_version", SCHEMA_VERSION),
        "workspace_id": payload.get("workspace_id"),
        "codebase_id": payload.get("codebase_id"),
        "snapshot_id": payload.get("snapshot_id"),
        "summary": payload.get("summary", {}),
        "claims": payload.get("claims", []),
        "relations": payload.get("relations", []),
        "artifact_refs": artifact_refs,
    }


def _extract_markdown_claims(workspace_id: str, codebase_id: str, snapshot_id: str, doc: dict[str, Any], path: Path, created_at: str) -> dict[str, list[dict[str, Any]]]:
    claims: list[dict[str, Any]] = []
    relations: list[dict[str, Any]] = []
    previous_claim_id: str | None = None
    lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
    for idx, line in enumerate(lines, start=1):
        text = ""
        source_block_type = ""
        confidence = 0.8
        heading = _HEADING_RE.match(line)
        bullet = _BULLET_RE.match(line)
        table = _TABLE_RE.match(line)
        if heading:
            text = heading.group(2).strip()
            source_block_type = "heading"
            confidence = 0.9
        elif bullet:
            text = bullet.group(1).strip()
            source_block_type = _source_block_type_for_text(text, default="bullet")
            confidence = 0.8
        elif table and not _is_table_separator(line):
            cells = [cell.strip() for cell in table.group(1).split("|") if cell.strip()]
            text = " | ".join(cells[:4])
            source_block_type = "table_row"
            confidence = 0.9
        else:
            for method, route in _INTERFACE_RE.findall(line):
                text = f"{method} {route}"
                source_block_type = "interface_list"
                confidence = 0.9
                break
        if not text or len(text) < 3:
            continue
        claim = _claim(
            workspace_id,
            codebase_id,
            snapshot_id,
            doc,
            text,
            source_block_type=source_block_type,
            line_range=[idx, idx],
            confidence=confidence,
            created_at=created_at,
        )
        claims.append(claim)
        if previous_claim_id and source_block_type in {"bullet", "numbered_item", "table_row", "acceptance_gate", "non_goal", "stop_condition", "interface_list"}:
            relations.append(_relation(workspace_id, codebase_id, snapshot_id, doc, previous_claim_id, claim["claim_id"], "contains", [idx, idx], created_at, confidence=min(confidence, 0.8)))
        if source_block_type == "heading":
            previous_claim_id = claim["claim_id"]
    return {"claims": claims, "relations": relations}


def _extract_mermaid_claims(workspace_id: str, codebase_id: str, snapshot_id: str, doc: dict[str, Any], path: Path, created_at: str) -> dict[str, list[dict[str, Any]]]:
    claims_by_node: dict[str, dict[str, Any]] = {}
    relations: list[dict[str, Any]] = []
    for idx, line in enumerate(path.read_text(encoding="utf-8", errors="ignore").splitlines(), start=1):
        edge = _MERMAID_EDGE_RE.match(line)
        if not edge:
            continue
        from_label, to_label = edge.group(1), edge.group(2)
        for label in (from_label, to_label):
            claims_by_node.setdefault(
                label,
                _claim(workspace_id, codebase_id, snapshot_id, doc, label, source_block_type="diagram_node", line_range=[idx, idx], confidence=0.7, created_at=created_at),
            )
        relations.append(
            _relation(
                workspace_id,
                codebase_id,
                snapshot_id,
                doc,
                claims_by_node[from_label]["claim_id"],
                claims_by_node[to_label]["claim_id"],
                "depends_on",
                [idx, idx],
                created_at,
                confidence=0.65,
            )
        )
    return {"claims": list(claims_by_node.values()), "relations": relations}


def _extract_drawio_claims(workspace_id: str, codebase_id: str, snapshot_id: str, doc: dict[str, Any], path: Path, created_at: str) -> dict[str, list[dict[str, Any]]]:
    try:
        root = ET.fromstring(path.read_text(encoding="utf-8", errors="ignore"))
    except ET.ParseError:
        return {"claims": [], "relations": []}
    cells: dict[str, ET.Element] = {}
    claims: dict[str, dict[str, Any]] = {}
    relations: list[dict[str, Any]] = []
    for cell in root.iter("mxCell"):
        cell_id = cell.attrib.get("id")
        if cell_id:
            cells[cell_id] = cell
        value = _clean_label(cell.attrib.get("value") or "")
        if not cell_id or not value:
            continue
        claims[cell_id] = _claim(
            workspace_id,
            codebase_id,
            snapshot_id,
            doc,
            value,
            source_block_type="diagram_node",
            line_range=None,
            confidence=0.7,
            created_at=created_at,
            drawio_cell_id=cell_id,
            drawio_diagram_id=_drawio_diagram_name(cell),
        )
    for cell_id, cell in cells.items():
        if cell.attrib.get("edge") != "1":
            continue
        source, target = cell.attrib.get("source"), cell.attrib.get("target")
        if not source or not target or source not in claims or target not in claims:
            continue
        label = _clean_label(cell.attrib.get("value") or "")
        relation_type = _relation_type(label)
        relations.append(
            _relation(
                workspace_id,
                codebase_id,
                snapshot_id,
                doc,
                claims[source]["claim_id"],
                claims[target]["claim_id"],
                relation_type,
                None,
                created_at,
                confidence=0.8 if label else 0.65,
                drawio_cell_id=cell_id,
            )
        )
    return {"claims": list(claims.values()), "relations": relations}


def _claim(
    workspace_id: str,
    codebase_id: str,
    snapshot_id: str,
    doc: dict[str, Any],
    label: str,
    *,
    source_block_type: str,
    line_range: list[int] | None,
    confidence: float,
    created_at: str,
    drawio_cell_id: str | None = None,
    drawio_diagram_id: str | None = None,
) -> dict[str, Any]:
    label = _clean_label(label)
    normalized = _normalize_label(label)
    source_path = str(doc.get("repo_path") or doc.get("path") or "")
    doc_id = str(doc.get("doc_id") or "")
    needs_review = []
    claim_type = _claim_type(label, source_block_type)
    if source_block_type in {"diagram_node", "diagram_edge"}:
        needs_review.append({"code": "DOCUMENT_DIAGRAM_CLAIM", "reason": "Diagram-derived claim is document evidence and not code-derived architecture."})
    if confidence <= 0.65:
        needs_review.append({"code": "LOW_CONFIDENCE_CLAIM", "reason": "Claim confidence is below accepted threshold."})
    return {
        "schema_version": SCHEMA_VERSION,
        "workspace_id": workspace_id,
        "codebase_id": codebase_id,
        "snapshot_id": snapshot_id,
        "claim_id": stable_id("archclaim", snapshot_id, doc_id, source_block_type, line_range or drawio_cell_id or "", normalized),
        "doc_id": doc_id,
        "claim_type": claim_type,
        "label": label[:300],
        "normalized_label": normalized,
        "status_hint": _status_hint(label),
        "scope_hint": doc.get("scope_hint") or "",
        "source_block_type": source_block_type,
        "drawio_cell_id": drawio_cell_id,
        "drawio_diagram_id": drawio_diagram_id,
        "source_path": source_path,
        "repo_path": source_path,
        "line_range": line_range,
        "evidence": [{"type": "source_file", "path": source_path, "repo_path": source_path, "line_range": line_range, "extractor": "architecture_doc_claim_extractor"}],
        "confidence": min(confidence, _confidence_ceiling(source_block_type)),
        "needs_review": needs_review,
        "created_at": created_at,
    }


def _relation(
    workspace_id: str,
    codebase_id: str,
    snapshot_id: str,
    doc: dict[str, Any],
    from_claim_id: str,
    to_claim_id: str,
    relation_type: str,
    line_range: list[int] | None,
    created_at: str,
    *,
    confidence: float,
    drawio_cell_id: str | None = None,
) -> dict[str, Any]:
    source_path = str(doc.get("repo_path") or doc.get("path") or "")
    return {
        "schema_version": SCHEMA_VERSION,
        "workspace_id": workspace_id,
        "codebase_id": codebase_id,
        "snapshot_id": snapshot_id,
        "relation_id": stable_id("archrel", snapshot_id, doc.get("doc_id"), from_claim_id, to_claim_id, relation_type, line_range or drawio_cell_id or ""),
        "from_claim_id": from_claim_id,
        "to_claim_id": to_claim_id,
        "relation_type": relation_type,
        "source_doc_id": doc.get("doc_id"),
        "source_path": source_path,
        "repo_path": source_path,
        "drawio_cell_id": drawio_cell_id,
        "evidence": [{"type": "source_file", "path": source_path, "repo_path": source_path, "line_range": line_range, "extractor": "architecture_doc_claim_extractor"}],
        "confidence": confidence,
        "needs_review": [] if confidence >= 0.7 else [{"code": "LOW_CONFIDENCE_RELATION", "reason": "Relation source lacks an explicit relation label."}],
        "created_at": created_at,
    }


def _claim_type(label: str, source_block_type: str) -> str:
    low = label.lower()
    if source_block_type == "acceptance_gate":
        return "acceptance_gate"
    if source_block_type == "non_goal":
        return "non_goal"
    if source_block_type == "stop_condition":
        return "forbidden_claim"
    if source_block_type == "interface_list" or _INTERFACE_RE.search(label):
        return "public_interface"
    for claim_type, hints in _CLAIM_TYPES.items():
        if any(hint in low for hint in hints):
            return claim_type
    return "component"


def _source_block_type_for_text(text: str, *, default: str) -> str:
    low = text.lower()
    if "acceptance" in low or "验收" in low or "exit gate" in low:
        return "acceptance_gate"
    if "out of scope" in low or "non-goal" in low or low.startswith("not ") or "不做" in text or "不是" in text:
        return "non_goal"
    if "must not" in low or "stop condition" in low or "false-green" in low or "不得" in text or "禁止" in text:
        return "stop_condition"
    if _INTERFACE_RE.search(text) or text.strip().startswith("knowledge_"):
        return "interface_list"
    return default


def _confidence_ceiling(source_block_type: str) -> float:
    return {
        "heading": 0.9,
        "table_row": 0.9,
        "acceptance_gate": 0.9,
        "non_goal": 0.9,
        "stop_condition": 0.9,
        "interface_list": 0.9,
        "bullet": 0.8,
        "numbered_item": 0.8,
        "diagram_node": 0.7,
        "diagram_edge": 0.65,
    }.get(source_block_type, 0.6)


def _status_hint(label: str) -> str:
    low = label.lower()
    if "accepted" in low or "已验收" in label or "完成" in label:
        return "accepted"
    if "pending" in low or "planned" in low or "计划" in label or "待" in label:
        return "planned"
    if "target" in low or "目标" in label:
        return "target"
    return "unknown"


def _relation_type(label: str) -> str:
    low = label.lower()
    if "govern" in low:
        return "governs"
    if "produce" in low:
        return "produces"
    if "consume" in low:
        return "consumes"
    if "implement" in low:
        return "implements"
    if "document" in low:
        return "documents"
    if "validate" in low:
        return "validates"
    if "block" in low:
        return "blocks"
    if "conflict" in low:
        return "conflicts_with"
    if "contain" in low:
        return "contains"
    return "depends_on"


def _drawio_diagram_name(cell: ET.Element) -> str | None:
    node = cell
    while node is not None:
        if node.tag == "diagram":
            return node.attrib.get("name")
        node = None
    return None


def _clean_label(value: str) -> str:
    text = re.sub(r"<[^>]+>", " ", html.unescape(value))
    text = _redact_local_paths(text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def _redact_local_paths(value: str) -> str:
    return re.sub(r"(?<![\w])/(?:Users|private|var|tmp|Volumes)/[^\s`'\"|)]+", "[REDACTED_LOCAL_PATH]", value)


def _normalize_label(label: str) -> str:
    cleaned = _clean_label(label).lower()
    cleaned = re.sub(r"[^a-z0-9\u4e00-\u9fff]+", "_", cleaned).strip("_")
    return cleaned[:96] or "claim"


def _is_table_separator(line: str) -> bool:
    return bool(re.match(r"^\s*\|?\s*:?-{3,}:?\s*(\|\s*:?-{3,}:?\s*)+\|?\s*$", line))


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


def _summary(workspace_id: str, codebase_id: str, snapshot_id: str, claims: list[dict[str, Any]], relations: list[dict[str, Any]], created_at: str) -> dict[str, Any]:
    claim_type_counts: dict[str, int] = {}
    block_type_counts: dict[str, int] = {}
    for claim in claims:
        claim_type = str(claim.get("claim_type") or "unknown")
        block_type = str(claim.get("source_block_type") or "unknown")
        claim_type_counts[claim_type] = claim_type_counts.get(claim_type, 0) + 1
        block_type_counts[block_type] = block_type_counts.get(block_type, 0) + 1
    return {
        "schema_version": SCHEMA_VERSION,
        "workspace_id": workspace_id,
        "codebase_id": codebase_id,
        "snapshot_id": snapshot_id,
        "created_at": created_at,
        "claim_count": len(claims),
        "relation_count": len(relations),
        "claim_type_counts": dict(sorted(claim_type_counts.items())),
        "source_block_type_counts": dict(sorted(block_type_counts.items())),
        "needs_review_count": sum(1 for item in [*claims, *relations] if item.get("needs_review")),
    }

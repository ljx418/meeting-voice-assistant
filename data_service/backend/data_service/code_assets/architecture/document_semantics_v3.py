"""V2.43 document semantic parser.

Document semantic claims are target/document facts only. They must not be
promoted to code facts without separate code evidence.
"""

from __future__ import annotations

import hashlib
import html
import re
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path
from typing import Any

from data_service.mcp_common import now, read_json, write_json

from ..artifacts import (
    architecture_document_semantic_claims_v243_path,
    architecture_document_semantic_relations_v243_path,
    architecture_document_semantic_summary_v243_path,
    write_jsonl,
    read_jsonl,
)


SCHEMA_VERSION = "v2.43_document_semantics"
_HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$")
_BULLET_RE = re.compile(r"^\s*(?:[-*+]|\d+[.)])\s+(.+?)\s*$")
_TABLE_RE = re.compile(r"^\s*\|(.+)\|\s*$")
_TAG_RE = re.compile(r"<[^>]+>")
_ABSOLUTE_PATH_RE = re.compile(r"(?<![A-Za-z]:)/(?:Users|private|var|tmp|Volumes|Applications)/[^\s`'\"|)>,]+")


def build_document_semantics_v3(
    *,
    workspace,
    workspace_id: str,
    codebase_id: str,
    snapshot_id: str,
    root: Path,
    documents: list[dict[str, Any]],
    artifact_refs: list[dict[str, str]],
) -> dict[str, Any]:
    created_at = now()
    claims: list[dict[str, Any]] = []
    relations: list[dict[str, Any]] = []
    blockers: list[dict[str, Any]] = []
    for doc in documents:
        rel = str(doc.get("repo_path") or doc.get("path") or "")
        if not rel:
            continue
        path = root / rel
        if not path.exists():
            blockers.append({"code": "DOCUMENT_NOT_FOUND", "path": rel})
            continue
        suffix = path.suffix.lower()
        if suffix == ".drawio":
            parsed = _parse_drawio(workspace_id, codebase_id, snapshot_id, doc, path, created_at)
        elif suffix in {".md", ".markdown", ".mmd"}:
            parsed = _parse_markdown(workspace_id, codebase_id, snapshot_id, doc, path, created_at)
        else:
            continue
        claims.extend(parsed["claims"])
        relations.extend(parsed["relations"])
    claims = _dedupe(claims, "claim_id")
    relations = _dedupe(relations, "relation_id")
    if not claims:
        blockers.append({"code": "DOCUMENT_SEMANTIC_CLAIMS_NOT_FOUND", "reason": "No markdown or drawio semantic claims were extracted."})
    summary = _summary(workspace_id, codebase_id, snapshot_id, claims, relations, blockers, artifact_refs, created_at)
    write_jsonl(architecture_document_semantic_claims_v243_path(workspace, codebase_id), claims)
    write_jsonl(architecture_document_semantic_relations_v243_path(workspace, codebase_id), relations)
    write_json(architecture_document_semantic_summary_v243_path(workspace, codebase_id), summary)
    return {
        "schema_version": SCHEMA_VERSION,
        "workspace_id": workspace_id,
        "codebase_id": codebase_id,
        "snapshot_id": snapshot_id,
        "claims": claims,
        "relations": relations,
        "summary": summary,
        "artifact_refs": artifact_refs,
        "created_at": created_at,
    }


def read_document_semantics_v3(workspace, codebase_id: str, artifact_refs: list[dict[str, str]]) -> dict[str, Any]:
    claims = read_jsonl(architecture_document_semantic_claims_v243_path(workspace, codebase_id))
    relations = read_jsonl(architecture_document_semantic_relations_v243_path(workspace, codebase_id))
    summary = read_json(architecture_document_semantic_summary_v243_path(workspace, codebase_id), {})
    if not summary:
        raise FileNotFoundError("ARCHITECTURE_DOCUMENT_SEMANTICS_V3_NOT_BUILT")
    return {
        "schema_version": SCHEMA_VERSION,
        "workspace_id": summary.get("workspace_id"),
        "codebase_id": codebase_id,
        "snapshot_id": summary.get("snapshot_id"),
        "claims": claims,
        "relations": relations,
        "summary": summary,
        "artifact_refs": artifact_refs,
    }


def public_document_semantics_v3_payload(payload: dict[str, Any], *, limit: int = 120) -> dict[str, Any]:
    claims = list(payload.get("claims") or [])
    relations = list(payload.get("relations") or [])
    return {
        "schema_version": payload.get("schema_version", SCHEMA_VERSION),
        "workspace_id": payload.get("workspace_id"),
        "codebase_id": payload.get("codebase_id"),
        "snapshot_id": payload.get("snapshot_id"),
        "summary": payload.get("summary") or {},
        "claims": {"total": len(claims), "sample": claims[:limit], "truncated": len(claims) > limit},
        "relations": {"total": len(relations), "sample": relations[:limit], "truncated": len(relations) > limit},
        "artifact_refs": payload.get("artifact_refs") or [],
    }


def _parse_markdown(workspace_id: str, codebase_id: str, snapshot_id: str, doc: dict[str, Any], path: Path, created_at: str) -> dict[str, list[dict[str, Any]]]:
    claims: list[dict[str, Any]] = []
    relations: list[dict[str, Any]] = []
    current_heading: dict[str, Any] | None = None
    for line_no, line in enumerate(path.read_text(encoding="utf-8", errors="ignore").splitlines(), start=1):
        label = ""
        block_type = ""
        confidence = 0.8
        heading = _HEADING_RE.match(line)
        bullet = _BULLET_RE.match(line)
        table = _TABLE_RE.match(line)
        if heading:
            label = heading.group(2).strip()
            block_type = "heading"
            confidence = 0.9
        elif bullet:
            label = bullet.group(1).strip()
            block_type = _semantic_block_type(label, default="bullet")
        elif table and not _is_table_separator(line):
            cells = [cell.strip() for cell in table.group(1).split("|") if cell.strip()]
            label = " | ".join(cells[:5])
            block_type = _semantic_block_type(label, default="table_row")
            confidence = 0.85
        if not label or len(label) < 3:
            continue
        claim = _claim(workspace_id, codebase_id, snapshot_id, doc, label, source_type="markdown", source_block_type=block_type, line_range=[line_no, line_no], drawio_cell_id=None, confidence=confidence, created_at=created_at)
        claims.append(claim)
        if current_heading and block_type != "heading":
            relations.append(_relation(workspace_id, codebase_id, snapshot_id, doc, current_heading["claim_id"], claim["claim_id"], "contains", [line_no, line_no], None, 0.78, created_at))
        if block_type == "heading":
            current_heading = claim
    return {"claims": claims, "relations": relations}


def _parse_drawio(workspace_id: str, codebase_id: str, snapshot_id: str, doc: dict[str, Any], path: Path, created_at: str) -> dict[str, list[dict[str, Any]]]:
    try:
        root = ET.fromstring(path.read_text(encoding="utf-8", errors="ignore"))
    except ET.ParseError:
        return {"claims": [], "relations": []}
    claims_by_cell: dict[str, dict[str, Any]] = {}
    relations: list[dict[str, Any]] = []
    for diagram in root.iter("diagram"):
        name = _clean_label(diagram.attrib.get("name") or "")
        if name:
            claim = _claim(workspace_id, codebase_id, snapshot_id, doc, name, source_type="drawio", source_block_type="drawio_page", line_range=None, drawio_cell_id=diagram.attrib.get("id"), confidence=0.72, created_at=created_at)
            claims_by_cell[claim["claim_id"]] = claim
    cells = {cell.attrib.get("id"): cell for cell in root.iter("mxCell") if cell.attrib.get("id")}
    for cell_id, cell in cells.items():
        value = _clean_label(cell.attrib.get("value") or "")
        if not value:
            continue
        block_type = _drawio_block_type(cell, value)
        claim = _claim(workspace_id, codebase_id, snapshot_id, doc, value, source_type="drawio", source_block_type=block_type, line_range=None, drawio_cell_id=cell_id, confidence=0.68 if block_type == "drawio_edge" else 0.7, created_at=created_at)
        claims_by_cell[cell_id] = claim
    for cell_id, cell in cells.items():
        if cell.attrib.get("edge") != "1":
            continue
        source_id, target_id = cell.attrib.get("source"), cell.attrib.get("target")
        if not source_id or not target_id or source_id not in claims_by_cell or target_id not in claims_by_cell:
            continue
        relations.append(_relation(workspace_id, codebase_id, snapshot_id, doc, claims_by_cell[source_id]["claim_id"], claims_by_cell[target_id]["claim_id"], "diagram_edge", None, cell_id, 0.65, created_at))
    return {"claims": list(claims_by_cell.values()), "relations": relations}


def _claim(workspace_id: str, codebase_id: str, snapshot_id: str, doc: dict[str, Any], label: str, *, source_type: str, source_block_type: str, line_range: list[int] | None, drawio_cell_id: str | None, confidence: float, created_at: str) -> dict[str, Any]:
    label = _clean_label(label)
    repo_path = str(doc.get("repo_path") or doc.get("path") or "")
    claim_role = _claim_role(label, source_block_type)
    needs_review = []
    if source_type == "drawio":
        needs_review.append({"code": "DRAWIO_DOCUMENT_CLAIM_ONLY", "reason": "Drawio semantics are document claims, not code facts."})
    if confidence < 0.75:
        needs_review.append({"code": "SEMANTIC_REVIEW_REQUIRED", "reason": "Document semantic confidence is below strong-evidence threshold."})
    return {
        "schema_version": SCHEMA_VERSION,
        "workspace_id": workspace_id,
        "codebase_id": codebase_id,
        "snapshot_id": snapshot_id,
        "claim_id": _stable_id("docsem", codebase_id, snapshot_id, repo_path, source_block_type, line_range or drawio_cell_id or "", label),
        "doc_id": str(doc.get("doc_id") or ""),
        "source_type": source_type,
        "source_block_type": source_block_type,
        "label": label[:300],
        "normalized_label": _normalize(label),
        "path": repo_path,
        "repo_path": repo_path,
        "line_range": line_range,
        "drawio_cell_id": drawio_cell_id,
        "confidence": round(min(confidence, 0.72 if source_type == "drawio" else 0.92), 3),
        "claim_role": claim_role,
        "is_code_fact": False,
        "evidence_refs": [{"type": "document_source", "path": repo_path, "line_range": line_range, "drawio_cell_id": drawio_cell_id}],
        "needs_review": needs_review,
        "created_at": created_at,
    }


def _relation(workspace_id: str, codebase_id: str, snapshot_id: str, doc: dict[str, Any], source_claim_id: str, target_claim_id: str, relation_type: str, line_range: list[int] | None, drawio_cell_id: str | None, confidence: float, created_at: str) -> dict[str, Any]:
    repo_path = str(doc.get("repo_path") or doc.get("path") or "")
    return {
        "schema_version": SCHEMA_VERSION,
        "workspace_id": workspace_id,
        "codebase_id": codebase_id,
        "snapshot_id": snapshot_id,
        "relation_id": _stable_id("docsemrel", codebase_id, snapshot_id, source_claim_id, target_claim_id, relation_type, line_range or drawio_cell_id or ""),
        "source_claim_id": source_claim_id,
        "target_claim_id": target_claim_id,
        "relation_type": relation_type,
        "path": repo_path,
        "repo_path": repo_path,
        "line_range": line_range,
        "drawio_cell_id": drawio_cell_id,
        "confidence": confidence,
        "is_code_fact": False,
        "evidence_refs": [{"type": "document_source", "path": repo_path, "line_range": line_range, "drawio_cell_id": drawio_cell_id}],
        "needs_review": [{"code": "DOCUMENT_RELATION_ONLY", "reason": "Document relation is not runtime topology."}] if relation_type == "diagram_edge" else [],
        "created_at": created_at,
    }


def _summary(workspace_id: str, codebase_id: str, snapshot_id: str, claims: list[dict[str, Any]], relations: list[dict[str, Any]], blockers: list[dict[str, Any]], artifact_refs: list[dict[str, str]], created_at: str) -> dict[str, Any]:
    source_types = Counter(str(item.get("source_type") or "unknown") for item in claims)
    block_types = Counter(str(item.get("source_block_type") or "unknown") for item in claims)
    roles = Counter(str(item.get("claim_role") or "unknown") for item in claims)
    return {
        "schema_version": SCHEMA_VERSION,
        "workspace_id": workspace_id,
        "codebase_id": codebase_id,
        "snapshot_id": snapshot_id,
        "claim_count": len(claims),
        "relation_count": len(relations),
        "source_type_counts": dict(sorted(source_types.items())),
        "source_block_type_counts": dict(sorted(block_types.items())),
        "claim_role_counts": dict(sorted(roles.items())),
        "drawio_claim_count": source_types.get("drawio", 0),
        "markdown_claim_count": source_types.get("markdown", 0),
        "code_fact_count": sum(1 for item in claims if item.get("is_code_fact")),
        "needs_review_count": sum(1 for item in claims if item.get("needs_review")),
        "blockers": blockers,
        "artifact_refs": artifact_refs,
        "created_at": created_at,
    }


def _semantic_block_type(label: str, *, default: str) -> str:
    low = label.lower()
    if "acceptance" in low or "验收" in low or "exit gate" in low or "出门条件" in low:
        return "acceptance_gate"
    if "non-goal" in low or "out of scope" in low or "不是" in low or "不做" in low:
        return "non_goal"
    if "stop" in low or "reject" in low or "禁止" in low or "不得" in low or "不能" in low:
        return "stop_condition"
    if "milestone" in low or "里程碑" in low or "phase" in low:
        return "milestone"
    return default


def _drawio_block_type(cell: ET.Element, value: str) -> str:
    style = (cell.attrib.get("style") or "").lower()
    low = value.lower()
    if cell.attrib.get("edge") == "1":
        return "drawio_edge"
    if "swimlane" in style or "lane" in low or "泳道" in value:
        return "drawio_lane"
    if "group" in style or "container" in style or "group" in low or "分组" in value:
        return "drawio_group"
    if "gate" in low or "验收" in value or "门槛" in value:
        return "acceptance_gate"
    if "legend" in low or "图例" in value:
        return "drawio_legend"
    return "drawio_group" if "rounded" in style else "drawio_node"


def _claim_role(label: str, block_type: str) -> str:
    low = label.lower()
    if block_type == "acceptance_gate":
        return "acceptance_gate"
    if block_type == "non_goal":
        return "non_goal"
    if block_type == "stop_condition":
        return "constraint"
    if "target" in low or "目标" in label or "architecture" in low or "架构" in label:
        return "target_design"
    if "must" in low or "shall" in low or "必须" in label:
        return "constraint"
    return "unknown"


def _clean_label(label: str) -> str:
    text = html.unescape(str(label or ""))
    text = _TAG_RE.sub(" ", text)
    text = _ABSOLUTE_PATH_RE.sub("<absolute_path>", text)
    text = text.replace("<", " ").replace(">", " ")
    return re.sub(r"\s+", " ", text).strip()


def _normalize(label: str) -> str:
    return re.sub(r"[^a-z0-9\u4e00-\u9fff]+", "_", label.lower()).strip("_")


def _is_table_separator(line: str) -> bool:
    return bool(re.match(r"^\s*\|?\s*:?-{3,}:?\s*(\|\s*:?-{3,}:?\s*)+\|?\s*$", line))


def _dedupe(items: list[dict[str, Any]], key: str) -> list[dict[str, Any]]:
    seen = set()
    out = []
    for item in items:
        value = item.get(key)
        if not value or value in seen:
            continue
        seen.add(value)
        out.append(item)
    return out


def _stable_id(*parts: Any) -> str:
    return hashlib.sha256("::".join(str(part) for part in parts).encode("utf-8")).hexdigest()[:24]

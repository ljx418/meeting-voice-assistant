"""V2.37 document-grounded architecture reconstruction service.

The service keeps document claims and code facts as separate artifacts. A
verification row can become ``supported`` only when both sides have evidence.
"""

from __future__ import annotations

import hashlib
import html
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from data_service.mcp_common import now, read_json, write_json

from data_service.code_assets.artifacts import (
    evidence_path,
    imports_path,
    inventory_surfaces_path,
    read_jsonl,
    snapshot_files_path,
    symbols_path,
    write_jsonl,
)
from data_service.code_assets.registry import CodebaseRegistry
from data_service.code_assets.snapshot import CodebaseSnapshotService
from data_service.code_assets.architecture.drawio_parser import parse_drawio

from .paths import (
    artifact_refs,
    brief_markdown_path,
    brief_path,
    current_model_path,
    doc_authority_documents_path,
    doc_authority_registry_path,
    doc_claim_relations_path,
    doc_claims_path,
    drift_findings_path,
    reconstruction_report_path,
    report_html_path,
    report_mermaid_path,
    report_svg_path,
    target_model_path,
    verification_matrix_path,
)


SCHEMA_VERSION = "v2.37"
ERROR_NOT_BUILT = "DOC_GROUNDED_ARCHITECTURE_NOT_BUILT"
DOC_SUFFIXES = {".md", ".markdown", ".mdx", ".drawio", ".mmd"}
DOC_NAMES = {"README", "CHANGELOG", "CONTRIBUTING", "ARCHITECTURE"}
CURRENT_VERSION_HINTS = ("v2_37", "v2.37", "v237")
LEGACY_VERSION_RE = re.compile(r"v(\d+)(?:[._-](\d+))?", re.I)


class DocGroundedArchitectureService:
    def __init__(self, workspace: Path, *, workspace_id: str) -> None:
        self.workspace = Path(workspace)
        self.workspace_id = workspace_id
        self.registry = CodebaseRegistry(self.workspace, workspace_id=workspace_id)
        self.snapshots = CodebaseSnapshotService(self.workspace, workspace_id=workspace_id)

    def build_pipeline(self, codebase_id: str, *, snapshot_id: str | None = None, mode: str = "architecture_review", max_tokens: int = 12000) -> dict[str, Any]:
        registry = self.build_document_authority_registry(codebase_id, snapshot_id=snapshot_id)
        claims = self.build_claim_graph(codebase_id)
        current = self.build_current_implementation_model(codebase_id)
        verification = self.build_verification(codebase_id)
        report = self.build_reconstruction_report(codebase_id)
        brief = self.create_agent_brief(codebase_id, mode=mode, max_tokens=max_tokens)
        return {
            "schema_version": SCHEMA_VERSION,
            "workspace_id": self.workspace_id,
            "codebase_id": codebase_id,
            "snapshot_id": registry.get("snapshot_id"),
            "document_authority_registry": registry,
            "claim_graph_summary": claims.get("summary", {}),
            "current_implementation_summary": current.get("summary", {}),
            "verification_summary": verification.get("summary", {}),
            "reconstruction_report_summary": report.get("summary", {}),
            "agent_brief": brief,
            "artifact_refs": artifact_refs(codebase_id) + brief.get("artifact_refs", []),
            "warnings": _collect_warnings(registry, claims, current, verification, report),
            "unresolved": verification.get("summary", {}).get("unresolved", []),
            "next_actions": ["knowledge_code_doc_grounded_architecture_report", "knowledge_code_doc_grounded_verification", "knowledge_code_doc_grounded_architecture_brief"],
        }

    def build_document_authority_registry(self, codebase_id: str, *, snapshot_id: str | None = None) -> dict[str, Any]:
        asset = self.registry.describe(codebase_id)
        if asset.status != "active":
            raise ValueError("CODEBASE_NOT_ACTIVE")
        resolved_snapshot_id = snapshot_id or self._latest_snapshot_id(codebase_id)
        self.snapshots.read_snapshot(codebase_id, resolved_snapshot_id)
        root = Path(asset.root_path).expanduser().resolve()
        files = read_jsonl(snapshot_files_path(self.workspace, codebase_id, resolved_snapshot_id))
        documents: list[dict[str, Any]] = []
        for record in files:
            rel = str(record.get("path") or "")
            if not record.get("included", True) or not _is_document_path(rel):
                continue
            doc = _document_record(root, rel, record, self.workspace_id, codebase_id, resolved_snapshot_id)
            if doc:
                documents.append(doc)
        documents.sort(key=lambda item: (str(item.get("repo_path") or ""), str(item.get("doc_id") or "")))
        registry = {
            "schema_version": SCHEMA_VERSION,
            "workspace_id": self.workspace_id,
            "codebase_id": codebase_id,
            "snapshot_id": resolved_snapshot_id,
            "generated_at": now(),
            "documents": documents,
            "summary": {
                "document_count": len(documents),
                "by_doc_type": dict(sorted(Counter(str(item["doc_type"]) for item in documents).items())),
                "by_authority_role": dict(sorted(Counter(str(item["authority_role"]) for item in documents).items())),
                "stale_count": sum(1 for item in documents if item.get("stale")),
            },
            "artifact_refs": artifact_refs(codebase_id),
            "warnings": [] if documents else ["ARCHITECTURE_DOCS_NOT_FOUND"],
            "unresolved": [] if documents else [{"reason": "no architecture documents found"}],
        }
        write_json(doc_authority_registry_path(self.workspace, codebase_id), registry)
        write_jsonl(doc_authority_documents_path(self.workspace, codebase_id), documents)
        return registry

    def read_document_authority_registry(self, codebase_id: str) -> dict[str, Any]:
        payload = read_json(doc_authority_registry_path(self.workspace, codebase_id), None)
        if not payload:
            raise FileNotFoundError(ERROR_NOT_BUILT)
        payload["artifact_refs"] = artifact_refs(codebase_id)
        return payload

    def build_claim_graph(self, codebase_id: str) -> dict[str, Any]:
        asset = self.registry.describe(codebase_id)
        root = Path(asset.root_path).expanduser().resolve()
        registry = self.read_document_authority_registry(codebase_id)
        claims: list[dict[str, Any]] = []
        relations: list[dict[str, Any]] = []
        for doc in registry.get("documents", []):
            path = root / str(doc.get("repo_path") or "")
            if not path.exists():
                continue
            if path.suffix.lower() == ".drawio":
                doc_claims, doc_relations = _extract_drawio_claims(path, doc)
            else:
                doc_claims, doc_relations = _extract_markdown_claims(path, doc)
            claims.extend(doc_claims)
            relations.extend(doc_relations)
        claims = _dedupe_by_id(claims, "claim_id")
        relations = _dedupe_by_id(relations, "relation_id")
        target_model = _target_model(registry, claims, relations)
        payload = {
            "schema_version": SCHEMA_VERSION,
            "workspace_id": self.workspace_id,
            "codebase_id": codebase_id,
            "snapshot_id": registry.get("snapshot_id"),
            "claims": claims,
            "relations": relations,
            "target_architecture_model": target_model,
            "summary": {
                "claim_count": len(claims),
                "relation_count": len(relations),
                "by_claim_type": dict(sorted(Counter(str(item.get("claim_type")) for item in claims).items())),
                "forbidden_claim_count": sum(1 for item in claims if item.get("claim_type") == "forbidden_claim"),
                "needs_review_count": sum(1 for item in claims if item.get("needs_review")),
            },
            "artifact_refs": artifact_refs(codebase_id),
        }
        write_jsonl(doc_claims_path(self.workspace, codebase_id), claims)
        write_jsonl(doc_claim_relations_path(self.workspace, codebase_id), relations)
        write_json(target_model_path(self.workspace, codebase_id), target_model)
        return payload

    def read_claim_graph(self, codebase_id: str) -> dict[str, Any]:
        claims = read_jsonl(doc_claims_path(self.workspace, codebase_id))
        target = read_json(target_model_path(self.workspace, codebase_id), None)
        if not claims or not target:
            raise FileNotFoundError(ERROR_NOT_BUILT)
        relations = read_jsonl(doc_claim_relations_path(self.workspace, codebase_id))
        return {
            "schema_version": SCHEMA_VERSION,
            "workspace_id": self.workspace_id,
            "codebase_id": codebase_id,
            "snapshot_id": _snapshot_id_from_items(claims) or target.get("snapshot_id"),
            "claims": claims,
            "relations": relations,
            "target_architecture_model": target,
            "summary": {
                "claim_count": len(claims),
                "relation_count": len(relations),
                "by_claim_type": dict(sorted(Counter(str(item.get("claim_type")) for item in claims).items())),
            },
            "artifact_refs": artifact_refs(codebase_id),
        }

    def build_current_implementation_model(self, codebase_id: str) -> dict[str, Any]:
        registry = self.read_document_authority_registry(codebase_id)
        snapshot_id = str(registry.get("snapshot_id") or "")
        files = read_jsonl(snapshot_files_path(self.workspace, codebase_id, snapshot_id))
        surfaces = read_jsonl(inventory_surfaces_path(self.workspace, codebase_id, snapshot_id))
        symbols = read_jsonl(symbols_path(self.workspace, codebase_id, snapshot_id))
        evidence = read_jsonl(evidence_path(self.workspace, codebase_id, snapshot_id))
        imports = read_jsonl(imports_path(self.workspace, codebase_id, snapshot_id))
        nodes, edges, blockers = _current_model_nodes(self.workspace_id, codebase_id, snapshot_id, files, surfaces, symbols, evidence, imports)
        model = {
            "schema_version": SCHEMA_VERSION,
            "workspace_id": self.workspace_id,
            "codebase_id": codebase_id,
            "snapshot_id": snapshot_id,
            "nodes": nodes,
            "edges": edges,
            "blockers": blockers,
            "summary": {
                "node_count": len(nodes),
                "edge_count": len(edges),
                "by_node_type": dict(sorted(Counter(str(item.get("node_type")) for item in nodes).items())),
                "blocker_count": len(blockers),
                "surface_count": len(surfaces),
                "symbol_count": len(symbols),
                "file_count": len([item for item in files if item.get("included", True)]),
            },
            "artifact_refs": artifact_refs(codebase_id),
        }
        write_json(current_model_path(self.workspace, codebase_id), model)
        return model

    def read_current_implementation_model(self, codebase_id: str) -> dict[str, Any]:
        payload = read_json(current_model_path(self.workspace, codebase_id), None)
        if not payload:
            raise FileNotFoundError(ERROR_NOT_BUILT)
        payload["artifact_refs"] = artifact_refs(codebase_id)
        return payload

    def build_verification(self, codebase_id: str) -> dict[str, Any]:
        claim_payload = self.read_claim_graph(codebase_id)
        current = self.read_current_implementation_model(codebase_id)
        claims = claim_payload.get("claims", [])
        nodes = current.get("nodes", [])
        rows, findings = _verify_claims(self.workspace_id, codebase_id, str(current.get("snapshot_id") or ""), claims, nodes)
        summary = {
            "verification_count": len(rows),
            "by_status": dict(sorted(Counter(str(item.get("verification_status")) for item in rows).items())),
            "supported_count": sum(1 for item in rows if item.get("verification_status") == "supported"),
            "weak_count": sum(1 for item in rows if item.get("verification_status") == "weakly_supported"),
            "unsupported_count": sum(1 for item in rows if item.get("verification_status") == "unsupported"),
            "code_not_documented_count": sum(1 for item in rows if item.get("verification_status") == "code_not_documented"),
            "unresolved": [{"claim_id": item.get("claim_id"), "reason": item.get("reason")} for item in rows if item.get("verification_status") in {"unsupported", "needs_review"}][:50],
        }
        payload = {
            "schema_version": SCHEMA_VERSION,
            "workspace_id": self.workspace_id,
            "codebase_id": codebase_id,
            "snapshot_id": current.get("snapshot_id"),
            "verification_rows": rows,
            "drift_findings": findings,
            "summary": summary,
            "artifact_refs": artifact_refs(codebase_id),
        }
        write_jsonl(verification_matrix_path(self.workspace, codebase_id), rows)
        write_jsonl(drift_findings_path(self.workspace, codebase_id), findings)
        return payload

    def read_verification(self, codebase_id: str) -> dict[str, Any]:
        rows = read_jsonl(verification_matrix_path(self.workspace, codebase_id))
        if not rows:
            raise FileNotFoundError(ERROR_NOT_BUILT)
        findings = read_jsonl(drift_findings_path(self.workspace, codebase_id))
        return {
            "schema_version": SCHEMA_VERSION,
            "workspace_id": self.workspace_id,
            "codebase_id": codebase_id,
            "snapshot_id": _snapshot_id_from_items(rows),
            "verification_rows": rows,
            "drift_findings": findings,
            "summary": {
                "verification_count": len(rows),
                "by_status": dict(sorted(Counter(str(item.get("verification_status")) for item in rows).items())),
                "supported_count": sum(1 for item in rows if item.get("verification_status") == "supported"),
            },
            "artifact_refs": artifact_refs(codebase_id),
        }

    def build_reconstruction_report(self, codebase_id: str) -> dict[str, Any]:
        registry = self.read_document_authority_registry(codebase_id)
        claim_graph = self.read_claim_graph(codebase_id)
        current = self.read_current_implementation_model(codebase_id)
        verification = self.read_verification(codebase_id)
        report = _build_report_payload(self.workspace_id, codebase_id, registry, claim_graph, current, verification)
        html_content = _render_report_html(report)
        mermaid = _render_report_mermaid(report)
        svg = _render_report_svg(report)
        write_json(reconstruction_report_path(self.workspace, codebase_id), report)
        _write_text(report_html_path(self.workspace, codebase_id), html_content)
        _write_text(report_mermaid_path(self.workspace, codebase_id), mermaid)
        _write_text(report_svg_path(self.workspace, codebase_id), svg)
        return report

    def read_reconstruction_report(self, codebase_id: str) -> dict[str, Any]:
        payload = read_json(reconstruction_report_path(self.workspace, codebase_id), None)
        if not payload:
            raise FileNotFoundError(ERROR_NOT_BUILT)
        payload["artifact_refs"] = artifact_refs(codebase_id)
        return payload

    def read_report_view(self, codebase_id: str, *, view: str = "html") -> dict[str, Any]:
        path = report_html_path(self.workspace, codebase_id) if view == "html" else report_svg_path(self.workspace, codebase_id)
        if not path.exists():
            raise FileNotFoundError(ERROR_NOT_BUILT)
        report = self.read_reconstruction_report(codebase_id)
        return {
            "schema_version": SCHEMA_VERSION,
            "workspace_id": self.workspace_id,
            "codebase_id": codebase_id,
            "snapshot_id": report.get("snapshot_id"),
            "view": view,
            "content_type": "text/html" if view == "html" else "image/svg+xml",
            "content": path.read_text(encoding="utf-8"),
            "artifact_refs": artifact_refs(codebase_id),
        }

    def create_agent_brief(self, codebase_id: str, *, mode: str = "architecture_review", role: str = "coding_agent", max_tokens: int = 12000) -> dict[str, Any]:
        report = self.read_reconstruction_report(codebase_id)
        verification = self.read_verification(codebase_id)
        brief = _build_brief_payload(self.workspace_id, codebase_id, mode, role, max_tokens, report, verification)
        write_json(brief_path(self.workspace, codebase_id, brief["brief_id"]), brief)
        _write_text(brief_markdown_path(self.workspace, codebase_id, brief["brief_id"]), _render_brief_markdown(brief))
        return brief

    def read_agent_brief(self, codebase_id: str, brief_id: str) -> dict[str, Any]:
        payload = read_json(brief_path(self.workspace, codebase_id, brief_id), None)
        if not payload:
            raise FileNotFoundError(ERROR_NOT_BUILT)
        return payload

    def _latest_snapshot_id(self, codebase_id: str) -> str:
        snapshots = self.snapshots.list_snapshots(codebase_id, limit=1)
        if not snapshots:
            raise FileNotFoundError("SNAPSHOT_NOT_FOUND")
        return str(snapshots[0]["snapshot_id"])


def public_doc_grounded_payload(payload: dict[str, Any]) -> dict[str, Any]:
    public = dict(payload)
    public.setdefault("schema_version", SCHEMA_VERSION)
    return public


def _is_document_path(rel: str) -> bool:
    path = Path(rel)
    return path.suffix.lower() in DOC_SUFFIXES or path.stem.upper() in DOC_NAMES or str(path).lower().startswith("docs/")


def _document_record(root: Path, rel: str, record: dict[str, Any], workspace_id: str, codebase_id: str, snapshot_id: str) -> dict[str, Any] | None:
    path = root / rel
    if not path.exists():
        return None
    doc_type = _doc_type(rel)
    role, level, stale = _authority(rel, doc_type)
    version_hint = _version_hint(rel)
    doc_id = _stable_id("doc", rel, str(record.get("sha256") or ""))
    evidence = [{"path": rel, "line_range": [1, 1], "evidence_type": "document_path"}]
    return {
        "schema_version": SCHEMA_VERSION,
        "workspace_id": workspace_id,
        "codebase_id": codebase_id,
        "snapshot_id": snapshot_id,
        "doc_id": doc_id,
        "repo_path": rel,
        "path": rel,
        "doc_type": doc_type,
        "version_hint": version_hint,
        "phase_hint": _phase_hint(rel),
        "authority_role": role,
        "authority_level": level,
        "stale": stale,
        "supersedes": [],
        "superseded_by": [],
        "sha256": record.get("sha256"),
        "loc": record.get("loc", 0),
        "evidence": evidence,
        "confidence": 0.95 if level == "primary" else 0.7,
        "needs_review": [] if level != "weak" else ["weak document authority"],
    }


def _doc_type(rel: str) -> str:
    low = rel.lower()
    name = Path(rel).name.lower()
    if name.endswith(".drawio"):
        return "drawio"
    if "prd" in low:
        return "prd"
    if "target_architecture" in low or "architecture" in low or "架构" in low:
        return "target_architecture"
    if "gap" in low:
        return "gap_analysis"
    if "audit" in low or "审计" in low:
        return "audit_report"
    if "acceptance" in low or "验收" in low:
        return "acceptance_plan"
    if "development" in low or "plan" in low or "计划" in low:
        return "implementation_plan"
    if name.startswith("readme"):
        return "readme"
    return "project_document"


def _authority(rel: str, doc_type: str) -> tuple[str, str, bool]:
    low = rel.lower()
    is_v237 = any(hint in low for hint in CURRENT_VERSION_HINTS)
    is_legacy_v2 = bool(LEGACY_VERSION_RE.search(low)) and not is_v237
    if is_v237 and doc_type in {"prd", "target_architecture"}:
        return "target", "primary", False
    if is_v237 and doc_type in {"implementation_plan", "acceptance_plan", "gap_analysis"}:
        return "implementation_plan", "supporting", False
    if is_v237 and doc_type == "audit_report":
        return "audit_status", "supporting", False
    if is_legacy_v2:
        return "historical_reference", "historical", True
    if doc_type in {"prd", "target_architecture"}:
        return "target", "primary", False
    if doc_type in {"gap_analysis", "audit_report", "acceptance_plan", "implementation_plan"}:
        return "implementation_plan", "supporting", False
    return "historical_reference" if "history/" in low else "unknown", "weak", "history/" in low


def _version_hint(rel: str) -> str:
    low = rel.lower()
    if any(hint in low for hint in CURRENT_VERSION_HINTS):
        return "V2.37"
    match = LEGACY_VERSION_RE.search(low)
    if not match:
        return ""
    major = match.group(1)
    minor = match.group(2)
    return f"V{major}.{minor}" if minor else f"V{major}"


def _phase_hint(rel: str) -> str:
    match = re.search(r"phase[_-]?(\d+)", rel, flags=re.I)
    return f"Phase {match.group(1)}" if match else ""


def _extract_markdown_claims(path: Path, doc: dict[str, Any]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
    claims: list[dict[str, Any]] = []
    relations: list[dict[str, Any]] = []
    previous_heading: str | None = None
    previous_claim_id: str | None = None
    for index, line in enumerate(lines, start=1):
        text = line.strip()
        if not text:
            continue
        source_block_type = ""
        label = ""
        if text.startswith("#"):
            source_block_type = "heading"
            label = text.lstrip("#").strip()
            previous_heading = label
        elif re.match(r"^[-*+]\s+", text):
            source_block_type = "bullet"
            label = re.sub(r"^[-*+]\s+", "", text).strip()
        elif re.match(r"^\d+[.)]\s+", text):
            source_block_type = "numbered_list"
            label = re.sub(r"^\d+[.)]\s+", "", text).strip()
        elif text.startswith("|") and text.endswith("|") and "---" not in text:
            source_block_type = "table_row"
            label = " | ".join(part.strip() for part in text.strip("|").split("|") if part.strip())
        elif any(hint in text.lower() for hint in ("acceptance", "out of scope", "non-goal", "forbidden", "must", "should")):
            source_block_type = "acceptance_gate" if "acceptance" in text.lower() else "policy"
            label = text
        if not label or len(label) < 4:
            continue
        claim = _claim(
            doc=doc,
            label=label,
            claim_type=_claim_type(label, source_block_type),
            source_block_type=source_block_type,
            line_range=[index, index],
            confidence=_claim_confidence(doc, source_block_type),
        )
        if source_block_type != "heading" and previous_heading:
            claim["parent_heading"] = previous_heading
        claims.append(claim)
        if previous_claim_id and source_block_type != "heading":
            relations.append(_relation(doc, previous_claim_id, claim["claim_id"], "contains", [index, index]))
        previous_claim_id = claim["claim_id"] if source_block_type == "heading" else previous_claim_id
    return claims, relations


def _extract_drawio_claims(path: Path, doc: dict[str, Any]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    parsed = parse_drawio(path, str(doc.get("repo_path") or ""))
    claims: list[dict[str, Any]] = []
    relations: list[dict[str, Any]] = []
    by_cell: dict[str, str] = {}
    for diagram in parsed.get("diagrams", []):
        for node in diagram.get("nodes", []):
            label = str(node.get("label") or "").strip()
            if not label:
                continue
            claim = _claim(
                doc=doc,
                label=label,
                claim_type=_claim_type(label, "diagram_node"),
                source_block_type="diagram_node",
                line_range=None,
                drawio_cell_id=str(node.get("raw_id") or ""),
                confidence=0.68,
            )
            claim["diagram_id"] = diagram.get("diagram_id")
            claims.append(claim)
            if node.get("raw_id"):
                by_cell[str(node["raw_id"])] = claim["claim_id"]
        for edge in diagram.get("edges", []):
            source = by_cell.get(str(edge.get("source") or ""))
            target = by_cell.get(str(edge.get("target") or ""))
            if source and target:
                relation = _relation(doc, source, target, str(edge.get("label") or "diagram_edge") or "diagram_edge", None)
                relation["drawio_cell_id"] = str(edge.get("raw_id") or "")
                relation["confidence"] = 0.66
                relations.append(relation)
    return claims, relations


def _claim(
    *,
    doc: dict[str, Any],
    label: str,
    claim_type: str,
    source_block_type: str,
    line_range: list[int] | None,
    confidence: float,
    drawio_cell_id: str | None = None,
) -> dict[str, Any]:
    claim_id = _stable_id("claim", str(doc.get("doc_id")), source_block_type, label, str(line_range or drawio_cell_id or ""))
    evidence = [{"path": doc.get("repo_path"), "line_range": line_range, "drawio_cell_id": drawio_cell_id, "evidence_type": "document_claim"}]
    needs_review = []
    if source_block_type.startswith("diagram"):
        needs_review.append("drawio claim is document-derived, not code-derived")
    if confidence < 0.75:
        needs_review.append("low confidence claim extraction")
    return {
        "schema_version": SCHEMA_VERSION,
        "workspace_id": doc.get("workspace_id"),
        "codebase_id": doc.get("codebase_id"),
        "snapshot_id": doc.get("snapshot_id"),
        "claim_id": claim_id,
        "doc_id": doc.get("doc_id"),
        "claim_type": claim_type,
        "label": label,
        "normalized_label": _normalize(label),
        "source_path": doc.get("repo_path"),
        "source_block_type": source_block_type,
        "line_range": line_range,
        "drawio_cell_id": drawio_cell_id,
        "authority_role": doc.get("authority_role"),
        "authority_level": doc.get("authority_level"),
        "confidence": round(confidence, 2),
        "evidence": evidence,
        "needs_review": needs_review,
        "is_code_fact": False,
    }


def _relation(doc: dict[str, Any], source_id: str, target_id: str, relation_type: str, line_range: list[int] | None) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "workspace_id": doc.get("workspace_id"),
        "codebase_id": doc.get("codebase_id"),
        "snapshot_id": doc.get("snapshot_id"),
        "relation_id": _stable_id("doc_rel", source_id, target_id, relation_type),
        "source_claim_id": source_id,
        "target_claim_id": target_id,
        "relation_type": _normalize_relation(relation_type),
        "source_path": doc.get("repo_path"),
        "line_range": line_range,
        "evidence": [{"path": doc.get("repo_path"), "line_range": line_range, "evidence_type": "document_relation"}],
        "confidence": 0.72,
    }


def _claim_type(label: str, block_type: str) -> str:
    low = label.lower()
    if block_type == "acceptance_gate" or "验收" in label:
        return "acceptance_gate"
    if "out of scope" in low or "non-goal" in low or "不做" in label or "不是" in label:
        return "non_goal"
    if "forbidden" in low or "禁止" in label or "不能" in label:
        return "forbidden_claim"
    if "provider" in low or "adapter" in low or "适配" in label:
        return "adapter"
    if "runtime" in low or "workflow" in low or "executor" in low or "工作流" in label:
        return "runtime"
    if "api" in low or "http" in low or "mcp" in low or "cli" in low or "接口" in label:
        return "public_interface"
    if "artifact" in low or "storage" in low or "evidence" in low or "证据" in label:
        return "artifact"
    if "governance" in low or "quality" in low or "policy" in low or "治理" in label:
        return "governance_boundary"
    if "layer" in low or "plane" in low or "层" in label:
        return "layer"
    if "phase" in low or "milestone" in low or "阶段" in label:
        return "milestone"
    return "component"


def _claim_confidence(doc: dict[str, Any], block_type: str) -> float:
    base = 0.86 if doc.get("authority_level") == "primary" else 0.74
    if block_type in {"heading", "acceptance_gate"}:
        base += 0.04
    if block_type == "table_row":
        base -= 0.03
    return min(max(base, 0.45), 0.95)


def _target_model(registry: dict[str, Any], claims: list[dict[str, Any]], relations: list[dict[str, Any]]) -> dict[str, Any]:
    target_claims = [claim for claim in claims if claim.get("authority_role") in {"target", "implementation_plan"} and claim.get("claim_type") not in {"non_goal", "forbidden_claim"}]
    nodes = [
        {
            "node_id": f"target:{claim['claim_id']}",
            "claim_id": claim["claim_id"],
            "label": claim["label"],
            "node_type": claim["claim_type"],
            "source_path": claim["source_path"],
            "document_evidence": claim["evidence"],
            "confidence": claim["confidence"],
            "needs_review": claim.get("needs_review", []),
        }
        for claim in target_claims
    ]
    return {
        "schema_version": SCHEMA_VERSION,
        "workspace_id": registry.get("workspace_id"),
        "codebase_id": registry.get("codebase_id"),
        "snapshot_id": registry.get("snapshot_id"),
        "nodes": nodes,
        "edges": [
            {"edge_id": relation["relation_id"], "source_claim_id": relation["source_claim_id"], "target_claim_id": relation["target_claim_id"], "relation_type": relation["relation_type"], "evidence": relation["evidence"]}
            for relation in relations
            if relation.get("source_claim_id") and relation.get("target_claim_id")
        ],
        "summary": {"target_node_count": len(nodes), "target_edge_count": len(relations)},
    }


def _current_model_nodes(
    workspace_id: str,
    codebase_id: str,
    snapshot_id: str,
    files: list[dict[str, Any]],
    surfaces: list[dict[str, Any]],
    symbols: list[dict[str, Any]],
    evidence: list[dict[str, Any]],
    imports: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    nodes: list[dict[str, Any]] = []
    edges: list[dict[str, Any]] = []
    blockers: list[dict[str, Any]] = []
    for surface in surfaces[:300]:
        path = str(surface.get("source_file") or surface.get("path") or "")
        line_range = surface.get("line_range") or [surface.get("start_line") or 1, surface.get("end_line") or surface.get("start_line") or 1]
        label = str(surface.get("name") or surface.get("path") or surface.get("tool_name") or surface.get("command") or surface.get("surface_id") or "")
        node_id = _stable_id("current_surface", str(surface.get("surface_id") or label), path)
        nodes.append(_current_node(workspace_id, codebase_id, snapshot_id, node_id, "public_surface", label, path, line_range, surface))
    for symbol in symbols[:600]:
        path = str(symbol.get("path") or symbol.get("source_file") or "")
        line_range = symbol.get("line_range") or [symbol.get("start_line") or 1, symbol.get("end_line") or symbol.get("start_line") or 1]
        label = str(symbol.get("qualified_name") or symbol.get("name") or symbol.get("symbol_id") or "")
        node_id = _stable_id("current_symbol", str(symbol.get("symbol_id") or label), path)
        nodes.append(_current_node(workspace_id, codebase_id, snapshot_id, node_id, str(symbol.get("kind") or "symbol"), label, path, line_range, symbol))
    for record in files[:800]:
        if not record.get("included", True):
            continue
        rel = str(record.get("path") or "")
        if not rel or not _is_code_like(rel):
            continue
        node_id = _stable_id("current_file", rel)
        nodes.append(_current_node(workspace_id, codebase_id, snapshot_id, node_id, "file", rel, rel, [1, max(1, int(record.get("loc") or 1))], record))
    for item in imports[:400]:
        source = str(item.get("path") or item.get("source") or "")
        target = str(item.get("module") or item.get("imported") or item.get("target") or "")
        if source and target:
            edges.append({"edge_id": _stable_id("current_edge", source, target), "source": source, "target": target, "edge_type": "module_imports_module", "confidence": 0.72})
    if not surfaces:
        blockers.append({"reason": "PUBLIC_SURFACE_ARTIFACT_MISSING", "message": "No public surface inventory was available; project may still be readable through files and symbols."})
    if not symbols:
        blockers.append({"reason": "SYMBOL_ARTIFACT_MISSING", "message": "No symbol index was available; verification falls back to file-level evidence."})
    if not evidence:
        blockers.append({"reason": "TRACE_EVIDENCE_ARTIFACT_MISSING", "message": "No existing trace evidence artifact was available."})
    return _dedupe_by_id(nodes, "node_id"), edges, blockers


def _current_node(workspace_id: str, codebase_id: str, snapshot_id: str, node_id: str, node_type: str, label: str, path: str, line_range: Any, raw: dict[str, Any]) -> dict[str, Any]:
    evidence = [{"path": path, "line_range": _line_range(line_range), "evidence_type": "code_fact"}] if path else []
    return {
        "schema_version": SCHEMA_VERSION,
        "workspace_id": workspace_id,
        "codebase_id": codebase_id,
        "snapshot_id": snapshot_id,
        "node_id": node_id,
        "node_type": node_type,
        "label": label,
        "normalized_label": _normalize(label),
        "source_path": path,
        "line_range": _line_range(line_range),
        "code_evidence": evidence,
        "source_artifact_ref": raw.get("surface_id") or raw.get("symbol_id") or path,
        "confidence": 0.9 if evidence else 0.55,
    }


def _verify_claims(workspace_id: str, codebase_id: str, snapshot_id: str, claims: list[dict[str, Any]], nodes: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    rows: list[dict[str, Any]] = []
    findings: list[dict[str, Any]] = []
    matched_node_ids: set[str] = set()
    for claim in claims:
        if claim.get("claim_type") in {"non_goal", "forbidden_claim"}:
            status = "needs_review"
            reason = "non-goal or forbidden claim is policy, not implementation proof"
            match = None
            strategy = "policy_claim"
            confidence = float(claim.get("confidence") or 0.5)
        else:
            match, strategy, confidence = _best_match(claim, nodes)
            if match and strategy != "token_overlap_only" and confidence >= 0.8 and claim.get("evidence") and match.get("code_evidence"):
                status = "supported"
                reason = "document claim matched by deterministic code evidence"
                matched_node_ids.add(str(match["node_id"]))
            elif match:
                status = "weakly_supported"
                reason = "match requires review or does not satisfy double-evidence threshold"
                matched_node_ids.add(str(match["node_id"]))
            else:
                status = "unsupported"
                reason = "no code evidence matched this document claim"
        row = {
            "schema_version": SCHEMA_VERSION,
            "workspace_id": workspace_id,
            "codebase_id": codebase_id,
            "snapshot_id": snapshot_id,
            "verification_id": _stable_id("verification", str(claim.get("claim_id")), str(match.get("node_id") if match else "")),
            "claim_id": claim.get("claim_id"),
            "claim_label": claim.get("label"),
            "current_node_id": match.get("node_id") if match else None,
            "current_label": match.get("label") if match else None,
            "verification_status": status,
            "match_strategy": strategy,
            "confidence": round(confidence, 2),
            "document_evidence": claim.get("evidence", []),
            "code_evidence": match.get("code_evidence", []) if match else [],
            "reason": reason,
            "needs_review": [] if status == "supported" else [reason],
        }
        rows.append(row)
        if status in {"unsupported", "weakly_supported"}:
            findings.append(
                {
                    "schema_version": SCHEMA_VERSION,
                    "finding_id": _stable_id("drift", str(claim.get("claim_id")), status),
                    "finding_type": "doc_code_mismatch" if status == "unsupported" else "weak_evidence",
                    "severity": "major" if status == "unsupported" and claim.get("authority_level") == "primary" else "minor",
                    "claim_id": claim.get("claim_id"),
                    "message": reason,
                    "document_evidence": claim.get("evidence", []),
                    "code_evidence": match.get("code_evidence", []) if match else [],
                }
            )
    for node in nodes[:100]:
        if str(node.get("node_id")) in matched_node_ids or node.get("node_type") == "file":
            continue
        rows.append(
            {
                "schema_version": SCHEMA_VERSION,
                "workspace_id": workspace_id,
                "codebase_id": codebase_id,
                "snapshot_id": snapshot_id,
                "verification_id": _stable_id("code_not_doc", str(node.get("node_id"))),
                "claim_id": None,
                "claim_label": None,
                "current_node_id": node.get("node_id"),
                "current_label": node.get("label"),
                "verification_status": "code_not_documented",
                "match_strategy": "reverse_coverage",
                "confidence": 0.7,
                "document_evidence": [],
                "code_evidence": node.get("code_evidence", []),
                "reason": "code fact has no matching document claim",
                "needs_review": ["consider documenting this implementation fact"],
            }
        )
    return rows, findings


def _best_match(claim: dict[str, Any], nodes: list[dict[str, Any]]) -> tuple[dict[str, Any] | None, str, float]:
    label = str(claim.get("label") or "")
    normalized = _normalize(label)
    if not normalized:
        return None, "none", 0.0
    best: tuple[dict[str, Any] | None, str, float] = (None, "none", 0.0)
    for node in nodes:
        node_label = str(node.get("label") or "")
        node_path = str(node.get("source_path") or "")
        node_norm = _normalize(f"{node_label} {node_path}")
        if normalized and normalized == _normalize(node_label):
            return node, "exact_label_match", 0.94
        if _contains_identifier(label, node_label) or _contains_identifier(label, node_path):
            score = 0.86
            if score > best[2]:
                best = (node, "path_and_line_evidence_match", score)
        else:
            overlap = _token_overlap(normalized, node_norm)
            if overlap > best[2]:
                best = (node, "token_overlap_only", overlap)
    if best[0] and best[2] >= 0.4:
        return best
    return None, "none", 0.0


def _contains_identifier(label: str, value: str) -> bool:
    if not label or not value:
        return False
    low_label = label.lower()
    low_value = value.lower()
    candidates = {low_value, Path(low_value).name, Path(low_value).stem}
    for candidate in candidates:
        if candidate and len(candidate) >= 4 and candidate in low_label:
            return True
    if "/" in low_label and low_label.strip("`'\"") in low_value:
        return True
    return False


def _token_overlap(a: str, b: str) -> float:
    left = set(a.split())
    right = set(b.split())
    if not left or not right:
        return 0.0
    return len(left & right) / max(len(left), len(right))


def _build_report_payload(workspace_id: str, codebase_id: str, registry: dict[str, Any], claim_graph: dict[str, Any], current: dict[str, Any], verification: dict[str, Any]) -> dict[str, Any]:
    rows = verification.get("verification_rows", [])
    by_status = Counter(str(row.get("verification_status")) for row in rows)
    supported = [row for row in rows if row.get("verification_status") == "supported"][:30]
    needs_review = [row for row in rows if row.get("verification_status") in {"weakly_supported", "unsupported", "needs_review"}][:50]
    report = {
        "schema_version": SCHEMA_VERSION,
        "workspace_id": workspace_id,
        "codebase_id": codebase_id,
        "snapshot_id": registry.get("snapshot_id"),
        "report_id": _stable_id("report", codebase_id, str(registry.get("snapshot_id") or "")),
        "sections": {
            "target_architecture_from_docs": claim_graph.get("target_architecture_model", {}),
            "current_implementation_from_code": {"summary": current.get("summary", {}), "sample_nodes": current.get("nodes", [])[:60], "blockers": current.get("blockers", [])},
            "diff_and_drift": {"summary": verification.get("summary", {}), "findings": verification.get("drift_findings", [])[:80]},
            "needs_review": needs_review,
            "supported_claims": supported,
        },
        "summary": {
            "document_count": registry.get("summary", {}).get("document_count", 0),
            "claim_count": claim_graph.get("summary", {}).get("claim_count", 0),
            "current_node_count": current.get("summary", {}).get("node_count", 0),
            "verification_count": len(rows),
            "by_status": dict(sorted(by_status.items())),
            "supported_count": by_status.get("supported", 0),
            "needs_review_count": len(needs_review),
        },
        "artifact_refs": artifact_refs(codebase_id),
        "warnings": _collect_warnings(registry, claim_graph, current, verification),
    }
    return report


def _render_report_html(report: dict[str, Any]) -> str:
    summary = report.get("summary", {})
    sections = report.get("sections", {})
    target_nodes = sections.get("target_architecture_from_docs", {}).get("nodes", [])[:8]
    current_nodes = sections.get("current_implementation_from_code", {}).get("sample_nodes", [])[:8]
    supported = sections.get("supported_claims", [])[:12]
    needs_review = sections.get("needs_review", [])[:20]
    svg = _render_report_svg(report)
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <title>V2.37 文档驱动架构核查报告</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; margin: 0; color: #172033; background: #f8fafc; }}
    header {{ padding: 28px 36px; background: #0f172a; color: white; }}
    main {{ padding: 24px 36px 48px; }}
    h1, h2 {{ margin: 0 0 12px; }}
    section {{ background: white; border: 1px solid #d8dee9; border-radius: 8px; padding: 18px; margin: 18px 0; }}
    .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 12px; }}
    .metric {{ border: 1px solid #e2e8f0; border-radius: 8px; padding: 12px; background: #f8fafc; }}
    .metric strong {{ display: block; font-size: 24px; color: #0f766e; }}
    table {{ width: 100%; border-collapse: collapse; }}
    th, td {{ border-bottom: 1px solid #e2e8f0; text-align: left; padding: 8px; vertical-align: top; }}
    th {{ background: #f1f5f9; }}
    .warn {{ color: #b45309; font-weight: 600; }}
    .ok {{ color: #047857; font-weight: 600; }}
    .diagram {{ overflow-x: auto; border: 1px solid #e2e8f0; border-radius: 8px; padding: 12px; background: #fff; }}
  </style>
</head>
<body>
<header>
  <h1>V2.37 文档驱动架构核查报告</h1>
  <p>目标：从项目 docs 重塑目标架构，从代码事实生成当前实现模型，并用双边 evidence 核查差异。</p>
</header>
<main>
  <section>
    <h2>一、总体结论</h2>
    <div class="grid">
      <div class="metric"><span>文档数</span><strong>{summary.get("document_count", 0)}</strong></div>
      <div class="metric"><span>架构声明</span><strong>{summary.get("claim_count", 0)}</strong></div>
      <div class="metric"><span>当前代码节点</span><strong>{summary.get("current_node_count", 0)}</strong></div>
      <div class="metric"><span>已支持声明</span><strong>{summary.get("supported_count", 0)}</strong></div>
      <div class="metric"><span>需复核项</span><strong>{summary.get("needs_review_count", 0)}</strong></div>
    </div>
  </section>
  <section>
    <h2>二、目标架构与当前实现关系图</h2>
    <div class="diagram">{svg}</div>
  </section>
  <section>
    <h2>三、Target Architecture from Docs</h2>
    {_html_list(target_nodes, "label", "source_path")}
  </section>
  <section>
    <h2>四、Current Implementation from Code Facts</h2>
    {_html_list(current_nodes, "label", "source_path")}
  </section>
  <section>
    <h2>五、Supported Claims</h2>
    {_html_rows(supported)}
  </section>
  <section>
    <h2>六、Needs Review / Drift</h2>
    {_html_rows(needs_review)}
  </section>
</main>
</body>
</html>"""


def _render_report_mermaid(report: dict[str, Any]) -> str:
    sections = report.get("sections", {})
    target_nodes = sections.get("target_architecture_from_docs", {}).get("nodes", [])[:6]
    current_nodes = sections.get("current_implementation_from_code", {}).get("sample_nodes", [])[:6]
    lines = ["flowchart LR", "  docs[\"Target Architecture from Docs\"]", "  code[\"Current Implementation from Code Facts\"]", "  diff[\"Diff / Drift / Needs Review\"]"]
    for idx, node in enumerate(target_nodes):
        lines.append(f"  t{idx}[\"{_mermaid_label(str(node.get('label') or 'target'))}\"]")
        lines.append(f"  docs --> t{idx}")
    for idx, node in enumerate(current_nodes):
        lines.append(f"  c{idx}[\"{_mermaid_label(str(node.get('label') or 'code'))}\"]")
        lines.append(f"  code --> c{idx}")
    lines.append("  docs --> diff")
    lines.append("  code --> diff")
    return "\n".join(lines) + "\n"


def _render_report_svg(report: dict[str, Any]) -> str:
    summary = report.get("summary", {})
    labels = [
        ("Target from Docs", summary.get("claim_count", 0), "#2563eb"),
        ("Current from Code", summary.get("current_node_count", 0), "#059669"),
        ("Supported", summary.get("supported_count", 0), "#0f766e"),
        ("Needs Review", summary.get("needs_review_count", 0), "#d97706"),
    ]
    width = 980
    height = 260
    boxes = []
    for idx, (label, count, color) in enumerate(labels):
        x = 30 + idx * 235
        boxes.append(f'<rect x="{x}" y="70" width="190" height="100" rx="8" fill="{color}" opacity="0.12" stroke="{color}" />')
        boxes.append(f'<text x="{x + 18}" y="110" font-family="Arial" font-size="16" fill="#0f172a">{html.escape(label)}</text>')
        boxes.append(f'<text x="{x + 18}" y="145" font-family="Arial" font-size="28" font-weight="700" fill="{color}">{html.escape(str(count))}</text>')
        if idx < len(labels) - 1:
            boxes.append(f'<path d="M{x + 195} 120 L{x + 225} 120" stroke="#64748b" stroke-width="2" marker-end="url(#arrow)" />')
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-label="V2.37 architecture relation chart"><defs><marker id="arrow" markerWidth="10" markerHeight="10" refX="6" refY="3" orient="auto"><path d="M0,0 L0,6 L7,3 z" fill="#64748b"/></marker></defs><rect width="{width}" height="{height}" fill="#ffffff"/><text x="30" y="38" font-family="Arial" font-size="20" font-weight="700" fill="#0f172a">文档目标架构 / 当前代码实现 / 差异核查</text>{"".join(boxes)}</svg>'


def _build_brief_payload(workspace_id: str, codebase_id: str, mode: str, role: str, max_tokens: int, report: dict[str, Any], verification: dict[str, Any]) -> dict[str, Any]:
    rows = verification.get("verification_rows", [])
    supported = [row for row in rows if row.get("verification_status") == "supported"]
    risky = [row for row in rows if row.get("verification_status") in {"unsupported", "weakly_supported", "needs_review"}]
    recommendations = []
    for row in supported[:20]:
        recommendations.append(
            {
                "recommendation": f"优先阅读并遵守已验证架构声明：{row.get('claim_label')}",
                "evidence_refs": list(row.get("document_evidence", [])) + list(row.get("code_evidence", [])),
                "needs_review": [],
                "priority": "high",
            }
        )
    for row in risky[:20]:
        recommendations.append(
            {
                "recommendation": f"复核架构声明与代码事实的差异：{row.get('claim_label') or row.get('current_label')}",
                "evidence_refs": list(row.get("document_evidence", [])) + list(row.get("code_evidence", [])),
                "needs_review": row.get("needs_review") or [row.get("reason")],
                "priority": "medium",
            }
        )
    token_estimate = 250 + sum(len(str(item.get("recommendation") or "")) // 3 + 40 for item in recommendations)
    omitted: list[dict[str, Any]] = []
    while recommendations and token_estimate > max_tokens:
        omitted_item = recommendations.pop()
        omitted.append({"reason": "token_budget", "item": omitted_item.get("recommendation")})
        token_estimate = 250 + sum(len(str(item.get("recommendation") or "")) // 3 + 40 for item in recommendations)
    brief_id = _stable_id("doc_grounded_brief", codebase_id, mode, role, str(report.get("snapshot_id") or ""), str(max_tokens))
    payload = {
        "schema_version": SCHEMA_VERSION,
        "workspace_id": workspace_id,
        "codebase_id": codebase_id,
        "snapshot_id": report.get("snapshot_id"),
        "brief_id": brief_id,
        "mode": mode,
        "role": role,
        "source_phase_refs": ["Phase 103", "Phase 104", "Phase 105", "Phase 106", "Phase 107"],
        "summary": report.get("summary", {}),
        "sections": {
            "target_current_diff": report.get("sections", {}).get("diff_and_drift", {}),
            "recommended_reading_order": [row.get("claim_label") for row in supported[:10] if row.get("claim_label")],
        },
        "recommendations": recommendations,
        "omitted_items": omitted,
        "token_estimate": token_estimate,
        "artifact_refs": artifact_refs(codebase_id) + [{"type": "architecture_agent_brief", "artifact_ref": f"architecture-doc-grounded://{codebase_id}/briefs/{brief_id}.json"}],
        "warnings": [] if recommendations else ["NO_EVIDENCE_BACKED_RECOMMENDATION"],
    }
    return payload


def _render_brief_markdown(brief: dict[str, Any]) -> str:
    lines = [
        "# V2.37 Agent Architecture Brief",
        "",
        f"- mode: `{brief.get('mode')}`",
        f"- role: `{brief.get('role')}`",
        f"- token_estimate: `{brief.get('token_estimate')}`",
        "",
        "## Recommendations",
    ]
    for item in brief.get("recommendations", []):
        marker = "needs_review" if item.get("needs_review") else "evidence-backed"
        lines.append(f"- [{marker}] {item.get('recommendation')}")
    if brief.get("omitted_items"):
        lines.extend(["", "## Omitted Items"])
        for item in brief["omitted_items"]:
            lines.append(f"- {item.get('reason')}: {item.get('item')}")
    return "\n".join(lines) + "\n"


def _html_list(items: list[dict[str, Any]], label_key: str, path_key: str) -> str:
    if not items:
        return "<p class=\"warn\">暂无可展示数据。</p>"
    rows = []
    for item in items:
        rows.append(f"<tr><td>{html.escape(str(item.get(label_key) or ''))}</td><td>{html.escape(str(item.get(path_key) or ''))}</td></tr>")
    return "<table><thead><tr><th>节点</th><th>证据路径</th></tr></thead><tbody>" + "".join(rows) + "</tbody></table>"


def _html_rows(rows: list[dict[str, Any]]) -> str:
    if not rows:
        return "<p class=\"warn\">暂无条目。</p>"
    rendered = []
    for row in rows:
        status = str(row.get("verification_status") or "")
        cls = "ok" if status == "supported" else "warn"
        rendered.append(
            "<tr>"
            f"<td class=\"{cls}\">{html.escape(status)}</td>"
            f"<td>{html.escape(str(row.get('claim_label') or row.get('current_label') or ''))}</td>"
            f"<td>{html.escape(str(row.get('match_strategy') or ''))}</td>"
            f"<td>{html.escape(str(row.get('reason') or ''))}</td>"
            "</tr>"
        )
    return "<table><thead><tr><th>状态</th><th>对象</th><th>匹配策略</th><th>说明</th></tr></thead><tbody>" + "".join(rendered) + "</tbody></table>"


def _collect_warnings(*payloads: dict[str, Any]) -> list[str]:
    warnings: list[str] = []
    for payload in payloads:
        for item in payload.get("warnings", []) or []:
            warnings.append(str(item))
        for blocker in payload.get("blockers", []) or payload.get("summary", {}).get("blockers", []) or []:
            warnings.append(str(blocker))
    return sorted(set(warnings))


def _is_code_like(rel: str) -> bool:
    return Path(rel).suffix.lower() in {".py", ".ts", ".tsx", ".js", ".jsx", ".vue", ".rs", ".go", ".java", ".kt", ".swift", ".sh"}


def _line_range(value: Any) -> list[int]:
    if isinstance(value, list) and len(value) >= 2:
        try:
            start = max(1, int(value[0]))
            end = max(start, int(value[1]))
            return [start, end]
        except (TypeError, ValueError):
            return [1, 1]
    return [1, 1]


def _dedupe_by_id(items: list[dict[str, Any]], key: str) -> list[dict[str, Any]]:
    seen: set[str] = set()
    result: list[dict[str, Any]] = []
    for item in items:
        value = str(item.get(key) or "")
        if not value or value in seen:
            continue
        seen.add(value)
        result.append(item)
    return result


def _stable_id(prefix: str, *parts: str) -> str:
    digest = hashlib.sha256("\x1f".join(str(part) for part in parts).encode("utf-8")).hexdigest()[:20]
    return f"{prefix}_{digest}"


def _normalize(text: str) -> str:
    text = re.sub(r"[`*_#|>()[\]{}:;,]", " ", str(text).lower())
    text = re.sub(r"[^a-z0-9_./\-\u4e00-\u9fff]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def _normalize_relation(text: str) -> str:
    value = _normalize(text).replace(" ", "_").strip("_")
    return value or "related_to"


def _snapshot_id_from_items(items: list[dict[str, Any]]) -> str | None:
    for item in items:
        if item.get("snapshot_id"):
            return str(item["snapshot_id"])
    return None


def _mermaid_label(label: str) -> str:
    return html.escape(label.replace('"', "'")[:60])


def _write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")

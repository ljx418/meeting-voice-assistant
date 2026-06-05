"""Document asset registry for V2.7 architecture documentation governance."""

from __future__ import annotations

import hashlib
import re
from collections import Counter
from pathlib import Path
from typing import Any

from data_service.mcp_common import now


SCHEMA_VERSION = "v2.7"
DOC_SUFFIXES = {".md", ".markdown", ".drawio", ".mmd"}
PATH_HINTS = ("docs/", "readme", "architecture", "arch", "design", "prd", "gap", "target", "acceptance", "audit", "roadmap", "matrix", "handoff")


def build_document_registry(
    *,
    workspace_id: str,
    codebase_id: str,
    snapshot_id: str,
    root: Path,
    files: list[dict[str, Any]],
) -> dict[str, Any]:
    created_at = now()
    documents: list[dict[str, Any]] = []
    sources: list[dict[str, Any]] = []
    for record in files:
        if not record.get("included", True):
            continue
        rel = str(record.get("path") or "")
        if not _is_document_candidate(rel):
            continue
        path = root / rel
        title, evidence = _document_title_and_evidence(path, rel, record)
        doc_type = _doc_type(rel, title)
        phase_hint, version_hint = _phase_version_hint(rel, title)
        authority_role, authority_level = _authority(doc_type, phase_hint, rel)
        doc_id = stable_id("archdoc", snapshot_id, rel)
        source = {
            "schema_version": SCHEMA_VERSION,
            "workspace_id": workspace_id,
            "codebase_id": codebase_id,
            "snapshot_id": snapshot_id,
            "source_id": stable_id("archdocsrc", snapshot_id, rel),
            "doc_id": doc_id,
            "path": rel,
            "repo_path": rel,
            "source_type": _source_type(rel),
            "parser": _parser_name(rel),
            "line_range": record.get("line_range"),
            "evidence": evidence,
            "created_at": created_at,
        }
        doc = {
            "schema_version": SCHEMA_VERSION,
            "workspace_id": workspace_id,
            "codebase_id": codebase_id,
            "snapshot_id": snapshot_id,
            "doc_id": doc_id,
            "doc_type": doc_type,
            "path": rel,
            "repo_path": rel,
            "title": title or Path(rel).name,
            "phase_hint": phase_hint,
            "version_hint": version_hint,
            "scope_hint": _scope_hint(rel, title),
            "authority_role": authority_role,
            "authority_level": authority_level,
            "supersedes": [],
            "superseded_by": [],
            "stale_hint": _stale_hint(phase_hint),
            "evidence": evidence,
            "confidence": _confidence(doc_type, authority_level),
            "needs_review": _needs_review(doc_type, authority_level),
            "created_at": created_at,
        }
        documents.append(doc)
        sources.append(source)
    documents = sorted(_dedupe(documents, "doc_id"), key=lambda item: item["path"])
    sources = sorted(_dedupe(sources, "source_id"), key=lambda item: item["path"])
    summary = _summary(workspace_id, codebase_id, snapshot_id, documents, created_at)
    return {"schema_version": SCHEMA_VERSION, "workspace_id": workspace_id, "codebase_id": codebase_id, "snapshot_id": snapshot_id, "documents": documents, "sources": sources, "summary": summary}


def public_document_registry_payload(payload: dict[str, Any], artifact_refs: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "schema_version": payload.get("schema_version", SCHEMA_VERSION),
        "workspace_id": payload.get("workspace_id"),
        "codebase_id": payload.get("codebase_id"),
        "snapshot_id": payload.get("snapshot_id"),
        "summary": payload.get("summary", {}),
        "documents": payload.get("documents", []),
        "sources": payload.get("sources", []),
        "artifact_refs": artifact_refs,
    }


def stable_id(prefix: str, *parts: Any) -> str:
    raw = "\x1f".join(str(part) for part in parts)
    return f"{prefix}_{hashlib.sha256(raw.encode('utf-8')).hexdigest()[:16]}"


def _is_document_candidate(path: str) -> bool:
    low = path.lower()
    suffix = Path(path).suffix.lower()
    if suffix not in DOC_SUFFIXES:
        return False
    if suffix == ".drawio":
        return True
    return any(hint in low for hint in PATH_HINTS)


def _document_title_and_evidence(path: Path, rel: str, record: dict[str, Any]) -> tuple[str, list[dict[str, Any]]]:
    line_range = record.get("line_range")
    title = ""
    if path.exists() and path.suffix.lower() in {".md", ".markdown"}:
        try:
            for idx, line in enumerate(path.read_text(encoding="utf-8", errors="ignore").splitlines(), start=1):
                stripped = line.strip()
                if stripped.startswith("#"):
                    title = stripped.lstrip("#").strip()
                    line_range = [idx, idx]
                    break
        except OSError:
            pass
    evidence = [{"type": "source_file", "path": rel, "repo_path": rel, "line_range": line_range, "extractor": "architecture_doc_registry"}]
    return title, evidence


def _doc_type(path: str, title: str) -> str:
    low = f"{path} {title}".lower()
    name = Path(path).name.lower()
    if name == "readme.md" or name == "00_readme.md":
        return "readme"
    if "api_matrix" in low or "api-matrix" in low:
        return "api_matrix"
    if "handoff" in low:
        return "handoff_summary"
    if Path(path).suffix.lower() == ".drawio":
        return "drawio"
    if "target_architecture" in low or "target-architecture" in low or "target architecture" in low:
        return "target_architecture"
    if "prd" in low:
        return "prd"
    if "gap" in low:
        return "gap_analysis"
    if "acceptance" in low:
        return "acceptance_plan"
    if "audit" in low:
        return "audit_report"
    if "development" in low or "plan" in low or "roadmap" in low:
        return "development_plan"
    if "architecture" in low or "/design/" in low or "design/" in low:
        return "target_architecture"
    return "unknown_architecture_doc"


def _phase_version_hint(path: str, title: str) -> tuple[str, str]:
    value = f"{path} {title}"
    matches = re.findall(r"\b[Vv](\d+(?:[._]\d+)*)", value)
    if not matches:
        return "", ""
    version = max(matches, key=lambda item: (item.count(".") + item.count("_"), len(item))).replace("_", ".")
    return f"V{version}", version


def _authority(doc_type: str, phase_hint: str, path: str) -> tuple[str, str]:
    is_v27 = phase_hint.startswith("V2.7") or "v2_7" in path.lower()
    if not is_v27 and phase_hint:
        return "historical_reference", "historical"
    if doc_type in {"prd", "target_architecture"}:
        return "target", "primary"
    if doc_type == "development_plan":
        return "implementation_plan", "supporting"
    if doc_type == "acceptance_plan":
        return "acceptance_result", "supporting"
    if doc_type == "audit_report":
        return "audit_status", "supporting"
    if doc_type in {"gap_analysis", "api_matrix", "handoff_summary"}:
        return "target" if is_v27 else "historical_reference", "supporting" if is_v27 else "historical"
    if doc_type == "readme":
        return "historical_reference" if phase_hint else "unknown", "weak"
    return "unknown", "weak"


def _scope_hint(path: str, title: str) -> str:
    low = f"{path} {title}".lower()
    if "documentation-code" in low or "doc_code" in low or "v2_7" in low:
        return "documentation_code_architecture_governance"
    if "research_notebook" in low or "research-notebook" in low:
        return "research_notebook"
    if "architecture" in low or "design" in low:
        return "architecture"
    return "project_documentation"


def _stale_hint(phase_hint: str) -> bool:
    if not phase_hint:
        return False
    return not phase_hint.startswith("V2.7")


def _confidence(doc_type: str, authority_level: str) -> float:
    if authority_level == "primary":
        return 0.9
    if authority_level == "supporting":
        return 0.8
    if authority_level == "historical":
        return 0.7
    if doc_type == "unknown_architecture_doc":
        return 0.45
    return 0.6


def _needs_review(doc_type: str, authority_level: str) -> list[dict[str, Any]]:
    if doc_type == "unknown_architecture_doc":
        return [{"code": "UNKNOWN_DOCUMENT_TYPE", "reason": "Document matched architecture hints but type is ambiguous."}]
    if authority_level == "weak":
        return [{"code": "WEAK_DOCUMENT_AUTHORITY", "reason": "Document authority is weak and needs review before use as architecture source."}]
    return []


def _source_type(path: str) -> str:
    suffix = Path(path).suffix.lower()
    if suffix == ".drawio":
        return "drawio"
    if suffix == ".mmd":
        return "mermaid"
    return "markdown"


def _parser_name(path: str) -> str:
    return {"drawio": "drawio_mxcell", "mermaid": "mermaid_text", "markdown": "markdown_document_registry"}[_source_type(path)]


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


def _summary(workspace_id: str, codebase_id: str, snapshot_id: str, documents: list[dict[str, Any]], created_at: str) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "workspace_id": workspace_id,
        "codebase_id": codebase_id,
        "snapshot_id": snapshot_id,
        "created_at": created_at,
        "document_count": len(documents),
        "doc_type_counts": dict(sorted(Counter(item["doc_type"] for item in documents).items())),
        "authority_role_counts": dict(sorted(Counter(item["authority_role"] for item in documents).items())),
        "authority_level_counts": dict(sorted(Counter(item["authority_level"] for item in documents).items())),
        "needs_review_count": sum(1 for item in documents if item.get("needs_review")),
        "stale_hint_count": sum(1 for item in documents if item.get("stale_hint")),
    }

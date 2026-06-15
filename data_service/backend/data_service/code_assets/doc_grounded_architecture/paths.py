"""Artifact paths for V2.37 document-grounded architecture outputs."""

from __future__ import annotations

from pathlib import Path

from data_service.code_assets.artifacts import architecture_dir


def doc_grounded_dir(workspace: Path, codebase_id: str) -> Path:
    return architecture_dir(workspace, codebase_id) / "doc_grounded"


def doc_authority_registry_path(workspace: Path, codebase_id: str) -> Path:
    return doc_grounded_dir(workspace, codebase_id) / "document_authority_registry.json"


def doc_authority_documents_path(workspace: Path, codebase_id: str) -> Path:
    return doc_grounded_dir(workspace, codebase_id) / "documents.jsonl"


def doc_claims_path(workspace: Path, codebase_id: str) -> Path:
    return doc_grounded_dir(workspace, codebase_id) / "architecture_claims.jsonl"


def doc_claim_relations_path(workspace: Path, codebase_id: str) -> Path:
    return doc_grounded_dir(workspace, codebase_id) / "architecture_claim_relations.jsonl"


def target_model_path(workspace: Path, codebase_id: str) -> Path:
    return doc_grounded_dir(workspace, codebase_id) / "target_architecture_model.json"


def current_model_path(workspace: Path, codebase_id: str) -> Path:
    return doc_grounded_dir(workspace, codebase_id) / "current_implementation_model.json"


def verification_matrix_path(workspace: Path, codebase_id: str) -> Path:
    return doc_grounded_dir(workspace, codebase_id) / "verification_matrix.jsonl"


def drift_findings_path(workspace: Path, codebase_id: str) -> Path:
    return doc_grounded_dir(workspace, codebase_id) / "drift_findings.jsonl"


def reconstruction_report_path(workspace: Path, codebase_id: str) -> Path:
    return doc_grounded_dir(workspace, codebase_id) / "reconstruction_report.json"


def views_dir(workspace: Path, codebase_id: str) -> Path:
    return doc_grounded_dir(workspace, codebase_id) / "views"


def report_html_path(workspace: Path, codebase_id: str) -> Path:
    return views_dir(workspace, codebase_id) / "document_grounded_architecture_report.html"


def report_mermaid_path(workspace: Path, codebase_id: str) -> Path:
    return views_dir(workspace, codebase_id) / "document_grounded_architecture_diff.mmd"


def report_svg_path(workspace: Path, codebase_id: str) -> Path:
    return views_dir(workspace, codebase_id) / "document_grounded_architecture_diff.svg"


def brief_path(workspace: Path, codebase_id: str, brief_id: str) -> Path:
    safe = (brief_id or "architecture_brief").strip().replace("/", "_")
    return doc_grounded_dir(workspace, codebase_id) / "briefs" / f"{safe}.json"


def brief_markdown_path(workspace: Path, codebase_id: str, brief_id: str) -> Path:
    safe = (brief_id or "architecture_brief").strip().replace("/", "_")
    return doc_grounded_dir(workspace, codebase_id) / "briefs" / f"{safe}.md"


def artifact_refs(codebase_id: str) -> list[dict[str, str]]:
    base = f"architecture-doc-grounded://{codebase_id}"
    return [
        {"type": "document_authority_registry", "artifact_ref": f"{base}/document_authority_registry.json"},
        {"type": "architecture_claims", "artifact_ref": f"{base}/architecture_claims.jsonl"},
        {"type": "target_architecture_model", "artifact_ref": f"{base}/target_architecture_model.json"},
        {"type": "current_implementation_model", "artifact_ref": f"{base}/current_implementation_model.json"},
        {"type": "verification_matrix", "artifact_ref": f"{base}/verification_matrix.jsonl"},
        {"type": "reconstruction_report", "artifact_ref": f"{base}/reconstruction_report.json"},
        {"type": "architecture_report_html", "artifact_ref": f"{base}/views/document_grounded_architecture_report.html"},
    ]

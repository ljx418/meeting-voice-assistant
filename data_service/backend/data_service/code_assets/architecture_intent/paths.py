"""Artifact paths for architecture intent artifacts."""

from __future__ import annotations

from pathlib import Path

from ..artifacts import codebase_dir


def architecture_intent_dir(workspace: Path, codebase_id: str) -> Path:
    return codebase_dir(workspace, codebase_id) / "architecture" / "intent"


def architecture_intent_sources_dir(workspace: Path, codebase_id: str) -> Path:
    return architecture_intent_dir(workspace, codebase_id) / "sources"


def architecture_intent_sources_path(workspace: Path, codebase_id: str) -> Path:
    return architecture_intent_sources_dir(workspace, codebase_id) / "architecture_sources.jsonl"


def architecture_intent_diagram_cells_path(workspace: Path, codebase_id: str) -> Path:
    return architecture_intent_sources_dir(workspace, codebase_id) / "diagram_cells.jsonl"


def architecture_intent_source_blocks_path(workspace: Path, codebase_id: str) -> Path:
    return architecture_intent_sources_dir(workspace, codebase_id) / "source_blocks.jsonl"


def architecture_intent_source_summary_path(workspace: Path, codebase_id: str) -> Path:
    return architecture_intent_sources_dir(workspace, codebase_id) / "architecture_source_summary.json"


def architecture_intent_source_artifact_refs(codebase_id: str) -> list[dict[str, str]]:
    base = f"architecture-intent://{codebase_id}/sources"
    return [
        {"type": "architecture_sources", "artifact_ref": f"{base}/architecture_sources.jsonl"},
        {"type": "architecture_diagram_cells", "artifact_ref": f"{base}/diagram_cells.jsonl"},
        {"type": "architecture_source_blocks", "artifact_ref": f"{base}/source_blocks.jsonl"},
        {"type": "architecture_source_summary", "artifact_ref": f"{base}/architecture_source_summary.json"},
    ]


def architecture_intent_claims_dir(workspace: Path, codebase_id: str) -> Path:
    return architecture_intent_dir(workspace, codebase_id) / "claims"


def architecture_intent_diagram_claims_path(workspace: Path, codebase_id: str) -> Path:
    return architecture_intent_claims_dir(workspace, codebase_id) / "diagram_claims.jsonl"


def architecture_intent_diagram_relations_path(workspace: Path, codebase_id: str) -> Path:
    return architecture_intent_claims_dir(workspace, codebase_id) / "diagram_relations.jsonl"


def architecture_intent_diagram_claim_summary_path(workspace: Path, codebase_id: str) -> Path:
    return architecture_intent_claims_dir(workspace, codebase_id) / "diagram_claim_summary.json"


def architecture_intent_claim_artifact_refs(codebase_id: str) -> list[dict[str, str]]:
    base = f"architecture-intent://{codebase_id}/claims"
    return [
        {"type": "architecture_diagram_claims", "artifact_ref": f"{base}/diagram_claims.jsonl"},
        {"type": "architecture_diagram_relations", "artifact_ref": f"{base}/diagram_relations.jsonl"},
        {"type": "architecture_diagram_claim_summary", "artifact_ref": f"{base}/diagram_claim_summary.json"},
    ]


def architecture_intent_proof_graph_dir(workspace: Path, codebase_id: str) -> Path:
    return architecture_intent_dir(workspace, codebase_id) / "proof_graph"


def architecture_intent_proof_nodes_path(workspace: Path, codebase_id: str) -> Path:
    return architecture_intent_proof_graph_dir(workspace, codebase_id) / "proof_nodes.jsonl"


def architecture_intent_proof_edges_path(workspace: Path, codebase_id: str) -> Path:
    return architecture_intent_proof_graph_dir(workspace, codebase_id) / "proof_edges.jsonl"


def architecture_intent_evidence_bundles_path(workspace: Path, codebase_id: str) -> Path:
    return architecture_intent_proof_graph_dir(workspace, codebase_id) / "evidence_bundles.jsonl"


def architecture_intent_proof_graph_summary_path(workspace: Path, codebase_id: str) -> Path:
    return architecture_intent_proof_graph_dir(workspace, codebase_id) / "proof_graph_summary.json"


def architecture_intent_proof_graph_artifact_refs(codebase_id: str) -> list[dict[str, str]]:
    base = f"architecture-intent://{codebase_id}/proof_graph"
    return [
        {"type": "architecture_intent_proof_nodes", "artifact_ref": f"{base}/proof_nodes.jsonl"},
        {"type": "architecture_intent_proof_edges", "artifact_ref": f"{base}/proof_edges.jsonl"},
        {"type": "architecture_intent_evidence_bundles", "artifact_ref": f"{base}/evidence_bundles.jsonl"},
        {"type": "architecture_intent_proof_graph_summary", "artifact_ref": f"{base}/proof_graph_summary.json"},
    ]


def architecture_intent_inference_dir(workspace: Path, codebase_id: str) -> Path:
    return architecture_intent_dir(workspace, codebase_id) / "intent"


def architecture_intent_candidates_path(workspace: Path, codebase_id: str) -> Path:
    return architecture_intent_inference_dir(workspace, codebase_id) / "intent_candidates.jsonl"


def architecture_intent_counter_evidence_path(workspace: Path, codebase_id: str) -> Path:
    return architecture_intent_inference_dir(workspace, codebase_id) / "counter_evidence.jsonl"


def architecture_intent_inference_summary_path(workspace: Path, codebase_id: str) -> Path:
    return architecture_intent_inference_dir(workspace, codebase_id) / "intent_summary.json"


def architecture_intent_inference_artifact_refs(codebase_id: str) -> list[dict[str, str]]:
    base = f"architecture-intent://{codebase_id}/intent"
    return [
        {"type": "architecture_intent_candidates", "artifact_ref": f"{base}/intent_candidates.jsonl"},
        {"type": "architecture_intent_counter_evidence", "artifact_ref": f"{base}/counter_evidence.jsonl"},
        {"type": "architecture_intent_summary", "artifact_ref": f"{base}/intent_summary.json"},
    ]


def architecture_intent_verification_dir(workspace: Path, codebase_id: str) -> Path:
    return architecture_intent_dir(workspace, codebase_id) / "verification"


def architecture_intent_diagram_code_alignment_path(workspace: Path, codebase_id: str) -> Path:
    return architecture_intent_verification_dir(workspace, codebase_id) / "diagram_code_alignment.jsonl"


def architecture_intent_undocumented_code_facts_path(workspace: Path, codebase_id: str) -> Path:
    return architecture_intent_verification_dir(workspace, codebase_id) / "undocumented_code_facts.jsonl"


def architecture_intent_architecture_diff_path(workspace: Path, codebase_id: str) -> Path:
    return architecture_intent_verification_dir(workspace, codebase_id) / "architecture_diff.json"


def architecture_intent_verification_summary_path(workspace: Path, codebase_id: str) -> Path:
    return architecture_intent_verification_dir(workspace, codebase_id) / "verification_summary.json"


def architecture_intent_verification_artifact_refs(codebase_id: str) -> list[dict[str, str]]:
    base = f"architecture-intent://{codebase_id}/verification"
    return [
        {"type": "architecture_diagram_code_alignment", "artifact_ref": f"{base}/diagram_code_alignment.jsonl"},
        {"type": "architecture_undocumented_code_facts", "artifact_ref": f"{base}/undocumented_code_facts.jsonl"},
        {"type": "architecture_diff", "artifact_ref": f"{base}/architecture_diff.json"},
        {"type": "architecture_verification_summary", "artifact_ref": f"{base}/verification_summary.json"},
    ]


def architecture_intent_report_dir(workspace: Path, codebase_id: str) -> Path:
    return architecture_intent_dir(workspace, codebase_id) / "report"


def architecture_intent_report_json_path(workspace: Path, codebase_id: str) -> Path:
    return architecture_intent_report_dir(workspace, codebase_id) / "architecture_intent_report.json"


def architecture_intent_report_html_path(workspace: Path, codebase_id: str) -> Path:
    return architecture_intent_report_dir(workspace, codebase_id) / "architecture_intent_report.html"


def architecture_intent_diff_mermaid_path(workspace: Path, codebase_id: str) -> Path:
    return architecture_intent_report_dir(workspace, codebase_id) / "architecture_intent_diff.mmd"


def architecture_intent_context_dir(workspace: Path, codebase_id: str) -> Path:
    return architecture_intent_dir(workspace, codebase_id) / "context"


def architecture_context_pack_v4_json_path(workspace: Path, codebase_id: str) -> Path:
    return architecture_intent_context_dir(workspace, codebase_id) / "architecture_context_pack_v4.json"


def architecture_context_pack_v4_markdown_path(workspace: Path, codebase_id: str) -> Path:
    return architecture_intent_context_dir(workspace, codebase_id) / "architecture_context_pack_v4.md"


def architecture_intent_governance_dir(workspace: Path, codebase_id: str) -> Path:
    return architecture_intent_dir(workspace, codebase_id) / "governance"


def architecture_intent_confirmed_facts_path(workspace: Path, codebase_id: str) -> Path:
    return architecture_intent_governance_dir(workspace, codebase_id) / "confirmed_facts.jsonl"


def architecture_intent_governance_events_path(workspace: Path, codebase_id: str) -> Path:
    return architecture_intent_governance_dir(workspace, codebase_id) / "governance_events.jsonl"


def architecture_intent_governance_summary_path(workspace: Path, codebase_id: str) -> Path:
    return architecture_intent_governance_dir(workspace, codebase_id) / "governance_summary.json"


def architecture_intent_report_artifact_refs(codebase_id: str) -> list[dict[str, str]]:
    base = f"architecture-intent://{codebase_id}/report"
    return [
        {"type": "architecture_intent_report_json", "artifact_ref": f"{base}/architecture_intent_report.json"},
        {"type": "architecture_intent_report_html", "artifact_ref": f"{base}/architecture_intent_report.html"},
        {"type": "architecture_intent_diff_mermaid", "artifact_ref": f"{base}/architecture_intent_diff.mmd"},
    ]


def architecture_context_pack_v4_artifact_refs(codebase_id: str) -> list[dict[str, str]]:
    base = f"architecture-intent://{codebase_id}/context"
    return [
        {"type": "architecture_context_pack_v4_json", "artifact_ref": f"{base}/architecture_context_pack_v4.json"},
        {"type": "architecture_context_pack_v4_markdown", "artifact_ref": f"{base}/architecture_context_pack_v4.md"},
    ]


def architecture_intent_governance_artifact_refs(codebase_id: str) -> list[dict[str, str]]:
    base = f"architecture-intent://{codebase_id}/governance"
    return [
        {"type": "architecture_confirmed_facts", "artifact_ref": f"{base}/confirmed_facts.jsonl"},
        {"type": "architecture_governance_events", "artifact_ref": f"{base}/governance_events.jsonl"},
        {"type": "architecture_governance_summary", "artifact_ref": f"{base}/governance_summary.json"},
    ]

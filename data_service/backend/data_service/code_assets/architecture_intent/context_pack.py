"""Architecture intent context pack v4 builder."""

from __future__ import annotations

import html
import hashlib
from pathlib import Path
from typing import Any

from data_service.mcp_common import now, read_json, write_json

from .diagram_verification import read_diagram_code_verification
from .governance import read_architecture_governance
from .intent_inference import read_intent_inference
from .paths import (
    architecture_context_pack_v4_artifact_refs,
    architecture_context_pack_v4_json_path,
    architecture_context_pack_v4_markdown_path,
)
from .source_model import SCHEMA_VERSION, redact_public_text


def build_architecture_context_pack_v4(
    *,
    workspace: Path,
    workspace_id: str,
    codebase_id: str,
    snapshot_id: str,
    mode: str = "architecture_review",
    max_items: int = 40,
) -> dict[str, Any]:
    created_at = now()
    intent = read_intent_inference(workspace=workspace, codebase_id=codebase_id)
    verification = read_diagram_code_verification(workspace=workspace, codebase_id=codebase_id)
    governance = read_architecture_governance(workspace=workspace, codebase_id=codebase_id)
    candidates = list(intent.get("intent_candidates") or [])[:max_items]
    alignments = list(verification.get("alignments") or [])[:max_items]
    recommendations = _recommendations(candidates, alignments)
    pack = {
        "schema_version": SCHEMA_VERSION,
        "workspace_id": workspace_id,
        "codebase_id": codebase_id,
        "snapshot_id": snapshot_id,
        "pack_id": _stable_id("archctxv4", snapshot_id, mode, len(candidates), len(alignments)),
        "mode": mode,
        "summary": {
            "intent_candidate_count": intent.get("summary", {}).get("intent_candidate_count", 0),
            "verification_count": verification.get("summary", {}).get("verification_count", 0),
            "confirmed_fact_count": governance.get("summary", {}).get("confirmed_fact_count", 0),
            "accepted_count": verification.get("summary", {}).get("status_counts", {}).get("accepted", 0),
            "missing_code_evidence_count": verification.get("summary", {}).get("status_counts", {}).get("missing_code_evidence", 0),
            "undocumented_code_fact_count": verification.get("summary", {}).get("undocumented_code_fact_count", 0),
        },
        "intent_candidates": candidates,
        "diagram_code_alignment": alignments,
        "confirmed_facts": list(governance.get("confirmed_facts") or []),
        "recommendations": recommendations,
        "source_phase_refs": [91, 92, 93, 94, 95, 96],
        "artifact_refs": architecture_context_pack_v4_artifact_refs(codebase_id),
        "created_at": created_at,
    }
    markdown = _render_markdown(pack)
    write_json(architecture_context_pack_v4_json_path(workspace, codebase_id), pack)
    path = architecture_context_pack_v4_markdown_path(workspace, codebase_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(markdown, encoding="utf-8")
    return {"context_pack": pack, "markdown": markdown, "artifact_refs": architecture_context_pack_v4_artifact_refs(codebase_id)}


def read_architecture_context_pack_v4(*, workspace: Path, codebase_id: str) -> dict[str, Any]:
    pack = read_json(architecture_context_pack_v4_json_path(workspace, codebase_id), {})
    markdown_path = architecture_context_pack_v4_markdown_path(workspace, codebase_id)
    return {
        "schema_version": pack.get("schema_version", SCHEMA_VERSION),
        "workspace_id": pack.get("workspace_id"),
        "codebase_id": codebase_id,
        "snapshot_id": pack.get("snapshot_id"),
        "context_pack": pack,
        "markdown": markdown_path.read_text(encoding="utf-8") if markdown_path.exists() else "",
        "artifact_refs": architecture_context_pack_v4_artifact_refs(codebase_id),
    }


def _recommendations(candidates: list[dict[str, Any]], alignments: list[dict[str, Any]]) -> list[dict[str, Any]]:
    recommendations: list[dict[str, Any]] = []
    missing = [row for row in alignments if row.get("match_status") in {"missing_code_evidence", "weak_match", "conflict", "stale"}]
    if missing:
        recommendations.append(
            {
                "recommendation_id": _stable_id("archrec", "review_missing", len(missing)),
                "text": "Review missing, weak, conflict, and stale diagram-to-code verification items before treating the target architecture as implemented.",
                "evidence_refs": [row.get("verification_id") for row in missing[:12] if row.get("verification_id")],
                "needs_review": [],
            }
        )
    for candidate in candidates[:8]:
        recommendations.append(
            {
                "recommendation_id": _stable_id("archrec", candidate.get("intent_id"), candidate.get("status")),
                "text": f"Inspect {candidate.get('intent_type')} intent candidate with status {candidate.get('status')}.",
                "evidence_refs": list(candidate.get("evidence_bundle_refs") or [])[:8],
                "needs_review": list(candidate.get("needs_review") or []),
            }
        )
    return [item for item in recommendations if item.get("evidence_refs") or item.get("needs_review")]


def _render_markdown(pack: dict[str, Any]) -> str:
    summary = pack.get("summary", {})
    lines = [
        "# Architecture Context Pack v4",
        "",
        f"- mode: `{pack.get('mode')}`",
        f"- codebase_id: `{pack.get('codebase_id')}`",
        f"- snapshot_id: `{pack.get('snapshot_id')}`",
        f"- intent candidates: {summary.get('intent_candidate_count', 0)}",
        f"- verification items: {summary.get('verification_count', 0)}",
        f"- accepted verifications: {summary.get('accepted_count', 0)}",
        f"- missing code evidence: {summary.get('missing_code_evidence_count', 0)}",
        f"- undocumented code facts: {summary.get('undocumented_code_fact_count', 0)}",
        "",
        "## Recommended Next Actions",
    ]
    for rec in pack.get("recommendations", [])[:20]:
        lines.append(f"- {redact_public_text(str(rec.get('text') or ''))}")
    return "\n".join(lines) + "\n"


def _stable_id(prefix: str, *parts: Any) -> str:
    raw = "\x1f".join(str(part) for part in parts)
    return f"{prefix}_{hashlib.sha256(raw.encode('utf-8')).hexdigest()[:16]}"

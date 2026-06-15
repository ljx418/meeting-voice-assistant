"""Human-readable architecture intent report builder."""

from __future__ import annotations

import html
import hashlib
from pathlib import Path
from typing import Any

from data_service.mcp_common import now, read_json, write_json

from .context_pack import read_architecture_context_pack_v4
from .diagram_verification import read_diagram_code_verification
from .governance import read_architecture_governance
from .intent_inference import read_intent_inference
from .paths import architecture_intent_diff_mermaid_path, architecture_intent_report_artifact_refs, architecture_intent_report_html_path, architecture_intent_report_json_path
from .source_model import SCHEMA_VERSION, redact_public_text


REPORT_SECTIONS = [
    "Target Architecture from Documents",
    "Current Architecture from Code Facts",
    "Inferred Intent Candidates",
    "Human Confirmed Architecture",
    "Diagram-to-Code Verification Board",
    "Diff / Drift / Missing Evidence",
    "Review Queue",
    "Recommended Next Actions",
]


def build_architecture_intent_report(*, workspace: Path, workspace_id: str, codebase_id: str, snapshot_id: str) -> dict[str, Any]:
    created_at = now()
    intent = read_intent_inference(workspace=workspace, codebase_id=codebase_id)
    verification = read_diagram_code_verification(workspace=workspace, codebase_id=codebase_id)
    governance = read_architecture_governance(workspace=workspace, codebase_id=codebase_id)
    context = read_architecture_context_pack_v4(workspace=workspace, codebase_id=codebase_id)
    nodes = _report_nodes(verification, intent, governance)
    report = {
        "schema_version": SCHEMA_VERSION,
        "workspace_id": workspace_id,
        "codebase_id": codebase_id,
        "snapshot_id": snapshot_id,
        "report_id": _stable_id("archreport", snapshot_id, verification.get("summary", {}).get("verification_count")),
        "sections": REPORT_SECTIONS,
        "summary": {
            "intent_candidate_count": intent.get("summary", {}).get("intent_candidate_count", 0),
            "verification_count": verification.get("summary", {}).get("verification_count", 0),
            "status_counts": verification.get("summary", {}).get("status_counts", {}),
            "undocumented_code_fact_count": verification.get("summary", {}).get("undocumented_code_fact_count", 0),
            "confirmed_fact_count": governance.get("summary", {}).get("confirmed_fact_count", 0),
        },
        "nodes": nodes,
        "verification_samples": list(verification.get("alignments") or [])[:30],
        "intent_samples": list(intent.get("intent_candidates") or [])[:20],
        "confirmed_facts": list(governance.get("confirmed_facts") or []),
        "context_pack_ref": context.get("context_pack", {}).get("pack_id"),
        "artifact_refs": architecture_intent_report_artifact_refs(codebase_id),
        "created_at": created_at,
    }
    html_text = _render_html(report, context.get("context_pack", {}))
    mermaid = _render_mermaid(report)
    write_json(architecture_intent_report_json_path(workspace, codebase_id), report)
    html_path = architecture_intent_report_html_path(workspace, codebase_id)
    html_path.parent.mkdir(parents=True, exist_ok=True)
    html_path.write_text(html_text, encoding="utf-8")
    mermaid_path = architecture_intent_diff_mermaid_path(workspace, codebase_id)
    mermaid_path.parent.mkdir(parents=True, exist_ok=True)
    mermaid_path.write_text(mermaid, encoding="utf-8")
    return {"report": report, "html": html_text, "mermaid": mermaid, "artifact_refs": architecture_intent_report_artifact_refs(codebase_id)}


def read_architecture_intent_report(*, workspace: Path, codebase_id: str) -> dict[str, Any]:
    report = read_json(architecture_intent_report_json_path(workspace, codebase_id), {})
    html_path = architecture_intent_report_html_path(workspace, codebase_id)
    mermaid_path = architecture_intent_diff_mermaid_path(workspace, codebase_id)
    return {
        "schema_version": report.get("schema_version", SCHEMA_VERSION),
        "workspace_id": report.get("workspace_id"),
        "codebase_id": codebase_id,
        "snapshot_id": report.get("snapshot_id"),
        "report": report,
        "html": html_path.read_text(encoding="utf-8") if html_path.exists() else "",
        "mermaid": mermaid_path.read_text(encoding="utf-8") if mermaid_path.exists() else "",
        "artifact_refs": architecture_intent_report_artifact_refs(codebase_id),
    }


def _report_nodes(verification: dict[str, Any], intent: dict[str, Any], governance: dict[str, Any]) -> list[dict[str, Any]]:
    nodes: list[dict[str, Any]] = []
    for row in list(verification.get("alignments") or [])[:60]:
        nodes.append({"node_id": row.get("verification_id"), "node_type": "verification", "label": row.get("claim_label"), "status": row.get("match_status")})
    for row in list(intent.get("intent_candidates") or [])[:30]:
        nodes.append({"node_id": row.get("intent_id"), "node_type": "intent", "label": row.get("label"), "status": row.get("status")})
    for row in list(governance.get("confirmed_facts") or []):
        nodes.append({"node_id": row.get("confirmation_id"), "node_type": "confirmed", "label": row.get("target_id"), "status": row.get("status")})
    return [node for node in nodes if node.get("node_id")]


def _render_html(report: dict[str, Any], context_pack: dict[str, Any]) -> str:
    summary = report.get("summary", {})
    sections = "\n".join(f"<section><h2>{_h(title)}</h2>{_section_body(title, report, context_pack)}</section>" for title in REPORT_SECTIONS)
    return f"""<!doctype html>
<html lang=\"zh-CN\">
<head>
  <meta charset=\"utf-8\" />
  <title>Architecture Intent Report</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; margin: 32px; color: #1f2937; }}
    h1 {{ font-size: 28px; }}
    h2 {{ margin-top: 28px; border-bottom: 1px solid #d1d5db; padding-bottom: 6px; }}
    .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 12px; }}
    .metric {{ border: 1px solid #d1d5db; border-radius: 8px; padding: 12px; background: #f9fafb; }}
    table {{ border-collapse: collapse; width: 100%; font-size: 13px; }}
    th, td {{ border: 1px solid #d1d5db; padding: 6px 8px; text-align: left; vertical-align: top; }}
    code {{ background: #f3f4f6; padding: 1px 4px; border-radius: 4px; }}
  </style>
</head>
<body>
  <h1>Architecture Intent Report</h1>
  <p>codebase=<code>{_h(report.get('codebase_id'))}</code> snapshot=<code>{_h(report.get('snapshot_id'))}</code></p>
  <div class=\"grid\">
    <div class=\"metric\"><strong>Intent</strong><br>{_h(summary.get('intent_candidate_count', 0))}</div>
    <div class=\"metric\"><strong>Verification</strong><br>{_h(summary.get('verification_count', 0))}</div>
    <div class=\"metric\"><strong>Undocumented</strong><br>{_h(summary.get('undocumented_code_fact_count', 0))}</div>
    <div class=\"metric\"><strong>Confirmed</strong><br>{_h(summary.get('confirmed_fact_count', 0))}</div>
  </div>
  {sections}
</body>
</html>
"""


def _section_body(title: str, report: dict[str, Any], context_pack: dict[str, Any]) -> str:
    if title == "Diagram-to-Code Verification Board":
        rows = "".join(
            f"<tr><td>{_h(row.get('match_status'))}</td><td>{_h(row.get('claim_type'))}</td><td>{_h(row.get('claim_label'))}</td><td>{_h(row.get('matched_code_label'))}</td></tr>"
            for row in report.get("verification_samples", [])[:20]
        )
        return f"<table><tr><th>Status</th><th>Type</th><th>Document Claim</th><th>Code Evidence</th></tr>{rows}</table>"
    if title == "Inferred Intent Candidates":
        items = "".join(f"<li>{_h(row.get('intent_type'))}: {_h(row.get('summary'))}</li>" for row in report.get("intent_samples", [])[:12])
        return f"<ul>{items}</ul>"
    if title == "Human Confirmed Architecture":
        facts = report.get("confirmed_facts", [])
        return "<p>No human-confirmed architecture facts yet.</p>" if not facts else "<ul>" + "".join(f"<li>{_h(fact.get('target_type'))}: {_h(fact.get('target_id'))}</li>" for fact in facts) + "</ul>"
    if title == "Recommended Next Actions":
        recs = context_pack.get("recommendations", [])
        return "<ul>" + "".join(f"<li>{_h(rec.get('text'))}</li>" for rec in recs[:12]) + "</ul>"
    if title == "Diff / Drift / Missing Evidence":
        counts = report.get("summary", {}).get("status_counts", {})
        return "<ul>" + "".join(f"<li>{_h(key)}: {_h(value)}</li>" for key, value in sorted(counts.items())) + "</ul>"
    return "<p>See persisted report JSON for source-linked details. This section is rendered from existing artifacts only.</p>"


def _render_mermaid(report: dict[str, Any]) -> str:
    lines = ["flowchart TD"]
    for node in report.get("nodes", [])[:80]:
        node_id = _mermaid_id(str(node.get("node_id") or "node"))
        label = _mermaid_label(f"{node.get('node_type')}: {node.get('status')}")
        lines.append(f"  {node_id}[\"{label}\"]")
    return "\n".join(lines) + "\n"


def _h(value: Any) -> str:
    return html.escape(redact_public_text(str(value if value is not None else "")))


def _mermaid_id(value: str) -> str:
    return "n_" + hashlib.sha256(value.encode("utf-8")).hexdigest()[:12]


def _mermaid_label(value: str) -> str:
    return html.escape(redact_public_text(value)).replace('"', "'")[:80]


def _stable_id(prefix: str, *parts: Any) -> str:
    raw = "\x1f".join(str(part) for part in parts)
    return f"{prefix}_{hashlib.sha256(raw.encode('utf-8')).hexdigest()[:16]}"

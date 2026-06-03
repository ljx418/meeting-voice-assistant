"""Generate V5-8A planning gate evidence.

This script validates planning-entry evidence only. It does not start V5-8
distributed runtime implementation, create workers, or execute Agent mutations.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from core.workflows.v4_u5e_local_document_workflow import (  # noqa: E402
    V4U5EWorkflowError,
    load_provider_config,
    resolve_allowed_folder,
    scan_markdown_folder,
)


OUTPUT_DIR = REPO_ROOT / "docs" / "design" / "V5.x" / "evidence" / "v5-8a-planning-gate"
UX12_DIR = REPO_ROOT / "docs" / "design" / "V4.x" / "evidence" / "unified-experience" / "UX-12"
V57B_REVIEW = REPO_ROOT / "docs" / "design" / "V5.x" / "evidence" / "v5-7b-external-review" / "v5-8-entry-decision.json"
V58_DOCS = [
    "docs/design/V5.x/v5_8_distributed_multi_agent_runtime_prd.md",
    "docs/design/V5.x/v5_8_target_architecture_delta.md",
    "docs/design/V5.x/v5_8_distributed_state_recovery_model.md",
    "docs/design/V5.x/v5_8_attempt_history_lineage_model.md",
    "docs/design/V5.x/v5_8_tenant_policy_credential_boundary.md",
    "docs/design/V5.x/v5_8_test_matrix.md",
    "docs/design/V5.x/v5_8_no_false_green_guard.md",
    "docs/design/V5.x/v5_8_entry_gate_plan.md",
    "docs/design/V5.x/v5_8_pre_implementation_audit.md",
    "docs/design/V5.x/v5_8_development_and_acceptance_plan.md",
]


def main() -> int:
    evidence = build_evidence()
    write_package(evidence)
    print(json.dumps({"status": evidence["status"], "output_dir": str(OUTPUT_DIR.relative_to(REPO_ROOT))}, ensure_ascii=False, indent=2))
    return 0 if evidence["status"] == "PASS" else 2


def build_evidence() -> dict[str, Any]:
    provider = load_provider_config().redacted()
    ux12_result = _read_json(UX12_DIR / "local-document-workflow-result.json")
    ux12_summary = (UX12_DIR / "result-summary.md").read_text(encoding="utf-8") if (UX12_DIR / "result-summary.md").exists() else ""
    v57b_entry = _read_json(V57B_REVIEW)
    docs_status = _check_docs()
    folder_readiness = _check_folder_readiness()

    quality = ux12_result.get("quality_report") or {}
    real_llm_backed = bool(ux12_result.get("real_llm_backed"))
    provider_invocation_count = int(quality.get("provider_invocation_count") or 0)
    scanner_actual_read_count = int(quality.get("scanner_actual_read_count") or 0)

    missing_evidence: list[str] = []
    if v57b_entry.get("decision") != "GO_FOR_V5_8_PLANNING_AND_PRE_IMPLEMENTATION_AUDIT":
        missing_evidence.append("V5-7B entry decision for V5-8 planning")
    if not docs_status["all_present"]:
        missing_evidence.append("V5-8 planning documents")
    if not provider.get("api_key_configured"):
        missing_evidence.append("current provider API key configured")
    if not real_llm_backed:
        missing_evidence.append("real LLM-backed UX-12 evidence")
    if provider_invocation_count <= 0:
        missing_evidence.append("provider invocation count")
    if scanner_actual_read_count <= 0 or folder_readiness["scanner_actual_read_count"] <= 0:
        missing_evidence.append("actual local Markdown folder read")
    if "status: PASS" not in ux12_summary:
        missing_evidence.append("UX-12 PASS summary")

    status = "PASS" if not missing_evidence else "BLOCKED"
    return {
        "schema_version": "v5_8a.planning_gate_evidence.v1",
        "stage": "V5-8A Distributed Runtime Planning Gate",
        "status": status,
        "decision_scope": "planning_gate_only",
        "v5_8_runtime_implementation_started": False,
        "v5_8_runtime_implementation_allowed": False,
        "real_data_scope": "local_real_markdown_folder_plus_real_llm_provider_evidence",
        "provider": provider,
        "ux12_evidence": {
            "real_llm_backed": real_llm_backed,
            "fallback_demo_only": bool(ux12_result.get("fallback_demo_only")),
            "provider_invocation_count": provider_invocation_count,
            "scanner_actual_read_count": scanner_actual_read_count,
            "provider": (ux12_result.get("provider") or {}).get("provider"),
            "model_ref": (ux12_result.get("provider") or {}).get("model_ref"),
            "provider_config_source": (ux12_result.get("provider") or {}).get("provider_config_source"),
            "evidence_ref": "docs/design/V4.x/evidence/unified-experience/UX-12/result-summary.md",
        },
        "folder_readiness": folder_readiness,
        "v5_7b_entry_decision": {
            "decision": v57b_entry.get("decision"),
            "decision_scope": v57b_entry.get("decision_scope"),
            "runtime_implementation_allowed": v57b_entry.get("v5_8_runtime_implementation_allowed"),
        },
        "docs_status": docs_status,
        "missing_evidence": missing_evidence,
        "false_green_risk": "LOW" if status == "PASS" else "HIGH",
        "claim_risk": "LOW" if status == "PASS" else "HIGH",
        "allowed_next_work": ["v5_8b_planning_or_implementation_prep"] if status == "PASS" else ["fix_v5_8a_evidence"],
        "forbidden_next_work": [
            "claim_distributed_multi_agent_runtime_ready",
            "claim_full_multi_agent_orchestration_ready",
            "claim_agent_executor_ready",
            "start_v5_8_runtime_implementation_without_v5_8b_gate",
        ],
        "redaction_status": "redacted",
    }


def write_package(evidence: dict[str, Any]) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUTPUT_DIR / "real-data-readiness.json").write_text(json.dumps(evidence, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
    (OUTPUT_DIR / "planning-gate-summary.md").write_text(render_summary(evidence), encoding="utf-8")
    (OUTPUT_DIR / "prd-spec-review.md").write_text(render_prd_review(evidence), encoding="utf-8")
    (OUTPUT_DIR / "architecture-risk-review.md").write_text(render_architecture_review(evidence), encoding="utf-8")
    (OUTPUT_DIR / "v5-8b-entry-decision.json").write_text(json.dumps(render_v58b_entry_decision(evidence), ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
    (OUTPUT_DIR / "index.html").write_text(render_html(evidence), encoding="utf-8")


def render_summary(evidence: dict[str, Any]) -> str:
    missing_lines = [f"- {item}" for item in evidence["missing_evidence"]] if evidence["missing_evidence"] else ["- none"]
    return "\n".join(
        [
            "# V5-8A Planning Gate Summary",
            "",
            f"status: {evidence['status']}",
            "stage: V5-8A Distributed Runtime Planning Gate",
            "decision_scope: planning_gate_only",
            "v5_8_runtime_implementation_started: false",
            "v5_8_runtime_implementation_allowed: false",
            f"real_data_scope: {evidence['real_data_scope']}",
            f"provider: {evidence['provider'].get('provider')}",
            f"model_ref: {evidence['provider'].get('model_ref')}",
            f"provider_config_source: {evidence['provider'].get('provider_config_source')}",
            f"api_key_configured: {str(evidence['provider'].get('api_key_configured')).lower()}",
            f"ux12_real_llm_backed: {str(evidence['ux12_evidence']['real_llm_backed']).lower()}",
            f"provider_invocation_count: {evidence['ux12_evidence']['provider_invocation_count']}",
            f"scanner_actual_read_count: {evidence['folder_readiness']['scanner_actual_read_count']}",
            "missing_evidence:",
            *missing_lines,
            "",
            "No False Green: V5-8A does not prove distributed multi-Agent runtime ready or full multi-Agent orchestration ready.",
            "",
        ]
    )


def render_prd_review(evidence: dict[str, Any]) -> str:
    status = "PASS" if evidence["docs_status"]["all_present"] else "BLOCKED"
    return "\n".join(
        [
            "# V5-8A PRD Spec Review",
            "",
            f"status: {status}",
            "",
            "Reviewed PRD intent:",
            "",
            "```text",
            "distributed run coordination",
            "parallel / serial multi-agent runtime",
            "distributed state recovery",
            "attempt history retention",
            "artifact lineage at scale",
            "tenant / policy / credential boundary",
            "observability and audit export for distributed runs",
            "```",
            "",
            "Spec drift evaluation: LOW if V5-8 remains planning-only until V5-8B gate passes.",
            "False green evaluation: MEDIUM because V5-8 names distributed runtime but implementation has not started.",
            "",
        ]
    )


def render_architecture_review(evidence: dict[str, Any]) -> str:
    status = "PASS" if evidence["status"] == "PASS" else "BLOCKED"
    return "\n".join(
        [
            "# V5-8A Architecture Risk Review",
            "",
            f"status: {status}",
            "",
            "Required before V5-8B:",
            "",
            "```text",
            "DistributedRunCoordinator must validate tenant scope before worker assignment.",
            "AgentWorkerRegistry must not grant source=agent durable mutation.",
            "DistributedStateStore must preserve attempts and artifact producer attempt refs.",
            "Provider calls must pass V5-2 credential boundary.",
            "Distributed audit export must include worker/action/recovery evidence.",
            "```",
            "",
            "Stop if any of these boundaries require broadening V5-7B controlled action policy.",
            "",
        ]
    )


def render_v58b_entry_decision(evidence: dict[str, Any]) -> dict[str, Any]:
    go = evidence["status"] == "PASS"
    return {
        "schema_version": "v5_8b.entry_decision.v1",
        "decision": "GO_FOR_V5_8B_PLANNING_OR_IMPLEMENTATION_PREP" if go else "BLOCKED_BY_V5_8A_EVIDENCE",
        "decision_scope": "v5_8b_minimal_coordination_slice_only" if go else "blocked",
        "v5_8b_runtime_implementation_may_start": go,
        "v5_8_complete_runtime_may_be_claimed": False,
        "required_before_v5_8b": [] if go else evidence["missing_evidence"],
        "forbidden_claims": [
            "distributed multi-Agent runtime ready",
            "full multi-Agent orchestration ready",
            "Agent executor ready",
            "production controlled executor ready",
            "production-ready external app support",
        ],
    }


def render_html(evidence: dict[str, Any]) -> str:
    badge = "PASS" if evidence["status"] == "PASS" else "BLOCKED"
    missing = "".join(f"<li>{item}</li>" for item in evidence["missing_evidence"]) or "<li>none</li>"
    return f"""<!doctype html>
<html lang=\"zh-CN\">
  <head>
    <meta charset=\"utf-8\" />
    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
    <title>V5-8A Planning Gate</title>
    <style>
      body {{ margin: 0; background: #f7f8fb; color: #111827; font-family: Inter, system-ui, -apple-system, BlinkMacSystemFont, \"Segoe UI\", \"PingFang SC\", \"Microsoft YaHei\", sans-serif; }}
      header {{ padding: 32px 40px; background: #fff; border-bottom: 1px solid #d8dee9; }}
      main {{ max-width: 1120px; margin: 0 auto; padding: 28px; display: grid; gap: 16px; }}
      section {{ background: #fff; border: 1px solid #d8dee9; border-radius: 10px; padding: 18px; }}
      .badge {{ display: inline-block; padding: 4px 10px; border-radius: 999px; font-weight: 700; color: {"#0f7a3a" if evidence["status"] == "PASS" else "#b42318"}; background: {"#e8f7ee" if evidence["status"] == "PASS" else "#fff0ed"}; }}
      table {{ width: 100%; border-collapse: collapse; }}
      td, th {{ border-bottom: 1px solid #d8dee9; padding: 10px; text-align: left; }}
      pre {{ background: #172033; color: #f8fafc; padding: 14px; border-radius: 8px; overflow: auto; }}
    </style>
  </head>
  <body>
    <header>
      <h1>V5-8A Distributed Runtime Planning Gate</h1>
      <p><span class=\"badge\">{badge}</span> planning gate only; runtime implementation is not started.</p>
    </header>
    <main>
      <section>
        <h2>真实数据 readiness</h2>
        <table>
          <tr><th>provider</th><td>{evidence["provider"].get("provider")}</td></tr>
          <tr><th>model_ref</th><td>{evidence["provider"].get("model_ref")}</td></tr>
          <tr><th>provider_config_source</th><td>{evidence["provider"].get("provider_config_source")}</td></tr>
          <tr><th>api_key_configured</th><td>{evidence["provider"].get("api_key_configured")}</td></tr>
          <tr><th>scanner_actual_read_count</th><td>{evidence["folder_readiness"]["scanner_actual_read_count"]}</td></tr>
          <tr><th>provider_invocation_count</th><td>{evidence["ux12_evidence"]["provider_invocation_count"]}</td></tr>
        </table>
      </section>
      <section>
        <h2>Missing evidence</h2>
        <ul>{missing}</ul>
      </section>
      <section>
        <h2>仍然禁止</h2>
        <pre>distributed multi-Agent runtime ready
full multi-Agent orchestration ready
Agent executor ready
production controlled executor ready
production-ready external app support
V5-8 runtime implementation without V5-8B gate</pre>
      </section>
    </main>
  </body>
</html>
"""


def _check_docs() -> dict[str, Any]:
    missing = [path for path in V58_DOCS if not (REPO_ROOT / path).exists()]
    return {"all_present": not missing, "required_docs": V58_DOCS, "missing_docs": missing}


def _check_folder_readiness() -> dict[str, Any]:
    try:
        root, fixture_source = resolve_allowed_folder("tests/fixtures/desktop/技术分享")
        scan = scan_markdown_folder(root)
        return {
            "status": "PASS",
            "folder_path": "tests/fixtures/desktop/技术分享",
            "fixture_source": fixture_source,
            "scanner_actual_read_count": scan["scanner_actual_read_count"],
            "markdown_file_count": scan["markdown_file_count"],
            "unsupported_file_count": scan["unsupported_file_count"],
            "empty_folders": scan["empty_folders"],
            "redaction_status": "redacted",
        }
    except V4U5EWorkflowError as exc:
        return {
            "status": "BLOCKED",
            "reason": exc.code,
            "scanner_actual_read_count": 0,
            "redaction_status": "redacted",
        }


def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    raise SystemExit(main())

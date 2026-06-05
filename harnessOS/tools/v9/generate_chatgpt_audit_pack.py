from __future__ import annotations

from pathlib import Path

from tools.v9.common import V9_ROOT


OUT_PATH = V9_ROOT / "v9_chatgpt_external_audit_single_file_pack.md"
FILES = [
    "00_README.md",
    "v9_target_prd.md",
    "v9_target_architecture.md",
    "v9_current_gap_analysis.md",
    "v9_front_stage_development_readiness_audit.md",
    "v9_development_and_acceptance_plan.md",
    "v9_acceptance_gate_matrix.md",
    "v9_no_false_green_claim_guard.md",
    "v9_contract_schema_bundle.md",
    "v9_human_authorization_ref_contract.md",
    "v9_api_and_service_boundary_spec.md",
    "v9_evidence_package_schema_and_validator_spec.md",
    "v9_test_fixture_and_ci_matrix.md",
    "v9_high_risk_human_decision_protocol.md",
    "v9_security_threat_model_and_abuse_cases.md",
    "v9_operational_runbook_and_incident_response.md",
    "v9_1_agent_executor_contract_package.md",
    "v9_1_agent_executor_safety_gate_implementation_plan.md",
    "v9_2_controlled_executor_engineering_design.md",
    "v9_3_orchestration_coordinator_engineering_design.md",
    "v9_4_coding_workflow_runtime_engineering_design.md",
    "v9_5_terminal_sandbox_engineering_design.md",
    "v9_6_workflow_studio_engineering_design.md",
    "v9_7_production_governance_engineering_design.md",
    "v9_8_final_acceptance_validator_engineering_design.md",
    "v9_document_audit_report.md",
    "decisions/v9_1_high_risk_human_decision.json",
    "decisions/v9_2_high_risk_human_decision.json",
    "v9_2_pre_implementation_development_and_acceptance_plan.md",
    "v9_2_pre_implementation_audit_closure.md",
    "reports/v9_1_contract_validation_report.json",
    "reports/v9_1_negative_test_results.json",
    "reports/v9_1_no_false_green_scan.json",
    "reports/v9_1_redaction_scan.json",
    "evidence/v9-1-readiness/result-summary.md",
    "evidence/v9-1-readiness/readiness-dashboard-data.json",
    "evidence/v9-1-safety-gate-implementation/result-summary.md",
    "evidence/v9-1-safety-gate-implementation/acceptance-data.json",
    "v9_1_internal_independent_audit_closure.md",
    "evidence/v9-1-internal-independent-audit/result-summary.md",
    "evidence/v9-1-internal-independent-audit/internal-audit-data.json",
    "evidence/v9-2-controlled-executor-pre-implementation/result-summary.md",
    "evidence/v9-2-controlled-executor-pre-implementation/pre-implementation-data.json",
    "v9_2_runtime_acceptance_closure.md",
    "evidence/v9-2-controlled-executor-runtime/result-summary.md",
    "evidence/v9-2-controlled-executor-runtime/acceptance-data.json",
    "../../../core/policies/v9_agent_executor_safety.py",
    "../../../core/policies/v9_controlled_executor_runtime.py",
    "../../../tests/test_v9_2_controlled_executor_runtime.py",
    "../../../tests/test_v9_2_runtime_evidence.py",
]


def main() -> int:
    lines = [
        "# V9 ChatGPT External Audit Single File Pack",
        "",
        "文档状态：external audit attachment / V9-1 safety gate implementation evidence / not runtime executor evidence。",
        "",
        "## Boundary",
        "",
        "```text",
        "proceed_to_v9_front_stage_readiness_audit=true",
        "proceed_to_v9_1_external_implementation_readiness_audit=true",
        "proceed_to_v9_1_implementation_planning=true",
        "proceed_to_v9_1_limited_safety_gate_implementation=true",
        "proceed_to_v9_2_limited_controlled_runtime_slice=true",
        "proceed_to_v9_1_runtime_implementation=false",
        "proceed_to_v9_2_runtime_executor_route=false",
        "proceed_to_v9_2_runtime_worker=false",
        "proceed_to_v9_3_runtime_implementation=false",
        "proceed_to_v9_4_runtime_implementation=false",
        "proceed_to_v9_full_runtime_development=false",
        "runtime_executor_route_created=false",
        "runtime_worker_created=false",
        "source_agent_durable_mutation_allowed=false",
        "```",
        "",
        "## Included Files",
    ]
    for relative in FILES:
        path = (V9_ROOT / relative).resolve()
        lines.append(f"- `docs/design/V9.x/{relative}` exists={path.exists()} size={path.stat().st_size if path.exists() else 0}")
    lines.extend(["", "## Attachments", ""])
    for relative in FILES:
        path = (V9_ROOT / relative).resolve()
        if not path.exists():
            continue
        suffix = path.suffix.lstrip(".") or "text"
        if suffix == "json":
            suffix = "json"
        elif suffix == "md":
            suffix = "markdown"
        else:
            suffix = "text"
        lines.extend(
            [
                f"### `docs/design/V9.x/{relative}`",
                f"```{suffix}",
                path.read_text(encoding="utf-8", errors="ignore"),
                "```",
                "",
            ]
        )
    OUT_PATH.write_text("\n".join(lines), encoding="utf-8")
    print(OUT_PATH)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

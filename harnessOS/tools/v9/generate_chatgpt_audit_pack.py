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
    "v9_user_scenario_acceptance_gate.md",
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
    "v9_3_development_and_acceptance_plan.md",
    "v9_3_orchestration_coordinator_engineering_design.md",
    "v9_4_development_and_acceptance_plan.md",
    "v9_4_coding_workflow_runtime_engineering_design.md",
    "v9_4_pre_implementation_readiness_closure.md",
    "v9_5_development_and_acceptance_plan.md",
    "v9_5_terminal_sandbox_engineering_design.md",
    "v9_6_development_and_acceptance_plan.md",
    "v9_6_workflow_studio_engineering_design.md",
    "v9_7_development_and_acceptance_plan.md",
    "v9_7_production_governance_engineering_design.md",
    "v9_8_development_and_acceptance_plan.md",
    "v9_8_final_acceptance_validator_engineering_design.md",
    "v9_document_audit_report.md",
    "decisions/v9_1_high_risk_human_decision.json",
    "decisions/v9_2_high_risk_human_decision.json",
    "decisions/v9_5_high_risk_human_decision.json",
    "v9_2_pre_implementation_development_and_acceptance_plan.md",
    "v9_2_pre_implementation_audit_closure.md",
    "reports/v9_1_contract_validation_report.json",
    "reports/v9_1_negative_test_results.json",
    "reports/v9_1_no_false_green_scan.json",
    "reports/v9_1_redaction_scan.json",
    "reports/v9_test_run_summary.json",
    "decisions/v9_4_high_risk_human_decision.json",
    "decisions/v9_7_high_risk_human_decision.json",
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
    "v9_3_runtime_acceptance_closure.md",
    "evidence/v9-3-orchestration-runtime/result-summary.md",
    "evidence/v9-3-orchestration-runtime/acceptance-data.json",
    "evidence/v9-3-orchestration-runtime/user-scenarios.json",
    "evidence/v9-4-readiness-closure/result-summary.md",
    "evidence/v9-4-readiness-closure/pre-implementation-data.json",
    "v9_4_runtime_acceptance_closure.md",
    "evidence/v9-4-coding-workflow-runtime/result-summary.md",
    "evidence/v9-4-coding-workflow-runtime/acceptance-data.json",
    "evidence/v9-4-coding-workflow-runtime/git-operation-deny-report.json",
    "evidence/v9-5-terminal-worker/result-summary.md",
    "evidence/v9-5-terminal-worker/acceptance-data.json",
    "evidence/v9-5-terminal-worker/command-decisions.json",
    "evidence/v9-5-terminal-worker/denial-evidence.json",
    "evidence/v9-6-workflow-studio/result-summary.md",
    "evidence/v9-6-workflow-studio/acceptance-data.json",
    "evidence/v9-6-workflow-studio/studio_network_log.json",
    "evidence/v9-6-workflow-studio/studio_hidden_form_scan.json",
    "evidence/v9-6-workflow-studio/studio_ui_copy_claim_scan.json",
    "evidence/v9-6-workflow-studio/manual_confirmation_evidence.json",
    "evidence/v9-6-workflow-studio/workflow_diff_proposal.json",
    "evidence/v9-7-production-governance/result-summary.md",
    "evidence/v9-7-production-governance/acceptance-data.json",
    "evidence/v9-7-production-governance/governance-fixture.json",
    "evidence/v9-7-production-governance/tenant-isolation-decisions.json",
    "evidence/v9-7-production-governance/credential-lease-decisions.json",
    "evidence/v9-7-production-governance/service-account-binding-decisions.json",
    "evidence/v9-7-production-governance/audit-export-package.json",
    "evidence/v9-7-production-governance/incident-timeline.json",
    "evidence/v9-7-production-governance/evidence-hardening-report.json",
    "evidence/v9-7-production-governance/terminal-automation-policy.json",
    "evidence/v9-7-production-governance/browser-automation-policy.json",
    "evidence/v9-3-orchestration-runtime/storyboard-provider-evidence.json",
    "evidence/v9-8-final-acceptance/v9-final-acceptance-data.json",
    "evidence/v9-8-final-acceptance/v9-final-result-summary.md",
    "../../../core/policies/v9_agent_executor_safety.py",
    "../../../core/policies/v9_controlled_executor_runtime.py",
    "../../../core/workflows/v9_3_multi_agent_orchestration_runtime.py",
    "../../../core/workflows/v9_4_coding_workflow_pilot.py",
    "../../../core/terminal_workers/v9_5_governed_terminal_worker.py",
    "../../../core/product_console/v9_6_workflow_studio.py",
    "../../../core/governance/v9_7_production_governance.py",
    "../../../tests/test_v9_2_controlled_executor_runtime.py",
    "../../../tests/test_v9_2_runtime_evidence.py",
    "../../../tests/test_v9_3_multi_agent_orchestration_runtime.py",
    "../../../tests/test_v9_4_readiness_closure.py",
    "../../../tests/test_v9_4_coding_workflow_pilot.py",
    "../../../tests/test_v9_5_governed_terminal_worker.py",
    "../../../tests/test_v9_6_workflow_studio.py",
    "../../../tests/test_v9_7_production_governance.py",
    "../../../tests/test_v9_8_final_acceptance.py",
    "../../../tools/v9/generate_v9_5_terminal_worker_evidence.py",
    "../../../tools/v9/generate_v9_6_workflow_studio_evidence.py",
    "../../../tools/v9/generate_v9_7_production_governance_evidence.py",
    "../../../tools/v9/generate_v9_3_provider_storyboard_evidence.py",
    "../../../tools/v9/generate_v9_8_final_acceptance.py",
]


def main() -> int:
    lines = [
        "# V9 ChatGPT External Audit Single File Pack",
        "",
        "文档状态：external audit attachment / V9-7 production governance evidence-aligned / not final V9 acceptance evidence。",
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
        "proceed_to_v9_3_runtime_implementation_complete_for_review=true",
        "proceed_to_v9_4_readiness_closure=true",
        "proceed_to_v9_4_runtime_implementation_complete_for_review=true",
        "proceed_to_v9_5_runtime_implementation_complete_for_review=true",
        "proceed_to_v9_6_runtime_implementation_complete_for_review=true",
        "proceed_to_v9_7_runtime_implementation_complete_for_review=true",
        "proceed_to_v9_8_final_acceptance=false",
        "proceed_to_v9_8_final_acceptance_validator=implemented_blocked",
        "v9_8_blocker=US-V9-08_provider_backed_storyboard_image_evidence",
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

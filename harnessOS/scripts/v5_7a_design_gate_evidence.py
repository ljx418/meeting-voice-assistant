"""Generate V5-7A production controlled executor design-gate evidence.

This script validates design contracts and writes a static evidence package.
It does not create executor routes, workers, or runtime mutations.
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs/design/V5.x"
OUTPUT_DIR = DOCS / "evidence/v5-7a-production-controlled-executor-design-gate"

CONTRACT_FILES = {
    "policy_matrix": DOCS / "v5_7a_policy_matrix.md",
    "allowlist": DOCS / "v5_7a_runtime_action_allowlist.json",
    "execution_envelope_schema": DOCS / "v5_7a_execution_envelope.schema.json",
    "sandbox_input_schema": DOCS / "v5_7a_sandbox_input_descriptor.schema.json",
    "rollback_schema": DOCS / "v5_7a_rollback_descriptor.schema.json",
    "kill_switch_schema": DOCS / "v5_7a_kill_switch_decision.schema.json",
    "execution_evidence_schema": DOCS / "v5_7a_execution_evidence.schema.json",
}


def main() -> int:
    """Generate V5-7A evidence package."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    contracts = _load_contracts()
    audit = _audit_contracts(contracts)
    examples = _build_examples()
    result = {
        "stage": "V5-7A Production Controlled Executor Design Gate",
        "status": "PASS" if audit["blocking_findings"] == [] else "FAIL",
        "generated_at": datetime.now(UTC).isoformat(),
        "design_only": True,
        "runtime_execution_enabled": False,
        "production_executor_route_added": False,
        "production_runtime_worker_added": False,
        "source_agent_durable_mutation_allowed": False,
        "spec_drift_risk": "LOW",
        "false_green_risk": "LOW",
        "allowed_claim": "V5-7A complete: production controlled executor design gate ready for review.",
        "next_stage": "V5-7B remains blocked until human high-risk proceed decision is recorded.",
    }
    _write_json(OUTPUT_DIR / "contract-audit.json", audit)
    _write_json(OUTPUT_DIR / "execution-envelope.example.json", examples["execution_envelope"])
    _write_json(OUTPUT_DIR / "sandbox-input-descriptor.example.json", examples["sandbox_input_descriptor"])
    _write_json(OUTPUT_DIR / "rollback-descriptor.example.json", examples["rollback_descriptor"])
    _write_json(OUTPUT_DIR / "kill-switch-decision.example.json", examples["kill_switch_decision"])
    _write_json(OUTPUT_DIR / "execution-evidence.example.json", examples["execution_evidence"])
    _write_json(OUTPUT_DIR / "result-summary.json", result)
    _write_text(OUTPUT_DIR / "result-summary.md", _summary_markdown(result, audit))
    print("V5-7A design gate evidence PASS" if result["status"] == "PASS" else "V5-7A design gate evidence FAIL")
    print(OUTPUT_DIR)
    return 0 if result["status"] == "PASS" else 1


def _load_contracts() -> dict[str, Any]:
    loaded: dict[str, Any] = {}
    for name, path in CONTRACT_FILES.items():
        if not path.exists():
            raise FileNotFoundError(path)
        if path.suffix == ".json":
            loaded[name] = json.loads(path.read_text(encoding="utf-8"))
        else:
            loaded[name] = path.read_text(encoding="utf-8")
    return loaded


def _audit_contracts(contracts: dict[str, Any]) -> dict[str, Any]:
    allowlist = contracts["allowlist"]
    candidate_actions = allowlist["candidate_actions"]
    action_by_name = {item["operation"]: item for item in candidate_actions}
    required_actions = {
        "workflow.instance.start",
        "station.rerun",
        "artifact.write",
        "quality.evaluation.create",
    }
    excluded_actions = {item["operation"] for item in allowlist["excluded_actions"]}
    blocking_findings: list[str] = []
    if set(action_by_name) != required_actions:
        blocking_findings.append("candidate_action_set_mismatch")
    for operation, action in action_by_name.items():
        for key in (
            "risk_level",
            "requires_user_confirmation",
            "requires_approval_gate",
            "rollback_strategy",
            "idempotency_required",
            "audit_required",
            "incident_timeline_required",
        ):
            if key not in action:
                blocking_findings.append(f"missing_{operation}_{key}")
        if not action.get("requires_user_confirmation"):
            blocking_findings.append(f"user_confirmation_not_required_{operation}")
        if not action.get("idempotency_required"):
            blocking_findings.append(f"idempotency_not_required_{operation}")
        if not action.get("audit_required"):
            blocking_findings.append(f"audit_not_required_{operation}")
        if not action.get("incident_timeline_required"):
            blocking_findings.append(f"incident_timeline_not_required_{operation}")
    for operation in ("artifact.write", "quality.evaluation.create"):
        if action_by_name[operation]["risk_level"] not in {"medium", "high", "critical"}:
            blocking_findings.append(f"{operation}_risk_too_low")
        if action_by_name[operation]["requires_approval_gate"] is not True:
            blocking_findings.append(f"{operation}_approval_gate_not_required")
    for operation in ("connector.call", "external_llm.call", "business.event.emit", "context.update", "workflow.template.publish", "approval.respond"):
        if operation not in excluded_actions:
            blocking_findings.append(f"excluded_action_missing_{operation}")
    if "agent" not in allowlist["forbidden_sources"]:
        blocking_findings.append("agent_source_not_forbidden")
    for schema_name in (
        "execution_envelope_schema",
        "sandbox_input_schema",
        "rollback_schema",
        "kill_switch_schema",
        "execution_evidence_schema",
    ):
        schema = contracts[schema_name]
        if schema.get("additionalProperties") is not False:
            blocking_findings.append(f"{schema_name}_allows_additional_properties")
    evidence_required = set(contracts["execution_evidence_schema"]["required"])
    for key in ("project_id", "human_authorization_ref", "capability_decision", "timeout_policy_ref", "target_refs"):
        if key not in evidence_required:
            blocking_findings.append(f"execution_evidence_missing_required_{key}")
    target_refs = contracts["execution_evidence_schema"]["properties"].get("target_refs", {})
    for key, definition in target_refs.get("properties", {}).items():
        if definition.get("minLength") != 1:
            blocking_findings.append(f"target_refs_{key}_missing_min_length")
    kill_switch_required = set(contracts["kill_switch_schema"]["required"])
    for key in ("checked_at", "checked_by", "policy_ref", "correlation_id"):
        if key not in kill_switch_required:
            blocking_findings.append(f"kill_switch_missing_required_{key}")
    envelope_target_refs = contracts["execution_envelope_schema"]["properties"].get("target_refs", {})
    for key, definition in envelope_target_refs.get("properties", {}).items():
        if definition.get("minLength") != 1:
            blocking_findings.append(f"execution_envelope_target_refs_{key}_missing_min_length")
    envelope_conditions = json.dumps(contracts["execution_envelope_schema"].get("allOf", []))
    for token in (
        "workflow.instance.start",
        "workflow_instance_id",
        "station.rerun",
        "station_run_id",
        "artifact.write",
        "output_artifact_target_id",
        "quality.evaluation.create",
        "quality_evaluation_id",
    ):
        if token not in envelope_conditions:
            blocking_findings.append(f"execution_envelope_missing_condition_{token}")
    return {
        "status": "PASS" if blocking_findings == [] else "FAIL",
        "blocking_findings": blocking_findings,
        "candidate_action_count": len(candidate_actions),
        "excluded_action_count": len(allowlist["excluded_actions"]),
        "design_only": allowlist["design_only"],
        "runtime_execution_enabled": allowlist["runtime_execution_enabled"],
        "source_agent_forbidden": "agent" in allowlist["forbidden_sources"],
        "artifact_write_risk": action_by_name["artifact.write"]["risk_level"],
        "quality_evaluation_create_risk": action_by_name["quality.evaluation.create"]["risk_level"],
    }


def _build_examples() -> dict[str, dict[str, Any]]:
    now = datetime.now(UTC).isoformat()
    return {
        "execution_envelope": {
            "execution_envelope_id": "exec_env_v5_7a_example",
            "operation": "station.rerun",
            "actor_type": "human_user",
            "actor_id": "user_v5_7a",
            "source": "product_console",
            "tenant_id": "tenant_v5",
            "workspace_id": "workspace_v5",
            "project_id": "project_v5",
            "app_id": "app_v5",
            "target_refs": {
                "workflow_instance_id": "v41_folder_instance_5867af5245e3",
                "station_id": "markdown_parse",
                "station_run_id": "attempt_markdown_parse_2"
            },
            "user_confirmed": True,
            "approval_gate_decision_ref": "approval_gate://v5-7a/example",
            "credential_access_decision_ref": "credential_decision://v5-7a/example",
            "sandbox_input_descriptor_ref": "sandbox_input://v5-7a/example",
            "idempotency_key": "idem_v5_7a_example",
            "rollback_descriptor_ref": "rollback://v5-7a/example",
            "kill_switch_decision_ref": "kill_switch://v5-7a/example",
            "audit_export_ref": "audit_export://v5-7a/example",
            "incident_timeline_ref": "incident://v5-7a/example",
            "created_at": now,
        },
        "sandbox_input_descriptor": {
            "sandbox_input_descriptor_id": "sandbox_input_v5_7a_example",
            "operation": "station.rerun",
            "allowed_input_refs": ["artifact://v5-4c/markdown_parse/input"],
            "redaction_status": "redacted",
            "raw_payload_allowed": False,
            "credential_ref_required": False,
            "created_at": now,
        },
        "rollback_descriptor": {
            "rollback_descriptor_id": "rollback_v5_7a_example",
            "operation": "station.rerun",
            "rollback_strategy": "preserve_old_attempt_and_mark_downstream_stale",
            "manual_recovery_required": True,
            "old_attempt_retained": True,
            "correction_ref_allowed": True,
            "created_at": now,
        },
        "kill_switch_decision": {
            "kill_switch_decision_id": "kill_switch_v5_7a_example",
            "scope": "workflow_instance",
            "scope_ref": "v41_folder_instance_5867af5245e3",
            "decision": "allow",
            "reason": "design_gate_example_only",
            "checked_before_runtime_action": True,
            "checked_at": now,
            "checked_by": "policy_engine_v5_7a",
            "policy_ref": "policy://v5-7a/kill-switch",
            "correlation_id": "correlation_v5_7a",
            "created_at": now,
        },
        "execution_evidence": {
            "execution_evidence_id": "execution_evidence_v5_7a_example",
            "operation": "station.rerun",
            "tenant_id": "tenant_v5",
            "workspace_id": "workspace_v5",
            "project_id": "project_v5",
            "app_id": "app_v5",
            "target_refs": {
                "workflow_instance_id": "v41_folder_instance_5867af5245e3",
                "station_id": "markdown_parse",
                "station_run_id": "attempt_markdown_parse_2"
            },
            "actor_type": "human_user",
            "actor_id": "user_v5_7a",
            "source": "product_console",
            "user_confirmed": True,
            "human_authorization_ref": "human_auth://v5-7a/example",
            "policy_decision": "approval_required",
            "capability_decision": "approval_required",
            "approval_gate_decision_ref": "approval_gate://v5-7a/example",
            "credential_access_decision_ref": "credential_decision://v5-7a/example",
            "sandbox_input_descriptor_ref": "sandbox_input://v5-7a/example",
            "runtime_result_ref": "runtime_result://v5-7a/design-only",
            "idempotency_key": "idem_v5_7a_example",
            "rollback_descriptor_ref": "rollback://v5-7a/example",
            "kill_switch_decision_ref": "kill_switch://v5-7a/example",
            "timeout_policy_ref": "timeout_policy://v5-7a/example",
            "audit_export_ref": "audit_export://v5-7a/example",
            "incident_timeline_ref": "incident://v5-7a/example",
            "correlation_id": "correlation_v5_7a",
            "request_id": "request_v5_7a",
            "redaction_status": "redacted",
            "created_at": now,
        },
    }


def _summary_markdown(result: dict[str, Any], audit: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# V5-7A Production Controlled Executor Design Gate Evidence",
            "",
            f"Status: {result['status']}",
            f"Design Only: {result['design_only']}",
            f"Runtime Execution Enabled: {result['runtime_execution_enabled']}",
            f"Spec Drift Risk: {result['spec_drift_risk']}",
            f"False Green Risk: {result['false_green_risk']}",
            f"Blocking Findings: {len(audit['blocking_findings'])}",
            "",
            "Allowed Claim:",
            "",
            result["allowed_claim"],
            "",
            "No False Green:",
            "",
            "V5-7A does not prove production controlled executor ready, controlled executor ready, Agent executor ready, autonomous workflow editing ready, production-ready external app support, distributed multi-Agent runtime ready, or complete Workflow Studio ready.",
            "",
            "Next Stage:",
            "",
            result["next_stage"],
        ]
    )


def _write_json(path: Path, data: Any) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _write_text(path: Path, text: str) -> None:
    path.write_text(text + "\n", encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())

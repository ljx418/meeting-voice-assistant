from __future__ import annotations

from core.policies.production_controlled_executor_runtime import ProductionControlledExecutorError
from tests.v5_3_observability_support import make_context
from tests.v5_7b_runtime_support import make_request, make_runtime


def test_execution_evidence_contains_required_refs_without_claiming_production_ready() -> None:
    context = make_context()
    runtime = make_runtime()

    result = runtime.execute(context, make_request(context, idempotency_key="evidence-required")).to_dict()
    evidence = result["evidence"]

    assert evidence["tenant_id"] == context.tenant_id
    assert evidence["workspace_id"] == context.workspace_id
    assert evidence["project_id"] == context.project_id
    assert evidence["app_id"] == context.app_id
    assert evidence["human_authorization_ref"].startswith("human-auth://")
    assert evidence["capability_decision"] == "allow_limited_runtime_slice"
    assert evidence["timeout_policy_ref"].startswith("timeout-policy://")
    assert evidence["kill_switch_decision_ref"].startswith("kill-switch://")
    assert evidence["audit_export_ref"].startswith("audit-export://")
    assert result["staging_only"] is True
    assert result["production_ready"] is False


def test_workspace_kill_switch_blocks_before_evidence_is_recorded() -> None:
    context = make_context()
    runtime = make_runtime()
    runtime.disable_workspace(context.workspace_id)

    result = runtime.execute(context, make_request(context, idempotency_key="kill-switch")).to_dict()

    assert result["status"] == "blocked"
    assert result["blocked_reason"] == "workspace_kill_switch_active"
    assert runtime.evidence == []


def test_raw_artifact_content_is_rejected_before_artifact_write() -> None:
    context = make_context()
    runtime = make_runtime()

    result = runtime.execute(
        context,
        make_request(
            context,
            operation="artifact.write",
            target_refs={"workflow_instance_id": "workflow-instance-v5-7b", "artifact_id": "artifact-summary-v1"},
            payload_refs={"raw_artifact_content": "do not allow this raw content"},
            approval_gate_decision_ref="approval-gate://v5-7b/artifact-write",
            idempotency_key="raw-artifact-denied",
        ),
    ).to_dict()

    assert result["status"] == "blocked"
    assert result["blocked_reason"] == "redaction_failed"


def test_result_dto_does_not_leak_sensitive_text() -> None:
    context = make_context()
    runtime = make_runtime()
    result = runtime.execute(context, make_request(context, idempotency_key="redaction-clean")).to_dict()
    dumped = str(result).lower()

    for forbidden in [
        "capability_token",
        "subscription_token",
        "authorization:",
        "bearer ",
        "raw_trace_payload",
        "raw_artifact_content",
        "raw_connector_payload",
        "raw prompt",
        "upstream signed url",
    ]:
        assert forbidden not in dumped


def test_redaction_error_shape_is_stable_and_redacted() -> None:
    error = ProductionControlledExecutorError("V5_7B_TEST", "Denied", reason="secret_detected", resource="payload_refs.secret")

    data = error.to_error()

    assert data == {
        "code": "V5_7B_TEST",
        "message": "Denied",
        "data": {"reason": "secret_detected", "resource": "payload_refs.secret"},
    }

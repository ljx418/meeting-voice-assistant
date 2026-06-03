from __future__ import annotations

from tests.v5_3_observability_support import make_context
from tests.v5_7b_runtime_support import make_human_authorization, make_request, make_runtime


def test_workflow_instance_start_records_evidence_and_incident_timeline_ref() -> None:
    context = make_context()
    runtime = make_runtime()

    result = runtime.execute(context, make_request(context, idempotency_key="start-1")).to_dict()

    assert result["status"] == "applied_limited_runtime_slice"
    assert result["workflow_state"]["status"] == "running"
    assert result["evidence"]["operation"] == "workflow.instance.start"
    assert result["evidence"]["user_confirmed"] is True
    assert result["evidence"]["incident_timeline_ref"].startswith("incident-timeline://")
    assert result["evidence"]["idempotency_key"] == "start-1"


def test_workflow_instance_start_idempotent_duplicate_returns_prior_execution_reference() -> None:
    context = make_context()
    runtime = make_runtime()
    request = make_request(context, idempotency_key="start-idempotent")

    first = runtime.execute(context, request).to_dict()
    second = runtime.execute(context, request).to_dict()

    assert first["status"] == "applied_limited_runtime_slice"
    assert second["status"] == "idempotent_replay"
    assert second["idempotent_replay"] is True
    assert second["runtime_result_ref"] == first["runtime_result_ref"]


def test_station_rerun_retains_old_attempt_creates_new_attempt_and_marks_stale() -> None:
    context = make_context()
    runtime = make_runtime()
    request = make_request(
        context,
        operation="station.rerun",
        target_refs={
            "workflow_instance_id": "workflow-instance-v5-7b",
            "station_id": "markdown_parse",
            "station_run_id": "station-run-v5-7b-1",
        },
        idempotency_key="rerun-1",
    )

    result = runtime.execute(context, request).to_dict()
    attempts = result["workflow_state"]["station_attempts"]["markdown_parse"]

    assert result["status"] == "applied_limited_runtime_slice"
    assert [attempt["status"] for attempt in attempts] == ["failed", "completed"]
    assert attempts[0]["station_run_id"] == "station-run-v5-7b-1"
    assert attempts[1]["attempt_number"] == 2
    assert result["workflow_state"]["downstream_stale"] == ["downstream-of:markdown_parse"]


def test_artifact_write_is_medium_risk_approval_gated_and_appends_version() -> None:
    context = make_context()
    runtime = make_runtime()
    target_refs = {"workflow_instance_id": "workflow-instance-v5-7b", "artifact_id": "artifact-summary-v1"}

    blocked = runtime.execute(
        context,
        make_request(context, operation="artifact.write", target_refs=target_refs, idempotency_key="artifact-no-approval"),
    ).to_dict()
    allowed = runtime.execute(
        context,
        make_request(
            context,
            operation="artifact.write",
            target_refs=target_refs,
            payload_refs={"content_ref": "artifact-content-ref://summary/v2"},
            approval_gate_decision_ref="approval-gate://v5-7b/artifact-write",
            idempotency_key="artifact-approved",
        ),
    ).to_dict()
    allowed_second = runtime.execute(
        context,
        make_request(
            context,
            operation="artifact.write",
            target_refs=target_refs,
            payload_refs={"content_ref": "artifact-content-ref://summary/v3"},
            approval_gate_decision_ref="approval-gate://v5-7b/artifact-write",
            idempotency_key="artifact-approved-2",
        ),
    ).to_dict()

    versions = allowed_second["workflow_state"]["artifact_versions"]["artifact-summary-v1"]
    assert blocked["status"] == "blocked"
    assert blocked["blocked_reason"] == "approval_gate_required"
    assert allowed["status"] == "applied_limited_runtime_slice"
    assert len(versions) == 2
    assert [version["operation"] for version in versions] == ["append_version", "append_version"]
    assert allowed["evidence"]["approval_gate_decision_ref"] == "approval-gate://v5-7b/artifact-write"


def test_quality_evaluation_create_is_medium_risk_approval_gated_and_appends_evaluation() -> None:
    context = make_context()
    runtime = make_runtime()
    target_refs = {"workflow_instance_id": "workflow-instance-v5-7b", "quality_evaluation_id": "quality-eval-v1", "artifact_id": "artifact-summary-v1"}

    blocked = runtime.execute(
        context,
        make_request(context, operation="quality.evaluation.create", target_refs=target_refs, idempotency_key="quality-no-approval"),
    ).to_dict()
    allowed = runtime.execute(
        context,
        make_request(
            context,
            operation="quality.evaluation.create",
            target_refs=target_refs,
            payload_refs={"quality_rule_ref": "quality-rule://summary-coverage", "score_ref": "quality-score-ref://summary-coverage-v1"},
            approval_gate_decision_ref="approval-gate://v5-7b/quality",
            idempotency_key="quality-approved",
        ),
    ).to_dict()

    evaluations = allowed["workflow_state"]["quality_evaluations"]
    assert blocked["blocked_reason"] == "approval_gate_required"
    assert allowed["status"] == "applied_limited_runtime_slice"
    assert len(evaluations) == 1
    assert evaluations[0]["operation"] == "append_evaluation"
    assert evaluations[0]["quality_rule_ref"] == "quality-rule://summary-coverage"


def test_excluded_actions_are_denied() -> None:
    context = make_context()
    runtime = make_runtime()

    for index, operation in enumerate(
        [
            "business.event.emit",
            "context.update",
            "workflow.template.publish",
            "approval.respond",
            "connector.call",
            "external_llm.call",
        ]
    ):
        result = runtime.execute(
            context,
            make_request(
                context,
                operation=operation,
                human_authorization=make_human_authorization(context, operations=(operation,)),
                target_refs={"workflow_instance_id": "workflow-instance-v5-7b"},
                idempotency_key=f"excluded-{index}",
            ),
        ).to_dict()
        assert result["status"] == "blocked"
        assert result["blocked_reason"] == "operation_not_allowed"

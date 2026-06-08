from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from core.workflows.v9_3_multi_agent_orchestration_runtime import (
    V93OrchestrationConfig,
    V93OrchestrationRuntimeError,
    deny_source_agent_direct_mutation,
    run_v9_3_multi_agent_orchestration,
    validate_fan_in_join,
    validate_retry_retains_old_attempt,
)
from tools.v9.generate_v9_3_provider_storyboard_evidence import (
    _blocked_reason_from_shapes,
    _extract_image_payloads,
)


V9_ROOT = Path("docs/design/V9.x")
EVIDENCE_ROOT = V9_ROOT / "evidence" / "v9-3-orchestration-runtime"


def test_v9_3_runtime_binds_one_agent_per_station_and_keeps_boundary() -> None:
    payload = run_v9_3_multi_agent_orchestration(V93OrchestrationConfig(evidence_dir=Path("/tmp/v9-3-test-evidence")))

    acceptance = payload["acceptance"]
    bindings = payload["station_agent_bindings"]

    assert acceptance["status"] == "PASS"
    assert acceptance["evidence_scope"] == "real_runtime_fixture"
    assert acceptance["runtime_backed"] is True
    assert acceptance["runtime_executor_route_created"] is False
    assert acceptance["runtime_worker_created"] is False
    assert acceptance["source_agent_durable_mutation_allowed"] is False
    assert acceptance["agent_executor_ready"] is False
    assert acceptance["controlled_executor_ready"] is False
    assert len({binding["station_id"] for binding in bindings}) == len(bindings)
    assert len({binding["agent_id"] for binding in bindings}) == len(bindings)


def test_v9_3_serial_parallel_fan_in_fan_out_and_attempt_history_are_auditable() -> None:
    payload = run_v9_3_multi_agent_orchestration(V93OrchestrationConfig(evidence_dir=Path("/tmp/v9-3-test-evidence")))

    branch_by_id = {branch["branch_id"]: branch for branch in payload["branch_states"]}
    attempts = payload["attempt_history"]
    fan_out = payload["fan_out_dispatches"][0]
    fan_in = payload["fan_in_join_decisions"][0]

    assert branch_by_id["branch-serial-research"]["downstream_branch_ids"] == ["branch-parallel-implementation", "branch-parallel-review"]
    assert set(fan_out["target_branch_ids"]) == {"branch-parallel-implementation", "branch-parallel-review"}
    assert fan_in["decision"] == "ready_to_synthesize"
    assert len(fan_in["input_artifact_refs"]) == len(fan_in["attribution_refs"]) == 2
    assert branch_by_id["branch-parallel-implementation"]["state"] == "recovered"
    assert validate_retry_retains_old_attempt(attempts)["status"] == "PASS"
    assert any(attempt["status"] == "failed" and attempt["error_ref"] for attempt in attempts)
    assert any(attempt["attempt_number"] == 2 and attempt["previous_attempt_id"] == "attempt-implementation-1" for attempt in attempts)


def test_v9_3_artifact_lineage_preserves_producer_agent_and_attempt() -> None:
    payload = run_v9_3_multi_agent_orchestration(V93OrchestrationConfig(evidence_dir=Path("/tmp/v9-3-test-evidence")))

    lineage = payload["artifact_lineage"]

    assert len(lineage) >= 4
    assert all(record["producer_agent_id"] for record in lineage)
    assert all(record["producer_attempt_id"] for record in lineage)
    implementation = next(record for record in lineage if record["producer_station_id"] == "station-implementation")
    assert implementation["producer_agent_id"] == "agent-implementation"
    assert implementation["producer_attempt_id"] == "attempt-implementation-2"


def test_v9_3_negative_fixtures_are_denied() -> None:
    fan_in_missing = json.loads((V9_ROOT / "fixtures/v9-3-orchestration/fan_in_missing_attribution.json").read_text(encoding="utf-8"))
    retry_overwrite = json.loads((V9_ROOT / "fixtures/v9-3-orchestration/retry_overwrites_old_attempt.json").read_text(encoding="utf-8"))
    source_agent = json.loads((V9_ROOT / "fixtures/v9-3-orchestration/source_agent_direct_mutation_attempt.json").read_text(encoding="utf-8"))

    assert validate_fan_in_join(fan_in_missing["fan_in_join_decision"]) == {"status": "DENIED", "reason": "fan_in_attribution_missing"}
    assert validate_retry_retains_old_attempt(retry_overwrite["attempt_history"], old_attempt_retained=retry_overwrite["old_attempt_retained"]) == {
        "status": "DENIED",
        "reason": "old_attempt_must_be_retained",
    }
    assert deny_source_agent_direct_mutation(source_agent["message"])["reason"] == "source_agent_direct_mutation_denied"


def test_v9_3_fan_in_and_retry_validators_bind_lineage_and_attempts_to_same_run() -> None:
    fan_in = {
        "orchestration_run_id": "run-a",
        "input_artifact_refs": ["artifact-ref://v9-3/implementation-proposal"],
        "attribution_refs": ["lineage-cross-run"],
    }
    cross_run_lineage = [
        {
            "lineage_record_id": "lineage-cross-run",
            "orchestration_run_id": "run-b",
            "output_artifact_ref": "artifact-ref://v9-3/implementation-proposal",
        }
    ]
    assert validate_fan_in_join(fan_in, cross_run_lineage) == {"status": "DENIED", "reason": "fan_in_attribution_run_mismatch"}

    attempt_history = [
        {
            "attempt_id": "attempt-old",
            "orchestration_run_id": "run-a",
            "station_id": "station-implementation",
            "attempt_number": 1,
            "status": "failed",
            "error_ref": "error-ref://v9-3/timeout",
        },
        {
            "attempt_id": "attempt-retry",
            "orchestration_run_id": "run-b",
            "station_id": "station-implementation",
            "attempt_number": 2,
            "previous_attempt_id": "attempt-old",
            "status": "recovered",
        },
    ]
    assert validate_retry_retains_old_attempt(attempt_history) == {"status": "DENIED", "reason": "retry_previous_attempt_run_mismatch"}


def test_v9_3_user_scenarios_are_runtime_backed_or_explicitly_blocked() -> None:
    payload = run_v9_3_multi_agent_orchestration(V93OrchestrationConfig(evidence_dir=Path("/tmp/v9-3-test-evidence")))
    scenarios = {item["scenario_id"]: item for item in payload["user_scenarios"]}

    assert scenarios["US-V9-07"]["status"] == "PASS"
    assert scenarios["US-V9-07"]["runtime_backed"] is True
    assert scenarios["US-V9-07"]["discussion_turn_count"] >= 2
    assert scenarios["US-V9-08"]["status"] == "BLOCKED"
    assert scenarios["US-V9-08"]["runtime_backed"] is False
    assert scenarios["US-V9-08"]["blocked_reason"] == "provider_image_generation_not_available_in_local_fixture"
    assert scenarios["US-V9-09"]["status"] == "PASS"
    assert scenarios["US-V9-09"]["mutation_applied_before_confirmation"] is False
    assert scenarios["US-V9-09"]["source_agent_direct_mutation_denied"] is True


def test_v9_3_entry_blocks_source_agent_or_missing_confirmation() -> None:
    with pytest.raises(V93OrchestrationRuntimeError, match="source=agent"):
        run_v9_3_multi_agent_orchestration(V93OrchestrationConfig(evidence_dir=Path("/tmp/v9-3-test-evidence"), source="agent", actor_type="agent"))
    with pytest.raises(V93OrchestrationRuntimeError, match="requires user confirmation"):
        run_v9_3_multi_agent_orchestration(V93OrchestrationConfig(evidence_dir=Path("/tmp/v9-3-test-evidence"), user_confirmed=False))


def test_v9_3_evidence_generator_writes_acceptance_dashboard() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "tools.v9.generate_v9_3_orchestration_evidence"],
        check=False,
        text=True,
        capture_output=True,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    data = json.loads((EVIDENCE_ROOT / "acceptance-data.json").read_text(encoding="utf-8"))
    html = (EVIDENCE_ROOT / "index.html").read_text(encoding="utf-8")

    assert data["status"] == "PASS"
    assert data["evidence_scope"] == "real_runtime_fixture"
    assert data["serial_parallel_fan_in_fan_out"] == "PASS"
    assert data["lost_worker_recovery"] == "PASS"
    assert data["artifact_lineage"] == "PASS"
    assert data["source_agent_direct_mutation_denied"] == "PASS"
    assert data["video_storyboard_fixture"] == "BLOCKED"
    assert "V9-3 多 Agent 编排运行切片" in html
    assert "执行器启动按钮" not in html
    assert "开始实现按钮" not in html


def test_v9_3_storyboard_provider_parser_supports_openai_compatible_shape() -> None:
    encoded_png = "iVBORw0KGgo="
    images = _extract_image_payloads({"data": [{"b64_json": encoded_png}]})

    assert images == [b"\x89PNG\r\n\x1a\n"]


def test_v9_3_storyboard_provider_block_reason_keeps_credential_rejected_blocked() -> None:
    reason = _blocked_reason_from_shapes(
        [
            {"base_resp_status_code": 2049, "base_resp_status_msg": "credential_rejected"},
            {"base_resp_status_code": 2049, "base_resp_status_msg": "credential_rejected"},
        ]
    )

    assert reason == "provider_credential_rejected"

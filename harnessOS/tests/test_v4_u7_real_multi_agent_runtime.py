from pathlib import Path

from core.workflows.v4_u5e_local_document_workflow import FakeLLMProviderAdapter
from core.workflows.v4_u7_real_multi_agent_runtime import (
    run_engineering_workflow_runtime,
    run_parallel_deliberation_runtime,
    run_serial_video_runtime,
    write_u7_evidence_package,
)


def test_u7_serial_video_provider_runtime_has_attempts_and_stale(tmp_path: Path) -> None:
    result = run_serial_video_runtime(provider_adapter=FakeLLMProviderAdapter())

    assert result["status"] == "completed"
    assert result["real_provider_backed"] is False
    assert result["deterministic_only"] is False
    assert len(result["nodes"]) == 6
    assert result["provider_invocation_count"] >= 7
    assert result["rerun"]["user_confirmed"] is True
    assert result["rerun"]["source_agent_can_rerun"] is False
    assert result["downstream_stale"]
    assert len(result["attempt_history"]["storyboard_agent"]) == 2

    write_u7_evidence_package(result, tmp_path)
    assert (tmp_path / "runtime-result.json").exists()
    assert (tmp_path / "operation-evidence.json").exists()
    assert (tmp_path / "workflow.drawio").read_text(encoding="utf-8").startswith("<mxfile")


def test_u7_parallel_deliberation_provider_runtime_contains_persona_semantics() -> None:
    result = run_parallel_deliberation_runtime(provider_adapter=FakeLLMProviderAdapter())

    assert result["status"] == "completed"
    assert result["parallel_semantics"]["persona_station_ids"] == [
        "product_persona",
        "architecture_persona",
        "risk_persona",
    ]
    assert result["parallel_semantics"]["cross_inspiration_edges"]
    assert len(result["nodes"]) == 6
    assert result["provider_invocation_count"] >= 7


def test_u7_engineering_provider_runtime_contains_human_confirmation_and_rerun() -> None:
    result = run_engineering_workflow_runtime(provider_adapter=FakeLLMProviderAdapter())

    assert result["status"] == "completed"
    assert len(result["nodes"]) == 11
    assert any(node["station_id"] == "human_confirmation" for node in result["nodes"])
    assert len(result["attempt_history"]["code_review"]) == 2
    assert result["quality_report"]["user_confirmation_required"] is True
    assert result["provider_invocation_count"] >= 12


def test_u7_evidence_is_redacted_from_provider_inputs(tmp_path: Path) -> None:
    result = run_engineering_workflow_runtime(provider_adapter=FakeLLMProviderAdapter())
    write_u7_evidence_package(result, tmp_path)

    combined = "\n".join(path.read_text(encoding="utf-8") for path in tmp_path.rglob("*") if path.is_file())
    for forbidden in [
        "capability_token",
        "subscription_token",
        "Authorization",
        "Bearer",
        "raw_trace_payload",
        "raw_artifact_content",
        "raw_connector_payload",
        "upstream signed URL",
    ]:
        assert forbidden not in combined

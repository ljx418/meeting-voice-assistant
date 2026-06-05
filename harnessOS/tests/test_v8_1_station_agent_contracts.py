from __future__ import annotations

from core.product_console.v7_3_workflow_run import build_workflow_spec
from core.station_agents import build_local_document_station_agent_registry, decide_agent_capability


def test_station_agent_registry_requires_agent_for_every_station_and_explainer() -> None:
    spec = build_workflow_spec("递归总结 Markdown 技术文档", "mission-v8", "2026-06-04T00:00:00+00:00")

    registry = build_local_document_station_agent_registry(spec).to_dict()

    assert registry["validation_result"]["status"] == "PASS"
    assert registry["validation_result"]["station_count"] == len(spec["stations"])
    assert registry["validation_result"]["agent_descriptor_count"] == len(spec["stations"])
    assert registry["validation_result"]["workflow_explainer_agent_exists"] is True
    assert registry["workflow_explainer_agent_id"] == "v8_workflow_explainer_agent"
    assert all(descriptor["source_policy"] == "source_agent_durable_mutation_denied" for descriptor in registry["station_agent_descriptors"])


def test_source_agent_durable_mutation_is_denied_by_capability_decision() -> None:
    decision = decide_agent_capability(
        agent_id="agent-v8",
        station_id="workflow_guard",
        operation="workflow.instance.start",
        source="agent",
        actor_type="agent",
        user_confirmed=True,
    ).to_dict()

    assert decision["allowed"] is False
    assert decision["forbidden_reason"] == "source_agent_durable_mutation_denied"
    assert decision["requires_user_confirmation"] is True


def test_unrestricted_connector_call_is_denied() -> None:
    decision = decide_agent_capability(
        agent_id="agent-v8",
        station_id="summary",
        operation="connector.call",
        source="mission_tui",
        actor_type="human_user",
        user_confirmed=True,
    ).to_dict()

    assert decision["allowed"] is False
    assert decision["forbidden_reason"] == "operation_requires_separate_stage_policy"

"""V4.0-P AgentTalk interaction E2E BFF contract tests."""

from __future__ import annotations

import asyncio

from fastapi.testclient import TestClient

from apps.api import create_app

from v4_0_reference_support import SCOPE_QUERY, assert_no_forbidden_text, build_gateway, seed_reference_console


def _client(monkeypatch, tmp_path, template_id: str = "v4_p_agenttalk_interaction"):
    monkeypatch.setenv("HARNESS_V3_5_DEV_MODE", "1")
    service = build_gateway(tmp_path)
    seeded = asyncio.run(seed_reference_console(service, template_id=template_id))
    return TestClient(create_app(gateway_service=service)), seeded


def test_interaction_state_is_bff_read_model_with_selected_ids(monkeypatch, tmp_path) -> None:
    client, seeded = _client(monkeypatch, tmp_path, "v4_p_interaction_state")
    instance_id = seeded["instance"]["workflow_instance_id"]

    client.post(
        f"/bff/instances/{instance_id}/agent/messages{SCOPE_QUERY}",
        json={"content": "解释当前流程，并给出一个可审计建议", "created_by": "workflow_console"},
    )
    state = client.get(f"/bff/instances/{instance_id}/agent/interaction-state{SCOPE_QUERY}").json()

    assert state["workflow_instance_id"] == instance_id
    assert state["agent_session_id"].startswith("ats_")
    assert state["selected_suggestion_id"].startswith("ags_")
    assert state["selected_proposal_id"].startswith("aap_")
    assert state["selected_patch_id"] == seeded["patch"]["workflow_patch_id"]
    assert state["refresh_generation"].startswith("agent_interaction:")
    assert state["source_refs"]["patch_queue"]["kind"] == "PatchQueueDTO"
    assert state["redaction_status"] == "redacted"
    assert_no_forbidden_text(state)


def test_explain_and_summarize_are_read_only_and_cannot_handoff(monkeypatch, tmp_path) -> None:
    client, seeded = _client(monkeypatch, tmp_path, "v4_p_read_only_intents")
    instance_id = seeded["instance"]["workflow_instance_id"]
    template_id = seeded["template"]["workflow_template_id"]

    before = client.get(f"/bff/workflows/{template_id}/patches{SCOPE_QUERY}&workflow_instance_id={instance_id}").json()
    response = client.post(
        f"/bff/instances/{instance_id}/agent/messages{SCOPE_QUERY}",
        json={"content": "解释当前流程并总结最近事件"},
    ).json()
    after = client.get(f"/bff/workflows/{template_id}/patches{SCOPE_QUERY}&workflow_instance_id={instance_id}").json()
    assert [item["patch_id"] for item in after] == [item["patch_id"] for item in before]
    assert "只给出摘要" in response["messages"][-1]["content"]

    proposal = client.post(
        f"/bff/instances/{instance_id}/agent/action-proposals{SCOPE_QUERY}",
        json={"intent_type": "explain_workflow", "title": "解释", "summary": "只读摘要"},
    ).json()
    blocked = client.post(
        f"/bff/instances/{instance_id}/agent/action-proposals/{proposal['proposal_id']}/handoff{SCOPE_QUERY}",
        json={"target_panel": "editing_panel", "workflow_patch_id": seeded["patch"]["workflow_patch_id"]},
    ).json()
    assert blocked["error"]["code"] == "WORKFLOW_ACTION_FORBIDDEN"
    assert_no_forbidden_text({"response": response, "proposal": proposal, "blocked": blocked})


def test_suggest_patch_handoff_opens_panel_without_applying_patch(monkeypatch, tmp_path) -> None:
    client, seeded = _client(monkeypatch, tmp_path, "v4_p_suggest_handoff")
    instance_id = seeded["instance"]["workflow_instance_id"]
    patch_id = seeded["patch"]["workflow_patch_id"]

    client.post(f"/bff/instances/{instance_id}/agent/messages{SCOPE_QUERY}", json={"content": "生成建议"})
    proposals = client.get(f"/bff/instances/{instance_id}/agent/action-proposals{SCOPE_QUERY}").json()
    proposal = next(item for item in proposals if item["policy_class"] == "proposal_only")
    handoff = client.post(
        f"/bff/instances/{instance_id}/agent/action-proposals/{proposal['proposal_id']}/handoff{SCOPE_QUERY}",
        json={"target_panel": "editing_panel", "workflow_patch_id": patch_id},
    ).json()
    diff = client.get(f"/bff/instances/{instance_id}/patches/{patch_id}/diff{SCOPE_QUERY}").json()

    assert handoff["status"] == "active"
    assert handoff["target_panel"] == "editing_panel"
    assert diff["workflow_patch_id"] == patch_id
    assert diff["operation"] == "update_station_prompt"
    assert_no_forbidden_text({"handoff": handoff, "diff": diff})


def test_canvas_chatbot_adds_controlled_approval_node_as_proposal_only(monkeypatch, tmp_path) -> None:
    client, seeded = _client(monkeypatch, tmp_path, "v4_p_canvas_chatbot_approval")
    instance_id = seeded["instance"]["workflow_instance_id"]
    template_id = seeded["template"]["workflow_template_id"]

    before_board = client.get(f"/bff/instances/{instance_id}/board{SCOPE_QUERY}").json()
    response = client.post(
        f"/bff/instances/{instance_id}/agent/messages{SCOPE_QUERY}",
        json={"content": "给这个工作流增加一个人工审批节点", "selected_station_id": "station_b"},
    ).json()
    proposals = client.get(f"/bff/instances/{instance_id}/agent/action-proposals{SCOPE_QUERY}").json()
    proposal = next(item for item in proposals if item["title"] == "生成节点调整建议")
    diff = client.get(f"/bff/instances/{instance_id}/patches/{proposal['workflow_patch_id']}/diff{SCOPE_QUERY}").json()
    after_board = client.get(f"/bff/instances/{instance_id}/board{SCOPE_QUERY}").json()
    patch_queue = client.get(f"/bff/workflows/{template_id}/patches{SCOPE_QUERY}&workflow_instance_id={instance_id}").json()

    assert response["messages"][-1]["content"].startswith("我已生成一个新增画布节点")
    assert proposal["title"] == "生成节点调整建议"
    assert diff["operation"] == "add_station"
    assert "人工审批" in str(diff)
    assert before_board["stations"] == after_board["stations"]
    assert any(item["patch_id"] == proposal["workflow_patch_id"] and item["status"] == "proposed" for item in patch_queue)
    assert_no_forbidden_text({"response": response, "proposal": proposal, "diff": diff})


def test_canvas_chatbot_updates_selected_node_prompt_as_proposal_only(monkeypatch, tmp_path) -> None:
    client, seeded = _client(monkeypatch, tmp_path, "v4_p_canvas_chatbot_prompt")
    instance_id = seeded["instance"]["workflow_instance_id"]

    before_board = client.get(f"/bff/instances/{instance_id}/board{SCOPE_QUERY}").json()
    response = client.post(
        f"/bff/instances/{instance_id}/agent/messages{SCOPE_QUERY}",
        json={"content": "优化当前节点 Prompt，增强角色一致性", "selected_station_id": "station_b", "selected_station_name": "Storyboard"},
    ).json()
    proposals = client.get(f"/bff/instances/{instance_id}/agent/action-proposals{SCOPE_QUERY}").json()
    proposal = next(item for item in proposals if item["title"] == "生成 Prompt 调整建议")
    diff = client.get(f"/bff/instances/{instance_id}/patches/{proposal['workflow_patch_id']}/diff{SCOPE_QUERY}").json()
    after_board = client.get(f"/bff/instances/{instance_id}/board{SCOPE_QUERY}").json()

    assert "Prompt Patch proposal" in response["messages"][-1]["content"]
    assert proposal["title"] == "生成 Prompt 调整建议"
    assert diff["operation"] == "update_station_prompt"
    assert "station_b" in str(diff)
    assert before_board["stations"] == after_board["stations"]
    assert_no_forbidden_text({"response": response, "proposal": proposal, "diff": diff})


def test_dismissed_proposal_and_agent_source_mutation_are_blocked(monkeypatch, tmp_path) -> None:
    client, seeded = _client(monkeypatch, tmp_path, "v4_p_stale_guards")
    instance_id = seeded["instance"]["workflow_instance_id"]
    template_id = seeded["template"]["workflow_template_id"]
    patch_id = seeded["patch"]["workflow_patch_id"]

    proposal = client.post(
        f"/bff/instances/{instance_id}/agent/action-proposals{SCOPE_QUERY}",
        json={"intent_type": "open_editing_panel", "target_panel": "editing"},
    ).json()
    client.post(f"/bff/instances/{instance_id}/agent/action-proposals/{proposal['proposal_id']}/dismiss{SCOPE_QUERY}")
    handoff = client.post(
        f"/bff/instances/{instance_id}/agent/action-proposals/{proposal['proposal_id']}/handoff{SCOPE_QUERY}",
        json={"target_panel": "editing_panel", "workflow_patch_id": patch_id},
    ).json()
    assert handoff["error"]["code"] == "WORKFLOW_ACTION_FORBIDDEN"

    applied_by_agent = client.post(
        f"/bff/workflows/{template_id}/patches/{patch_id}/apply{SCOPE_QUERY}",
        json={"workflow_instance_id": instance_id, "user_confirmed": True, "source": "agent"},
    ).json()
    assert applied_by_agent["error"]["code"] == "WORKFLOW_ACTION_FORBIDDEN"

    state = client.get(f"/bff/instances/{instance_id}/agent/interaction-state{SCOPE_QUERY}").json()
    assert "dismissed_proposal_not_handoffable" in state["stale_reasons"]
    assert_no_forbidden_text({"handoff": handoff, "applied_by_agent": applied_by_agent, "state": state})

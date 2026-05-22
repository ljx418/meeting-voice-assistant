"""V4.0-J Agent action policy guard tests."""

from __future__ import annotations

import asyncio

from fastapi.testclient import TestClient

from apps.api import create_app

from v4_0_reference_support import SCOPE_QUERY, build_gateway, seed_reference_console


def _client(monkeypatch, tmp_path):
    monkeypatch.setenv("HARNESS_V3_5_DEV_MODE", "1")
    service = build_gateway(tmp_path)
    seeded = asyncio.run(seed_reference_console(service, template_id="v4_j_policy"))
    return TestClient(create_app(gateway_service=service)), seeded


def test_agent_action_policy_classes(monkeypatch, tmp_path) -> None:
    client, seeded = _client(monkeypatch, tmp_path)
    instance_id = seeded["instance"]["workflow_instance_id"]

    cases = {
        "explain_workflow": "display_only",
        "open_context_panel": "navigation",
        "propose_context_update": "proposal_only",
    }
    for intent, policy in cases.items():
        result = client.post(
            f"/bff/instances/{instance_id}/agent/action-proposals{SCOPE_QUERY}",
            json={"intent_type": intent, "title": intent, "summary": "policy test"},
        ).json()
        assert result["policy_class"] == policy
        assert result["policy_decision"] == "proposal_only"


def test_forbidden_agent_actions_are_rejected(monkeypatch, tmp_path) -> None:
    client, seeded = _client(monkeypatch, tmp_path)
    instance_id = seeded["instance"]["workflow_instance_id"]

    for intent in (
        "apply_patch",
        "reject_patch",
        "publish_version",
        "respond_approval",
        "update_context",
        "emit_business_event",
        "start_workflow",
        "rerun_station",
        "call_connector",
        "call_external_llm",
    ):
        blocked = client.post(
            f"/bff/instances/{instance_id}/agent/action-proposals{SCOPE_QUERY}",
            json={"intent_type": intent, "title": intent, "summary": "must be blocked"},
        ).json()
        assert blocked["error"]["code"] == "WORKFLOW_ACTION_FORBIDDEN"

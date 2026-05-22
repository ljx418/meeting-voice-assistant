"""V4.0-I Agent patch governance tests."""

from __future__ import annotations

import asyncio

from fastapi.testclient import TestClient

from apps.api import create_app

from v4_0_reference_support import SCOPE_QUERY, assert_no_forbidden_text, build_gateway, seed_reference_console


def _client(monkeypatch, tmp_path, template_id: str = "v4_i_agent_patch"):
    monkeypatch.setenv("HARNESS_V3_5_DEV_MODE", "1")
    service = build_gateway(tmp_path)
    seeded = asyncio.run(seed_reference_console(service, template_id=template_id))
    return TestClient(create_app(gateway_service=service)), seeded


def test_source_agent_can_propose_but_cannot_apply_or_publish(monkeypatch, tmp_path) -> None:
    client, seeded = _client(monkeypatch, tmp_path, "v4_i_agent_governance")
    template_id = seeded["template"]["workflow_template_id"]
    instance_id = seeded["instance"]["workflow_instance_id"]

    proposed = client.post(
        f"/bff/workflows/{template_id}/patches{SCOPE_QUERY}",
        json={
            "source": "agent",
            "intent_type": "inspector_update",
            "operation": "update_station_prompt",
            "workflow_instance_id": instance_id,
            "payload": {"station_id": "station_b", "prompt_patch": "增强角色一致性"},
        },
    ).json()
    assert proposed["source"] == "agent"
    assert proposed["operation"] == "update_station_prompt"

    agent_apply = client.post(
        f"/bff/workflows/{template_id}/patches/{proposed['workflow_patch_id']}/apply{SCOPE_QUERY}",
        json={"workflow_instance_id": instance_id, "user_confirmed": True, "source": "agent"},
    ).json()
    assert agent_apply["error"]["code"] == "WORKFLOW_ACTION_FORBIDDEN"

    agent_publish = client.post(
        f"/bff/workflows/{template_id}/publish{SCOPE_QUERY}",
        json={"version": "9.9.9", "expected_draft_revision": 1, "user_confirmed": True, "source": "agent"},
    ).json()
    assert agent_publish["error"]["code"] == "WORKFLOW_ACTION_FORBIDDEN"
    assert_no_forbidden_text({"proposed": proposed, "agent_apply": agent_apply, "agent_publish": agent_publish})


def test_agent_high_risk_patch_remains_governed(monkeypatch, tmp_path) -> None:
    client, seeded = _client(monkeypatch, tmp_path, "v4_i_agent_high_risk")
    template_id = seeded["template"]["workflow_template_id"]
    instance_id = seeded["instance"]["workflow_instance_id"]

    proposed = client.post(
        f"/bff/workflows/{template_id}/patches{SCOPE_QUERY}",
        json={
            "source": "agent",
            "intent_type": "inspector_update",
            "operation": "update_connector",
            "workflow_instance_id": instance_id,
            "payload": {"station_id": "station_b", "connector_refs": ["mcp"]},
        },
    ).json()
    diff = client.get(f"/bff/workflows/{template_id}/patches/{proposed['workflow_patch_id']}/diff{SCOPE_QUERY}").json()
    assert diff["requires_approval"] is True
    blocked = client.post(
        f"/bff/workflows/{template_id}/patches/{proposed['workflow_patch_id']}/apply{SCOPE_QUERY}",
        json={"workflow_instance_id": instance_id, "user_confirmed": True, "source": "editing_panel"},
    ).json()
    assert blocked["error"]["code"] == "WORKFLOW_ACTION_FORBIDDEN"
    assert_no_forbidden_text({"diff": diff, "blocked": blocked})

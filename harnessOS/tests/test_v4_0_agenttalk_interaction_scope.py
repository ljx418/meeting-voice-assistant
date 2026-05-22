"""V4.0-P AgentTalk interaction scope isolation tests."""

from __future__ import annotations

import asyncio

from fastapi.testclient import TestClient

from apps.api import create_app

from v4_0_reference_support import OTHER_SCOPE, SCOPE_QUERY, assert_no_forbidden_text, build_gateway, seed_reference_console


def test_agenttalk_interaction_state_and_handoff_are_instance_scoped(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("HARNESS_V3_5_DEV_MODE", "1")
    service = build_gateway(tmp_path)
    first = asyncio.run(seed_reference_console(service, template_id="v4_p_scope_a"))
    second = asyncio.run(seed_reference_console(service, template_id="v4_p_scope_b", scope=OTHER_SCOPE))
    client = TestClient(create_app(gateway_service=service))
    first_instance = first["instance"]["workflow_instance_id"]
    second_instance = second["instance"]["workflow_instance_id"]

    first_state = client.get(f"/bff/instances/{first_instance}/agent/interaction-state{SCOPE_QUERY}").json()
    wrong_scope_state = client.get(f"/bff/instances/{second_instance}/agent/interaction-state{SCOPE_QUERY}").json()

    assert first_state["workflow_instance_id"] == first_instance
    assert wrong_scope_state["error"]["code"] in {"METHOD_NOT_FOUND", "SCOPE_MISMATCH"}
    assert_no_forbidden_text({"first_state": first_state, "wrong_scope_state": wrong_scope_state})

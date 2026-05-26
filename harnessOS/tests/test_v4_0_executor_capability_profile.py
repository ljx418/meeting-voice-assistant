"""V4.0-Q executor capability profile and source=agent guard tests."""

from __future__ import annotations

import asyncio
import json
from pathlib import Path

from fastapi.testclient import TestClient

from apps.api import create_app

from v4_0_reference_support import SCOPE_QUERY, assert_no_forbidden_text, build_gateway, seed_reference_console


CONTRACT_PATH = Path("docs/design/V4.0/v4_0_q_controlled_executor_design_gate_contract.json")


def _client(monkeypatch, tmp_path, template_id: str = "v4_q_executor_capability"):
    monkeypatch.setenv("HARNESS_V3_5_DEV_MODE", "1")
    service = build_gateway(tmp_path)
    seeded = asyncio.run(seed_reference_console(service, template_id=template_id))
    return TestClient(create_app(gateway_service=service)), seeded


def test_executor_capabilities_remain_inactive_in_q_contract() -> None:
    contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    profile = {item["capability"]: item for item in contract["capability_profile"]}
    for capability in ("executor.dry_run", "executor.user_confirmed_execute", "executor.approval_gated_execute", "executor.admin_override"):
        assert profile[capability]["active_in_q"] is False
        assert profile[capability]["can_mutate_runtime"] is False
    for capability in ("agent.propose", "agent.handoff", "agent.explain", "agent.navigate"):
        assert profile[capability]["can_mutate_runtime"] is False


def test_source_agent_cannot_execute_mutations_even_with_executor_claims(monkeypatch, tmp_path) -> None:
    client, seeded = _client(monkeypatch, tmp_path)
    instance_id = seeded["instance"]["workflow_instance_id"]
    template_id = seeded["template"]["workflow_template_id"]
    patch_id = seeded["patch"]["workflow_patch_id"]
    approval_id = seeded["approval"]["approval_id"]
    executor_claims = {"capabilities": ["executor.dry_run", "executor.user_confirmed_execute", "executor.admin_override"]}

    responses = [
        client.post(
            f"/bff/workflows/{template_id}/patches/{patch_id}/apply{SCOPE_QUERY}",
            json={"workflow_instance_id": instance_id, "user_confirmed": True, "source": "agent", "executor_claims": executor_claims},
        ).json(),
        client.post(
            f"/bff/workflows/{template_id}/publish{SCOPE_QUERY}",
            json={"workflow_instance_id": instance_id, "version": "9.9.9", "expected_draft_revision": 1, "user_confirmed": True, "source": "agent", "executor_claims": executor_claims},
        ).json(),
        client.post(
            f"/bff/instances/{instance_id}/approvals/{approval_id}/respond{SCOPE_QUERY}",
            json={"decision": "approve", "user_confirmed": True, "source": "agent", "executor_claims": executor_claims},
        ).json(),
        client.post(
            f"/bff/instances/{instance_id}/context/update{SCOPE_QUERY}",
            json={"op": "set", "path": "business.q_guard", "value": "blocked", "user_confirmed": True, "source": "agent", "executor_claims": executor_claims},
        ).json(),
        client.post(
            f"/bff/instances/{instance_id}/business-events{SCOPE_QUERY}",
            json={"event_type": "business.q.guard", "payload": {"value": "blocked"}, "user_confirmed": True, "source": "agent", "executor_claims": executor_claims},
        ).json(),
    ]

    for response in responses:
        assert response["error"]["code"] == "WORKFLOW_ACTION_FORBIDDEN"
    assert_no_forbidden_text(responses)

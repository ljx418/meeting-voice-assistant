"""V4.0-S capability token binding design tests."""

from __future__ import annotations

import asyncio
import json
from pathlib import Path

from fastapi.testclient import TestClient

from apps.api import create_app

from v4_0_reference_support import SCOPE_QUERY, assert_no_forbidden_text, build_gateway, seed_reference_console


CONTRACT_PATH = Path("docs/design/V4.0/v4_0_s_production_auth_tenant_boundary_design_contract.json")
REQUIRED_BINDINGS = {
    "origin binding",
    "audience binding",
    "tenant binding",
    "workspace binding",
    "actor binding",
    "capability binding",
    "expiration",
    "rotation",
    "revocation",
    "emergency revoke",
    "audit",
}


def test_capability_token_binding_design_cannot_bypass_user_confirmation() -> None:
    contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    bindings = {item["binding"]: item for item in contract["capability_token_binding_design"]}
    assert set(bindings) == REQUIRED_BINDINGS
    for binding in bindings.values():
        assert binding["can_bypass_user_confirmation"] is False
    boundary = contract["agent_and_executor_boundary"]
    assert boundary["source_agent_can_mutate"] is False
    assert boundary["executor_capabilities_active"] is False
    assert boundary["future_executor_claims_enable_mutation"] is False
    assert boundary["user_confirmation_required_for_mutation"] is True


def test_future_executor_claims_do_not_allow_source_agent_mutation(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("HARNESS_V3_5_DEV_MODE", "1")
    service = build_gateway(tmp_path)
    seeded = asyncio.run(seed_reference_console(service, template_id="v4_s_token_binding"))
    client = TestClient(create_app(gateway_service=service))
    instance_id = seeded["instance"]["workflow_instance_id"]
    template_id = seeded["template"]["workflow_template_id"]
    patch_id = seeded["patch"]["workflow_patch_id"]
    approval_id = seeded["approval"]["approval_id"]
    token_claims = {
        "capabilities": ["executor.dry_run", "executor.user_confirmed_execute", "executor.admin_override"],
        "tenant_id": "future-tenant",
        "actor_id": "future-agent",
    }

    responses = [
        client.post(
            f"/bff/workflows/{template_id}/patches/{patch_id}/apply{SCOPE_QUERY}",
            json={"workflow_instance_id": instance_id, "user_confirmed": True, "source": "agent", "token_claims": token_claims},
        ).json(),
        client.post(
            f"/bff/workflows/{template_id}/publish{SCOPE_QUERY}",
            json={"workflow_instance_id": instance_id, "version": "9.9.9", "expected_draft_revision": 1, "user_confirmed": True, "source": "agent", "token_claims": token_claims},
        ).json(),
        client.post(
            f"/bff/instances/{instance_id}/approvals/{approval_id}/respond{SCOPE_QUERY}",
            json={"decision": "approve", "user_confirmed": True, "source": "agent", "token_claims": token_claims},
        ).json(),
        client.post(
            f"/bff/instances/{instance_id}/context/update{SCOPE_QUERY}",
            json={"op": "set", "path": "business.s_guard", "value": "blocked", "user_confirmed": True, "source": "agent", "token_claims": token_claims},
        ).json(),
        client.post(
            f"/bff/instances/{instance_id}/business-events{SCOPE_QUERY}",
            json={"event_type": "business.s.guard", "payload": {"value": "blocked"}, "user_confirmed": True, "source": "agent", "token_claims": token_claims},
        ).json(),
    ]

    for response in responses:
        assert response["error"]["code"] == "WORKFLOW_ACTION_FORBIDDEN"
    assert_no_forbidden_text(responses)

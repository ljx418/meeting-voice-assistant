"""V4.0-L Agent handoff audit redaction tests."""

from __future__ import annotations

import asyncio
import json

from fastapi.testclient import TestClient

from apps.api import create_app

from v4_0_reference_support import FORBIDDEN_TEXT, SCOPE_QUERY, assert_no_forbidden_text, build_gateway, seed_reference_console


def test_handoff_audit_query_is_redacted(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("HARNESS_V3_5_DEV_MODE", "1")
    service = build_gateway(tmp_path)
    seeded = asyncio.run(seed_reference_console(service, template_id="v4_l_handoff_audit"))
    instance_id = seeded["instance"]["workflow_instance_id"]
    patch_id = seeded["patch"]["workflow_patch_id"]
    client = TestClient(create_app(gateway_service=service))

    proposal = client.post(
        f"/bff/instances/{instance_id}/agent/action-proposals{SCOPE_QUERY}",
        json={"intent_type": "open_editing_panel", "workflow_patch_id": patch_id, "target_panel": "editing"},
    ).json()
    handoff = client.post(
        f"/bff/instances/{instance_id}/agent/action-proposals/{proposal['proposal_id']}/handoff{SCOPE_QUERY}",
        json={
            "target_panel": "editing_panel",
            "workflow_patch_id": patch_id,
            "suggested_form_prefill": {
                "capability_token": "capability_token",
                "Authorization": "Bearer secret-token-value",
                "raw_trace_payload": "raw",
            },
        },
    ).json()
    client.get(f"/bff/instances/{instance_id}/agent/action-handoffs/{handoff['handoff_id']}{SCOPE_QUERY}")
    audit = client.get(f"/bff/instances/{instance_id}/agent/action-handoffs/{handoff['handoff_id']}/audit{SCOPE_QUERY}").json()
    text = json.dumps(audit)
    for forbidden in FORBIDDEN_TEXT:
        assert forbidden not in text
    assert_no_forbidden_text(audit)


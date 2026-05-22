"""V4.0-K Agent action handoff redaction tests."""

from __future__ import annotations

import asyncio

from fastapi.testclient import TestClient

from apps.api import create_app

from v4_0_reference_support import SCOPE_QUERY, assert_no_forbidden_text, build_gateway, seed_reference_console


def test_handoff_dto_and_audit_are_redacted(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("HARNESS_V3_5_DEV_MODE", "1")
    service = build_gateway(tmp_path)
    seeded = asyncio.run(seed_reference_console(service, template_id="v4_k_handoff_redaction"))
    instance_id = seeded["instance"]["workflow_instance_id"]
    patch_id = seeded["patch"]["workflow_patch_id"]
    client = TestClient(create_app(gateway_service=service))

    proposal = client.post(
        f"/bff/instances/{instance_id}/agent/action-proposals{SCOPE_QUERY}",
        json={
            "intent_type": "open_editing_panel",
            "workflow_patch_id": patch_id,
            "target_panel": "editing",
            "payload": {"summary": "ok", "capability_token": "secret-token-value"},
        },
    ).json()
    assert proposal["error"]["code"] == "WORKFLOW_PATCH_INVALID"

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
                "note": "safe",
                "Authorization": "Bearer secret-token-value",
                "raw_trace_payload": "secret-token-value",
            },
        },
    ).json()

    assert "Authorization" not in handoff["suggested_form_prefill"]
    assert "raw_trace_payload" not in handoff["suggested_form_prefill"]
    assert_no_forbidden_text(handoff)

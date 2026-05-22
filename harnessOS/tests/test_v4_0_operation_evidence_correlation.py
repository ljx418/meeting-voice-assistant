"""V4.0-M operation evidence correlation coverage."""

from __future__ import annotations

import asyncio

from fastapi.testclient import TestClient

from apps.api import create_app

from v4_0_reference_support import SCOPE_QUERY, build_gateway, seed_reference_console


def test_approval_context_and_business_event_evidence_are_correlated(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("HARNESS_V3_5_DEV_MODE", "1")
    service = build_gateway(tmp_path)
    seeded = asyncio.run(seed_reference_console(service, template_id="v4_m_correlation"))
    client = TestClient(create_app(gateway_service=service))
    instance_id = seeded["instance"]["workflow_instance_id"]
    approval_id = seeded["approval"]["approval_id"]

    approved = client.post(
        f"/bff/instances/{instance_id}/approvals/{approval_id}/respond{SCOPE_QUERY}",
        json={"decision": "approve", "source": "approval_panel", "user_confirmed": True, "correlation_id": "corr_approval"},
    ).json()
    assert approved["evidence"]["correlation_id"] == "corr_approval"
    assert approved["evidence"]["runtime_result_ref"]["type"] == "approval"

    context = client.get(f"/bff/instances/{instance_id}/context{SCOPE_QUERY}").json()
    updated = client.post(
        f"/bff/instances/{instance_id}/context/update{SCOPE_QUERY}",
        json={
            "op": "set",
            "path": "business.review_note",
            "value": "ok",
            "expected_revision": context["revision"],
            "source": "context_panel",
            "user_confirmed": True,
            "correlation_id": "corr_context",
        },
    ).json()
    assert updated["evidence"]["correlation_id"] == "corr_context"
    assert updated["evidence"]["runtime_result_ref"]["type"] == "workflow_context"

    event = client.post(
        f"/bff/instances/{instance_id}/business-events{SCOPE_QUERY}",
        json={
            "event_type": "business.workflow.note_submitted",
            "event_id": "evt_m_correlation",
            "payload": {"note": "ok"},
            "binding": {"target_path": "context.business.event_note", "payload_path": "event.payload.note"},
            "source": "context_panel",
            "user_confirmed": True,
            "correlation_id": "corr_event",
        },
    ).json()
    assert event["evidence"]["correlation_id"] == "corr_event"
    assert event["evidence"]["runtime_result_ref"]["type"] == "business_event"

    evidence = client.get(f"/bff/instances/{instance_id}/agent/operation-evidence{SCOPE_QUERY}").json()
    assert {"approval.respond", "workflow.context.update", "business.event.emit"}.issubset({item["operation"] for item in evidence})
    assert {"corr_approval", "corr_context", "corr_event"}.issubset({item["correlation_id"] for item in evidence})

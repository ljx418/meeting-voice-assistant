"""V4.0-M operation evidence redaction tests."""

from __future__ import annotations

import asyncio

from fastapi.testclient import TestClient

from apps.api import create_app

from v4_0_reference_support import FORBIDDEN_TEXT, SCOPE_QUERY, build_gateway, seed_reference_console


def test_operation_evidence_and_governance_review_are_redacted(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("HARNESS_V3_5_DEV_MODE", "1")
    service = build_gateway(tmp_path)
    seeded = asyncio.run(seed_reference_console(service, template_id="v4_m_redaction"))
    client = TestClient(create_app(gateway_service=service))
    instance_id = seeded["instance"]["workflow_instance_id"]
    template_id = seeded["template"]["workflow_template_id"]
    patch_id = seeded["patch"]["workflow_patch_id"]

    client.post(
        f"/bff/workflows/{template_id}/patches/{patch_id}/apply{SCOPE_QUERY}",
        json={
            "workflow_instance_id": instance_id,
            "user_confirmed": True,
            "source": "editing_panel",
            "correlation_id": "Bearer secret-token-value",
            "idempotency_key": "raw_trace_payload secret-token-value",
            "raw_artifact_content": "secret-token-value",
            "Authorization": "Bearer secret-token-value",
        },
    )
    evidence = client.get(f"/bff/instances/{instance_id}/agent/operation-evidence{SCOPE_QUERY}").text
    review = client.get(f"/bff/instances/{instance_id}/agent/governance-review{SCOPE_QUERY}").text
    for forbidden in FORBIDDEN_TEXT + ("raw prompt",):
        assert forbidden not in evidence
        assert forbidden not in review

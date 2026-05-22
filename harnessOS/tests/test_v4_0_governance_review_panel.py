"""V4.0-M governance review panel BFF tests."""

from __future__ import annotations

import asyncio

from fastapi.testclient import TestClient

from apps.api import create_app

from v4_0_reference_support import SCOPE_QUERY, build_gateway, seed_reference_console


def test_governance_review_is_derived_read_model(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("HARNESS_V3_5_DEV_MODE", "1")
    service = build_gateway(tmp_path)
    seeded = asyncio.run(seed_reference_console(service, template_id="v4_m_governance_review"))
    client = TestClient(create_app(gateway_service=service))
    instance_id = seeded["instance"]["workflow_instance_id"]
    template_id = seeded["template"]["workflow_template_id"]
    patch_id = seeded["patch"]["workflow_patch_id"]

    client.post(
        f"/bff/workflows/{template_id}/patches/{patch_id}/reject{SCOPE_QUERY}",
        json={"workflow_instance_id": instance_id, "user_confirmed": True, "source": "editing_panel", "reason": "not now"},
    )
    review = client.get(f"/bff/instances/{instance_id}/agent/governance-review{SCOPE_QUERY}").json()
    assert review["summary"]["evidence_count"] == 1
    assert review["summary"]["operation_counts"]["workflow.patch.reject"] == 1
    assert review["operation_evidence"][0]["operation"] == "workflow.patch.reject"
    assert review["redaction_status"] == "redacted"

    unsupported_write = client.post(
        f"/bff/instances/{instance_id}/agent/governance-review{SCOPE_QUERY}",
        json={"status": "succeeded"},
    )
    assert unsupported_write.status_code == 405

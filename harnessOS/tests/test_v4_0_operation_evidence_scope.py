"""V4.0-M operation evidence scope and capability tests."""

from __future__ import annotations

import asyncio

from fastapi.testclient import TestClient

from apps.api import create_app
from core.protocol.auth import issue_capability_token

from v4_0_reference_support import LOCAL_ORIGIN, SCOPE_QUERY, build_gateway, seed_reference_console


SECRET = "v4-m-evidence-secret"


def test_operation_evidence_routes_enforce_instance_ownership(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("HARNESS_V3_5_DEV_MODE", "1")
    service = build_gateway(tmp_path)
    first = asyncio.run(seed_reference_console(service, template_id="v4_m_scope_a"))
    second = asyncio.run(seed_reference_console(service, template_id="v4_m_scope_b"))
    client = TestClient(create_app(gateway_service=service))
    first_instance = first["instance"]["workflow_instance_id"]
    second_instance = second["instance"]["workflow_instance_id"]
    patch_id = first["patch"]["workflow_patch_id"]
    template_id = first["template"]["workflow_template_id"]

    applied = client.post(
        f"/bff/workflows/{template_id}/patches/{patch_id}/apply{SCOPE_QUERY}",
        json={"workflow_instance_id": first_instance, "user_confirmed": True, "source": "editing_panel"},
    ).json()
    evidence_id = applied["evidence"]["evidence_id"]

    wrong_instance = client.get(f"/bff/instances/{second_instance}/agent/operation-evidence/{evidence_id}{SCOPE_QUERY}").json()
    assert wrong_instance["error"]["code"] == "SCOPE_MISMATCH"


def test_operation_evidence_routes_require_read_capabilities(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("HARNESS_CAPABILITY_TOKEN_SECRET", SECRET)
    monkeypatch.delenv("HARNESS_V3_5_DEV_MODE", raising=False)
    service = build_gateway(tmp_path)
    seeded = asyncio.run(seed_reference_console(service, template_id="v4_m_capability"))
    client = TestClient(create_app(gateway_service=service))
    instance_id = seeded["instance"]["workflow_instance_id"]

    def token(capabilities: tuple[str, ...]) -> str:
        return issue_capability_token(
            app_profile=service.app_registry.get("reference_app"),
            project_id="demo_a",
            workspace_id="local",
            capabilities=capabilities,
            allowed_origins=(LOCAL_ORIGIN,),
            secret=SECRET,
        )

    missing = client.get(
        f"/bff/instances/{instance_id}/agent/operation-evidence",
        headers={"Authorization": f"Bearer {token(('workflows.read',))}", "Origin": LOCAL_ORIGIN},
    ).json()
    assert missing["error"]["code"] == "CAPABILITY_DENIED"

    ok = client.get(
        f"/bff/instances/{instance_id}/agent/operation-evidence",
        headers={"Authorization": f"Bearer {token(('operation_evidence.read',))}", "Origin": LOCAL_ORIGIN},
    )
    assert ok.status_code == 200

    review_missing = client.get(
        f"/bff/instances/{instance_id}/agent/governance-review",
        headers={"Authorization": f"Bearer {token(('operation_evidence.read',))}", "Origin": LOCAL_ORIGIN},
    ).json()
    assert review_missing["error"]["code"] == "CAPABILITY_DENIED"

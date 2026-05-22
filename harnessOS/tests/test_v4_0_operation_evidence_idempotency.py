"""V4.0-M operation evidence idempotency tests."""

from __future__ import annotations

import asyncio

from fastapi.testclient import TestClient

from apps.api import create_app

from v4_0_reference_support import SCOPE_QUERY, build_gateway, seed_reference_console


def test_repeated_idempotent_patch_apply_does_not_duplicate_success_evidence(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("HARNESS_V3_5_DEV_MODE", "1")
    service = build_gateway(tmp_path)
    seeded = asyncio.run(seed_reference_console(service, template_id="v4_m_idempotent_apply"))
    client = TestClient(create_app(gateway_service=service))
    instance_id = seeded["instance"]["workflow_instance_id"]
    template_id = seeded["template"]["workflow_template_id"]
    patch_id = seeded["patch"]["workflow_patch_id"]
    payload = {"workflow_instance_id": instance_id, "user_confirmed": True, "source": "editing_panel"}

    first = client.post(f"/bff/workflows/{template_id}/patches/{patch_id}/apply{SCOPE_QUERY}", json=payload).json()
    second = client.post(f"/bff/workflows/{template_id}/patches/{patch_id}/apply{SCOPE_QUERY}", json=payload).json()
    assert first["evidence"]["status"] == "succeeded"
    assert second["idempotent"] is True
    assert second["evidence"]["status"] == "idempotent_replayed"

    evidence = client.get(f"/bff/instances/{instance_id}/agent/operation-evidence{SCOPE_QUERY}").json()
    statuses = [item["status"] for item in evidence]
    assert statuses.count("succeeded") == 1
    assert statuses.count("idempotent_replayed") == 1


def test_blocked_high_risk_operation_records_blocked_evidence(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("HARNESS_V3_5_DEV_MODE", "1")
    service = build_gateway(tmp_path)
    seeded = asyncio.run(seed_reference_console(service, template_id="v4_m_blocked"))
    client = TestClient(create_app(gateway_service=service))
    instance_id = seeded["instance"]["workflow_instance_id"]
    template_id = seeded["template"]["workflow_template_id"]

    from apps.gateway.protocol import RpcRequest

    risky = asyncio.run(
        service.handle_rpc(
            RpcRequest(
                id="risk",
                method="workflow.patch.propose",
                params={
                    "workflow_template_id": template_id,
                    "patch": {
                        "operation": "update_connector",
                        "payload": {"station_id": "station_b", "connector_refs": ["dangerous_connector"]},
                        "actor_type": "agent",
                        "actor_id": "agent_m",
                        "proposed_by": "agent_m",
                        "metadata": {"workflow_instance_id": instance_id},
                    },
                    "scope": {"app_id": "reference_app", "project_id": "demo_a", "workspace_id": "local"},
                },
            )
        )
    ).result["patch"]

    blocked = client.post(
        f"/bff/workflows/{template_id}/patches/{risky['workflow_patch_id']}/apply{SCOPE_QUERY}",
        json={"workflow_instance_id": instance_id, "user_confirmed": True, "source": "editing_panel"},
    ).json()
    assert blocked["error"]["code"] == "WORKFLOW_ACTION_FORBIDDEN"
    evidence = client.get(f"/bff/instances/{instance_id}/agent/operation-evidence{SCOPE_QUERY}").json()
    assert evidence[-1]["operation"] == "workflow.patch.apply"
    assert evidence[-1]["status"] == "blocked"

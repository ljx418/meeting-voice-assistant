"""V4.0-E reference console scope and ownership isolation tests."""

from __future__ import annotations

import asyncio

from fastapi.testclient import TestClient

from apps.api import create_app

from v4_0_reference_support import OTHER_SCOPE, OTHER_SCOPE_QUERY, SCOPE, SCOPE_QUERY, build_gateway, rpc, seed_reference_console


def test_reference_console_rejects_cross_scope_resources(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("HARNESS_V3_5_DEV_MODE", "1")
    service = build_gateway(tmp_path)
    seeded = asyncio.run(seed_reference_console(service))
    client = TestClient(create_app(gateway_service=service))
    instance_id = seeded["instance"]["workflow_instance_id"]
    artifact_id = seeded["station_b"]["output_artifact_ids"][0]

    for path in (
        f"/bff/instances/{instance_id}/status{OTHER_SCOPE_QUERY}",
        f"/bff/instances/{instance_id}/board{OTHER_SCOPE_QUERY}",
        f"/bff/instances/{instance_id}/artifacts/{artifact_id}/metadata{OTHER_SCOPE_QUERY}",
        f"/bff/instances/{instance_id}/quality{OTHER_SCOPE_QUERY}",
        f"/bff/instances/{instance_id}/context{OTHER_SCOPE_QUERY}",
    ):
        response = client.get(path)
        assert response.json()["error"]["code"] == "SCOPE_MISMATCH"


def test_reference_console_rejects_same_scope_wrong_instance_resources(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("HARNESS_V3_5_DEV_MODE", "1")
    service = build_gateway(tmp_path)
    first = asyncio.run(seed_reference_console(service, template_id="reference_console_scope_a"))
    second = asyncio.run(seed_reference_console(service, template_id="reference_console_scope_b"))
    client = TestClient(create_app(gateway_service=service))
    first_instance = first["instance"]["workflow_instance_id"]
    second_instance = second["instance"]["workflow_instance_id"]
    approval_id = first["approval"]["approval_id"]
    artifact_id = first["station_b"]["output_artifact_ids"][0]
    evaluation_id = first["quality"]["evaluation_id"]
    patch_id = first["patch"]["workflow_patch_id"]

    wrong_approval = client.post(
        f"/bff/instances/{second_instance}/approvals/{approval_id}/respond{SCOPE_QUERY}",
        json={"decision": "approve", "source": "approval_panel", "user_confirmed": True},
    )
    wrong_artifact = client.get(f"/bff/instances/{second_instance}/artifacts/{artifact_id}/metadata{SCOPE_QUERY}")
    wrong_quality = client.get(f"/bff/instances/{second_instance}/quality/{evaluation_id}{SCOPE_QUERY}")
    wrong_patch = client.get(f"/bff/instances/{second_instance}/patches/{patch_id}/diff{SCOPE_QUERY}")

    assert wrong_approval.json()["error"]["code"] == "SCOPE_MISMATCH"
    assert wrong_artifact.json()["error"]["code"] == "SCOPE_MISMATCH"
    assert wrong_quality.json()["error"]["code"] == "SCOPE_MISMATCH"
    assert wrong_patch.json()["error"]["code"] == "SCOPE_MISMATCH"

    sibling = asyncio.run(
        rpc(
            service,
            "workflow.instance.start",
            {"workflow_version_id": first["version"]["workflow_version_id"], "scope": SCOPE},
        )
    )["workflow_instance"]
    same_template_wrong_instance = client.get(f"/bff/instances/{sibling['workflow_instance_id']}/patches/{patch_id}/diff{SCOPE_QUERY}")
    assert same_template_wrong_instance.json()["error"]["code"] == "SCOPE_MISMATCH"

    # Same app/workspace but different project is also isolated.
    other_project = asyncio.run(seed_reference_console(service, template_id="reference_console_scope_c", scope=OTHER_SCOPE))
    other_instance = other_project["instance"]["workflow_instance_id"]
    cross_project_patch = client.get(f"/bff/instances/{other_instance}/patches/{patch_id}/diff{OTHER_SCOPE_QUERY}")
    assert cross_project_patch.json()["error"]["code"] == "SCOPE_MISMATCH"

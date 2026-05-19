"""V4.0-E reference Workflow Console BFF/runtime E2E tests."""

from __future__ import annotations

import asyncio

from fastapi.testclient import TestClient

from apps.api import create_app

from v4_0_reference_support import SCOPE_QUERY, assert_no_forbidden_text, build_gateway, seed_reference_console


def test_reference_workflow_console_real_bff_runtime_dtos(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("HARNESS_V3_5_DEV_MODE", "1")
    service = build_gateway(tmp_path)
    seeded = asyncio.run(seed_reference_console(service))
    instance_id = seeded["instance"]["workflow_instance_id"]
    patch_id = seeded["patch"]["workflow_patch_id"]
    station_b = seeded["station_b"]
    artifact_id = station_b["output_artifact_ids"][0]
    client = TestClient(create_app(gateway_service=service))

    workflows = client.get(f"/bff/workflows{SCOPE_QUERY}").json()
    versions = client.get(f"/bff/workflows/{seeded['template']['workflow_template_id']}/versions{SCOPE_QUERY}").json()
    instances = client.get(f"/bff/instances{SCOPE_QUERY}").json()
    status = client.get(f"/bff/instances/{instance_id}/status{SCOPE_QUERY}").json()
    board = client.get(f"/bff/instances/{instance_id}/board{SCOPE_QUERY}").json()
    outputs = client.get(f"/bff/instances/{instance_id}/stations/{station_b['station_run_id']}/outputs{SCOPE_QUERY}").json()
    metadata = client.get(f"/bff/instances/{instance_id}/artifacts/{artifact_id}/metadata{SCOPE_QUERY}").json()
    lineage = client.get(f"/bff/instances/{instance_id}/artifacts/{artifact_id}/lineage{SCOPE_QUERY}").json()
    quality = client.get(f"/bff/instances/{instance_id}/quality{SCOPE_QUERY}").json()
    approvals = client.get(f"/bff/instances/{instance_id}/approvals{SCOPE_QUERY}").json()
    context = client.get(f"/bff/instances/{instance_id}/context{SCOPE_QUERY}").json()
    diff = client.get(f"/bff/instances/{instance_id}/patches/{patch_id}/diff{SCOPE_QUERY}").json()

    assert workflows[0]["workflow_template_id"] == seeded["template"]["workflow_template_id"]
    assert versions[0]["workflow_version_id"] == seeded["version"]["workflow_version_id"]
    assert instances[0]["workflow_instance_id"] == instance_id
    assert status["status"] == "waiting_approval"
    assert board["workflow_instance"]["workflow_instance_id"] == instance_id
    assert len(board["stations"]) >= 3
    assert outputs[0]["artifact_id"] == artifact_id
    assert metadata["artifact_id"] == artifact_id
    assert any(item["artifact_id"] == artifact_id for item in lineage["artifacts"])
    assert {
        "source_artifact_id": seeded["runs"][0]["output_artifact_ids"][0],
        "target_artifact_id": artifact_id,
        "relation": "derived_from",
    } in lineage["edges"]
    assert quality[0]["evaluation_id"] == seeded["quality"]["evaluation_id"]
    assert approvals[0]["approval_id"] == seeded["approval"]["approval_id"]
    assert context["business"]["selected_scene"] == "scene_001"
    assert diff["workflow_patch_id"] == patch_id
    assert diff["operation"] == "update_station_prompt"
    assert diff["redacted"] is True
    assert_no_forbidden_text(
        {
            "workflows": workflows,
            "versions": versions,
            "instances": instances,
            "status": status,
            "board": board,
            "outputs": outputs,
            "metadata": metadata,
            "lineage": lineage,
            "quality": quality,
            "approvals": approvals,
            "context": context,
            "diff": diff,
        }
    )

"""V4.0-R auth and tenant boundary preflight tests."""

from __future__ import annotations

import asyncio
import json
from pathlib import Path

from fastapi.testclient import TestClient

from apps.api import create_app

from v4_0_reference_support import OTHER_SCOPE, OTHER_SCOPE_QUERY, SCOPE, SCOPE_QUERY, build_gateway, rpc, seed_reference_console


CONTRACT_PATH = Path("docs/design/V4.0/v4_0_r_production_readiness_preflight_contract.json")


def test_auth_and_tenant_identity_fields_are_registered_as_gaps() -> None:
    contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    assert set(contract["identity_and_tenancy_fields"]) >= {
        "tenant_id",
        "app_id",
        "project_id",
        "workspace_id",
        "user_id",
        "actor_type",
        "actor_id",
        "service_account_id",
        "agent_id",
        "session_id",
    }
    gaps = {gap["category"]: gap for gap in contract["production_gaps"]}
    assert "enterprise identity" in gaps["auth_sso_oauth"]["required_production_state"].lower()
    assert "tenant_id" in gaps["multi_tenant_isolation"]["current_state"]


def test_scope_wrong_instance_and_wrong_resource_guards_still_hold(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("HARNESS_V3_5_DEV_MODE", "1")
    service = build_gateway(tmp_path)
    first = asyncio.run(seed_reference_console(service, template_id="v4_r_scope_a"))
    second = asyncio.run(seed_reference_console(service, template_id="v4_r_scope_b"))
    other_scope = asyncio.run(seed_reference_console(service, template_id="v4_r_scope_c", scope=OTHER_SCOPE))
    client = TestClient(create_app(gateway_service=service))

    first_instance = first["instance"]["workflow_instance_id"]
    second_instance = second["instance"]["workflow_instance_id"]
    other_instance = other_scope["instance"]["workflow_instance_id"]
    artifact_id = first["station_b"]["output_artifact_ids"][0]
    patch_id = first["patch"]["workflow_patch_id"]
    evaluation_id = first["quality"]["evaluation_id"]

    cross_scope = client.get(f"/bff/instances/{first_instance}/board{OTHER_SCOPE_QUERY}")
    wrong_instance_artifact = client.get(f"/bff/instances/{second_instance}/artifacts/{artifact_id}/metadata{SCOPE_QUERY}")
    wrong_instance_quality = client.get(f"/bff/instances/{second_instance}/quality/{evaluation_id}{SCOPE_QUERY}")
    wrong_scope_patch = client.get(f"/bff/instances/{other_instance}/patches/{patch_id}/diff{OTHER_SCOPE_QUERY}")

    sibling = asyncio.run(
        rpc(
            service,
            "workflow.instance.start",
            {"workflow_version_id": first["version"]["workflow_version_id"], "scope": SCOPE},
        )
    )["workflow_instance"]
    same_scope_wrong_resource = client.get(f"/bff/instances/{sibling['workflow_instance_id']}/patches/{patch_id}/diff{SCOPE_QUERY}")

    assert cross_scope.json()["error"]["code"] == "SCOPE_MISMATCH"
    assert wrong_instance_artifact.json()["error"]["code"] == "SCOPE_MISMATCH"
    assert wrong_instance_quality.json()["error"]["code"] == "SCOPE_MISMATCH"
    assert wrong_scope_patch.json()["error"]["code"] == "SCOPE_MISMATCH"
    assert same_scope_wrong_resource.json()["error"]["code"] == "SCOPE_MISMATCH"

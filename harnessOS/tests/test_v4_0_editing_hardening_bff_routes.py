"""V4.0-G governed editing BFF route tests."""

from __future__ import annotations

import asyncio
import json

from fastapi.testclient import TestClient

from apps.api import create_app
from apps.gateway.protocol import RpcRequest

from v4_0_reference_support import SCOPE, SCOPE_QUERY, assert_no_forbidden_text, build_gateway, seed_reference_console


async def _rpc(service, method: str, params: dict | None = None):
    response = await service.handle_rpc(RpcRequest(id=method, method=method, params=params or {}))
    assert response.error is None, response.error
    return response.result


def _propose(service, template_id: str, operation: str, payload: dict, *, metadata: dict | None = None):
    return asyncio.run(
        _rpc(
            service,
            "workflow.patch.propose",
            {
                "workflow_template_id": template_id,
                "patch": {
                    "operation": operation,
                    "payload": payload,
                    "actor_type": "agent",
                    "actor_id": "agent_v4_g",
                    "proposed_by": "agent_v4_g",
                    "metadata": metadata or {},
                },
                "scope": SCOPE,
            },
        )
    )["patch"]


def test_editing_bff_apply_reject_publish_governed_flow(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("HARNESS_V3_5_DEV_MODE", "1")
    service = build_gateway(tmp_path)
    seeded = asyncio.run(seed_reference_console(service, template_id="v4_g_editing_bff"))
    template_id = seeded["template"]["workflow_template_id"]
    instance_id = seeded["instance"]["workflow_instance_id"]
    patch_id = seeded["patch"]["workflow_patch_id"]
    client = TestClient(create_app(gateway_service=service))

    listed = client.get(f"/bff/instances/{instance_id}/patches{SCOPE_QUERY}").json()
    assert listed[0]["workflow_patch_id"] == patch_id
    denied_agent = client.post(
        f"/bff/workflows/{template_id}/patches/{patch_id}/apply{SCOPE_QUERY}",
        json={"workflow_instance_id": instance_id, "user_confirmed": True, "source": "agent"},
    )
    assert denied_agent.json()["error"]["code"] == "WORKFLOW_ACTION_FORBIDDEN"
    missing_confirm = client.post(
        f"/bff/workflows/{template_id}/patches/{patch_id}/apply{SCOPE_QUERY}",
        json={"workflow_instance_id": instance_id, "source": "editing_panel"},
    )
    assert missing_confirm.json()["error"]["code"] == "WORKFLOW_ACTION_FORBIDDEN"

    applied = client.post(
        f"/bff/workflows/{template_id}/patches/{patch_id}/apply{SCOPE_QUERY}",
        json={"workflow_instance_id": instance_id, "user_confirmed": True, "source": "editing_panel"},
    ).json()
    assert applied["operation"] == "workflow.patch.apply"
    assert applied["resource"]["status"] == "applied"
    assert applied["resource"]["resulting_draft_revision"] == seeded["patch"]["base_revision"] + 1
    repeated = client.post(
        f"/bff/workflows/{template_id}/patches/{patch_id}/apply{SCOPE_QUERY}",
        json={"workflow_instance_id": instance_id, "user_confirmed": True, "source": "editing_panel"},
    ).json()
    assert repeated["idempotent"] is True
    assert repeated["resource"]["resulting_draft_revision"] == applied["resource"]["resulting_draft_revision"]

    published = client.post(
        f"/bff/workflows/{template_id}/publish{SCOPE_QUERY}",
        json={
            "version": "2.0.0",
            "expected_draft_revision": applied["resource"]["resulting_draft_revision"],
            "user_confirmed": True,
            "source": "editing_panel",
        },
    ).json()
    assert published["operation"] == "workflow.template.publish"
    assert published["resource"]["version"] == "2.0.0"
    versions = client.get(f"/bff/workflows/{template_id}/versions{SCOPE_QUERY}").json()
    assert {version["version"] for version in versions} >= {"1.0.0", "2.0.0"}
    duplicate = client.post(
        f"/bff/workflows/{template_id}/publish{SCOPE_QUERY}",
        json={
            "version": "2.0.0",
            "expected_draft_revision": applied["resource"]["resulting_draft_revision"],
            "user_confirmed": True,
            "source": "editing_panel",
        },
    )
    assert duplicate.json()["error"]["code"] in {"WORKFLOW_VERSION_CONFLICT", "WORKFLOW_PUBLISHED_IMMUTABLE"}
    assert_no_forbidden_text({"applied": applied, "repeated": repeated, "published": published, "versions": versions})


def test_editing_bff_blocks_high_risk_patch_before_apply(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("HARNESS_V3_5_DEV_MODE", "1")
    service = build_gateway(tmp_path)
    seeded = asyncio.run(seed_reference_console(service, template_id="v4_g_high_risk"))
    template_id = seeded["template"]["workflow_template_id"]
    instance_id = seeded["instance"]["workflow_instance_id"]
    risky = _propose(
        service,
        template_id,
        "update_connector",
        {"station_id": "station_b", "connector_refs": ["dangerous_connector"]},
        metadata={"workflow_instance_id": instance_id, "raw_trace_payload": "secret-token-value"},
    )
    client = TestClient(create_app(gateway_service=service))

    diff = client.get(f"/bff/workflows/{template_id}/patches/{risky['workflow_patch_id']}/diff{SCOPE_QUERY}").json()
    assert diff["requires_approval"] is True
    blocked = client.post(
        f"/bff/workflows/{template_id}/patches/{risky['workflow_patch_id']}/apply{SCOPE_QUERY}",
        json={"workflow_instance_id": instance_id, "user_confirmed": True, "source": "editing_panel"},
    ).json()
    assert blocked["error"]["code"] == "WORKFLOW_ACTION_FORBIDDEN"
    stored = asyncio.run(_rpc(service, "workflow.patch.diff", {"workflow_patch_id": risky["workflow_patch_id"], "scope": SCOPE}))["diff"]
    assert stored["workflow_patch_id"] == risky["workflow_patch_id"]
    assert_no_forbidden_text({"diff": diff, "blocked": blocked})


def test_editing_bff_reject_idempotency_and_conflicts(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("HARNESS_V3_5_DEV_MODE", "1")
    service = build_gateway(tmp_path)
    seeded = asyncio.run(seed_reference_console(service, template_id="v4_g_reject"))
    template_id = seeded["template"]["workflow_template_id"]
    instance_id = seeded["instance"]["workflow_instance_id"]
    patch = _propose(
        service,
        template_id,
        "update_station_prompt",
        {"station_id": "station_b", "prompt_ref": "reject.prompt.v1"},
        metadata={"workflow_instance_id": instance_id},
    )
    client = TestClient(create_app(gateway_service=service))

    rejected = client.post(
        f"/bff/workflows/{template_id}/patches/{patch['workflow_patch_id']}/reject{SCOPE_QUERY}",
        json={"workflow_instance_id": instance_id, "reason": "not now", "user_confirmed": True, "source": "editing_panel"},
    ).json()
    assert rejected["resource"]["status"] == "rejected"
    repeated = client.post(
        f"/bff/workflows/{template_id}/patches/{patch['workflow_patch_id']}/reject{SCOPE_QUERY}",
        json={"workflow_instance_id": instance_id, "user_confirmed": True, "source": "editing_panel"},
    ).json()
    assert repeated["idempotent"] is True
    apply_rejected = client.post(
        f"/bff/workflows/{template_id}/patches/{patch['workflow_patch_id']}/apply{SCOPE_QUERY}",
        json={"workflow_instance_id": instance_id, "user_confirmed": True, "source": "editing_panel"},
    )
    assert apply_rejected.json()["error"]["code"] == "WORKFLOW_PATCH_CONFLICT"


def test_editing_bff_ownership_and_redaction(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("HARNESS_V3_5_DEV_MODE", "1")
    service = build_gateway(tmp_path)
    first = asyncio.run(seed_reference_console(service, template_id="v4_g_owner_a"))
    second = asyncio.run(seed_reference_console(service, template_id="v4_g_owner_b"))
    client = TestClient(create_app(gateway_service=service))
    first_patch = first["patch"]["workflow_patch_id"]
    wrong_template = second["template"]["workflow_template_id"]
    wrong_instance = second["instance"]["workflow_instance_id"]

    wrong_template_response = client.post(
        f"/bff/workflows/{wrong_template}/patches/{first_patch}/apply{SCOPE_QUERY}",
        json={"workflow_instance_id": first["instance"]["workflow_instance_id"], "user_confirmed": True, "source": "editing_panel"},
    )
    assert wrong_template_response.json()["error"]["code"] == "SCOPE_MISMATCH"
    wrong_instance_response = client.post(
        f"/bff/workflows/{first['template']['workflow_template_id']}/patches/{first_patch}/apply{SCOPE_QUERY}",
        json={"workflow_instance_id": wrong_instance, "user_confirmed": True, "source": "editing_panel"},
    )
    assert wrong_instance_response.json()["error"]["code"] == "SCOPE_MISMATCH"
    raw = json.dumps({"a": wrong_template_response.json(), "b": wrong_instance_response.json()}, ensure_ascii=False)
    assert "secret-token-value" not in raw

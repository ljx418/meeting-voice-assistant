"""V4.0-M operation evidence BFF route tests."""

from __future__ import annotations

import asyncio

from fastapi.testclient import TestClient

from apps.api import create_app

from v4_0_reference_support import SCOPE_QUERY, assert_no_forbidden_text, build_gateway, seed_reference_console


def _patch_handoff(client: TestClient, instance_id: str, patch_id: str) -> dict:
    proposal = client.post(
        f"/bff/instances/{instance_id}/agent/action-proposals{SCOPE_QUERY}",
        json={"intent_type": "open_editing_panel", "workflow_patch_id": patch_id, "target_panel": "editing"},
    ).json()
    return client.post(
        f"/bff/instances/{instance_id}/agent/action-proposals/{proposal['proposal_id']}/handoff{SCOPE_QUERY}",
        json={"target_panel": "editing_panel", "workflow_patch_id": patch_id},
    ).json()


def test_patch_apply_creates_operation_evidence_chain(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("HARNESS_V3_5_DEV_MODE", "1")
    service = build_gateway(tmp_path)
    seeded = asyncio.run(seed_reference_console(service, template_id="v4_m_evidence_apply"))
    client = TestClient(create_app(gateway_service=service))
    instance_id = seeded["instance"]["workflow_instance_id"]
    template_id = seeded["template"]["workflow_template_id"]
    patch_id = seeded["patch"]["workflow_patch_id"]
    handoff = _patch_handoff(client, instance_id, patch_id)

    applied = client.post(
        f"/bff/workflows/{template_id}/patches/{patch_id}/apply{SCOPE_QUERY}",
        json={
            "workflow_instance_id": instance_id,
            "user_confirmed": True,
            "source": "editing_panel",
            "proposal_id": handoff["proposal_id"],
            "handoff_id": handoff["handoff_id"],
        },
    ).json()
    assert applied["operation"] == "workflow.patch.apply"
    assert applied["evidence"]["status"] == "succeeded"
    assert applied["evidence"]["runtime_result_ref"]["type"] == "workflow_patch"

    evidence = client.get(f"/bff/instances/{instance_id}/agent/operation-evidence{SCOPE_QUERY}").json()
    assert [item["operation"] for item in evidence] == ["workflow.patch.apply"]
    assert evidence[0]["proposal_id"] == handoff["proposal_id"]
    assert evidence[0]["handoff_id"] == handoff["handoff_id"]
    assert evidence[0]["user_confirmed"] is True

    review = client.get(f"/bff/instances/{instance_id}/agent/governance-review{SCOPE_QUERY}").json()
    assert review["summary"]["evidence_count"] == 1
    assert review["summary"]["status_counts"]["succeeded"] == 1
    assert review["operation_evidence"][0]["evidence_id"] == evidence[0]["evidence_id"]
    assert_no_forbidden_text({"applied": applied, "evidence": evidence, "review": review})


def test_publish_creates_operation_evidence_chain(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("HARNESS_V3_5_DEV_MODE", "1")
    service = build_gateway(tmp_path)
    seeded = asyncio.run(seed_reference_console(service, template_id="v4_m_evidence_publish"))
    client = TestClient(create_app(gateway_service=service))
    instance_id = seeded["instance"]["workflow_instance_id"]
    template_id = seeded["template"]["workflow_template_id"]
    patch_id = seeded["patch"]["workflow_patch_id"]
    handoff = _patch_handoff(client, instance_id, patch_id)

    applied = client.post(
        f"/bff/workflows/{template_id}/patches/{patch_id}/apply{SCOPE_QUERY}",
        json={
            "workflow_instance_id": instance_id,
            "user_confirmed": True,
            "source": "editing_panel",
            "proposal_id": handoff["proposal_id"],
            "handoff_id": handoff["handoff_id"],
        },
    ).json()
    published = client.post(
        f"/bff/workflows/{template_id}/publish{SCOPE_QUERY}",
        json={
            "workflow_instance_id": instance_id,
            "version": "2.0.0",
            "expected_draft_revision": applied["resource"]["resulting_draft_revision"],
            "user_confirmed": True,
            "source": "editing_panel",
            "correlation_id": "corr_publish",
        },
    ).json()

    assert published["operation"] == "workflow.template.publish"
    assert published["evidence"]["status"] == "succeeded"
    assert published["evidence"]["correlation_id"] == "corr_publish"
    assert published["evidence"]["runtime_result_ref"]["type"] == "workflow_version"

    evidence = client.get(f"/bff/instances/{instance_id}/agent/operation-evidence{SCOPE_QUERY}").json()
    assert {"workflow.patch.apply", "workflow.template.publish"} == {item["operation"] for item in evidence}
    assert_no_forbidden_text({"published": published, "evidence": evidence})


def test_evidence_routes_are_read_only_and_do_not_execute_mutation(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("HARNESS_V3_5_DEV_MODE", "1")
    service = build_gateway(tmp_path)
    seeded = asyncio.run(seed_reference_console(service, template_id="v4_m_evidence_read_only"))
    client = TestClient(create_app(gateway_service=service))
    instance_id = seeded["instance"]["workflow_instance_id"]
    patch_id = seeded["patch"]["workflow_patch_id"]

    before = client.get(f"/bff/instances/{instance_id}/patches/{patch_id}/diff{SCOPE_QUERY}").json()
    assert before["workflow_patch_id"] == patch_id
    assert client.get(f"/bff/instances/{instance_id}/agent/operation-evidence{SCOPE_QUERY}").json() == []
    assert client.get(f"/bff/instances/{instance_id}/agent/governance-review{SCOPE_QUERY}").json()["summary"]["evidence_count"] == 0
    after = client.get(f"/bff/instances/{instance_id}/patches/{patch_id}/diff{SCOPE_QUERY}").json()
    assert after["workflow_patch_id"] == patch_id

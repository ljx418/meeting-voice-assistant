"""V4.0-E reference console DTO redaction and no-bypass tests."""

from __future__ import annotations

import asyncio
from pathlib import Path

from fastapi.testclient import TestClient

from apps.api import create_app

from v4_0_reference_support import SCOPE_QUERY, assert_no_forbidden_text, build_gateway, seed_reference_console


APP_ROOT = Path(__file__).resolve().parents[1] / "apps" / "workflow-console"


def test_reference_console_dto_schema_snapshots_are_redacted(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("HARNESS_V3_5_DEV_MODE", "1")
    monkeypatch.setenv("HARNESS_CAPABILITY_TOKEN_SECRET", "v4-e-redaction")
    service = build_gateway(tmp_path)
    seeded = asyncio.run(seed_reference_console(service))
    instance_id = seeded["instance"]["workflow_instance_id"]
    patch_id = seeded["patch"]["workflow_patch_id"]
    client = TestClient(create_app(gateway_service=service))

    board = client.get(f"/bff/instances/{instance_id}/board{SCOPE_QUERY}").json()
    status = client.get(f"/bff/instances/{instance_id}/status{SCOPE_QUERY}").json()
    approval = client.get(f"/bff/instances/{instance_id}/approvals{SCOPE_QUERY}").json()[0]
    quality = client.get(f"/bff/instances/{instance_id}/quality{SCOPE_QUERY}").json()[0]
    context = client.get(f"/bff/instances/{instance_id}/context{SCOPE_QUERY}").json()
    patch = client.get(f"/bff/instances/{instance_id}/patches/{patch_id}/diff{SCOPE_QUERY}").json()
    event = client.get(f"/bff/events/subscribe{SCOPE_QUERY}&channels=business&workflow_instance_id={instance_id}").text

    assert set(status) == {
        "workflow_instance_id",
        "status",
        "current_station_ids",
        "station_counts",
        "job_counts",
        "artifact_count",
        "quality_count",
    }
    assert {"approval_id", "workflow_instance_id", "station_run_id", "status", "active"} <= set(approval)
    assert {"evaluation_id", "workflow_instance_id", "station_run_id", "artifact_id", "rubric_id", "score", "status"} <= set(quality)
    assert set(context) >= {"workflow_instance_id", "revision", "business"}
    assert set(patch) == {
        "workflow_patch_id",
        "workflow_draft_id",
        "base_revision",
        "operation",
        "target",
        "before_summary",
        "after_summary",
        "risk_flags",
        "requires_approval",
        "redacted",
    }
    assert board["workflow_instance"]["workflow_instance_id"] == instance_id
    assert_no_forbidden_text({"board": board, "status": status, "approval": approval, "quality": quality, "context": context, "patch": patch, "event": event})


def test_reference_console_frontend_source_avoids_forbidden_runtime_paths() -> None:
    source = "\n".join(
        path.read_text(encoding="utf-8", errors="ignore")
        for path in (APP_ROOT / "src").rglob("*.ts*")
        if "__tests__" not in path.parts
    )
    for forbidden in (
        "/v1/rpc",
        "/v1/events/subscribe",
        "artifact.read(",
        "quality.evaluation.create",
        "quality.evaluation.attach",
        'method: "workflow.patch.apply"',
        'method: "workflow.patch.reject"',
        'method: "workflow.template.publish"',
        "approval.approve(",
        "approval.reject(",
        "/approval.approve",
        "/approval.reject",
        "import core",
        "apps.gateway",
        "WorkflowStore",
        "ArtifactRegistry",
        "ApprovalStore",
    ):
        assert forbidden not in source

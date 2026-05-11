"""V3.5-MVP end-to-end SDK + BFF + EventBridge smoke tests."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[1]
SDK_PATH = ROOT / "sdk/python"
if str(SDK_PATH) not in sys.path:
    sys.path.insert(0, str(SDK_PATH))

from harnessos_client import HarnessOSClient, Scope
from templates.bff.fastapi_minimal.app import create_app as create_bff_app

from apps.api import create_app as create_harness_app
from apps.gateway.approvals import ApprovalStore
from apps.gateway.artifacts import ArtifactRegistry
from apps.gateway.runtime import GatewayRuntimePool
from apps.gateway.service import GatewayService
from apps.gateway.storage import GatewaySessionStore
from apps.gateway.traces import TraceStore
from core.apps.profiles import AppProfile
from core.apps.scope import ScopeContext
from core.protocol.auth import issue_capability_token
from core.stores.sqlite import CoreSQLiteStore


SECRET = "phase-mvp-e2e-secret"
LOCAL_ORIGIN = "http://localhost:5173"
REFERENCE_SCOPE = Scope(app_id="reference_app", project_id="demo", workspace_id="local")


class AsgiJsonRpcTransport:
    def __init__(self, client: TestClient) -> None:
        self.client = client

    def request(self, payload: dict[str, Any], *, headers: dict[str, str], timeout: float) -> dict[str, Any]:
        merged_headers = {"Origin": LOCAL_ORIGIN, **headers}
        return self.client.post("/v1/rpc", json=payload, headers=merged_headers).json()


class UpstreamResponse:
    def __init__(self, text: str) -> None:
        self.closed = False
        self._payload = text.encode("utf-8")

    def __iter__(self):
        yield self._payload

    def close(self) -> None:
        self.closed = True


def _reference_profile() -> AppProfile:
    return AppProfile(
        app_id="reference_app",
        display_name="Reference App",
        domain="reference",
        default_pack="video_studio",
        connector_refs=("remote_comfyui",),
        default_project_id="demo",
        default_workspace_id="local",
        allowed_origins=(LOCAL_ORIGIN,),
        default_capabilities=(
            "sessions",
            "turns",
            "events",
            "artifacts",
            "artifact_lineage",
            "jobs",
            "approvals",
            "connectors.read",
            "packs.read",
            "rpc",
        ),
    )


def _environment(monkeypatch, tmp_path: Path):
    monkeypatch.setenv("HARNESS_CAPABILITY_TOKEN_SECRET", SECRET)
    monkeypatch.delenv("HARNESS_V3_5_DEV_MODE", raising=False)
    runtime = GatewayRuntimePool(
        store=GatewaySessionStore(tmp_path / "sessions"),
        artifact_registry=ArtifactRegistry(tmp_path / "artifacts", allowed_roots=[tmp_path]),
        core_store=CoreSQLiteStore(tmp_path / "core.sqlite3"),
    )
    gateway = GatewayService(
        runtime_pool=runtime,
        trace_store=TraceStore(tmp_path / "traces"),
        approval_store=ApprovalStore(tmp_path / "approvals"),
    )
    profile = _reference_profile()
    gateway.app_registry.register(profile)
    token = issue_capability_token(
        app_profile=profile,
        capabilities=profile.default_capabilities,
        allowed_origins=(LOCAL_ORIGIN,),
        secret=SECRET,
    )
    harness_client = TestClient(create_harness_app(gateway_service=gateway))
    sdk = HarnessOSClient(
        base_url="http://testserver",
        capability_token=token,
        scope=REFERENCE_SCOPE,
        transport=AsgiJsonRpcTransport(harness_client),
    )
    upstream_responses: list[UpstreamResponse] = []

    def open_upstream(url: str) -> UpstreamResponse:
        parsed = urlsplit(url)
        path = parsed.path or "/v1/events/subscribe"
        query = parsed.query
        separator = "&" if query else ""
        target = f"{path}?{query}{separator}follow=0"
        response = harness_client.get(target)
        upstream = UpstreamResponse(response.text)
        upstream_responses.append(upstream)
        return upstream

    bff = TestClient(
        create_bff_app(
            config={"identity_scope": REFERENCE_SCOPE.to_dict()},
            sdk_client=sdk,
            upstream_opener=open_upstream,
        )
    )
    return gateway, bff, upstream_responses


def test_v3_5_mvp_sdk_bff_eventbridge_e2e(monkeypatch, tmp_path: Path) -> None:
    gateway, bff, upstream_responses = _environment(monkeypatch, tmp_path)

    session = bff.post("/bff/session/start", json={"model": "demo"})
    assert session.status_code == 200
    session_payload = session.json()
    assert session_payload["session_id"]

    turn = bff.post("/bff/turn/start", json={"session_id": session_payload["session_id"], "input": "hello"})
    assert turn.status_code == 200
    assert turn.json()["session_id"] == session_payload["session_id"]

    artifact = bff.post(
        "/bff/rpc",
        json={
            "method": "artifact.register_external",
            "params": {
                "kind": "note",
                "external_asset_uri": "file:///tmp/reference-note.txt",
                "session_id": session_payload["session_id"],
            },
        },
    )
    assert artifact.status_code == 200
    artifact_id = artifact.json()["artifact"]["artifact_id"]

    job = gateway.core_service.create_job(
        workflow_id="reference.workflow",
        session_id=session_payload["session_id"],
        scope=ScopeContext(app_id="reference_app", project_id="demo", workspace_id="local"),
    )
    gateway.core_service.update_job(job_id=job.job_id, status="completed", progress=1.0, artifact_ids=[artifact_id])

    approval = gateway.approval_store.request(
        action="publish",
        request_summary="Publish reference result",
        app_id="reference_app",
        project_id="demo",
        workspace_id="local",
    )
    approved = bff.post(
        "/bff/approval/respond",
        json={"approval_id": approval["approval_id"], "decision": "approve", "reason": "ok"},
    )
    assert approved.status_code == 200
    assert approved.json()["status"] == "approved"

    events = bff.get("/bff/events/subscribe?channels=chat,job,artifact,approval")
    assert events.status_code == 200
    assert events.headers["content-type"].startswith("text/event-stream")
    assert "event: artifact.registered" in events.text
    assert "event: job.completed" in events.text
    assert "event: approval.approved" in events.text
    assert "subscription_token" not in events.text
    assert upstream_responses and upstream_responses[-1].closed is True

    artifacts = bff.post("/bff/rpc", json={"method": "artifact.list", "params": {}})
    assert artifacts.status_code == 200
    assert artifacts.json()["count"] == 1

    jobs = bff.post("/bff/rpc", json={"method": "job.list", "params": {}})
    assert jobs.status_code == 200
    assert any(item["job_id"] == job.job_id for item in jobs.json()["jobs"])

    packs = bff.post("/bff/rpc", json={"method": "pack.list", "params": {}})
    assert packs.status_code == 200
    assert packs.json()["count"] >= 1

    connector = bff.post("/bff/rpc", json={"method": "connector.health", "params": {"connector_id": "remote_comfyui"}})
    assert connector.status_code == 200
    assert connector.json()["connector"]["connector_id"] == "remote_comfyui"

    denied = bff.post("/bff/rpc", json={"method": "meeting.process_recording", "params": {}})
    assert denied.status_code == 403
    assert denied.json()["error"]["code"] == "METHOD_FORBIDDEN"

    isolated = bff.post("/bff/rpc", json={"method": "artifact.list", "params": {"scope": {"app_id": "knowledge"}}})
    assert isolated.status_code == 403
    assert isolated.json()["error"]["code"] == "SCOPE_MISMATCH"


def test_v3_5_mvp_tokens_are_redacted_from_bff_responses_and_records(monkeypatch, tmp_path: Path) -> None:
    gateway, bff, _ = _environment(monkeypatch, tmp_path)
    response = bff.post(
        "/bff/rpc",
        json={
            "method": "session.start",
            "params": {"debug": "Authorization Bearer cap-secret-token subscription_token=sub-secret"},
        },
    )
    assert "cap-secret-token" not in response.text
    assert "sub-secret" not in response.text

    job = gateway.core_service.create_job(
        workflow_id="reference.failure",
        scope=ScopeContext(app_id="reference_app", project_id="demo", workspace_id="local"),
    )
    gateway.core_service.update_job(
        job_id=job.job_id,
        status="failed",
        failure_context={"message": "Authorization Bearer cap-secret-token subscription_token=sub-secret"},
    )
    saved = gateway.core_service.get_job(job.job_id).model_dump(mode="json")
    assert "cap-secret-token" not in json.dumps(saved)
    assert "sub-secret" not in json.dumps(saved)

    trace_text = json.dumps(
        gateway.core_service.list_trace_records(app_id="reference_app", project_id="demo", workspace_id="local"),
        default=str,
    )
    assert "cap-secret-token" not in trace_text
    assert "sub-secret" not in trace_text

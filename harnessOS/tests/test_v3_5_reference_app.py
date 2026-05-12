"""V3.5-I platform-neutral reference app tests."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Iterable

from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[1]
SDK_PATH = ROOT / "sdk/python"
if str(SDK_PATH) not in sys.path:
    sys.path.insert(0, str(SDK_PATH))

from harnessos_client import EventSubscription
from apps.gateway.connectors import ConnectorRegistry
from core.packs import PackRegistry
from core.protocol.version import HARNESSOS_VERSION
from core.services import CoreAppService
from core.stores import CoreSQLiteStore
from templates.bff.fastapi.app import create_app


REFERENCE_APP = ROOT / "examples" / "reference_app"
FRONTEND_SRC = REFERENCE_APP / "frontend" / "src"
DOCS = ROOT / "docs" / "design" / "V3.5"

BASE_CONFIG = {
    "demo_identity_mode": True,
    "harnessos_capability_token": "server-side-placeholder-token",
    "identity_scope": {"app_id": "reference_app", "project_id": "demo", "workspace_id": "local"},
    "demo_capabilities": [
        "sessions",
        "turns",
        "events",
        "artifacts.read",
        "artifacts.write",
        "jobs",
        "approvals",
        "packs.read",
        "connectors.read",
    ],
}


class FakeSdkClient:
    def __init__(self) -> None:
        self.sessions: dict[tuple[str, str, str], list[dict[str, Any]]] = {}
        self.artifacts: dict[tuple[str, str, str], list[dict[str, Any]]] = {}
        self.jobs: dict[tuple[str, str, str], list[dict[str, Any]]] = {}
        self.approvals: dict[tuple[str, str, str], dict[str, dict[str, Any]]] = {}
        self.last_subscription_scope: dict[str, Any] | None = None
        self.calls: list[tuple[str, dict[str, Any]]] = []

    def rpc(self, method: str, params: dict[str, Any]) -> dict[str, Any]:
        self.calls.append(("rpc", {"method": method, "params": params}))
        return {"method": method, "params": params}

    def session_start(self, *, model: str | None = None, scope: Any = None) -> dict[str, Any]:
        scope_dict = _scope(scope)
        key = _scope_key(scope_dict)
        item = {
            "session_id": f"sess_{scope_dict['project_id']}",
            "model": model,
            "scope": scope_dict,
            "trace_id": f"trace_{scope_dict['project_id']}",
        }
        self.sessions.setdefault(key, []).append(item)
        self.calls.append(("session_start", item))
        return item

    def turn_start(self, *, input: str, session_id: str | None = None, domain: str | None = None, scope: Any = None) -> dict[str, Any]:
        scope_dict = _scope(scope)
        result = {
            "turn_id": f"turn_{scope_dict['project_id']}",
            "session_id": session_id,
            "input": input,
            "domain": domain,
            "scope": scope_dict,
            "trace_id": f"trace_turn_{scope_dict['project_id']}",
        }
        self.calls.append(("turn_start", result))
        return result

    def events_subscribe(self, *, channels: list[str] | None = None, scope: Any = None) -> EventSubscription:
        scope_dict = _scope(scope)
        self.last_subscription_scope = scope_dict
        selected_channels = tuple(channels or ("chat", "job", "artifact", "approval"))
        self.calls.append(("events_subscribe", {"channels": list(selected_channels), "scope": scope_dict}))
        return EventSubscription(
            subscription_id=f"sub_{scope_dict['project_id']}",
            transport="eventsource",
            eventsource_url=f"http://upstream.local/v1/events/subscribe?subscription_token=upstream-secret-{scope_dict['project_id']}",
            subscription_token=f"upstream-secret-{scope_dict['project_id']}",
            replay_cursor=f"cursor_{scope_dict['project_id']}",
            expires_at="2026-05-12T12:00:00Z",
            allowed_channels=selected_channels,
        )

    def artifact_register_external(self, *, kind: str, external_asset_uri: str, scope: Any = None) -> dict[str, Any]:
        scope_dict = _scope(scope)
        key = _scope_key(scope_dict)
        artifact = {
            "artifact_id": f"art_{scope_dict['project_id']}_{len(self.artifacts.get(key, [])) + 1}",
            "kind": kind,
            "external_asset_uri": external_asset_uri,
            "metadata": {"trace_id": f"trace_art_{scope_dict['project_id']}"},
            "scope": scope_dict,
        }
        self.artifacts.setdefault(key, []).append(artifact)
        return artifact

    def artifact_list(self, *, session_id: str | None = None, kind: str | None = None, scope: Any = None) -> dict[str, Any]:
        items = list(self.artifacts.get(_scope_key(_scope(scope)), []))
        if kind:
            items = [item for item in items if item["kind"] == kind]
        return {"artifacts": items, "count": len(items)}

    def artifact_read_metadata(self, *, artifact_id: str, scope: Any = None) -> dict[str, Any]:
        for artifact in self.artifacts.get(_scope_key(_scope(scope)), []):
            if artifact["artifact_id"] == artifact_id:
                return {"artifact": artifact, "metadata": artifact.get("metadata", {})}
        return {"artifact": None, "metadata": {}}

    def artifact_lineage(self, *, artifact_id: str | None = None, session_id: str | None = None, scope: Any = None) -> dict[str, Any]:
        artifacts = self.artifacts.get(_scope_key(_scope(scope)), [])
        return {"artifacts": artifacts, "edges": [], "roots": [artifact_id] if artifact_id else [], "leaves": [artifact_id] if artifact_id else [], "count": len(artifacts)}

    def job_list(self, *, session_id: str | None = None, status: str | None = None, scope: Any = None) -> dict[str, Any]:
        scope_dict = _scope(scope)
        key = _scope_key(scope_dict)
        self.jobs.setdefault(
            key,
            [
                {
                    "job_id": f"job_{scope_dict['project_id']}",
                    "status": "completed",
                    "scope": scope_dict,
                    "trace_id": f"trace_job_{scope_dict['project_id']}",
                }
            ],
        )
        items = list(self.jobs[key])
        if status:
            items = [item for item in items if item["status"] == status]
        return {"jobs": items, "count": len(items)}

    def job_get(self, *, job_id: str, scope: Any = None) -> dict[str, Any]:
        for job in self.job_list(scope=scope)["jobs"]:
            if job["job_id"] == job_id:
                return {"job": job}
        return {"job": None}

    def approval_respond(self, *, approval_id: str, decision: str, reason: str | None = None, scope: Any = None) -> dict[str, Any]:
        scope_dict = _scope(scope)
        key = _scope_key(scope_dict)
        approvals = self.approvals.setdefault(
            key,
            {
                "appr_reference": {
                    "approval_id": "appr_reference",
                    "status": "pending",
                    "scope": scope_dict,
                    "trace_id": f"trace_approval_{scope_dict['project_id']}",
                }
            },
        )
        approval = approvals.setdefault(
            approval_id,
            {"approval_id": approval_id, "status": "pending", "scope": scope_dict, "trace_id": f"trace_approval_{scope_dict['project_id']}"},
        )
        approval["status"] = "approved" if decision == "approve" else "rejected"
        approval["reason"] = reason
        return {"approval": approval, "status": approval["status"], "trace_id": approval["trace_id"], "idempotent": False}

    def connector_health(self, *, connector_id: str) -> dict[str, Any]:
        return {"connector_id": connector_id, "health": {"status": "available"}}

    def pack_list(self) -> dict[str, Any]:
        return {"packs": [{"name": "reference_app_pack", "domain": "reference_app"}], "count": 1}

    def pack_get(self, *, app_id: str | None = None, pack_id: str | None = None) -> dict[str, Any]:
        return {"pack": {"name": pack_id or "reference_app_pack", "app_id": app_id or "reference_app"}}


class ScopeAwareUpstream:
    def __init__(self, sdk: FakeSdkClient) -> None:
        self.sdk = sdk
        self.opened_urls: list[str] = []
        self.opened_streams: list[FakeSseStream] = []

    def __call__(self, url: str) -> "FakeSseStream":
        self.opened_urls.append(url)
        scope = self.sdk.last_subscription_scope or {"app_id": "reference_app", "project_id": "demo", "workspace_id": "local"}
        project_id = str(scope.get("project_id") or "demo")
        stream = FakeSseStream(
            [
                _sse(
                    event_id=f"cursor_approval_{project_id}",
                    event="approval.required",
                    data={
                        "event_id": f"evt_approval_{project_id}",
                        "type": "approval.required",
                        "channel": "approval",
                        "cursor": f"cursor_approval_{project_id}",
                        "scope": scope,
                        "approval_id": "appr_reference",
                        "trace_id": f"trace_approval_{project_id}",
                        "data": {"prompt": "Approve reference action?"},
                    },
                )
            ]
        )
        self.opened_streams.append(stream)
        return stream


class FakeSseStream:
    def __init__(self, frames: list[bytes]) -> None:
        self.frames = frames
        self.closed = False

    def __iter__(self) -> Iterable[bytes]:
        return iter(self.frames)

    def close(self) -> None:
        self.closed = True


def test_reference_app_fixture_is_platform_neutral() -> None:
    banned = ("meeting", "knowledge", "data_service", "voice_service", "funasr")
    for path in REFERENCE_APP.rglob("*"):
        if "node_modules" in path.parts:
            continue
        if path.is_file() and path.name != ".gitkeep":
            text = path.read_text(encoding="utf-8").lower()
            for value in banned:
                assert value not in text, f"{path}: {value}"


def test_frontend_uses_bff_only_and_no_direct_core_or_event_rpc_calls() -> None:
    source = "\n".join(path.read_text(encoding="utf-8") for path in FRONTEND_SRC.rglob("*") if path.is_file())

    assert "/bff/events/subscribe" in source
    assert "/bff/sessions" in source
    assert "/bff/turns" in source
    assert "/bff/embed/bootstrap" in source
    assert "/bff/approvals/" in source
    for forbidden in ("/v1/rpc", "/v1/events/subscribe", "/bff/rpc", "HARNESSOS_BASE_URL", "approval.approve", "approval.reject"):
        assert forbidden not in source


def test_reference_pack_and_connector_are_discovered_only_by_external_paths(tmp_path: Path) -> None:
    pack_registry = PackRegistry.load_from_paths([REFERENCE_APP])
    pack = pack_registry.get_pack("reference_app_pack")

    assert pack is not None
    assert pack.domain == "reference_app"
    assert pack.manifest_schema_version == "1"
    assert pack.min_harnessos_version == HARNESSOS_VERSION
    assembly = pack_registry.evaluate_assembly(
        "reference_app_pack",
        supported_workflows={"reference_app.workflow"},
        available_connectors={"reference_app_connector"},
        available_connector_capabilities={"reference_app_connector": {"capabilities": {"reference.run"}, "tools": {"reference_tool"}}},
        available_policy_bundles={"reference_app.default"},
    )
    assert assembly.status == "assembled"

    connector_registry = ConnectorRegistry(
        core_service=CoreAppService(CoreSQLiteStore(tmp_path / "core.sqlite3")),
        connector_descriptor_paths=[REFERENCE_APP / "connector"],
    )
    health = connector_registry.refresh_health("reference_app_connector")
    assert health["health"]["status"] == "available"
    assert health["connector"]["execution_mode"] == "stub"


def test_reference_ids_are_not_hardcoded_in_core_or_gateway() -> None:
    for path in [
        ROOT / "core" / "packs" / "registry.py",
        ROOT / "apps" / "gateway" / "connectors.py",
        ROOT / "apps" / "gateway" / "service.py",
    ]:
        text = path.read_text(encoding="utf-8")
        assert "reference_app_pack" not in text
        assert "reference_app_connector" not in text


def test_bff_sdk_hooks_embed_events_and_approval_flow() -> None:
    sdk = FakeSdkClient()
    upstream = ScopeAwareUpstream(sdk)
    client = TestClient(create_app(config=BASE_CONFIG, sdk_client=sdk, upstream_opener=upstream))

    assert client.post("/bff/sessions", json={"model": "demo"}).json()["session_id"] == "sess_demo"
    assert client.post("/bff/turns", json={"input": "hello"}).json()["turn_id"] == "turn_demo"

    bootstrap = client.get("/bff/embed/bootstrap?channels=chat,job,artifact,approval&create_session=true").json()
    raw_bootstrap = json.dumps(bootstrap)
    assert bootstrap["embedDefinition"]["allowedEventChannels"] == ["chat", "job", "artifact", "approval"]
    assert "trace" not in bootstrap["embedDefinition"]["allowedEventChannels"]
    assert "approval.respond" in bootstrap["embedDefinition"]["allowedActions"]
    assert "approval.approve" not in bootstrap["embedDefinition"]["allowedActions"]
    assert bootstrap["eventSubscription"]["eventsourceUrl"].startswith("/bff/events/subscribe")
    assert "subscription_token" not in raw_bootstrap
    assert "upstream-secret" not in raw_bootstrap

    event_response = client.get("/bff/events/subscribe?channels=approval")
    event_text = event_response.text
    assert event_response.status_code == 200
    assert "event: approval.required" in event_text
    assert "appr_reference" in event_text
    assert "upstream-secret" not in event_text

    approval = client.post("/bff/approvals/appr_reference/respond", json={"decision": "approve", "reason": "reference app smoke"}).json()
    assert approval["status"] == "approved"
    assert approval["approval"]["approval_id"] == "appr_reference"

    assert client.get("/bff/artifacts").json()["count"] == 0
    assert client.get("/bff/jobs").json()["jobs"][0]["job_id"] == "job_demo"
    assert client.get("/bff/packs").json()["packs"][0]["name"] == "reference_app_pack"
    assert client.get("/bff/connectors/reference_app_connector/health").json()["connector_id"] == "reference_app_connector"

    denied = client.post("/bff/rpc", json={"method": "events.subscribe", "params": {"channels": ["approval"]}})
    assert denied.status_code == 403
    assert denied.json()["error"]["code"] == "METHOD_FORBIDDEN"


def test_scope_isolation_for_artifacts_jobs_approvals_and_events() -> None:
    sdk = FakeSdkClient()
    upstream = ScopeAwareUpstream(sdk)
    demo = TestClient(create_app(config=BASE_CONFIG, sdk_client=sdk, upstream_opener=upstream))
    other_config = {
        **BASE_CONFIG,
        "identity_scope": {"app_id": "reference_app", "project_id": "other", "workspace_id": "local"},
    }
    other = TestClient(create_app(config=other_config, sdk_client=sdk, upstream_opener=upstream))

    demo_artifact = demo.post("/bff/artifacts/external", json={"kind": "result", "external_asset_uri": "memory://demo"}).json()
    other_artifact = other.post("/bff/artifacts/external", json={"kind": "result", "external_asset_uri": "memory://other"}).json()

    assert demo_artifact["artifact_id"].startswith("art_demo")
    assert other_artifact["artifact_id"].startswith("art_other")
    assert demo.get("/bff/artifacts").json()["artifacts"][0]["artifact_id"] == demo_artifact["artifact_id"]
    assert other.get("/bff/artifacts").json()["artifacts"][0]["artifact_id"] == other_artifact["artifact_id"]
    assert demo.get("/bff/jobs").json()["jobs"][0]["job_id"] == "job_demo"
    assert other.get("/bff/jobs").json()["jobs"][0]["job_id"] == "job_other"

    demo_event = demo.get("/bff/events/subscribe?channels=approval").text
    other_event = other.get("/bff/events/subscribe?channels=approval").text
    assert '"project_id": "demo"' in demo_event
    assert '"project_id": "other"' not in demo_event
    assert '"project_id": "other"' in other_event
    assert '"project_id": "demo"' not in other_event

    conflict = demo.post("/bff/sessions?project_id=other", json={})
    assert conflict.status_code == 403
    assert conflict.json()["error"]["code"] == "SCOPE_MISMATCH"


def test_embed_and_trace_contract_are_visible_without_secret_leakage() -> None:
    source = (FRONTEND_SRC / "views" / "TracePanel.tsx").read_text(encoding="utf-8")
    assert "trace_id" in source
    assert "trace_count" in source
    assert "redacted_summary" in source

    sdk = FakeSdkClient()
    client = TestClient(create_app(config=BASE_CONFIG, sdk_client=sdk, upstream_opener=ScopeAwareUpstream(sdk)))
    payload = client.get("/bff/embed/bootstrap?channels=chat,approval").json()
    raw = json.dumps(payload)
    assert "capability_token" not in raw
    assert "subscription_token" not in raw
    assert "upstream-secret" not in raw
    assert payload["eventSubscription"]["eventsourceUrl"].startswith("/bff/events/subscribe")


def test_docs_mark_reference_app_phase_and_dev_local_completion() -> None:
    for name in [
        "00_README.md",
        "v3_5_current_gap_analysis.md",
        "v3_5_acceptance_plan.md",
        "v3_5_development_plan_application_adaptation_layer.md",
        "v3_5_reference_app_plan.md",
    ]:
        text = (DOCS / name).read_text(encoding="utf-8")
        assert "V3.5-I Reference App" in text
        assert "dev/local Application Adaptation Layer" in text


def _scope(scope: Any) -> dict[str, Any]:
    if hasattr(scope, "to_dict"):
        return scope.to_dict()
    return dict(scope)


def _scope_key(scope: dict[str, Any]) -> tuple[str, str, str]:
    return (
        str(scope.get("app_id") or "reference_app"),
        str(scope.get("project_id") or "demo"),
        str(scope.get("workspace_id") or "local"),
    )


def _sse(*, event_id: str, event: str, data: dict[str, Any]) -> bytes:
    return f"id: {event_id}\nevent: {event}\ndata: {json.dumps(data)}\n\n".encode("utf-8")

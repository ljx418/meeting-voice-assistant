"""V3.6-H business event bridge and workflow context tests."""

from __future__ import annotations

import asyncio
import json

from fastapi.testclient import TestClient

from apps.api import create_app
from apps.gateway.approvals import APPROVAL_PENDING, ApprovalStore
from apps.gateway.artifacts import ArtifactRegistry
from apps.gateway.protocol import RpcRequest
from apps.gateway.runtime import GatewayRuntimePool
from apps.gateway.service import GatewayService
from apps.gateway.storage import GatewaySessionStore
from apps.gateway.traces import TraceStore
from core.protocol.auth import issue_capability_token
from core.protocol.schemas.errors import ProtocolError
from core.protocol.schemas.methods import METHOD_SCHEMAS
from core.protocol.schemas.workflow_events import WORKFLOW_EVENT_SCHEMAS


SECRET = "v3-6-h-secret"
LOCAL_ORIGIN = "http://localhost:5173"


def _scope(app_id: str = "meeting", project_id: str = "demo", workspace_id: str = "local") -> dict[str, str]:
    return {"app_id": app_id, "project_id": project_id, "workspace_id": workspace_id}


def _gateway(tmp_path) -> GatewayService:
    runtime = GatewayRuntimePool(
        store=GatewaySessionStore(tmp_path / "sessions"),
        artifact_registry=ArtifactRegistry(tmp_path / "artifacts"),
        trace_store=TraceStore(tmp_path / "traces"),
        approval_store=ApprovalStore(tmp_path / "approvals"),
    )
    return GatewayService(runtime_pool=runtime)


def _template(template_id: str = "workflow_business") -> dict:
    return {
        "workflow_template_id": template_id,
        "name": "Business Event Workflow",
        "stations": [
            {"station_id": "station_a", "name": "A"},
            {"station_id": "station_b", "name": "B", "approval_required": True},
            {"station_id": "station_c", "name": "C"},
        ],
        "edges": [
            {"edge_id": "a_to_b", "from_station_id": "station_a", "to_station_id": "station_b"},
            {"edge_id": "b_to_c", "from_station_id": "station_b", "to_station_id": "station_c"},
        ],
    }


async def _rpc(service: GatewayService, method: str, params: dict | None = None):
    return await service.handle_rpc(RpcRequest(id=method, method=method, params=params or {}))


async def _started(service: GatewayService, template_id: str = "workflow_business") -> dict:
    created = await _rpc(service, "workflow.template.create", {"template": _template(template_id), "scope": _scope()})
    assert created.error is None
    published = await _rpc(service, "workflow.template.publish", {"workflow_template_id": template_id, "version": "1.0.0", "scope": _scope()})
    assert published.error is None
    started = await _rpc(service, "workflow.instance.start", {"workflow_version_id": published.result["version"]["workflow_version_id"], "scope": _scope()})
    assert started.error is None
    return started.result["workflow_instance"]


def _token(service: GatewayService, capabilities: tuple[str, ...]) -> str:
    return issue_capability_token(
        app_profile=service.app_registry.get("meeting"),
        project_id="demo",
        workspace_id="local",
        capabilities=capabilities,
        allowed_origins=(LOCAL_ORIGIN,),
        secret=SECRET,
    )


def _headers(service: GatewayService, capabilities: tuple[str, ...]) -> dict[str, str]:
    return {"Authorization": f"Bearer {_token(service, capabilities)}", "Origin": LOCAL_ORIGIN}


def _sse_events(body: str) -> list[dict]:
    events = []
    for frame in body.strip().split("\n\n"):
        data = "".join(line.removeprefix("data: ") for line in frame.splitlines() if line.startswith("data: "))
        if data:
            events.append(json.loads(data))
    return events


def _assert_workflow_event_schema(event: dict, event_type: str, channel: str) -> None:
    schema = next(item for item in WORKFLOW_EVENT_SCHEMAS if item["type"] == event_type)
    assert set(schema["envelope_schema"]["required"]) <= set(event)
    assert event["type"] == event_type
    assert event["channel"] == channel
    assert isinstance(event["data"], dict)


def test_context_update_shallow_merge_path_set_revision_and_scope(tmp_path) -> None:
    async def run() -> None:
        service = _gateway(tmp_path)
        instance = await _started(service)
        got = await _rpc(service, "workflow.context.get", {"workflow_instance_id": instance["workflow_instance_id"], "scope": _scope()})
        assert got.error is None
        assert got.result["context"]["revision"] == 1
        assert got.result["context"]["business"] == {}

        updated = await _rpc(
            service,
            "workflow.context.update",
            {
                "workflow_instance_id": instance["workflow_instance_id"],
                "business": {"selected": "shot_1"},
                "expected_revision": 1,
                "scope": _scope(),
            },
        )
        assert updated.error is None
        assert updated.result["context"]["revision"] == 2
        assert updated.result["context"]["business"]["selected"] == "shot_1"

        path_set = await _rpc(
            service,
            "workflow.context.update",
            {
                "workflow_instance_id": instance["workflow_instance_id"],
                "path": "context.business.review.status",
                "value": "ready",
                "expected_revision": 2,
                "scope": _scope(),
            },
        )
        assert path_set.error is None
        assert path_set.result["context"]["business"]["review"]["status"] == "ready"

        stale = await _rpc(
            service,
            "workflow.context.update",
            {
                "workflow_instance_id": instance["workflow_instance_id"],
                "business": {"late": True},
                "expected_revision": 2,
                "scope": _scope(),
            },
        )
        assert stale.error.code == "WORKFLOW_CONTEXT_CONFLICT"
        cross_scope = await _rpc(service, "workflow.context.get", {"workflow_instance_id": instance["workflow_instance_id"], "scope": _scope(app_id="knowledge")})
        assert cross_scope.error.code == "SCOPE_MISMATCH"

    asyncio.run(run())


def test_context_update_cannot_mutate_runtime_or_system_state(tmp_path) -> None:
    async def run() -> None:
        service = _gateway(tmp_path)
        instance = await _started(service)
        for payload in (
            {"system": {"owner": "ui"}},
            {"runtime": {"status": "running"}},
            {"business": {"status": "running"}},
            {"path": "context.system.owner", "value": "ui"},
        ):
            params = {"workflow_instance_id": instance["workflow_instance_id"], "scope": _scope(), **payload}
            response = await _rpc(service, "workflow.context.update", params)
            assert response.error is not None
            assert response.error.code in {"WORKFLOW_CONTEXT_SCOPE_MISMATCH", "BUSINESS_EVENT_BINDING_INVALID"}
        after = await _rpc(service, "workflow.instance.get", {"workflow_instance_id": instance["workflow_instance_id"], "scope": _scope()})
        assert after.result["workflow_instance"]["status"] == "waiting_approval"

    asyncio.run(run())


def test_business_event_namespace_binding_apply_and_idempotency(tmp_path) -> None:
    async def run() -> None:
        service = _gateway(tmp_path)
        instance = await _started(service)
        for event_type in ("business.*", "meeting.started", "knowledge.ingested", "video.rendered"):
            response = await _rpc(
                service,
                "business.event.emit",
                {"event": {"type": event_type, "workflow_instance_id": instance["workflow_instance_id"], "payload": {}}, "scope": _scope()},
            )
            assert response.error.code == "BUSINESS_EVENT_INVALID"

        invalid_binding = await _rpc(
            service,
            "business.event.bind",
            {
                "workflow_instance_id": instance["workflow_instance_id"],
                "event_type": "business.video.shot.selected",
                "target_path": "context.system.selected",
                "payload_path": "event.payload.shot_id",
                "scope": _scope(),
            },
        )
        assert invalid_binding.error.code == "BUSINESS_EVENT_BINDING_INVALID"

        binding = await _rpc(
            service,
            "business.event.bind",
            {
                "workflow_instance_id": instance["workflow_instance_id"],
                "event_type": "business.video.shot.selected",
                "target_path": "context.business.video.selected_shot_id",
                "payload_path": "event.payload.shot_id",
                "mode": "set",
                "scope": _scope(),
            },
        )
        assert binding.error is None
        duplicate_binding = await _rpc(
            service,
            "business.event.bind",
            {
                "binding_id": binding.result["binding"]["binding_id"],
                "workflow_instance_id": instance["workflow_instance_id"],
                "event_type": "business.video.shot.selected",
                "target_path": "context.business.video.duplicate",
                "payload_path": "event.payload.shot_id",
                "mode": "set",
                "scope": _scope(),
            },
        )
        assert duplicate_binding.error.code == "BUSINESS_EVENT_BINDING_INVALID"
        assert duplicate_binding.error.data["reason"] == "duplicate_binding_id"
        emitted = await _rpc(
            service,
            "business.event.emit",
            {
                "event": {
                    "event_id": "evt_1",
                    "type": "business.video.shot.selected",
                    "workflow_instance_id": instance["workflow_instance_id"],
                    "payload": {"shot_id": "shot_001"},
                },
                "scope": _scope(),
            },
        )
        assert emitted.error is None
        assert emitted.result["idempotent"] is False
        assert emitted.result["context"]["business"]["video"]["selected_shot_id"] == "shot_001"

        repeated = await _rpc(
            service,
            "business.event.emit",
            {
                "event": {
                    "event_id": "evt_1",
                    "type": "business.video.shot.selected",
                    "workflow_instance_id": instance["workflow_instance_id"],
                    "payload": {"shot_id": "shot_002"},
                },
                "scope": _scope(),
            },
        )
        assert repeated.error is None
        assert repeated.result["idempotent"] is True
        assert repeated.result["context"]["business"]["video"]["selected_shot_id"] == "shot_001"

    asyncio.run(run())


def test_business_event_idempotency_marker_is_not_consumed_when_context_write_fails(tmp_path) -> None:
    async def run() -> None:
        service = _gateway(tmp_path)
        instance = await _started(service)
        await _rpc(
            service,
            "business.event.bind",
            {
                "workflow_instance_id": instance["workflow_instance_id"],
                "event_type": "business.video.shot.selected",
                "target_path": "context.business.video.selected_shot_id",
                "payload_path": "event.payload.shot_id",
                "mode": "set",
                "scope": _scope(),
            },
        )
        original = service.workflow_repository.store.apply_business_event_context
        calls = {"count": 0}

        def fail_once(event_key, context, *, scope):
            calls["count"] += 1
            if calls["count"] == 1:
                raise ProtocolError(
                    "WORKFLOW_EXECUTION_FAILED",
                    "simulated context write failure",
                    {"reason": "simulated"},
                )
            return original(event_key, context, scope=scope)

        service.workflow_repository.store.apply_business_event_context = fail_once  # type: ignore[method-assign]
        first = await _rpc(
            service,
            "business.event.emit",
            {
                "event": {
                    "event_id": "evt_retry",
                    "type": "business.video.shot.selected",
                    "workflow_instance_id": instance["workflow_instance_id"],
                    "payload": {"shot_id": "shot_failed"},
                },
                "scope": _scope(),
            },
        )
        assert first.error.code == "WORKFLOW_EXECUTION_FAILED"
        service.workflow_repository.store.apply_business_event_context = original  # type: ignore[method-assign]

        retry = await _rpc(
            service,
            "business.event.emit",
            {
                "event": {
                    "event_id": "evt_retry",
                    "type": "business.video.shot.selected",
                    "workflow_instance_id": instance["workflow_instance_id"],
                    "payload": {"shot_id": "shot_recovered"},
                },
                "scope": _scope(),
            },
        )
        assert retry.error is None
        assert retry.result["idempotent"] is False
        assert retry.result["context"]["business"]["video"]["selected_shot_id"] == "shot_recovered"

        repeated = await _rpc(
            service,
            "business.event.emit",
            {
                "event": {
                    "event_id": "evt_retry",
                    "type": "business.video.shot.selected",
                    "workflow_instance_id": instance["workflow_instance_id"],
                    "payload": {"shot_id": "shot_ignored"},
                },
                "scope": _scope(),
            },
        )
        assert repeated.error is None
        assert repeated.result["idempotent"] is True
        assert repeated.result["context"]["business"]["video"]["selected_shot_id"] == "shot_recovered"

    asyncio.run(run())


def test_business_event_does_not_bypass_approval_or_runtime(tmp_path) -> None:
    async def run() -> None:
        service = _gateway(tmp_path)
        instance = await _started(service)
        pending = service.approval_store.list_approvals(status=APPROVAL_PENDING, app_id="meeting", project_id="demo", workspace_id="local")
        assert len(pending) == 1
        await _rpc(
            service,
            "business.event.bind",
            {
                "workflow_instance_id": instance["workflow_instance_id"],
                "event_type": "business.video.shot.selected",
                "target_path": "context.business.video.selected_shot_id",
                "payload_path": "event.payload.shot_id",
                "scope": _scope(),
            },
        )
        emitted = await _rpc(
            service,
            "business.event.emit",
            {
                "event": {
                    "type": "business.video.shot.selected",
                    "workflow_instance_id": instance["workflow_instance_id"],
                    "payload": {"shot_id": "shot_001"},
                },
                "scope": _scope(),
            },
        )
        assert emitted.error is None
        current = await _rpc(service, "workflow.instance.get", {"workflow_instance_id": instance["workflow_instance_id"], "scope": _scope()})
        assert current.result["workflow_instance"]["status"] == "waiting_approval"
        approvals = service.approval_store.list_approvals(status=APPROVAL_PENDING, app_id="meeting", project_id="demo", workspace_id="local")
        assert len(approvals) == 1
        runs = await _rpc(service, "station.run.list", {"workflow_instance_id": instance["workflow_instance_id"], "scope": _scope()})
        assert [run["station_id"] for run in runs.result["station_runs"]] == ["station_a", "station_b"]

    asyncio.run(run())


def test_eventbridge_sse_and_redaction(tmp_path, monkeypatch) -> None:
    async def setup() -> tuple[GatewayService, dict]:
        service = _gateway(tmp_path)
        instance = await _started(service)
        await _rpc(
            service,
            "business.event.bind",
            {
                "workflow_instance_id": instance["workflow_instance_id"],
                "event_type": "business.video.shot.selected",
                "target_path": "context.business.video.selected_shot_id",
                "payload_path": "event.payload.shot_id",
                "scope": _scope(),
            },
        )
        emitted = await _rpc(
            service,
            "business.event.emit",
            {
                "event": {
                    "idempotency_key": "idem_1",
                    "type": "business.video.shot.selected",
                    "workflow_instance_id": instance["workflow_instance_id"],
                    "payload": {
                        "shot_id": "shot_001",
                        "secret": "secret-token-value",
                        "raw_trace_payload": {"Authorization": "Bearer secret-token-value"},
                    },
                },
                "scope": _scope(),
            },
        )
        assert emitted.error is None
        return service, instance

    service, instance = asyncio.run(setup())
    monkeypatch.setenv("HARNESS_CAPABILITY_TOKEN_SECRET", SECRET)
    monkeypatch.delenv("HARNESS_V3_5_DEV_MODE", raising=False)
    client = TestClient(create_app(gateway_service=service))
    headers = _headers(service, ("events", "business_events.read", "business_events.write", "workflow_context.read"))
    descriptor = client.post(
        "/v1/rpc",
        json={
            "id": "sub",
            "method": "events.subscribe",
            "params": {"channels": ["business", "workflow_context"], "workflow_instance_id": instance["workflow_instance_id"]},
        },
        headers=headers,
    ).json()["result"]
    response = client.get(
        descriptor["eventsource_url"] + f"&workflow_instance_id={instance['workflow_instance_id']}",
        headers={"Origin": LOCAL_ORIGIN},
    )
    assert response.status_code == 200
    events = _sse_events(response.text)
    business_event = next(event for event in events if event["type"] == "business.event.received")
    context_event = next(event for event in events if event["type"] == "workflow.context.updated")
    _assert_workflow_event_schema(business_event, "business.event.received", "business")
    _assert_workflow_event_schema(context_event, "workflow.context.updated", "workflow_context")
    assert business_event["workflow_instance_id"] == instance["workflow_instance_id"]
    assert context_event["data"]["context_revision"] >= 2
    raw = json.dumps(events, ensure_ascii=False)
    for forbidden in ("secret-token-value", "Authorization", "Bearer ", "raw_trace_payload", "raw_artifact_content"):
        assert forbidden not in raw


def test_external_capabilities_method_metadata_and_no_sdk_default(tmp_path, monkeypatch) -> None:
    async def setup() -> tuple[GatewayService, dict]:
        service = _gateway(tmp_path)
        instance = await _started(service)
        return service, instance

    service, instance = asyncio.run(setup())
    schema_by_method = {entry["method"]: entry for entry in METHOD_SCHEMAS}
    for method in ("business.event.emit", "business.event.bind", "workflow.context.get", "workflow.context.update"):
        assert schema_by_method[method]["runtime_handler"] is True
        assert schema_by_method[method]["sdk_exposure"] == "workflow_runtime"

    monkeypatch.setenv("HARNESS_CAPABILITY_TOKEN_SECRET", SECRET)
    monkeypatch.delenv("HARNESS_V3_5_DEV_MODE", raising=False)
    client = TestClient(create_app(gateway_service=service))
    no_cap = _headers(service, ("events",))
    read_cap = _headers(service, ("workflow_context.read",))
    write_cap = _headers(service, ("workflow_context.write",))
    business_cap = _headers(service, ("business_events.write",))
    get_payload = {"id": "g", "method": "workflow.context.get", "params": {"workflow_instance_id": instance["workflow_instance_id"]}}
    assert client.post("/v1/rpc", json=get_payload, headers=no_cap).json()["error"]["code"] == "CAPABILITY_DENIED"
    assert client.post("/v1/rpc", json=get_payload, headers=read_cap).json()["result"]["context"]["workflow_instance_id"] == instance["workflow_instance_id"]
    update_payload = {
        "id": "u",
        "method": "workflow.context.update",
        "params": {"workflow_instance_id": instance["workflow_instance_id"], "business": {"ok": True}},
    }
    assert client.post("/v1/rpc", json=update_payload, headers=read_cap).json()["error"]["code"] == "CAPABILITY_DENIED"
    assert client.post("/v1/rpc", json=update_payload, headers=write_cap).json()["result"]["context"]["business"]["ok"] is True
    emit_payload = {
        "id": "e",
        "method": "business.event.emit",
        "params": {
            "event": {
                "type": "business.video.shot.selected",
                "workflow_instance_id": instance["workflow_instance_id"],
                "payload": {"shot_id": "shot_001"},
            }
        },
    }
    assert client.post("/v1/rpc", json=emit_payload, headers=write_cap).json()["error"]["code"] == "CAPABILITY_DENIED"
    assert client.post("/v1/rpc", json=emit_payload, headers=business_cap).json()["error"]["code"] == "BUSINESS_EVENT_UNBOUND"

    from sdk.python.harnessos_client.protocol_snapshot import WRAPPER_METHODS

    assert not any(method.startswith("business.event.") for method in WRAPPER_METHODS.values())
    assert not any(method.startswith("workflow.context.") for method in WRAPPER_METHODS.values())
    ts_snapshot = (tmp_path.parents[2] / "noop") if False else None
    del ts_snapshot


def test_no_quality_board_patch_mutation_creep(tmp_path) -> None:
    async def run() -> None:
        service = _gateway(tmp_path)
        instance = await _started(service)
        await _rpc(
            service,
            "workflow.context.update",
            {"workflow_instance_id": instance["workflow_instance_id"], "business": {"selected": "shot_1"}, "scope": _scope()},
        )
        traces = json.dumps(service.trace_store.list_records(app_id="meeting", project_id="demo", workspace_id="local"), ensure_ascii=False)
        assert "workflow.patch." not in traces
        assert "quality.evaluation.created" not in traces
        board = await _rpc(service, "workflow.board.get", {"workflow_instance_id": instance["workflow_instance_id"], "scope": _scope()})
        assert "business" not in board.result["board"]

    asyncio.run(run())

"""V3.6-B workflow template/draft/version service tests."""

from __future__ import annotations

import asyncio
import json
from pathlib import Path

from fastapi.testclient import TestClient

from apps.api import create_app
from apps.gateway.protocol import RpcRequest
from apps.gateway.service import GatewayService
from core.protocol.auth import issue_capability_token


SECRET = "v3-6-b-secret"
LOCAL_ORIGIN = "http://localhost:5173"


def _scope(app_id: str = "meeting", project_id: str = "demo", workspace_id: str = "local") -> dict[str, str]:
    return {"app_id": app_id, "project_id": project_id, "workspace_id": workspace_id}


def _template(template_id: str = "workflow_demo", *, name: str = "Demo Workflow") -> dict:
    return {
        "workflow_template_id": template_id,
        "name": name,
        "stations": [
            {"station_id": "station_a", "name": "A"},
            {"station_id": "station_b", "name": "B"},
        ],
        "edges": [
            {
                "edge_id": "edge_a_b",
                "from_station_id": "station_a",
                "to_station_id": "station_b",
                "order": 1,
            }
        ],
    }


async def _rpc(service: GatewayService, method: str, params: dict | None = None):
    return await service.handle_rpc(RpcRequest(id=method, method=method, params=params or {}))


def test_create_template_uniqueness_scope_and_initial_draft() -> None:
    async def run() -> None:
        service = GatewayService()
        created = await _rpc(service, "workflow.template.create", {"template": _template(), "scope": _scope()})
        assert created.error is None
        assert created.result["template"]["workflow_template_id"] == "workflow_demo"
        assert created.result["template"]["app_id"] == "meeting"
        assert created.result["template"]["project_id"] == "demo"
        assert created.result["draft"]["status"] == "editable"
        assert created.result["draft"]["revision"] == 1

        duplicate = await _rpc(service, "workflow.template.create", {"template": _template(), "scope": _scope()})
        assert duplicate.error.code == "WORKFLOW_TEMPLATE_ALREADY_EXISTS"

        other_scope = await _rpc(
            service,
            "workflow.template.create",
            {"template": _template(), "scope": _scope("knowledge", "demo", "local")},
        )
        assert other_scope.error is None
        listed = await _rpc(service, "workflow.template.list", {"scope": _scope()})
        assert listed.result["count"] == 1
        assert listed.result["templates"][0]["app_id"] == "meeting"

    asyncio.run(run())


def test_update_save_revision_conflicts_and_publish_fork_semantics() -> None:
    async def run() -> None:
        service = GatewayService()
        created = await _rpc(service, "workflow.template.create", {"template": _template(), "scope": _scope()})
        draft_id = created.result["draft"]["workflow_draft_id"]

        updated_template = _template(name="Updated")
        updated = await _rpc(
            service,
            "workflow.template.update_draft",
            {
                "workflow_template_id": "workflow_demo",
                "draft": updated_template,
                "expected_revision": 1,
                "scope": _scope(),
            },
        )
        assert updated.error is None
        assert updated.result["draft"]["revision"] == 2
        assert updated.result["forked"] is False

        stale = await _rpc(
            service,
            "workflow.draft.save",
            {"workflow_draft_id": draft_id, "draft": updated_template, "expected_revision": 1, "scope": _scope()},
        )
        assert stale.error.code == "WORKFLOW_DRAFT_CONFLICT"

        published = await _rpc(
            service,
            "workflow.template.publish",
            {"workflow_template_id": "workflow_demo", "version": "1.0.0", "expected_revision": 2, "scope": _scope()},
        )
        assert published.error is None
        version_id = published.result["version"]["workflow_version_id"]
        assert published.result["draft"]["status"] == "published"
        assert published.result["version"]["snapshot"]["name"] == "Updated"

        save_published = await _rpc(
            service,
            "workflow.draft.save",
            {"workflow_draft_id": draft_id, "draft": _template(name="Illegal"), "scope": _scope()},
        )
        assert save_published.error.code == "WORKFLOW_PUBLISHED_IMMUTABLE"

        forked = await _rpc(
            service,
            "workflow.template.update_draft",
            {"workflow_template_id": "workflow_demo", "draft": _template(name="Forked"), "scope": _scope()},
        )
        assert forked.error is None
        assert forked.result["forked"] is True
        assert forked.result["base_version_id"] == version_id
        assert forked.result["draft_id"] != draft_id

        fetched_version = await _rpc(service, "workflow.version.get", {"workflow_version_id": version_id, "scope": _scope()})
        assert fetched_version.result["version"]["snapshot"]["name"] == "Updated"

    asyncio.run(run())


def test_publish_requires_explicit_version_and_duplicate_version_conflicts() -> None:
    async def run() -> None:
        service = GatewayService()
        await _rpc(service, "workflow.template.create", {"template": _template(), "scope": _scope()})
        missing = await _rpc(service, "workflow.template.publish", {"workflow_template_id": "workflow_demo", "scope": _scope()})
        assert missing.error.code == "INVALID_PARAMS"

        first = await _rpc(service, "workflow.template.publish", {"workflow_template_id": "workflow_demo", "version": "1.0.0", "scope": _scope()})
        assert first.error is None
        await _rpc(service, "workflow.template.update_draft", {"workflow_template_id": "workflow_demo", "draft": _template(name="Next"), "scope": _scope()})
        duplicate = await _rpc(service, "workflow.template.publish", {"workflow_template_id": "workflow_demo", "version": "1.0.0", "scope": _scope()})
        assert duplicate.error.code == "WORKFLOW_VERSION_CONFLICT"

    asyncio.run(run())


def test_concurrent_save_and_publish_conflicts_are_stable() -> None:
    async def run() -> None:
        service = GatewayService()
        created = await _rpc(service, "workflow.template.create", {"template": _template(), "scope": _scope()})
        draft_id = created.result["draft"]["workflow_draft_id"]
        save1, save2 = await asyncio.gather(
            _rpc(service, "workflow.draft.save", {"workflow_draft_id": draft_id, "draft": _template(name="S1"), "expected_revision": 1, "scope": _scope()}),
            _rpc(service, "workflow.draft.save", {"workflow_draft_id": draft_id, "draft": _template(name="S2"), "expected_revision": 1, "scope": _scope()}),
        )
        codes = sorted(resp.error.code if resp.error else "OK" for resp in (save1, save2))
        assert codes == ["OK", "WORKFLOW_DRAFT_CONFLICT"]

        current = save1.result["draft"] if save1.error is None else save2.result["draft"]
        pub1, pub2 = await asyncio.gather(
            _rpc(service, "workflow.template.publish", {"workflow_template_id": "workflow_demo", "version": "1.0.0", "expected_revision": current["revision"], "scope": _scope()}),
            _rpc(service, "workflow.template.publish", {"workflow_template_id": "workflow_demo", "version": "1.0.0", "expected_revision": current["revision"], "scope": _scope()}),
        )
        codes = sorted(resp.error.code if resp.error else "OK" for resp in (pub1, pub2))
        assert codes == ["OK", "WORKFLOW_VERSION_CONFLICT"]

    asyncio.run(run())


def test_archive_semantics_and_scope_isolation() -> None:
    async def run() -> None:
        service = GatewayService()
        await _rpc(service, "workflow.template.create", {"template": _template(), "scope": _scope()})
        await _rpc(service, "workflow.template.publish", {"workflow_template_id": "workflow_demo", "version": "1.0.0", "scope": _scope()})
        archived = await _rpc(service, "workflow.template.archive", {"workflow_template_id": "workflow_demo", "scope": _scope()})
        assert archived.error is None
        assert archived.result["template"]["status"] == "archived"
        assert archived.result["idempotent"] is False
        archived_again = await _rpc(service, "workflow.template.archive", {"workflow_template_id": "workflow_demo", "scope": _scope()})
        assert archived_again.error is None
        assert archived_again.result["idempotent"] is True

        listed = await _rpc(service, "workflow.template.list", {"scope": _scope()})
        assert listed.result["count"] == 0
        listed_archived = await _rpc(service, "workflow.template.list", {"scope": _scope(), "include_archived": True})
        assert listed_archived.result["count"] == 1
        versions = await _rpc(service, "workflow.version.list", {"workflow_template_id": "workflow_demo", "scope": _scope()})
        assert versions.result["count"] == 1

        update = await _rpc(service, "workflow.template.update_draft", {"workflow_template_id": "workflow_demo", "draft": _template(), "scope": _scope()})
        assert update.error.code == "WORKFLOW_TEMPLATE_ARCHIVED"
        publish = await _rpc(service, "workflow.template.publish", {"workflow_template_id": "workflow_demo", "version": "2.0.0", "scope": _scope()})
        assert publish.error.code == "WORKFLOW_TEMPLATE_ARCHIVED"

        cross_scope = await _rpc(service, "workflow.template.get", {"workflow_template_id": "workflow_demo", "scope": _scope("knowledge")})
        assert cross_scope.error.code == "WORKFLOW_TEMPLATE_NOT_FOUND"

    asyncio.run(run())


def test_schema_validation_errors_for_invalid_contract_fields() -> None:
    async def run() -> None:
        service = GatewayService()
        duplicate_station = _template()
        duplicate_station["stations"].append({"station_id": "station_a", "name": "Duplicate"})
        invalid = await _rpc(service, "workflow.template.create", {"template": duplicate_station, "scope": _scope()})
        assert invalid.error.code == "WORKFLOW_SCHEMA_INVALID"

        invalid_edge = _template()
        invalid_edge["edges"][0]["to_station_id"] = "missing"
        invalid = await _rpc(service, "workflow.template.create", {"template": invalid_edge, "scope": _scope()})
        assert invalid.error.code == "WORKFLOW_SCHEMA_INVALID"

        for field in ("layout", "capability_token"):
            payload = _template(f"bad_{field}")
            payload[field] = "not allowed"
            invalid = await _rpc(service, "workflow.template.create", {"template": payload, "scope": _scope()})
            assert invalid.error.code == "WORKFLOW_SCHEMA_INVALID"

    asyncio.run(run())


def test_trace_redaction_and_no_runtime_execution() -> None:
    async def run() -> None:
        service = GatewayService()
        initial_jobs = len(service.core_service.list_jobs(app_id="meeting", project_id="demo", workspace_id="local"))
        initial_artifacts = len(service.core_service.list_artifacts(app_id="meeting", project_id="demo", workspace_id="local"))
        initial_approvals = len(service.core_service.list_approvals(app_id="meeting", project_id="demo", workspace_id="local"))
        created = await _rpc(service, "workflow.template.create", {"template": _template(), "scope": _scope()})
        updated = await _rpc(
            service,
            "workflow.template.update_draft",
            {"workflow_template_id": "workflow_demo", "draft": _template(name="Safe"), "scope": _scope()},
        )
        published = await _rpc(service, "workflow.template.publish", {"workflow_template_id": "workflow_demo", "version": "1.0.0", "scope": _scope()})
        archived = await _rpc(service, "workflow.template.archive", {"workflow_template_id": "workflow_demo", "scope": _scope()})
        assert all(resp.error is None for resp in (created, updated, published, archived))

        records = service.trace_store.list_records(app_id="meeting", project_id="demo", workspace_id="local")
        event_types = {record["event_type"] for record in records}
        assert {"workflow.template.created", "workflow.template.draft_updated", "workflow.template.published", "workflow.template.archived"} <= event_types
        raw_trace = json.dumps(records, ensure_ascii=False)
        for token in ("capability_token", "subscription_token", "Authorization", "secret-token-value", "Bearer "):
            assert token not in raw_trace

        assert len(service.core_service.list_jobs(app_id="meeting", project_id="demo", workspace_id="local")) == initial_jobs
        assert len(service.core_service.list_artifacts(app_id="meeting", project_id="demo", workspace_id="local")) == initial_artifacts
        assert len(service.core_service.list_approvals(app_id="meeting", project_id="demo", workspace_id="local")) == initial_approvals

    asyncio.run(run())


def _client(monkeypatch, gateway: GatewayService) -> TestClient:
    monkeypatch.setenv("HARNESS_CAPABILITY_TOKEN_SECRET", SECRET)
    monkeypatch.delenv("HARNESS_V3_5_DEV_MODE", raising=False)
    return TestClient(create_app(gateway_service=gateway))


def _token(gateway: GatewayService, capabilities: tuple[str, ...]) -> str:
    return issue_capability_token(
        app_profile=gateway.app_registry.get("meeting"),
        capabilities=capabilities,
        allowed_origins=(LOCAL_ORIGIN,),
        secret=SECRET,
    )


def _headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}", "Origin": LOCAL_ORIGIN}


def test_external_capability_mapping_for_workflow_methods(monkeypatch) -> None:
    gateway = GatewayService()
    client = _client(monkeypatch, gateway)
    read = _headers(_token(gateway, ("workflows.read",)))
    write = _headers(_token(gateway, ("workflows.write",)))
    publish_cap = _headers(_token(gateway, ("workflow_versions.publish", "workflows.read")))

    denied_create = client.post("/v1/rpc", json={"id": "c", "method": "workflow.template.create", "params": {"template": _template()}}, headers=read)
    assert denied_create.json()["error"]["code"] == "CAPABILITY_DENIED"

    created = client.post("/v1/rpc", json={"id": "c", "method": "workflow.template.create", "params": {"template": _template()}}, headers=write)
    assert created.json()["result"]["template"]["app_id"] == "meeting"

    denied_get = client.post("/v1/rpc", json={"id": "g", "method": "workflow.template.get", "params": {"workflow_template_id": "workflow_demo"}}, headers=write)
    assert denied_get.json()["error"]["code"] == "CAPABILITY_DENIED"

    denied_publish = client.post(
        "/v1/rpc",
        json={"id": "p", "method": "workflow.template.publish", "params": {"workflow_template_id": "workflow_demo", "version": "1.0.0"}},
        headers=write,
    )
    assert denied_publish.json()["error"]["code"] == "CAPABILITY_DENIED"

    published = client.post(
        "/v1/rpc",
        json={"id": "p", "method": "workflow.template.publish", "params": {"workflow_template_id": "workflow_demo", "version": "1.0.0"}},
        headers=publish_cap,
    )
    assert published.json()["result"]["version"]["version"] == "1.0.0"


def test_method_list_sdk_exposure_and_planned_split() -> None:
    async def run() -> None:
        service = GatewayService()
        listed = await _rpc(service, "method.list", {})
        methods = {entry["method"]: entry for entry in listed.result["methods"]}
        for method in (
            "workflow.template.create",
            "workflow.template.get",
            "workflow.template.list",
            "workflow.template.update_draft",
            "workflow.draft.save",
            "workflow.template.publish",
            "workflow.template.archive",
            "workflow.version.get",
            "workflow.version.list",
        ):
            assert methods[method]["runtime_handler"] is True
            assert methods[method]["sdk_exposure"] == "workflow_runtime"

        for method in (
            "workflow.instance.start",
            "workflow.instance.get",
            "workflow.instance.list",
            "workflow.instance.status",
            "workflow.instance.pause",
            "workflow.instance.resume",
            "workflow.instance.cancel",
            "workflow.instance.retry",
            "station.run.get",
            "station.run.list",
            "station.rerun",
        ):
            assert methods[method]["runtime_handler"] is True
            assert methods[method]["sdk_exposure"] == "workflow_runtime"
        for method in ("workflow.board.get", "station.output.list"):
            assert methods[method]["runtime_handler"] is True
            assert methods[method]["sdk_exposure"] == "workflow_runtime"
        planned = await _rpc(service, "method.list", {"include_planned": True})
        planned_methods = {entry["method"]: entry for entry in planned.result["methods"]}
        assert planned_methods["business.event.emit"]["runtime_handler"] is True
        assert planned_methods["business.event.emit"]["sdk_exposure"] == "workflow_runtime"
        assert planned_methods["workflow.patch.propose"]["runtime_handler"] is True
        assert planned_methods["workflow.patch.propose"]["sdk_exposure"] == "workflow_runtime"

    asyncio.run(run())


def test_python_and_typescript_default_sdk_surface_do_not_gain_workflow_wrappers() -> None:
    from sdk.python.harnessos_client.protocol_snapshot import WRAPPER_METHODS

    assert not any(method.startswith("workflow.template.") for method in WRAPPER_METHODS.values())
    assert "workflow.draft.save" not in set(WRAPPER_METHODS.values())
    ts_snapshot = (Path(__file__).resolve().parents[1] / "sdk/typescript/src/protocolSnapshot.ts").read_text(encoding="utf-8")
    assert "workflow.template.create" not in ts_snapshot

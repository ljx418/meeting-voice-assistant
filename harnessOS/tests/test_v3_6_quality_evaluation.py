"""V3.6-F quality evaluation MVP tests."""

from __future__ import annotations

import asyncio
import json

from fastapi.testclient import TestClient

from apps.api import create_app
from apps.gateway.approvals import ApprovalStore
from apps.gateway.artifacts import ArtifactRegistry
from apps.gateway.protocol import RpcRequest
from apps.gateway.runtime import GatewayRuntimePool
from apps.gateway.service import GatewayService
from apps.gateway.storage import GatewaySessionStore
from apps.gateway.traces import TraceStore
from core.protocol.auth import issue_capability_token
from core.protocol.schemas.methods import METHOD_SCHEMAS


SECRET = "v3-6-f-secret"
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


def _template(template_id: str = "workflow_quality", *, threshold: float = 0.8) -> dict:
    return {
        "workflow_template_id": template_id,
        "name": "Quality Workflow",
        "stations": [
            {
                "station_id": "station_a",
                "name": "A",
                "output_contracts": [{"contract_id": "a_out", "artifact_kind": "artifact_a", "direction": "output"}],
            }
        ],
        "edges": [],
        "quality_contracts": [
            {
                "contract_id": "quality_a",
                "rubric_id": "rubric_a",
                "evaluator_type": "rule",
                "threshold": threshold,
                "blocking": True,
            }
        ],
    }


async def _rpc(service: GatewayService, method: str, params: dict | None = None):
    return await service.handle_rpc(RpcRequest(id=method, method=method, params=params or {}))


async def _started(service: GatewayService, template: dict | None = None):
    payload = template or _template()
    created = await _rpc(service, "workflow.template.create", {"template": payload, "scope": _scope()})
    assert created.error is None
    published = await _rpc(
        service,
        "workflow.template.publish",
        {"workflow_template_id": payload["workflow_template_id"], "version": "1.0.0", "scope": _scope()},
    )
    assert published.error is None
    started = await _rpc(
        service,
        "workflow.instance.start",
        {"workflow_version_id": published.result["version"]["workflow_version_id"], "scope": _scope()},
    )
    assert started.error is None
    run = started.result["station_runs"][0]
    return started.result["workflow_instance"], run, run["output_artifact_ids"][0]


def _evaluation_payload(instance: dict, run: dict, artifact_id: str, **overrides) -> dict:
    payload = {
        "workflow_instance_id": instance["workflow_instance_id"],
        "station_run_id": run["station_run_id"],
        "artifact_id": artifact_id,
        "rubric_id": "rubric_a",
        "evaluator_type": "manual",
        "score": 0.75,
        "status": "warning",
        "issues": [],
        "suggestions": [],
    }
    payload.update(overrides)
    return payload


def test_manual_rule_placeholder_and_auto_attach(tmp_path) -> None:
    async def run() -> None:
        service = _gateway(tmp_path)
        instance, station_run, artifact_id = await _started(service)

        manual = await _rpc(
            service,
            "quality.evaluation.create",
            {"evaluation": _evaluation_payload(instance, station_run, artifact_id), "auto_attach": True, "scope": _scope()},
        )
        assert manual.error is None
        assert manual.result["attached"] is True
        assert manual.result["evaluation"]["status"] == "warning"
        station = await _rpc(service, "station.run.get", {"station_run_id": station_run["station_run_id"], "scope": _scope()})
        assert manual.result["evaluation"]["evaluation_id"] in station.result["station_run"]["quality_evaluation_ids"]

        rule_pass = await _rpc(
            service,
            "quality.evaluation.create",
            {"evaluation": _evaluation_payload(instance, station_run, artifact_id, evaluator_type="rule", score=0.9, status=None), "scope": _scope()},
        )
        assert rule_pass.error is None
        assert rule_pass.result["evaluation"]["status"] == "passed"
        assert rule_pass.result["evaluation"]["rubric_id"] == "rubric_a"

        rule_fail = await _rpc(
            service,
            "quality.evaluation.create",
            {"evaluation": _evaluation_payload(instance, station_run, artifact_id, evaluator_type="rule", score=0.2, status=None), "scope": _scope()},
        )
        assert rule_fail.error is None
        assert rule_fail.result["evaluation"]["status"] == "failed"

        placeholder = await _rpc(
            service,
            "quality.evaluation.create",
            {
                "evaluation": _evaluation_payload(
                    instance,
                    station_run,
                    artifact_id,
                    evaluator_type="llm_placeholder",
                    rubric_id=None,
                    score=None,
                    status=None,
                ),
                "scope": _scope(),
            },
        )
        assert placeholder.error is None
        assert placeholder.result["evaluation"]["status"] == "manual_required"
        assert placeholder.result["evaluation"]["evaluator_type"] == "llm_placeholder"
        assert placeholder.result["evaluation"]["rubric_id"] == "llm_placeholder"

    asyncio.run(run())


def test_score_status_rubric_validation(tmp_path) -> None:
    async def run() -> None:
        service = _gateway(tmp_path)
        instance, station_run, artifact_id = await _started(service)

        invalid_score = await _rpc(
            service,
            "quality.evaluation.create",
            {"evaluation": _evaluation_payload(instance, station_run, artifact_id, score=1.2), "scope": _scope()},
        )
        assert invalid_score.error.code == "QUALITY_EVALUATION_INVALID"

        invalid_status = await _rpc(
            service,
            "quality.evaluation.create",
            {"evaluation": _evaluation_payload(instance, station_run, artifact_id, status="excellent"), "scope": _scope()},
        )
        assert invalid_status.error.code == "QUALITY_EVALUATION_INVALID"

        missing_rubric = await _rpc(
            service,
            "quality.evaluation.create",
            {"evaluation": _evaluation_payload(instance, station_run, artifact_id, evaluator_type="rule", rubric_id="missing"), "scope": _scope()},
        )
        assert missing_rubric.error.code == "QUALITY_EVALUATION_INVALID"

    asyncio.run(run())


def test_attach_idempotency_and_different_target_denied(tmp_path) -> None:
    async def run() -> None:
        service = _gateway(tmp_path)
        instance, station_run, artifact_id = await _started(service, _template("workflow_quality_attach"))
        evaluation = await _rpc(
            service,
            "quality.evaluation.create",
            {"evaluation": _evaluation_payload(instance, station_run, artifact_id), "scope": _scope()},
        )
        evaluation_id = evaluation.result["evaluation"]["evaluation_id"]
        first = await _rpc(service, "quality.evaluation.attach", {"evaluation_id": evaluation_id, "scope": _scope()})
        assert first.error is None
        assert first.result["idempotent"] is False
        repeated = await _rpc(service, "quality.evaluation.attach", {"evaluation_id": evaluation_id, "scope": _scope()})
        assert repeated.error is None
        assert repeated.result["idempotent"] is True

        other_instance, other_run, other_artifact = await _started(service, _template("workflow_quality_attach_other"))
        changed = await _rpc(
            service,
            "quality.evaluation.attach",
            {
                "evaluation_id": evaluation_id,
                "workflow_instance_id": other_instance["workflow_instance_id"],
                "station_run_id": other_run["station_run_id"],
                "artifact_id": other_artifact,
                "scope": _scope(),
            },
        )
        assert changed.error.code == "QUALITY_EVALUATION_ALREADY_ATTACHED"

    asyncio.run(run())


def test_binding_validation_scope_and_not_found(tmp_path) -> None:
    async def run() -> None:
        service = _gateway(tmp_path)
        instance, station_run, artifact_id = await _started(service, _template("workflow_quality_binding"))
        missing_artifact = await _rpc(
            service,
            "quality.evaluation.create",
            {"evaluation": _evaluation_payload(instance, station_run, "art_missing"), "scope": _scope()},
        )
        assert missing_artifact.error.code == "WORKFLOW_ARTIFACT_INPUT_MISSING"

        missing_station = await _rpc(
            service,
            "quality.evaluation.create",
            {"evaluation": _evaluation_payload(instance, {**station_run, "station_run_id": "sr_missing"}, artifact_id), "scope": _scope()},
        )
        assert missing_station.error.code == "STATION_RUN_NOT_FOUND"

        cross_artifact = service.artifact_registry.register_external(
            external_asset_uri="harnessos://cross",
            app_id="knowledge",
            project_id="demo",
            workspace_id="local",
            domain="workflow_runtime",
            kind="artifact_a",
        )
        cross = await _rpc(
            service,
            "quality.evaluation.create",
            {"evaluation": _evaluation_payload(instance, station_run, cross_artifact["artifact_id"]), "scope": _scope()},
        )
        assert cross.error.code == "SCOPE_MISMATCH"

        missing_eval = await _rpc(service, "quality.evaluation.get", {"evaluation_id": "qe_missing", "scope": _scope()})
        assert missing_eval.error.code == "QUALITY_EVALUATION_NOT_FOUND"

        missing_list_instance = await _rpc(
            service,
            "quality.evaluation.list",
            {"workflow_instance_id": "wfi_missing", "scope": _scope()},
        )
        assert missing_list_instance.error.code == "WORKFLOW_INSTANCE_NOT_FOUND"

        missing_list_station = await _rpc(
            service,
            "quality.evaluation.list",
            {"station_run_id": "sr_missing", "scope": _scope()},
        )
        assert missing_list_station.error.code == "STATION_RUN_NOT_FOUND"

    asyncio.run(run())


def test_input_artifact_requires_explicit_allow_and_no_artifact_read(tmp_path) -> None:
    async def run() -> None:
        service = _gateway(tmp_path)
        seed = service.artifact_registry.register_external(
            external_asset_uri="harnessos://seed",
            app_id="meeting",
            project_id="demo",
            workspace_id="local",
            domain="workflow_runtime",
            kind="seed",
        )
        template = {
            "workflow_template_id": "workflow_quality_input",
            "name": "Input Quality",
            "stations": [
                {
                    "station_id": "station_input",
                    "name": "Input",
                    "input_contracts": [{"contract_id": "seed_in", "artifact_kind": "seed", "direction": "input"}],
                    "output_contracts": [{"contract_id": "out", "artifact_kind": "result", "direction": "output"}],
                }
            ],
            "quality_contracts": [{"contract_id": "q", "rubric_id": "rubric_a", "threshold": 0.5}],
        }
        created = await _rpc(service, "workflow.template.create", {"template": template, "scope": _scope()})
        assert created.error is None
        published = await _rpc(service, "workflow.template.publish", {"workflow_template_id": "workflow_quality_input", "version": "1.0.0", "scope": _scope()})
        started = await _rpc(service, "workflow.instance.start", {"workflow_version_id": published.result["version"]["workflow_version_id"], "input_artifact_ids": [seed["artifact_id"]], "scope": _scope()})
        instance = started.result["workflow_instance"]
        station_run = started.result["station_runs"][0]

        def fail_if_read(_: str) -> dict:
            raise AssertionError("quality evaluator must not call artifact.read")

        service.artifact_registry.read_artifact = fail_if_read
        denied = await _rpc(
            service,
            "quality.evaluation.create",
            {"evaluation": _evaluation_payload(instance, station_run, seed["artifact_id"], evaluator_type="rule", score=0.8), "scope": _scope()},
        )
        assert denied.error.code == "QUALITY_EVALUATION_INVALID"
        allowed = await _rpc(
            service,
            "quality.evaluation.create",
            {"evaluation": _evaluation_payload(instance, station_run, seed["artifact_id"], evaluator_type="rule", score=0.8, allow_input_artifact=True), "scope": _scope()},
        )
        assert allowed.error is None

    asyncio.run(run())


def test_failed_evaluation_does_not_mutate_workflow_station_or_trigger_creep(tmp_path) -> None:
    async def run() -> None:
        service = _gateway(tmp_path)
        instance, station_run, artifact_id = await _started(service, _template("workflow_quality_no_creep"))
        before_instance_status = instance["status"]
        before_station_status = station_run["status"]
        evaluation = await _rpc(
            service,
            "quality.evaluation.create",
            {"evaluation": _evaluation_payload(instance, station_run, artifact_id, evaluator_type="rule", score=0.1, status=None), "auto_attach": True, "scope": _scope()},
        )
        assert evaluation.result["evaluation"]["status"] == "failed"
        after_instance = await _rpc(service, "workflow.instance.get", {"workflow_instance_id": instance["workflow_instance_id"], "scope": _scope()})
        after_station = await _rpc(service, "station.run.get", {"station_run_id": station_run["station_run_id"], "scope": _scope()})
        assert after_instance.result["workflow_instance"]["status"] == before_instance_status
        assert after_station.result["station_run"]["status"] == before_station_status
        assert evaluation.result["evaluation"]["evaluation_id"] in after_station.result["station_run"]["quality_evaluation_ids"]

        trace = json.dumps(service.trace_store.list_records(app_id="meeting", project_id="demo", workspace_id="local"), ensure_ascii=False)
        for prefix in ("workflow.board", "business.", "workflow.patch.", "approval.required", "station.run.rerun_requested"):
            assert prefix not in trace

    asyncio.run(run())


def test_redaction_and_artifact_read_policy_regression(tmp_path) -> None:
    async def run() -> None:
        service = _gateway(tmp_path)
        instance, station_run, artifact_id = await _started(service, _template("workflow_quality_redaction"))
        evaluation = await _rpc(
            service,
            "quality.evaluation.create",
            {
                "evaluation": _evaluation_payload(
                    instance,
                    station_run,
                    artifact_id,
                    issues=[{"secret": "secret-token-value"}],
                    suggestions=[{"Authorization": "Bearer secret-token-value"}],
                    metadata={"capability_token": "secret-token-value", "raw_artifact_content": "do not store"},
                ),
                "auto_attach": True,
                "scope": _scope(),
            },
        )
        raw_eval = json.dumps(evaluation.result["evaluation"], ensure_ascii=False)
        raw_trace = json.dumps(service.trace_store.list_records(app_id="meeting", project_id="demo", workspace_id="local"), ensure_ascii=False)
        assert "secret-token-value" not in raw_eval
        assert "secret-token-value" not in raw_trace
        assert "raw_artifact_content" not in raw_eval
        assert "raw_artifact_content" not in raw_trace

        external = service.artifact_registry.register_external(
            external_asset_uri="harnessos://external",
            app_id="meeting",
            project_id="demo",
            workspace_id="local",
            kind="external",
            mime="application/json",
        )
        video = service.artifact_registry.register_external(
            external_asset_uri="harnessos://video",
            app_id="meeting",
            project_id="demo",
            workspace_id="local",
            kind="video",
            mime="video/mp4",
        )
        binary_path = tmp_path / "payload.bin"
        binary_path.write_bytes(b"\x00\x01")
        binary = service.artifact_registry.register_file(str(binary_path), app_id="meeting", project_id="demo", workspace_id="local")
        large_path = tmp_path / "large.txt"
        large_path.write_text("x" * (1024 * 1024 + 1), encoding="utf-8")
        large = service.artifact_registry.register_file(str(large_path), app_id="meeting", project_id="demo", workspace_id="local")
        for artifact in (external, video, binary, large):
            response = await _rpc(service, "artifact.read", {"artifact_id": artifact["artifact_id"], "scope": _scope()})
            assert response.error.code == "ARTIFACT_READ_BLOCKED"

    asyncio.run(run())


def test_method_metadata_sdk_exclusion_and_external_capabilities(monkeypatch, tmp_path) -> None:
    service = _gateway(tmp_path)
    monkeypatch.setenv("HARNESS_CAPABILITY_TOKEN_SECRET", SECRET)
    monkeypatch.delenv("HARNESS_V3_5_DEV_MODE", raising=False)
    client = TestClient(create_app(gateway_service=service))
    instance, station_run, artifact_id = asyncio.run(_started(service, _template("workflow_quality_auth")))
    schema_by_method = {entry["method"]: entry for entry in METHOD_SCHEMAS}
    for method in ("quality.evaluation.create", "quality.evaluation.get", "quality.evaluation.list", "quality.evaluation.attach"):
        assert schema_by_method[method]["runtime_handler"] is True
        assert schema_by_method[method]["sdk_exposure"] == "workflow_runtime"

    methods = {entry["method"]: entry for entry in asyncio.run(_rpc(service, "method.list", {})).result["methods"]}
    assert methods["quality.evaluation.create"]["sdk_exposure"] == "workflow_runtime"
    planned = {
        entry["method"]: entry
        for entry in asyncio.run(_rpc(service, "method.list", {"include_planned": True})).result["methods"]
    }
    assert planned["workflow.board.get"]["runtime_handler"] is True
    assert planned["workflow.board.get"]["sdk_exposure"] == "workflow_runtime"
    assert planned["business.event.emit"]["runtime_handler"] is True
    assert planned["business.event.emit"]["sdk_exposure"] == "workflow_runtime"
    assert planned["workflow.patch.propose"]["runtime_handler"] is True
    assert planned["workflow.patch.propose"]["sdk_exposure"] == "workflow_runtime"

    def token(capabilities: tuple[str, ...]) -> str:
        return issue_capability_token(
            app_profile=service.app_registry.get("meeting"),
            project_id="demo",
            workspace_id="local",
            capabilities=capabilities,
            allowed_origins=(LOCAL_ORIGIN,),
            secret=SECRET,
        )

    read_headers = {"Authorization": f"Bearer {token(('quality.read',))}", "Origin": LOCAL_ORIGIN}
    write_headers = {"Authorization": f"Bearer {token(('quality.write',))}", "Origin": LOCAL_ORIGIN}
    payload = _evaluation_payload(instance, station_run, artifact_id)
    denied_create = client.post("/v1/rpc", json={"id": "q", "method": "quality.evaluation.create", "params": {"evaluation": payload}}, headers=read_headers)
    assert denied_create.json()["error"]["code"] == "CAPABILITY_DENIED"
    created = client.post("/v1/rpc", json={"id": "q", "method": "quality.evaluation.create", "params": {"evaluation": payload}}, headers=write_headers)
    assert created.json()["result"]["evaluation"]["evaluation_id"]
    eval_id = created.json()["result"]["evaluation"]["evaluation_id"]
    denied_get = client.post("/v1/rpc", json={"id": "g", "method": "quality.evaluation.get", "params": {"evaluation_id": eval_id}}, headers=write_headers)
    assert denied_get.json()["error"]["code"] == "CAPABILITY_DENIED"
    ok_get = client.post("/v1/rpc", json={"id": "g", "method": "quality.evaluation.get", "params": {"evaluation_id": eval_id}}, headers=read_headers)
    assert ok_get.json()["result"]["evaluation"]["evaluation_id"] == eval_id

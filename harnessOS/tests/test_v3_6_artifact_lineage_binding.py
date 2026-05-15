"""V3.6-E station artifact contract and lineage binding tests."""

from __future__ import annotations

import asyncio
import json

from apps.gateway.approvals import ApprovalStore
from apps.gateway.artifacts import ArtifactRegistry
from apps.gateway.protocol import RpcRequest
from apps.gateway.runtime import GatewayRuntimePool
from apps.gateway.service import GatewayService
from apps.gateway.storage import GatewaySessionStore
from apps.gateway.traces import TraceStore
from core.workflows.models import Station


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


def _contract_template(template_id: str = "workflow_artifacts", *, user_metadata: dict | None = None) -> dict:
    return {
        "workflow_template_id": template_id,
        "name": "Artifact Workflow",
        "stations": [
            {
                "station_id": "station_a",
                "name": "A",
                "metadata": user_metadata or {},
                "output_contracts": [
                    {
                        "contract_id": "a_out",
                        "artifact_kind": "artifact_a",
                        "direction": "output",
                        "cardinality": "one",
                        "kind_match_policy": "exact",
                    }
                ],
            },
            {
                "station_id": "station_b",
                "name": "B",
                "input_contracts": [
                    {
                        "contract_id": "b_in",
                        "artifact_kind": "artifact_a",
                        "direction": "input",
                        "required": True,
                        "cardinality": "one",
                        "kind_match_policy": "exact",
                    }
                ],
                "output_contracts": [
                    {
                        "contract_id": "b_out",
                        "artifact_kind": "artifact_b",
                        "direction": "output",
                        "cardinality": "one",
                        "kind_match_policy": "exact",
                    }
                ],
            },
        ],
        "edges": [
            {"edge_id": "edge_a_b", "from_station_id": "station_a", "to_station_id": "station_b", "order": 1},
        ],
    }


def _input_template(template_id: str = "workflow_input", *, expected_kind: str = "seed") -> dict:
    return {
        "workflow_template_id": template_id,
        "name": "Input Workflow",
        "stations": [
            {
                "station_id": "station_input",
                "name": "Input",
                "input_contracts": [
                    {
                        "contract_id": "seed_in",
                        "artifact_kind": expected_kind,
                        "direction": "input",
                        "required": True,
                        "cardinality": "one",
                        "kind_match_policy": "exact",
                    }
                ],
                "output_contracts": [
                    {"contract_id": "seed_out", "artifact_kind": "result", "direction": "output"}
                ],
            }
        ],
        "edges": [],
    }


def _many_input_template(template_id: str = "workflow_many_input") -> dict:
    return {
        "workflow_template_id": template_id,
        "name": "Many Input Workflow",
        "stations": [
            {
                "station_id": "station_many",
                "name": "Many",
                "input_contracts": [
                    {
                        "contract_id": "many_in",
                        "artifact_kind": "seed",
                        "direction": "input",
                        "required": True,
                        "cardinality": "many",
                        "kind_match_policy": "exact",
                    }
                ],
                "output_contracts": [
                    {"contract_id": "many_out", "artifact_kind": "result", "direction": "output"}
                ],
            }
        ],
        "edges": [],
    }


async def _rpc(service: GatewayService, method: str, params: dict | None = None):
    return await service.handle_rpc(RpcRequest(id=method, method=method, params=params or {}))


async def _publish(service: GatewayService, template: dict, *, version: str = "1.0.0") -> dict:
    created = await _rpc(service, "workflow.template.create", {"template": template, "scope": _scope()})
    assert created.error is None
    published = await _rpc(
        service,
        "workflow.template.publish",
        {"workflow_template_id": template["workflow_template_id"], "version": version, "scope": _scope()},
    )
    assert published.error is None
    return published.result["version"]


def test_artifact_contract_id_uniqueness_is_enforced(tmp_path) -> None:
    payload = {
        "station_id": "station_bad",
        "name": "Bad",
        "input_contracts": [{"contract_id": "dup", "artifact_kind": "a", "direction": "input"}],
        "output_contracts": [{"contract_id": "dup", "artifact_kind": "b", "direction": "output"}],
    }
    try:
        Station.model_validate(payload)
    except Exception as exc:
        assert "duplicate artifact contract ids" in str(exc)
    else:
        raise AssertionError("duplicate contract ids should be rejected")

    async def run() -> None:
        service = _gateway(tmp_path)
        duplicated = {
            "workflow_template_id": "workflow_duplicate_contract",
            "name": "Duplicate Contract",
            "stations": [payload],
            "edges": [],
        }
        response = await _rpc(service, "workflow.template.create", {"template": duplicated, "scope": _scope()})
        assert response.error.code == "WORKFLOW_ARTIFACT_CONTRACT_INVALID"

        reusable = {
            "workflow_template_id": "workflow_reusable_contract",
            "name": "Reusable Contract",
            "stations": [
                {
                    "station_id": "station_a",
                    "name": "A",
                    "output_contracts": [{"contract_id": "shared", "artifact_kind": "a", "direction": "output"}],
                },
                {
                    "station_id": "station_b",
                    "name": "B",
                    "output_contracts": [{"contract_id": "shared", "artifact_kind": "b", "direction": "output"}],
                },
            ],
            "edges": [{"edge_id": "ab", "from_station_id": "station_a", "to_station_id": "station_b", "order": 1}],
        }
        allowed = await _rpc(service, "workflow.template.create", {"template": reusable, "scope": _scope()})
        assert allowed.error is None

    asyncio.run(run())


def test_bindings_metadata_namespace_and_lineage(tmp_path) -> None:
    async def run() -> None:
        service = _gateway(tmp_path)
        version = await _publish(
            service,
            _contract_template(user_metadata={"workflow": {"workflow_instance_id": "bad"}, "note": "user"}),
        )
        started = await _rpc(service, "workflow.instance.start", {"workflow_version_id": version["workflow_version_id"], "scope": _scope()})
        assert started.error is None
        instance_id = started.result["workflow_instance"]["workflow_instance_id"]
        runs = await _rpc(service, "station.run.list", {"workflow_instance_id": instance_id, "scope": _scope()})
        station_a, station_b = runs.result["station_runs"]

        assert station_a["output_bindings"] == {"a_out": station_a["output_artifact_ids"]}
        assert station_a["output_artifact_ids"] == [
            artifact_id
            for artifact_ids in station_a["output_bindings"].values()
            for artifact_id in artifact_ids
        ]
        assert station_b["input_bindings"] == {"b_in": station_a["output_artifact_ids"]}
        assert station_b["input_artifact_ids"] == station_a["output_artifact_ids"]
        assert station_b["output_bindings"] == {"b_out": station_b["output_artifact_ids"]}
        assert station_b["output_artifact_ids"] == [
            artifact_id
            for artifact_ids in station_b["output_bindings"].values()
            for artifact_id in artifact_ids
        ]

        a_metadata = await _rpc(service, "artifact.read_metadata", {"artifact_id": station_a["output_artifact_ids"][0], "scope": _scope()})
        metadata = a_metadata.result["artifact"]["metadata"]
        assert set(metadata) == {"workflow", "artifact_contract", "lineage", "user"}
        assert metadata["workflow"]["workflow_instance_id"] == instance_id
        assert metadata["user"]["workflow"]["workflow_instance_id"] == "bad"
        assert metadata["artifact_contract"]["contract_id"] == "a_out"

        b_metadata = await _rpc(service, "artifact.read_metadata", {"artifact_id": station_b["output_artifact_ids"][0], "scope": _scope()})
        assert b_metadata.result["artifact"]["metadata"]["lineage"]["parent_artifact_ids"] == station_a["output_artifact_ids"]
        assert b_metadata.result["artifact"]["kind"] == "artifact_b"
        assert b_metadata.result["artifact"]["kind"] != "connector_result"
        lineage = await _rpc(service, "artifact.lineage", {"domain": "workflow_runtime", "scope": _scope()})
        assert lineage.error is None
        edge = {
            "source_artifact_id": station_a["output_artifact_ids"][0],
            "target_artifact_id": station_b["output_artifact_ids"][0],
            "relation": "derived_from",
        }
        assert edge in lineage.result["edges"]
        assert station_a["output_artifact_ids"][0] in lineage.result["roots"]
        assert station_b["output_artifact_ids"][0] in lineage.result["leaves"]

    asyncio.run(run())


def test_input_validation_missing_kind_mismatch_and_cross_scope(tmp_path) -> None:
    async def run() -> None:
        service = _gateway(tmp_path)
        version = await _publish(service, _input_template())
        original_read_artifact = service.artifact_registry.read_artifact

        def fail_if_read(_: str) -> dict:
            raise AssertionError("workflow input validation must not call artifact.read")

        service.artifact_registry.read_artifact = fail_if_read
        missing = await _rpc(service, "workflow.instance.start", {"workflow_version_id": version["workflow_version_id"], "scope": _scope()})
        assert missing.error.code == "WORKFLOW_ARTIFACT_INPUT_MISSING"

        wrong = service.artifact_registry.register_external(
            external_asset_uri="harnessos://wrong",
            app_id="meeting",
            project_id="demo",
            workspace_id="local",
            domain="workflow_runtime",
            kind="wrong",
            metadata={},
        )
        mismatch = await _rpc(
            service,
            "workflow.instance.start",
            {"workflow_version_id": version["workflow_version_id"], "input_artifact_ids": [wrong["artifact_id"]], "scope": _scope()},
        )
        assert mismatch.error.code == "WORKFLOW_ARTIFACT_KIND_MISMATCH"

        other_scope = service.artifact_registry.register_external(
            external_asset_uri="harnessos://seed",
            app_id="knowledge",
            project_id="demo",
            workspace_id="local",
            domain="workflow_runtime",
            kind="seed",
            metadata={},
        )
        scoped = await _rpc(
            service,
            "workflow.instance.start",
            {"workflow_version_id": version["workflow_version_id"], "input_artifact_ids": [other_scope["artifact_id"]], "scope": _scope()},
        )
        assert scoped.error.code == "SCOPE_MISMATCH"
        service.artifact_registry.read_artifact = original_read_artifact

    asyncio.run(run())


def test_parent_ids_are_stable_deduped_first_seen_order_and_rerun_has_no_false_parent_edge(tmp_path) -> None:
    async def run() -> None:
        service = _gateway(tmp_path)
        many_version = await _publish(service, _many_input_template())
        seed_b = service.artifact_registry.register_external(
            external_asset_uri="harnessos://seed-b",
            app_id="meeting",
            project_id="demo",
            workspace_id="local",
            domain="workflow_runtime",
            kind="seed",
            metadata={},
        )
        seed_a = service.artifact_registry.register_external(
            external_asset_uri="harnessos://seed-a",
            app_id="meeting",
            project_id="demo",
            workspace_id="local",
            domain="workflow_runtime",
            kind="seed",
            metadata={},
        )
        many_started = await _rpc(
            service,
            "workflow.instance.start",
            {
                "workflow_version_id": many_version["workflow_version_id"],
                "input_artifact_ids": [seed_b["artifact_id"], seed_a["artifact_id"], seed_b["artifact_id"]],
                "scope": _scope(),
            },
        )
        assert many_started.error is None
        many_run = many_started.result["station_runs"][0]
        assert many_run["input_bindings"] == {"many_in": [seed_b["artifact_id"], seed_a["artifact_id"]]}
        many_metadata = await _rpc(service, "artifact.read_metadata", {"artifact_id": many_run["output_artifact_ids"][0], "scope": _scope()})
        assert many_metadata.result["artifact"]["metadata"]["lineage"]["parent_artifact_ids"] == [seed_b["artifact_id"], seed_a["artifact_id"]]

        version = await _publish(service, _contract_template())
        started = await _rpc(service, "workflow.instance.start", {"workflow_version_id": version["workflow_version_id"], "scope": _scope()})
        instance_id = started.result["workflow_instance"]["workflow_instance_id"]
        runs = await _rpc(service, "station.run.list", {"workflow_instance_id": instance_id, "scope": _scope()})
        old_a = runs.result["station_runs"][0]
        old_a_artifact = old_a["output_artifact_ids"][0]

        rerun = await _rpc(service, "station.rerun", {"station_run_id": old_a["station_run_id"], "scope": _scope()})
        assert rerun.error is None
        new_a = rerun.result["station_run"]
        new_a_artifact = new_a["output_artifact_ids"][0]
        assert new_a_artifact != old_a_artifact
        metadata = await _rpc(service, "artifact.read_metadata", {"artifact_id": new_a_artifact, "scope": _scope()})
        workflow = metadata.result["artifact"]["metadata"]["workflow"]
        assert workflow["attempt"] == old_a["attempt"] + 1
        assert workflow["rerun_of_station_run_id"] == old_a["station_run_id"]
        assert metadata.result["artifact"]["metadata"]["lineage"]["parent_artifact_ids"] == []

        lineage = await _rpc(service, "artifact.lineage", {"domain": "workflow_runtime", "scope": _scope()})
        false_edge = {"source_artifact_id": old_a_artifact, "target_artifact_id": new_a_artifact, "relation": "derived_from"}
        assert false_edge not in lineage.result["edges"]

    asyncio.run(run())


def test_artifact_read_blocking_policy_is_unchanged(tmp_path) -> None:
    async def run() -> None:
        service = _gateway(tmp_path)
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
        binary = service.artifact_registry.register_file(
            str(binary_path),
            app_id="meeting",
            project_id="demo",
            workspace_id="local",
            kind="binary",
        )
        large_path = tmp_path / "large.txt"
        large_path.write_text("x" * (1024 * 1024 + 1), encoding="utf-8")
        large = service.artifact_registry.register_file(
            str(large_path),
            app_id="meeting",
            project_id="demo",
            workspace_id="local",
            kind="large",
        )
        for artifact in (external, video, binary, large):
            response = await _rpc(service, "artifact.read", {"artifact_id": artifact["artifact_id"], "scope": _scope()})
            assert response.error.code == "ARTIFACT_READ_BLOCKED"

    asyncio.run(run())


def test_artifact_registration_failure_does_not_mark_station_completed(tmp_path, monkeypatch) -> None:
    async def run() -> None:
        service = _gateway(tmp_path)
        version = await _publish(service, _contract_template("workflow_failure"))

        def fail_register_external(**_: object) -> dict:
            raise RuntimeError("secret=super-secret-token")

        monkeypatch.setattr(service.artifact_registry, "register_external", fail_register_external)
        response = await _rpc(service, "workflow.instance.start", {"workflow_version_id": version["workflow_version_id"], "max_steps": 1, "scope": _scope()})
        assert response.error.code == "WORKFLOW_ARTIFACT_REGISTRATION_FAILED"
        assert "super-secret-token" not in json.dumps(response.error.data, ensure_ascii=False)
        instances = await _rpc(service, "workflow.instance.list", {"scope": _scope()})
        instance_id = instances.result["workflow_instances"][0]["workflow_instance_id"]
        runs = await _rpc(service, "station.run.list", {"workflow_instance_id": instance_id, "scope": _scope()})
        assert runs.result["station_runs"][0]["status"] == "failed"
        raw = json.dumps(runs.result["station_runs"][0]["failure_context"], ensure_ascii=False)
        assert "super-secret-token" not in raw
        assert runs.result["station_runs"][0]["output_artifact_ids"] == []

    asyncio.run(run())


def test_no_quality_board_business_patch_runtime_creep(tmp_path) -> None:
    async def run() -> None:
        service = _gateway(tmp_path)
        version = await _publish(service, _contract_template("workflow_no_creep"))
        started = await _rpc(service, "workflow.instance.start", {"workflow_version_id": version["workflow_version_id"], "scope": _scope()})
        assert started.error is None
        trace = json.dumps(service.trace_store.list_records(app_id="meeting", project_id="demo", workspace_id="local"), ensure_ascii=False)
        for prefix in ("quality.", "workflow.board", "business.", "workflow.patch."):
            assert prefix not in trace

    asyncio.run(run())

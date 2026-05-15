"""V3.6 workflow runtime contract inventory and object schema tests."""

from __future__ import annotations

import asyncio
from pathlib import Path

import pytest
from apps.gateway.protocol import RpcRequest
from apps.gateway.service import GatewayService
from core.protocol.contracts.error_inventory import ERROR_INVENTORY
from core.protocol.contracts.event_inventory import EVENT_INVENTORY
from core.protocol.contracts.workflow_error_inventory import WORKFLOW_ERROR_INVENTORY
from core.protocol.contracts.workflow_event_inventory import WORKFLOW_EVENT_INVENTORY
from core.protocol.contracts.workflow_method_inventory import WORKFLOW_METHOD_INVENTORY
from core.protocol.schemas.workflow_errors import WORKFLOW_ERROR_SCHEMAS
from core.protocol.schemas.workflow_events import WORKFLOW_EVENT_SCHEMAS
from core.protocol.schemas.workflow_methods import WORKFLOW_METHOD_SCHEMAS
from core.protocol.schemas.workflow_objects import WORKFLOW_OBJECT_SCHEMAS
from core.workflows.models import (
    ArtifactContract,
    BusinessEvent,
    BusinessEventBinding,
    PipelineBoard,
    QualityContract,
    QualityEvaluation,
    Station,
    StationRun,
    WorkflowAction,
    WorkflowContext,
    WorkflowDraft,
    WorkflowEdge,
    WorkflowInstance,
    WorkflowPatch,
    WorkflowTemplate,
    WorkflowVersion,
)
from pydantic import ValidationError
from sdk.python.harnessos_client.protocol_snapshot import WRAPPER_METHODS


REPO_ROOT = Path(__file__).resolve().parents[1]

EXPECTED_METHODS = {
    "workflow.template.create",
    "workflow.template.get",
    "workflow.template.list",
    "workflow.template.update_draft",
    "workflow.template.publish",
    "workflow.template.archive",
    "workflow.version.get",
    "workflow.version.list",
    "workflow.instance.start",
    "workflow.instance.get",
    "workflow.instance.list",
    "workflow.instance.pause",
    "workflow.instance.resume",
    "workflow.instance.cancel",
    "workflow.instance.retry",
    "workflow.instance.status",
    "station.run.get",
    "station.run.list",
    "station.rerun",
    "station.output.list",
    "quality.evaluation.create",
    "quality.evaluation.get",
    "quality.evaluation.list",
    "quality.evaluation.attach",
    "workflow.board.get",
    "business.event.emit",
    "workflow.context.get",
    "workflow.context.update",
    "business.event.bind",
    "workflow.patch.propose",
    "workflow.patch.diff",
    "workflow.patch.apply",
    "workflow.patch.reject",
    "workflow.draft.save",
}

ALLOWED_CAPABILITIES = {
    "workflows.read",
    "workflows.write",
    "workflows.execute",
    "stations.read",
    "stations.execute",
    "quality.read",
    "quality.write",
    "board.read",
    "business_events.write",
    "workflow_context.read",
    "workflow_context.write",
    "workflow_patches.read",
    "workflow_patches.write",
    "workflow_versions.publish",
}

EXPECTED_OBJECTS = {
    "WorkflowTemplate",
    "WorkflowVersion",
    "WorkflowDraft",
    "WorkflowInstance",
    "Station",
    "WorkflowEdge",
    "StationRun",
    "ArtifactContract",
    "QualityContract",
    "QualityEvaluation",
    "WorkflowAction",
    "WorkflowPatch",
    "WorkflowContext",
    "BusinessEvent",
    "BusinessEventBinding",
    "PipelineBoard",
}

WORKFLOW_MODELS = [
    WorkflowTemplate,
    WorkflowVersion,
    WorkflowDraft,
    WorkflowInstance,
    Station,
    WorkflowEdge,
    StationRun,
    ArtifactContract,
    QualityContract,
    QualityEvaluation,
    WorkflowAction,
    WorkflowPatch,
    WorkflowContext,
    BusinessEvent,
    PipelineBoard,
]

UI_ONLY_FIELDS = {"x", "y", "position", "canvas", "panel", "react_state", "component", "layout"}
SECRET_FIELDS = {"capability_token", "subscription_token", "authorization", "secret", "raw_trace_payload"}

EXPECTED_EVENTS = {
    "workflow.template.created",
    "workflow.template.published",
    "workflow.instance.started",
    "workflow.instance.paused",
    "workflow.instance.resumed",
    "workflow.instance.completed",
    "workflow.instance.failed",
    "workflow.instance.cancelled",
    "station.run.started",
    "station.run.waiting_approval",
    "station.run.completed",
    "station.run.failed",
    "station.run.rerun_requested",
    "quality.evaluated",
    "workflow.context.updated",
    "business.event.received",
    "workflow.patch.proposed",
    "workflow.patch.applied",
    "workflow.patch.rejected",
    "business.*",
}

EXPECTED_ERRORS = {
    "WORKFLOW_TEMPLATE_ALREADY_EXISTS",
    "WORKFLOW_TEMPLATE_NOT_FOUND",
    "WORKFLOW_VERSION_NOT_FOUND",
    "WORKFLOW_DRAFT_NOT_FOUND",
    "WORKFLOW_DRAFT_CONFLICT",
    "WORKFLOW_VERSION_CONFLICT",
    "WORKFLOW_TEMPLATE_ARCHIVED",
    "WORKFLOW_SCHEMA_INVALID",
    "WORKFLOW_INSTANCE_NOT_FOUND",
    "STATION_NOT_FOUND",
    "STATION_RUN_NOT_FOUND",
    "QUALITY_EVALUATION_NOT_FOUND",
    "QUALITY_EVALUATION_INVALID",
    "QUALITY_EVALUATION_UNSUPPORTED",
    "QUALITY_EVALUATION_ALREADY_ATTACHED",
    "WORKFLOW_CONTEXT_NOT_FOUND",
    "WORKFLOW_PATCH_NOT_FOUND",
    "WORKFLOW_INVALID_STATE",
    "WORKFLOW_PUBLISHED_IMMUTABLE",
    "WORKFLOW_PATCH_CONFLICT",
    "WORKFLOW_PATCH_INVALID",
    "WORKFLOW_ACTION_FORBIDDEN",
    "WORKFLOW_RUNTIME_UNSUPPORTED",
    "WORKFLOW_EXECUTION_FAILED",
    "WORKFLOW_APPROVAL_REQUIRED",
    "WORKFLOW_APPROVAL_INACTIVE",
    "WORKFLOW_APPROVAL_SIDE_EFFECT_FAILED",
    "WORKFLOW_ARTIFACT_CONTRACT_MISSING",
    "WORKFLOW_ARTIFACT_CONTRACT_INVALID",
    "WORKFLOW_ARTIFACT_INPUT_MISSING",
    "WORKFLOW_ARTIFACT_OUTPUT_INVALID",
    "WORKFLOW_ARTIFACT_KIND_MISMATCH",
    "WORKFLOW_ARTIFACT_REGISTRATION_FAILED",
    "WORKFLOW_CONTEXT_SCOPE_MISMATCH",
    "BUSINESS_EVENT_INVALID",
    "BUSINESS_EVENT_UNBOUND",
    "BUSINESS_EVENT_ALREADY_APPLIED",
    "BUSINESS_EVENT_BINDING_NOT_FOUND",
    "BUSINESS_EVENT_BINDING_INVALID",
    "WORKFLOW_CONTEXT_CONFLICT",
    "BOARD_NOT_AVAILABLE",
}


def test_workflow_method_inventory_is_complete_and_planned() -> None:
    methods = {entry["method"]: entry for entry in WORKFLOW_METHOD_INVENTORY}
    assert set(methods) == EXPECTED_METHODS
    assert "workflow.version.publish" not in methods
    assert methods["workflow.template.publish"]["capability"] == "workflow_versions.publish"
    implemented = {
        method
        for method, entry in methods.items()
        if entry["planned_phase"] in {"V3.6-B", "V3.6-C", "V3.6-F", "V3.6-G", "V3.6-H", "V3.6-I"}
    }
    for entry in methods.values():
        assert entry["family"] == "workflow_runtime"
        assert entry["introduced_in"] == "V3.6"
        assert entry["status"] == ("implemented" if entry["method"] in implemented else "planned")
        assert entry["planned_phase"]
        if entry["method"] in implemented:
            assert entry["handler_ref"]
        else:
            assert entry["handler_ref"] is None
        assert entry["capability"] in ALLOWED_CAPABILITIES


def test_workflow_method_schema_matches_inventory_and_is_not_runtime() -> None:
    inventory_methods = {entry["method"] for entry in WORKFLOW_METHOD_INVENTORY}
    schema_methods = {entry["method"] for entry in WORKFLOW_METHOD_SCHEMAS}
    assert schema_methods == inventory_methods
    implemented = {entry["method"] for entry in WORKFLOW_METHOD_INVENTORY if entry["status"] == "implemented"}
    for schema in WORKFLOW_METHOD_SCHEMAS:
        assert schema["family"] == "workflow_runtime"
        assert schema["introduced_in"] == "V3.6"
        assert schema["status"] == ("implemented" if schema["method"] in implemented else "planned")
        assert schema["runtime_handler"] is (schema["method"] in implemented)
        assert schema["sdk_exposure"] == ("workflow_runtime" if schema["method"] in implemented else "planned")
        assert schema["planned_phase"]
        assert schema["capability"] in ALLOWED_CAPABILITIES


def test_workflow_methods_are_not_callable_or_sdk_default() -> None:
    workflow_methods = {entry["method"] for entry in WORKFLOW_METHOD_INVENTORY}
    implemented = {entry["method"] for entry in WORKFLOW_METHOD_INVENTORY if entry["status"] == "implemented"}
    planned_after_c = workflow_methods - implemented

    async def run() -> None:
        service = GatewayService()
        default = await service.handle_rpc(RpcRequest(id="methods", method="method.list", params={}))
        assert default.error is None
        default_methods = {entry["method"] for entry in default.result["methods"]}
        assert implemented <= default_methods
        assert not planned_after_c & default_methods

        planned = await service.handle_rpc(
            RpcRequest(id="planned", method="method.list", params={"include_planned": True})
        )
        assert planned.error is None
        planned_methods = {entry["method"] for entry in planned.result["methods"]}
        assert workflow_methods <= planned_methods

    asyncio.run(run())

    python_wrappers = set(WRAPPER_METHODS.values())
    assert not workflow_methods & python_wrappers

    snapshot = (REPO_ROOT / "sdk/typescript/src/protocolSnapshot.ts").read_text(encoding="utf-8")
    for method in workflow_methods:
        assert method not in snapshot


def test_workflow_object_schema_contracts_are_not_ui_stable() -> None:
    objects = {schema["name"]: schema for schema in WORKFLOW_OBJECT_SCHEMAS}
    assert set(objects) == EXPECTED_OBJECTS
    for schema in objects.values():
        assert schema["family"] == "workflow_runtime"
        assert schema["introduced_in"] == "V3.6"
        assert schema["schema_status"] == "contract"
        assert schema["stable_for_ui"] is False
        assert schema["schema"]["type"] == "object"


def test_workflow_event_inventory_and_schema_are_namespaced() -> None:
    event_types = {entry["type"] for entry in WORKFLOW_EVENT_INVENTORY}
    schema_types = {entry["type"] for entry in WORKFLOW_EVENT_SCHEMAS}
    v3_5_events = {entry["type"] for entry in EVENT_INVENTORY}
    assert event_types == EXPECTED_EVENTS
    assert schema_types == event_types
    assert event_types & (v3_5_events - {"business.*"}) == set()
    assert "business.*" in event_types
    for event in event_types:
        assert not event.startswith(("meeting.", "knowledge.", "video."))
    for entry in WORKFLOW_EVENT_INVENTORY:
        assert entry["family"] == "workflow_runtime"
        assert entry["introduced_in"] == "V3.6"
        assert entry["planned_phase"]


def test_workflow_error_inventory_and_schema_are_unique() -> None:
    codes = [entry["code"] for entry in WORKFLOW_ERROR_INVENTORY]
    schema_codes = {entry["code"] for entry in WORKFLOW_ERROR_SCHEMAS}
    base_codes = {entry["code"] for entry in ERROR_INVENTORY}
    assert set(codes) == EXPECTED_ERRORS
    assert len(codes) == len(set(codes))
    assert schema_codes == set(codes)
    assert not (set(codes) & base_codes)
    for entry in WORKFLOW_ERROR_INVENTORY:
        assert entry["family"] == "workflow_runtime"
        assert entry["introduced_in"] == "V3.6"
        assert entry["status"] == "planned"
        assert entry["category"]
        assert "retryable" in entry
        assert entry["planned_phase"]


def test_workflow_contract_files_do_not_introduce_runtime_or_business_dependencies() -> None:
    contract_files = [
        REPO_ROOT / "core/protocol/contracts/workflow_method_inventory.py",
        REPO_ROOT / "core/protocol/contracts/workflow_event_inventory.py",
        REPO_ROOT / "core/protocol/contracts/workflow_error_inventory.py",
        REPO_ROOT / "core/protocol/schemas/workflow_methods.py",
        REPO_ROOT / "core/protocol/schemas/workflow_events.py",
        REPO_ROOT / "core/protocol/schemas/workflow_objects.py",
        REPO_ROOT / "core/protocol/schemas/workflow_errors.py",
    ]
    forbidden_business = ("meeting", "knowledge", "video", "data_service", "voice_service", "funasr")
    forbidden_runtime = ("RuntimeAdapter", "CoreStore")
    for path in contract_files:
        text = path.read_text(encoding="utf-8").lower()
        for token in forbidden_business + forbidden_runtime:
            assert token.lower() not in text, f"{token} leaked into {path}"

    workflow_model = REPO_ROOT / "core/workflows/models.py"
    text = workflow_model.read_text(encoding="utf-8").lower()
    for token in forbidden_business + forbidden_runtime:
        assert token.lower() not in text, f"{token} leaked into {workflow_model}"


def _roundtrip(model: object) -> None:
    cls = type(model)
    dumped = model.model_dump(mode="json")
    restored = cls.model_validate(dumped)
    assert restored.model_dump(mode="json") == dumped


def _sample_station(station_id: str = "station_a") -> Station:
    return Station(
        station_id=station_id,
        name=f"Station {station_id}",
        input_contracts=[
            ArtifactContract(
                contract_id=f"{station_id}_input",
                artifact_kind="generic.input",
                direction="input",
                schema_ref="schema://generic-input",
            )
        ],
        output_contracts=[
            ArtifactContract(
                contract_id=f"{station_id}_output",
                artifact_kind="generic.output",
                direction="output",
                schema_ref="schema://generic-output",
            )
        ],
    )


def test_workflow_object_models_roundtrip_and_required_fields() -> None:
    station_a = _sample_station("station_a")
    station_b = _sample_station("station_b")
    template = WorkflowTemplate(
        workflow_template_id="wft_demo",
        app_id="reference_app",
        name="Demo workflow",
        latest_draft_id="wfd_demo",
        latest_published_version_id="wfv_1",
        stations=[station_a, station_b],
        edges=[
            WorkflowEdge(
                edge_id="edge_a_b",
                from_station_id="station_a",
                to_station_id="station_b",
                order=1,
            )
        ],
    )
    objects = [
        template,
        WorkflowDraft(workflow_draft_id="wfd_demo", workflow_template_id="wft_demo", draft=template.model_dump()),
        WorkflowVersion(
            workflow_version_id="wfv_1",
            workflow_template_id="wft_demo",
            version="1.0.0",
            snapshot=template.model_dump(mode="json"),
        ),
        WorkflowInstance(
            workflow_instance_id="wfi_1",
            workflow_template_id="wft_demo",
            workflow_version="1.0.0",
            app_id="reference_app",
            status="blocked",
        ),
        StationRun(
            station_run_id="sr_1",
            workflow_instance_id="wfi_1",
            station_id="station_a",
            status="waiting_approval",
            attempt=2,
            rerun_of_station_run_id="sr_0",
            job_id="job_1",
            input_artifact_ids=["art_in"],
            output_artifact_ids=["art_out"],
            trace_id="trace_1",
        ),
        QualityContract(contract_id="qc_1", rubric_id="rubric_1", evaluator_type="manual"),
        QualityEvaluation(
            evaluation_id="qe_1",
            workflow_instance_id="wfi_1",
            station_run_id="sr_1",
            artifact_id="art_out",
            rubric_id="rubric_1",
            evaluator_type="rule",
            score=0.9,
            status="completed",
        ),
        WorkflowAction(action_id="act_1", workflow_instance_id="wfi_1", action_type="rerun", station_run_id="sr_1"),
        WorkflowPatch(
            workflow_patch_id="patch_1",
            workflow_template_id="wft_demo",
            workflow_draft_id="wfd_demo",
            base_revision=1,
            operation="update_edge",
            payload={"edge_id": "edge_a_b", "edge_patch": {"order": 2}},
            diff={"edge_id": "edge_a_b"},
            proposed_by="agent",
        ),
        WorkflowContext(workflow_instance_id="wfi_1", app_id="reference_app", business={"stage": "draft"}),
        BusinessEvent(type="business.example.selected", payload={"id": "item_1"}),
        BusinessEventBinding(
            binding_id="beb_1",
            workflow_instance_id="wfi_1",
            event_type="business.example.selected",
            target_path="context.business.selected_id",
            payload_path="event.payload.id",
        ),
        PipelineBoard(
            workflow_instance={"workflow_instance_id": "wfi_1", "status": "blocked"},
            stations=[{"station_id": "station_a", "status": "waiting_approval"}],
            trace_summary={"trace_id": "trace_1", "redacted": True},
        ),
    ]

    for model in objects:
        _roundtrip(model)

    with pytest.raises(ValidationError):
        WorkflowInstance(workflow_instance_id="wfi_missing", workflow_template_id="wft_demo", workflow_version="1.0.0")


def test_workflow_template_edge_references_existing_stations() -> None:
    station = _sample_station("station_a")
    WorkflowTemplate(
        workflow_template_id="wft_valid_edge",
        app_id="reference_app",
        name="Valid edge",
        stations=[station],
        edges=[WorkflowEdge(edge_id="self", from_station_id="station_a", to_station_id="station_a")],
    )

    with pytest.raises(ValidationError, match="missing station ids"):
        WorkflowTemplate(
            workflow_template_id="wft_invalid_edge",
            app_id="reference_app",
            name="Invalid edge",
            stations=[station],
            edges=[WorkflowEdge(edge_id="bad", from_station_id="station_a", to_station_id="station_b")],
        )


def test_workflow_draft_and_published_version_semantics() -> None:
    snapshot = {"stations": [{"station_id": "station_a"}]}
    draft = WorkflowDraft(workflow_draft_id="wfd_1", workflow_template_id="wft_1", draft={"stations": []})
    version = WorkflowVersion(
        workflow_version_id="wfv_1",
        workflow_template_id="wft_1",
        version="1.0.0",
        snapshot=snapshot.copy(),
    )

    draft.draft["stations"].append({"station_id": "station_b"})
    assert version.snapshot == snapshot

    with pytest.raises((TypeError, ValidationError)):
        version.version = "2.0.0"

    template = WorkflowTemplate(
        workflow_template_id="wft_1",
        app_id="reference_app",
        name="Versioned workflow",
        latest_draft_id=draft.workflow_draft_id,
        latest_published_version_id=version.workflow_version_id,
    )
    assert template.latest_draft_id == "wfd_1"
    assert template.latest_published_version_id == "wfv_1"


def test_station_run_binds_job_artifact_trace_and_rerun_keeps_history() -> None:
    first = StationRun(
        station_run_id="sr_1",
        workflow_instance_id="wfi_1",
        station_id="station_a",
        status="completed",
        job_id="job_1",
        output_artifact_ids=["art_1"],
        trace_id="trace_1",
    )
    rerun = StationRun(
        station_run_id="sr_2",
        workflow_instance_id="wfi_1",
        station_id="station_a",
        status="completed",
        attempt=2,
        rerun_of_station_run_id=first.station_run_id,
        job_id="job_2",
        output_artifact_ids=["art_2"],
        trace_id="trace_2",
    )
    assert first.output_artifact_ids == ["art_1"]
    assert rerun.rerun_of_station_run_id == "sr_1"
    assert rerun.output_artifact_ids == ["art_2"]


def test_artifact_contract_does_not_replace_artifact_registry_contract() -> None:
    contract = ArtifactContract(
        contract_id="ac_1",
        artifact_kind="generic.report",
        direction="output",
        schema_ref="schema://report",
        metadata_schema={"type": "object"},
        preview_policy={"mode": "metadata_only"},
        large_file_policy_ref="artifact.read.default",
    )
    assert contract.direction == "output"
    for forbidden in ("content", "path", "storage_backend", "uri"):
        with pytest.raises(ValidationError):
            ArtifactContract(
                contract_id="bad",
                artifact_kind="generic.report",
                direction="output",
                **{forbidden: "not allowed"},
            )


def test_quality_contract_and_evaluation_are_separate() -> None:
    contract = QualityContract(contract_id="qc_1", rubric_id="rubric_1", evaluator_type="llm_placeholder")
    evaluation = QualityEvaluation(
        evaluation_id="qe_1",
        workflow_instance_id="wfi_1",
        station_run_id="sr_1",
        rubric_id=contract.rubric_id,
        evaluator_type="manual",
        status="completed",
        issues=[{"message": "Needs review"}],
        suggestions=[{"message": "Tighten output"}],
    )
    assert contract.evaluator_type == "llm_placeholder"
    assert evaluation.evaluator_type == "manual"

    with pytest.raises(ValidationError):
        QualityContract(contract_id="qc_bad", rubric_id="rubric_bad", evaluator_type="real_llm")


def test_workflow_action_and_patch_are_separate_and_patch_is_draft_only() -> None:
    action = WorkflowAction(action_id="act_1", workflow_instance_id="wfi_1", action_type="pause")
    assert action.action_type == "pause"

    patch = WorkflowPatch(
        workflow_patch_id="patch_1",
        workflow_template_id="wft_1",
        workflow_draft_id="wfd_1",
        base_revision=1,
        target="draft",
        operation="add_station",
        payload={"station": {"station_id": "station_new", "name": "New"}},
        diff={"station_id": "station_new"},
        proposed_by="agent",
    )
    assert patch.target == "draft"

    with pytest.raises(ValidationError):
        WorkflowPatch(
            workflow_patch_id="patch_bad",
            workflow_template_id="wft_1",
            workflow_draft_id="wfd_1",
            base_revision=1,
            target="published",
            operation="add_station",
            payload={"station": {"station_id": "station_new", "name": "New"}},
            diff={},
            proposed_by="agent",
        )

    with pytest.raises(ValidationError):
        WorkflowPatch(
            workflow_patch_id="patch_bad_op",
            workflow_template_id="wft_1",
            workflow_draft_id="wfd_1",
            base_revision=1,
            operation="rewrite_everything",
            payload={},
            diff={},
            proposed_by="agent",
        )


def test_business_event_requires_business_namespace_without_core_business_canonical_events() -> None:
    BusinessEvent(type="business.example.selected", payload={"id": "item_1"})
    BusinessEvent(type="business.video.shot.selected", payload={"id": "shot_1"})
    for bad_type in ("business.*", "meeting.started", "knowledge.ingested", "video.rendered"):
        with pytest.raises(ValidationError):
            BusinessEvent(type=bad_type, payload={})

    canonical_events = {entry["type"] for entry in WORKFLOW_EVENT_INVENTORY}
    assert "business.video.shot.selected" not in canonical_events
    assert "business.*" in canonical_events


def test_workflow_models_do_not_define_ui_only_or_secret_fields() -> None:
    forbidden_fields = UI_ONLY_FIELDS | SECRET_FIELDS
    for model in WORKFLOW_MODELS:
        assert not (set(model.model_fields) & forbidden_fields), model.__name__

    for model in WORKFLOW_MODELS:
        required = {
            field_name: _sample_value_for_field(field_name)
            for field_name, field in model.model_fields.items()
            if field.is_required()
        }
        forbidden_name = next(iter(forbidden_fields))
        with pytest.raises(ValidationError):
            model(**required, **{forbidden_name: "not allowed"})


def _sample_value_for_field(field_name: str) -> object:
    samples = {
        "workflow_template_id": "wft_1",
        "workflow_version_id": "wfv_1",
        "workflow_draft_id": "wfd_1",
        "workflow_instance_id": "wfi_1",
        "station_id": "station_a",
        "station_run_id": "sr_1",
        "edge_id": "edge_1",
        "from_station_id": "station_a",
        "to_station_id": "station_a",
        "contract_id": "contract_1",
        "artifact_kind": "generic.report",
        "direction": "output",
        "rubric_id": "rubric_1",
        "evaluation_id": "qe_1",
        "action_id": "act_1",
        "action_type": "pause",
        "workflow_patch_id": "patch_1",
        "workflow_draft_id": "wfd_1",
        "base_revision": 1,
        "operation": "add_station",
        "payload": {},
        "diff": {},
        "proposed_by": "agent",
        "app_id": "reference_app",
        "name": "Workflow",
        "version": "1.0.0",
        "workflow_version": "1.0.0",
        "snapshot": {},
        "draft": {},
        "status": "created",
        "type": "business.example",
        "payload": {},
        "values": {},
        "workflow_instance": {},
        "stations": [],
    }
    return samples[field_name]


def test_pipeline_board_is_summary_only_and_redacted() -> None:
    board = PipelineBoard(
        workflow_instance={"workflow_instance_id": "wfi_1"},
        stations=[{"station_id": "station_a"}],
        trace_summary={"trace_id": "trace_1", "redacted": True},
    )
    assert board.trace_summary["redacted"] is True

    for forbidden in ("raw_trace_payload", "authorization", "subscription_token", "capability_token"):
        with pytest.raises(ValidationError):
            PipelineBoard(
                workflow_instance={"workflow_instance_id": "wfi_1"},
                stations=[],
                **{forbidden: "not allowed"},
            )

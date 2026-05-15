"""V3.5-A protocol schema registry tests."""

from __future__ import annotations

import asyncio

import pytest
from pydantic import ValidationError

from apps.gateway.protocol import RpcError, RpcRequest, RpcResponse
from apps.gateway.service import GatewayService
from core.protocol.contracts.method_inventory import METHOD_INVENTORY
from core.protocol.contracts.workflow_method_inventory import WORKFLOW_METHOD_INVENTORY
from core.protocol.schemas.errors import ERROR_SCHEMAS
from core.protocol.schemas.workflow_errors import WORKFLOW_ERROR_SCHEMAS
from core.protocol.schemas.events import EVENT_SCHEMAS
from core.protocol.schemas.methods import METHOD_SCHEMAS


def test_contracts_default_methods_have_schema() -> None:
    default_methods = {entry["method"] for entry in METHOD_INVENTORY if entry["surface"] == "default"}
    schema_methods = {entry["method"] for entry in METHOD_SCHEMAS}
    assert default_methods <= schema_methods


def test_schema_methods_exist_in_contracts_inventory() -> None:
    contract_methods = {entry["method"] for entry in METHOD_INVENTORY} | {
        entry["method"] for entry in WORKFLOW_METHOD_INVENTORY
    }
    schema_methods = {entry["method"] for entry in METHOD_SCHEMAS}
    assert schema_methods <= contract_methods


def test_forbidden_methods_are_not_default_schema_exposure() -> None:
    forbidden = {entry["method"] for entry in METHOD_INVENTORY if entry["surface"] == "forbidden_by_default"}
    default_schema = {entry["method"] for entry in METHOD_SCHEMAS if entry["sdk_exposure"] == "default"}
    assert not (forbidden & default_schema)
    assert not any(method.startswith("meeting.") for method in default_schema)
    assert not any(method.startswith("knowledge.") for method in default_schema)


def test_events_subscribe_schema_has_runtime_handler_after_phase_c() -> None:
    schemas = {entry["method"]: entry for entry in METHOD_SCHEMAS}
    assert schemas["events.subscribe"]["status"] == "implemented"
    assert schemas["events.subscribe"]["runtime_handler"] is True
    assert schemas["events.subscribe"]["sdk_exposure"] == "default"


def test_method_schema_errors_exist_in_error_registry() -> None:
    errors = {entry["code"] for entry in ERROR_SCHEMAS} | {entry["code"] for entry in WORKFLOW_ERROR_SCHEMAS}
    for method in METHOD_SCHEMAS:
        assert set(method["errors"]) <= errors, method["method"]


def test_event_schema_matches_contract_inventory() -> None:
    event_types = {entry["type"] for entry in EVENT_SCHEMAS}
    assert "artifact.registered" in event_types
    assert "artifact.created" not in event_types
    assert "business.*" in event_types


def test_rpc_response_requires_exactly_one_result_or_error() -> None:
    assert RpcResponse(id="ok", result={}).error is None
    assert RpcResponse(id="err", error=RpcError(code="INVALID_PARAMS", message="bad")).result is None
    with pytest.raises(ValidationError):
        RpcResponse(id="both", result={}, error=RpcError(code="INVALID_PARAMS", message="bad"))
    with pytest.raises(ValidationError):
        RpcResponse(id="neither")


def test_method_list_includes_events_subscribe_and_approval_respond() -> None:
    async def run() -> None:
        service = GatewayService()
        listed = await service.handle_rpc(RpcRequest(id="m1", method="method.list", params={}))
        assert listed.error is None
        methods = {entry["method"]: entry for entry in listed.result["methods"]}
        schema_refs = {entry["schema_ref"] for entry in METHOD_SCHEMAS}
        for entry in methods.values():
            if entry.get("schema_ref"):
                assert entry["schema_ref"] in schema_refs
        assert methods["events.subscribe"]["schema_ref"] == "protocol.methods.events.subscribe"
        assert methods["events.subscribe"]["sdk_exposure"] == "default"
        assert methods["events.subscribe"]["runtime_handler"] is True
        assert "meeting.process_recording" not in methods
        assert "pack.execute_stub" not in methods
        assert "workflow.execute_stub" not in methods
        assert methods["approval.respond"]["schema_ref"] == "protocol.methods.approval.respond"
        assert methods["approval.respond"]["sdk_exposure"] == "default"
        assert methods["approval.respond"]["stability"] == "beta"
        assert methods["approval.respond"]["runtime_handler"] is True
        assert all({"surface", "status", "stability", "runtime_handler", "sdk_exposure"} <= set(entry) for entry in methods.values())
        assert not [entry["method"] for entry in methods.values() if entry["stability"] == "legacy"]

        planned = await service.handle_rpc(
            RpcRequest(id="m2", method="method.list", params={"include_planned": True})
        )
        assert planned.error is None
        planned_methods = {entry["method"]: entry for entry in planned.result["methods"]}
        assert planned_methods["events.subscribe"]["runtime_handler"] is True
        assert planned_methods["events.subscribe"]["schema_ref"] == "protocol.methods.events.subscribe"
        assert planned_methods["events.subscribe"]["schema_ref"] in schema_refs

    asyncio.run(run())


def test_method_list_forbidden_and_events_subscribe_runtime_contract() -> None:
    async def run() -> None:
        service = GatewayService()
        forbidden = await service.handle_rpc(
            RpcRequest(id="m3", method="method.list", params={"include_forbidden": True})
        )
        assert forbidden.error is None
        methods = {entry["method"]: entry for entry in forbidden.result["methods"]}
        assert methods["meeting.process_recording"]["surface"] == "forbidden_by_default"
        assert methods["meeting.process_recording"]["sdk_exposure"] == "forbidden"
        assert methods["meeting.process_recording"]["forbidden_reason"]
        assert methods["pack.execute_stub"]["surface"] == "forbidden_by_default"
        forbidden_methods = [entry for entry in methods.values() if entry["surface"] == "forbidden_by_default"]
        assert forbidden_methods
        assert all(entry["sdk_exposure"] != "default" for entry in forbidden_methods)

        direct = await service.handle_rpc(RpcRequest(id="m4", method="events.subscribe", params={}))
        assert direct.result is None
        assert direct.error is not None
        assert direct.error.code == "AUTH_REQUIRED"

    asyncio.run(run())

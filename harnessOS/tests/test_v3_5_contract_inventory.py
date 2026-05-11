"""V3.5-0 contract inventory tests."""

from __future__ import annotations

from core.protocol.contracts.error_inventory import ERROR_INVENTORY
from core.protocol.contracts.event_inventory import EVENT_INVENTORY
from core.protocol.contracts.method_inventory import FORBIDDEN_BUSINESS_WRAPPERS, METHOD_INVENTORY


REQUIRED_METHOD_FIELDS = {
    "method",
    "surface",
    "status",
    "capability",
    "stability",
    "planned_phase",
    "handler_ref",
    "forbidden_reason",
}
REQUIRED_EVENT_FIELDS = {"type", "channel", "status", "replayable", "aliases"}
REQUIRED_ERROR_FIELDS = {"code", "status", "category", "retryable", "planned_phase"}


def _methods_by_surface(surface: str) -> set[str]:
    return {entry["method"] for entry in METHOD_INVENTORY if entry["surface"] == surface}


def test_method_inventory_shape_and_surfaces_are_stable() -> None:
    for entry in METHOD_INVENTORY:
        assert REQUIRED_METHOD_FIELDS <= set(entry)
    default = _methods_by_surface("default")
    optional = _methods_by_surface("optional")
    forbidden = _methods_by_surface("forbidden_by_default")
    assert default
    assert optional
    assert forbidden
    assert not (default & optional)
    assert not (default & forbidden)
    assert not (optional & forbidden)


def test_default_methods_and_planned_phase_requirements() -> None:
    default = _methods_by_surface("default")
    assert {
        "session.start",
        "turn.start",
        "events.subscribe",
        "artifact.list",
        "artifact.read_metadata",
        "artifact.register_external",
        "artifact.lineage",
        "job.get",
        "job.list",
        "approval.respond",
        "connector.health",
        "pack.list",
        "pack.get",
    } <= default
    planned = {entry["method"]: entry for entry in METHOD_INVENTORY if entry["status"] == "planned"}
    for entry in planned.values():
        assert entry["planned_phase"]
    implemented = {entry["method"]: entry for entry in METHOD_INVENTORY if entry["status"] == "implemented"}
    assert implemented["approval.respond"]["surface"] == "default"
    assert implemented["events.subscribe"]["surface"] == "default"


def test_forbidden_methods_have_reasons_and_no_business_wrappers_are_default() -> None:
    forbidden = [entry for entry in METHOD_INVENTORY if entry["surface"] == "forbidden_by_default"]
    assert forbidden
    for entry in forbidden:
        assert entry["status"] in {"legacy", "debug", "deprecated"}
        assert entry["forbidden_reason"]
    default = _methods_by_surface("default")
    assert not any(method.startswith("meeting.") for method in default)
    assert not any(method.startswith("knowledge.") for method in default)
    assert "pack.execute_stub" not in default
    assert "workflow.execute_stub" not in default
    assert not set(FORBIDDEN_BUSINESS_WRAPPERS) & default


def test_event_inventory_canonical_names_and_aliases() -> None:
    for entry in EVENT_INVENTORY:
        assert REQUIRED_EVENT_FIELDS <= set(entry)
    event_types = [entry["type"] for entry in EVENT_INVENTORY]
    assert len(event_types) == len(set(event_types))
    assert "artifact.registered" in event_types
    assert "artifact.created" not in event_types
    aliases = [alias for entry in EVENT_INVENTORY for alias in entry["aliases"]]
    assert len(aliases) == len(set(aliases))
    assert "artifact.created" in aliases
    assert not (set(aliases) & set(event_types))
    business = [entry for entry in EVENT_INVENTORY if entry["channel"] == "business"]
    assert business == [
        {"type": "business.*", "channel": "business", "status": "reserved", "replayable": False, "aliases": ()}
    ]


def test_event_inventory_required_channels_are_complete() -> None:
    by_channel = {}
    for entry in EVENT_INVENTORY:
        by_channel.setdefault(entry["channel"], set()).add(entry["type"])

    assert {
        "turn.started",
        "item.delta",
        "turn.completed",
        "turn.failed",
    } <= by_channel["chat"]
    assert {
        "job.queued",
        "job.running",
        "job.completed",
        "job.failed",
        "job.cancelled",
    } <= by_channel["job"]
    assert {
        "artifact.registered",
        "artifact.updated",
        "artifact.read_blocked",
    } <= by_channel["artifact"]
    assert {
        "approval.required",
        "approval.approved",
        "approval.rejected",
    } <= by_channel["approval"]
    assert {"trace.recorded"} <= by_channel["trace"]
    assert by_channel["business"] == {"business.*"}


def test_error_inventory_codes_are_unique_and_planned_errors_have_phase() -> None:
    for entry in ERROR_INVENTORY:
        assert REQUIRED_ERROR_FIELDS <= set(entry)
    codes = [entry["code"] for entry in ERROR_INVENTORY]
    assert len(codes) == len(set(codes))
    required = {
        "INVALID_PARAMS",
        "METHOD_NOT_FOUND",
        "SESSION_NOT_FOUND",
        "ARTIFACT_READ_BLOCKED",
        "AUTH_REQUIRED",
        "AUTH_INVALID",
        "AUTH_FORBIDDEN",
        "CAPABILITY_DENIED",
        "SCOPE_MISMATCH",
        "EVENT_CURSOR_INVALID",
        "RUNTIME_ERROR",
        "SUBSCRIPTION_TOKEN_INVALID",
        "SUBSCRIPTION_TOKEN_EXPIRED",
        "SUBSCRIPTION_TOKEN_SCOPE_MISMATCH",
        "SUBSCRIPTION_TOKEN_CHANNEL_DENIED",
        "METHOD_FORBIDDEN",
        "METHOD_DEPRECATED",
        "SCOPE_REQUIRED",
        "APP_PROFILE_NOT_FOUND",
        "PACK_NOT_FOUND",
        "CONNECTOR_NOT_FOUND",
        "APPROVAL_CONFLICT",
        "APPROVAL_NOT_FOUND",
        "APPROVAL_RETRY_CONSUMED",
        "APPROVAL_INVALID_DECISION",
    }
    assert required <= set(codes)
    for entry in ERROR_INVENTORY:
        if entry["status"] == "planned":
            assert entry["planned_phase"]

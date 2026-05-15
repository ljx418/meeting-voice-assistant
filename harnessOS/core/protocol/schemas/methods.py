"""V3.5 protocol method schema registry."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from core.protocol.contracts.method_inventory import METHOD_INVENTORY
from core.protocol.contracts.workflow_method_inventory import WORKFLOW_METHOD_INVENTORY
from core.protocol.schemas.workflow_methods import WORKFLOW_METHOD_SCHEMAS


def _object(properties: Optional[Dict[str, Any]] = None, required: Optional[list[str]] = None) -> Dict[str, Any]:
    return {
        "type": "object",
        "properties": properties or {},
        "required": required or [],
        "additionalProperties": True,
    }


def _schema(
    method: str,
    *,
    capability: str,
    stability: str,
    sdk_exposure: str,
    status: str,
    runtime_handler: bool,
    params_schema: Dict[str, Any],
    result_schema: Dict[str, Any],
    errors: list[str],
    scope_required: bool = True,
    auth_required: bool = False,
    deprecated_by: Optional[str] = None,
) -> Dict[str, Any]:
    return {
        "method": method,
        "schema_ref": f"protocol.methods.{method}",
        "capability": capability,
        "stability": stability,
        "sdk_exposure": sdk_exposure,
        "status": status,
        "runtime_handler": runtime_handler,
        "params_schema": params_schema,
        "result_schema": result_schema,
        "errors": errors,
        "scope_required": scope_required,
        "auth_required": auth_required,
        "deprecated_by": deprecated_by,
    }


_SCOPE = {
    "scope": {
        "type": "object",
        "properties": {
            "app_id": {"type": "string"},
            "project_id": {"type": "string"},
            "workspace_id": {"type": "string"},
        },
        "additionalProperties": True,
    }
}


BASE_METHOD_SCHEMAS: List[Dict[str, Any]] = [
    _schema(
        "session.start",
        capability="sessions",
        stability="stable",
        sdk_exposure="default",
        status="implemented",
        runtime_handler=True,
        params_schema=_object({"model": {"type": "string"}, **_SCOPE}),
        result_schema=_object({"session_id": {"type": "string"}, "state": {"type": "string"}}, ["session_id"]),
        errors=["INVALID_PARAMS", "APP_PROFILE_NOT_FOUND"],
    ),
    _schema(
        "turn.start",
        capability="turns",
        stability="stable",
        sdk_exposure="default",
        status="implemented",
        runtime_handler=True,
        params_schema=_object(
            {"session_id": {"type": "string"}, "input": {"type": "string"}, "domain": {"type": "string"}, **_SCOPE},
            ["input"],
        ),
        result_schema=_object({"session_id": {"type": "string"}, "turn_id": {"type": "string"}}, ["session_id", "turn_id"]),
        errors=["INVALID_PARAMS", "SESSION_NOT_FOUND", "SCOPE_MISMATCH"],
    ),
    _schema(
        "events.subscribe",
        capability="events",
        stability="beta",
        sdk_exposure="default",
        status="implemented",
        runtime_handler=True,
        params_schema=_object(
            {
                "channels": {"type": "array", "items": {"type": "string"}},
                "mode": {"type": "string", "enum": ["native_eventsource", "fetch_stream"]},
                "session_id": {"type": "string"},
                "job_id": {"type": "string"},
                "artifact_id": {"type": "string"},
                "approval_id": {"type": "string"},
                "trace_id": {"type": "string"},
                "since": {"type": "string"},
                "last_event_id": {"type": "string"},
                "ttl_seconds": {"type": "integer"},
                **_SCOPE,
            }
        ),
        result_schema=_object(
            {
                "subscription_id": {"type": "string"},
                "transport": {"type": "string"},
                "eventsource_url": {"type": "string"},
                "subscription_token": {"type": "string"},
                "replay_cursor": {"type": "string"},
                "expires_at": {"type": "string"},
                "allowed_channels": {"type": "array", "items": {"type": "string"}},
            },
            ["subscription_id", "transport", "eventsource_url", "subscription_token", "replay_cursor"],
        ),
        errors=[
            "INVALID_PARAMS",
            "AUTH_REQUIRED",
            "CAPABILITY_DENIED",
            "SCOPE_MISMATCH",
            "SUBSCRIPTION_TOKEN_INVALID",
        ],
    ),
    _schema(
        "artifact.list",
        capability="artifacts",
        stability="stable",
        sdk_exposure="default",
        status="implemented",
        runtime_handler=True,
        params_schema=_object({"session_id": {"type": "string"}, "kind": {"type": "string"}, **_SCOPE}),
        result_schema=_object({"artifacts": {"type": "array"}, "count": {"type": "integer"}}, ["artifacts", "count"]),
        errors=["INVALID_PARAMS", "SCOPE_MISMATCH"],
    ),
    _schema(
        "artifact.read_metadata",
        capability="artifacts",
        stability="stable",
        sdk_exposure="default",
        status="implemented",
        runtime_handler=True,
        params_schema=_object({"artifact_id": {"type": "string"}, **_SCOPE}, ["artifact_id"]),
        result_schema=_object({"artifact": {"type": "object"}}, ["artifact"]),
        errors=["INVALID_PARAMS", "SCOPE_MISMATCH"],
    ),
    _schema(
        "artifact.register_external",
        capability="artifacts",
        stability="stable",
        sdk_exposure="default",
        status="implemented",
        runtime_handler=True,
        params_schema=_object({"kind": {"type": "string"}, "external_asset_uri": {"type": "string"}, **_SCOPE}, ["kind"]),
        result_schema=_object({"artifact": {"type": "object"}, "trace_id": {"type": "string"}}, ["artifact"]),
        errors=["INVALID_PARAMS", "SCOPE_MISMATCH"],
    ),
    _schema(
        "artifact.lineage",
        capability="artifact_lineage",
        stability="stable",
        sdk_exposure="default",
        status="implemented",
        runtime_handler=True,
        params_schema=_object({"artifact_id": {"type": "string"}, "session_id": {"type": "string"}, **_SCOPE}),
        result_schema=_object({"artifacts": {"type": "array"}, "edges": {"type": "array"}}, ["artifacts", "edges"]),
        errors=["INVALID_PARAMS", "SCOPE_MISMATCH"],
    ),
    _schema(
        "job.get",
        capability="jobs",
        stability="stable",
        sdk_exposure="default",
        status="implemented",
        runtime_handler=True,
        params_schema=_object({"job_id": {"type": "string"}, **_SCOPE}, ["job_id"]),
        result_schema=_object({"job": {"type": "object"}}, ["job"]),
        errors=["INVALID_PARAMS", "SCOPE_MISMATCH"],
    ),
    _schema(
        "job.list",
        capability="jobs",
        stability="stable",
        sdk_exposure="default",
        status="implemented",
        runtime_handler=True,
        params_schema=_object({"session_id": {"type": "string"}, "status": {"type": "string"}, **_SCOPE}),
        result_schema=_object({"jobs": {"type": "array"}, "count": {"type": "integer"}}, ["jobs", "count"]),
        errors=["INVALID_PARAMS", "SCOPE_MISMATCH"],
    ),
    _schema(
        "approval.respond",
        capability="approvals",
        stability="beta",
        sdk_exposure="default",
        status="implemented",
        runtime_handler=True,
        params_schema=_object(
            {
                "approval_id": {"type": "string"},
                "decision": {"type": "string", "enum": ["approve", "reject"]},
                "reason": {"type": "string"},
                **_SCOPE,
            },
            ["approval_id", "decision"],
        ),
        result_schema=_object(
            {
                "approval": {"type": "object"},
                "status": {"type": "string"},
                "trace_id": {"type": ["string", "null"]},
                "idempotent": {"type": "boolean"},
                "workflow_side_effect": {"type": ["object", "null"]},
            },
            ["approval", "status", "idempotent"],
        ),
        errors=[
            "INVALID_PARAMS",
            "APPROVAL_CONFLICT",
            "APPROVAL_NOT_FOUND",
            "APPROVAL_INVALID_DECISION",
            "WORKFLOW_APPROVAL_INACTIVE",
            "WORKFLOW_APPROVAL_SIDE_EFFECT_FAILED",
            "SCOPE_MISMATCH",
        ],
    ),
    _schema(
        "connector.health",
        capability="connectors.read",
        stability="stable",
        sdk_exposure="default",
        status="implemented",
        runtime_handler=True,
        params_schema=_object({"connector_id": {"type": "string"}}, ["connector_id"]),
        result_schema=_object({"connector_id": {"type": "string"}, "health": {"type": "object"}}, ["connector_id"]),
        errors=["INVALID_PARAMS", "CONNECTOR_NOT_FOUND"],
        scope_required=False,
    ),
    _schema(
        "pack.list",
        capability="packs.read",
        stability="stable",
        sdk_exposure="default",
        status="implemented",
        runtime_handler=True,
        params_schema=_object(),
        result_schema=_object({"packs": {"type": "array"}, "count": {"type": "integer"}}, ["packs", "count"]),
        errors=["INVALID_PARAMS"],
        scope_required=False,
    ),
    _schema(
        "pack.get",
        capability="packs.read",
        stability="stable",
        sdk_exposure="default",
        status="implemented",
        runtime_handler=True,
        params_schema=_object({"app_id": {"type": "string"}, "pack_id": {"type": "string"}}),
        result_schema=_object({"pack": {"type": "object"}}, ["pack"]),
        errors=["INVALID_PARAMS", "PACK_NOT_FOUND"],
        scope_required=False,
    ),
]

METHOD_SCHEMAS: List[Dict[str, Any]] = BASE_METHOD_SCHEMAS + WORKFLOW_METHOD_SCHEMAS


def get_method_schema(method: str) -> Dict[str, Any]:
    for schema in METHOD_SCHEMAS:
        if schema["method"] == method:
            return schema
    raise KeyError(f"Method schema not found: {method}")


def list_method_schemas(*, sdk_exposure: Optional[str] = None, include_planned: bool = True) -> List[Dict[str, Any]]:
    schemas = METHOD_SCHEMAS
    if sdk_exposure is not None:
        schemas = [schema for schema in schemas if schema["sdk_exposure"] == sdk_exposure]
    if not include_planned:
        schemas = [schema for schema in schemas if schema["runtime_handler"]]
    return list(schemas)


_CONTRACT_METHODS = {entry["method"] for entry in METHOD_INVENTORY} | {
    entry["method"] for entry in WORKFLOW_METHOD_INVENTORY
}
_SCHEMA_METHODS = {entry["method"] for entry in METHOD_SCHEMAS}
if missing := (_SCHEMA_METHODS - _CONTRACT_METHODS):
    raise RuntimeError(f"Method schemas not present in contracts inventory: {sorted(missing)}")

"""V3.6 workflow runtime method schema drafts.

Draft metadata only; no handler registration; no behavior change.
"""

from __future__ import annotations

from typing import Any, Dict, List

from core.protocol.contracts.workflow_method_inventory import WORKFLOW_METHOD_INVENTORY

FAMILY = "workflow_runtime"
INTRODUCED_IN = "V3.6"


def _object(properties: Dict[str, Any] | None = None, required: list[str] | None = None) -> Dict[str, Any]:
    return {
        "type": "object",
        "properties": properties or {},
        "required": required or [],
        "additionalProperties": True,
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


def _schema(entry: Dict[str, Any], params: Dict[str, Any], result: Dict[str, Any], errors: list[str]) -> Dict[str, Any]:
    method = str(entry["method"])
    return {
        "method": method,
        "schema_ref": f"protocol.workflow.methods.{method}",
        "capability": entry["capability"],
        "stability": entry.get("stability", "draft"),
        "sdk_exposure": "workflow_runtime" if entry.get("status") == "implemented" else "planned",
        "status": entry.get("status", "planned"),
        "runtime_handler": entry.get("status") == "implemented",
        "params_schema": params,
        "result_schema": result,
        "errors": errors,
        "scope_required": True,
        "auth_required": True,
        "deprecated_by": None,
        "planned_phase": entry["planned_phase"],
        "family": FAMILY,
        "introduced_in": INTRODUCED_IN,
    }


_BY_METHOD = {entry["method"]: entry for entry in WORKFLOW_METHOD_INVENTORY}


def _m(method: str, params: Dict[str, Any], result: Dict[str, Any], errors: list[str]) -> Dict[str, Any]:
    return _schema(_BY_METHOD[method], params, result, errors)


WORKFLOW_METHOD_SCHEMAS: List[Dict[str, Any]] = [
    _m("workflow.template.create", _object({"template": {"type": "object"}, **_SCOPE}, ["template"]), _object({"template": {"type": "object"}, "draft": {"type": "object"}, "trace_id": {"type": "string"}}), ["INVALID_PARAMS", "WORKFLOW_TEMPLATE_ALREADY_EXISTS", "WORKFLOW_SCHEMA_INVALID"]),
    _m("workflow.template.get", _object({"workflow_template_id": {"type": "string"}, **_SCOPE}, ["workflow_template_id"]), _object({"template": {"type": "object"}}), ["WORKFLOW_TEMPLATE_NOT_FOUND", "SCOPE_MISMATCH"]),
    _m("workflow.template.list", _object({"include_archived": {"type": "boolean"}, **_SCOPE}), _object({"templates": {"type": "array"}, "count": {"type": "integer"}}), ["SCOPE_MISMATCH"]),
    _m("workflow.template.update_draft", _object({"workflow_template_id": {"type": "string"}, "draft": {"type": "object"}, "expected_revision": {"type": "integer"}, **_SCOPE}, ["workflow_template_id", "draft"]), _object({"draft": {"type": "object"}, "draft_id": {"type": "string"}, "forked": {"type": "boolean"}, "base_version_id": {"type": ["string", "null"]}, "trace_id": {"type": "string"}}), ["WORKFLOW_TEMPLATE_NOT_FOUND", "WORKFLOW_PUBLISHED_IMMUTABLE", "WORKFLOW_DRAFT_CONFLICT", "WORKFLOW_TEMPLATE_ARCHIVED", "WORKFLOW_SCHEMA_INVALID"]),
    _m("workflow.template.publish", _object({"workflow_template_id": {"type": "string"}, "version": {"type": "string"}, "expected_revision": {"type": "integer"}, **_SCOPE}, ["workflow_template_id", "version"]), _object({"template": {"type": "object"}, "draft": {"type": "object"}, "version": {"type": "object"}, "trace_id": {"type": "string"}}), ["WORKFLOW_TEMPLATE_NOT_FOUND", "WORKFLOW_INVALID_STATE", "WORKFLOW_VERSION_CONFLICT", "WORKFLOW_DRAFT_CONFLICT", "WORKFLOW_TEMPLATE_ARCHIVED", "WORKFLOW_SCHEMA_INVALID"]),
    _m("workflow.template.archive", _object({"workflow_template_id": {"type": "string"}, **_SCOPE}, ["workflow_template_id"]), _object({"template": {"type": "object"}, "idempotent": {"type": "boolean"}, "trace_id": {"type": "string"}}), ["WORKFLOW_TEMPLATE_NOT_FOUND"]),
    _m("workflow.version.get", _object({"workflow_version_id": {"type": "string"}, **_SCOPE}, ["workflow_version_id"]), _object({"version": {"type": "object"}}), ["WORKFLOW_VERSION_NOT_FOUND"]),
    _m("workflow.version.list", _object({"workflow_template_id": {"type": "string"}, **_SCOPE}, ["workflow_template_id"]), _object({"versions": {"type": "array"}, "count": {"type": "integer"}}), ["WORKFLOW_TEMPLATE_NOT_FOUND"]),
    _m("workflow.instance.start", _object({"workflow_version_id": {"type": "string"}, "workflow_template_id": {"type": "string"}, "workflow_version": {"type": "string"}, "input": {"type": "object"}, "input_artifact_ids": {"type": "array", "items": {"type": "string"}}, "max_steps": {"type": "integer"}, "session_id": {"type": "string"}, "thread_id": {"type": "string"}, **_SCOPE}), _object({"workflow_instance": {"type": "object"}, "station_runs": {"type": "array"}, "resolved_version": {"type": "object"}}), ["WORKFLOW_TEMPLATE_NOT_FOUND", "WORKFLOW_VERSION_NOT_FOUND", "WORKFLOW_RUNTIME_UNSUPPORTED", "WORKFLOW_EXECUTION_FAILED", "WORKFLOW_ARTIFACT_INPUT_MISSING", "WORKFLOW_ARTIFACT_KIND_MISMATCH", "WORKFLOW_ARTIFACT_CONTRACT_INVALID", "WORKFLOW_ARTIFACT_REGISTRATION_FAILED"]),
    _m("workflow.instance.get", _object({"workflow_instance_id": {"type": "string"}, **_SCOPE}, ["workflow_instance_id"]), _object({"workflow_instance": {"type": "object"}}), ["WORKFLOW_INSTANCE_NOT_FOUND"]),
    _m("workflow.instance.list", _object({**_SCOPE}), _object({"workflow_instances": {"type": "array"}, "count": {"type": "integer"}}), ["SCOPE_MISMATCH"]),
    _m("workflow.instance.pause", _object({"workflow_instance_id": {"type": "string"}, **_SCOPE}, ["workflow_instance_id"]), _object({"workflow_instance": {"type": "object"}}), ["WORKFLOW_INSTANCE_NOT_FOUND", "WORKFLOW_INVALID_STATE"]),
    _m("workflow.instance.resume", _object({"workflow_instance_id": {"type": "string"}, "max_steps": {"type": "integer"}, **_SCOPE}, ["workflow_instance_id"]), _object({"workflow_instance": {"type": "object"}, "station_runs": {"type": "array"}}), ["WORKFLOW_INSTANCE_NOT_FOUND", "WORKFLOW_INVALID_STATE", "WORKFLOW_EXECUTION_FAILED"]),
    _m("workflow.instance.cancel", _object({"workflow_instance_id": {"type": "string"}, **_SCOPE}, ["workflow_instance_id"]), _object({"workflow_instance": {"type": "object"}}), ["WORKFLOW_INSTANCE_NOT_FOUND", "WORKFLOW_INVALID_STATE"]),
    _m("workflow.instance.retry", _object({"workflow_instance_id": {"type": "string"}, **_SCOPE}, ["workflow_instance_id"]), _object({"workflow_instance": {"type": "object"}}), ["WORKFLOW_INSTANCE_NOT_FOUND", "WORKFLOW_INVALID_STATE"]),
    _m("workflow.instance.status", _object({"workflow_instance_id": {"type": "string"}, **_SCOPE}, ["workflow_instance_id"]), _object({"status": {"type": "object"}}), ["WORKFLOW_INSTANCE_NOT_FOUND"]),
    _m("station.run.get", _object({"station_run_id": {"type": "string"}, **_SCOPE}, ["station_run_id"]), _object({"station_run": {"type": "object"}}), ["STATION_RUN_NOT_FOUND"]),
    _m("station.run.list", _object({"workflow_instance_id": {"type": "string"}, **_SCOPE}, ["workflow_instance_id"]), _object({"station_runs": {"type": "array"}, "count": {"type": "integer"}}), ["WORKFLOW_INSTANCE_NOT_FOUND"]),
    _m("station.rerun", _object({"station_run_id": {"type": "string"}, **_SCOPE}, ["station_run_id"]), _object({"station_run": {"type": "object"}}), ["STATION_RUN_NOT_FOUND", "WORKFLOW_INVALID_STATE"]),
    _m("station.output.list", _object({"station_run_id": {"type": "string"}, **_SCOPE}, ["station_run_id"]), _object({"artifacts": {"type": "array"}, "count": {"type": "integer"}}), ["STATION_RUN_NOT_FOUND"]),
    _m("quality.evaluation.create", _object({"evaluation": {"type": "object"}, "auto_attach": {"type": "boolean"}, **_SCOPE}, ["evaluation"]), _object({"evaluation": {"type": "object"}, "trace_id": {"type": "string"}, "attached": {"type": "boolean"}}), ["INVALID_PARAMS", "QUALITY_EVALUATION_INVALID", "QUALITY_EVALUATION_UNSUPPORTED", "QUALITY_EVALUATION_ALREADY_ATTACHED", "WORKFLOW_INSTANCE_NOT_FOUND", "STATION_RUN_NOT_FOUND", "WORKFLOW_ARTIFACT_INPUT_MISSING", "SCOPE_MISMATCH"]),
    _m("quality.evaluation.get", _object({"evaluation_id": {"type": "string"}, **_SCOPE}, ["evaluation_id"]), _object({"evaluation": {"type": "object"}}), ["QUALITY_EVALUATION_NOT_FOUND"]),
    _m("quality.evaluation.list", _object({"workflow_instance_id": {"type": "string"}, "station_run_id": {"type": "string"}, **_SCOPE}), _object({"evaluations": {"type": "array"}, "count": {"type": "integer"}}), ["WORKFLOW_INSTANCE_NOT_FOUND", "STATION_RUN_NOT_FOUND", "QUALITY_EVALUATION_INVALID"]),
    _m("quality.evaluation.attach", _object({"evaluation_id": {"type": "string"}, "workflow_instance_id": {"type": "string"}, "artifact_id": {"type": "string"}, "station_run_id": {"type": "string"}, "allow_input_artifact": {"type": "boolean"}, **_SCOPE}, ["evaluation_id"]), _object({"evaluation": {"type": "object"}, "idempotent": {"type": "boolean"}, "trace_id": {"type": "string"}}), ["QUALITY_EVALUATION_NOT_FOUND", "STATION_RUN_NOT_FOUND", "WORKFLOW_INSTANCE_NOT_FOUND", "WORKFLOW_ARTIFACT_INPUT_MISSING", "QUALITY_EVALUATION_ALREADY_ATTACHED", "SCOPE_MISMATCH"]),
    _m("workflow.board.get", _object({"workflow_instance_id": {"type": "string"}, **_SCOPE}, ["workflow_instance_id"]), _object({"board": {"type": "object"}}), ["WORKFLOW_INSTANCE_NOT_FOUND", "BOARD_NOT_AVAILABLE"]),
    _m("business.event.emit", _object({"event": {"type": "object"}, **_SCOPE}, ["event"]), _object({"event": {"type": "object"}, "context": {"type": "object"}, "idempotent": {"type": "boolean"}, "trace_id": {"type": "string"}}), ["BUSINESS_EVENT_INVALID", "BUSINESS_EVENT_UNBOUND", "BUSINESS_EVENT_ALREADY_APPLIED"]),
    _m("workflow.context.get", _object({"workflow_instance_id": {"type": "string"}, **_SCOPE}, ["workflow_instance_id"]), _object({"context": {"type": "object"}}), ["WORKFLOW_CONTEXT_NOT_FOUND"]),
    _m("workflow.context.update", _object({"workflow_instance_id": {"type": "string"}, "values": {"type": "object"}, "business": {"type": "object"}, "path": {"type": "string"}, "value": {}, "expected_revision": {"type": "integer"}, **_SCOPE}, ["workflow_instance_id"]), _object({"context": {"type": "object"}, "trace_id": {"type": "string"}}), ["WORKFLOW_CONTEXT_NOT_FOUND", "WORKFLOW_CONTEXT_SCOPE_MISMATCH", "WORKFLOW_CONTEXT_CONFLICT", "BUSINESS_EVENT_BINDING_INVALID"]),
    _m("business.event.bind", _object({"binding": {"type": "object"}, "event_type": {"type": "string"}, "workflow_instance_id": {"type": "string"}, "target_path": {"type": "string"}, "payload_path": {"type": "string"}, "mode": {"type": "string"}, **_SCOPE}, ["workflow_instance_id"]), _object({"binding": {"type": "object"}, "trace_id": {"type": "string"}}), ["BUSINESS_EVENT_INVALID", "BUSINESS_EVENT_BINDING_INVALID"]),
    _m("workflow.patch.propose", _object({"workflow_template_id": {"type": "string"}, "patch": {"type": "object"}, **_SCOPE}, ["workflow_template_id", "patch"]), _object({"patch": {"type": "object"}, "trace_id": {"type": "string"}}), ["WORKFLOW_TEMPLATE_NOT_FOUND", "WORKFLOW_DRAFT_NOT_FOUND", "WORKFLOW_TEMPLATE_ARCHIVED", "WORKFLOW_PUBLISHED_IMMUTABLE", "WORKFLOW_PATCH_INVALID", "WORKFLOW_PATCH_CONFLICT"]),
    _m("workflow.patch.diff", _object({"workflow_patch_id": {"type": "string"}, **_SCOPE}, ["workflow_patch_id"]), _object({"diff": {"type": "object"}}), ["WORKFLOW_PATCH_NOT_FOUND", "SCOPE_MISMATCH"]),
    _m("workflow.patch.apply", _object({"workflow_patch_id": {"type": "string"}, "actor_type": {"type": "string"}, **_SCOPE}, ["workflow_patch_id"]), _object({"patch": {"type": "object"}, "draft": {"type": "object"}, "idempotent": {"type": "boolean"}, "trace_id": {"type": "string"}}), ["WORKFLOW_PATCH_NOT_FOUND", "WORKFLOW_PATCH_CONFLICT", "WORKFLOW_PATCH_INVALID", "WORKFLOW_ACTION_FORBIDDEN", "WORKFLOW_TEMPLATE_ARCHIVED", "WORKFLOW_PUBLISHED_IMMUTABLE"]),
    _m("workflow.patch.reject", _object({"workflow_patch_id": {"type": "string"}, "reason": {"type": "string"}, **_SCOPE}, ["workflow_patch_id"]), _object({"patch": {"type": "object"}, "idempotent": {"type": "boolean"}, "trace_id": {"type": "string"}}), ["WORKFLOW_PATCH_NOT_FOUND", "WORKFLOW_PATCH_CONFLICT"]),
    _m("workflow.draft.save", _object({"workflow_draft_id": {"type": "string"}, "draft": {"type": "object"}, "expected_revision": {"type": "integer"}, **_SCOPE}, ["workflow_draft_id", "draft"]), _object({"draft": {"type": "object"}, "trace_id": {"type": "string"}}), ["WORKFLOW_DRAFT_NOT_FOUND", "WORKFLOW_PUBLISHED_IMMUTABLE", "WORKFLOW_DRAFT_CONFLICT", "WORKFLOW_SCHEMA_INVALID"]),
]


_CONTRACT_METHODS = {entry["method"] for entry in WORKFLOW_METHOD_INVENTORY}
_SCHEMA_METHODS = {entry["method"] for entry in WORKFLOW_METHOD_SCHEMAS}
if missing := (_SCHEMA_METHODS - _CONTRACT_METHODS):
    raise RuntimeError(f"Workflow method schemas not present in contracts inventory: {sorted(missing)}")

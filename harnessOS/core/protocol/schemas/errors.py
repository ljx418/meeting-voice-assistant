"""V3.5 protocol error schema registry."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from core.protocol.contracts.error_inventory import ERROR_INVENTORY
from core.protocol.schemas.workflow_errors import WORKFLOW_ERROR_SCHEMAS


class ProtocolError(RuntimeError):
    """Stable protocol error used by new V3.5 RPC methods."""

    def __init__(self, code: str, message: str, data: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message)
        self.code = code
        self.data = data or {}


def _schema(
    code: str,
    *,
    http_status: int,
    message_template: str,
    retryable: bool = False,
    sdk_exception: str = "HarnessOSProtocolError",
    data_schema: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    return {
        "code": code,
        "http_status": http_status,
        "message_template": message_template,
        "retryable": retryable,
        "sdk_exception": sdk_exception,
        "data_schema": data_schema or {"type": "object", "additionalProperties": True},
    }


ERROR_SCHEMAS: List[Dict[str, Any]] = [
    _schema("INVALID_PARAMS", http_status=400, message_template="Invalid params."),
    _schema("METHOD_NOT_FOUND", http_status=404, message_template="Method not found."),
    _schema("SESSION_NOT_FOUND", http_status=404, message_template="Session not found."),
    _schema("ARTIFACT_READ_BLOCKED", http_status=403, message_template="Artifact read is blocked."),
    _schema("AUTH_REQUIRED", http_status=401, message_template="Authentication is required."),
    _schema("AUTH_INVALID", http_status=401, message_template="Authentication token is invalid."),
    _schema("AUTH_FORBIDDEN", http_status=403, message_template="Authentication token is forbidden."),
    _schema("CAPABILITY_DENIED", http_status=403, message_template="Capability is denied."),
    _schema("SCOPE_MISMATCH", http_status=403, message_template="Requested scope does not match the resource."),
    _schema("SCOPE_REQUIRED", http_status=400, message_template="Scope is required."),
    _schema("APP_PROFILE_NOT_FOUND", http_status=404, message_template="App profile not found."),
    _schema("EVENT_CURSOR_INVALID", http_status=400, message_template="Event cursor is invalid."),
    _schema("SUBSCRIPTION_TOKEN_INVALID", http_status=401, message_template="Subscription token is invalid."),
    _schema("SUBSCRIPTION_TOKEN_EXPIRED", http_status=401, message_template="Subscription token is expired."),
    _schema(
        "SUBSCRIPTION_TOKEN_SCOPE_MISMATCH",
        http_status=403,
        message_template="Subscription token scope does not match the request.",
    ),
    _schema(
        "SUBSCRIPTION_TOKEN_CHANNEL_DENIED",
        http_status=403,
        message_template="Subscription token cannot access the requested channel.",
    ),
    _schema("APPROVAL_CONFLICT", http_status=409, message_template="Approval decision conflicts with existing state."),
    _schema("APPROVAL_NOT_FOUND", http_status=404, message_template="Approval not found."),
    _schema("APPROVAL_RETRY_CONSUMED", http_status=409, message_template="Approval retry was already consumed."),
    _schema("APPROVAL_INVALID_DECISION", http_status=400, message_template="Approval decision is invalid."),
    _schema("METHOD_FORBIDDEN", http_status=403, message_template="Method is forbidden for this surface."),
    _schema("METHOD_DEPRECATED", http_status=410, message_template="Method is deprecated."),
    _schema("PACK_NOT_FOUND", http_status=404, message_template="Pack not found."),
    _schema("CONNECTOR_NOT_FOUND", http_status=404, message_template="Connector not found."),
    _schema("RUNTIME_ERROR", http_status=500, message_template="Runtime error.", retryable=True),
] + WORKFLOW_ERROR_SCHEMAS


def get_error_schema(code: str) -> Dict[str, Any]:
    for schema in ERROR_SCHEMAS:
        if schema["code"] == code:
            return schema
    raise KeyError(f"Error schema not found: {code}")


_CONTRACT_CODES = {entry["code"] for entry in ERROR_INVENTORY}
_SCHEMA_CODES = {entry["code"] for entry in ERROR_SCHEMAS}
if missing := (_CONTRACT_CODES - _SCHEMA_CODES):
    raise RuntimeError(f"Error schemas missing contract codes: {sorted(missing)}")

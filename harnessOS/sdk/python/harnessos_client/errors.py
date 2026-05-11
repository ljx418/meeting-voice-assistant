"""Python SDK error hierarchy."""

from __future__ import annotations

from typing import Any, Optional


class HarnessOSError(Exception):
    """Base SDK error."""


class TransportError(HarnessOSError):
    """Raised for transport failures before a valid JSON-RPC response exists."""

    def __init__(self, message: str) -> None:
        super().__init__(_redact_text(message))


class RpcError(HarnessOSError):
    """Raised for JSON-RPC protocol errors."""

    def __init__(self, code: str, message: str, data: Optional[dict[str, Any]] = None) -> None:
        self.code = code
        self.data = _redact(data or {})
        super().__init__(f"{code}: {_redact_text(message)}")


class ProtocolError(RpcError):
    """Generic mapped protocol error."""


class InvalidParamsError(ProtocolError):
    pass


class MethodNotFoundError(ProtocolError):
    pass


class SessionNotFoundError(ProtocolError):
    pass


class AuthRequiredError(ProtocolError):
    pass


class AuthInvalidError(ProtocolError):
    pass


class AuthForbiddenError(ProtocolError):
    pass


class CapabilityDeniedError(ProtocolError):
    pass


class ScopeMismatchError(ProtocolError):
    pass


class MethodForbiddenError(ProtocolError):
    pass


class ApprovalConflictError(ProtocolError):
    pass


class ApprovalNotFoundError(ProtocolError):
    pass


class ArtifactReadBlockedError(ProtocolError):
    pass


class EventCursorInvalidError(ProtocolError):
    pass


class PackNotFoundError(ProtocolError):
    pass


class ConnectorNotFoundError(ProtocolError):
    pass


_ERROR_TYPES = {
    "INVALID_PARAMS": InvalidParamsError,
    "METHOD_NOT_FOUND": MethodNotFoundError,
    "SESSION_NOT_FOUND": SessionNotFoundError,
    "AUTH_REQUIRED": AuthRequiredError,
    "AUTH_INVALID": AuthInvalidError,
    "AUTH_FORBIDDEN": AuthForbiddenError,
    "CAPABILITY_DENIED": CapabilityDeniedError,
    "SCOPE_MISMATCH": ScopeMismatchError,
    "METHOD_FORBIDDEN": MethodForbiddenError,
    "APPROVAL_CONFLICT": ApprovalConflictError,
    "APPROVAL_NOT_FOUND": ApprovalNotFoundError,
    "ARTIFACT_READ_BLOCKED": ArtifactReadBlockedError,
    "EVENT_CURSOR_INVALID": EventCursorInvalidError,
    "PACK_NOT_FOUND": PackNotFoundError,
    "CONNECTOR_NOT_FOUND": ConnectorNotFoundError,
}


def error_from_rpc(payload: dict[str, Any]) -> RpcError:
    code = str(payload.get("code") or "RUNTIME_ERROR")
    message = str(payload.get("message") or code)
    data = payload.get("data") if isinstance(payload.get("data"), dict) else {}
    error_type = _ERROR_TYPES.get(code, ProtocolError)
    return error_type(code, message, data)


def _redact(data: dict[str, Any]) -> dict[str, Any]:
    redacted = {}
    for key, value in data.items():
        lower = str(key).lower()
        if "token" in lower or lower == "authorization":
            redacted[key] = "[REDACTED]"
        elif isinstance(value, str):
            redacted[key] = _redact_text(value)
        else:
            redacted[key] = value
    return redacted


def _redact_text(value: str) -> str:
    parts = value.split()
    cleaned = []
    skip_next = False
    for part in parts:
        if skip_next:
            cleaned.append("[REDACTED]")
            skip_next = False
            continue
        if part.lower() == "bearer":
            cleaned.append(part)
            skip_next = True
        elif "subscription_token=" in part:
            cleaned.append(part.split("subscription_token=", 1)[0] + "subscription_token=[REDACTED]")
        elif len(part) > 48 and "." in part:
            cleaned.append("[REDACTED]")
        else:
            cleaned.append(part)
    return " ".join(cleaned)

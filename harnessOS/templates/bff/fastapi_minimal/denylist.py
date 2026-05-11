"""Denylist helpers for the V3.5-D2 Minimal BFF Smoke."""

from __future__ import annotations

from typing import Any

from harnessos_client.protocol_snapshot import DEFAULT_METHODS, is_forbidden_method


FORBIDDEN_EXACT = {
    "approval.approve",
    "approval.reject",
    "pack.execute_stub",
    "workflow.execute_stub",
}


def assert_allowed_rpc(method: str, params: dict[str, Any]) -> None:
    """Reject legacy/debug/admin/business facade methods."""
    if params.get("scope_mode") == "all":
        raise BffForbiddenError("scope_mode=all is not allowed through the BFF.")
    if method == "method.list" and params.get("include_forbidden"):
        raise BffForbiddenError("include_forbidden is not allowed through the BFF.")
    if method in FORBIDDEN_EXACT or is_forbidden_method(method) or method not in DEFAULT_METHODS:
        raise BffForbiddenError(f"method is not allowed through the BFF: {method}")


class BffForbiddenError(RuntimeError):
    """Raised when a request is outside the Minimal BFF surface."""

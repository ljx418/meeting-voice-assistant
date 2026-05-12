"""Constrained JSON-RPC proxy for the V3.5-F BFF template."""

from __future__ import annotations

from typing import Any

from .capability_policy import CapabilityPolicy
from .errors import BffError
from .identity import Identity


RPC_ALLOWED_METHODS = {
    "session.start",
    "turn.start",
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
}

RPC_FORBIDDEN_METHODS = {
    "events.subscribe",
    "approval.approve",
    "approval.reject",
    "pack.execute_stub",
    "workflow.execute_stub",
    "method.list",
}


def assert_rpc_allowed(method: str, params: dict[str, Any], *, identity: Identity, capability_policy: CapabilityPolicy) -> None:
    if (
        method in RPC_FORBIDDEN_METHODS
        or method not in RPC_ALLOWED_METHODS
        or method.startswith("meeting.")
        or method.startswith("knowledge.")
        or bool(params.get("scope_mode") == "all")
        or bool(method == "method.list" and params.get("include_forbidden"))
    ):
        raise BffError("METHOD_FORBIDDEN", f"method is not allowed through /bff/rpc: {method}", data={"method": method}, status_code=403)
    capability_policy.require(identity, method)

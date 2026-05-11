"""Method capability resolution for external V3.5 auth guards."""

from __future__ import annotations

from typing import Any, Optional

from core.protocol.contracts.method_inventory import METHOD_INVENTORY
from core.protocol.schemas.methods import METHOD_SCHEMAS


_SCHEMA_BY_METHOD = {str(entry["method"]): entry for entry in METHOD_SCHEMAS}
_CONTRACTS = list(METHOD_INVENTORY)


def get_method_capability(method: str) -> Optional[str]:
    """Resolve a method capability from schema/inventory metadata."""
    schema = _SCHEMA_BY_METHOD.get(method)
    if schema is not None:
        return _normalize_capability(method, str(schema.get("capability") or ""))
    contract = _find_contract(method)
    if contract is None:
        return None
    return _normalize_capability(method, str(contract.get("capability") or ""))


def is_forbidden_method(method: str) -> bool:
    """Return whether a method belongs to the forbidden external surface."""
    contract = _find_contract(method)
    return bool(contract and contract.get("surface") == "forbidden_by_default")


def _find_contract(method: str) -> Optional[dict[str, Any]]:
    for entry in _CONTRACTS:
        if entry.get("method") == method:
            return entry
    for entry in _CONTRACTS:
        pattern = str(entry.get("method") or "")
        if pattern.endswith(".*") and method.startswith(pattern[:-1]):
            return entry
    return None


def _normalize_capability(method: str, capability: str) -> str:
    if method in {"connector.health", "connector.list", "connector.get"}:
        return "connectors.read"
    if method in {"pack.list", "pack.get"}:
        return "packs.read"
    if method in {"trace.list", "trace.get", "core.trace.list"}:
        return "traces.read"
    return capability

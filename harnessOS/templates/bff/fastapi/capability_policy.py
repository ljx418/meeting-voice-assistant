"""BFF-side capability checks."""

from __future__ import annotations

from .errors import BffError
from .identity import Identity


ROUTE_CAPABILITIES = {
    "session.start": "sessions",
    "turn.start": "turns",
    "artifact.list": "artifacts.read",
    "artifact.read_metadata": "artifacts.read",
    "artifact.register_external": "artifacts.write",
    "artifact.lineage": "artifacts.read",
    "job.get": "jobs",
    "job.list": "jobs",
    "approval.respond": "approvals",
    "connector.health": "connectors.read",
    "pack.list": "packs.read",
    "pack.get": "packs.read",
    "events.subscribe": "events",
}


class CapabilityPolicy:
    def require(self, identity: Identity, action: str) -> None:
        required = ROUTE_CAPABILITIES.get(action, action)
        if required not in identity.capabilities:
            raise BffError(
                "CAPABILITY_DENIED",
                f"BFF identity lacks capability: {required}",
                data={"capability": required},
                status_code=403,
            )

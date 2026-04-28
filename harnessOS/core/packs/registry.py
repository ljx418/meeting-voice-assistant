"""Domain Pack manifest loading and lookup."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional


@dataclass(frozen=True)
class DomainPackManifest:
    """Portable description of one business capability pack."""

    name: str
    version: str
    domain: str
    description: str = ""
    status: str = "stub"
    workflows: tuple[str, ...] = ()
    subagents: tuple[str, ...] = ()
    skills: tuple[str, ...] = ()
    connectors: tuple[str, ...] = ()
    artifact_kinds: tuple[str, ...] = ()
    risk_profile: str = "standard"
    manifest_path: Optional[str] = None
    metadata: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_mapping(cls, data: dict[str, Any], *, manifest_path: Optional[Path] = None) -> "DomainPackManifest":
        """Build a manifest from parsed JSON data."""
        return cls(
            name=_require_str(data, "name"),
            version=_require_str(data, "version"),
            domain=_require_str(data, "domain"),
            description=_optional_str(data, "description") or "",
            status=_optional_str(data, "status") or "stub",
            workflows=tuple(_string_list(data.get("workflows"))),
            subagents=tuple(_string_list(data.get("subagents"))),
            skills=tuple(_string_list(data.get("skills"))),
            connectors=tuple(_string_list(data.get("connectors"))),
            artifact_kinds=tuple(_string_list(data.get("artifact_kinds"))),
            risk_profile=_optional_str(data, "risk_profile") or "standard",
            manifest_path=str(manifest_path) if manifest_path else None,
            metadata=dict(data.get("metadata") or {}),
        )

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable manifest view."""
        return {
            "name": self.name,
            "version": self.version,
            "domain": self.domain,
            "description": self.description,
            "status": self.status,
            "workflows": list(self.workflows),
            "subagents": list(self.subagents),
            "skills": list(self.skills),
            "connectors": list(self.connectors),
            "artifact_kinds": list(self.artifact_kinds),
            "risk_profile": self.risk_profile,
            "manifest_path": self.manifest_path,
            "metadata": dict(self.metadata),
        }


class PackRegistry:
    """In-memory registry of Domain Pack manifests."""

    def __init__(self, manifests: Optional[list[DomainPackManifest]] = None) -> None:
        self._packs_by_name: dict[str, DomainPackManifest] = {}
        self._packs_by_domain: dict[str, DomainPackManifest] = {}
        self._workflow_index: dict[str, DomainPackManifest] = {}
        for manifest in manifests or []:
            self.register(manifest)

    def register(self, manifest: DomainPackManifest) -> None:
        """Register one pack manifest."""
        self._packs_by_name[manifest.name] = manifest
        self._packs_by_domain[manifest.domain] = manifest
        for workflow_id in manifest.workflows:
            self._workflow_index[workflow_id] = manifest

    @classmethod
    def load_from_path(cls, root: Path) -> "PackRegistry":
        """Load all pack manifests from a directory."""
        manifests: list[DomainPackManifest] = []
        if root.exists():
            for manifest_path in sorted(root.glob("*/manifest.json")):
                data = json.loads(manifest_path.read_text(encoding="utf-8"))
                manifests.append(DomainPackManifest.from_mapping(data, manifest_path=manifest_path))
        return cls(manifests)

    def list_packs(self, *, domain: Optional[str] = None, status: Optional[str] = None) -> list[dict[str, Any]]:
        """Return registered packs, optionally filtered."""
        packs = sorted(self._packs_by_name.values(), key=lambda item: item.name)
        if domain:
            packs = [pack for pack in packs if pack.domain == domain]
        if status:
            packs = [pack for pack in packs if pack.status == status]
        return [pack.to_dict() for pack in packs]

    def get_pack(self, name_or_domain: str) -> Optional[DomainPackManifest]:
        """Resolve a pack by name or domain."""
        return self._packs_by_name.get(name_or_domain) or self._packs_by_domain.get(name_or_domain)

    def get_workflow_pack(self, workflow_id: str) -> Optional[DomainPackManifest]:
        """Resolve the pack that declares a workflow."""
        return self._workflow_index.get(workflow_id)


def build_default_pack_registry() -> PackRegistry:
    """Load repository-local Domain Pack manifests."""
    repo_root = Path(__file__).resolve().parents[2]
    return PackRegistry.load_from_path(repo_root / "packs")


def _require_str(data: dict[str, Any], key: str) -> str:
    value = data.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"Pack manifest field {key} is required")
    return value


def _optional_str(data: dict[str, Any], key: str) -> Optional[str]:
    value = data.get(key)
    if value is None:
        return None
    if not isinstance(value, str):
        raise ValueError(f"Pack manifest field {key} must be a string")
    return value


def _string_list(value: Any) -> list[str]:
    if value is None:
        return []
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise ValueError("Pack manifest list fields must contain strings")
    return value

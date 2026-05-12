"""Domain Pack manifest loading and lookup."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional, TYPE_CHECKING

from core.protocol.version import HARNESSOS_VERSION

if TYPE_CHECKING:
    from core.apps import AppRegistry

ALLOWED_WORKFLOW_TEMPLATE_KINDS = {"typed_dag", "multi_agent_typed_dag"}
ALLOWED_WORKFLOW_NODE_TYPES = {
    "agent",
    "skill",
    "tool",
    "connector",
    "artifact",
    "approval",
    "evaluation",
}
CURRENT_PACK_TARGET_VERSION = "3.0"


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
    manifest_schema_version: str = "1"
    workflow_dsl: dict[str, Any] = field(default_factory=dict)
    policy_bundles: tuple[str, ...] = ()
    artifact_schemas: dict[str, Any] = field(default_factory=dict)
    workflow_templates: dict[str, Any] = field(default_factory=dict)
    agents: tuple[dict[str, Any], ...] = ()
    connector_capabilities: dict[str, Any] = field(default_factory=dict)
    memory_scopes: dict[str, Any] = field(default_factory=dict)
    evaluation_rules: dict[str, Any] = field(default_factory=dict)
    min_harnessos_version: str = ""
    target_harnessos_version: str = ""

    @classmethod
    def from_mapping(cls, data: dict[str, Any], *, manifest_path: Optional[Path] = None) -> "DomainPackManifest":
        """Build a manifest from parsed JSON data."""
        return cls(
            name=_require_str(data, "name"),
            version=_require_str(data, "version"),
            domain=_require_str(data, "domain"),
            manifest_schema_version=_optional_str(data, "manifest_schema_version") or "1",
            description=_optional_str(data, "description") or "",
            status=_optional_str(data, "status") or "stub",
            workflows=tuple(_string_list(data.get("workflows"))),
            workflow_dsl=_mapping(data.get("workflow_dsl"), field_name="workflow_dsl"),
            subagents=tuple(_string_list(data.get("subagents"))),
            skills=tuple(_string_list(data.get("skills"))),
            policy_bundles=tuple(_string_list(data.get("policy_bundles"))),
            connectors=tuple(_string_list(data.get("connectors"))),
            artifact_kinds=tuple(_string_list(data.get("artifact_kinds"))),
            artifact_schemas=_mapping(data.get("artifact_schemas"), field_name="artifact_schemas"),
            workflow_templates=_mapping(data.get("workflow_templates"), field_name="workflow_templates"),
            agents=tuple(_mapping_list(data.get("agents"), field_name="agents", required_key="agent_id")),
            connector_capabilities=_mapping(
                data.get("connector_capabilities"),
                field_name="connector_capabilities",
            ),
            memory_scopes=_mapping(data.get("memory_scopes"), field_name="memory_scopes"),
            evaluation_rules=_mapping(data.get("evaluation_rules"), field_name="evaluation_rules"),
            min_harnessos_version=_optional_str(data, "min_harnessos_version") or "",
            target_harnessos_version=_optional_str(data, "target_harnessos_version") or "",
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
            "manifest_schema_version": self.manifest_schema_version,
            "description": self.description,
            "status": self.status,
            "workflows": list(self.workflows),
            "workflow_dsl": dict(self.workflow_dsl),
            "subagents": list(self.subagents),
            "skills": list(self.skills),
            "skill_refs": list(self.skills),
            "policy_bundles": list(self.policy_bundles),
            "connectors": list(self.connectors),
            "connector_refs": list(self.connectors),
            "artifact_kinds": list(self.artifact_kinds),
            "artifact_schemas": dict(self.artifact_schemas),
            "workflow_templates": dict(self.workflow_templates),
            "agents": [dict(agent) for agent in self.agents],
            "connector_capabilities": dict(self.connector_capabilities),
            "memory_scopes": dict(self.memory_scopes),
            "evaluation_rules": dict(self.evaluation_rules),
            "min_harnessos_version": self.min_harnessos_version,
            "target_harnessos_version": self.target_harnessos_version,
            "risk_profile": self.risk_profile,
            "manifest_path": self.manifest_path,
            "metadata": dict(self.metadata),
        }


@dataclass(frozen=True)
class PackAssemblyResult:
    """Runtime assembly status for one Domain Pack."""

    pack_name: str
    app_id: str
    domain: str
    status: str
    registered_workflows: tuple[str, ...] = ()
    missing_dependencies: tuple[str, ...] = ()
    conflicts: tuple[str, ...] = ()
    disabled_reason: str = ""
    manifest_schema_version: str = "1"
    workflow_dsl: dict[str, Any] = field(default_factory=dict)
    skill_refs: tuple[str, ...] = ()
    policy_bundles: tuple[str, ...] = ()
    connector_refs: tuple[str, ...] = ()
    artifact_kinds: tuple[str, ...] = ()
    artifact_schemas: dict[str, Any] = field(default_factory=dict)
    workflow_templates: dict[str, Any] = field(default_factory=dict)
    agents: tuple[dict[str, Any], ...] = ()
    connector_capabilities: dict[str, Any] = field(default_factory=dict)
    memory_scopes: dict[str, Any] = field(default_factory=dict)
    evaluation_rules: dict[str, Any] = field(default_factory=dict)
    next_actions: tuple[str, ...] = ()
    compatibility_warnings: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable assembly view."""
        return {
            "pack_name": self.pack_name,
            "app_id": self.app_id,
            "domain": self.domain,
            "status": self.status,
            "registered_workflows": list(self.registered_workflows),
            "missing_dependencies": list(self.missing_dependencies),
            "conflicts": list(self.conflicts),
            "disabled_reason": self.disabled_reason,
            "blocked_reason": self.disabled_reason,
            "manifest_schema_version": self.manifest_schema_version,
            "workflow_dsl": dict(self.workflow_dsl),
            "skill_refs": list(self.skill_refs),
            "policy_bundles": list(self.policy_bundles),
            "connector_refs": list(self.connector_refs),
            "artifact_kinds": list(self.artifact_kinds),
            "artifact_schemas": dict(self.artifact_schemas),
            "workflow_templates": dict(self.workflow_templates),
            "agents": [dict(agent) for agent in self.agents],
            "connector_capabilities": dict(self.connector_capabilities),
            "memory_scopes": dict(self.memory_scopes),
            "evaluation_rules": dict(self.evaluation_rules),
            "next_actions": list(self.next_actions),
            "compatibility_warnings": list(self.compatibility_warnings),
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
        existing_by_name = self._packs_by_name.get(manifest.name)
        if existing_by_name is not None:
            raise ValueError(_pack_conflict_message("pack_name", manifest.name, existing_by_name, manifest))
        existing_by_domain = self._packs_by_domain.get(manifest.domain)
        if existing_by_domain is not None:
            raise ValueError(_pack_conflict_message("domain", manifest.domain, existing_by_domain, manifest))
        for workflow_id in manifest.workflows:
            existing_workflow_pack = self._workflow_index.get(workflow_id)
            if existing_workflow_pack is not None:
                raise ValueError(
                    _pack_conflict_message("workflow_id", workflow_id, existing_workflow_pack, manifest)
                )
        self._packs_by_name[manifest.name] = manifest
        self._packs_by_domain[manifest.domain] = manifest
        for workflow_id in manifest.workflows:
            self._workflow_index[workflow_id] = manifest

    @classmethod
    def load_from_path(cls, root: Path) -> "PackRegistry":
        """Load all pack manifests from a directory."""
        return cls.load_from_paths([root])

    @classmethod
    def load_from_paths(cls, roots: list[Path]) -> "PackRegistry":
        """Load pack manifests from multiple roots in order."""
        manifests: list[DomainPackManifest] = []
        for root in roots:
            if not root.exists():
                continue
            for manifest_path in sorted(root.glob("*/manifest.json")):
                data = json.loads(manifest_path.read_text(encoding="utf-8"))
                if _manifest_is_template(data):
                    continue
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

    def list_packs_with_assembly(
        self,
        *,
        domain: Optional[str] = None,
        status: Optional[str] = None,
        supported_workflows: Optional[set[str]] = None,
        available_connectors: Optional[set[str]] = None,
        app_enabled_connectors_by_domain: Optional[dict[str, set[str]]] = None,
        available_policy_bundles: Optional[set[str]] = None,
        compatible_manifest_schema_versions: Optional[set[str]] = None,
        available_connector_capabilities: Optional[dict[str, dict[str, set[str]]]] = None,
    ) -> list[dict[str, Any]]:
        """Return registered packs enriched with runtime assembly status."""
        packs = self.list_packs(domain=domain, status=status)
        return [
            {
                **pack,
                "assembly": self.evaluate_assembly(
                    pack["name"],
                    supported_workflows=supported_workflows,
                    available_connectors=available_connectors,
                    app_enabled_connectors_by_domain=app_enabled_connectors_by_domain,
                    available_policy_bundles=available_policy_bundles,
                    compatible_manifest_schema_versions=compatible_manifest_schema_versions,
                    available_connector_capabilities=available_connector_capabilities,
                ).to_dict(),
            }
            for pack in packs
        ]

    def get_pack(self, name_or_domain: str) -> Optional[DomainPackManifest]:
        """Resolve a pack by name or domain."""
        return self._packs_by_name.get(name_or_domain) or self._packs_by_domain.get(name_or_domain)

    def get_workflow_pack(self, workflow_id: str) -> Optional[DomainPackManifest]:
        """Resolve the pack that declares a workflow."""
        return self._workflow_index.get(workflow_id)

    def list_agents(self, *, pack_name: Optional[str] = None, domain: Optional[str] = None) -> list[dict[str, Any]]:
        """Return agent contracts declared by registered packs."""
        packs = sorted(self._packs_by_name.values(), key=lambda item: item.name)
        if pack_name:
            packs = [pack for pack in packs if pack.name == pack_name]
        if domain:
            packs = [pack for pack in packs if pack.domain == domain]
        agents: list[dict[str, Any]] = []
        for pack in packs:
            for agent in pack.agents:
                agents.append(
                    {
                        **dict(agent),
                        "pack_name": pack.name,
                        "pack_version": pack.version,
                        "domain": pack.domain,
                    }
                )
        return agents

    def get_agent(self, agent_id: str) -> Optional[dict[str, Any]]:
        """Resolve one agent contract by id."""
        for agent in self.list_agents():
            if agent.get("agent_id") == agent_id:
                return agent
        return None

    def evaluate_assembly(
        self,
        name_or_domain: str,
        *,
        supported_workflows: Optional[set[str]] = None,
        available_connectors: Optional[set[str]] = None,
        app_enabled_connectors_by_domain: Optional[dict[str, set[str]]] = None,
        available_policy_bundles: Optional[set[str]] = None,
        compatible_manifest_schema_versions: Optional[set[str]] = None,
        available_connector_capabilities: Optional[dict[str, dict[str, set[str]]]] = None,
    ) -> PackAssemblyResult:
        """Evaluate whether a pack can be assembled by the current runtime."""
        manifest = self.get_pack(name_or_domain)
        if manifest is None:
            raise LookupError(f"Pack not found: {name_or_domain}")
        assembly_view = {
            "manifest_schema_version": manifest.manifest_schema_version,
            "workflow_dsl": manifest.workflow_dsl,
            "skill_refs": manifest.skills,
            "policy_bundles": manifest.policy_bundles,
            "connector_refs": manifest.connectors,
            "artifact_kinds": manifest.artifact_kinds,
            "artifact_schemas": manifest.artifact_schemas,
            "workflow_templates": manifest.workflow_templates,
            "agents": manifest.agents,
            "connector_capabilities": manifest.connector_capabilities,
            "memory_scopes": manifest.memory_scopes,
            "evaluation_rules": manifest.evaluation_rules,
        }
        compatibility = _manifest_version_compatibility(manifest)
        if manifest.status != "active":
            return PackAssemblyResult(
                pack_name=manifest.name,
                app_id=manifest.domain,
                domain=manifest.domain,
                status="stub",
                disabled_reason=f"Pack status is {manifest.status}.",
                **assembly_view,
            )

        supported_workflows = supported_workflows or set()
        available_connectors = available_connectors or set()
        app_enabled_connectors_by_domain = app_enabled_connectors_by_domain or {}
        available_policy_bundles = available_policy_bundles or set()
        compatible_manifest_schema_versions = compatible_manifest_schema_versions or {"1"}
        available_connector_capabilities = available_connector_capabilities or {}
        schema_supported = manifest.manifest_schema_version in compatible_manifest_schema_versions
        external_pack_version_status = _external_pack_target_version_status(manifest)
        app_enabled_connectors = app_enabled_connectors_by_domain.get(manifest.domain)
        missing_connectors = [
            connector for connector in manifest.connectors if connector not in available_connectors
        ]
        app_profile_connector_gaps = [
            f"app_profile_connector:{connector}"
            for connector in manifest.connectors
            if app_enabled_connectors is not None and connector not in app_enabled_connectors
        ]
        missing_capabilities = _missing_connector_capabilities(
            required=manifest.connector_capabilities,
            available=available_connector_capabilities,
        )
        missing_policy_bundles = [
            policy_bundle for policy_bundle in manifest.policy_bundles if policy_bundle not in available_policy_bundles
        ]
        unsupported_workflows = [
            workflow_id for workflow_id in manifest.workflows if workflow_id not in supported_workflows
        ]
        invalid_workflow_templates = _invalid_workflow_templates(manifest.workflow_templates)
        conflicts = tuple(_pack_conflicts(manifest))
        missing_dependencies = tuple(
            (
                []
                if schema_supported
                else [f"manifest_schema:{manifest.manifest_schema_version}"]
            )
            + compatibility["blocked"]
            + external_pack_version_status["blocked"]
            + [f"connector:{connector}" for connector in missing_connectors]
            + app_profile_connector_gaps
            + [f"workflow:{workflow_id}" for workflow_id in unsupported_workflows]
        )
        degraded_dependencies = tuple(
            compatibility["degraded"]
            + external_pack_version_status["degraded"]
            + missing_capabilities
            + [f"policy_bundle:{policy_bundle}" for policy_bundle in missing_policy_bundles]
        )
        compatibility_warnings = tuple(compatibility["warnings"])
        if missing_dependencies or conflicts:
            next_actions = _dedupe_preserve_order(
                list(_next_action_for_dependency(dependency) for dependency in missing_dependencies)
                + list(_next_action_for_conflict(conflict) for conflict in conflicts)
            )
            return PackAssemblyResult(
                pack_name=manifest.name,
                app_id=manifest.domain,
                domain=manifest.domain,
                status="blocked",
                missing_dependencies=missing_dependencies,
                conflicts=conflicts,
                disabled_reason=_blocked_reason(
                    missing_dependencies=missing_dependencies,
                    conflicts=conflicts,
                ),
                next_actions=next_actions,
                compatibility_warnings=compatibility_warnings,
                **assembly_view,
            )
        if degraded_dependencies or invalid_workflow_templates:
            next_actions = _dedupe_preserve_order(
                list(_next_action_for_dependency(dependency) for dependency in degraded_dependencies)
                + list(_next_action_for_conflict(conflict) for conflict in invalid_workflow_templates)
            )
            return PackAssemblyResult(
                pack_name=manifest.name,
                app_id=manifest.domain,
                domain=manifest.domain,
                status="degraded",
                missing_dependencies=degraded_dependencies,
                conflicts=tuple(invalid_workflow_templates),
                disabled_reason=_degraded_reason(
                    missing_dependencies=degraded_dependencies,
                    conflicts=tuple(invalid_workflow_templates),
                ),
                next_actions=next_actions,
                compatibility_warnings=compatibility_warnings,
                **assembly_view,
            )
        return PackAssemblyResult(
            pack_name=manifest.name,
            app_id=manifest.domain,
            domain=manifest.domain,
            status="assembled",
            registered_workflows=manifest.workflows,
            compatibility_warnings=compatibility_warnings,
            **assembly_view,
        )

    def list_assemblies(
        self,
        *,
        supported_workflows: Optional[set[str]] = None,
        available_connectors: Optional[set[str]] = None,
        app_enabled_connectors_by_domain: Optional[dict[str, set[str]]] = None,
        available_policy_bundles: Optional[set[str]] = None,
        compatible_manifest_schema_versions: Optional[set[str]] = None,
        available_connector_capabilities: Optional[dict[str, dict[str, set[str]]]] = None,
    ) -> list[PackAssemblyResult]:
        """Return assembly status for all packs."""
        return [
            self.evaluate_assembly(
                manifest.name,
                supported_workflows=supported_workflows,
                available_connectors=available_connectors,
                app_enabled_connectors_by_domain=app_enabled_connectors_by_domain,
                available_policy_bundles=available_policy_bundles,
                compatible_manifest_schema_versions=compatible_manifest_schema_versions,
                available_connector_capabilities=available_connector_capabilities,
            )
            for manifest in sorted(self._packs_by_name.values(), key=lambda item: item.name)
        ]


def build_default_pack_registry(*, app_registry: Optional["AppRegistry"] = None) -> PackRegistry:
    """Load repository-local and configured external Domain Pack manifests."""
    repo_root = Path(__file__).resolve().parents[2]
    roots = [repo_root / "packs"]
    roots.extend(_external_pack_roots())
    roots.extend(_app_profile_pack_roots(app_registry))
    return PackRegistry.load_from_paths(roots)


def _external_pack_roots() -> list[Path]:
    raw = os.environ.get("HARNESS_PACK_PATHS") or os.environ.get("HARNESS_EXTERNAL_PACK_PATHS") or ""
    roots: list[Path] = []
    for item in raw.split(os.pathsep):
        if item.strip():
            roots.append(Path(item).expanduser().resolve())
    return roots


def _app_profile_pack_roots(app_registry: Optional["AppRegistry"]) -> list[Path]:
    if app_registry is None:
        return []
    repo_root = Path(__file__).resolve().parents[2]
    roots: list[Path] = []
    seen: set[Path] = set()
    for profile in app_registry.list_profiles():
        for raw_path in profile.get("pack_paths", []):
            if not isinstance(raw_path, str) or not raw_path.strip():
                continue
            candidate = Path(raw_path).expanduser()
            if not candidate.is_absolute():
                candidate = (repo_root / candidate).resolve()
            else:
                candidate = candidate.resolve()
            if candidate in seen:
                continue
            seen.add(candidate)
            roots.append(candidate)
    return roots


def _pack_conflict_message(
    field_name: str,
    field_value: str,
    existing: DomainPackManifest,
    incoming: DomainPackManifest,
) -> str:
    existing_path = existing.manifest_path or "<memory>"
    incoming_path = incoming.manifest_path or "<memory>"
    return (
        f"Pack registry conflict for {field_name}={field_value}: "
        f"existing pack {existing.name} from {existing_path}; "
        f"incoming pack {incoming.name} from {incoming_path}"
    )


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


def _mapping(value: Any, *, field_name: str) -> dict[str, Any]:
    if value is None:
        return {}
    if not isinstance(value, dict):
        raise ValueError(f"Pack manifest field {field_name} must be an object")
    return dict(value)


def _mapping_list(value: Any, *, field_name: str, required_key: str) -> list[dict[str, Any]]:
    if value is None:
        return []
    if not isinstance(value, list):
        raise ValueError(f"Pack manifest field {field_name} must be a list")
    items: list[dict[str, Any]] = []
    for item in value:
        if not isinstance(item, dict):
            raise ValueError(f"Pack manifest field {field_name} must contain objects")
        required_value = item.get(required_key)
        if not isinstance(required_value, str) or not required_value.strip():
            raise ValueError(f"Pack manifest field {field_name} requires {required_key}")
        items.append(dict(item))
    return items


def _manifest_is_template(data: dict[str, Any]) -> bool:
    metadata = data.get("metadata") or {}
    return isinstance(metadata, dict) and metadata.get("template") is True


def _missing_connector_capabilities(
    *,
    required: dict[str, Any],
    available: dict[str, dict[str, set[str]]],
) -> list[str]:
    missing: list[str] = []
    for connector_id, capability_groups in required.items():
        if not isinstance(capability_groups, dict):
            continue
        available_groups = available.get(connector_id, {})
        for group_name, required_values in capability_groups.items():
            if not isinstance(required_values, list):
                continue
            available_values = set(available_groups.get(group_name, set()))
            for required_value in required_values:
                if isinstance(required_value, str) and required_value not in available_values:
                    missing.append(f"connector_capability:{connector_id}:{group_name}:{required_value}")
    return missing


def _dedupe_preserve_order(values: list[str]) -> tuple[str, ...]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        if value in seen:
            continue
        seen.add(value)
        result.append(value)
    return tuple(result)


def _invalid_workflow_templates(workflow_templates: dict[str, Any]) -> list[str]:
    missing: list[str] = []
    for template_id, template in workflow_templates.items():
        if not isinstance(template, dict):
            missing.append(f"workflow_template:{template_id}:invalid")
            continue
        kind = template.get("kind")
        if kind not in ALLOWED_WORKFLOW_TEMPLATE_KINDS:
            missing.append(f"workflow_template:{template_id}:kind:{kind}")
        nodes = template.get("nodes")
        if not isinstance(nodes, list):
            missing.append(f"workflow_template:{template_id}:nodes")
            continue
        for node in nodes:
            if not isinstance(node, dict):
                missing.append(f"workflow_template:{template_id}:node")
                continue
            node_id = node.get("id")
            node_type = node.get("type")
            if not isinstance(node_id, str) or not node_id.strip():
                missing.append(f"workflow_template:{template_id}:node_id")
            if node_type not in ALLOWED_WORKFLOW_NODE_TYPES:
                missing.append(f"workflow_template:{template_id}:node_type:{node_type}")
    return sorted(set(missing))


def _next_action_for_dependency(dependency: str) -> str:
    if dependency.startswith("min_harnessos_version:"):
        return (
            f"Use a pack with min_harnessos_version <= {HARNESSOS_VERSION} "
            f"(current {dependency.removeprefix('min_harnessos_version:')})."
        )
    if dependency.startswith("target_harnessos_version:"):
        return (
            f"Review pack target_harnessos_version against {HARNESSOS_VERSION} "
            f"(current {dependency.removeprefix('target_harnessos_version:')})."
        )
    if dependency.startswith("workflow_template:"):
        return f"Fix Pack workflow template dependency {dependency}."
    if dependency.startswith("connector_capability:"):
        _, connector_id, group_name, value = dependency.split(":", 3)
        return f"Register connector capability {connector_id}.{group_name}.{value}."
    if dependency.startswith("connector:"):
        return f"Register connector {dependency.removeprefix('connector:')}."
    if dependency.startswith("app_profile_connector:"):
        return f"Add connector {dependency.removeprefix('app_profile_connector:')} to the matching AppProfile."
    if dependency.startswith("policy_bundle:"):
        return f"Register policy bundle {dependency.removeprefix('policy_bundle:')}."
    if dependency.startswith("workflow:"):
        return f"Register workflow {dependency.removeprefix('workflow:')}."
    if dependency.startswith("manifest_schema:"):
        return f"Add compatibility for manifest schema {dependency.removeprefix('manifest_schema:')}."
    if dependency == "target_version:missing":
        return f"Declare metadata.target_version={CURRENT_PACK_TARGET_VERSION} for the external pack."
    if dependency.startswith("target_version:"):
        return (
            f"Align external pack target_version to {CURRENT_PACK_TARGET_VERSION} "
            f"(current {dependency.removeprefix('target_version:')})."
        )
    return f"Resolve dependency {dependency}."


def _pack_conflicts(manifest: DomainPackManifest) -> list[str]:
    conflicts: list[str] = []
    artifact_schema_keys = set(manifest.artifact_schemas.keys())
    for artifact_kind in sorted(artifact_schema_keys - set(manifest.artifact_kinds)):
        conflicts.append(f"artifact_schema:{artifact_kind}:undeclared_kind")
    template_ids = set()
    for template_id, template in manifest.workflow_templates.items():
        if template_id in template_ids:
            conflicts.append(f"workflow_template:{template_id}:duplicate")
            continue
        template_ids.add(template_id)
        if not isinstance(template, dict):
            continue
        seen_node_ids: set[str] = set()
        nodes = template.get("nodes")
        if not isinstance(nodes, list):
            continue
        for node in nodes:
            if not isinstance(node, dict):
                continue
            node_id = node.get("id")
            if not isinstance(node_id, str) or not node_id.strip():
                continue
            if node_id in seen_node_ids:
                conflicts.append(f"workflow_template:{template_id}:duplicate_node:{node_id}")
                continue
            seen_node_ids.add(node_id)
    return conflicts


def _next_action_for_conflict(conflict: str) -> str:
    if conflict.startswith("artifact_schema:"):
        return f"Declare artifact kind for schema conflict {conflict}."
    if conflict.startswith("workflow_template:"):
        return f"Fix workflow template conflict {conflict}."
    return f"Resolve conflict {conflict}."


def _blocked_reason(
    *,
    missing_dependencies: tuple[str, ...],
    conflicts: tuple[str, ...],
) -> str:
    if missing_dependencies and conflicts:
        return "Pack has blocked assembly dependencies and conflicts."
    if missing_dependencies:
        if any(dependency.startswith("manifest_schema:") for dependency in missing_dependencies):
            return "Pack is blocked by an incompatible manifest schema."
        if any(
            dependency.startswith("connector:") or dependency.startswith("app_profile_connector:")
            for dependency in missing_dependencies
        ):
            return "Pack is blocked by missing or disabled connectors."
        if any(dependency.startswith("target_version:") for dependency in missing_dependencies):
            return "Pack is blocked by an incompatible external pack target_version."
        if any(dependency.startswith("min_harnessos_version:") for dependency in missing_dependencies):
            return "Pack is blocked by an incompatible min_harnessos_version."
        if any(dependency.startswith("workflow:") for dependency in missing_dependencies):
            return "Pack is blocked by unsupported workflow registration."
        return "Pack has blocked assembly dependencies."
    return "Pack has assembly conflicts."


def _degraded_reason(
    *,
    missing_dependencies: tuple[str, ...],
    conflicts: tuple[str, ...],
) -> str:
    if missing_dependencies and conflicts:
        return "Pack is assembled with degraded dependencies and non-blocking conflicts."
    if missing_dependencies:
        if missing_dependencies == ("target_version:missing",):
            return "Pack is degraded because metadata.target_version is not declared."
        if any(dependency.startswith("target_harnessos_version:") for dependency in missing_dependencies):
            return "Pack is degraded by target_harnessos_version compatibility warnings."
        if all(dependency.startswith("policy_bundle:") for dependency in missing_dependencies):
            return "Pack is degraded by missing policy bundles."
        if all(dependency.startswith("connector_capability:") for dependency in missing_dependencies):
            return "Pack is degraded by missing non-blocking connector capabilities."
        return "Pack is assembled with degraded dependencies."
    return "Pack is assembled with non-blocking conflicts."


def _external_pack_target_version_status(manifest: DomainPackManifest) -> dict[str, list[str]]:
    blocked: list[str] = []
    degraded: list[str] = []
    manifest_path = manifest.manifest_path
    if not manifest_path:
        return {"blocked": blocked, "degraded": degraded}
    path = Path(manifest_path).expanduser().resolve()
    repo_packs_root = Path(__file__).resolve().parents[2] / "packs"
    try:
        path.relative_to(repo_packs_root.resolve())
        return {"blocked": blocked, "degraded": degraded}
    except ValueError:
        pass
    target_version = manifest.metadata.get("target_version")
    if not isinstance(target_version, str) or not target_version.strip():
        degraded.append("target_version:missing")
        return {"blocked": blocked, "degraded": degraded}
    if target_version != CURRENT_PACK_TARGET_VERSION:
        blocked.append(f"target_version:{target_version}")
    return {"blocked": blocked, "degraded": degraded}


def _manifest_version_compatibility(manifest: DomainPackManifest) -> dict[str, list[str]]:
    blocked: list[str] = []
    degraded: list[str] = []
    warnings: list[str] = []
    if manifest.min_harnessos_version and _compare_versions(manifest.min_harnessos_version, HARNESSOS_VERSION) > 0:
        blocked.append(f"min_harnessos_version:{manifest.min_harnessos_version}")
    if manifest.target_harnessos_version and manifest.target_harnessos_version != HARNESSOS_VERSION:
        degraded.append(f"target_harnessos_version:{manifest.target_harnessos_version}")
        warnings.append(
            f"Pack target_harnessos_version {manifest.target_harnessos_version} differs from harnessOS {HARNESSOS_VERSION}."
        )
    return {"blocked": blocked, "degraded": degraded, "warnings": warnings}


def _compare_versions(left: str, right: str) -> int:
    left_parts = _version_parts(left)
    right_parts = _version_parts(right)
    if left_parts > right_parts:
        return 1
    if left_parts < right_parts:
        return -1
    return 0


def _version_parts(value: str) -> tuple[int, int, int]:
    parts = value.split(".")
    parsed: list[int] = []
    for item in parts[:3]:
        digits = ""
        for char in item:
            if not char.isdigit():
                break
            digits += char
        parsed.append(int(digits or "0"))
    while len(parsed) < 3:
        parsed.append(0)
    return tuple(parsed[:3])

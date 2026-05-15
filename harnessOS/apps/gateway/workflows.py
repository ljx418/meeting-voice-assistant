"""Domain workflow registry and lead orchestrator for gateway turns."""

from __future__ import annotations

import importlib
import inspect
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional, Protocol

from apps.gateway.artifacts import ArtifactRegistry
from apps.gateway.connector_execution import ConnectorExecutionRuntime
from apps.gateway.connectors import ConnectorRegistry
from core.apps import ScopeContext
from core.apps.profiles import AppRegistry
from core.packs import PackAssemblyResult, PackRegistry


AVAILABLE_CONNECTOR_CAPABILITIES = {
    "data_service_mcp": {
        "capabilities": {
            "knowledge.lifecycle",
            "knowledge.source",
            "knowledge.build",
            "knowledge.query",
            "knowledge.summarize",
            "knowledge.citation",
        },
        "tools": {
            "knowledge_workspace_create",
            "knowledge_workspace_list",
            "knowledge_workspace_describe",
            "knowledge_source_import",
            "knowledge_source_list",
            "knowledge_source_remove",
            "knowledge_build_start",
            "knowledge_build_status",
            "knowledge_build_cancel",
            "knowledge_workspace_archive",
            "knowledge_ingest_v2",
            "knowledge_query_v2",
            "knowledge_quality_summary_v2",
            "knowledge_correction_plan_v2",
            "knowledge_quality_feedback_v2",
            "knowledge_correction_rules_v2",
            "knowledge_review_correction_rule_v2",
            "knowledge_query",
            "knowledge_quality_summary",
            "knowledge_quality_feedback",
            "knowledge_correction_rules",
            "knowledge_review_correction_rule",
            "knowledge_correction_plan",
        },
        "resources": {
            "data_service://summary",
            "data_service://layout",
            "data_service://build-status",
            "data_service://quality-report",
        },
    },
    "remote_comfyui": {
        "modes": {"txt2img", "txt2video", "image_to_video"},
    },
}
AVAILABLE_POLICY_BUNDLES = {
    "core.readonly",
    "meeting.default",
    "meeting.standard",
    "knowledge.default",
    "knowledge.standard",
    "video.planning",
}
COMPATIBLE_PACK_SCHEMA_VERSIONS = {"1"}


@dataclass(frozen=True)
class WorkflowContext:
    """Context passed to domain workflows."""

    session_id: str
    turn_id: str
    domain: Optional[str] = None
    scope: ScopeContext = field(default_factory=ScopeContext)
    artifact_registry: Optional[ArtifactRegistry] = None
    approval_id: Optional[str] = None


class DomainWorkflow(Protocol):
    """Protocol implemented by gateway domain workflows."""

    workflow_id: str
    domain: str
    priority: int

    def should_handle(self, user_input: str, context: WorkflowContext) -> bool:
        """Return whether this workflow should handle the turn."""

    async def run(self, user_input: str, context: WorkflowContext) -> dict[str, Any]:
        """Run the workflow."""


class WorkflowRegistry:
    """Ordered registry of domain workflows."""

    def __init__(
        self,
        pack_registry: Optional[PackRegistry] = None,
        *,
        assemblies: Optional[list[PackAssemblyResult]] = None,
    ) -> None:
        self._workflows: list[DomainWorkflow] = []
        self._pack_registry = pack_registry
        self._assemblies_by_domain = {assembly.domain: assembly for assembly in assemblies or []}

    def register(self, workflow: DomainWorkflow) -> None:
        """Register one workflow."""
        self._workflows.append(workflow)
        self._workflows.sort(key=lambda item: item.priority, reverse=True)

    def list_workflows(self) -> list[dict[str, Any]]:
        """Return registered workflow metadata."""
        workflows = []
        for workflow in self._workflows:
            metadata = {
                "workflow_id": workflow.workflow_id,
                "domain": workflow.domain,
                "priority": workflow.priority,
                "assembly_status": "manual",
                "assembly_source": "manual",
            }
            if self._pack_registry is not None:
                pack = self._pack_registry.get_workflow_pack(workflow.workflow_id)
                if pack is not None:
                    assembly = self._assemblies_by_domain.get(pack.domain)
                    metadata.update(
                        {
                            "pack_name": pack.name,
                            "pack_version": pack.version,
                            "pack_status": pack.status,
                            "assembly_status": assembly.status if assembly else "unknown",
                            "assembly_source": "pack",
                        }
                    )
            workflows.append(metadata)
        return workflows

    def blocked_pack_for_domain(self, domain: Optional[str]) -> Optional[PackAssemblyResult]:
        """Return a blocked assembly for an explicit domain, if any."""
        if not domain:
            return None
        assembly = self._assemblies_by_domain.get(domain)
        if assembly is not None and assembly.status == "blocked":
            return assembly
        return None

    def select(self, user_input: str, context: WorkflowContext) -> Optional[DomainWorkflow]:
        """Select the first workflow that can handle the turn."""
        if context.domain:
            for workflow in self._workflows:
                if workflow.domain == context.domain and workflow.should_handle(user_input, context):
                    return workflow
            return None
        for workflow in self._workflows:
            if workflow.should_handle(user_input, context):
                return workflow
        return None


class LeadOrchestrator:
    """Route turns to registered domain workflows."""

    def __init__(self, registry: WorkflowRegistry) -> None:
        self.registry = registry

    async def run_if_applicable(self, user_input: str, context: WorkflowContext) -> Optional[dict[str, Any]]:
        """Run a workflow if one matches; otherwise return None."""
        workflow = self.registry.select(user_input, context)
        if workflow is None:
            return None
        result = await workflow.run(user_input, context)
        result.setdefault("domain", workflow.domain)
        result.setdefault("workflow_id", workflow.workflow_id)
        return result


class PackDomainWorkflow:
    """Adapter that exposes one pack-declared workflow through DomainWorkflow."""

    def __init__(
        self,
        *,
        workflow_id: str,
        domain: str,
        workflow: Any,
        priority: Optional[int] = None,
    ) -> None:
        self.workflow_id = workflow_id
        self.domain = domain
        self.workflow = workflow
        self.priority = (
            int(priority)
            if isinstance(priority, int)
            else int(getattr(workflow, "priority", 50))
        )

    def should_handle(self, user_input: str, context: WorkflowContext) -> bool:
        method = getattr(self.workflow, "should_handle")
        parameters = inspect.signature(method).parameters
        if "context" in parameters:
            return bool(method(user_input, context))
        if "domain" in parameters:
            return bool(method(user_input, domain=context.domain))
        return bool(method(user_input))

    async def run(self, user_input: str, context: WorkflowContext) -> dict[str, Any]:
        method = getattr(self.workflow, "run")
        parameters = inspect.signature(method).parameters
        if "context" in parameters:
            return await method(user_input, context)
        kwargs: dict[str, Any] = {}
        if "domain" in parameters:
            kwargs["domain"] = context.domain
        if "session_id" in parameters:
            kwargs["session_id"] = context.session_id
        if "turn_id" in parameters:
            kwargs["turn_id"] = context.turn_id
        if "scope" in parameters:
            kwargs["scope"] = context.scope
        if "approval_id" in parameters:
            kwargs["approval_id"] = context.approval_id
        if kwargs:
            return await method(user_input, **kwargs)
        return await method(user_input)


class MeetingDomainWorkflow:
    """Adapter that exposes the Meeting pack workflow through DomainWorkflow."""

    workflow_id = "meeting.workflow"
    domain = "meeting"
    priority = 100

    def __init__(self, workflow: Any) -> None:
        self.workflow = workflow

    def should_handle(self, user_input: str, context: WorkflowContext) -> bool:
        return self.workflow.should_handle(user_input, domain=context.domain)

    async def run(self, user_input: str, context: WorkflowContext) -> dict[str, Any]:
        return await self.workflow.run(
            user_input,
            domain=context.domain,
            session_id=context.session_id,
            turn_id=context.turn_id,
            scope=context.scope,
            approval_id=context.approval_id,
        )


def build_default_orchestrator(
    meeting_workflow: Any | None = None,
    *,
    pack_registry: Optional[PackRegistry] = None,
    connector_registry: Optional[ConnectorRegistry] = None,
    connector_execution_runtime: Optional[ConnectorExecutionRuntime] = None,
    app_registry: Optional[AppRegistry] = None,
) -> LeadOrchestrator:
    """Build the default gateway workflow orchestrator."""
    assemblies: list[PackAssemblyResult] = []
    if pack_registry is not None:
        assembly_inputs = build_pack_assembly_inputs(
            connector_registry=connector_registry,
            app_registry=app_registry,
        )
        assemblies = pack_registry.list_assemblies(
            supported_workflows=_supported_workflow_ids(pack_registry),
            available_connectors=assembly_inputs["available_connectors"],
            app_enabled_connectors_by_domain=assembly_inputs["app_enabled_connectors_by_domain"],
            available_connector_capabilities=assembly_inputs["available_connector_capabilities"],
            available_policy_bundles=AVAILABLE_POLICY_BUNDLES,
            compatible_manifest_schema_versions=COMPATIBLE_PACK_SCHEMA_VERSIONS,
        )
    registry = WorkflowRegistry(pack_registry=pack_registry, assemblies=assemblies)
    if pack_registry is None:
        for workflow in _fallback_workflows(
            meeting_workflow,
            connector_execution_runtime=connector_execution_runtime,
        ):
            registry.register(workflow)
    elif meeting_workflow is not None:
        for workflow in _load_pack_declared_workflows(
            pack_registry=pack_registry,
            assemblies=assemblies,
            meeting_workflow=meeting_workflow,
            connector_execution_runtime=connector_execution_runtime,
        ):
            registry.register(workflow)
    return LeadOrchestrator(registry)


def build_pack_assembly_inputs(
    *,
    connector_registry: Optional[ConnectorRegistry] = None,
    app_registry: Optional[AppRegistry] = None,
) -> dict[str, Any]:
    """Build runtime assembly inputs from app and connector registries."""
    available_connectors: set[str] = set()
    available_connector_capabilities = dict(AVAILABLE_CONNECTOR_CAPABILITIES)
    app_enabled_connectors_by_domain: dict[str, set[str]] = {}

    if app_registry is not None:
        for profile in app_registry.list_profiles():
            profile_connectors: set[str] = set()
            for connector_ref in profile.get("connector_refs", []):
                if isinstance(connector_ref, str) and connector_ref.strip():
                    profile_connectors.add(connector_ref)
            domain = profile.get("domain")
            if isinstance(domain, str) and domain.strip():
                app_enabled_connectors_by_domain.setdefault(domain, set()).update(profile_connectors)

    if connector_registry is not None:
        for connector in connector_registry.list_connectors():
            connector_id = connector.get("connector_id")
            if isinstance(connector_id, str) and connector_id.strip():
                available_connectors.add(connector_id)
                capabilities = connector.get("capabilities")
                if isinstance(capabilities, dict):
                    available_connector_capabilities[connector_id] = {
                        key: set(value) if isinstance(value, list) else value
                        for key, value in capabilities.items()
                    }

    return {
        "available_connectors": available_connectors,
        "app_enabled_connectors_by_domain": app_enabled_connectors_by_domain,
        "available_connector_capabilities": available_connector_capabilities,
    }


def _fallback_workflows(
    meeting_workflow: Any | None,
    *,
    connector_execution_runtime: Optional[ConnectorExecutionRuntime] = None,
) -> list[DomainWorkflow]:
    if meeting_workflow is None:
        return []
    from packs.knowledge.workflow import KnowledgeWorkflow
    from packs.video_studio.workflow import VideoStudioWorkflow

    return [
        MeetingDomainWorkflow(meeting_workflow),
        KnowledgeWorkflow(
            connector_execution_runtime=connector_execution_runtime,
        ),
        VideoStudioWorkflow(),
    ]


def _load_pack_declared_workflows(
    *,
    pack_registry: PackRegistry,
    assemblies: list[PackAssemblyResult],
    meeting_workflow: Any | None,
    connector_execution_runtime: Optional[ConnectorExecutionRuntime] = None,
) -> list[DomainWorkflow]:
    workflows: list[DomainWorkflow] = []
    for assembly in assemblies:
        if assembly.status != "assembled":
            continue
        manifest = pack_registry.get_pack(assembly.pack_name)
        if manifest is None:
            continue
        for workflow_id in assembly.registered_workflows:
            entrypoint = _workflow_entrypoint(manifest, workflow_id)
            if entrypoint is None:
                continue
            workflow = _instantiate_pack_workflow(
                entrypoint=entrypoint,
                manifest_path=manifest.manifest_path,
                meeting_workflow=meeting_workflow,
                connector_execution_runtime=connector_execution_runtime,
            )
            priority = 100 if workflow is meeting_workflow else None
            workflows.append(
                PackDomainWorkflow(
                    workflow_id=workflow_id,
                    domain=manifest.domain,
                    workflow=workflow,
                    priority=priority,
                )
            )
    return workflows


def _workflow_entrypoint(manifest: Any, workflow_id: str) -> Optional[str]:
    workflow_dsl = getattr(manifest, "workflow_dsl", {})
    if not isinstance(workflow_dsl, dict):
        return None
    config = workflow_dsl.get(workflow_id)
    if not isinstance(config, dict):
        return None
    entrypoint = config.get("entrypoint")
    if not isinstance(entrypoint, str) or not entrypoint.strip():
        return None
    return entrypoint


def _instantiate_pack_workflow(
    *,
    entrypoint: str,
    manifest_path: Optional[str],
    meeting_workflow: Any | None,
    connector_execution_runtime: Optional[ConnectorExecutionRuntime] = None,
) -> Any:
    module_name, _, symbol_name = entrypoint.partition(":")
    if not module_name or not symbol_name:
        raise ValueError(f"Invalid workflow entrypoint: {entrypoint}")
    _ensure_manifest_import_root(manifest_path)
    module = importlib.import_module(module_name)
    symbol = getattr(module, symbol_name)

    if meeting_workflow is not None and inspect.isclass(symbol) and isinstance(meeting_workflow, symbol):
        return meeting_workflow

    if not inspect.isclass(symbol):
        raise TypeError(f"Workflow entrypoint must resolve to a class: {entrypoint}")

    parameters = inspect.signature(symbol).parameters
    kwargs: dict[str, Any] = {}
    if "connector_execution_runtime" in parameters:
        kwargs["connector_execution_runtime"] = connector_execution_runtime
    return symbol(**kwargs)


def _ensure_manifest_import_root(manifest_path: Optional[str]) -> None:
    if not isinstance(manifest_path, str) or not manifest_path.strip():
        return
    path = Path(manifest_path).expanduser().resolve()
    import_root = path.parent.parent
    import_root_str = str(import_root)
    if import_root_str not in sys.path:
        sys.path.insert(0, import_root_str)


def _supported_workflow_ids(pack_registry: PackRegistry) -> set[str]:
    supported: set[str] = set()
    for pack in pack_registry.list_packs():
        for workflow_id in pack.get("workflows", []):
            if isinstance(workflow_id, str) and workflow_id.strip():
                supported.add(workflow_id)
    return supported

"""Domain workflow registry and lead orchestrator for gateway turns."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Optional, Protocol

from apps.gateway.artifacts import ArtifactRegistry
from core.apps import ScopeContext
from core.packs import PackAssemblyResult, PackRegistry
from packs.meeting.workflow import MeetingWorkflow


AVAILABLE_WORKFLOW_CONNECTORS = {"meeting_voice_mcp", "local.knowledge", "data_service_mcp", "remote_comfyui"}
AVAILABLE_CONNECTOR_CAPABILITIES = {
    "data_service_mcp": {
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
AVAILABLE_POLICY_BUNDLES = {"core.readonly", "meeting.standard", "knowledge.standard", "video.planning"}
COMPATIBLE_PACK_SCHEMA_VERSIONS = {"1"}
SUPPORTED_WORKFLOW_IDS = {"meeting.workflow", "knowledge.workflow", "video.workflow"}


@dataclass(frozen=True)
class WorkflowContext:
    """Context passed to domain workflows."""

    session_id: str
    turn_id: str
    domain: Optional[str] = None
    scope: ScopeContext = field(default_factory=ScopeContext)
    artifact_registry: Optional[ArtifactRegistry] = None


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


class MeetingDomainWorkflow:
    """Adapter that exposes the Meeting pack workflow through DomainWorkflow."""

    workflow_id = "meeting.workflow"
    domain = "meeting"
    priority = 100

    def __init__(self, workflow: MeetingWorkflow) -> None:
        self.workflow = workflow

    def should_handle(self, user_input: str, context: WorkflowContext) -> bool:
        return self.workflow.should_handle(user_input, domain=context.domain)

    async def run(self, user_input: str, context: WorkflowContext) -> dict[str, Any]:
        return await self.workflow.run(
            user_input,
            domain=context.domain,
            session_id=context.session_id,
            turn_id=context.turn_id,
        )


def build_default_orchestrator(
    meeting_workflow: MeetingWorkflow,
    *,
    pack_registry: Optional[PackRegistry] = None,
) -> LeadOrchestrator:
    """Build the default gateway workflow orchestrator."""
    workflow_factories = _default_workflow_factories(meeting_workflow)
    assemblies: list[PackAssemblyResult] = []
    if pack_registry is not None:
        assemblies = pack_registry.list_assemblies(
            supported_workflows=SUPPORTED_WORKFLOW_IDS,
            available_connectors=AVAILABLE_WORKFLOW_CONNECTORS,
            available_connector_capabilities=AVAILABLE_CONNECTOR_CAPABILITIES,
            available_policy_bundles=AVAILABLE_POLICY_BUNDLES,
            compatible_manifest_schema_versions=COMPATIBLE_PACK_SCHEMA_VERSIONS,
        )
    registry = WorkflowRegistry(pack_registry=pack_registry, assemblies=assemblies)
    if pack_registry is None:
        for workflow_factory in workflow_factories.values():
            registry.register(workflow_factory())
    else:
        for assembly in assemblies:
            if assembly.status != "assembled":
                continue
            for workflow_id in assembly.registered_workflows:
                workflow_factory = workflow_factories.get(workflow_id)
                if workflow_factory is not None:
                    registry.register(workflow_factory())
    return LeadOrchestrator(registry)


def _default_workflow_factories(meeting_workflow: MeetingWorkflow) -> dict[str, Callable[[], DomainWorkflow]]:
    from packs.knowledge.workflow import KnowledgeWorkflow
    from packs.video_studio.workflow import VideoStudioWorkflow

    return {
        "meeting.workflow": lambda: MeetingDomainWorkflow(meeting_workflow),
        "knowledge.workflow": KnowledgeWorkflow,
        "video.workflow": VideoStudioWorkflow,
    }

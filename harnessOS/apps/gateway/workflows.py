"""Domain workflow registry and lead orchestrator for gateway turns."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional, Protocol

from apps.gateway.artifacts import ArtifactRegistry
from apps.gateway.meeting import MeetingWorkflow
from core.packs import PackRegistry
from tools.knowledge import kb_ingest, kb_search


@dataclass(frozen=True)
class WorkflowContext:
    """Context passed to domain workflows."""

    session_id: str
    turn_id: str
    domain: Optional[str] = None
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

    def __init__(self, pack_registry: Optional[PackRegistry] = None) -> None:
        self._workflows: list[DomainWorkflow] = []
        self._pack_registry = pack_registry

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
            }
            if self._pack_registry is not None:
                pack = self._pack_registry.get_workflow_pack(workflow.workflow_id)
                if pack is not None:
                    metadata.update(
                        {
                            "pack_name": pack.name,
                            "pack_version": pack.version,
                            "pack_status": pack.status,
                        }
                    )
            workflows.append(metadata)
        return workflows

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
    """Adapter that exposes the existing MeetingWorkflow through DomainWorkflow."""

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


class KnowledgeWorkflow:
    """Minimal knowledge workflow backed by existing kb tools."""

    workflow_id = "knowledge.workflow"
    domain = "knowledge"
    priority = 50

    def should_handle(self, user_input: str, context: WorkflowContext) -> bool:
        if context.domain == "knowledge":
            return True
        if context.domain and context.domain != "knowledge":
            return False
        lowered = user_input.lower()
        return any(keyword in lowered for keyword in ("knowledge", "知识", "知识库", "检索", "搜索", "查询", "wiki"))

    async def run(self, user_input: str, context: WorkflowContext) -> dict[str, Any]:
        if _looks_like_ingest(user_input):
            document = _extract_document(user_input)
            result = kb_ingest(document, title="Knowledge Workflow Note")
            content = f"知识库内容已登记。\n{result}"
            return {
                "status": "success",
                "content": content,
                "knowledge": {"operation": "ingest", "result": result, "sources": []},
            }

        result = kb_search(user_input, top_k=5)
        content = f"知识检索已完成。\n{result}"
        return {
            "status": "success",
            "content": content,
            "knowledge": {
                "operation": "search",
                "query": user_input,
                "result": result,
                "sources": _extract_source_lines(result),
            },
        }


def build_default_orchestrator(
    meeting_workflow: MeetingWorkflow,
    *,
    pack_registry: Optional[PackRegistry] = None,
) -> LeadOrchestrator:
    """Build the default gateway workflow orchestrator."""
    registry = WorkflowRegistry(pack_registry=pack_registry)
    registry.register(MeetingDomainWorkflow(meeting_workflow))
    registry.register(KnowledgeWorkflow())
    return LeadOrchestrator(registry)


def _looks_like_ingest(user_input: str) -> bool:
    lowered = user_input.lower()
    return any(keyword in lowered for keyword in ("ingest", "录入", "写入知识库", "加入知识库", "保存到知识库"))


def _extract_document(user_input: str) -> str:
    for marker in ("：", ":", "\n"):
        if marker in user_input:
            candidate = user_input.split(marker, 1)[1].strip()
            if candidate:
                return candidate
    return user_input.strip()


def _extract_source_lines(result: str) -> list[str]:
    return [line.strip() for line in result.splitlines() if line.strip().startswith("ID:")]

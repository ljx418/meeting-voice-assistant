from __future__ import annotations

import asyncio
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from apps.gateway.artifacts import ArtifactRegistry
from apps.gateway.meeting import MeetingWorkflow
from apps.gateway.protocol import RpcRequest
from apps.gateway.runtime import GatewayRuntimePool
from apps.gateway.service import GatewayService
from apps.gateway.storage import GatewaySessionStore
from apps.gateway.workflows import (
    KnowledgeWorkflow,
    LeadOrchestrator,
    MeetingDomainWorkflow,
    WorkflowContext,
    WorkflowRegistry,
)
from tools.knowledge import kb_ingest


class FakeAgent:
    def invoke(self, user_input: str):
        return {"status": "success", "content": f"reply: {user_input}"}


class FakeMeetingService:
    async def process_recording(self, path, *, engine=None, language=None, title=None):
        return {
            "source_path": path,
            "session_id": "meeting_orchestrated",
            "transcript_chars": 10,
            "segment_count": 1,
            "analysis": {"theme": "编排会议"},
            "minutes_path": "",
            "artifacts": {},
        }

    async def analyze_text(self, text, *, title=None):
        return {
            "session_id": "meeting_text",
            "transcript_chars": 0,
            "segment_count": 0,
            "analysis": {"theme": "文本会议"},
            "minutes_path": "",
            "artifacts": {},
        }


def test_workflow_registry_selects_explicit_domain(tmp_path):
    registry = WorkflowRegistry()
    meeting = MeetingDomainWorkflow(MeetingWorkflow(FakeMeetingService(), ArtifactRegistry(tmp_path / "artifacts")))
    knowledge = KnowledgeWorkflow()
    registry.register(knowledge)
    registry.register(meeting)

    context = WorkflowContext(session_id="sess", turn_id="turn", domain="knowledge")
    selected = registry.select("请检索知识库", context)

    assert selected is knowledge
    assert registry.list_workflows()[0]["domain"] == "meeting"


def test_lead_orchestrator_runs_knowledge_workflow():
    kb_ingest("会议 MCP 支持语音转写和会议纪要。", title="Meeting MCP")
    registry = WorkflowRegistry()
    registry.register(KnowledgeWorkflow())
    orchestrator = LeadOrchestrator(registry)

    async def run():
        result = await orchestrator.run_if_applicable(
            "检索知识库 会议 MCP",
            WorkflowContext(session_id="sess", turn_id="turn"),
        )
        assert result is not None
        assert result["domain"] == "knowledge"
        assert result["workflow_id"] == "knowledge.workflow"
        assert "知识检索已完成" in result["content"]
        assert "Meeting MCP" in result["content"]

    asyncio.run(run())


def test_gateway_workflow_list_and_knowledge_route(tmp_path):
    kb_ingest("harnessOS 的 Phase 1-D 目标是 Lead Orchestrator。", title="Phase 1-D")

    async def run():
        service = GatewayService(
            GatewayRuntimePool(
                agent_factory=lambda _model: FakeAgent(),
                runtime_backend="simple",
                store=GatewaySessionStore(tmp_path),
            )
        )
        listed = await service.handle_rpc(RpcRequest(id="w1", method="workflow.list"))
        assert listed.error is None
        assert {item["domain"] for item in listed.result["workflows"]} == {"meeting", "knowledge"}
        assert {item["pack_name"] for item in listed.result["workflows"]} == {"meeting", "knowledge"}

        started = await service.handle_rpc(RpcRequest(id="s1", method="session.start"))
        response = await service.handle_rpc(
            RpcRequest(
                id="t1",
                method="turn.start",
                params={
                    "session_id": started.result["session_id"],
                    "input": "检索知识库 Phase 1-D",
                },
            )
        )
        assert response.error is None
        completed = response.result["events"][-1]
        assert completed["data"]["domain"] == "knowledge"
        assert completed["data"]["workflow_id"] == "knowledge.workflow"
        assert "知识检索已完成" in response.result["final_text"]

    asyncio.run(run())

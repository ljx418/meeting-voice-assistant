from __future__ import annotations

import asyncio
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from apps.gateway.artifacts import ArtifactRegistry
from apps.gateway.protocol import RpcRequest
from apps.gateway.runtime import GatewayRuntimePool
from apps.gateway.service import GatewayService
from apps.gateway.storage import GatewaySessionStore
from apps.gateway.workflows import (
    LeadOrchestrator,
    MeetingDomainWorkflow,
    WorkflowContext,
    WorkflowRegistry,
    build_pack_assembly_inputs,
)
from core.apps import AppProfile, AppRegistry
from packs.meeting.workflow import MeetingWorkflow
from packs.knowledge.workflow import KnowledgeWorkflow
from packs.video_studio.workflow import VideoStudioWorkflow


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


def test_default_runtime_uses_meeting_pack_workflow(tmp_path):
    pool = GatewayRuntimePool(
        agent_factory=lambda _model: FakeAgent(),
        runtime_backend="simple",
        store=GatewaySessionStore(tmp_path),
        artifact_registry=ArtifactRegistry(tmp_path / "artifacts"),
    )

    assert pool.orchestrator.registry.list_workflows()[0]["domain"] == "meeting"
    meeting_workflow = pool.orchestrator.registry._workflows[0]
    assert meeting_workflow.workflow.__class__.__module__ == "packs.meeting.workflow"


def test_gateway_meeting_module_is_compatibility_export_only():
    import apps.gateway.meeting as gateway_meeting

    assert gateway_meeting.MeetingWorkflow.__module__ == "packs.meeting.workflow"
    assert gateway_meeting.MeetingGatewayService.__module__ == "packs.meeting.connector"


def test_lead_orchestrator_runs_knowledge_workflow():
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
        assert result["knowledge"]["execution_mode"] == "legacy_fallback"

    asyncio.run(run())


def test_lead_orchestrator_runs_video_studio_workflow(tmp_path):
    registry = WorkflowRegistry()
    registry.register(VideoStudioWorkflow())
    orchestrator = LeadOrchestrator(registry)

    async def run():
        result = await orchestrator.run_if_applicable(
            "请为主题: 城市夜跑 生成一个短视频脚本和分镜",
            WorkflowContext(
                session_id="sess",
                turn_id="turn",
                artifact_registry=ArtifactRegistry(tmp_path / "artifacts"),
            ),
        )
        assert result is not None
        assert result["domain"] == "video_studio"
        assert result["workflow_id"] == "video.workflow"
        assert "视频工作流规划已完成" in result["content"]
        assert set(result["artifact_records"]) == {
            "brief",
            "script",
            "storyboard",
            "shot_list",
            "asset_plan",
            "render_output",
        }
        assert result["video_studio"]["brief"]["title"] == "城市夜跑"

    asyncio.run(run())


def test_gateway_workflow_list_and_knowledge_route(tmp_path):
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
        assert {item["domain"] for item in listed.result["workflows"]} == {
            "meeting",
            "knowledge",
            "video_studio",
        }
        assert {item["pack_name"] for item in listed.result["workflows"]} == {
            "meeting",
            "knowledge",
            "video_studio",
        }
        assert {item["assembly_status"] for item in listed.result["workflows"]} == {"assembled"}
        assert {item["assembly_source"] for item in listed.result["workflows"]} == {"pack"}

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
        assert completed["data"]["approval_required"] is True
        assert "操作需要审批" in response.result["final_text"]
        assert completed["data"]["knowledge"]["connector_id"] == "data_service_mcp"
        assert completed["data"]["knowledge"]["tool"] == "knowledge_query_v2"

        artifacts = await service.handle_rpc(
            RpcRequest(
                id="a1",
                method="artifact.list",
                params={"session_id": started.result["session_id"], "domain": "knowledge"},
            )
        )
        assert artifacts.error is None
        assert not [item for item in artifacts.result["artifacts"] if item["kind"] == "connector_result"]

    asyncio.run(run())


def test_build_pack_assembly_inputs_unions_connectors_for_shared_domain():
    app_registry = AppRegistry(
        [
            AppProfile(
                app_id="knowledge_a",
                display_name="Knowledge A",
                domain="knowledge",
                default_pack="knowledge",
                connector_refs=("data_service_mcp",),
            ),
            AppProfile(
                app_id="knowledge_b",
                display_name="Knowledge B",
                domain="knowledge",
                default_pack="knowledge",
                connector_refs=("local.knowledge",),
            ),
        ]
    )

    inputs = build_pack_assembly_inputs(app_registry=app_registry)

    assert inputs["app_enabled_connectors_by_domain"]["knowledge"] == {
        "data_service_mcp",
        "local.knowledge",
    }

from __future__ import annotations

import asyncio
import json
import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from apps.gateway.artifacts import ArtifactRegistry
from apps.gateway.cross_domain_mcp_workflow import MeetingToKnowledgeMcpRunner
from apps.gateway.knowledge_mcp_workflow import KnowledgeMcpWorkflowRunner
from apps.gateway.protocol import RpcRequest
from apps.gateway.runtime import GatewayRuntimePool, normalize_runtime_event
from apps.gateway.service import GatewayService
from apps.gateway.storage import GatewaySessionStore
from core.config import DataServiceMcpConfig, FunASRMcpConfig, MeetingMcpConfig
from core.packs import DomainPackManifest, PackRegistry
from core.stores import CoreSQLiteStore


class FakeAgent:
    def invoke(self, user_input: str):
        return {
            "status": "success",
            "content": f"reply: {user_input}",
            "model": "fake-model",
        }


class AssistantTextDelta:
    text = "hello"


class AssistantTurnComplete:
    message = None
    usage = None


class FakeBundleEngine:
    async def submit_message(self, user_input: str):
        event = AssistantTextDelta()
        event.text = f"bundle: {user_input}"
        yield event
        yield AssistantTurnComplete()

    async def continue_pending(self):
        event = AssistantTextDelta()
        event.text = "continued"
        yield event
        yield AssistantTurnComplete()


class FakeBundle:
    engine = FakeBundleEngine()


class FakeMeetingService:
    def __init__(self, artifact_dir: Path) -> None:
        self.artifact_dir = artifact_dir

    async def process_recording(self, path, *, engine=None, language=None, title=None):
        self.artifact_dir.mkdir(parents=True, exist_ok=True)
        paths = {
            "analysis": self.artifact_dir / "analysis.json",
            "minutes": self.artifact_dir / "minutes.md",
            "result": self.artifact_dir / "result.json",
            "transcript": self.artifact_dir / "transcript.json",
        }
        paths["analysis"].write_text('{"theme":"测试会议"}', encoding="utf-8")
        paths["minutes"].write_text("# 测试会议\n\n行动项：完成 Phase 5-D。", encoding="utf-8")
        paths["result"].write_text('{"ok":true}', encoding="utf-8")
        paths["transcript"].write_text('{"text":"完成 Phase 5-D"}', encoding="utf-8")
        return {
            "source_path": path,
            "session_id": "meeting_cross_domain",
            "transcript_chars": 16,
            "segment_count": 1,
            "analysis": {"theme": "测试会议", "summary": "测试摘要"},
            "minutes_path": str(paths["minutes"]),
            "artifacts": {kind: str(path) for kind, path in paths.items()},
        }


class ArtifactWorkflowOrchestrator:
    def __init__(self, artifact_path: Path) -> None:
        self.artifact_path = artifact_path
        self.registry = self

    def list_workflows(self):
        return [{"workflow_id": "meeting.workflow", "domain": "meeting"}]

    def select(self, user_input, context):
        return self

    workflow_id = "meeting.workflow"
    domain = "meeting"

    async def run(self, user_input, context):
        return await self.run_if_applicable(user_input, context)

    async def run_if_applicable(self, user_input, context):
        artifact = context.artifact_registry.register_file(
            str(self.artifact_path),
            session_id=context.session_id,
            turn_id=context.turn_id,
            domain="meeting",
            kind="minutes",
        )
        return {
            "status": "success",
            "content": "meeting artifact ready",
            "meeting": {"artifact_records": {"minutes": artifact}},
            "domain": "meeting",
            "workflow_id": "meeting.workflow",
        }


def test_gateway_rpc_happy_path(tmp_path):
    async def run():
        pool = GatewayRuntimePool(
            model="fake-model",
            agent_factory=lambda _model: FakeAgent(),
            runtime_backend="simple",
            store=GatewaySessionStore(tmp_path),
        )
        service = GatewayService(pool)
        init = await service.handle_rpc(RpcRequest(id="1", method="initialize"))
        assert init.error is None
        assert init.result["protocol_version"] == "v1alpha"

        started = await service.handle_rpc(RpcRequest(id="2", method="session.start"))
        assert started.error is None
        session_id = started.result["session_id"]

        turn = await service.handle_rpc(
            RpcRequest(
                id="3",
                method="turn.start",
                params={"session_id": session_id, "input": "你好"},
            )
        )
        assert turn.error is None
        assert turn.result["final_text"] == "reply: 你好"
        assert [event["type"] for event in turn.result["events"]] == [
            "turn.started",
            "item.delta",
            "turn.completed",
        ]
        events = await service.handle_rpc(
            RpcRequest(
                id="4",
                method="session.events",
                params={"session_id": session_id},
            )
        )
        assert events.error is None
        assert len(events.result["events"]) == 3

    asyncio.run(run())


def test_gateway_rpc_method_registry_and_capabilities(tmp_path):
    async def run():
        pool = GatewayRuntimePool(
            model="fake-model",
            agent_factory=lambda _model: FakeAgent(),
            runtime_backend="simple",
            store=GatewaySessionStore(tmp_path),
        )
        service = GatewayService(pool)

        init = await service.handle_rpc(RpcRequest(id="1", method="initialize"))
        assert init.error is None
        init_methods = {method["method"]: method for method in init.result["methods"]}
        assert "turn.start" in init_methods
        assert "artifact.lineage" in init_methods
        assert "agent.list" in init_methods
        assert "workflow.execute_stub" in init_methods
        assert "connector.submit" in init_methods
        assert "memory.summary" in init_methods
        assert init_methods["artifact.lineage"]["alias_of"] == "core.artifact.lineage"
        assert init.result["capabilities"]["turns"] is True
        assert init.result["capabilities"]["artifact_lineage"] is True
        assert init.result["capabilities"]["agents"] is True
        assert init.result["capabilities"]["pack_execution"] is True
        assert init.result["capabilities"]["connector_execution"] is True
        assert init.result["capabilities"]["memory"] is True
        assert init.result["capabilities"]["stdio_jsonl"] is True

        listed = await service.handle_rpc(RpcRequest(id="2", method="method.list"))
        assert listed.error is None
        listed_methods = {method["method"]: method for method in listed.result["methods"]}
        assert listed.result["count"] == len(listed_methods)
        assert listed_methods == init_methods
        assert listed.result["capabilities"]["turns"] is True
        assert listed.result["capabilities"]["artifact_lineage"] is True
        assert listed.result["capabilities"]["agents"] is True
        assert listed.result["capabilities"]["pack_execution"] is True
        assert listed.result["capabilities"]["connector_execution"] is True
        assert listed.result["capabilities"]["memory"] is True

    asyncio.run(run())


def test_gateway_memory_rpc_and_turn_context_injection(tmp_path):
    async def run():
        core_store = CoreSQLiteStore(tmp_path / "core.sqlite3")
        pool = GatewayRuntimePool(
            model="fake-model",
            agent_factory=lambda _model: FakeAgent(),
            runtime_backend="simple",
            store=GatewaySessionStore(tmp_path / "sessions"),
            core_store=core_store,
        )
        service = GatewayService(pool)
        started = await service.handle_rpc(RpcRequest(id="1", method="session.start"))
        session_id = started.result["session_id"]

        first = await service.handle_rpc(
            RpcRequest(id="2", method="turn.start", params={"session_id": session_id, "input": "first memory turn"})
        )
        assert first.error is None

        memories = await service.handle_rpc(
            RpcRequest(id="3", method="memory.list", params={"session_id": session_id, "kind": "session_summary"})
        )
        assert memories.error is None
        assert memories.result["count"] >= 1
        memory_id = memories.result["memories"][-1]["memory_id"]

        fetched = await service.handle_rpc(RpcRequest(id="4", method="memory.get", params={"memory_id": memory_id}))
        assert fetched.error is None
        assert fetched.result["memory"]["kind"] == "session_summary"

        second = await service.handle_rpc(
            RpcRequest(id="5", method="turn.start", params={"session_id": session_id, "input": "use prior context"})
        )
        assert second.error is None
        assert "Relevant session memory:" in second.result["final_text"]
        assert "first memory turn" in second.result["final_text"]
        assert service.core_store.list_trace_records(session_id=session_id, event_type="memory.context")

    asyncio.run(run())


def test_gateway_pack_list_and_get(tmp_path):
    async def run():
        pool = GatewayRuntimePool(
            model="fake-model",
            agent_factory=lambda _model: FakeAgent(),
            runtime_backend="simple",
            store=GatewaySessionStore(tmp_path),
        )
        service = GatewayService(pool)

        listed = await service.handle_rpc(RpcRequest(id="packs", method="pack.list"))
        assert listed.error is None
        packs = {pack["name"]: pack for pack in listed.result["packs"]}
        assert set(packs) == {
            "meeting",
            "knowledge",
            "investment",
            "interview",
            "video_studio",
        }
        assert packs["meeting"]["assembly"]["status"] == "assembled"
        assert packs["meeting"]["assembly"]["app_id"] == "meeting"
        assert packs["meeting"]["assembly"]["conflicts"] == []
        assert packs["knowledge"]["assembly"]["status"] == "assembled"
        assert packs["video_studio"]["assembly"]["status"] == "assembled"
        assert packs["investment"]["assembly"]["status"] == "stub"

        active = await service.handle_rpc(
            RpcRequest(id="active", method="pack.list", params={"status": "active"})
        )
        assert active.error is None
        assert {pack["name"] for pack in active.result["packs"]} == {"meeting", "knowledge", "video_studio"}
        assert {pack["assembly"]["status"] for pack in active.result["packs"]} == {"assembled"}

        meeting = await service.handle_rpc(
            RpcRequest(id="meeting", method="pack.get", params={"domain": "meeting"})
        )
        assert meeting.error is None
        assert meeting.result["pack"]["status"] == "active"
        assert meeting.result["pack"]["manifest_schema_version"] == "1"
        assert "meeting.workflow" in meeting.result["pack"]["workflows"]
        assert "meeting.workflow" in meeting.result["pack"]["workflow_dsl"]
        assert meeting.result["pack"]["skill_refs"] == ["meeting.transcribe", "meeting.minutes"]
        assert meeting.result["pack"]["policy_bundles"] == ["meeting.standard"]
        assert meeting.result["pack"]["connector_refs"] == ["meeting_voice_mcp"]
        assert meeting.result["pack"]["artifact_schemas"]["minutes"]["parents"] == ["result"]
        assert meeting.result["pack"]["assembly"]["status"] == "assembled"
        assert meeting.result["pack"]["assembly"]["app_id"] == "meeting"
        assert meeting.result["pack"]["assembly"]["conflicts"] == []
        assert meeting.result["pack"]["assembly"]["registered_workflows"] == ["meeting.workflow"]
        assert meeting.result["pack"]["assembly"]["workflow_dsl"]["meeting.workflow"]["steps"][0]["id"] == "transcribe"

        knowledge = await service.handle_rpc(
            RpcRequest(id="knowledge", method="pack.get", params={"domain": "knowledge"})
        )
        assert knowledge.error is None
        assert knowledge.result["pack"]["assembly"]["status"] == "assembled"
        assert knowledge.result["pack"]["connector_refs"] == ["local.knowledge", "data_service_mcp"]
        assert knowledge.result["pack"]["workflow_templates"]["knowledge.lifecycle"]["kind"] == "typed_dag"
        assert knowledge.result["pack"]["workflow_templates"]["knowledge.lifecycle"]["nodes"][0]["type"] == "connector"
        assert knowledge.result["pack"]["agents"][0]["agent_id"] == "knowledge.curator"
        assert "knowledge_workspace_archive" in knowledge.result["pack"]["connector_capabilities"]["data_service_mcp"]["tools"]
        assert "knowledge_query" in knowledge.result["pack"]["connector_capabilities"]["data_service_mcp"]["tools"]

        video = await service.handle_rpc(
            RpcRequest(id="video", method="pack.get", params={"domain": "video_studio"})
        )
        assert video.error is None
        assert video.result["pack"]["status"] == "active"
        assert video.result["pack"]["assembly"]["status"] == "assembled"
        assert video.result["pack"]["assembly"]["app_id"] == "video_studio"
        assert video.result["pack"]["assembly"]["registered_workflows"] == ["video.workflow"]
        assert video.result["pack"]["workflow_templates"]["video.pipeline"]["kind"] == "multi_agent_typed_dag"

    asyncio.run(run())


def test_gateway_agent_contract_methods(tmp_path):
    async def run():
        pool = GatewayRuntimePool(
            model="fake-model",
            agent_factory=lambda _model: FakeAgent(),
            runtime_backend="simple",
            store=GatewaySessionStore(tmp_path),
        )
        service = GatewayService(pool)

        pack_agents = await service.handle_rpc(
            RpcRequest(id="pa", method="pack.agents", params={"domain": "knowledge"})
        )
        assert pack_agents.error is None
        assert [agent["agent_id"] for agent in pack_agents.result["agents"]] == [
            "knowledge.curator",
            "knowledge.quality_reviewer",
        ]

        listed = await service.handle_rpc(
            RpcRequest(id="al", method="agent.list", params={"domain": "video_studio"})
        )
        assert listed.error is None
        assert {agent["agent_id"] for agent in listed.result["agents"]} >= {"studio.lead", "qa.publisher"}

        fetched = await service.handle_rpc(
            RpcRequest(id="ag", method="agent.get", params={"agent_id": "knowledge.curator"})
        )
        assert fetched.error is None
        assert fetched.result["agent"]["domain"] == "knowledge"
        assert fetched.result["agent"]["pack_name"] == "knowledge"
        assert "data_service_mcp.knowledge_query_v2" in fetched.result["agent"]["tool_refs"]

    asyncio.run(run())


def test_gateway_pack_plan_and_stub_execution_registers_lineage(tmp_path):
    async def run():
        core_store = CoreSQLiteStore(tmp_path / "core.sqlite3")
        pool = GatewayRuntimePool(
            model="fake-model",
            agent_factory=lambda _model: FakeAgent(),
            runtime_backend="simple",
            store=GatewaySessionStore(tmp_path / "sessions"),
            artifact_registry=ArtifactRegistry(tmp_path / "artifacts"),
            core_store=core_store,
        )
        service = GatewayService(pool)
        started = await service.handle_rpc(RpcRequest(id="1", method="session.start"))
        session_id = started.result["session_id"]

        plan = await service.handle_rpc(
            RpcRequest(
                id="plan",
                method="pack.plan",
                params={"domain": "knowledge", "template_id": "knowledge.lifecycle"},
            )
        )
        assert plan.error is None
        assert plan.result["plan"]["status"] == "planned"
        assert plan.result["plan"]["execution_order"][0] == "workspace_create"

        executed = await service.handle_rpc(
            RpcRequest(
                id="exec",
                method="workflow.execute_stub",
                params={
                    "workflow_id": "knowledge.workflow",
                    "template_id": "knowledge.lifecycle",
                    "session_id": session_id,
                    "inputs": {"query_intent": "demo"},
                },
            )
        )
        assert executed.error is None
        assert executed.result["status"] == "stubbed"
        assert [artifact["kind"] for artifact in executed.result["artifact_records"]] == [
            "source",
            "summary",
            "quality_report",
            "correction_plan",
        ]
        lineage = executed.result["artifact_lineage"]
        assert lineage["count"] == 4
        assert len(lineage["edges"]) == 3
        assert {artifact.kind for artifact in core_store.list_artifacts(domain="knowledge")} == {
            "source",
            "summary",
            "quality_report",
            "correction_plan",
        }

    asyncio.run(run())


def test_gateway_connector_registry_lists_meeting_mcp(tmp_path):
    module_path = tmp_path / "app" / "meeting_mcp" / "mcp_stdio.py"
    module_path.parent.mkdir(parents=True, exist_ok=True)
    module_path.write_text("# fake meeting mcp module\n", encoding="utf-8")

    async def run():
        pool = GatewayRuntimePool(
            model="fake-model",
            agent_factory=lambda _model: FakeAgent(),
            runtime_backend="simple",
            store=GatewaySessionStore(tmp_path / "sessions"),
            core_store=CoreSQLiteStore(tmp_path / "core.sqlite3"),
        )
        service = GatewayService(pool)
        service.connector_registry.meeting_config = MeetingMcpConfig(
            cwd=str(tmp_path),
            command="python3",
            args="-m app.meeting_mcp.mcp_stdio",
        )
        service.connector_registry.funasr_config = FunASRMcpConfig(
            cwd="/Users/Zhuanz/Desktop/workspace/meeting-voice-assistant/backend",
            command="python3",
            args="-m funasr_service.mcp_stdio",
        )

        listed = await service.handle_rpc(RpcRequest(id="c1", method="connector.list"))
        assert listed.error is None
        connectors = {connector["connector_id"]: connector for connector in listed.result["connectors"]}
        assert "meeting_voice_mcp" in connectors
        assert "funasr_mcp" in connectors
        assert "data_service_mcp" in connectors
        assert "remote_comfyui" in connectors
        assert connectors["meeting_voice_mcp"]["domain"] == "meeting"
        assert connectors["meeting_voice_mcp"]["kind"] == "mcp_stdio"
        assert connectors["funasr_mcp"]["domain"] == "meeting"
        assert connectors["funasr_mcp"]["kind"] == "mcp_stdio"
        assert "funasr_recognize_file" in connectors["funasr_mcp"]["capabilities"]["tools"]
        assert connectors["data_service_mcp"]["domain"] == "knowledge"
        assert connectors["data_service_mcp"]["health"] == "contract_stub"
        assert connectors["data_service_mcp"]["capabilities"]["contract_only"] is True
        assert "knowledge_workspace_archive" in connectors["data_service_mcp"]["capabilities"]["tools"]
        assert connectors["remote_comfyui"]["domain"] == "video_studio"
        assert connectors["remote_comfyui"]["kind"] == "http_service"
        assert connectors["remote_comfyui"]["health"] == "not_configured"

        fetched = await service.handle_rpc(
            RpcRequest(id="c2", method="connector.get", params={"connector_id": "meeting_voice_mcp"})
        )
        assert fetched.error is None
        assert fetched.result["connector"]["config_ref"] == "HARNESS_MEETING_MCP_*"

        comfyui = await service.handle_rpc(
            RpcRequest(id="c4", method="connector.get", params={"connector_id": "remote_comfyui"})
        )
        assert comfyui.error is None
        assert comfyui.result["connector"]["config_ref"] == "HARNESS_COMFYUI_*"

        funasr = await service.handle_rpc(
            RpcRequest(id="c5", method="connector.get", params={"connector_id": "funasr_mcp"})
        )
        assert funasr.error is None
        assert funasr.result["connector"]["config_ref"] == "HARNESS_FUNASR_MCP_*"

        health = await service.handle_rpc(
            RpcRequest(id="c3", method="connector.health", params={"connector_id": "meeting_voice_mcp"})
        )
        assert health.error is None
        assert health.result["health"]["status"] == "available"
        assert health.result["connector"]["trust_level"] == "trusted_local"
        assert health.result["connector"]["execution_mode"] == "stdio"
        assert health.result["connector"]["allowed_commands"]
        assert health.result["connector"]["allowed_paths"]
        assert health.result["connector"]["network_policy"] == "none"

    asyncio.run(run())


def test_gateway_connector_execution_submit_poll_collect_and_cancel(tmp_path):
    async def run():
        core_store = CoreSQLiteStore(tmp_path / "core.sqlite3")
        pool = GatewayRuntimePool(
            model="fake-model",
            agent_factory=lambda _model: FakeAgent(),
            runtime_backend="simple",
            store=GatewaySessionStore(tmp_path / "sessions"),
            artifact_registry=ArtifactRegistry(tmp_path / "artifacts"),
            core_store=core_store,
        )
        service = GatewayService(pool)
        started = await service.handle_rpc(RpcRequest(id="1", method="session.start"))
        session_id = started.result["session_id"]

        submitted = await service.handle_rpc(
            RpcRequest(
                id="submit",
                method="connector.submit",
                params={
                    "connector_id": "data_service_mcp",
                    "tool": "knowledge_query",
                    "session_id": session_id,
                    "input": {"query": "demo"},
                },
            )
        )
        assert submitted.error is None
        job_id = submitted.result["job"]["job_id"]
        assert submitted.result["job"]["status"] == "completed"
        assert submitted.result["artifact"]["kind"] == "connector_result"
        assert [event["event_type"] for event in submitted.result["events"]] == [
            "job.queued",
            "job.running",
            "job.completed",
        ]

        polled = await service.handle_rpc(
            RpcRequest(id="poll", method="connector.poll", params={"job_id": job_id})
        )
        assert polled.error is None
        assert polled.result["terminal"] is True
        assert polled.result["job"]["artifact_ids"] == [submitted.result["artifact"]["artifact_id"]]

        collected = await service.handle_rpc(
            RpcRequest(id="collect", method="connector.collect", params={"job_id": job_id})
        )
        assert collected.error is None
        assert collected.result["artifacts"][0]["kind"] == "connector_result"
        assert collected.result["artifact_lineage"]["count"] == 1
        assert core_store.get_job(job_id).artifact_ids == [submitted.result["artifact"]["artifact_id"]]

        funasr_submitted = await service.handle_rpc(
            RpcRequest(
                id="funasr-submit",
                method="connector.submit",
                params={
                    "connector_id": "funasr_mcp",
                    "tool": "funasr_recognize_file",
                    "session_id": session_id,
                    "input": {"path": "/tmp/demo.wav"},
                },
            )
        )
        assert funasr_submitted.error is None
        assert funasr_submitted.result["job"]["status"] == "completed"
        assert funasr_submitted.result["artifact"]["metadata"]["connector_id"] == "funasr_mcp"

        deferred = await service.handle_rpc(
            RpcRequest(
                id="defer",
                method="connector.submit",
                params={
                    "connector_id": "data_service_mcp",
                    "tool": "knowledge_build_status",
                    "session_id": session_id,
                    "defer": True,
                },
            )
        )
        assert deferred.error is None
        assert deferred.result["job"]["status"] == "running"
        cancelled = await service.handle_rpc(
            RpcRequest(
                id="cancel",
                method="connector.cancel",
                params={"job_id": deferred.result["job"]["job_id"], "reason": "test cancel"},
            )
        )
        assert cancelled.error is None
        assert cancelled.result["job"]["status"] == "cancelled"
        assert cancelled.result["terminal"] is True

    asyncio.run(run())


def test_gateway_connector_execution_can_call_data_service_mcp_stdio(tmp_path):
    mcp_package = tmp_path / "data_service"
    mcp_package.mkdir()
    (mcp_package / "__init__.py").write_text("", encoding="utf-8")
    (mcp_package / "mcp_stdio.py").write_text(
        """
import json
import sys

for line in sys.stdin:
    request = json.loads(line)
    method = request.get("method")
    request_id = request.get("id")
    if method == "initialize":
        result = {"protocolVersion": "2024-11-05", "capabilities": {"tools": {}}}
    elif method == "tools/call":
        params = request.get("params") or {}
        result = {
            "content": [{
                "type": "text",
                "text": json.dumps({
                    "workspace_id": "project-knowledge",
                    "operation_id": None,
                    "status": "ok",
                    "warnings": [],
                    "artifact_refs": [],
                    "next_actions": [],
                    "data": {
                        "tool": params.get("name"),
                        "arguments": params.get("arguments"),
                    },
                }),
            }],
            "isError": False,
        }
    else:
        result = {}
    print(json.dumps({"jsonrpc": "2.0", "id": request_id, "result": result}), flush=True)
""".strip()
        + "\n",
        encoding="utf-8",
    )

    async def run():
        core_store = CoreSQLiteStore(tmp_path / "core.sqlite3")
        pool = GatewayRuntimePool(
            model="fake-model",
            agent_factory=lambda _model: FakeAgent(),
            runtime_backend="simple",
            store=GatewaySessionStore(tmp_path / "sessions"),
            artifact_registry=ArtifactRegistry(tmp_path / "artifacts"),
            core_store=core_store,
        )
        service = GatewayService(pool)
        service.connector_registry.data_service_config = DataServiceMcpConfig(
            cwd=str(tmp_path),
            command=sys.executable,
            args="-m data_service.mcp_stdio",
            execution="stdio",
            request_timeout=5,
            workspace_root=str(tmp_path / "managed"),
            allowed_workspace_roots=str(tmp_path),
            allowed_source_roots=str(tmp_path),
        )
        started = await service.handle_rpc(RpcRequest(id="1", method="session.start"))
        submitted = await service.handle_rpc(
            RpcRequest(
                id="submit",
                method="connector.submit",
                params={
                    "connector_id": "data_service_mcp",
                    "tool": "knowledge_query_v2",
                    "session_id": started.result["session_id"],
                    "input": {
                        "workspace_id": "project-knowledge",
                        "query": "Content",
                        "mode": "hybrid",
                        "top_k": 8,
                    },
                },
            )
        )

        assert submitted.error is None
        assert submitted.result["job"]["status"] == "completed"
        artifact_payload = json.loads(Path(submitted.result["artifact"]["path"]).read_text(encoding="utf-8"))
        assert artifact_payload["execution_deferred"] is False
        assert artifact_payload["result"]["content"][0]["status"] == "ok"
        assert artifact_payload["result"]["content"][0]["data"]["tool"] == "knowledge_query_v2"
        assert artifact_payload["result"]["content"][0]["data"]["arguments"]["workspace_id"] == "project-knowledge"

    asyncio.run(run())


def test_gateway_connector_deferred_job_completes_in_background(tmp_path):
    mcp_package = tmp_path / "data_service"
    mcp_package.mkdir()
    (mcp_package / "__init__.py").write_text("", encoding="utf-8")
    (mcp_package / "mcp_stdio.py").write_text(
        """
import json
import sys
import time

for line in sys.stdin:
    request = json.loads(line)
    method = request.get("method")
    request_id = request.get("id")
    if method == "initialize":
        result = {"protocolVersion": "2024-11-05", "capabilities": {"tools": {}}}
    elif method == "tools/call":
        time.sleep(0.1)
        result = {
            "content": [{
                "type": "text",
                "text": json.dumps({"status": "ok", "job": "done"}),
            }],
            "isError": False,
        }
    else:
        result = {}
    print(json.dumps({"jsonrpc": "2.0", "id": request_id, "result": result}), flush=True)
""".strip()
        + "\n",
        encoding="utf-8",
    )

    async def run():
        core_store = CoreSQLiteStore(tmp_path / "core.sqlite3")
        pool = GatewayRuntimePool(
            model="fake-model",
            agent_factory=lambda _model: FakeAgent(),
            runtime_backend="simple",
            store=GatewaySessionStore(tmp_path / "sessions"),
            artifact_registry=ArtifactRegistry(tmp_path / "artifacts"),
            core_store=core_store,
        )
        service = GatewayService(pool)
        service.connector_registry.data_service_config = DataServiceMcpConfig(
            cwd=str(tmp_path),
            command=sys.executable,
            args="-m data_service.mcp_stdio",
            execution="stdio",
            request_timeout=5,
            workspace_root=str(tmp_path / "managed"),
            allowed_workspace_roots=str(tmp_path),
            allowed_source_roots=str(tmp_path),
        )
        started = await service.handle_rpc(RpcRequest(id="1", method="session.start"))
        deferred = await service.handle_rpc(
            RpcRequest(
                id="2",
                method="connector.submit",
                params={
                    "connector_id": "data_service_mcp",
                    "tool": "knowledge_query_v2",
                    "session_id": started.result["session_id"],
                    "defer": True,
                },
            )
        )
        assert deferred.error is None
        job_id = deferred.result["job"]["job_id"]
        assert deferred.result["job"]["status"] == "running"

        deadline = time.time() + 3
        final = None
        while time.time() < deadline:
            polled = await service.handle_rpc(RpcRequest(id="3", method="connector.poll", params={"job_id": job_id}))
            assert polled.error is None
            if polled.result["job"]["status"] == "completed":
                final = polled.result
                break
            await asyncio.sleep(0.05)
        assert final is not None
        assert final["terminal"] is True
        assert final["job"]["artifact_ids"]

    asyncio.run(run())


def test_gateway_connector_mcp_iserror_marks_job_failed(tmp_path):
    mcp_package = tmp_path / "data_service"
    mcp_package.mkdir()
    (mcp_package / "__init__.py").write_text("", encoding="utf-8")
    (mcp_package / "mcp_stdio.py").write_text(
        """
import json
import sys

for line in sys.stdin:
    request = json.loads(line)
    method = request.get("method")
    request_id = request.get("id")
    if method == "initialize":
        result = {"protocolVersion": "2024-11-05", "capabilities": {"tools": {}}}
    elif method == "tools/call":
        result = {
            "content": [{"type": "text", "text": "backend exploded"}],
            "isError": True,
        }
    else:
        result = {}
    print(json.dumps({"jsonrpc": "2.0", "id": request_id, "result": result}), flush=True)
""".strip()
        + "\n",
        encoding="utf-8",
    )

    async def run():
        core_store = CoreSQLiteStore(tmp_path / "core.sqlite3")
        pool = GatewayRuntimePool(
            model="fake-model",
            agent_factory=lambda _model: FakeAgent(),
            runtime_backend="simple",
            store=GatewaySessionStore(tmp_path / "sessions"),
            artifact_registry=ArtifactRegistry(tmp_path / "artifacts"),
            core_store=core_store,
        )
        service = GatewayService(pool)
        service.connector_registry.data_service_config = DataServiceMcpConfig(
            cwd=str(tmp_path),
            command=sys.executable,
            args="-m data_service.mcp_stdio",
            execution="stdio",
            request_timeout=5,
            workspace_root=str(tmp_path / "managed"),
            allowed_workspace_roots=str(tmp_path),
            allowed_source_roots=str(tmp_path),
        )
        started = await service.handle_rpc(RpcRequest(id="1", method="session.start"))
        submitted = await service.handle_rpc(
            RpcRequest(
                id="2",
                method="connector.submit",
                params={
                    "connector_id": "data_service_mcp",
                    "tool": "knowledge_query_v2",
                    "session_id": started.result["session_id"],
                },
            )
        )
        assert submitted.error is None
        assert submitted.result["job"]["status"] == "failed"
        failure = submitted.result["job"]["metadata"]["failure_context"]
        assert "backend exploded" in failure["message"]
        assert submitted.result["job"]["artifact_ids"] == []

    asyncio.run(run())


def test_gateway_connector_submit_blocks_unallowlisted_payload_path(tmp_path):
    mcp_package = tmp_path / "data_service"
    mcp_package.mkdir()
    (mcp_package / "__init__.py").write_text("", encoding="utf-8")
    (mcp_package / "mcp_stdio.py").write_text(
        """
import json
import sys

for line in sys.stdin:
    request = json.loads(line)
    request_id = request.get("id")
    if request.get("method") == "initialize":
        result = {"protocolVersion": "2024-11-05", "capabilities": {"tools": {}}}
    else:
        result = {}
    print(json.dumps({"jsonrpc": "2.0", "id": request_id, "result": result}), flush=True)
""".strip()
        + "\n",
        encoding="utf-8",
    )

    async def run():
        core_store = CoreSQLiteStore(tmp_path / "core.sqlite3")
        pool = GatewayRuntimePool(
            model="fake-model",
            agent_factory=lambda _model: FakeAgent(),
            runtime_backend="simple",
            store=GatewaySessionStore(tmp_path / "sessions"),
            artifact_registry=ArtifactRegistry(tmp_path / "artifacts"),
            core_store=core_store,
        )
        service = GatewayService(pool)
        service.connector_registry.data_service_config = DataServiceMcpConfig(
            cwd=str(tmp_path),
            command=sys.executable,
            args="-m data_service.mcp_stdio",
            execution="stdio",
            request_timeout=5,
            workspace_root=str(tmp_path / "managed"),
            allowed_workspace_roots=str(tmp_path / "managed"),
            allowed_source_roots=str(tmp_path / "sources"),
        )
        started = await service.handle_rpc(RpcRequest(id="1", method="session.start"))
        submitted = await service.handle_rpc(
            RpcRequest(
                id="2",
                method="connector.submit",
                params={
                    "connector_id": "data_service_mcp",
                    "tool": "knowledge_query_v2",
                    "session_id": started.result["session_id"],
                    "input": {"workspace_id": "/etc/passwd"},
                },
            )
        )
        assert submitted.error is None
        assert submitted.result["job"]["status"] == "failed"
        assert "connector_security_blocked" in submitted.result["job"]["metadata"]["failure_context"]["message"]

    asyncio.run(run())


def test_knowledge_mcp_workflow_runner_completes_external_e2e_with_stdio(tmp_path):
    mcp_package = tmp_path / "data_service"
    mcp_package.mkdir()
    (mcp_package / "__init__.py").write_text("", encoding="utf-8")
    (mcp_package / "mcp_stdio.py").write_text(
        """
import json
import sys

workspace_id = "project-knowledge"
operation_id = "op-1"

def envelope(tool, arguments):
    status = "ok"
    data = {"tool": tool, "arguments": arguments}
    op_id = None
    if tool == "knowledge_build_start":
        status = "queued"
        op_id = operation_id
    elif tool == "knowledge_build_status":
        status = "completed"
        op_id = operation_id
        data["stage"] = "completed"
    elif tool == "knowledge_correction_rules_v2":
        data["rules"] = [{"rule_id": "rule-1", "status": "draft"}]
    return {
        "workspace_id": workspace_id,
        "operation_id": op_id,
        "status": status,
        "warnings": [],
        "artifact_refs": [],
        "next_actions": [],
        "data": data,
    }

for line in sys.stdin:
    request = json.loads(line)
    method = request.get("method")
    request_id = request.get("id")
    if method == "initialize":
        result = {"protocolVersion": "2024-11-05", "capabilities": {"tools": {}}}
    elif method == "tools/call":
        params = request.get("params") or {}
        result = {
            "content": [{
                "type": "text",
                "text": json.dumps(envelope(params.get("name"), params.get("arguments") or {})),
            }],
            "isError": False,
        }
    else:
        result = {}
    print(json.dumps({"jsonrpc": "2.0", "id": request_id, "result": result}), flush=True)
""".strip()
        + "\n",
        encoding="utf-8",
    )

    core_store = CoreSQLiteStore(tmp_path / "core.sqlite3")
    pool = GatewayRuntimePool(
        model="fake-model",
        agent_factory=lambda _model: FakeAgent(),
        runtime_backend="simple",
        store=GatewaySessionStore(tmp_path / "sessions"),
        artifact_registry=ArtifactRegistry(tmp_path / "artifacts"),
        core_store=core_store,
    )
    service = GatewayService(pool)
    service.connector_registry.data_service_config = DataServiceMcpConfig(
        cwd=str(tmp_path),
        command=sys.executable,
        args="-m data_service.mcp_stdio",
        execution="stdio",
        request_timeout=5,
        workspace_root=str(tmp_path / "managed"),
        allowed_workspace_roots=str(tmp_path),
        allowed_source_roots=str(tmp_path),
    )
    result = KnowledgeMcpWorkflowRunner(service.connector_execution_runtime).run_acceptance(
        name="Project Knowledge",
        query="Content",
        texts=[{"title": "Note", "content": "# Note\n\nContent"}],
        poll_interval=0,
        max_polls=3,
    )

    assert result.status == "ok"
    assert result.workspace_id == "project-knowledge"
    assert [step["tool"] for step in result.steps] == [
        "knowledge_workspace_create",
        "knowledge_source_import",
        "knowledge_build_start",
        "knowledge_build_status",
        "knowledge_query_v2",
        "knowledge_quality_feedback_v2",
        "knowledge_correction_rules_v2",
        "knowledge_review_correction_rule_v2",
        "knowledge_correction_plan_v2",
        "knowledge_workspace_archive",
    ]
    assert result.steps[-1]["envelope"]["data"]["tool"] == "knowledge_workspace_archive"


def test_meeting_to_knowledge_cross_domain_runner_links_lineage(tmp_path):
    mcp_package = tmp_path / "data_service"
    mcp_package.mkdir()
    (mcp_package / "__init__.py").write_text("", encoding="utf-8")
    (mcp_package / "mcp_stdio.py").write_text(
        """
import json
import sys

workspace_id = "meeting-knowledge"
operation_id = "op-cross"

def envelope(tool, arguments):
    status = "ok"
    data = {"tool": tool, "arguments": arguments}
    op_id = None
    if tool == "knowledge_build_start":
        status = "queued"
        op_id = operation_id
    elif tool == "knowledge_build_status":
        status = "completed"
        op_id = operation_id
    elif tool == "knowledge_correction_rules_v2":
        data["rules"] = [{"rule_id": "rule-cross"}]
    return {
        "workspace_id": workspace_id,
        "operation_id": op_id,
        "status": status,
        "warnings": [],
        "artifact_refs": [],
        "next_actions": [],
        "data": data,
    }

for line in sys.stdin:
    request = json.loads(line)
    method = request.get("method")
    request_id = request.get("id")
    if method == "initialize":
        result = {"protocolVersion": "2024-11-05", "capabilities": {"tools": {}}}
    elif method == "tools/call":
        params = request.get("params") or {}
        result = {
            "content": [{
                "type": "text",
                "text": json.dumps(envelope(params.get("name"), params.get("arguments") or {})),
            }],
            "isError": False,
        }
    else:
        result = {}
    print(json.dumps({"jsonrpc": "2.0", "id": request_id, "result": result}), flush=True)
""".strip()
        + "\n",
        encoding="utf-8",
    )
    audio = tmp_path / "cross.mp3"
    audio.write_bytes(b"demo")

    async def run():
        core_store = CoreSQLiteStore(tmp_path / "core.sqlite3")
        pool = GatewayRuntimePool(
            model="fake-model",
            agent_factory=lambda _model: FakeAgent(),
            runtime_backend="simple",
            store=GatewaySessionStore(tmp_path / "sessions"),
            artifact_registry=ArtifactRegistry(tmp_path / "artifacts"),
            core_store=core_store,
        )
        pool._meeting_workflow.service = FakeMeetingService(tmp_path / "meeting-output")
        service = GatewayService(pool)
        service.connector_registry.data_service_config = DataServiceMcpConfig(
            cwd=str(tmp_path),
            command=sys.executable,
            args="-m data_service.mcp_stdio",
            execution="stdio",
            request_timeout=5,
            workspace_root=str(tmp_path / "managed"),
            allowed_workspace_roots=str(tmp_path),
            allowed_source_roots=str(tmp_path),
        )
        result = await MeetingToKnowledgeMcpRunner(service).run(
            audio_path=str(audio),
            query="行动项是什么？",
            poll_interval=0,
            max_polls=3,
        )

        payload = result.to_dict()
        assert payload["status"] == "ok"
        assert payload["knowledge"]["workspace_id"] == "meeting-knowledge"
        assert payload["artifact_lineage"]["count"] >= 14
        edges = payload["artifact_lineage"]["edges"]
        assert any(edge["source_artifact_id"].startswith("art_") for edge in edges)
        source_import_step = next(
            step for step in payload["knowledge"]["steps"] if step["tool"] == "knowledge_source_import"
        )
        source_artifact = core_store.get_artifact(source_import_step["artifact_id"])
        assert len(source_artifact.parent_ids) == 2

    asyncio.run(run())


def test_turn_start_records_trace(tmp_path):
    async def run():
        pool = GatewayRuntimePool(
            model="fake-model",
            agent_factory=lambda _model: FakeAgent(),
            runtime_backend="simple",
            store=GatewaySessionStore(tmp_path),
        )
        service = GatewayService(pool)
        started = await service.handle_rpc(RpcRequest(id="1", method="session.start"))
        session_id = started.result["session_id"]

        turn = await service.handle_rpc(
            RpcRequest(id="2", method="turn.start", params={"session_id": session_id, "input": "trace"})
        )

        assert turn.error is None
        assert turn.result["trace_id"].startswith("trace_")
        assert all(
            event["data"].get("trace_id") == turn.result["trace_id"]
            for event in turn.result["events"]
            if event["type"] in {"turn.started", "item.delta", "turn.completed"}
        )

    asyncio.run(run())


def test_turn_start_explicit_blocked_pack_returns_explainable_failure(tmp_path):
    registry = PackRegistry(
        [
            DomainPackManifest(
                name="knowledge",
                version="0.1.0",
                domain="knowledge",
                status="active",
                workflows=("knowledge.workflow",),
                connectors=("missing.connector",),
            )
        ]
    )

    async def run():
        pool = GatewayRuntimePool(
            model="fake-model",
            agent_factory=lambda _model: FakeAgent(),
            runtime_backend="simple",
            store=GatewaySessionStore(tmp_path),
            pack_registry=registry,
        )
        service = GatewayService(pool)
        pack = await service.handle_rpc(RpcRequest(id="pack", method="pack.get", params={"domain": "knowledge"}))
        assert pack.error is None
        assert pack.result["pack"]["assembly"]["status"] == "blocked"
        assert pack.result["pack"]["assembly"]["missing_dependencies"] == ["connector:missing.connector"]

        started = await service.handle_rpc(RpcRequest(id="1", method="session.start"))
        turn = await service.handle_rpc(
            RpcRequest(
                id="2",
                method="turn.start",
                params={
                    "session_id": started.result["session_id"],
                    "domain": "knowledge",
                    "input": "run demo workflow",
                },
            )
        )

        assert turn.error is None
        assert turn.result["events"][-1]["type"] == "turn.failed"
        assert "Pack assembly blocked for domain knowledge" in turn.result["events"][-1]["data"]["message"]
        assert "connector:missing.connector" in turn.result["events"][-1]["data"]["message"]

    asyncio.run(run())


def test_turn_start_mirrors_core_records(tmp_path):
    async def run():
        core_store = CoreSQLiteStore(tmp_path / "core.sqlite3")
        pool = GatewayRuntimePool(
            model="fake-model",
            agent_factory=lambda _model: FakeAgent(),
            runtime_backend="simple",
            store=GatewaySessionStore(tmp_path / "sessions"),
            core_store=core_store,
        )
        service = GatewayService(pool)
        started = await service.handle_rpc(RpcRequest(id="1", method="session.start"))
        session_id = started.result["session_id"]

        turn = await service.handle_rpc(
            RpcRequest(id="2", method="turn.start", params={"session_id": session_id, "input": "core mirror"})
        )

        assert turn.error is None
        sessions = core_store.list_sessions()
        threads = core_store.list_threads(session_id=session_id)
        turns = core_store.list_turns(session_id=session_id)
        items = core_store.list_items(turn_id=turn.result["turn_id"])

        assert [session.session_id for session in sessions] == [session_id]
        assert len(threads) == 1
        assert len(turns) == 1
        assert turns[0].turn_id == turn.result["turn_id"]
        assert turns[0].input == "core mirror"
        assert turns[0].state == "completed"
        assert [item.item_type for item in items] == [
            "user_message",
            "assistant_message_delta",
            "assistant_message",
        ]
        trace_records = core_store.list_trace_records(trace_id=turn.result["trace_id"])
        turn_trace_types = [
            record.event_type for record in trace_records
            if not record.event_type.startswith("memory.")
        ]
        assert turn_trace_types == [
            "turn.started",
            "item.delta",
            "turn.completed",
        ]

        rpc_session = await service.handle_rpc(
            RpcRequest(id="3", method="session.get", params={"session_id": session_id})
        )
        rpc_threads = await service.handle_rpc(
            RpcRequest(id="4", method="thread.list", params={"session_id": session_id})
        )
        rpc_turn = await service.handle_rpc(
            RpcRequest(id="5", method="turn.get", params={"turn_id": turn.result["turn_id"]})
        )
        rpc_items = await service.handle_rpc(
            RpcRequest(id="6", method="turn.items", params={"turn_id": turn.result["turn_id"]})
        )
        rpc_traces = await service.handle_rpc(
            RpcRequest(id="7", method="core.trace.list", params={"trace_id": turn.result["trace_id"]})
        )

        assert rpc_session.error is None
        assert rpc_session.result["session"]["session_id"] == session_id
        assert rpc_threads.error is None
        assert rpc_threads.result["count"] == 1
        assert rpc_turn.error is None
        assert rpc_turn.result["turn"]["input"] == "core mirror"
        assert rpc_items.error is None
        assert rpc_items.result["count"] == 3
        assert rpc_traces.error is None
        assert rpc_traces.result["count"] >= 3

    asyncio.run(run())


def test_policy_approval_and_retry_mirror_core_governance_records(tmp_path):
    async def run():
        core_store = CoreSQLiteStore(tmp_path / "core.sqlite3")
        pool = GatewayRuntimePool(
            model="fake-model",
            agent_factory=lambda _model: FakeAgent(),
            runtime_backend="simple",
            store=GatewaySessionStore(tmp_path / "sessions"),
            core_store=core_store,
        )
        service = GatewayService(pool)
        started = await service.handle_rpc(RpcRequest(id="1", method="session.start"))
        session_id = started.result["session_id"]

        blocked = await service.handle_rpc(
            RpcRequest(
                id="2",
                method="turn.start",
                params={"session_id": session_id, "input": "请写入 demo.txt，内容为 hello"},
            )
        )

        assert blocked.error is None
        completed = blocked.result["events"][-1]
        approval_id = completed["data"]["approval"]["approval_id"]
        retry_id = completed["data"]["retry_context"]["retry_id"]

        approvals = core_store.list_approvals(decision="pending")
        retries = core_store.list_retries(approval_id=approval_id, status="pending_approval")
        traces = core_store.list_trace_records(trace_id=blocked.result["trace_id"])

        assert [approval.approval_id for approval in approvals] == [approval_id]
        assert [retry.retry_id for retry in retries] == [retry_id]
        assert "approval.request" in [trace.event_type for trace in traces]

        rpc_approvals = await service.handle_rpc(
            RpcRequest(id="3", method="core.approval.list", params={"decision": "pending"})
        )
        rpc_retries = await service.handle_rpc(
            RpcRequest(id="4", method="core.retry.list", params={"approval_id": approval_id})
        )
        rpc_traces = await service.handle_rpc(
            RpcRequest(id="5", method="core.trace.list", params={"trace_id": blocked.result["trace_id"]})
        )

        assert rpc_approvals.error is None
        assert rpc_approvals.result["approvals"][0]["approval_id"] == approval_id
        assert rpc_retries.error is None
        assert rpc_retries.result["retries"][0]["retry_id"] == retry_id
        assert rpc_traces.error is None
        assert any(trace["event_type"] == "approval.request" for trace in rpc_traces.result["traces"])

    asyncio.run(run())


def test_turn_completed_artifacts_mirror_core_records(tmp_path):
    async def run():
        artifact_path = tmp_path / "minutes.md"
        artifact_path.write_text("# Minutes\n", encoding="utf-8")
        core_store = CoreSQLiteStore(tmp_path / "core.sqlite3")
        pool = GatewayRuntimePool(
            model="fake-model",
            agent_factory=lambda _model: FakeAgent(),
            runtime_backend="simple",
            store=GatewaySessionStore(tmp_path / "sessions"),
            artifact_registry=ArtifactRegistry(tmp_path / "artifacts", allowed_roots=[tmp_path]),
            core_store=core_store,
            orchestrator=ArtifactWorkflowOrchestrator(artifact_path),
        )
        service = GatewayService(pool)
        started = await service.handle_rpc(RpcRequest(id="1", method="session.start"))
        session_id = started.result["session_id"]

        turn = await service.handle_rpc(
            RpcRequest(
                id="2",
                method="turn.start",
                params={"session_id": session_id, "input": "请分析会议音频"},
            )
        )

        assert turn.error is None
        artifacts = core_store.list_artifacts(domain="meeting", kind="minutes")
        assert len(artifacts) == 1
        assert artifacts[0].owner_session_id == session_id
        assert artifacts[0].owner_turn_id == turn.result["turn_id"]
        assert artifacts[0].uri == str(artifact_path)

        rpc_artifacts = await service.handle_rpc(
            RpcRequest(id="3", method="core.artifact.list", params={"domain": "meeting", "kind": "minutes"})
        )
        assert rpc_artifacts.error is None
        assert rpc_artifacts.result["count"] == 1
        assert rpc_artifacts.result["artifacts"][0]["owner_turn_id"] == turn.result["turn_id"]

        jobs = await service.handle_rpc(
            RpcRequest(id="4", method="job.list", params={"session_id": session_id, "domain": "meeting"})
        )
        assert jobs.error is None
        assert jobs.result["count"] == 1
        job = jobs.result["jobs"][0]
        assert job["workflow_id"] == "meeting.workflow"
        assert job["status"] == "completed"
        assert job["progress"] == 1.0
        assert job["turn_id"] == turn.result["turn_id"]
        assert job["artifact_ids"] == [artifacts[0].artifact_id]
        assert turn.result["events"][-1]["data"]["job_id"] == job["job_id"]

        fetched = await service.handle_rpc(RpcRequest(id="5", method="job.get", params={"job_id": job["job_id"]}))
        assert fetched.error is None
        assert fetched.result["job"]["job_id"] == job["job_id"]

        job_events = await service.handle_rpc(RpcRequest(id="6", method="job.events", params={"job_id": job["job_id"]}))
        assert job_events.error is None
        assert [event["event_type"] for event in job_events.result["events"]] == [
            "job.queued",
            "job.started",
            "job.completed",
        ]

        cancelled = await service.handle_rpc(RpcRequest(id="7", method="job.cancel", params={"job_id": job["job_id"]}))
        assert cancelled.error is None
        assert cancelled.result["job"]["status"] == "completed"

        queued = await service.handle_rpc(
            RpcRequest(id="8", method="job.create", params={"workflow_id": "meeting.workflow", "domain": "meeting"})
        )
        assert queued.error is None
        assert queued.result["job"]["status"] == "queued"
        queued_events = await service.handle_rpc(
            RpcRequest(id="9", method="job.events", params={"job_id": queued.result["job"]["job_id"]})
        )
        assert queued_events.result["events"][0]["event_type"] == "job.queued"

        memory = await service.handle_rpc(
            RpcRequest(
                id="10",
                method="memory.list",
                params={"session_id": session_id, "kind": "artifact_ref:minutes"},
            )
        )
        assert memory.error is None
        assert memory.result["count"] == 1
        assert memory.result["memories"][0]["source_artifact_id"] == artifacts[0].artifact_id
        assert memory.result["memories"][0]["refs"][0]["type"] == "artifact"

    asyncio.run(run())


def test_video_studio_workflow_registers_planning_artifacts(tmp_path):
    async def run():
        core_store = CoreSQLiteStore(tmp_path / "core.sqlite3")
        artifact_registry = ArtifactRegistry(tmp_path / "artifacts")
        pool = GatewayRuntimePool(
            model="fake-model",
            agent_factory=lambda _model: FakeAgent(),
            runtime_backend="simple",
            store=GatewaySessionStore(tmp_path / "sessions"),
            core_store=core_store,
            artifact_registry=artifact_registry,
        )
        service = GatewayService(pool)
        started = await service.handle_rpc(RpcRequest(id="1", method="session.start"))
        session_id = started.result["session_id"]

        turn = await service.handle_rpc(
            RpcRequest(
                id="2",
                method="turn.start",
                params={
                    "session_id": session_id,
                    "domain": "video_studio",
                    "input": "请为主题: 城市夜跑 生成一个短视频脚本、分镜和镜头清单",
                },
            )
        )

        assert turn.error is None
        completed = turn.result["events"][-1]
        assert completed["data"]["domain"] == "video_studio"
        assert completed["data"]["workflow_id"] == "video.workflow"
        assert "视频工作流规划已完成" in turn.result["final_text"]

        artifacts = core_store.list_artifacts(domain="video_studio")
        assert {artifact.kind for artifact in artifacts} == {
            "brief",
            "script",
            "storyboard",
            "shot_list",
            "asset_plan",
            "render_output",
        }
        assert {artifact.owner_session_id for artifact in artifacts} == {session_id}
        assert {artifact.owner_turn_id for artifact in artifacts} == {turn.result["turn_id"]}
        artifacts_by_kind = {artifact.kind: artifact for artifact in artifacts}
        assert artifacts_by_kind["brief"].parent_ids == []
        assert artifacts_by_kind["script"].parent_ids == [artifacts_by_kind["brief"].artifact_id]
        assert artifacts_by_kind["storyboard"].parent_ids == [artifacts_by_kind["script"].artifact_id]
        assert artifacts_by_kind["shot_list"].parent_ids == [artifacts_by_kind["storyboard"].artifact_id]
        assert artifacts_by_kind["asset_plan"].parent_ids == [artifacts_by_kind["shot_list"].artifact_id]
        assert artifacts_by_kind["render_output"].parent_ids == [artifacts_by_kind["asset_plan"].artifact_id]

        lineage = await service.handle_rpc(
            RpcRequest(
                id="3",
                method="artifact.lineage",
                params={"session_id": session_id, "domain": "video_studio"},
            )
        )
        assert lineage.error is None
        assert lineage.result["count"] == 6
        assert lineage.result["roots"] == [artifacts_by_kind["brief"].artifact_id]
        assert lineage.result["leaves"] == [artifacts_by_kind["render_output"].artifact_id]
        assert lineage.result["edges"] == [
            {
                "source_artifact_id": artifacts_by_kind["brief"].artifact_id,
                "target_artifact_id": artifacts_by_kind["script"].artifact_id,
                "relation": "derived_from",
            },
            {
                "source_artifact_id": artifacts_by_kind["script"].artifact_id,
                "target_artifact_id": artifacts_by_kind["storyboard"].artifact_id,
                "relation": "derived_from",
            },
            {
                "source_artifact_id": artifacts_by_kind["storyboard"].artifact_id,
                "target_artifact_id": artifacts_by_kind["shot_list"].artifact_id,
                "relation": "derived_from",
            },
            {
                "source_artifact_id": artifacts_by_kind["shot_list"].artifact_id,
                "target_artifact_id": artifacts_by_kind["asset_plan"].artifact_id,
                "relation": "derived_from",
            },
            {
                "source_artifact_id": artifacts_by_kind["asset_plan"].artifact_id,
                "target_artifact_id": artifacts_by_kind["render_output"].artifact_id,
                "relation": "derived_from",
            },
        ]
        shot_lineage = await service.handle_rpc(
            RpcRequest(
                id="4",
                method="core.artifact.lineage",
                params={"artifact_id": artifacts_by_kind["render_output"].artifact_id},
            )
        )
        assert shot_lineage.error is None
        assert {item["kind"] for item in shot_lineage.result["artifacts"]} == {
            "brief",
            "script",
            "storyboard",
            "shot_list",
            "asset_plan",
            "render_output",
        }

        jobs = await service.handle_rpc(
            RpcRequest(id="5", method="job.list", params={"session_id": session_id, "domain": "video_studio"})
        )
        assert jobs.error is None
        assert jobs.result["count"] == 1
        job = jobs.result["jobs"][0]
        assert job["workflow_id"] == "video.workflow"
        assert job["status"] == "completed"
        assert set(job["artifact_ids"]) == {artifact.artifact_id for artifact in artifacts}

    asyncio.run(run())


def test_gateway_rpc_unknown_session(tmp_path):
    async def run():
        service = GatewayService(
            GatewayRuntimePool(
                agent_factory=lambda _model: FakeAgent(),
                runtime_backend="simple",
                store=GatewaySessionStore(tmp_path),
            )
        )
        response = await service.handle_rpc(
            RpcRequest(
                id="bad",
                method="turn.start",
                params={"session_id": "missing", "input": "hello"},
            )
        )
        assert response.result is None
        assert response.error is not None
        assert response.error.code == "SESSION_NOT_FOUND"

    asyncio.run(run())


def test_gateway_resume_and_interrupt(tmp_path):
    async def run():
        service = GatewayService(
            GatewayRuntimePool(
                model="fake-model",
                agent_factory=lambda _model: FakeAgent(),
                runtime_backend="simple",
                store=GatewaySessionStore(tmp_path),
            )
        )
        started = await service.handle_rpc(RpcRequest(id="1", method="session.start"))
        session_id = started.result["session_id"]
        await service.handle_rpc(
            RpcRequest(
                id="2",
                method="turn.start",
                params={"session_id": session_id, "input": "first"},
            )
        )
        await service.handle_rpc(
            RpcRequest(
                id="3",
                method="session.close",
                params={"session_id": session_id},
            )
        )
        resumed = await service.handle_rpc(
            RpcRequest(
                id="4",
                method="session.resume",
                params={"session_id": session_id},
            )
        )
        assert resumed.error is None
        assert resumed.result["session_id"] == session_id

        interrupted = await service.handle_rpc(
            RpcRequest(
                id="5",
                method="turn.interrupt",
                params={"session_id": session_id},
            )
        )
        assert interrupted.error is None
        assert interrupted.result["interrupted"] is True

        continued = await service.handle_rpc(
            RpcRequest(
                id="6",
                method="turn.continue",
                params={"session_id": session_id},
            )
        )
        assert continued.error is None
        assert continued.result["events"][0]["type"] == "item.status"

    asyncio.run(run())


def test_gateway_session_list_read_and_transcript(tmp_path):
    async def run():
        service = GatewayService(
            GatewayRuntimePool(
                model="fake-model",
                agent_factory=lambda _model: FakeAgent(),
                runtime_backend="simple",
                store=GatewaySessionStore(tmp_path),
            )
        )
        started = await service.handle_rpc(RpcRequest(id="1", method="session.start"))
        session_id = started.result["session_id"]
        await service.handle_rpc(
            RpcRequest(
                id="2",
                method="turn.start",
                params={"session_id": session_id, "input": "hello"},
            )
        )

        sessions = await service.handle_rpc(RpcRequest(id="3", method="session.list"))
        assert sessions.error is None
        assert sessions.result["sessions"][0]["session_id"] == session_id

        session = await service.handle_rpc(
            RpcRequest(id="4", method="session.read", params={"session_id": session_id})
        )
        assert session.error is None
        assert session.result["session"]["backend"] == "simple"

        transcript = await service.handle_rpc(
            RpcRequest(id="5", method="session.transcript", params={"session_id": session_id})
        )
        assert transcript.error is None
        assert [item["role"] for item in transcript.result["transcript"]] == ["user", "assistant"]
        assert transcript.result["transcript"][1]["content"] == "reply: hello"

    asyncio.run(run())


def test_gateway_session_scope_resolution_and_isolation(tmp_path):
    """PhaseA frozen gateway scope baseline: session queries must isolate by app scope."""
    async def run():
        service = GatewayService(
            GatewayRuntimePool(
                model="fake-model",
                agent_factory=lambda _model: FakeAgent(),
                runtime_backend="simple",
                store=GatewaySessionStore(tmp_path),
            )
        )

        knowledge_started = await service.handle_rpc(
            RpcRequest(
                id="1",
                method="session.start",
                params={
                    "scope": {
                        "app_id": "knowledge",
                        "project_id": "project_knowledge",
                        "workspace_id": "workspace_knowledge",
                    }
                },
            )
        )
        assert knowledge_started.error is None
        knowledge_session_id = knowledge_started.result["session_id"]
        assert knowledge_started.result["app_id"] == "knowledge"
        assert knowledge_started.result["project_id"] == "project_knowledge"
        assert knowledge_started.result["workspace_id"] == "workspace_knowledge"

        default_started = await service.handle_rpc(RpcRequest(id="2", method="session.start"))
        assert default_started.error is None
        default_session_id = default_started.result["session_id"]

        listed_knowledge = await service.handle_rpc(
            RpcRequest(id="3", method="session.list", params={"app_id": "knowledge"})
        )
        assert listed_knowledge.error is None
        assert [session["session_id"] for session in listed_knowledge.result["sessions"]] == [knowledge_session_id]
        assert listed_knowledge.result["sessions"][0]["app_id"] == "knowledge"

        listed_all = await service.handle_rpc(
            RpcRequest(id="4", method="session.list", params={"scope_mode": "all"})
        )
        assert listed_all.error is None
        assert {session["session_id"] for session in listed_all.result["sessions"]} == {
            knowledge_session_id,
            default_session_id,
        }

        denied = await service.handle_rpc(
            RpcRequest(
                id="5",
                method="session.read",
                params={"session_id": knowledge_session_id, "app_id": "meeting"},
            )
        )
        assert denied.error is not None
        assert denied.error.code == "INVALID_PARAMS"
        assert "requested scope" in denied.error.message

        allowed = await service.handle_rpc(
            RpcRequest(
                id="6",
                method="session.read",
                params={"session_id": knowledge_session_id, "scope_mode": "all"},
            )
        )
        assert allowed.error is None
        assert allowed.result["session"]["app_id"] == "knowledge"

        transcript_denied = await service.handle_rpc(
            RpcRequest(
                id="7",
                method="session.transcript",
                params={"session_id": knowledge_session_id, "app_id": "meeting"},
            )
        )
        assert transcript_denied.error is not None
        assert transcript_denied.error.code == "INVALID_PARAMS"

    asyncio.run(run())


def test_turn_scope_override_keeps_runtime_events_and_memory_in_requested_scope(tmp_path):
    async def run():
        core_store = CoreSQLiteStore(tmp_path / "core.sqlite3")
        service = GatewayService(
            GatewayRuntimePool(
                model="fake-model",
                agent_factory=lambda _model: FakeAgent(),
                runtime_backend="simple",
                store=GatewaySessionStore(tmp_path / "sessions"),
                core_store=core_store,
            )
        )

        started = await service.handle_rpc(RpcRequest(id="1", method="session.start"))
        session_id = started.result["session_id"]

        turn = await service.handle_rpc(
            RpcRequest(
                id="2",
                method="turn.start",
                params={
                    "session_id": session_id,
                    "input": "hello scoped world",
                    "scope": {
                        "app_id": "knowledge",
                        "project_id": "project_k",
                        "workspace_id": "workspace_k",
                    },
                },
            )
        )
        assert turn.error is None
        assert turn.result["app_id"] == "knowledge"
        assert all(event["app_id"] == "knowledge" for event in turn.result["events"])
        assert all(event["workspace_id"] == "workspace_k" for event in turn.result["events"])

        turn_record = core_store.get_turn(turn.result["turn_id"])
        assert turn_record.app_id == "knowledge"
        assert turn_record.workspace_id == "workspace_k"

        memories = await service.handle_rpc(
            RpcRequest(id="3", method="memory.list", params={"app_id": "knowledge", "session_id": session_id})
        )
        assert memories.error is None
        assert memories.result["count"] == 1
        assert memories.result["memories"][0]["kind"] == "session_summary"
        assert memories.result["memories"][0]["app_id"] == "knowledge"
        assert memories.result["memories"][0]["workspace_id"] == "workspace_k"

    asyncio.run(run())


def test_turn_mutation_rpcs_enforce_session_scope(tmp_path):
    async def run():
        service = GatewayService(
            GatewayRuntimePool(
                model="fake-model",
                runtime_factory=lambda _model: FakeBundle(),
                runtime_backend="openharness",
                store=GatewaySessionStore(tmp_path),
            )
        )
        started = await service.handle_rpc(
            RpcRequest(
                id="1",
                method="session.start",
                params={"scope": {"app_id": "knowledge", "workspace_id": "workspace_k"}},
            )
        )
        session_id = started.result["session_id"]

        for rpc_id, method in [("2", "turn.continue"), ("3", "turn.interrupt")]:
            denied = await service.handle_rpc(
                RpcRequest(id=rpc_id, method=method, params={"session_id": session_id, "app_id": "meeting"})
            )
            assert denied.error is not None
            assert denied.error.code == "INVALID_PARAMS"

    asyncio.run(run())


def test_gateway_unknown_method_error_code(tmp_path):
    async def run():
        service = GatewayService(
            GatewayRuntimePool(
                agent_factory=lambda _model: FakeAgent(),
                runtime_backend="simple",
                store=GatewaySessionStore(tmp_path),
            )
        )
        response = await service.handle_rpc(RpcRequest(id="bad", method="missing.method"))
        assert response.error is not None
        assert response.error.code == "METHOD_NOT_FOUND"

    asyncio.run(run())


def test_gateway_rpc_router_stable_error_codes(tmp_path):
    async def run():
        service = GatewayService(
            GatewayRuntimePool(
                agent_factory=lambda _model: FakeAgent(),
                runtime_backend="simple",
                store=GatewaySessionStore(tmp_path),
            )
        )

        invalid = await service.handle_rpc(RpcRequest(id="invalid", method="session.close", params={}))
        assert invalid.error is not None
        assert invalid.error.code == "INVALID_PARAMS"

        async def fail_handler(_params):
            raise RuntimeError("intentional handler failure")

        service.rpc_router.register("test.failure", fail_handler, capability="tests")
        failed = await service.handle_rpc(RpcRequest(id="failed", method="test.failure"))
        assert failed.error is not None
        assert failed.error.code == "RUNTIME_ERROR"
        assert "intentional handler failure" in failed.error.message

    asyncio.run(run())


def test_gateway_runtime_bundle_backend_paths(tmp_path):
    async def run():
        service = GatewayService(
            GatewayRuntimePool(
                model="fake-model",
                runtime_factory=lambda _model: FakeBundle(),
                runtime_backend="openharness",
                store=GatewaySessionStore(tmp_path),
            )
        )
        started = await service.handle_rpc(RpcRequest(id="1", method="session.start"))
        assert started.error is None
        assert started.result["backend"] == "openharness"
        session_id = started.result["session_id"]

        turn = await service.handle_rpc(
            RpcRequest(
                id="2",
                method="turn.start",
                params={"session_id": session_id, "input": "hello"},
            )
        )
        assert turn.error is None
        assert turn.result["final_text"] == "bundle: hello"

        continued = await service.handle_rpc(
            RpcRequest(
                id="3",
                method="turn.continue",
                params={"session_id": session_id},
            )
        )
        assert continued.error is None
        assert continued.result["final_text"] == "continued"

    asyncio.run(run())


def test_turn_retry_enforces_session_scope(tmp_path):
    async def run():
        service = GatewayService(
            GatewayRuntimePool(
                model="fake-model",
                agent_factory=lambda _model: FakeAgent(),
                runtime_backend="simple",
                store=GatewaySessionStore(tmp_path),
            )
        )
        started = await service.handle_rpc(
            RpcRequest(
                id="1",
                method="session.start",
                params={"scope": {"app_id": "knowledge", "workspace_id": "workspace_k"}},
            )
        )
        session_id = started.result["session_id"]

        blocked = await service.handle_rpc(
            RpcRequest(
                id="2",
                method="turn.start",
                params={"session_id": session_id, "input": "请帮我写入 release.txt 并提交"},
            )
        )
        assert blocked.error is None
        approval_id = blocked.result["events"][-1]["data"]["approval"]["approval_id"]

        denied = await service.handle_rpc(
            RpcRequest(
                id="3",
                method="turn.retry",
                params={"session_id": session_id, "approval_id": approval_id, "app_id": "meeting"},
            )
        )
        assert denied.error is not None
        assert denied.error.code == "INVALID_PARAMS"

    asyncio.run(run())


def test_normalize_runtime_event_uses_class_name_not_identity():
    event = normalize_runtime_event(
        AssistantTextDelta(),
        session_id="sess_test",
        turn_id="turn_test",
    )
    assert event.type == "item.delta"
    assert event.data["text"] == "hello"

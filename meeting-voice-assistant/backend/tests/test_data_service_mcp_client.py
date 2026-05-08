from types import SimpleNamespace

import pytest

from app.core.data_service_mcp_client import DataServiceMcpClient


class FakeDataServiceMcpClient(DataServiceMcpClient):
    def __init__(self):
        self.settings = SimpleNamespace(
            mcp_enabled=True,
            mcp_workspace_id="meeting-knowledge",
            mcp_workspace_name="Meeting Knowledge",
            mcp_session_ephemeral=True,
            mcp_session_ttl_seconds=86400,
            mcp_build_timeout=5.0,
            mcp_build_poll_interval=0.01,
            request_timeout=5.0,
            mcp_delete_on_close=True,
        )
        self.calls = []

    async def call_tool(self, name, arguments):
        self.calls.append((name, arguments))
        if name == "knowledge_workspace_create":
            return {"status": "ok", "workspace_id": "meeting-knowledge", "data": {}}
        if name == "knowledge_session_create":
            return {"status": "ok", "data": {"session": {"session_id": "ksess_test"}}}
        if name == "knowledge_session_ingest":
            return {"status": "ok", "data": {"source": {"source_id": "src_test"}}}
        if name == "knowledge_session_build_start":
            return {"status": "queued", "operation_id": "sop_test", "data": {"stage": "queued"}}
        if name == "knowledge_session_build_status":
            return {"status": "succeeded", "operation_id": "sop_test", "data": {"stage": "completed"}}
        if name == "knowledge_graph_snapshot":
            return {
                "status": "ok",
                "data": {
                    "nodes": [{"id": "actor:speaker_0", "type": "actor", "label": "speaker_0"}],
                    "edges": [],
                    "communities": [{"id": "comm_test", "title": "验收", "summary": "验收安排"}],
                    "stats": {"node_count": 1, "actor_count": 1, "unit_count": 0, "community_count": 1},
                },
            }
        if name == "knowledge_actor_summary":
            return {
                "status": "ok",
                "data": {
                    "actor": {"actor_id": arguments["actor_id"], "label": arguments["actor_id"]},
                    "summary": "speaker summary",
                    "decisions": [],
                    "tasks": [],
                    "risks": [],
                    "questions": [],
                    "statements": [],
                    "source_refs": [],
                },
            }
        if name == "knowledge_session_close":
            return {"status": "closed", "warnings": []}
        if name == "knowledge_session_delete":
            return {"status": "disposed", "warnings": []}
        raise AssertionError(f"unexpected tool: {name}")


@pytest.mark.asyncio
async def test_ingest_meeting_session_uses_structured_session_tools():
    client = FakeDataServiceMcpClient()

    result = await client.ingest_meeting_session(
        meeting_id="upload_12345678",
        title="项目会议",
        segments=[
            {"speaker": "speaker_0", "text": "我们下周一完成最终验收。", "start_time": 0.0, "end_time": 2.0},
            {"speaker": "speaker_1", "text": "我负责整理发布材料。", "start_time": 2.0, "end_time": 4.0},
        ],
    )

    assert result["status"] == "ok"
    assert result["session_id"] == "ksess_test"
    assert result["source_id"] == "src_test"
    assert result["session_graph"]["communities"][0]["id"] == "comm_test"
    assert [name for name, _args in client.calls] == [
        "knowledge_workspace_create",
        "knowledge_session_create",
        "knowledge_session_ingest",
        "knowledge_session_build_start",
        "knowledge_session_build_status",
        "knowledge_graph_snapshot",
        "knowledge_actor_summary",
        "knowledge_actor_summary",
    ]
    ingest_args = client.calls[2][1]
    assert ingest_args["content_format"] == "turns"
    assert ingest_args["records"][0]["record_id"] == "turn-0001"
    assert ingest_args["records"][0]["actor_id"] == "speaker_0"


@pytest.mark.asyncio
async def test_close_meeting_session_closes_and_deletes_session():
    client = FakeDataServiceMcpClient()

    result = await client.close_meeting_session({"workspace_id": "meeting-knowledge", "session_id": "ksess_test"})

    assert result["status"] == "disposed"
    assert [name for name, _args in client.calls] == ["knowledge_session_close", "knowledge_session_delete"]

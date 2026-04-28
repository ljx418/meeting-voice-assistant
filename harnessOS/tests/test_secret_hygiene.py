from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from apps.gateway.approvals import ApprovalStore
from apps.gateway.artifacts import ArtifactRegistry
from apps.gateway.protocol import RpcRequest
from apps.gateway.retries import RetryStore
from apps.gateway.runtime import GatewayRuntimePool
from apps.gateway.service import GatewayService
from apps.gateway.storage import GatewaySessionStore
from apps.gateway.traces import TraceStore


SECRET = "sk-test-1234567890"
AUTH = "Authorization: Bearer abcdef123456"


class EchoAgent:
    def invoke(self, user_input: str):
        return {"status": "success", "content": f"echo {user_input}", "model": "fake-model"}


def _service(tmp_path: Path) -> GatewayService:
    artifacts = ArtifactRegistry(tmp_path / "artifacts")
    traces = TraceStore(tmp_path / "traces")
    approvals = ApprovalStore(tmp_path / "approvals")
    retries = RetryStore(tmp_path / "retries")
    pool = GatewayRuntimePool(
        model="fake-model",
        agent_factory=lambda _model: EchoAgent(),
        runtime_backend="simple",
        store=GatewaySessionStore(tmp_path / "sessions"),
        artifact_registry=artifacts,
        trace_store=traces,
        approval_store=approvals,
        retry_store=retries,
    )
    return GatewayService(
        runtime_pool=pool,
        artifact_registry=artifacts,
        trace_store=traces,
        approval_store=approvals,
        retry_store=retries,
    )


def test_trace_and_session_event_persistence_masks_secrets(tmp_path):
    async def run():
        service = _service(tmp_path)
        started = await service.handle_rpc(RpcRequest(id="1", method="session.start"))
        session_id = started.result["session_id"]
        turn = await service.handle_rpc(
            RpcRequest(
                id="2",
                method="turn.start",
                params={"session_id": session_id, "input": f"请记住 {SECRET} 和 {AUTH}"},
            )
        )

        assert turn.error is None
        event_log = (tmp_path / "sessions" / session_id / "events.jsonl").read_text(encoding="utf-8")
        trace_log = (tmp_path / "traces" / "index.jsonl").read_text(encoding="utf-8")
        assert SECRET not in event_log
        assert "abcdef123456" not in event_log
        assert SECRET not in trace_log
        assert "abcdef123456" not in trace_log
        assert "[REDACTED]" in event_log
        assert "[REDACTED]" in trace_log

        trace = await service.handle_rpc(
            RpcRequest(id="3", method="trace.get", params={"trace_id": turn.result["trace_id"]})
        )
        assert trace.error is None
        trace_payload = json.dumps(trace.result, ensure_ascii=False)
        assert SECRET not in trace_payload
        assert "abcdef123456" not in trace_payload

    asyncio.run(run())


def test_approval_and_retry_persistence_masks_secrets(tmp_path):
    async def run():
        service = _service(tmp_path)
        started = await service.handle_rpc(RpcRequest(id="1", method="session.start"))
        session_id = started.result["session_id"]
        blocked = await service.handle_rpc(
            RpcRequest(
                id="2",
                method="turn.start",
                params={"session_id": session_id, "input": f"请写入 secret.txt，内容为 {SECRET}"},
            )
        )

        assert blocked.error is None
        approval_index = (tmp_path / "approvals" / "index.json").read_text(encoding="utf-8")
        retry_index = (tmp_path / "retries" / "index.json").read_text(encoding="utf-8")
        assert SECRET not in approval_index
        assert SECRET not in retry_index
        assert "[REDACTED]" in approval_index
        assert "[REDACTED]" in retry_index

    asyncio.run(run())


def test_artifact_read_masks_secret_content_and_metadata(tmp_path):
    artifact_file = tmp_path / "artifact.json"
    artifact_file.write_text(
        json.dumps({"api_key": SECRET, "note": AUTH}, ensure_ascii=False),
        encoding="utf-8",
    )

    async def run():
        service = _service(tmp_path)
        registered = await service.handle_rpc(
            RpcRequest(
                id="1",
                method="artifact.register",
                params={
                    "path": str(artifact_file),
                    "metadata": {"token": SECRET, "note": AUTH},
                },
            )
        )
        artifact_id = registered.result["artifact"]["artifact_id"]
        assert SECRET not in json.dumps(registered.result, ensure_ascii=False)

        read = await service.handle_rpc(
            RpcRequest(id="2", method="artifact.read", params={"artifact_id": artifact_id})
        )

        assert read.error is None
        payload = json.dumps(read.result, ensure_ascii=False)
        assert SECRET not in payload
        assert "abcdef123456" not in payload
        assert "[REDACTED]" in payload

    asyncio.run(run())

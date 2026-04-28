from __future__ import annotations

import asyncio
import json
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from apps.gateway.protocol import RpcRequest
from apps.gateway.runtime import GatewayRuntimePool
from apps.gateway.service import GatewayService
from apps.gateway.storage import GatewaySessionStore


class FakeAgent:
    def invoke(self, user_input: str):
        return {"status": "success", "content": f"reply: {user_input}"}


def test_rpc_and_service_response_shapes_match(tmp_path):
    async def run():
        service = GatewayService(
            GatewayRuntimePool(
                agent_factory=lambda _model: FakeAgent(),
                runtime_backend="simple",
                store=GatewaySessionStore(tmp_path),
            )
        )
        for request in (
            RpcRequest(id="1", method="initialize"),
            RpcRequest(id="2", method="health.ping"),
            RpcRequest(id="3", method="session.start"),
        ):
            response = await service.handle_rpc(request)
            payload = response.model_dump(mode="json")
            assert set(payload) == {"id", "result", "error"}
            assert payload["id"] == request.id
            assert payload["error"] is None

    asyncio.run(run())


def test_stdio_response_shape_matches_rpc_response():
    process = subprocess.run(
        [sys.executable, "-m", "apps.gateway.stdio_server"],
        input=(
            '{"id":"1","method":"initialize","params":{}}\n'
            '{"id":"2","method":"health.ping","params":{}}\n'
        ),
        text=True,
        capture_output=True,
        cwd=PROJECT_ROOT,
        timeout=10,
        check=False,
    )

    assert process.returncode == 0
    responses = [json.loads(line) for line in process.stdout.splitlines() if line.strip()]
    assert len(responses) == 2
    for index, payload in enumerate(responses, start=1):
        assert set(payload) == {"id", "result", "error"}
        assert payload["id"] == str(index)
        assert payload["error"] is None

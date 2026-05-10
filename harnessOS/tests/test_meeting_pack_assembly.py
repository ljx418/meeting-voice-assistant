from __future__ import annotations

import asyncio

from apps.gateway.protocol import RpcRequest
from apps.gateway.service import GatewayService


def test_meeting_pack_get_exposes_phase_d_assembly_contract():
    async def run():
        service = GatewayService()
        response = await service.handle_rpc(
            RpcRequest(id="pack", method="pack.get", params={"domain": "meeting"})
        )

        assert response.error is None
        pack = response.result["pack"]
        assembly = pack["assembly"]
        assert pack["workflows"] == ["meeting.workflow"]
        assert pack["connector_refs"] == ["meeting_voice_mcp", "funasr_mcp"]
        assert pack["skill_refs"] == ["meeting-minutes", "action-items"]
        assert pack["policy_bundles"] == ["meeting.default"]
        assert set(pack["artifact_kinds"]) == {"transcript", "analysis", "result", "minutes"}
        assert assembly["status"] in {"assembled", "degraded", "blocked"}
        assert "missing_dependencies" in assembly
        assert "blocked_reason" in assembly
        assert "next_actions" in assembly

    asyncio.run(run())

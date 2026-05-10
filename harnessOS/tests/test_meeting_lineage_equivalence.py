from __future__ import annotations

import asyncio

from apps.gateway.protocol import RpcRequest
from tests.meeting_phase_d_helpers import PhaseDMeetingService, make_phase_d_gateway


def test_meeting_lineage_equivalence_requires_four_pack_artifacts(tmp_path):
    audio = tmp_path / "lineage.mp3"
    audio.write_bytes(b"audio")
    service = make_phase_d_gateway(tmp_path, PhaseDMeetingService(tmp_path / "meeting-output"))

    async def run():
        session = await service.handle_rpc(
            RpcRequest(id="session", method="session.start", params={"app_id": "meeting"})
        )
        turn = await service.handle_rpc(
            RpcRequest(
                id="turn",
                method="turn.start",
                params={
                    "session_id": session.result["session_id"],
                    "domain": "meeting",
                    "input": f"请分析 {audio}",
                },
            )
        )
        assert turn.error is None
        lineage = await service.handle_rpc(
            RpcRequest(
                id="lineage",
                method="artifact.lineage",
                params={"session_id": session.result["session_id"], "domain": "meeting", "app_id": "meeting"},
            )
        )

        artifacts = lineage.result["artifacts"]
        kinds = {artifact["kind"] for artifact in artifacts}
        assert {"transcript", "analysis", "result", "minutes"} <= kinds
        assert len(lineage.result["edges"]) >= 3
        assert lineage.result["roots"]
        assert lineage.result["leaves"]
        for artifact in artifacts:
            assert artifact["app_id"] == "meeting"
            assert artifact["owner_session_id"] == session.result["session_id"]

    asyncio.run(run())

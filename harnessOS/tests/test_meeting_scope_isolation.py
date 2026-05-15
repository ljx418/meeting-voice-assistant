from __future__ import annotations

import asyncio

from apps.gateway.protocol import RpcRequest
from tests.meeting_phase_d_helpers import PhaseDMeetingService, make_phase_d_gateway


def test_meeting_artifacts_are_hidden_from_knowledge_scope(tmp_path):
    audio = tmp_path / "scope.mp3"
    audio.write_bytes(b"audio")
    service = make_phase_d_gateway(tmp_path, PhaseDMeetingService(tmp_path / "meeting-output"))

    async def run():
        meeting_session = await service.handle_rpc(
            RpcRequest(id="meeting-session", method="session.start", params={"app_id": "meeting"})
        )
        knowledge_session = await service.handle_rpc(
            RpcRequest(id="knowledge-session", method="session.start", params={"app_id": "knowledge"})
        )
        turn = await service.handle_rpc(
            RpcRequest(
                id="meeting-turn",
                method="turn.start",
                params={
                    "session_id": meeting_session.result["session_id"],
                    "domain": "meeting",
                    "input": f"请处理 {audio}",
                },
            )
        )
        assert turn.error is None

        meeting_lineage = await service.handle_rpc(
            RpcRequest(
                id="meeting-lineage",
                method="artifact.lineage",
                params={
                    "session_id": meeting_session.result["session_id"],
                    "domain": "meeting",
                    "app_id": "meeting",
                },
            )
        )
        knowledge_lineage = await service.handle_rpc(
            RpcRequest(
                id="knowledge-lineage",
                method="artifact.lineage",
                params={
                    "session_id": knowledge_session.result["session_id"],
                    "domain": "meeting",
                    "app_id": "knowledge",
                },
            )
        )

        assert meeting_lineage.error is None
        assert meeting_lineage.result["count"] == 4
        assert knowledge_lineage.error is None
        assert knowledge_lineage.result["count"] == 0

    asyncio.run(run())


def test_legacy_meeting_facade_rejects_non_meeting_session_scope(tmp_path):
    audio = tmp_path / "legacy-scope.mp3"
    audio.write_bytes(b"audio")
    service = make_phase_d_gateway(tmp_path, PhaseDMeetingService(tmp_path / "meeting-output"))

    async def run():
        knowledge_session = await service.handle_rpc(
            RpcRequest(id="knowledge-session", method="session.start", params={"app_id": "knowledge"})
        )
        response = await service.handle_rpc(
            RpcRequest(
                id="legacy",
                method="meeting.process_recording",
                params={"session_id": knowledge_session.result["session_id"], "path": str(audio)},
            )
        )

        assert response.error is not None
        assert response.error.code == "SCOPE_MISMATCH"
        assert "session does not belong to the requested scope" in response.error.message

    asyncio.run(run())

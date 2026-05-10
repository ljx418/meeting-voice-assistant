from __future__ import annotations

import asyncio

from apps.gateway.protocol import RpcRequest
from tests.meeting_phase_d_helpers import PhaseDMeetingService, make_phase_d_gateway


def test_meeting_workflow_standard_path_registers_four_artifacts_with_bindings(tmp_path):
    audio = tmp_path / "phase-d.mp3"
    audio.write_bytes(b"audio")
    service = make_phase_d_gateway(tmp_path, PhaseDMeetingService(tmp_path / "meeting-output"))

    async def run():
        session = await service.handle_rpc(
            RpcRequest(id="session", method="session.start", params={"app_id": "meeting"})
        )
        response = await service.handle_rpc(
            RpcRequest(
                id="turn",
                method="turn.start",
                params={
                    "session_id": session.result["session_id"],
                    "domain": "meeting",
                    "input": f"请处理会议音频 {audio}",
                },
            )
        )

        assert response.error is None
        completed = response.result["events"][-1]
        meeting = completed["data"]["meeting"]
        assert completed["data"]["workflow_id"] == "meeting.workflow"
        assert set(meeting["artifacts"]) == {"transcript", "analysis", "result", "minutes"}
        assert [meeting["artifact_records"][kind]["app_id"] for kind in meeting["artifacts"]] == [
            "meeting",
            "meeting",
            "meeting",
            "meeting",
        ]

        lineage = await service.handle_rpc(
            RpcRequest(
                id="lineage",
                method="artifact.lineage",
                params={"session_id": session.result["session_id"], "domain": "meeting", "app_id": "meeting"},
            )
        )
        assert lineage.error is None
        assert [artifact["kind"] for artifact in lineage.result["artifacts"]] == [
            "transcript",
            "analysis",
            "result",
            "minutes",
        ]
        assert len(lineage.result["edges"]) == 3
        assert lineage.result["roots"] == [meeting["artifacts"]["transcript"]["artifact_id"]]
        assert lineage.result["leaves"] == [meeting["artifacts"]["minutes"]["artifact_id"]]

    asyncio.run(run())

from __future__ import annotations

import asyncio

from apps.gateway.protocol import RpcRequest
from tests.meeting_phase_d_helpers import PhaseDMeetingService, make_phase_d_gateway


EXPECTED_KINDS = {"transcript", "analysis", "result", "minutes"}


def test_legacy_meeting_process_recording_facade_returns_pack_artifacts_and_warning(tmp_path):
    audio = tmp_path / "legacy.mp3"
    audio.write_bytes(b"audio")
    service = make_phase_d_gateway(tmp_path, PhaseDMeetingService(tmp_path / "meeting-output"))

    async def run():
        response = await service.handle_rpc(
            RpcRequest(
                id="legacy",
                method="meeting.process_recording",
                params={"path": str(audio), "engine": "funasr", "language": "en", "session_id": "legacy_session"},
            )
        )

        assert response.error is None
        warning = response.result["deprecation_warning"]
        assert response.result["legacy_facade"] is True
        assert response.result["workflow_id"] == "meeting.workflow"
        assert warning["legacy_method"] == "meeting.process_recording"
        assert warning["replacement"] == "turn.start / meeting.workflow"
        assert warning["sunset_stage"] == "stage_1_compat_facade"
        assert warning["trace_event"] == "legacy_facade.deprecation_warning"
        assert set(response.result["artifacts"]) == EXPECTED_KINDS

        traces = await service.handle_rpc(
            RpcRequest(
                id="traces",
                method="trace.list",
                params={"session_id": "legacy_session", "app_id": "meeting", "event_type": warning["trace_event"]},
            )
        )
        assert traces.error is None
        assert traces.result["count"] >= 1
        assert all(trace["event_type"] == warning["trace_event"] for trace in traces.result["traces"])

    asyncio.run(run())


def test_legacy_meeting_process_recording_is_equivalent_to_pack_workflow(tmp_path):
    audio = tmp_path / "equivalence.mp3"
    audio.write_bytes(b"audio")
    service = make_phase_d_gateway(tmp_path, PhaseDMeetingService(tmp_path / "meeting-output"))

    async def run():
        legacy = await service.handle_rpc(
            RpcRequest(
                id="legacy",
                method="meeting.process_recording",
                params={"path": str(audio), "engine": "funasr", "language": "en", "session_id": "legacy_equiv"},
            )
        )
        standard_session = await service.handle_rpc(
            RpcRequest(id="standard-session", method="session.start", params={"app_id": "meeting"})
        )
        standard = await service.handle_rpc(
            RpcRequest(
                id="standard-turn",
                method="turn.start",
                params={
                    "session_id": standard_session.result["session_id"],
                    "domain": "meeting",
                    "input": f"请分析 {audio}",
                },
            )
        )

        assert legacy.error is None
        assert standard.error is None
        standard_data = standard.result["events"][-1]["data"]
        standard_meeting = standard_data["meeting"]
        legacy_meeting = legacy.result
        assert legacy_meeting["analysis"] == standard_meeting["analysis"]
        assert legacy_meeting["transcript_chars"] == standard_meeting["transcript_chars"]
        assert set(legacy_meeting["artifacts"]) == set(standard_meeting["artifacts"]) == EXPECTED_KINDS
        assert legacy_meeting["gateway_session_id"] == "legacy_equiv"
        assert legacy_meeting["job_id"].startswith("job_")

        legacy_lineage = await service.handle_rpc(
            RpcRequest(
                id="legacy-lineage",
                method="artifact.lineage",
                params={"session_id": "legacy_equiv", "domain": "meeting", "app_id": "meeting"},
            )
        )
        standard_lineage = await service.handle_rpc(
            RpcRequest(
                id="standard-lineage",
                method="artifact.lineage",
                params={"session_id": standard_session.result["session_id"], "domain": "meeting", "app_id": "meeting"},
            )
        )
        assert legacy_lineage.error is None
        assert standard_lineage.error is None
        assert _lineage_shape(legacy_lineage.result) == _lineage_shape(standard_lineage.result)

        legacy_jobs = await service.handle_rpc(
            RpcRequest(id="legacy-jobs", method="job.list", params={"session_id": "legacy_equiv", "domain": "meeting", "app_id": "meeting"})
        )
        standard_jobs = await service.handle_rpc(
            RpcRequest(
                id="standard-jobs",
                method="job.list",
                params={"session_id": standard_session.result["session_id"], "domain": "meeting", "app_id": "meeting"},
            )
        )
        assert legacy_jobs.result["count"] == standard_jobs.result["count"] == 1
        assert legacy_jobs.result["jobs"][0]["status"] == standard_jobs.result["jobs"][0]["status"] == "completed"
        assert set(legacy_jobs.result["jobs"][0]["artifact_ids"]) == {
            artifact["artifact_id"] for artifact in legacy_lineage.result["artifacts"]
        }
        assert set(standard_jobs.result["jobs"][0]["artifact_ids"]) == {
            artifact["artifact_id"] for artifact in standard_lineage.result["artifacts"]
        }

        legacy_traces = await service.handle_rpc(
            RpcRequest(id="legacy-traces", method="trace.list", params={"session_id": "legacy_equiv", "app_id": "meeting"})
        )
        standard_traces = await service.handle_rpc(
            RpcRequest(
                id="standard-traces",
                method="trace.list",
                params={"session_id": standard_session.result["session_id"], "app_id": "meeting"},
            )
        )
        assert legacy_traces.result["count"] >= standard_traces.result["count"] >= 2
        assert "legacy_facade.deprecation_warning" in {
            trace["event_type"] for trace in legacy_traces.result["traces"]
        }
        assert "turn.completed" in {trace["event_type"] for trace in standard_traces.result["traces"]}

    asyncio.run(run())


def _lineage_shape(lineage: dict) -> dict[str, object]:
    artifacts = lineage["artifacts"]
    by_id = {artifact["artifact_id"]: artifact["kind"] for artifact in artifacts}
    return {
        "kinds": {artifact["kind"] for artifact in artifacts},
        "roots": {by_id[artifact_id] for artifact_id in lineage["roots"]},
        "leaves": {by_id[artifact_id] for artifact_id in lineage["leaves"]},
        "edges": {
            (by_id[edge["source_artifact_id"]], by_id[edge["target_artifact_id"]])
            for edge in lineage["edges"]
        },
        "scopes": {
            (artifact["kind"], artifact["app_id"], artifact["domain"])
            for artifact in artifacts
        },
    }

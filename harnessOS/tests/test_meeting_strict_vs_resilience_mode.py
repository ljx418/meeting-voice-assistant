from __future__ import annotations

import asyncio

import pytest

from apps.gateway.artifacts import ArtifactRegistry
from core.apps import ScopeContext
from packs.meeting.connector import MeetingMcpError
from packs.meeting.workflow import MeetingWorkflow, register_meeting_artifacts


class FailingAnalysisService:
    async def analyze_text(self, text, *, title=None):
        raise RuntimeError("meeting_voice_mcp unavailable")


def _submitted_fixture(tmp_path):
    transcript_artifact = tmp_path / "funasr-transcript.json"
    transcript_artifact.write_text('{"result":{"transcript":"hello"}}\n', encoding="utf-8")
    return {
        "job": {"job_id": "job_funasr", "status": "completed"},
        "artifact": {"artifact_id": "art_funasr", "path": str(transcript_artifact)},
    }


def test_meeting_resilience_mode_records_fallback_metadata(tmp_path, monkeypatch):
    monkeypatch.delenv("HARNESS_MEETING_E2E_STRICT", raising=False)
    registry = ArtifactRegistry(tmp_path / "artifacts")
    workflow = MeetingWorkflow(service=FailingAnalysisService(), artifact_registry=registry)

    async def run():
        result = await workflow._analyze_transcript_with_fallback(
            audio_path=tmp_path / "resilience.mp3",
            transcript="hello meeting",
            submitted=_submitted_fixture(tmp_path),
            connector={"metadata": {"execution": "mcp_stdio"}},
        )
        registered = register_meeting_artifacts(
            result,
            artifact_registry=registry,
            session_id="sess_resilience",
            turn_id="turn_resilience",
            scope=ScopeContext(app_id="meeting"),
        )
        assert result["execution"]["mode"] == "funasr_mcp_then_local_meeting_analysis"
        assert "meeting_voice_mcp unavailable" in result["execution"]["fallback_reason"]
        assert registered["minutes"]["record"]["metadata"]["fallback"] == "local_analysis"
        assert registered["minutes"]["record"]["metadata"]["fallback_reason"] == "meeting_voice_mcp unavailable"

    asyncio.run(run())


def test_meeting_strict_mode_does_not_silently_fallback(tmp_path, monkeypatch):
    monkeypatch.setenv("HARNESS_MEETING_E2E_STRICT", "1")
    workflow = MeetingWorkflow(service=FailingAnalysisService(), artifact_registry=ArtifactRegistry(tmp_path / "artifacts"))

    async def run():
        with pytest.raises(MeetingMcpError, match="strict mode"):
            await workflow._analyze_transcript_with_fallback(
                audio_path=tmp_path / "strict.mp3",
                transcript="hello meeting",
                submitted=_submitted_fixture(tmp_path),
                connector={"metadata": {"execution": "mcp_stdio"}},
            )

    asyncio.run(run())

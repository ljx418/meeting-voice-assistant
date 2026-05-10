from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from apps.gateway.artifacts import ArtifactRegistry
from apps.gateway.runtime import GatewayRuntimePool
from apps.gateway.service import GatewayService
from apps.gateway.storage import GatewaySessionStore
from apps.gateway.traces import TraceStore
from packs.meeting.workflow import MeetingWorkflow


class FakeAgent:
    def invoke(self, user_input: str):
        return {"status": "success", "content": f"reply: {user_input}"}


class PhaseDMeetingService:
    def __init__(self, artifact_dir: Path):
        self.artifact_dir = artifact_dir
        self.recording_calls: list[dict[str, object]] = []
        self.text_calls: list[dict[str, object]] = []

    def _artifacts(self) -> dict[str, str]:
        self.artifact_dir.mkdir(parents=True, exist_ok=True)
        paths = {
            "transcript": self.artifact_dir / "transcript.json",
            "analysis": self.artifact_dir / "analysis.json",
            "result": self.artifact_dir / "result.json",
            "minutes": self.artifact_dir / "minutes.md",
        }
        paths["transcript"].write_text('{"text":"phase d transcript"}\n', encoding="utf-8")
        paths["analysis"].write_text('{"theme":"PhaseD Meeting"}\n', encoding="utf-8")
        paths["result"].write_text('{"ok":true}\n', encoding="utf-8")
        paths["minutes"].write_text("# PhaseD Meeting\n\n- action item\n", encoding="utf-8")
        return {kind: str(path) for kind, path in paths.items()}

    async def process_recording(self, path, *, engine=None, language=None, title=None):
        self.recording_calls.append({"path": path, "engine": engine, "language": language, "title": title})
        return {
            "source_path": path,
            "session_id": "meeting_phase_d",
            "transcript_chars": 24,
            "segment_count": 1,
            "analysis": {"theme": "PhaseD Meeting", "summary": "PhaseD migration standard path."},
            "minutes_path": str(self.artifact_dir / "minutes.md"),
            "artifacts": self._artifacts(),
            "execution": {
                "mode": "meeting_mcp_process_recording",
                "steps": [
                    {"connector_id": "meeting_voice_mcp", "tool": "meeting_process_file"},
                ],
            },
        }

    async def analyze_text(self, text, *, title=None):
        self.text_calls.append({"text": text, "title": title})
        return {
            "source_path": None,
            "session_id": "meeting_phase_d_text",
            "transcript_chars": len(text),
            "segment_count": 0,
            "analysis": {"theme": title or "PhaseD Text", "summary": text[:80]},
            "minutes_path": str(self.artifact_dir / "minutes.md"),
            "artifacts": self._artifacts(),
        }


def make_phase_d_gateway(tmp_path: Path, meeting_service: PhaseDMeetingService) -> GatewayService:
    registry = ArtifactRegistry(tmp_path / "artifacts")
    trace_store = TraceStore(tmp_path / "traces")
    workflow = MeetingWorkflow(service=meeting_service, artifact_registry=registry)
    pool = GatewayRuntimePool(
        agent_factory=lambda _model: FakeAgent(),
        runtime_backend="simple",
        store=GatewaySessionStore(tmp_path / "sessions"),
        meeting_workflow=workflow,
        artifact_registry=registry,
        trace_store=trace_store,
    )
    service = GatewayService(pool, trace_store=trace_store)
    service.meeting_service = meeting_service
    return service

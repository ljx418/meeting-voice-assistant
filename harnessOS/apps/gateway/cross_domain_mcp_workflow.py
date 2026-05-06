"""Cross-domain MCP workflow runner for Meeting -> Knowledge acceptance."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional

from apps.gateway.knowledge_mcp_workflow import KnowledgeMcpWorkflowRunner
from apps.gateway.protocol import RpcRequest
from apps.gateway.service import GatewayService


@dataclass(frozen=True)
class MeetingToKnowledgeResult:
    """Result for one Meeting -> Knowledge cross-domain MCP workflow."""

    status: str
    session_id: str
    meeting: dict[str, Any]
    knowledge: dict[str, Any]
    artifact_lineage: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "session_id": self.session_id,
            "meeting": self.meeting,
            "knowledge": self.knowledge,
            "artifact_lineage": self.artifact_lineage,
        }


class MeetingToKnowledgeMcpRunner:
    """Run audio -> meeting minutes -> knowledge import/build/query through MCP connectors."""

    def __init__(self, gateway_service: GatewayService) -> None:
        self.gateway_service = gateway_service

    async def run(
        self,
        *,
        audio_path: str,
        query: str,
        workspace_name: str = "HarnessOS Meeting Knowledge",
        session_id: Optional[str] = None,
        poll_interval: float = 0.2,
        max_polls: int = 120,
    ) -> MeetingToKnowledgeResult:
        """Run the cross-domain acceptance workflow."""
        resolved_session_id = session_id or await self._start_session()
        meeting_result = await self._run_meeting_turn(
            session_id=resolved_session_id,
            audio_path=audio_path,
        )
        minutes = _meeting_artifact(meeting_result, "minutes")
        transcript = _meeting_artifact(meeting_result, "transcript")
        minutes_text = _read_artifact_text(minutes)
        parent_artifact_ids = [
            artifact_id
            for artifact_id in (
                transcript.get("artifact_id"),
                minutes.get("artifact_id"),
            )
            if isinstance(artifact_id, str) and artifact_id
        ]

        knowledge_result = KnowledgeMcpWorkflowRunner(
            self.gateway_service.connector_execution_runtime,
        ).run_acceptance(
            name=workspace_name,
            query=query,
            texts=[
                {
                    "title": Path(audio_path).stem,
                    "content": minutes_text,
                    "metadata": {
                        "source": "meeting_minutes",
                        "source_audio_path": str(Path(audio_path).expanduser()),
                        "minutes_artifact_id": minutes.get("artifact_id"),
                        "transcript_artifact_id": transcript.get("artifact_id"),
                    },
                }
            ],
            session_id=resolved_session_id,
            parent_artifact_ids=parent_artifact_ids,
            poll_interval=poll_interval,
            max_polls=max_polls,
        )
        lineage = self.gateway_service.core_service.artifact_lineage(
            owner_session_id=resolved_session_id,
        )
        status = "ok" if knowledge_result.status in {"ok", "archived", "completed"} else knowledge_result.status
        return MeetingToKnowledgeResult(
            status=status,
            session_id=resolved_session_id,
            meeting=meeting_result,
            knowledge=knowledge_result.to_dict(),
            artifact_lineage=lineage,
        )

    async def _start_session(self) -> str:
        response = await self.gateway_service.handle_rpc(RpcRequest(id="cross-session", method="session.start"))
        if response.error is not None:
            raise RuntimeError(response.error.message)
        return str(response.result["session_id"])

    async def _run_meeting_turn(self, *, session_id: str, audio_path: str) -> dict[str, Any]:
        response = await self.gateway_service.handle_rpc(
            RpcRequest(
                id="cross-meeting",
                method="turn.start",
                params={
                    "session_id": session_id,
                    "domain": "meeting",
                    "input": f"请分析 {audio_path}，生成会议纪要",
                },
            )
        )
        if response.error is not None:
            raise RuntimeError(response.error.message)
        events = response.result.get("events") or []
        completed = events[-1] if events else {}
        data = completed.get("data") if isinstance(completed, dict) else {}
        meeting = data.get("meeting") if isinstance(data, dict) else None
        if not isinstance(meeting, dict):
            raise RuntimeError("Meeting workflow did not return meeting payload")
        return meeting


def _meeting_artifact(meeting: dict[str, Any], kind: str) -> dict[str, Any]:
    artifacts = meeting.get("artifacts") or {}
    artifact = artifacts.get(kind) if isinstance(artifacts, dict) else None
    if not isinstance(artifact, dict) or not artifact.get("path"):
        raise RuntimeError(f"Meeting workflow did not return {kind} artifact")
    return artifact


def _read_artifact_text(artifact: dict[str, Any]) -> str:
    path = Path(str(artifact["path"])).expanduser()
    if not path.exists() or not path.is_file():
        raise RuntimeError(f"Meeting artifact file does not exist: {path}")
    return path.read_text(encoding="utf-8")

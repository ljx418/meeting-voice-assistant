"""Meeting Domain Pack workflow implementation."""

from __future__ import annotations

import asyncio
import json
import os
import re
from pathlib import Path
from typing import Any, Optional

from apps.gateway.artifacts import ArtifactError, ArtifactRegistry
from apps.gateway.connector_execution import ConnectorExecutionRuntime
from apps.gateway.connectors import (
    ConnectorRegistry,
    FUNASR_MCP_CONNECTOR_ID,
    MEETING_VOICE_MCP_CONNECTOR_ID,
)
from core.apps import ScopeContext
from packs.meeting.connector import (
    MeetingGatewayService,
    MeetingMcpError,
    SUPPORTED_AUDIO_EXTENSIONS,
)


class MeetingWorkflow:
    """Natural-language meeting workflow used by turn.start."""

    def __init__(
        self,
        service: Optional[MeetingGatewayService] = None,
        artifact_registry: Optional[ArtifactRegistry] = None,
        connector_registry: Optional[ConnectorRegistry] = None,
        connector_execution_runtime: Optional[ConnectorExecutionRuntime] = None,
    ) -> None:
        self.service = service or MeetingGatewayService()
        self.artifact_registry = artifact_registry or ArtifactRegistry()
        self.connector_registry = connector_registry
        self.connector_execution_runtime = connector_execution_runtime

    def should_handle(self, user_input: str, *, domain: Optional[str] = None) -> bool:
        """Return whether this turn should use the meeting workflow."""
        if domain == "meeting":
            return True
        if domain and domain != "meeting":
            return False
        lowered = user_input.lower()
        if any(keyword in lowered for keyword in ("interview", "面试", "候选人", "简历", "candidate", "resume")):
            return False
        has_meeting_keyword = any(
            keyword in lowered
            for keyword in ("meeting", "会议", "纪要", "转写", "音频", "summary", "minutes", "transcribe")
        )
        return has_meeting_keyword and bool(extract_audio_path(user_input))

    async def run(
        self,
        user_input: str,
        *,
        domain: Optional[str] = None,
        session_id: Optional[str] = None,
        turn_id: Optional[str] = None,
        scope: Optional[ScopeContext] = None,
        approval_id: Optional[str] = None,
    ) -> dict[str, Any]:
        """Run a meeting task and return text plus structured metadata."""
        audio_path = extract_audio_path(user_input)
        if audio_path:
            if self.connector_registry is not None and _meeting_strict_mode():
                self.connector_registry.require_available(MEETING_VOICE_MCP_CONNECTOR_ID)
            funasr_connector = self._funasr_mcp_connector()
            if funasr_connector is not None:
                result = await self._process_recording_with_funasr_mcp(
                    audio_path,
                    session_id=session_id,
                    turn_id=turn_id,
                    scope=scope,
                    approval_id=approval_id,
                    connector=funasr_connector,
                )
                if result.get("approval_required"):
                    return result
            else:
                result = await self.service.process_recording(
                    audio_path,
                    engine=None,
                    language=None,
                    title=Path(audio_path).stem,
                )
                result["execution"] = {
                    "mode": "meeting_mcp_process_recording",
                    "steps": [
                        {
                            "connector_id": MEETING_VOICE_MCP_CONNECTOR_ID,
                            "tool": "meeting_process_file",
                        }
                    ],
                }
        elif domain == "meeting":
            result = await self.service.analyze_text(user_input, title="Meeting Notes")
            result["execution"] = {
                "mode": "meeting_mcp_text_analysis",
                "steps": [
                    {
                        "connector_id": MEETING_VOICE_MCP_CONNECTOR_ID,
                        "tool": "meeting_analyze_text",
                    }
                ],
            }
        else:
            raise MeetingMcpError("Meeting workflow requires a supported audio path or explicit domain=meeting text.")
        register_meeting_artifacts(
            result,
            artifact_registry=self.artifact_registry,
            session_id=session_id,
            turn_id=turn_id,
            scope=scope,
        )
        text = format_meeting_final_text(result)
        return {"status": "success", "content": text, "meeting": result}

    def _funasr_mcp_connector(self) -> Optional[dict[str, Any]]:
        if self.connector_execution_runtime is None or self.connector_registry is None:
            return None
        connector = self.connector_registry.get_connector(FUNASR_MCP_CONNECTOR_ID)
        if connector.get("metadata", {}).get("execution") != "mcp_stdio":
            return None
        return connector

    async def _process_recording_with_funasr_mcp(
        self,
        audio_path: str,
        *,
        session_id: Optional[str],
        turn_id: Optional[str],
        scope: Optional[ScopeContext],
        approval_id: Optional[str],
        connector: dict[str, Any],
    ) -> dict[str, Any]:
        path = Path(audio_path).expanduser().resolve()
        if not path.exists() or not path.is_file():
            raise MeetingMcpError(f"Audio file does not exist: {path}")
        submitted = self.connector_execution_runtime.submit(
            connector_id=FUNASR_MCP_CONNECTOR_ID,
            tool="funasr_recognize_file",
            payload={"path": str(path)},
            session_id=session_id,
            turn_id=turn_id,
            scope=scope,
            approval_id=approval_id,
        )
        if submitted.get("approval_required"):
            approval = submitted.get("approval") or {}
            requested_approval_id = approval.get("approval_id")
            return {
                "status": "success",
                "content": f"操作需要审批。Approval ID: {requested_approval_id}",
                "approval_required": True,
                "approval": approval,
                "retry_context": submitted.get("retry_context"),
                "meeting": {
                    "source_path": str(path),
                    "transcription": {
                        "connector_id": FUNASR_MCP_CONNECTOR_ID,
                        "connector_job_id": submitted.get("job", {}).get("job_id"),
                        "mode": connector.get("metadata", {}).get("execution"),
                        "tool": "funasr_recognize_file",
                    },
                    "execution": {
                        "mode": "funasr_mcp_then_meeting_mcp_analysis",
                        "steps": [
                            {
                                "connector_id": FUNASR_MCP_CONNECTOR_ID,
                                "tool": "funasr_recognize_file",
                            },
                            {
                                "connector_id": MEETING_VOICE_MCP_CONNECTOR_ID,
                                "tool": "meeting_analyze_text",
                            },
                        ],
                    },
                },
            }
        if submitted["job"]["status"] != "completed":
            failure = submitted["job"].get("metadata", {}).get("failure_context") or {}
            message = failure.get("message") or submitted["job"]["status"]
            raise MeetingMcpError(f"FunASR MCP transcription failed: {message}")
        transcript = _extract_funasr_transcript(submitted)
        if not transcript.strip():
            raise MeetingMcpError("FunASR MCP transcription returned empty transcript")
        result = await self._analyze_transcript_with_fallback(
            audio_path=path,
            transcript=transcript,
            submitted=submitted,
            connector=connector,
        )
        result["source_path"] = str(path)
        result["transcription"] = {
            "connector_id": FUNASR_MCP_CONNECTOR_ID,
            "connector_job_id": submitted["job"]["job_id"],
            "artifact_id": submitted.get("artifact", {}).get("artifact_id"),
            "mode": connector.get("metadata", {}).get("execution"),
            "tool": "funasr_recognize_file",
        }
        result["execution"] = {
            "mode": "funasr_mcp_then_meeting_mcp_analysis",
            "steps": [
                {
                    "connector_id": FUNASR_MCP_CONNECTOR_ID,
                    "tool": "funasr_recognize_file",
                },
                {
                    "connector_id": MEETING_VOICE_MCP_CONNECTOR_ID,
                    "tool": "meeting_analyze_text",
                },
            ],
        }
        result["transcript_chars"] = len(transcript)
        raw = result.get("raw")
        if isinstance(raw, dict):
            raw["transcript"] = transcript
        else:
            result["raw"] = {"transcript": transcript}
        artifacts = result.get("artifacts")
        if not isinstance(artifacts, dict):
            artifacts = {}
            result["artifacts"] = artifacts
        artifacts.setdefault("transcript", self._write_funasr_transcript_artifact(path, transcript, result))
        artifacts.setdefault("result", self._write_meeting_result_artifact(path, transcript, result))
        return result

    async def _analyze_transcript_with_fallback(
        self,
        *,
        audio_path: Path,
        transcript: str,
        submitted: dict[str, Any],
        connector: dict[str, Any],
    ) -> dict[str, Any]:
        timeout = _meeting_analysis_timeout()
        try:
            return await asyncio.wait_for(
                self.service.analyze_text(transcript, title=audio_path.stem),
                timeout=timeout,
            )
        except Exception as exc:
            if _meeting_strict_mode():
                raise MeetingMcpError(f"Meeting MCP analysis failed in strict mode: {exc}") from exc
            return self._build_local_analysis_result(
                audio_path=audio_path,
                transcript=transcript,
                submitted=submitted,
                connector=connector,
                fallback_reason=str(exc),
            )

    def _build_local_analysis_result(
        self,
        *,
        audio_path: Path,
        transcript: str,
        submitted: dict[str, Any],
        connector: dict[str, Any],
        fallback_reason: str,
    ) -> dict[str, Any]:
        output_dir = self.artifact_registry.root / "meeting" / "local_analysis" / audio_path.stem
        output_dir.mkdir(parents=True, exist_ok=True)
        summary = transcript.strip().replace("\n", " ")[:500]
        analysis = {
            "theme": audio_path.stem,
            "summary": summary,
            "fallback_reason": fallback_reason,
        }
        result_payload = {
            "source_path": str(audio_path),
            "transcript_chars": len(transcript),
            "analysis": analysis,
            "transcription_artifact_id": submitted.get("artifact", {}).get("artifact_id"),
        }
        transcript_path = output_dir / "transcript.json"
        analysis_path = output_dir / "analysis.json"
        result_path = output_dir / "result.json"
        minutes_path = output_dir / "minutes.md"
        transcript_path.write_text(
            json.dumps(
                {
                    "source_path": str(audio_path),
                    "transcript": transcript,
                    "connector_job_id": submitted.get("job", {}).get("job_id"),
                },
                ensure_ascii=False,
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        analysis_path.write_text(json.dumps(analysis, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        result_path.write_text(json.dumps(result_payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        minutes_path.write_text(
            f"# {audio_path.stem}\n\n## 摘要\n\n{summary}\n",
            encoding="utf-8",
        )
        return {
            "source_path": str(audio_path),
            "session_id": None,
            "transcript_chars": len(transcript),
            "segment_count": 0,
            "analysis": analysis,
            "minutes_path": str(minutes_path),
            "raw": {"transcript": transcript, "analysis_fallback": True},
            "artifacts": {
                "transcript": str(transcript_path),
                "analysis": str(analysis_path),
                "result": str(result_path),
                "minutes": str(minutes_path),
            },
            "execution": {
                "mode": "funasr_mcp_then_local_meeting_analysis",
                "fallback_reason": fallback_reason,
                "steps": [
                    {
                        "connector_id": FUNASR_MCP_CONNECTOR_ID,
                        "tool": "funasr_recognize_file",
                    },
                    {
                        "connector_id": MEETING_VOICE_MCP_CONNECTOR_ID,
                        "tool": "meeting_analyze_text",
                        "fallback": "local_analysis",
                    },
                ],
            },
        }

    def _write_funasr_transcript_artifact(
        self,
        audio_path: Path,
        transcript: str,
        result: dict[str, Any],
    ) -> str:
        output_dir = self.artifact_registry.root / "meeting" / "funasr_transcripts"
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / f"{audio_path.stem}_transcript.json"
        payload = {
            "source_path": str(audio_path),
            "session_id": result.get("session_id"),
            "transcript": transcript,
            "transcription": result.get("transcription"),
        }
        output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return str(output_path)

    def _write_meeting_result_artifact(
        self,
        audio_path: Path,
        transcript: str,
        result: dict[str, Any],
    ) -> str:
        output_dir = self.artifact_registry.root / "meeting" / "workflow_results"
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / f"{audio_path.stem}_result.json"
        payload = {
            "source_path": str(audio_path),
            "session_id": result.get("session_id"),
            "transcript_chars": len(transcript),
            "analysis": result.get("analysis") or {},
            "transcription": result.get("transcription"),
            "execution": result.get("execution"),
        }
        output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return str(output_path)


def extract_audio_path(text: str) -> Optional[str]:
    """Extract the first supported local audio path from user text."""
    extension_pattern = "|".join(re.escape(ext.lstrip(".")) for ext in sorted(SUPPORTED_AUDIO_EXTENSIONS))
    for match in re.finditer(rf"\.({extension_pattern})\b", text, flags=re.IGNORECASE):
        prefix = text[:match.start()]
        slash_positions = [index for index, char in enumerate(prefix) if char == "/"]
        if not slash_positions:
            continue
        candidates = []
        existing_candidates = []
        for start in reversed(slash_positions):
            candidate = text[start:match.end()].strip().strip("\"'")
            candidate = candidate.rstrip(" \t\r\n，。；;、,.)）]】")
            if candidate:
                candidates.append(candidate)
                if Path(candidate).expanduser().exists():
                    existing_candidates.append(candidate)
        if existing_candidates:
            return max(existing_candidates, key=len)
        if candidates:
            return candidates[-1]
    return None


def format_meeting_final_text(result: dict[str, Any]) -> str:
    """Render a user-facing meeting workflow result."""
    analysis = result.get("analysis") or {}
    theme = analysis.get("theme") or "未识别主题"
    summary = analysis.get("summary") or ""
    minutes_path = result.get("minutes_path") or ""
    artifacts = result.get("artifacts") or {}
    lines = [
        "会议分析已完成。",
        f"主题：{theme}",
        f"转写字数：{result.get('transcript_chars', 0)}",
        f"分段数量：{result.get('segment_count', 0)}",
    ]
    if summary:
        lines.append(f"摘要：{summary}")
    execution = result.get("execution") or {}
    execution_steps = execution.get("steps") if isinstance(execution, dict) else None
    if isinstance(execution_steps, list) and execution_steps:
        execution_parts: list[str] = []
        for step in execution_steps:
            if not isinstance(step, dict):
                continue
            connector_id = step.get("connector_id")
            tool = step.get("tool")
            if isinstance(connector_id, str) and isinstance(tool, str):
                execution_parts.append(f"connector {connector_id}.{tool}")
        if execution_parts:
            lines.append(f"标准入口：{' -> '.join(execution_parts)}")
    if minutes_path:
        lines.append(f"会议纪要：{minutes_path}")
    if artifacts:
        artifact_parts = []
        for name, value in artifacts.items():
            if isinstance(value, dict):
                path = value.get("path", "")
                artifact_id = value.get("artifact_id")
                suffix = f" ({artifact_id})" if artifact_id else ""
                artifact_parts.append(f"{name}: {path}{suffix}")
            else:
                artifact_parts.append(f"{name}: {value}")
        artifact_text = "，".join(artifact_parts)
        lines.append(f"Artifacts：{artifact_text}")
    return "\n".join(lines)


def register_meeting_artifacts(
    result: dict[str, Any],
    *,
    artifact_registry: ArtifactRegistry,
    session_id: Optional[str] = None,
    turn_id: Optional[str] = None,
    scope: Optional[ScopeContext] = None,
) -> dict[str, Any]:
    """Register meeting output paths as harnessOS artifact records."""
    artifacts = result.get("artifacts") or {}
    if not isinstance(artifacts, dict):
        return {}

    registered: dict[str, Any] = {}
    for kind, value in _ordered_meeting_artifacts(artifacts):
        path = value.get("path") if isinstance(value, dict) else value
        if not isinstance(path, str) or not path:
            continue
        parent_kind = _meeting_artifact_parent_kind(str(kind), registered)
        try:
            source_metadata = _meeting_transcription_metadata(result) if str(kind) == "transcript" else {}
            record = artifact_registry.register_file(
                path,
                session_id=session_id,
                turn_id=turn_id,
                app_id=scope.app_id if scope else "default",
                project_id=scope.project_id if scope else None,
                workspace_id=scope.workspace_id if scope else None,
                domain="meeting",
                kind=str(kind),
                metadata={
                    "meeting_session_id": result.get("session_id"),
                    "source_path": result.get("source_path"),
                    "source_artifact_id": registered[parent_kind]["artifact_id"] if parent_kind else None,
                    "lineage_step": str(kind),
                    **_meeting_fallback_metadata(result),
                    **source_metadata,
                },
            )
        except ArtifactError:
            continue
        registered[str(kind)] = {"path": path, "artifact_id": record["artifact_id"], "record": record}

    if registered:
        result["artifacts"] = registered
        result["artifact_records"] = {kind: item["record"] for kind, item in registered.items()}
    return registered


def _ordered_meeting_artifacts(artifacts: dict[str, Any]) -> list[tuple[str, Any]]:
    preferred_order = ("transcript", "analysis", "result", "minutes")
    ordered = [(kind, artifacts[kind]) for kind in preferred_order if kind in artifacts]
    ordered.extend((str(kind), value) for kind, value in artifacts.items() if str(kind) not in preferred_order)
    return ordered


def _meeting_artifact_parent_kind(kind: str, registered: dict[str, Any]) -> Optional[str]:
    parent_by_kind = {
        "analysis": "transcript",
        "result": "analysis",
        "minutes": "result",
    }
    parent_kind = parent_by_kind.get(kind)
    if parent_kind in registered:
        return parent_kind
    return None


def _meeting_transcription_metadata(result: dict[str, Any]) -> dict[str, Any]:
    transcription = result.get("transcription")
    if not isinstance(transcription, dict):
        return {}
    return {
        "connector_id": transcription.get("connector_id"),
        "connector_job_id": transcription.get("connector_job_id"),
        "transcription_artifact_id": transcription.get("artifact_id"),
        "transcription_mode": transcription.get("mode"),
        "transcription_tool": transcription.get("tool"),
    }


def _meeting_fallback_metadata(result: dict[str, Any]) -> dict[str, Any]:
    execution = result.get("execution")
    if not isinstance(execution, dict):
        return {}
    fallback_reason = execution.get("fallback_reason")
    if not fallback_reason:
        return {}
    return {
        "fallback": "local_analysis",
        "fallback_reason": fallback_reason,
        "fallback_mode": execution.get("mode"),
    }


def _extract_funasr_transcript(submitted: dict[str, Any]) -> str:
    artifact = submitted.get("artifact") or {}
    path = artifact.get("path")
    if not isinstance(path, str) or not path:
        raise MeetingMcpError("FunASR MCP submission did not return a result artifact")
    payload = _read_json_file(path)
    result = payload.get("result")
    candidates = _walk_transcript_candidates(result)
    for candidate in candidates:
        text = str(candidate or "").strip()
        if text:
            return text
    raise MeetingMcpError("FunASR MCP result did not contain transcript text")


def _read_json_file(path: str) -> dict[str, Any]:
    try:
        data = Path(path).read_text(encoding="utf-8")
        payload = json.loads(data)
    except Exception as exc:
        raise MeetingMcpError(f"Failed to read FunASR MCP result artifact: {exc}") from exc
    if not isinstance(payload, dict):
        raise MeetingMcpError("FunASR MCP result artifact is not a JSON object")
    return payload


def _walk_transcript_candidates(value: Any) -> list[Any]:
    candidates: list[Any] = []
    if isinstance(value, dict):
        for key in ("transcript", "text", "recognized_text", "result", "output"):
            if key in value and not isinstance(value[key], (dict, list)):
                candidates.append(value[key])
        for key in ("content", "mcp_result", "data", "result", "output"):
            if key in value:
                candidates.extend(_walk_transcript_candidates(value[key]))
    elif isinstance(value, list):
        for item in value:
            candidates.extend(_walk_transcript_candidates(item))
    return candidates


def _meeting_analysis_timeout() -> float:
    try:
        return max(1.0, float(os.getenv("HARNESS_MEETING_ANALYSIS_TIMEOUT", "30")))
    except ValueError:
        return 30.0


def _meeting_strict_mode() -> bool:
    value = os.getenv("HARNESS_MEETING_E2E_STRICT", "")
    return value.strip().lower() in {"1", "true", "yes", "on", "strict"}

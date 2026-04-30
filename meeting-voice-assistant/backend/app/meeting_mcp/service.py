"""Service facade for exposing meeting capabilities over MCP."""

from __future__ import annotations

import json
from dataclasses import asdict, is_dataclass
from pathlib import Path
from typing import Any, Optional
from uuid import uuid4

from app.config import config
from app.core.asr import ASRFactory
from app.core.audio_analyzer import AudioAnalyzer
from app.core.audio_analyzer.state import TranscriptSegment
from app.core.llm_analyzer import LLMAnalyzer


class MeetingMcpService:
    """Small application service used by the meeting MCP stdio server."""

    def __init__(self, output_root: Optional[Path] = None) -> None:
        self.output_root = Path(output_root or config.workspace_output_dir).expanduser().resolve()
        self.latest_session_id: Optional[str] = None

    async def transcribe_file(
        self,
        path: str,
        *,
        engine: Optional[str] = None,
        language: str = "zh",
        session_id: Optional[str] = None,
    ) -> dict[str, Any]:
        """Transcribe one local audio/video file through the configured ASR adapter."""
        file_path = Path(path).expanduser().resolve()
        if not file_path.exists() or not file_path.is_file():
            raise FileNotFoundError(f"Audio file not found: {file_path}")

        resolved_session_id = session_id or f"meeting_{uuid4().hex[:8]}"
        adapter = ASRFactory.create(engine or config.asr.engine)
        segments: list[dict[str, Any]] = []
        speakers: set[str] = set()
        duration = 0.0

        try:
            if hasattr(adapter, "initialize"):
                await adapter.initialize()
            async for result in adapter.recognize_file(file_path):
                segment = {
                    "text": result.text,
                    "speaker": result.speaker or "unknown",
                    "start_time": float(result.start_time or 0),
                    "end_time": float(result.end_time or 0),
                    "confidence": float(getattr(result, "confidence", 1.0) or 1.0),
                    "is_final": bool(getattr(result, "is_final", True)),
                }
                segments.append(segment)
                speakers.add(segment["speaker"])
                duration = max(duration, segment["end_time"])
        finally:
            if hasattr(adapter, "close"):
                await adapter.close()

        text = " ".join(segment["text"] for segment in segments if segment.get("text"))
        payload = {
            "session_id": resolved_session_id,
            "engine": engine or config.asr.engine,
            "language": language,
            "source_path": str(file_path),
            "text": text,
            "segments": segments,
            "speaker_count": len([speaker for speaker in speakers if speaker and speaker != "unknown"]),
            "duration": duration,
        }
        self.latest_session_id = resolved_session_id
        self._write_artifact(resolved_session_id, "transcript.json", payload)
        return payload

    async def analyze_text(
        self,
        text: str,
        *,
        session_id: Optional[str] = None,
        mode: str = "audio_analyzer",
    ) -> dict[str, Any]:
        """Analyze meeting transcript text into structured meeting notes."""
        if not text or len(text.strip()) < 10:
            raise ValueError("text must contain at least 10 non-empty characters")
        resolved_session_id = session_id or f"meeting_{uuid4().hex[:8]}"

        if mode == "audio_analyzer":
            result = AudioAnalyzer().analyze_transcript(text)
        elif mode == "llm":
            analyzer = LLMAnalyzer(
                provider=config.llm.provider,
                api_key=config.llm.dashscope_api_key,
                endpoint=config.llm.dashscope_endpoint,
                model=config.llm.dashscope_model,
            )
            try:
                result = await analyzer.analyze_text(text)
            finally:
                await analyzer.close()
        else:
            raise ValueError("mode must be 'audio_analyzer' or 'llm'")

        payload = {
            "session_id": resolved_session_id,
            "mode": mode,
            **_analysis_result_to_dict(result),
        }
        self.latest_session_id = resolved_session_id
        self._write_artifact(resolved_session_id, "analysis.json", payload)
        return payload

    async def process_file(
        self,
        path: str,
        *,
        engine: Optional[str] = None,
        language: str = "zh",
        analyze: bool = True,
        mode: str = "audio_analyzer",
    ) -> dict[str, Any]:
        """Transcribe a file and optionally analyze the resulting transcript."""
        session_id = f"meeting_{uuid4().hex[:8]}"
        transcription = await self.transcribe_file(
            path,
            engine=engine,
            language=language,
            session_id=session_id,
        )
        analysis = None
        if analyze and transcription.get("text"):
            analysis = await self.analyze_text(
                transcription["text"],
                session_id=session_id,
                mode=mode,
            )
        payload = {
            "session_id": session_id,
            "transcript": transcription.get("text", ""),
            "segments": transcription.get("segments", []),
            "analysis": analysis,
            "artifacts": {},
        }
        self.latest_session_id = session_id
        self._write_artifact(session_id, "result.json", payload)
        payload["artifacts"] = self._artifact_paths(session_id)
        self._write_artifact(session_id, "result.json", payload)
        return payload

    def formats(self) -> dict[str, Any]:
        """Return supported meeting input formats."""
        return {
            "audio": ["mp3", "wav", "m4a", "ogg", "flac", "webm"],
            "video": ["mp4", "webm"],
            "engines": ASRFactory.available_engines(),
        }

    def agent_guide(self) -> dict[str, Any]:
        """Return concise instructions for agents using the meeting MCP tools."""
        return {
            "scope": "meeting",
            "non_goals": ["interview workflows", "candidate scoring", "answer coaching"],
            "recommended_workflows": [
                {
                    "goal": "Transcribe and summarize a local meeting recording",
                    "steps": [
                        "Call meeting_process_file with path, engine, language, analyze=true.",
                        "Inspect transcript length, segment count, analysis.theme, analysis.summary, and action_items.",
                        "Call meeting_build_minutes with the returned session_id to produce a human-readable Markdown minutes artifact.",
                    ],
                },
                {
                    "goal": "Analyze an existing transcript",
                    "steps": [
                        "Call meeting_analyze_text with the transcript text.",
                        "Call meeting_build_minutes with the returned session_id if a Markdown artifact is needed.",
                    ],
                },
            ],
            "quality_checks": [
                "A successful file run should return a non-empty transcript and at least one artifact path.",
                "For meeting scenarios, prefer action_items, key_points, speaker_roles, and chapters over raw transcript text.",
                "If the ASR engine is funasr, ensure the FunASR service endpoint is reachable before processing files.",
            ],
        }

    def latest_session(self) -> dict[str, Any]:
        """Return the latest MCP-produced session summary."""
        session_id = self.latest_session_id or self._latest_session_id_by_mtime()
        if not session_id:
            return {"session_id": None, "artifacts": {}}
        return {
            "session_id": session_id,
            "artifacts": self._artifact_paths(session_id),
        }

    def build_minutes(
        self,
        *,
        session_id: Optional[str] = None,
        title: Optional[str] = None,
        include_transcript_preview: bool = True,
    ) -> dict[str, Any]:
        """Build a Markdown meeting-minutes artifact from a previous MCP session."""
        resolved_session_id = session_id or self.latest_session().get("session_id")
        if not resolved_session_id:
            raise ValueError("session_id is required when no latest meeting session exists")

        analysis = self._read_json_artifact(resolved_session_id, "analysis.json") or {}
        result = self._read_json_artifact(resolved_session_id, "result.json") or {}
        transcript_payload = self._read_json_artifact(resolved_session_id, "transcript.json") or {}
        transcript = result.get("transcript") or transcript_payload.get("text") or ""
        segments = result.get("segments") or transcript_payload.get("segments") or []
        analysis_data = result.get("analysis") or analysis
        if not analysis_data and not transcript:
            raise FileNotFoundError(f"No meeting artifacts found for session: {resolved_session_id}")

        markdown = _render_minutes_markdown(
            session_id=resolved_session_id,
            title=title or analysis_data.get("theme") or "Meeting Minutes",
            analysis=analysis_data,
            transcript=transcript,
            segments=segments,
            include_transcript_preview=include_transcript_preview,
        )
        path = self._session_dir(resolved_session_id) / "minutes.md"
        path.write_text(markdown + "\n", encoding="utf-8")
        self.latest_session_id = resolved_session_id
        return {
            "session_id": resolved_session_id,
            "path": str(path),
            "markdown": markdown,
            "artifacts": self._artifact_paths(resolved_session_id),
        }

    def _session_dir(self, session_id: str) -> Path:
        path = self.output_root / session_id
        path.mkdir(parents=True, exist_ok=True)
        return path

    def _write_artifact(self, session_id: str, filename: str, payload: dict[str, Any]) -> Path:
        path = self._session_dir(session_id) / filename
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return path

    def _artifact_paths(self, session_id: str) -> dict[str, str]:
        session_dir = self._session_dir(session_id)
        return {
            path.stem: str(path)
            for path in sorted([*session_dir.glob("*.json"), *session_dir.glob("*.md")])
        }

    def _read_json_artifact(self, session_id: str, filename: str) -> Optional[dict[str, Any]]:
        path = self._session_dir(session_id) / filename
        if not path.exists():
            return None
        return json.loads(path.read_text(encoding="utf-8"))

    def _latest_session_id_by_mtime(self) -> Optional[str]:
        if not self.output_root.exists():
            return None
        session_dirs = [
            path for path in self.output_root.iterdir()
            if path.is_dir() and path.name.startswith("meeting_")
        ]
        if not session_dirs:
            return None
        latest = max(session_dirs, key=lambda path: path.stat().st_mtime)
        return latest.name


def _analysis_result_to_dict(result: Any) -> dict[str, Any]:
    if hasattr(result, "to_dict"):
        data = result.to_dict()
    elif is_dataclass(result):
        data = asdict(result)
    elif hasattr(result, "__dict__"):
        data = dict(result.__dict__)
    elif isinstance(result, dict):
        data = dict(result)
    else:
        data = {}
    return {
        "theme": data.get("theme"),
        "summary": data.get("summary"),
        "chapters": _jsonable_list(data.get("chapters", [])),
        "speaker_roles": _jsonable_list(data.get("speaker_roles", [])),
        "topics": list(data.get("topics", []) or []),
        "key_points": list(data.get("key_points", []) or []),
        "action_items": _jsonable_list(data.get("action_items", [])),
        "raw_response": data.get("raw_response", ""),
    }


def _jsonable_list(items: Any) -> list[Any]:
    result = []
    for item in items or []:
        if hasattr(item, "to_dict"):
            result.append(item.to_dict())
        elif is_dataclass(item):
            result.append(asdict(item))
        else:
            result.append(item)
    return result


def _render_minutes_markdown(
    *,
    session_id: str,
    title: str,
    analysis: dict[str, Any],
    transcript: str,
    segments: list[dict[str, Any]],
    include_transcript_preview: bool,
) -> str:
    lines = [
        f"# {title}",
        "",
        f"- Session: `{session_id}`",
        f"- Transcript characters: {len(transcript)}",
        f"- Segments: {len(segments)}",
        "",
    ]

    summary = analysis.get("summary")
    if summary:
        lines.extend(["## Summary", "", str(summary), ""])

    _append_list_section(lines, "Key Points", analysis.get("key_points"))
    _append_list_section(lines, "Topics", analysis.get("topics"))
    _append_action_items(lines, analysis.get("action_items"))
    _append_structured_section(lines, "Chapters", analysis.get("chapters"))
    _append_structured_section(lines, "Speaker Roles", analysis.get("speaker_roles"))

    if include_transcript_preview and transcript:
        preview = transcript[:1200]
        suffix = "..." if len(transcript) > len(preview) else ""
        lines.extend(["## Transcript Preview", "", f"{preview}{suffix}", ""])

    return "\n".join(lines).rstrip()


def _append_list_section(lines: list[str], title: str, items: Any) -> None:
    values = [item for item in (items or []) if item]
    if not values:
        return
    lines.extend([f"## {title}", ""])
    for item in values:
        lines.append(f"- {item}")
    lines.append("")


def _append_action_items(lines: list[str], items: Any) -> None:
    values = [item for item in (items or []) if item]
    if not values:
        return
    lines.extend(["## Action Items", ""])
    for item in values:
        if isinstance(item, dict):
            owner = item.get("owner") or item.get("assignee")
            task = item.get("task") or item.get("todo") or item.get("content") or json.dumps(item, ensure_ascii=False)
            prefix = f"{owner}: " if owner else ""
            lines.append(f"- {prefix}{task}")
        else:
            lines.append(f"- {item}")
    lines.append("")


def _append_structured_section(lines: list[str], title: str, items: Any) -> None:
    values = [item for item in (items or []) if item]
    if not values:
        return
    lines.extend([f"## {title}", ""])
    for item in values:
        if isinstance(item, dict):
            label = item.get("title") or item.get("name") or item.get("speaker") or item.get("chapter") or "Item"
            lines.append(f"- **{label}**: {json.dumps(item, ensure_ascii=False)}")
        else:
            lines.append(f"- {item}")
    lines.append("")


def segments_from_dicts(items: list[dict[str, Any]]) -> list[TranscriptSegment]:
    """Test helper for constructing AudioAnalyzer-compatible segments."""
    return [
        TranscriptSegment(
            text=str(item.get("text", "")),
            speaker=str(item.get("speaker", "unknown")),
            start_time=float(item.get("start_time", 0) or 0),
            end_time=float(item.get("end_time", 0) or 0),
        )
        for item in items
    ]

"""Local persistence for gateway sessions and event logs."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Dict, Iterable, Optional, Union

from apps.gateway.persistence import append_text_locked, atomic_write_text, file_lock, read_json_locked
from apps.gateway.protocol import GatewayEvent
from apps.gateway.secrets import mask_value

_SESSION_ID_RE = re.compile(r"^[A-Za-z0-9_.:-]{1,128}$")


class GatewaySessionStore:
    """Filesystem-backed session snapshot and event log store."""

    def __init__(self, root: Optional[Union[str, Path]] = None) -> None:
        default_root = Path(__file__).resolve().parents[2] / ".harnessos" / "sessions"
        base = Path(root or default_root).expanduser().resolve()
        self.root = base

    def save_snapshot(self, session: Any) -> None:
        """Persist a lightweight snapshot for a runtime session."""
        path = self._session_dir(session.session_id) / "snapshot.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        agent_messages = list(getattr(getattr(session, "agent", None), "messages", []) or [])
        bundle = getattr(session, "bundle", None)
        if bundle is not None and hasattr(bundle, "engine"):
            agent_messages = [
                message.model_dump(mode="json") if hasattr(message, "model_dump") else message
                for message in getattr(bundle.engine, "messages", []) or []
            ]
        payload = {
            "session_id": session.session_id,
            "model": session.model,
            "app_id": getattr(session, "app_id", "default"),
            "project_id": getattr(session, "project_id", None),
            "workspace_id": getattr(session, "workspace_id", None),
            "state": session.state,
            "backend": getattr(session, "backend", "simple"),
            "interrupted": bool(getattr(session, "interrupted", False)),
            "created_at": session.created_at.isoformat(),
            "last_active_at": session.last_active_at.isoformat(),
            "agent_messages": mask_value(agent_messages),
        }
        atomic_write_text(path, json.dumps(payload, ensure_ascii=False, indent=2) + "\n")

    def load_snapshot(self, session_id: str) -> Dict[str, Any]:
        """Load a session snapshot."""
        path = self._session_dir(session_id) / "snapshot.json"
        if not path.exists():
            raise KeyError(f"Snapshot not found for session_id: {session_id}")
        payload = read_json_locked(path, {}, RuntimeError)
        if not isinstance(payload, dict):
            raise RuntimeError(f"Snapshot must be an object: {path}")
        return payload

    def list_snapshots(self) -> list[Dict[str, Any]]:
        """List persisted session snapshots."""
        if not self.root.exists():
            return []
        snapshots: list[Dict[str, Any]] = []
        for path in sorted(self.root.glob("*/snapshot.json")):
            try:
                payload = read_json_locked(path, {}, RuntimeError)
                if isinstance(payload, dict):
                    snapshots.append(payload)
            except (OSError, RuntimeError):
                continue
        snapshots.sort(key=lambda item: str(item.get("last_active_at", "")), reverse=True)
        return snapshots

    def append_event(self, event: GatewayEvent) -> None:
        """Append one normalized protocol event to the session event log."""
        if not event.session_id:
            return
        event = event.model_copy(deep=True)
        event.data = mask_value(event.data)
        path = self._session_dir(event.session_id) / "events.jsonl"
        append_text_locked(path, event.model_dump_json() + "\n")

    def append_events(self, events: Iterable[GatewayEvent]) -> None:
        """Append multiple events."""
        for event in events:
            self.append_event(event)

    def read_events(self, session_id: str) -> list[Dict[str, Any]]:
        """Read normalized events for a session."""
        self.load_snapshot(session_id)
        path = self._session_dir(session_id) / "events.jsonl"
        if not path.exists():
            return []
        events = []
        for line in _read_text_locked(path).splitlines():
            if line.strip():
                events.append(json.loads(line))
        return events

    def read_transcript(self, session_id: str) -> list[Dict[str, Any]]:
        """Rebuild a compact transcript from persisted gateway events."""
        transcript: list[Dict[str, Any]] = []
        assistant_parts_by_turn: dict[str, list[str]] = {}
        for event in self.read_events(session_id):
            event_type = event.get("type")
            turn_id = str(event.get("turn_id") or "")
            data = event.get("data") or {}
            if event_type == "turn.started":
                transcript.append(
                    {
                        "role": "user",
                        "turn_id": turn_id,
                        "content": str(data.get("input", "")),
                        "timestamp": event.get("timestamp"),
                    }
                )
            elif event_type == "item.delta":
                assistant_parts_by_turn.setdefault(turn_id, []).append(str(data.get("text", "")))
            elif event_type == "turn.completed":
                content = "".join(assistant_parts_by_turn.pop(turn_id, []))
                if not content:
                    message = data.get("message") or {}
                    blocks = message.get("content") if isinstance(message, dict) else None
                    if isinstance(blocks, list):
                        content = "".join(
                            str(block.get("text", ""))
                            for block in blocks
                            if isinstance(block, dict) and block.get("type") == "text"
                        )
                transcript.append(
                    {
                        "role": "assistant",
                        "turn_id": turn_id,
                        "content": content,
                        "timestamp": event.get("timestamp"),
                    }
                )
            elif event_type in {"turn.failed", "turn.interrupted"}:
                transcript.append(
                    {
                        "role": "system",
                        "turn_id": turn_id,
                        "content": str(data.get("message", event_type)),
                        "timestamp": event.get("timestamp"),
                    }
                )
        return transcript

    def _session_dir(self, session_id: str) -> Path:
        if not _SESSION_ID_RE.fullmatch(str(session_id)):
            raise ValueError(f"Invalid session_id: {session_id}")
        path = (self.root / str(session_id)).resolve()
        if path != self.root and self.root not in path.parents:
            raise ValueError(f"Invalid session path for session_id: {session_id}")
        return path


def _read_text_locked(path: Path) -> str:
    with file_lock(path):
        return path.read_text(encoding="utf-8")

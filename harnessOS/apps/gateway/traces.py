"""Trace and audit records for gateway-visible operations."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Optional, Union

from apps.gateway.persistence import append_text_locked, file_lock
from apps.gateway.protocol import GatewayEvent, new_id
from apps.gateway.secrets import mask_text, mask_value


class TraceError(RuntimeError):
    """Raised when trace persistence or lookup fails."""


class TraceStore:
    """Filesystem-backed trace store used by Gateway service and runtime."""

    def __init__(self, root: Optional[Union[str, Path]] = None) -> None:
        default_root = Path(__file__).resolve().parents[2] / ".harnessos" / "traces"
        self.root = Path(root or default_root).expanduser().resolve()
        self.index_path = self.root / "index.jsonl"

    def new_trace_id(self) -> str:
        """Create a trace id."""
        return new_id("trace")

    def record_event(self, event: GatewayEvent) -> dict[str, Any]:
        """Record one normalized gateway event as a trace/audit record."""
        event = event.model_copy(deep=True)
        event.data = mask_value(event.data)
        data = event.data or {}
        trace_id = str(data.get("trace_id") or self.new_trace_id())
        record = self._base_record(
            trace_id=trace_id,
            session_id=event.session_id,
            turn_id=event.turn_id,
            app_id=event.app_id,
            project_id=event.project_id,
            workspace_id=event.workspace_id,
            event_type=event.type,
            status=_status_from_event_type(event.type),
            metadata={
                "event": event.model_dump(mode="json"),
            },
        )
        record["workflow_id"] = data.get("workflow_id")
        record["artifact_ids"] = _artifact_ids_from_payload(data)
        record["approval_ids"] = _approval_ids_from_payload(data)
        if event.type == "turn.started":
            record["input_summary"] = _summarize_text(str(data.get("input", "")))
        elif event.type in {"item.delta", "turn.completed", "turn.failed", "turn.interrupted"}:
            record["input_summary"] = _summarize_text(_event_text(data))
        self.append_record(record)
        return record

    def record_artifact_operation(
        self,
        *,
        operation: str,
        artifact: dict[str, Any],
        trace_id: Optional[str] = None,
        session_id: Optional[str] = None,
        turn_id: Optional[str] = None,
        status: str = "success",
        metadata: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        """Record an artifact register/get/read/list operation."""
        resolved_trace_id = trace_id or str((artifact.get("metadata") or {}).get("trace_id") or self.new_trace_id())
        artifact_id = artifact.get("artifact_id")
        record = self._base_record(
            trace_id=resolved_trace_id,
            session_id=session_id or artifact.get("session_id"),
            turn_id=turn_id or artifact.get("turn_id"),
            app_id=artifact.get("app_id"),
            project_id=artifact.get("project_id"),
            workspace_id=artifact.get("workspace_id"),
            event_type=f"artifact.{operation}",
            status=status,
            metadata=mask_value(metadata or {}),
        )
        record["artifact_ids"] = [artifact_id] if artifact_id else []
        record["input_summary"] = _summarize_text(str(artifact.get("name") or artifact.get("path") or operation))
        self.append_record(record)
        return record

    def record_approval_operation(
        self,
        *,
        operation: str,
        approval: dict[str, Any],
        status: Optional[str] = None,
        metadata: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        """Record an approval lifecycle operation."""
        approval_id = approval.get("approval_id")
        trace_id = str(approval.get("trace_id") or self.new_trace_id())
        record = self._base_record(
            trace_id=trace_id,
            session_id=approval.get("session_id"),
            turn_id=approval.get("turn_id"),
            app_id=approval.get("app_id"),
            project_id=approval.get("project_id"),
            workspace_id=approval.get("workspace_id"),
            event_type=f"approval.{operation}",
            status=status or str(approval.get("status") or operation),
            metadata=mask_value(metadata or {}),
        )
        record["approval_ids"] = [approval_id] if approval_id else []
        record["input_summary"] = _summarize_text(
            str(approval.get("request_summary") or approval.get("action") or operation)
        )
        self.append_record(record)
        return record

    def append_record(self, record: dict[str, Any]) -> None:
        """Append one trace record."""
        append_text_locked(
            self.index_path,
            json.dumps(record, ensure_ascii=False, separators=(",", ":")) + "\n",
        )

    def list_records(
        self,
        *,
        trace_id: Optional[str] = None,
        session_id: Optional[str] = None,
        turn_id: Optional[str] = None,
        artifact_id: Optional[str] = None,
        event_type: Optional[str] = None,
        app_id: Optional[str] = None,
        project_id: Optional[str] = None,
        workspace_id: Optional[str] = None,
    ) -> list[dict[str, Any]]:
        """List trace records, optionally filtered."""
        records = self._load_records()
        if trace_id is not None:
            records = [record for record in records if record.get("trace_id") == trace_id]
        if session_id is not None:
            records = [record for record in records if record.get("session_id") == session_id]
        if turn_id is not None:
            records = [record for record in records if record.get("turn_id") == turn_id]
        if artifact_id is not None:
            records = [record for record in records if artifact_id in (record.get("artifact_ids") or [])]
        if event_type is not None:
            records = [record for record in records if record.get("event_type") == event_type]
        if app_id is not None:
            records = [record for record in records if record.get("app_id") == app_id]
        if project_id is not None:
            records = [record for record in records if record.get("project_id") == project_id]
        if workspace_id is not None:
            records = [record for record in records if record.get("workspace_id") == workspace_id]
        return records

    def get_trace(self, trace_id: str) -> dict[str, Any]:
        """Return all records for one trace id."""
        records = self.list_records(trace_id=trace_id)
        if not records:
            raise KeyError(f"Trace not found: {trace_id}")
        return {
            "trace_id": trace_id,
            "records": records,
            "count": len(records),
        }

    def _base_record(
        self,
        *,
        trace_id: str,
        session_id: Optional[str],
        turn_id: Optional[str],
        app_id: Optional[str],
        project_id: Optional[str],
        workspace_id: Optional[str],
        event_type: str,
        status: str,
        metadata: dict[str, Any],
    ) -> dict[str, Any]:
        return {
            "trace_id": trace_id,
            "session_id": session_id,
            "turn_id": turn_id,
            "app_id": app_id,
            "project_id": project_id,
            "workspace_id": workspace_id,
            "event_type": event_type,
            "workflow_id": None,
            "artifact_ids": [],
            "approval_ids": [],
            "status": status,
            "input_summary": "",
            "created_at": datetime.now().isoformat(),
            "metadata": mask_value(metadata),
        }

    def _load_records(self) -> list[dict[str, Any]]:
        if not self.index_path.exists():
            return []
        records: list[dict[str, Any]] = []
        with file_lock(self.index_path):
            text = self.index_path.read_text(encoding="utf-8")
        for line in text.splitlines():
            if not line.strip():
                continue
            try:
                payload = json.loads(line)
            except json.JSONDecodeError as exc:
                raise TraceError(f"Trace index is not valid JSONL: {self.index_path}") from exc
            if isinstance(payload, dict):
                records.append(payload)
        return records


def _status_from_event_type(event_type: str) -> str:
    if event_type.endswith(".failed") or event_type == "turn.failed":
        return "failed"
    if event_type.endswith(".interrupted") or event_type == "turn.interrupted":
        return "interrupted"
    if event_type.endswith(".completed") or event_type == "turn.completed":
        return "success"
    return "running"


def _artifact_ids_from_payload(data: dict[str, Any]) -> list[str]:
    ids: list[str] = []
    artifacts = data.get("artifacts") or (data.get("meeting") or {}).get("artifacts")
    if isinstance(artifacts, dict):
        for value in artifacts.values():
            if isinstance(value, dict) and isinstance(value.get("artifact_id"), str):
                ids.append(value["artifact_id"])
    artifact_records = data.get("artifact_records") or (data.get("meeting") or {}).get("artifact_records")
    if isinstance(artifact_records, dict):
        for value in artifact_records.values():
            if isinstance(value, dict) and isinstance(value.get("artifact_id"), str):
                ids.append(value["artifact_id"])
    return sorted(set(ids))


def _approval_ids_from_payload(data: dict[str, Any]) -> list[str]:
    approval_id = data.get("approval_id")
    if isinstance(approval_id, str):
        return [approval_id]
    approval = data.get("approval")
    if isinstance(approval, dict) and isinstance(approval.get("approval_id"), str):
        return [approval["approval_id"]]
    approvals = data.get("approval_ids")
    if isinstance(approvals, list):
        return [item for item in approvals if isinstance(item, str)]
    return []


def _event_text(data: dict[str, Any]) -> str:
    if isinstance(data.get("text"), str):
        return data["text"]
    if isinstance(data.get("message"), str):
        return data["message"]
    message = data.get("message")
    if isinstance(message, dict):
        blocks = message.get("content")
        if isinstance(blocks, list):
            return "".join(
                str(block.get("text", ""))
                for block in blocks
                if isinstance(block, dict) and block.get("type") == "text"
            )
    return ""


def _summarize_text(text: str, limit: int = 240) -> str:
    compact = " ".join(mask_text(text or "").split())
    if len(compact) <= limit:
        return compact
    return compact[: limit - 3].rstrip() + "..."

"""Retry context persistence for gateway turns."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Optional, Union

from apps.gateway.persistence import atomic_write_text, read_json_locked, update_json_list_locked
from apps.gateway.protocol import new_id
from apps.gateway.secrets import mask_text, mask_value


RETRY_PENDING_APPROVAL = "pending_approval"
RETRY_RETRYING = "retrying"
RETRY_RETRIED = "retried"


class RetryError(RuntimeError):
    """Raised when retry context persistence or state transitions fail."""


class RetryStore:
    """Filesystem-backed retry context store."""

    def __init__(self, root: Optional[Union[str, Path]] = None) -> None:
        default_root = Path(__file__).resolve().parents[2] / ".harnessos" / "retries"
        self.root = Path(root or default_root).expanduser().resolve()
        self.index_path = self.root / "index.json"

    def create_policy_context(
        self,
        *,
        session_id: str,
        turn_id: str,
        user_input: str,
        domain: Optional[str],
        trace_id: str,
        approval_id: str,
        app_id: Optional[str] = None,
        project_id: Optional[str] = None,
        workspace_id: Optional[str] = None,
        policy: dict[str, Any],
    ) -> dict[str, Any]:
        """Save the original turn that was blocked by policy approval."""
        record = {
            "retry_id": new_id("retry"),
            "source_turn_id": turn_id,
            "session_id": session_id,
            "input": mask_text(user_input),
            "domain": domain,
            "trace_id": trace_id,
            "approval_id": approval_id,
            "app_id": app_id,
            "project_id": project_id,
            "workspace_id": workspace_id,
            "status": RETRY_PENDING_APPROVAL,
            "workflow_id": None,
            "failure_message": None,
            "artifact_ids": [],
            "policy": mask_value(policy),
            "created_at": datetime.now().isoformat(),
            "retried_at": None,
            "retry_turn_id": None,
            "retry_trace_id": None,
        }
        return update_json_list_locked(
            self.index_path,
            lambda records: _append_record(records, record),
            RetryError,
        )

    def get_by_turn(self, session_id: str, source_turn_id: str) -> dict[str, Any]:
        """Return a retry context by source turn id."""
        for record in self._load_records():
            if record.get("session_id") == session_id and record.get("source_turn_id") == source_turn_id:
                return record
        raise KeyError(f"Retry context not found for turn_id: {source_turn_id}")

    def get_by_approval(self, approval_id: str) -> dict[str, Any]:
        """Return a retry context by approval id."""
        for record in self._load_records():
            if record.get("approval_id") == approval_id:
                return record
        raise KeyError(f"Retry context not found for approval_id: {approval_id}")

    def mark_retried(
        self,
        retry_id: str,
        *,
        retry_turn_id: str,
        retry_trace_id: Optional[str],
    ) -> dict[str, Any]:
        """Mark one retry context as consumed."""
        def update(records: list[dict[str, Any]]) -> dict[str, Any]:
            for index, record in enumerate(records):
                if record.get("retry_id") != retry_id:
                    continue
                if record.get("status") == RETRY_RETRIED:
                    raise RetryError(f"Retry context already retried: {retry_id}")
                updated = dict(record)
                updated["status"] = RETRY_RETRIED
                updated["retried_at"] = datetime.now().isoformat()
                updated["retry_turn_id"] = retry_turn_id
                updated["retry_trace_id"] = retry_trace_id
                records[index] = updated
                return updated
            raise KeyError(f"Retry context not found: {retry_id}")

        return update_json_list_locked(self.index_path, update, RetryError)

    def mark_retrying(self, retry_id: str) -> dict[str, Any]:
        """Atomically reserve one retry context before executing side effects."""
        def update(records: list[dict[str, Any]]) -> dict[str, Any]:
            for index, record in enumerate(records):
                if record.get("retry_id") != retry_id:
                    continue
                if record.get("status") != RETRY_PENDING_APPROVAL:
                    raise RetryError(f"Retry context is not pending: {retry_id}")
                updated = dict(record)
                updated["status"] = RETRY_RETRYING
                updated["retrying_at"] = datetime.now().isoformat()
                records[index] = updated
                return updated
            raise KeyError(f"Retry context not found: {retry_id}")

        return update_json_list_locked(self.index_path, update, RetryError)

    def _load_records(self) -> list[dict[str, Any]]:
        if not self.index_path.exists():
            return []
        payload = read_json_locked(self.index_path, [], RetryError)
        if not isinstance(payload, list):
            raise RetryError(f"Retry index must be a list: {self.index_path}")
        return [record for record in payload if isinstance(record, dict)]

    def _save_records(self, records: list[dict[str, Any]]) -> None:
        self.index_path.parent.mkdir(parents=True, exist_ok=True)
        atomic_write_text(
            self.index_path,
            json.dumps(records, ensure_ascii=False, indent=2) + "\n",
        )


def _append_record(records: list[dict[str, Any]], record: dict[str, Any]) -> dict[str, Any]:
    records.append(record)
    return record

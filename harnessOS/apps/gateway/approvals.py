"""Approval request lifecycle for gateway governance."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Optional, Union

from apps.gateway.persistence import atomic_write_text, read_json_locked, update_json_list_locked
from apps.gateway.protocol import new_id
from apps.gateway.secrets import mask_text, mask_value


APPROVAL_PENDING = "pending"
APPROVAL_APPROVED = "approved"
APPROVAL_REJECTED = "rejected"
APPROVAL_EXPIRED = "expired"
APPROVAL_STATUSES = {APPROVAL_PENDING, APPROVAL_APPROVED, APPROVAL_REJECTED, APPROVAL_EXPIRED}


class ApprovalError(RuntimeError):
    """Raised when approval persistence or state transitions fail."""


class ApprovalConflictError(ApprovalError):
    """Raised when a decision conflicts with an existing approval decision."""

    def __init__(self, message: str, *, current_status: Optional[str] = None) -> None:
        super().__init__(message)
        self.current_status = current_status


class ApprovalStore:
    """Filesystem-backed approval request store."""

    def __init__(self, root: Optional[Union[str, Path]] = None) -> None:
        default_root = Path(__file__).resolve().parents[2] / ".harnessos" / "approvals"
        self.root = Path(root or default_root).expanduser().resolve()
        self.index_path = self.root / "index.json"

    def request(
        self,
        *,
        action: str,
        request_summary: str,
        trace_id: Optional[str] = None,
        session_id: Optional[str] = None,
        turn_id: Optional[str] = None,
        app_id: Optional[str] = None,
        project_id: Optional[str] = None,
        workspace_id: Optional[str] = None,
        risk_level: str = "medium",
        metadata: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        """Create a pending approval request."""
        record = {
            "approval_id": new_id("appr"),
            "trace_id": trace_id,
            "session_id": session_id,
            "turn_id": turn_id,
            "app_id": app_id,
            "project_id": project_id,
            "workspace_id": workspace_id,
            "risk_level": risk_level,
            "action": action,
            "status": APPROVAL_PENDING,
            "request_summary": mask_text(request_summary),
            "decision_reason": None,
            "created_at": datetime.now().isoformat(),
            "decided_at": None,
            "metadata": mask_value(metadata or {}),
        }
        return update_json_list_locked(
            self.index_path,
            lambda records: _append_record(records, record),
            ApprovalError,
        )

    def list_approvals(
        self,
        *,
        status: Optional[str] = None,
        session_id: Optional[str] = None,
        trace_id: Optional[str] = None,
        app_id: Optional[str] = None,
        project_id: Optional[str] = None,
        workspace_id: Optional[str] = None,
    ) -> list[dict[str, Any]]:
        """List approval records, optionally filtered."""
        records = self._load_records()
        if status is not None:
            if status not in APPROVAL_STATUSES:
                raise ApprovalError(f"Unsupported approval status: {status}")
            records = [record for record in records if record.get("status") == status]
        if session_id is not None:
            records = [record for record in records if record.get("session_id") == session_id]
        if trace_id is not None:
            records = [record for record in records if record.get("trace_id") == trace_id]
        if app_id is not None:
            records = [record for record in records if record.get("app_id") == app_id]
        if project_id is not None:
            records = [record for record in records if record.get("project_id") == project_id]
        if workspace_id is not None:
            records = [record for record in records if record.get("workspace_id") == workspace_id]
        return records

    def get_approval(self, approval_id: str) -> dict[str, Any]:
        """Return one approval record."""
        for record in self._load_records():
            if record.get("approval_id") == approval_id:
                return record
        raise KeyError(f"Approval not found: {approval_id}")

    def approve(self, approval_id: str, *, reason: Optional[str] = None) -> dict[str, Any]:
        """Approve a pending approval."""
        return self._decide(approval_id, status=APPROVAL_APPROVED, reason=reason)

    def reject(self, approval_id: str, *, reason: Optional[str] = None) -> dict[str, Any]:
        """Reject a pending approval."""
        return self._decide(approval_id, status=APPROVAL_REJECTED, reason=reason)

    def respond(self, approval_id: str, *, status: str, reason: Optional[str] = None) -> tuple[dict[str, Any], bool]:
        """Apply an idempotent approval decision."""
        if status not in {APPROVAL_APPROVED, APPROVAL_REJECTED}:
            raise ApprovalError(f"Unsupported approval decision status: {status}")

        def decide(records: list[dict[str, Any]]) -> tuple[dict[str, Any], bool]:
            for index, record in enumerate(records):
                if record.get("approval_id") != approval_id:
                    continue
                current_status = record.get("status")
                if current_status == status:
                    return dict(record), True
                if current_status != APPROVAL_PENDING:
                    raise ApprovalConflictError(
                        f"Approval {approval_id} is already decided: current status is {current_status}",
                        current_status=current_status if isinstance(current_status, str) else None,
                    )
                decided = dict(record)
                decided["status"] = status
                decided["decision_reason"] = mask_text(reason) if reason is not None else None
                decided["decided_at"] = datetime.now().isoformat()
                records[index] = decided
                return decided, False
            raise KeyError(f"Approval not found: {approval_id}")

        return update_json_list_locked(self.index_path, decide, ApprovalError)

    def begin_workflow_side_effect(self, approval_id: str) -> tuple[dict[str, Any], str]:
        """Atomically reserve workflow approval side-effect execution.

        Returns a marker state:
        - reserved: caller owns side-effect execution
        - applied: side effect already completed
        - applying: another caller is applying it
        - inactive: workflow binding is inactive
        """

        def reserve(records: list[dict[str, Any]]) -> tuple[dict[str, Any], str]:
            for index, record in enumerate(records):
                if record.get("approval_id") != approval_id:
                    continue
                metadata = dict(record.get("metadata") or {})
                binding = dict(metadata.get("workflow_binding") or {})
                if not binding:
                    return dict(record), "none"
                if binding.get("active") is False:
                    return dict(record), "inactive"
                current = str(binding.get("workflow_side_effect_status") or "pending")
                if current == "applied":
                    return dict(record), "applied"
                if current == "applying":
                    return dict(record), "applying"
                if current not in {"pending", "failed"}:
                    current = "pending"
                binding["workflow_side_effect_status"] = "applying"
                binding["workflow_side_effect_error"] = None
                metadata["workflow_binding"] = mask_value(binding)
                updated = dict(record)
                updated["metadata"] = mask_value(metadata)
                records[index] = updated
                return updated, "reserved"
            raise KeyError(f"Approval not found: {approval_id}")

        return update_json_list_locked(self.index_path, reserve, ApprovalError)

    def mark_workflow_side_effect(
        self,
        approval_id: str,
        *,
        status: str,
        error: Optional[str] = None,
    ) -> dict[str, Any]:
        """Update a workflow approval side-effect marker."""
        if status not in {"pending", "applying", "applied", "failed"}:
            raise ApprovalError(f"Unsupported workflow side-effect status: {status}")

        def mark(records: list[dict[str, Any]]) -> dict[str, Any]:
            for index, record in enumerate(records):
                if record.get("approval_id") != approval_id:
                    continue
                metadata = dict(record.get("metadata") or {})
                binding = dict(metadata.get("workflow_binding") or {})
                if not binding:
                    return dict(record)
                binding["workflow_side_effect_status"] = status
                binding["workflow_side_effect_error"] = mask_text(error) if error else None
                metadata["workflow_binding"] = mask_value(binding)
                updated = dict(record)
                updated["metadata"] = mask_value(metadata)
                records[index] = updated
                return updated
            raise KeyError(f"Approval not found: {approval_id}")

        return update_json_list_locked(self.index_path, mark, ApprovalError)

    def update_workflow_binding(self, approval_id: str, updates: dict[str, Any]) -> dict[str, Any]:
        """Merge workflow binding metadata updates for one approval."""

        def update(records: list[dict[str, Any]]) -> dict[str, Any]:
            for index, record in enumerate(records):
                if record.get("approval_id") != approval_id:
                    continue
                metadata = dict(record.get("metadata") or {})
                binding = dict(metadata.get("workflow_binding") or {})
                binding.update(updates)
                metadata["workflow_binding"] = mask_value(binding)
                updated = dict(record)
                updated["metadata"] = mask_value(metadata)
                records[index] = updated
                return updated
            raise KeyError(f"Approval not found: {approval_id}")

        return update_json_list_locked(self.index_path, update, ApprovalError)

    def deactivate_workflow_binding(self, approval_id: str, *, reason: str) -> dict[str, Any]:
        """Mark a workflow-bound approval inactive without deciding it."""
        return self.update_workflow_binding(
            approval_id,
            {
                "active": False,
                "inactive_reason": mask_text(reason),
            },
        )

    def _decide(self, approval_id: str, *, status: str, reason: Optional[str]) -> dict[str, Any]:
        def decide(records: list[dict[str, Any]]) -> dict[str, Any]:
            for index, record in enumerate(records):
                if record.get("approval_id") != approval_id:
                    continue
                current_status = record.get("status")
                if current_status != APPROVAL_PENDING:
                    raise ApprovalError(
                        f"Approval {approval_id} is not pending: current status is {current_status}"
                    )
                decided = dict(record)
                decided["status"] = status
                decided["decision_reason"] = mask_text(reason) if reason is not None else None
                decided["decided_at"] = datetime.now().isoformat()
                records[index] = decided
                return decided
            raise KeyError(f"Approval not found: {approval_id}")

        return update_json_list_locked(self.index_path, decide, ApprovalError)

    def _load_records(self) -> list[dict[str, Any]]:
        if not self.index_path.exists():
            return []
        payload = read_json_locked(self.index_path, [], ApprovalError)
        if not isinstance(payload, list):
            raise ApprovalError(f"Approval index must be a list: {self.index_path}")
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

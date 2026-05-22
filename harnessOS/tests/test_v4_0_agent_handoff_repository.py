"""V4.0-L Agent handoff repository tests."""

from __future__ import annotations

import pytest

from apps.api.agent_handoff_store import InMemoryAgentHandoffStore
from core.protocol.schemas.errors import ProtocolError


def _handoff(handoff_id: str = "aah_repo") -> dict:
    return {
        "handoff_id": handoff_id,
        "agent_session_id": "ats_repo",
        "proposal_id": "aap_repo",
        "workflow_instance_id": "wfi_repo",
        "workflow_template_id": "wf_repo",
        "target_panel": "editing_panel",
        "target_resource": {"workflow_patch_id": "wfp_repo"},
        "suggested_form_prefill": {},
        "expires_at": "2099-01-01T00:00:00+00:00",
        "status": "active",
        "created_at": "2026-05-21T00:00:00+00:00",
        "created_by": "agent",
        "redaction_status": "redacted",
    }


def test_repository_methods_and_lifecycle_transitions() -> None:
    store = InMemoryAgentHandoffStore()
    created = store.create(_handoff())
    assert created["status"] == "active"
    assert store.get("aah_repo")["handoff_id"] == "aah_repo"
    assert len(store.list(agent_session_id="ats_repo", workflow_instance_id="wfi_repo")) == 1

    opened = store.mark_opened("aah_repo")
    assert opened["status"] == "opened"
    assert store.mark_opened("aah_repo")["status"] == "opened"

    used = store.mark_used("aah_repo")
    assert used["status"] == "used_for_user_confirmed_action"
    with pytest.raises(ProtocolError):
        store.mark_opened("aah_repo")


def test_repeated_dismiss_is_idempotent_and_terminal_cannot_reopen() -> None:
    store = InMemoryAgentHandoffStore()
    store.create(_handoff("aah_dismiss"))
    assert store.dismiss("aah_dismiss")["status"] == "dismissed"
    assert store.dismiss("aah_dismiss")["status"] == "dismissed"
    with pytest.raises(ProtocolError):
        store.mark_used("aah_dismiss")


def test_expire_stale_blocked_and_audit_are_append_only() -> None:
    store = InMemoryAgentHandoffStore()
    store.create(_handoff("aah_expire"))
    assert store.expire("aah_expire", reason="test_expired")["status"] == "expired"
    store.append_audit("aah_expire", "handoff_expired", summary="expired", data={"token": "secret-token-value"})
    audit = store.list_audit("aah_expire")
    assert audit[0]["event_type"] == "handoff_expired"
    assert "token" not in audit[0]["data"]

    store.create(_handoff("aah_stale"))
    assert store.mark_stale("aah_stale", reason="draft_revision_changed")["status"] == "stale"

    store.create(_handoff("aah_blocked"))
    assert store.mark_blocked("aah_blocked", reason="patch_requires_approval")["status"] == "blocked"

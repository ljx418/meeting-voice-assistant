from __future__ import annotations

import pytest

from core.product_console.thin_web_console import ThinWebConsoleError, build_manual_confirmation
from tests.v5_6_console_support import make_context, make_target


def test_manual_confirmation_records_user_confirmed_handoff() -> None:
    context = make_context()
    record = build_manual_confirmation(
        context,
        operation="context.update",
        source="user",
        user_confirmed=True,
        target=make_target(context),
    )
    data = record.to_dict()
    assert data["user_confirmed"] is True
    assert data["policy_decision"] == "allow"
    assert data["target_refs"]["workflow_instance_id"] == "workflow_instance_v5_6"


def test_manual_confirmation_requires_user_confirmed_for_durable_mutation() -> None:
    context = make_context()
    with pytest.raises(ThinWebConsoleError) as exc:
        build_manual_confirmation(
            context,
            operation="context.update",
            source="user",
            user_confirmed=False,
            target=make_target(context),
        )
    assert exc.value.code == "USER_CONFIRMATION_REQUIRED"


def test_agent_source_cannot_record_durable_mutation_confirmation() -> None:
    context = make_context(actor_type="agent", actor_id="agent_v5_6")
    with pytest.raises(ThinWebConsoleError) as exc:
        build_manual_confirmation(
            context,
            operation="context.update",
            source="agent",
            user_confirmed=True,
            target=make_target(context),
        )
    assert exc.value.code == "AGENT_EXECUTION_DENIED"

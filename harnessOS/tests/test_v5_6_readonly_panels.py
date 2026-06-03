from __future__ import annotations

import pytest

from core.product_console.thin_web_console import ConsolePanel, ThinWebConsoleError, validate_thin_web_console_state
from tests.v5_6_console_support import make_state


def test_readonly_panels_do_not_expose_execution_actions() -> None:
    state = make_state()
    for panel in state.panels:
        assert "run" not in panel.allowed_actions
        assert "execute" not in panel.allowed_actions
        assert "apply" not in panel.allowed_actions
        assert "publish" not in panel.allowed_actions


def test_readonly_panel_with_execution_action_is_rejected() -> None:
    state = make_state()
    bad_panels = list(state.panels)
    bad_panels[0] = ConsolePanel(
        panel_id="runtime_report",
        title="运行报告",
        readonly=True,
        allowed_actions=("view", "execute"),
        source_refs={},
        data={},
    )
    bad_state = state.__class__(
        console_id=state.console_id,
        tenant_context=state.tenant_context,
        navigation_items=state.navigation_items,
        panels=tuple(bad_panels),
        manual_confirmation=state.manual_confirmation,
        global_assertions=state.global_assertions,
        source_refs=state.source_refs,
    )
    with pytest.raises(ThinWebConsoleError) as exc:
        validate_thin_web_console_state(bad_state)
    assert exc.value.code == "THIN_CONSOLE_ACTION_DENIED"


from __future__ import annotations

import pytest

from core.product_console.thin_web_console import ThinWebConsoleError, build_thin_web_console_state, render_console_html
from tests.v5_6_console_support import make_context, make_state


def test_rendered_html_has_no_direct_internal_routes_or_false_execution_copy() -> None:
    html = render_console_html(make_state())
    assert "/v1/rpc" not in html
    assert "/v1/events/subscribe" not in html
    for forbidden in ("自动应用", "自动发布", "Agent 已执行", "Agent 已发布"):
        assert forbidden not in html
    assert "<button" not in html


def test_state_rejects_browser_internal_route_exposure() -> None:
    context = make_context()
    state = make_state()
    with pytest.raises(ThinWebConsoleError) as exc:
        build_thin_web_console_state(
            context,
            runtime_result={"workflow_instance_id": "wf", "status": "completed"},
            evidence_chain={},
            audit_export={"browser_allowed_path": "/v1/rpc"},
            external_apps=[],
            manual_confirmation=state.manual_confirmation,
            source_refs={"runtime_result": "runtime", "evidence_chain": "evidence"},
        )
    assert exc.value.code == "THIN_CONSOLE_BROWSER_ROUTE_DENIED"


from __future__ import annotations

from tests.v5_6_console_support import make_state


def test_thin_web_console_state_uses_tenant_context_and_readonly_panels() -> None:
    state = make_state()
    data = state.to_dict()
    assert data["tenant_context"]["tenant_id"] == "tenant_v5"
    assert data["readonly"] is True
    assert {panel["panel_id"] for panel in data["panels"]} == {
        "runtime_report",
        "evidence_review",
        "audit_export",
        "external_app_admin",
    }
    assert all(panel["readonly"] is True for panel in data["panels"])


def test_thin_web_console_state_preserves_source_refs() -> None:
    data = make_state().to_dict()
    assert data["source_refs"]["runtime_result"] == "runtime-result.json"
    assert data["source_refs"]["evidence_chain"] == "evidence.json"


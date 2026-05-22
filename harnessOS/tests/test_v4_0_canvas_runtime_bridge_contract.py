"""V4.0-H canvas bridge contract/source guard tests."""

from __future__ import annotations

from pathlib import Path


APP_ROOT = Path("apps/workflow-console")


def test_canvas_bridge_frontend_uses_bff_proposal_route_only() -> None:
    client = (APP_ROOT / "src" / "api" / "workflowConsoleClient.ts").read_text(encoding="utf-8")
    assert "/workflows/${encodeURIComponent(templateId)}/patches`" in client
    assert "/patches/propose" not in client
    assert "/v1/rpc" not in client
    assert "/v1/events/subscribe" not in client


def test_canvas_bridge_intents_do_not_include_layout_fields_in_payload_builders() -> None:
    source = (APP_ROOT / "src" / "api" / "canvasPatchIntents.ts").read_text(encoding="utf-8")
    for forbidden in (" x:", " y:", "position", "zoom", "selection", "viewport", "panelCollapsed"):
        assert forbidden not in source
    assert "NodeAddIntent" in source
    assert "EdgeAddIntent" in source
    assert "InspectorUpdateIntent" in source


def test_canvas_bridge_does_not_expose_direct_mutation_or_agent_apply() -> None:
    source = "\n".join(path.read_text(encoding="utf-8") for path in (APP_ROOT / "src").rglob("*.tsx"))
    assert "WorkflowStore" not in source
    assert "ArtifactRegistry" not in source
    assert "ApprovalStore" not in source
    assert "source: \"agent\"" not in source
    assert "workflow.patch.apply" not in source
    assert "workflow.template.publish" not in source

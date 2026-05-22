"""V4.0-C Workflow Studio shell patch proposal contract tests."""

from __future__ import annotations

from pathlib import Path


APP_ROOT = Path("apps/workflow-console")


def _source_text() -> str:
    parts: list[str] = []
    for path in APP_ROOT.rglob("*"):
        if any(part in path.parts for part in {"node_modules", "dist", "dist-test", "__tests__"}):
            continue
        if path.suffix in {".ts", ".tsx", ".css", ".json"}:
            parts.append(path.read_text(encoding="utf-8", errors="ignore"))
    return "\n".join(parts)


def test_editing_panel_exists_and_uses_bff_patch_routes() -> None:
    client = (APP_ROOT / "src" / "api" / "workflowConsoleClient.ts").read_text(encoding="utf-8")
    panel = (APP_ROOT / "src" / "components" / "WorkflowEditingPanel.tsx").read_text(encoding="utf-8")

    for route in (
        "/patches`",
        "/diff",
    ):
        assert route in client
    for governed_route in ("/apply", "/reject", "/publish"):
        assert governed_route in client
    assert "/v1/rpc" not in client
    assert "/v1/events/subscribe" not in client
    assert "工作流编辑" in panel
    assert "查看 Diff" in panel
    assert "等待用户确认" in panel
    assert "应用到草稿" in panel
    assert "拒绝变更" in panel
    assert "发布新版本" in panel


def test_high_risk_patch_is_displayed_but_not_silently_applied() -> None:
    text = _source_text()
    assert "requires_approval" in text
    assert "需要治理审批" in text
    assert "等待治理确认" in text
    assert "disabled" in (APP_ROOT / "src" / "components" / "WorkflowEditingPanel.tsx").read_text(encoding="utf-8")


def test_editing_source_does_not_mutate_published_version_or_bypass_governance() -> None:
    text = _source_text()
    forbidden = (
        "WorkflowVersion.snapshot",
        "published_snapshot",
        "scope_mode=all",
        "approval.approve(",
        "approval.reject(",
        "/approval.approve",
        "/approval.reject",
        "WorkflowStore",
        "ArtifactRegistry",
        "ApprovalStore",
        "fetch('/v1/rpc'",
        'fetch("/v1/rpc"',
        "new EventSource('/v1/events/subscribe'",
        'new EventSource("/v1/events/subscribe"',
    )
    for snippet in forbidden:
        assert snippet not in text

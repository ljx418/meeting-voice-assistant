"""V4.0-A Workflow Console read-only contract tests."""

from __future__ import annotations

from pathlib import Path


APP_ROOT = Path("apps/workflow-console")


def _read_all_source() -> str:
    if not APP_ROOT.exists():
        return ""
    parts: list[str] = []
    for path in APP_ROOT.rglob("*"):
        if any(part in path.parts for part in {"node_modules", "dist", "dist-test", "__tests__"}):
            continue
        if path.suffix in {".ts", ".tsx", ".js", ".jsx", ".css", ".json"}:
            parts.append(path.read_text(encoding="utf-8", errors="ignore"))
    return "\n".join(parts)


def test_workflow_console_app_scaffold_exists() -> None:
    assert (APP_ROOT / "package.json").exists()
    assert (APP_ROOT / "src" / "App.tsx").exists()
    assert (APP_ROOT / "src" / "api" / "workflowConsoleClient.ts").exists()
    assert (APP_ROOT / "src" / "components" / "StationBoard.tsx").exists()


def test_workflow_console_client_uses_structured_bff_routes() -> None:
    text = (APP_ROOT / "src" / "api" / "workflowConsoleClient.ts").read_text(encoding="utf-8")
    for route in (
        "/workflows",
        "/instances",
        "/status",
        "/board",
        "/outputs",
        "/metadata",
        "/lineage",
        "/events/subscribe",
    ):
        assert route in text
    assert "/v1/rpc" not in text
    assert "/v1/events/subscribe" not in text


def test_workflow_console_source_uses_controlled_editing_boundary() -> None:
    text = _read_all_source()
    for forbidden in (
        'method: "workflow.instance.start"',
        'method: "approval.respond"',
        'method: "workflow.context.update"',
        'method: "business.event.emit"',
        'method: "quality.evaluation.create"',
        'method: "quality.evaluation.attach"',
        'method: "workflow.template.publish"',
        'method: "workflow.draft.save"',
        'method: "artifact.read"',
    ):
        assert forbidden not in text
    assert "/patches" in text
    assert "/publish" in text


def test_workflow_console_redaction_components_exist() -> None:
    text = _read_all_source()
    assert "redactValue" in text
    assert "safeText" in text
    assert "raw_trace_payload" in text
    assert "raw_artifact_content" in text
    assert "EventFeed" in text
    assert "TraceSummaryPanel" in text
    assert "ArtifactSummaryPanel" in text

"""V4.0-C AgentTalkWindow preparation shell contract tests."""

from __future__ import annotations

from pathlib import Path


APP_ROOT = Path("apps/workflow-console")

SOURCE_SUFFIXES = {".ts", ".tsx", ".js", ".jsx"}
IGNORED_DIRS = {"node_modules", "dist", "dist-test", "__tests__", "e2e"}


def _source_text() -> str:
    parts: list[str] = []
    for path in APP_ROOT.rglob("*"):
        if not path.is_file() or path.suffix not in SOURCE_SUFFIXES:
            continue
        if any(part in IGNORED_DIRS for part in path.parts):
            continue
        parts.append(path.read_text(encoding="utf-8", errors="ignore"))
    return "\n".join(parts)


def test_agent_talk_shell_components_exist() -> None:
    for relative in (
        "src/components/AgentTalkShell.tsx",
        "src/components/AgentEventTimeline.tsx",
        "src/components/AgentPatchProposalCard.tsx",
        "src/components/AgentApprovalNotice.tsx",
        "src/components/AgentContextSummary.tsx",
        "src/api/agentTalkTypes.ts",
        "src/api/embedTypes.ts",
    ):
        assert (APP_ROOT / relative).exists()


def test_agent_talk_source_uses_bff_propose_diff_and_no_direct_core_paths() -> None:
    client = (APP_ROOT / "src" / "api" / "workflowConsoleClient.ts").read_text(encoding="utf-8")
    text = _source_text()
    assert "/workflows/" in client
    assert "/patches`" in client
    assert "/diff" in client
    for forbidden in (
        "/v1/rpc",
        "/v1/events/subscribe",
        "import core/",
        "apps.gateway",
        "WorkflowStore",
        "ArtifactRegistry",
        "ApprovalStore",
    ):
        assert forbidden not in text


def test_agent_talk_shell_has_no_mutation_actions_or_misleading_copy() -> None:
    text = _source_text()
    for forbidden in (
        'method: "workflow.patch.apply"',
        'method: "workflow.patch.reject"',
        'method: "workflow.template.publish"',
        'method: "workflow.instance.start"',
        'method: "workflow.context.update"',
        'method: "business.event.emit"',
        'method: "quality.evaluation.create"',
        'method: "quality.evaluation.attach"',
        "approval.approve(",
        "approval.reject(",
        "/approval.approve",
        "/approval.reject",
        "自动应用",
        "自动发布",
        "已帮你修改并发布",
        "一键修改工作流",
    ):
        assert forbidden not in text

    patch_card = (APP_ROOT / "src" / "components" / "AgentPatchProposalCard.tsx").read_text(encoding="utf-8")
    for forbidden_label in ("Apply", "Reject", "Publish", "应用到草稿", "拒绝变更", "发布新版本"):
        assert forbidden_label not in patch_card
    assert "生成建议" in patch_card
    assert "查看 Diff" in patch_card


def test_agent_talk_allowed_actions_are_non_mutating() -> None:
    text = (APP_ROOT / "src" / "api" / "agentTalkTypes.ts").read_text(encoding="utf-8")
    for allowed in (
        "explain_workflow",
        "summarize_events",
        "show_patch_diff",
        "show_approval_notice",
        "show_context_summary",
    ):
        assert allowed in text
    for forbidden in (
        "apply_patch",
        "publish_version",
        "respond_approval",
        "update_context",
        "emit_business_event",
        "start_workflow",
    ):
        assert forbidden not in text


def test_agent_talk_context_and_event_boundary() -> None:
    context = (APP_ROOT / "src" / "components" / "AgentContextSummary.tsx").read_text(encoding="utf-8")
    timeline = (APP_ROOT / "src" / "components" / "AgentEventTimeline.tsx").read_text(encoding="utf-8")
    data = (APP_ROOT / "src" / "api" / "demoData.ts").read_text(encoding="utf-8")
    assert "context.business" in context
    assert "context.system" not in context
    assert "context.runtime" not in context
    assert "event.source" in timeline
    assert 'source: "demo"' in data
    assert 'source: "trace_only"' in data
    assert "quality.evaluated" in data
    assert "not_runtime_e2e: true" in data


def test_agent_talk_embed_boundary() -> None:
    text = (APP_ROOT / "src" / "api" / "embedTypes.ts").read_text(encoding="utf-8")
    assert "bff_eventsource_url" in text
    without_bff_field = text.replace("bff_eventsource_url", "")
    for forbidden in (
        "eventsource_url:",
        "capability_token",
        "subscription_token",
        "Authorization",
        "secret",
    ):
        assert forbidden not in without_bff_field

"""V4.0-P AgentTalk interaction claim guard tests."""

from __future__ import annotations

from pathlib import Path


ALLOWED_P_CLAIM = "V4.0-P complete: AgentTalkWindow interaction E2E baseline ready for dev/local Workflow Console validation."
FORBIDDEN_P_CLAIMS = {
    "complete AgentTalkWindow ready",
    "Agent executor ready",
    "controlled executor ready",
    "autonomous workflow editing ready",
    "complete Workflow Studio ready",
    "production-ready external app support",
    "full low-code canvas editing ready",
}
FORBIDDEN_UI_COPY = {
    "自动应用",
    "自动发布",
    "已帮你修改并发布",
    "Agent 已执行",
    "Agent 已发布",
}


def test_v4_0_p_allowed_claim_is_documented() -> None:
    plan = Path("docs/design/V4.0/v4_0_p_agenttalk_window_interaction_e2e_plan.md").read_text(encoding="utf-8")
    assert ALLOWED_P_CLAIM in plan


def test_agenttalk_forbidden_claims_and_misleading_copy_are_guarded() -> None:
    for path in [*Path("docs/design/V4.0").glob("*.md"), *Path("apps/workflow-console/src").rglob("*.*")]:
        text = path.read_text(encoding="utf-8")
        relative = path.as_posix()
        for claim in FORBIDDEN_P_CLAIMS:
            if claim not in text:
                continue
            assert "不能声明" in text or "禁止" in text or "Forbidden" in text or "No False Green" in text, (
                f"{claim!r} appears outside explicit forbidden/non-goal context in {relative}"
            )
        for copy in FORBIDDEN_UI_COPY:
            if copy not in text:
                continue
            assert (
                "禁止" in text
                or "FORBIDDEN" in text
                or "forbidden" in text
                or "No forbidden copy" in text
                or "must not show" in text
                or "不显示" in text
                or "不出现" in text
                or "误导文案" in text
            ), (
                f"{copy!r} appears outside a forbidden-copy guard in {relative}"
            )

from __future__ import annotations

from pathlib import Path


FORBIDDEN_CLAIMS = [
    "production-ready external app support",
    "enterprise auth ready",
    "multi-tenant control plane ready",
    "Agent executor ready",
    "controlled executor ready",
    "production controlled executor ready",
    "complete Workflow Studio ready",
    "complete AgentTalkWindow ready",
    "full multi-Agent orchestration ready",
    "distributed multi-Agent runtime ready",
    "autonomous workflow editing ready",
    "生产级Agent执行器已完成",
    "生产级受控执行器已完成",
]

SAFE_CONTEXT = (
    "Forbidden",
    "No False Green",
    "forbidden",
    "禁止",
    "不得",
    "不能",
    "不证明",
    "不声明",
    "not ",
    "not_",
    "no ",
    "No-Go",
    "Stop",
    "Claim Guard",
    "仍禁止",
    "仍然禁止",
    "Non Goals",
    "不能被",
    "不得把",
    "不应",
    "avoid",
    "cannot",
)


def test_v5_docs_do_not_claim_v5_3_production_readiness() -> None:
    docs = Path("docs/design/V5.x")
    violations: list[str] = []
    for path in docs.glob("*.md"):
        lines = path.read_text(encoding="utf-8").splitlines()
        for line_no, line in enumerate(lines, start=1):
            context = "\n".join(lines[max(0, line_no - 20) : min(len(lines), line_no + 2)])
            for claim in FORBIDDEN_CLAIMS:
                if claim in line and not any(marker in context for marker in SAFE_CONTEXT):
                    violations.append(f"{path}:{line_no}: {claim}")

    assert violations == []


def test_ready_for_review_is_not_collapsed_to_ready_in_v5_3_docs() -> None:
    docs = [
        Path("docs/design/V5.x/v5_3_observability_audit_export_prd.md"),
        Path("docs/design/V5.x/v5_3_planning_audit_for_chatgpt.md"),
        Path("docs/design/V5.x/v5_3_test_matrix.md"),
    ]
    text = "\n".join(path.read_text(encoding="utf-8") for path in docs)

    assert "V5-3 complete: production audit export ready" not in text
    assert "V5-3 complete: observability platform ready" not in text
    assert "V5-3 complete: production observability ready" not in text

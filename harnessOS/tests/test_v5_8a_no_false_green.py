from __future__ import annotations

from pathlib import Path


FORBIDDEN = [
    "distributed multi-Agent runtime ready",
    "full multi-Agent orchestration ready",
    "Agent executor ready",
    "production controlled executor ready",
    "production-ready external app support",
    "complete Workflow Studio ready",
    "autonomous workflow editing ready",
]

SAFE_CONTEXT = (
    "Forbidden",
    "No False Green",
    "forbidden",
    "禁止",
    "不得",
    "不能",
    "does not prove",
    "not ",
    "not_",
    "Stop",
)


def test_v5_8a_docs_do_not_claim_forbidden_completion() -> None:
    docs = [
        Path("docs/design/V5.x/v5_8_entry_gate_plan.md"),
        Path("docs/design/V5.x/v5_8_pre_implementation_audit.md"),
        Path("docs/design/V5.x/v5_8_development_and_acceptance_plan.md"),
        Path("docs/design/V5.x/v5_8_no_false_green_guard.md"),
    ]
    violations: list[str] = []
    for path in docs:
        lines = path.read_text(encoding="utf-8").splitlines()
        for line_no, line in enumerate(lines, start=1):
            context = "\n".join(lines[max(0, line_no - 12) : min(len(lines), line_no + 2)])
            for claim in FORBIDDEN:
                if claim in line and not any(marker in context for marker in SAFE_CONTEXT):
                    violations.append(f"{path}:{line_no}:{claim}")

    assert violations == []


def test_v5_8a_keeps_runtime_implementation_not_started() -> None:
    text = Path("docs/design/V5.x/v5_8_pre_implementation_audit.md").read_text(encoding="utf-8")

    assert "V5-8E final acceptance package: PASS." in text
    assert "NO-GO for complete V5-8 distributed multi-Agent runtime completion claim." in text
    assert "Complete full multi-Agent orchestration remains not complete." in text

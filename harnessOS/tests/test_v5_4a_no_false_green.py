from __future__ import annotations

from pathlib import Path


FORBIDDEN_COMPLETION = [
    "V5-4A complete: Agent executor ready",
    "V5-4A complete: controlled executor ready",
]


def test_v5_4a_docs_do_not_claim_executor_readiness() -> None:
    docs = Path("docs/design/V5.x")
    violations: list[str] = []
    for path in docs.glob("v5_4a*.md"):
        text = path.read_text(encoding="utf-8")
        for claim in FORBIDDEN_COMPLETION:
            if claim in text:
                violations.append(f"{path}: {claim}")
        lines = text.splitlines()
        for line_no, line in enumerate(lines, start=1):
            context = "\n".join(lines[max(0, line_no - 6) : min(len(lines), line_no + 2)])
            if "Agent executor ready" in line and not any(marker in context for marker in ("不得", "不证明", "does not prove", "not ", "No False Green", "Forbidden Claims")):
                violations.append(f"{path}:{line_no}: Agent executor ready")

    assert violations == []


def test_v5_4a_allowed_claim_is_safety_gate_only() -> None:
    guard = Path("docs/design/V5.x/v5_4a_no_false_green_guard.md").read_text(encoding="utf-8")

    assert "V5-4A planning complete: Agent executor safety gate implementation plan ready for review." in guard
    assert "Agent executor ready" in guard
    assert "No False Green" in guard

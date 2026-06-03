from __future__ import annotations

from pathlib import Path


def test_v5_4c_docs_do_not_claim_ready_executor_capabilities() -> None:
    violations: list[str] = []
    forbidden = [
        "V5-4C complete: controlled executor" + " ready",
        "V5-4C complete: Agent executor" + " ready",
        "V5-4C complete: production controlled executor" + " ready",
        "V5-4C complete: autonomous workflow editing" + " ready",
    ]
    for path in Path("docs/design/V5.x").glob("v5_4c*.md"):
        text = path.read_text(encoding="utf-8")
        for claim in forbidden:
            if claim in text:
                violations.append(f"{path}: {claim}")

    assert violations == []

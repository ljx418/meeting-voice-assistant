from __future__ import annotations

import json
from pathlib import Path

from core.product_console.v8_station_agent_workflow import terminal_worker_blocked_payload


def test_terminal_worker_remains_blocked_without_human_high_risk_decision() -> None:
    payload = terminal_worker_blocked_payload()

    assert payload["current_decision"] == "NO_GO_FOR_RUNTIME_IMPLEMENTATION"
    assert "controlled_terminal_worker_runtime" in payload["blocked_work"]
    assert "human high-risk proceed decision recorded" in payload["required_before_implementation"]


def test_v8_terminal_worker_contract_does_not_claim_executor_ready() -> None:
    text = Path("docs/design/V8.x/v8_terminal_worker_high_risk_contract.md").read_text(encoding="utf-8")
    lowered = text.lower()

    assert "does not make any of them an unrestricted agent executor" in lowered
    assert "no apply / commit / push / publish without human_authorization_ref" in lowered
    assert "production automation ready" not in lowered.split("## 1. Scope")[0]


def test_v8_no_false_green_guard_contains_terminal_forbidden_claims() -> None:
    text = Path("docs/design/V8.x/v8_no_false_green_claim_guard.md").read_text(encoding="utf-8")

    assert "unrestricted terminal worker ready" in text
    assert "ChromeCLI production automation ready" in text
    assert "Codex终端执行器已生产可用" in text
    assert "Claude终端执行器已生产可用" in text

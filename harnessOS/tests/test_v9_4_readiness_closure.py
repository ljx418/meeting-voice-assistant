from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from tools.v9.generate_v9_4_readiness_closure import build_readiness_closure


V9_ROOT = Path("docs/design/V9.x")
EVIDENCE_ROOT = V9_ROOT / "evidence" / "v9-4-readiness-closure"


def test_v9_4_readiness_closure_is_no_go_for_runtime_implementation() -> None:
    data = build_readiness_closure()

    assert data["status"] == "PASS"
    assert data["current_decision"] == "NO_GO_FOR_RUNTIME_IMPLEMENTATION"
    assert data["v9_4_runtime_implementation_allowed"] is False
    assert data["human_high_risk_proceed_decision_recorded"] is False
    assert "runtime_implementation" in data["blocked_work"]
    assert "git_commit" in data["blocked_work"]
    assert "git_push" in data["blocked_work"]
    assert "production_deploy" in data["blocked_work"]
    assert data["entry_baseline"]["v9_3_status"] == "PASS"


def test_v9_4_fixtures_enforce_proposal_only_and_denials() -> None:
    data = build_readiness_closure()
    results = data["fixture_results"]

    assert all(item["status"] == "PASS" for item in results)
    operations = {item.get("operation") for item in results}
    assert "git.commit" in operations
    assert "git.push" in operations
    assert "production.deploy" in operations
    assert "patch.apply" in operations
    assert "approval.resolve" in operations


def test_v9_4_readiness_generator_writes_human_review_page() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "tools.v9.generate_v9_4_readiness_closure"],
        check=False,
        text=True,
        capture_output=True,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    data = json.loads((EVIDENCE_ROOT / "pre-implementation-data.json").read_text(encoding="utf-8"))
    html = (EVIDENCE_ROOT / "index.html").read_text(encoding="utf-8")

    assert data["status"] == "PASS"
    assert data["current_decision"] == "NO_GO_FOR_RUNTIME_IMPLEMENTATION"
    assert data["v9_4_runtime_implementation_allowed"] is False
    assert "human high-risk proceed decision 尚未记录" in html
    assert "执行器启动按钮" not in html
    assert "开始实现按钮" not in html

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


V9_ROOT = Path("docs/design/V9.x")
EVIDENCE_ROOT = V9_ROOT / "evidence" / "v9-2-controlled-executor-runtime"


def test_v9_2_runtime_evidence_generator_proves_limited_runtime_slice() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "tools.v9.generate_v9_2_runtime_evidence"],
        check=False,
        text=True,
        capture_output=True,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    data = json.loads((EVIDENCE_ROOT / "acceptance-data.json").read_text(encoding="utf-8"))

    assert data["status"] == "PASS"
    assert data["evidence_scope"] == "real_runtime_fixture"
    assert data["runtime_backed"] is True
    assert data["fallback_demo_only"] is False
    assert data["transcript_only"] is False
    assert data["report_only"] is False
    assert data["v9_2_runtime_implementation_allowed"] is True
    assert data["runtime_executor_route_created"] is False
    assert data["runtime_worker_created"] is False
    assert data["source_agent_durable_mutation_allowed"] is False
    assert data["agent_executor_ready"] is False
    assert data["controlled_executor_ready"] is False
    assert data["production_controlled_executor_ready"] is False
    assert set(data["allowed_operations"]) == {
        "workflow.instance.start",
        "station.rerun",
        "artifact.write",
        "quality.evaluation.create",
    }
    assert all(item["status"] == "PASS" for item in data["scenarios"])
    assert all(item["status"] == "PASS" for item in data["checks"])
    assert any(item["scenario_id"] == "source_agent_durable_mutation_denied" for item in data["scenarios"])
    assert any(item["scenario_id"] == "excluded_operations_hard_denied" for item in data["scenarios"])
    assert any(item["scenario_id"] == "redaction_forbidden_content_denied" for item in data["scenarios"])


def test_v9_2_runtime_acceptance_html_is_static_and_boundary_clear() -> None:
    html = (EVIDENCE_ROOT / "index.html").read_text(encoding="utf-8")

    assert "runtime_backed: true" in html
    assert "没有新增 route、worker" in html
    assert "source=agent durable mutation" in html
    assert "执行器启动按钮" not in html
    assert "开始实现按钮" not in html

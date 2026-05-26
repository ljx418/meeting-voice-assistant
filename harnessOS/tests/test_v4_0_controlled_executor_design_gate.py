"""V4.0-Q controlled executor design gate no-implementation guard."""

from __future__ import annotations

import json
from pathlib import Path

from tests.v4_0_guard_utils import assert_no_forbidden_route_fragments


CONTRACT_PATH = Path("docs/design/V4.0/v4_0_q_controlled_executor_design_gate_contract.json")
PLAN_PATH = Path("docs/design/V4.0/v4_0_q_controlled_executor_design_gate_plan.md")
COMPLETION_PATH = Path("docs/design/V4.0/v4_0_q_controlled_executor_design_gate_completion_note.md")


def _contract() -> dict:
    return json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))


def test_q_contract_is_design_gate_only() -> None:
    contract = _contract()
    assert contract["stage"] == "V4.0-Q"
    assert contract["runtime_enabled"] is False
    assert contract["callable_executor_routes_enabled"] is False
    assert contract["allowed_claim"] == "V4.0-Q complete: controlled executor design gate ready for review."


def test_q_does_not_add_executor_bff_or_frontend_routes() -> None:
    forbidden_route_fragments = {"/execute", "/run", "/agent/execute", "/kill-switch", "/rollback", "/admin-override"}
    assert_no_forbidden_route_fragments(forbidden_route_fragments)

    bff = "\n".join(path.read_text(encoding="utf-8") for path in Path("apps/api").rglob("*.py"))
    client = "\n".join(
        path.read_text(encoding="utf-8")
        for path in Path("apps/workflow-console/src").rglob("*.*")
        if "__tests__" not in path.parts and path.suffix in {".ts", ".tsx"}
    )
    combined = f"{bff}\n{client}"

    forbidden_runtime_markers = {
        "executor worker",
        "executor runtime service",
        '"connector.call"',
        '"external_llm.call"',
        "connector.call(",
        "external_llm.call(",
    }
    for marker in forbidden_runtime_markers:
        assert marker not in combined


def test_q_plan_and_completion_note_preserve_no_false_green_boundary() -> None:
    plan = PLAN_PATH.read_text(encoding="utf-8")
    completion = COMPLETION_PATH.read_text(encoding="utf-8")
    assert "不实现 controlled executor" in plan
    assert "No executor route, worker, runtime service" in completion
    assert "V4.0-Q complete: controlled executor design gate ready for review." in completion

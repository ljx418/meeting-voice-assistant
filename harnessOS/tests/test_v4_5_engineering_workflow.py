"""V4.5 long-running engineering workflow tests."""

from __future__ import annotations

import json
from pathlib import Path

from fastapi.testclient import TestClient

from apps.api import create_app
from core.workflows.v4_5_engineering_workflow import STAGES, assert_no_forbidden_text, build_engineering_spec, run_engineering_workflow, validate_engineering_spec
from scripts.v4_5_engineering_workflow_evidence import DEFAULT_OUTPUT_DIR, FORBIDDEN_TERMS, generate_engineering_workflow_evidence
from v4_0_reference_support import SCOPE_QUERY, build_gateway


TASK_PATH = Path("tests/fixtures/v4_5/engineering_task/product_task.md")


def _client(monkeypatch, tmp_path) -> TestClient:
    monkeypatch.setenv("HARNESS_V3_5_DEV_MODE", "1")
    return TestClient(create_app(gateway_service=build_gateway(tmp_path)))


def test_engineering_spec_has_required_stage_order_and_governance() -> None:
    spec = build_engineering_spec()

    validate_engineering_spec(spec)
    assert [stage["stage_id"] for stage in spec["stages"]] == [stage[0] for stage in STAGES]
    assert spec["governance"]["source_agent_can_mutate"] is False
    assert spec["governance"]["real_code_modification"] is False
    assert_no_forbidden_text(spec)


def test_engineering_runner_uses_real_task_fixture_and_generates_artifacts() -> None:
    run = run_engineering_workflow(task_text=TASK_PATH.read_text(encoding="utf-8"), task_path=TASK_PATH.as_posix(), scope={"app_id": "reference_app"})

    assert run["status"] == "completed"
    assert run["backed_by"] == "v4_5_engineering_workflow_runtime"
    assert len(run["nodes"]) == 11
    assert len(run["artifacts"]) == 11
    assert run["quality_report"]["status"] == "passed"
    assert run["agent_mutation_allowed"] is False
    assert_no_forbidden_text(run)


def test_engineering_bff_requires_confirmation_and_blocks_agent(monkeypatch, tmp_path) -> None:
    client = _client(monkeypatch, tmp_path)

    denied = client.post(f"/bff/v4_5/runtime/workflows/engineering/start{SCOPE_QUERY}", json={"task_path": TASK_PATH.as_posix(), "source": "run_panel"}).json()
    assert denied["error"]["code"] == "METHOD_FORBIDDEN"

    agent_denied = client.post(
        f"/bff/v4_5/runtime/workflows/engineering/start{SCOPE_QUERY}",
        json={"task_path": TASK_PATH.as_posix(), "user_confirmed": True, "source": "agent"},
    ).json()
    assert agent_denied["error"]["code"] == "METHOD_FORBIDDEN"

    started = client.post(
        f"/bff/v4_5/runtime/workflows/engineering/start{SCOPE_QUERY}",
        json={"task_path": TASK_PATH.as_posix(), "user_confirmed": True, "source": "run_panel"},
    ).json()
    assert started["status"] == "completed"
    assert started["agent_mutation_allowed"] is False


def test_engineering_rerun_marks_downstream_stale_and_preserves_attempts(monkeypatch, tmp_path) -> None:
    client = _client(monkeypatch, tmp_path)
    started = client.post(
        f"/bff/v4_5/runtime/workflows/engineering/start{SCOPE_QUERY}",
        json={"task_path": TASK_PATH.as_posix(), "user_confirmed": True, "source": "run_panel"},
    ).json()
    rerun = client.post(
        f"/bff/v4_5/runtime/instances/{started['workflow_instance_id']}/rerun-stage{SCOPE_QUERY}",
        json={"stage_id": "code_review", "user_confirmed": True, "source": "run_panel"},
    ).json()
    assert rerun["status"] == "waiting_user_confirmation"
    assert {item["stage_id"] for item in rerun["downstream_stale"]} == {"e2e_acceptance", "human_confirmation"}
    code_review = next(node for node in rerun["nodes"] if node["stage_id"] == "code_review")
    assert len(code_review["attempts"]) == 2

    continued = client.post(
        f"/bff/v4_5/runtime/instances/{started['workflow_instance_id']}/continue-downstream{SCOPE_QUERY}",
        json={"user_confirmed": True, "source": "run_panel"},
    ).json()
    assert continued["status"] == "completed"
    assert continued["downstream_stale"] == []

    evidence = client.get(f"/bff/v4_5/runtime/instances/{started['workflow_instance_id']}/evidence{SCOPE_QUERY}").json()
    assert {"workflow.instance.start", "station.rerun", "workflow.instance.continue_downstream"}.issubset(
        {item["operation"] for item in evidence}
    )
    assert all(item["source"] != "agent" for item in evidence)
    assert_no_forbidden_text({"rerun": rerun, "continued": continued, "evidence": evidence})


def test_engineering_evidence_package_can_be_rebuilt_and_is_complete(tmp_path) -> None:
    manifest = generate_engineering_workflow_evidence(tmp_path)

    assert manifest["status"] == "completed"
    assert "durable_task_board.html" in manifest["files"]
    required = {
        "tui-transcript.txt",
        "engineering_workflow.json",
        "engineering_workflow.yaml",
        "engineering_board.drawio",
        "engineering_status.drawio",
        "engineering_artifact_lineage.drawio",
        "durable_task_board.html",
        "stage_artifacts.html",
        "quality_gate_report.html",
        "evidence_chain.html",
        "rerun_history.html",
        "runtime-result.json",
        "attempt-history.json",
        "downstream-stale.json",
        "operation-evidence.json",
        "result-summary.md",
    }
    assert required.issubset({path.name for path in DEFAULT_OUTPUT_DIR.iterdir() if path.is_file()})


def test_engineering_evidence_package_is_read_only_and_redacted() -> None:
    combined = "\n".join(path.read_text(encoding="utf-8") for path in DEFAULT_OUTPUT_DIR.iterdir() if path.is_file())
    assert "<form" not in combined.lower()
    for term in FORBIDDEN_TERMS:
        assert term not in combined
    for forbidden_copy in ["自动应用", "自动发布", "Agent 已执行", "Agent 已发布"]:
        assert forbidden_copy not in combined


def test_engineering_bff_has_no_direct_v1_route_contract() -> None:
    from apps.api.routers import bff_v45

    text = json.dumps([route.path for route in bff_v45.router.routes])
    assert "/v1/rpc" not in text
    assert "/v1/events/subscribe" not in text
    assert "/agent/execute" not in text


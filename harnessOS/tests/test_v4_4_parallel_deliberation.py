"""V4.4 parallel deliberation workflow tests."""

from __future__ import annotations

import json
from pathlib import Path

from fastapi.testclient import TestClient

from apps.api import create_app
from core.workflows.v4_4_parallel_deliberation import (
    PERSONAS,
    assert_no_forbidden_text,
    build_deliberation_spec,
    run_deliberation_workflow,
    validate_deliberation_spec,
)
from scripts.v4_4_parallel_deliberation_evidence import DEFAULT_OUTPUT_DIR, FORBIDDEN_TERMS, generate_parallel_deliberation_evidence
from v4_0_reference_support import SCOPE_QUERY, build_gateway


QUESTION_PATH = Path("tests/fixtures/v4_4/deliberation/project_question.md")


def _client(monkeypatch, tmp_path) -> TestClient:
    monkeypatch.setenv("HARNESS_V3_5_DEV_MODE", "1")
    return TestClient(create_app(gateway_service=build_gateway(tmp_path)))


def test_parallel_deliberation_spec_has_personas_and_inspiration_edges() -> None:
    spec = build_deliberation_spec()

    validate_deliberation_spec(spec)
    assert {persona["station_id"] for persona in PERSONAS}.issubset({station["station_id"] for station in spec["stations"]})
    assert any("inspiration" in edge["edge_id"] for edge in spec["edges"])
    assert any(edge["to_station_id"] == "synthesis" for edge in spec["edges"])
    assert_no_forbidden_text(spec)


def test_parallel_deliberation_runner_uses_real_question_fixture() -> None:
    run = run_deliberation_workflow(
        question_text=QUESTION_PATH.read_text(encoding="utf-8"),
        question_path=QUESTION_PATH.as_posix(),
        scope={"app_id": "reference_app"},
    )

    assert run["status"] == "completed"
    assert run["backed_by"] == "v4_4_parallel_deliberation_runtime"
    assert len(run["nodes"]) == 6
    assert len(run["artifacts"]) == 6
    assert run["quality_report"]["status"] == "passed"
    assert "synthesis_with_attribution.md" in {artifact["name"] for artifact in run["artifacts"]}
    assert_no_forbidden_text(run)


def test_parallel_deliberation_bff_requires_confirmation_and_blocks_agent(monkeypatch, tmp_path) -> None:
    client = _client(monkeypatch, tmp_path)

    denied = client.post(
        f"/bff/v4_4/runtime/workflows/parallel-deliberation/start{SCOPE_QUERY}",
        json={"question_path": QUESTION_PATH.as_posix(), "source": "run_panel"},
    ).json()
    assert denied["error"]["code"] == "METHOD_FORBIDDEN"

    agent_denied = client.post(
        f"/bff/v4_4/runtime/workflows/parallel-deliberation/start{SCOPE_QUERY}",
        json={"question_path": QUESTION_PATH.as_posix(), "user_confirmed": True, "source": "agent"},
    ).json()
    assert agent_denied["error"]["code"] == "METHOD_FORBIDDEN"

    started = client.post(
        f"/bff/v4_4/runtime/workflows/parallel-deliberation/start{SCOPE_QUERY}",
        json={"question_path": QUESTION_PATH.as_posix(), "user_confirmed": True, "source": "run_panel"},
    ).json()
    assert started["status"] == "completed"
    assert started["agent_mutation_allowed"] is False
    assert_no_forbidden_text(started)


def test_parallel_deliberation_rerun_marks_synthesis_stale(monkeypatch, tmp_path) -> None:
    client = _client(monkeypatch, tmp_path)
    started = client.post(
        f"/bff/v4_4/runtime/workflows/parallel-deliberation/start{SCOPE_QUERY}",
        json={"question_path": QUESTION_PATH.as_posix(), "user_confirmed": True, "source": "run_panel"},
    ).json()

    rerun = client.post(
        f"/bff/v4_4/runtime/instances/{started['workflow_instance_id']}/rerun-station{SCOPE_QUERY}",
        json={"station_id": "architecture_agent", "user_confirmed": True, "source": "run_panel"},
    ).json()
    assert rerun["status"] == "waiting_user_confirmation"
    assert {item["station_id"] for item in rerun["downstream_stale"]} == {"synthesis", "contradiction_review"}

    continued = client.post(
        f"/bff/v4_4/runtime/instances/{started['workflow_instance_id']}/continue-downstream{SCOPE_QUERY}",
        json={"user_confirmed": True, "source": "run_panel"},
    ).json()
    assert continued["status"] == "completed"
    assert continued["downstream_stale"] == []

    evidence = client.get(f"/bff/v4_4/runtime/instances/{started['workflow_instance_id']}/evidence{SCOPE_QUERY}").json()
    assert {"workflow.instance.start", "station.rerun", "workflow.instance.continue_downstream"}.issubset(
        {item["operation"] for item in evidence}
    )
    assert all(item["source"] != "agent" for item in evidence)
    assert_no_forbidden_text({"rerun": rerun, "continued": continued, "evidence": evidence})


def test_parallel_deliberation_evidence_package_can_be_rebuilt(tmp_path) -> None:
    manifest = generate_parallel_deliberation_evidence(tmp_path)

    assert manifest["status"] == "completed"
    assert "deliberation_workflow.drawio" in manifest["files"]
    assert "deliberation_report.html" in manifest["files"]


def test_parallel_deliberation_evidence_package_outputs_are_complete_and_redacted() -> None:
    required = {
        "tui-transcript.txt",
        "deliberation_workflow.json",
        "deliberation_workflow.yaml",
        "deliberation_workflow.drawio",
        "deliberation_status.drawio",
        "deliberation_artifact_lineage.drawio",
        "deliberation_report.html",
        "persona_artifacts.html",
        "synthesis.html",
        "evidence.html",
        "runtime-result.json",
        "attempt-history.json",
        "downstream-stale.json",
        "operation-evidence.json",
        "result-summary.md",
    }
    assert required.issubset({path.name for path in DEFAULT_OUTPUT_DIR.iterdir() if path.is_file()})
    combined = "\n".join(path.read_text(encoding="utf-8") for path in DEFAULT_OUTPUT_DIR.iterdir() if path.is_file())
    for term in FORBIDDEN_TERMS:
        assert term not in combined
    for forbidden_copy in ["自动应用", "自动发布", "Agent 已执行", "Agent 已发布"]:
        assert forbidden_copy not in combined
    assert "<form" not in combined.lower()


def test_parallel_deliberation_bff_has_no_direct_v1_route_contract() -> None:
    from apps.api.routers import bff_v44

    text = json.dumps([route.path for route in bff_v44.router.routes])
    assert "/v1/rpc" not in text
    assert "/v1/events/subscribe" not in text
    assert "/agent/execute" not in text


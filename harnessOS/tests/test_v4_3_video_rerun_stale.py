"""V4.3 serial video rerun and stale propagation tests."""

from __future__ import annotations

import json

from fastapi.testclient import TestClient

from apps.api import create_app
from v4_0_reference_support import SCOPE_QUERY, assert_no_forbidden_text, build_gateway


BRIEF_PATH = "tests/fixtures/v4_3/video_brief/launch_brief.md"


def _client(monkeypatch, tmp_path) -> TestClient:
    monkeypatch.setenv("HARNESS_V3_5_DEV_MODE", "1")
    return TestClient(create_app(gateway_service=build_gateway(tmp_path)))


def _start(client: TestClient, *, simulate_failure_station: str | None = None, source: str = "run_panel") -> dict:
    payload = {"brief_path": BRIEF_PATH, "user_confirmed": True, "source": source}
    if simulate_failure_station:
        payload["simulate_failure_station"] = simulate_failure_station
    return client.post(f"/bff/v4_3/runtime/workflows/serial-video/start{SCOPE_QUERY}", json=payload).json()


def test_video_runtime_start_requires_confirmation_and_blocks_agent(monkeypatch, tmp_path) -> None:
    client = _client(monkeypatch, tmp_path)

    missing_confirmation = client.post(
        f"/bff/v4_3/runtime/workflows/serial-video/start{SCOPE_QUERY}",
        json={"brief_path": BRIEF_PATH, "source": "run_panel"},
    ).json()
    assert missing_confirmation["error"]["code"] == "METHOD_FORBIDDEN"

    agent_denied = client.post(
        f"/bff/v4_3/runtime/workflows/serial-video/start{SCOPE_QUERY}",
        json={"brief_path": BRIEF_PATH, "user_confirmed": True, "source": "agent"},
    ).json()
    assert agent_denied["error"]["code"] == "METHOD_FORBIDDEN"

    started = _start(client)
    assert started["status"] == "completed"
    assert started["backed_by"] == "v4_3_serial_video_runtime"
    assert started["user_confirmed_required"] is True
    assert started["agent_mutation_allowed"] is False
    assert len(started["nodes"]) == 6
    assert_no_forbidden_text(started)


def test_video_runtime_rerun_preserves_attempt_history_and_marks_downstream_stale(monkeypatch, tmp_path) -> None:
    client = _client(monkeypatch, tmp_path)
    failed = _start(client, simulate_failure_station="storyboard_agent")
    assert failed["status"] == "failed"

    agent_denied = client.post(
        f"/bff/v4_3/runtime/instances/{failed['workflow_instance_id']}/rerun-station{SCOPE_QUERY}",
        json={"station_id": "storyboard_agent", "user_confirmed": True, "source": "agent"},
    ).json()
    assert agent_denied["error"]["code"] == "METHOD_FORBIDDEN"

    rerun = client.post(
        f"/bff/v4_3/runtime/instances/{failed['workflow_instance_id']}/rerun-station{SCOPE_QUERY}",
        json={"station_id": "storyboard_agent", "user_confirmed": True, "source": "run_panel"},
    ).json()
    assert rerun["status"] == "waiting_user_confirmation"
    storyboard = next(node for node in rerun["nodes"] if node["station_id"] == "storyboard_agent")
    assert [attempt["status"] for attempt in storyboard["attempts"]] == ["failed", "completed"]
    assert {item["station_id"] for item in rerun["downstream_stale"]} == {
        "copywriting_agent",
        "editing_plan_agent",
        "quality_review_agent",
        "publish_preparation_agent",
    }

    history = client.get(f"/bff/v4_3/runtime/instances/{failed['workflow_instance_id']}/attempt-history{SCOPE_QUERY}").json()
    assert any(station["station_id"] == "storyboard_agent" and len(station["attempts"]) == 2 for station in history["stations"])

    continued = client.post(
        f"/bff/v4_3/runtime/instances/{failed['workflow_instance_id']}/continue-downstream{SCOPE_QUERY}",
        json={"user_confirmed": True, "source": "run_panel"},
    ).json()
    assert continued["status"] == "completed"
    assert continued["downstream_stale"] == []
    assert continued["quality_report"]["status"] == "passed"
    assert_no_forbidden_text({"rerun": rerun, "continued": continued, "history": history})


def test_video_runtime_evidence_records_real_user_confirmed_operations(monkeypatch, tmp_path) -> None:
    client = _client(monkeypatch, tmp_path)
    failed = _start(client, simulate_failure_station="storyboard_agent")
    client.post(
        f"/bff/v4_3/runtime/instances/{failed['workflow_instance_id']}/rerun-station{SCOPE_QUERY}",
        json={"station_id": "storyboard_agent", "user_confirmed": True, "source": "run_panel"},
    )
    client.post(
        f"/bff/v4_3/runtime/instances/{failed['workflow_instance_id']}/continue-downstream{SCOPE_QUERY}",
        json={"user_confirmed": True, "source": "run_panel"},
    )
    evidence = client.get(f"/bff/v4_3/runtime/instances/{failed['workflow_instance_id']}/evidence{SCOPE_QUERY}").json()

    assert {"workflow.instance.start", "station.rerun", "workflow.instance.continue_downstream"}.issubset(
        {item["operation"] for item in evidence}
    )
    assert all(item["user_confirmed"] is True for item in evidence)
    assert all(item["source"] != "agent" for item in evidence)
    assert all(item["runtime_result_ref"]["workflow_instance_id"] == failed["workflow_instance_id"] for item in evidence)
    assert_no_forbidden_text(evidence)


def test_video_runtime_bff_has_no_direct_v1_or_agent_execute_contract() -> None:
    from apps.api.routers import bff_v43

    text = json.dumps([route.path for route in bff_v43.router.routes])
    assert "/v1/rpc" not in text
    assert "/v1/events/subscribe" not in text
    assert "/agent/execute" not in text

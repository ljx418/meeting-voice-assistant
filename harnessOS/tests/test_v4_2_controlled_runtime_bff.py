"""V4.2-C controlled runtime BFF tests."""

from __future__ import annotations

import json

from fastapi.testclient import TestClient

from apps.api import create_app

from v4_0_reference_support import SCOPE_QUERY, assert_no_forbidden_text, build_gateway


def _client(monkeypatch, tmp_path) -> TestClient:
    monkeypatch.setenv("HARNESS_V3_5_DEV_MODE", "1")
    return TestClient(create_app(gateway_service=build_gateway(tmp_path)))


def _start(client: TestClient, *, folder_path: str = "Desktop/技术分享", source: str = "run_panel") -> dict:
    return client.post(
        f"/bff/v4_2/runtime/workflows/local-folder-summary/start{SCOPE_QUERY}",
        json={"folder_path": folder_path, "user_confirmed": True, "source": source},
    ).json()


def test_controlled_runtime_start_requires_user_confirmation_and_blocks_agent(monkeypatch, tmp_path) -> None:
    client = _client(monkeypatch, tmp_path)

    missing_confirmation = client.post(
        f"/bff/v4_2/runtime/workflows/local-folder-summary/start{SCOPE_QUERY}",
        json={"folder_path": "Desktop/技术分享", "source": "run_panel"},
    ).json()
    assert missing_confirmation["error"]["code"] == "METHOD_FORBIDDEN"

    agent_denied = client.post(
        f"/bff/v4_2/runtime/workflows/local-folder-summary/start{SCOPE_QUERY}",
        json={"folder_path": "Desktop/技术分享", "user_confirmed": True, "source": "agent"},
    ).json()
    assert agent_denied["error"]["code"] == "METHOD_FORBIDDEN"

    started = _start(client)
    assert started["status"] == "completed"
    assert started["backed_by"] == "generic_controlled_runtime"
    assert started["user_confirmed_required"] is True
    assert started["agent_mutation_allowed"] is False
    assert len(started["nodes"]) == 9
    assert {artifact["name"] for artifact in started["artifacts"]} == {
        "AgentOS_总结.md",
        "前端低代码_总结.md",
        "项目复盘_总结.md",
        "总览总结.md",
        "quality_report.json",
    }
    assert_no_forbidden_text(started)


def test_controlled_runtime_rerun_preserves_attempt_history_and_marks_downstream_stale(monkeypatch, tmp_path) -> None:
    client = _client(monkeypatch, tmp_path)
    failed = _start(client, folder_path="tests/fixtures/desktop/技术分享_损坏")
    assert failed["status"] == "failed"
    parse_node = next(node for node in failed["nodes"] if node["station_id"] == "markdown_parse")
    assert parse_node["status"] == "failed"
    assert "Markdown parse failed" in parse_node["error"]

    agent_denied = client.post(
        f"/bff/v4_2/runtime/instances/{failed['workflow_instance_id']}/rerun-station{SCOPE_QUERY}",
        json={"station_id": "markdown_parse", "user_confirmed": True, "source": "agent"},
    ).json()
    assert agent_denied["error"]["code"] == "METHOD_FORBIDDEN"

    rerun = client.post(
        f"/bff/v4_2/runtime/instances/{failed['workflow_instance_id']}/rerun-station{SCOPE_QUERY}",
        json={"station_id": "markdown_parse", "user_confirmed": True, "source": "run_panel"},
    ).json()
    assert rerun["status"] == "waiting_user_confirmation"
    rerun_parse_node = next(node for node in rerun["nodes"] if node["station_id"] == "markdown_parse")
    assert [attempt["status"] for attempt in rerun_parse_node["attempts"]] == ["failed", "completed"]
    assert "Markdown parse failed" in rerun_parse_node["attempts"][0]["error"]
    assert {item["station_id"] for item in rerun["downstream_stale"]} == {
        "folder_group",
        "per_folder_summary",
        "overview_summary",
        "quality_check",
        "artifact_publish",
    }

    history = client.get(f"/bff/v4_2/runtime/instances/{failed['workflow_instance_id']}/attempt-history{SCOPE_QUERY}").json()
    assert history["workflow_instance_id"] == failed["workflow_instance_id"]
    assert any(station["station_id"] == "markdown_parse" and len(station["attempts"]) == 2 for station in history["stations"])

    continued = client.post(
        f"/bff/v4_2/runtime/instances/{failed['workflow_instance_id']}/continue-downstream{SCOPE_QUERY}",
        json={"user_confirmed": True, "source": "run_panel"},
    ).json()
    assert continued["status"] == "completed"
    assert continued["downstream_stale"] == []
    assert continued["quality_report"]["status"] == "passed"
    assert_no_forbidden_text({"rerun": rerun, "continued": continued, "history": history})


def test_controlled_runtime_evidence_uses_real_operations_and_runtime_refs(monkeypatch, tmp_path) -> None:
    client = _client(monkeypatch, tmp_path)
    failed = _start(client, folder_path="tests/fixtures/desktop/技术分享_损坏")
    client.post(
        f"/bff/v4_2/runtime/instances/{failed['workflow_instance_id']}/rerun-station{SCOPE_QUERY}",
        json={"station_id": "markdown_parse", "user_confirmed": True, "source": "run_panel"},
    )
    client.post(
        f"/bff/v4_2/runtime/instances/{failed['workflow_instance_id']}/continue-downstream{SCOPE_QUERY}",
        json={"user_confirmed": True, "source": "run_panel"},
    )
    evidence = client.get(f"/bff/v4_2/runtime/instances/{failed['workflow_instance_id']}/evidence{SCOPE_QUERY}").json()

    operations = {item["operation"] for item in evidence}
    assert {"workflow.instance.start", "station.rerun", "workflow.instance.continue_downstream"}.issubset(operations)
    assert all(item["user_confirmed"] is True for item in evidence)
    assert all(item["source"] != "agent" for item in evidence)
    assert all(item["policy_decision"] == "user_confirmed_only" for item in evidence)
    assert all(item["runtime_result_ref"]["workflow_instance_id"] == failed["workflow_instance_id"] for item in evidence)
    assert any(item["timeout_baseline"]["enabled"] is True for item in evidence)
    assert any(item["kill_switch_baseline"]["enabled"] is True for item in evidence)
    assert_no_forbidden_text(evidence)


def test_controlled_runtime_bff_has_no_direct_browser_v1_route_contract() -> None:
    from apps.api.routers import bff_v42

    text = json.dumps([route.path for route in bff_v42.router.routes])
    assert "/v1/rpc" not in text
    assert "/v1/events/subscribe" not in text
    assert "/agent/execute" not in text

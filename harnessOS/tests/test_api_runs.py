from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from fastapi.testclient import TestClient

from apps.api import app, create_app
from apps.gateway.service import GatewayService


def test_create_run_endpoint_returns_gateway_result(monkeypatch):
    monkeypatch.setenv("DEEPSEEK_API_KEY", "")
    monkeypatch.setenv("MINIMAX_API_KEY", "")
    monkeypatch.setenv("OPENAI_API_KEY", "")
    monkeypatch.setenv("OPENHARNESS_API_KEY", "")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "")
    monkeypatch.setenv("HARNESS_V3_5_DEV_MODE", "1")

    client = TestClient(app)
    response = client.post(
        "/v1/runs",
        json={"input": "你好", "close_session": True},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["session_id"].startswith("sess_")
    assert payload["turn_id"].startswith("turn_")
    assert payload["events"][0]["type"] == "turn.started"
    assert "你好" in payload["final_text"]


def test_session_query_and_rpc_endpoints(monkeypatch):
    monkeypatch.setenv("DEEPSEEK_API_KEY", "")
    monkeypatch.setenv("MINIMAX_API_KEY", "")
    monkeypatch.setenv("OPENAI_API_KEY", "")
    monkeypatch.setenv("OPENHARNESS_API_KEY", "")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "")
    monkeypatch.setenv("HARNESS_V3_5_DEV_MODE", "1")

    client = TestClient(app)
    run_response = client.post(
        "/v1/runs",
        json={"input": "你好", "close_session": False},
    )
    assert run_response.status_code == 200
    session_id = run_response.json()["session_id"]

    sessions = client.get("/v1/sessions")
    assert sessions.status_code == 200
    assert any(item["session_id"] == session_id for item in sessions.json()["sessions"])

    session = client.get(f"/v1/sessions/{session_id}")
    assert session.status_code == 200
    assert session.json()["session"]["session_id"] == session_id

    transcript = client.get(f"/v1/sessions/{session_id}/transcript")
    assert transcript.status_code == 200
    roles = [item["role"] for item in transcript.json()["transcript"]]
    assert "user" in roles
    assert "assistant" in roles

    rpc = client.post(
        "/v1/rpc",
        json={"id": "req_1", "method": "health.ping", "params": {}},
    )
    assert rpc.status_code == 200
    assert rpc.json()["id"] == "req_1"
    assert rpc.json()["error"] is None


def test_create_app_accepts_injected_gateway_service(monkeypatch):
    monkeypatch.setenv("DEEPSEEK_API_KEY", "")
    monkeypatch.setenv("MINIMAX_API_KEY", "")
    monkeypatch.setenv("OPENAI_API_KEY", "")
    monkeypatch.setenv("OPENHARNESS_API_KEY", "")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "")
    monkeypatch.setenv("HARNESS_V3_5_DEV_MODE", "1")

    gateway = GatewayService()
    injected_app = create_app(gateway_service=gateway)
    assert injected_app.state.gateway_service is gateway

    client = TestClient(injected_app)
    run_response = client.post("/v1/runs", json={"input": "你好", "close_session": False})
    assert run_response.status_code == 200
    session_id = run_response.json()["session_id"]

    assert gateway.runtime_pool.read_session(session_id)["session_id"] == session_id

    rpc = client.post(
        "/v1/rpc",
        json={"id": "req_1", "method": "health.ping", "params": {}},
    )
    assert rpc.status_code == 200
    assert rpc.json()["result"]["active_sessions"] >= 1

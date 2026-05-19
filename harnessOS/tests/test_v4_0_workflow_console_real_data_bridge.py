"""V4.0-A2 real data bridge tests from V3.6 runtime to BFF DTOs."""

from __future__ import annotations

import asyncio
import json

from fastapi.testclient import TestClient

from apps.api import create_app

from tests.test_v4_0_workflow_console_bff_routes import SCOPE_QUERY, _gateway, _seed


def test_real_v3_6_dummy_pipeline_flows_through_bff_frontend_dtos(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("HARNESS_V3_5_DEV_MODE", "1")
    service = _gateway(tmp_path)
    seeded = asyncio.run(_seed(service, "v4_a2_real_bridge"))
    instance_id = seeded["instance"]["workflow_instance_id"]
    client = TestClient(create_app(gateway_service=service))

    status = client.get(f"/bff/instances/{instance_id}/status{SCOPE_QUERY}").json()
    board = client.get(f"/bff/instances/{instance_id}/board{SCOPE_QUERY}").json()
    first_run = board["stations"][0]["runs"][0]
    outputs = client.get(f"/bff/instances/{instance_id}/stations/{first_run['station_run_id']}/outputs{SCOPE_QUERY}").json()
    metadata = client.get(f"/bff/instances/{instance_id}/artifacts/{outputs[0]['artifact_id']}/metadata{SCOPE_QUERY}").json()
    lineage = client.get(f"/bff/instances/{instance_id}/artifacts/{outputs[0]['artifact_id']}/lineage{SCOPE_QUERY}").json()

    assert status["workflow_instance_id"] == instance_id
    assert status["station_counts"]["completed"] >= 1
    assert board["workflow_instance"]["workflow_instance_id"] == instance_id
    assert board["stations"][0]["station"]["station_id"] == "station_a"
    assert outputs[0]["artifact_id"] == metadata["artifact_id"]
    assert lineage["artifacts"]
    raw = json.dumps({"status": status, "board": board, "outputs": outputs, "metadata": metadata, "lineage": lineage}, ensure_ascii=False)
    assert "raw_artifact_content" not in raw
    assert "raw_trace_payload" not in raw
    assert "subscription_token" not in raw

"""V4.0-H canvas bridge redaction tests."""

from __future__ import annotations

import asyncio
import json

from fastapi.testclient import TestClient

from apps.api import create_app

from v4_0_reference_support import SCOPE_QUERY, assert_no_forbidden_text, build_gateway, seed_reference_console


def test_canvas_bridge_error_and_proposal_payloads_are_redacted(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("HARNESS_V3_5_DEV_MODE", "1")
    service = build_gateway(tmp_path)
    seeded = asyncio.run(seed_reference_console(service, template_id="v4_h_redaction"))
    client = TestClient(create_app(gateway_service=service))
    template_id = seeded["template"]["workflow_template_id"]

    denied = client.post(
        f"/bff/workflows/{template_id}/patches{SCOPE_QUERY}",
        json={
            "source": "canvas",
            "intent_type": "node_add",
            "operation": "add_station",
            "payload": {
                "station": {
                    "station_id": "station_secret",
                    "name": "Secret",
                    "metadata": {
                        "node_catalog_id": "character_consistency",
                        "raw_trace_payload": "secret-token-value",
                    },
                }
            },
        },
    ).json()
    assert denied["error"]["code"] == "WORKFLOW_PATCH_INVALID"

    proposed = client.post(
        f"/bff/workflows/{template_id}/patches{SCOPE_QUERY}",
        json={
            "source": "inspector",
            "intent_type": "inspector_update",
            "operation": "update_station_prompt",
            "workflow_instance_id": seeded["instance"]["workflow_instance_id"],
            "payload": {"station_id": "station_b", "prompt_patch": "只保留脱敏摘要"},
        },
    ).json()
    raw = json.dumps({"denied": denied, "proposed": proposed}, ensure_ascii=False)
    assert "secret-token-value" not in raw
    assert_no_forbidden_text({"denied": denied, "proposed": proposed})

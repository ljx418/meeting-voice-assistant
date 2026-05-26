"""V4.0-R secret and token hygiene preflight tests."""

from __future__ import annotations

import asyncio
import json
from pathlib import Path

from fastapi.testclient import TestClient

from apps.api import create_app

from v4_0_reference_support import OTHER_SCOPE_QUERY, SCOPE_QUERY, assert_no_forbidden_text, build_gateway, seed_reference_console


CONTRACT_PATH = Path("docs/design/V4.0/v4_0_r_production_readiness_preflight_contract.json")


def test_secret_hygiene_contract_covers_required_fields_and_surfaces() -> None:
    contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    assert set(contract["secret_hygiene_fields"]) >= {
        "capability_token",
        "subscription_token",
        "Authorization",
        "Bearer",
        "secret",
        "raw_trace_payload",
        "raw_artifact_content",
        "raw_connector_payload",
        "raw prompt",
        "upstream signed URL",
    }
    assert set(contract["secret_hygiene_surfaces"]) >= {
        "BFF DTO",
        "error response",
        "event payload",
        "frontend DOM / HTML",
        "audit summary",
    }


def test_bff_error_event_and_audit_summaries_remain_redacted(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("HARNESS_V3_5_DEV_MODE", "1")
    monkeypatch.setenv("HARNESS_CAPABILITY_TOKEN_SECRET", "v4-r-redaction")
    service = build_gateway(tmp_path)
    seeded = asyncio.run(seed_reference_console(service, template_id="v4_r_redaction"))
    client = TestClient(create_app(gateway_service=service))
    instance_id = seeded["instance"]["workflow_instance_id"]
    patch_id = seeded["patch"]["workflow_patch_id"]

    payload = {
        "board": client.get(f"/bff/instances/{instance_id}/board{SCOPE_QUERY}").json(),
        "context": client.get(f"/bff/instances/{instance_id}/context{SCOPE_QUERY}").json(),
        "diff": client.get(f"/bff/instances/{instance_id}/patches/{patch_id}/diff{SCOPE_QUERY}").json(),
        "event": client.get(f"/bff/events/subscribe{SCOPE_QUERY}&channels=business&workflow_instance_id={instance_id}").text,
        "audit": client.get(f"/bff/instances/{instance_id}/agent/governance-review{SCOPE_QUERY}").json(),
        "error": client.get(f"/bff/instances/{instance_id}/board{OTHER_SCOPE_QUERY}").json(),
    }
    assert_no_forbidden_text(payload)

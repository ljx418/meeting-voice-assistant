"""V4.0-R external app production boundary tests."""

from __future__ import annotations

import json
from pathlib import Path


CONTRACT_PATH = Path("docs/design/V4.0/v4_0_r_production_readiness_preflight_contract.json")
PLAN_PATH = Path("docs/design/V4.0/v4_0_r_production_readiness_preflight_plan.md")


def test_external_app_production_gaps_are_complete() -> None:
    contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    assert set(contract["external_app_production_gaps"]) >= {
        "app registration",
        "domain verification",
        "origin allowlist review",
        "tenant provisioning",
        "service account lifecycle",
        "token rotation / revocation",
        "SDK versioning policy",
        "API compatibility policy",
        "quota / rate limit",
        "abuse detection",
        "customer offboarding",
        "data export / deletion",
        "support runbook",
    }
    ext_gap = next(gap for gap in contract["production_gaps"] if gap["category"] == "external_app_onboarding")
    assert ext_gap["blocking_for_production"] is True
    assert ext_gap["status"] == "open_gap"


def test_v3_5_sdk_bff_embed_are_documented_as_dev_local_only() -> None:
    plan = PLAN_PATH.read_text(encoding="utf-8")
    assert "V3.5 SDK / BFF / Embed 仍是 dev/local baseline" in plan
    assert "不实现 production-ready external app support" in plan

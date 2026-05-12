"""V3.5-F Full BFF Template contract tests."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SDK_PATH = ROOT / "sdk/python"
if str(SDK_PATH) not in sys.path:
    sys.path.insert(0, str(SDK_PATH))

from templates.bff.fastapi.settings import load_settings


TEMPLATE = ROOT / "templates/bff/fastapi"
DOCS = ROOT / "docs/design/V3.5"


def test_config_examples_are_safe() -> None:
    config = json.loads((TEMPLATE / "config.example.json").read_text(encoding="utf-8"))
    env = (TEMPLATE / ".env.example").read_text(encoding="utf-8")
    serialized = json.dumps(config) + env
    assert "meeting" not in serialized
    assert "knowledge" not in serialized
    assert "sub-secret" not in serialized
    assert "cap-secret" not in serialized
    assert "<server-side-harnessos-capability-token>" in env
    assert config["demo_identity_mode"] is True


def test_wildcard_origin_with_credentials_is_invalid() -> None:
    with pytest.raises(Exception) as raised:
        load_settings(
            {
                "allowed_origins": ["*"],
                "allow_credentials": True,
                "demo_identity_mode": True,
                "harnessos_capability_token": "placeholder-token",
            }
        )
    assert "BFF_ALLOWED_ORIGINS" in str(raised.value)


def test_demo_mode_must_be_explicit_and_missing_token_is_not_usable() -> None:
    settings = load_settings({"harnessos_capability_token": None})
    assert settings.demo_identity_mode is False
    assert settings.config_error is not None
    assert "BFF_DEMO_IDENTITY_MODE" in settings.config_error
    assert "HARNESSOS_CAPABILITY_TOKEN" in settings.config_error


def test_fastapi_template_import_boundary() -> None:
    forbidden = (
        "from apps",
        "import apps",
        "from core",
        "import core",
        "GatewayService",
        "RuntimeAdapter",
        "Core Store",
        "fastapi_minimal",
        "/v1/runs/stream",
    )
    saw_harnessos_client = False
    for path in TEMPLATE.glob("*.py"):
        text = path.read_text(encoding="utf-8")
        assert not any(item in text for item in forbidden), path
        if "harnessos_client" in text:
            saw_harnessos_client = True
    assert saw_harnessos_client


def test_documents_mark_v3_5_f_as_complete() -> None:
    expected = "V3.5-F"
    for name in (
        "00_README.md",
        "v3_5_current_gap_analysis.md",
        "v3_5_acceptance_plan.md",
        "v3_5_event_bridge_plan.md",
        "v3_5_development_plan_application_adaptation_layer.md",
    ):
        text = (DOCS / name).read_text(encoding="utf-8")
        assert "V3.5-MVP complete" in text
        assert "V3.5-E1" in text
        assert "V3.5-E2" in text
        assert expected in text
    gap = (DOCS / "v3_5_current_gap_analysis.md").read_text(encoding="utf-8")
    assert "V3.5-F Full BFF Template complete" in gap
    assert "V3.5-I" in gap
    assert "V3.5 complete at dev/local Application Adaptation Layer level" in gap
    assert "production-ready external app support" in gap

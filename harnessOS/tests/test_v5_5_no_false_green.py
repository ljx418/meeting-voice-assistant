from __future__ import annotations

import json
from pathlib import Path

from core.apps.external_onboarding import ExternalAppOnboardingRegistry
from tests.v5_3_observability_support import make_context


def test_external_app_dtos_do_not_leak_secret_or_claim_production_ready() -> None:
    context = make_context()
    registry = ExternalAppOnboardingRegistry()
    registration = registry.register_app(
        context,
        app_registration_id="external_app_v5_5",
        display_name="Partner App",
        allowed_capabilities=["workflow.read"],
        source="user",
        user_confirmed=True,
    )
    dumped = json.dumps(registration.to_dict(), ensure_ascii=False)

    assert ("production-ready external app" + " support") not in dumped
    assert "Authorization" not in dumped
    assert "Bearer " not in dumped
    assert "capability_token" not in dumped
    assert "secret" not in dumped.lower()


def test_v5_5_docs_do_not_claim_production_ready_external_app_support() -> None:
    violations: list[str] = []
    for path in Path("docs/design/V5.x").glob("v5_5*.md"):
        text = path.read_text(encoding="utf-8")
        if ("V5-5 complete: production-ready external app" + " support") in text:
            violations.append(str(path))
    assert violations == []

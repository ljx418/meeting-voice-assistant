"""V3.5-H Embed Contract tests."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[1]
SDK_PATH = ROOT / "sdk/python"
if str(SDK_PATH) not in sys.path:
    sys.path.insert(0, str(SDK_PATH))

from harnessos_client import EventSubscription
from core.protocol.contracts.event_inventory import EVENT_INVENTORY
from core.protocol.schemas.events import EVENT_SCHEMAS
from templates.bff.fastapi.app import create_app


DEMO = ROOT / "examples" / "embed_contract_demo"
DOCS = ROOT / "docs" / "design" / "V3.5"


class FakeSdkClient:
    def __init__(self) -> None:
        self.calls: list[tuple[str, dict[str, Any]]] = []

    def session_start(self, *, model=None, scope=None):
        self.calls.append(("session_start", {"model": model, "scope": _scope(scope)}))
        return {"session_id": "sess_embed", "scope": _scope(scope)}

    def events_subscribe(self, *, channels=None, scope=None):
        self.calls.append(("events_subscribe", {"channels": channels, "scope": _scope(scope)}))
        return EventSubscription(
            subscription_id="sub_embed",
            transport="eventsource",
            eventsource_url="http://upstream.local/v1/events/subscribe?subscription_token=upstream-secret",
            subscription_token="upstream-secret",
            replay_cursor="cursor_embed",
            expires_at="2026-05-12T12:00:00Z",
            allowed_channels=tuple(channels or ("chat",)),
        )


CONFIG = {
    "demo_identity_mode": True,
    "harnessos_capability_token": "server-side-placeholder-token",
    "identity_scope": {"app_id": "reference_app", "project_id": "demo", "workspace_id": "local"},
    "demo_capabilities": [
        "sessions",
        "turns",
        "events",
        "artifacts.read",
        "jobs",
        "approvals",
        "packs.read",
        "connectors.read",
    ],
}


def test_embed_definition_static_shape_excludes_runtime_and_tokens() -> None:
    definition = _json(DEMO / "embed_definition.example.json")
    forbidden = {"capability_token", "capabilityToken", "session_id", "sessionId", "eventsource_url", "eventsourceUrl", "subscription_token"}

    assert definition["schemaVersion"] == "1"
    assert definition["capabilityMode"] == "bff"
    assert definition["transportMode"] == "bff_proxy"
    assert definition["tracePolicy"]["enabled"] is False
    assert not (set(definition) & forbidden)
    assert "trace" not in definition["allowedEventChannels"]


def test_allowed_actions_exclude_forbidden_methods() -> None:
    definition = _json(DEMO / "embed_definition.example.json")
    actions = set(definition["allowedActions"])

    assert {"session.start", "turn.start", "approval.respond", "artifact.read_metadata", "job.get", "pack.get"} <= actions
    for forbidden in ("approval.approve", "approval.reject", "meeting.process_recording", "knowledge.search", "scope_mode=all"):
        assert forbidden not in actions


def test_embed_bootstrap_hides_upstream_subscription_token_and_uses_bff_url() -> None:
    sdk = FakeSdkClient()
    app = create_app(config=CONFIG, sdk_client=sdk)
    client = TestClient(app)

    response = client.get("/bff/embed/bootstrap?channels=chat,job&create_session=true")
    assert response.status_code == 200
    payload = response.json()
    raw = json.dumps(payload)

    assert payload["session"]["session_id"] == "sess_embed"
    assert payload["eventSubscription"]["eventsourceUrl"].startswith("/bff/events/subscribe")
    assert "upstream-secret" not in raw
    assert "subscription_token" not in raw
    assert [call[0] for call in sdk.calls] == ["session_start", "events_subscribe"]


def test_embed_bootstrap_does_not_create_session_by_default() -> None:
    sdk = FakeSdkClient()
    client = TestClient(create_app(config=CONFIG, sdk_client=sdk))

    response = client.get("/bff/embed/bootstrap")
    assert response.status_code == 200
    assert response.json()["session"] is None
    assert [call[0] for call in sdk.calls] == ["events_subscribe"]


def test_trace_channel_requires_debug_or_trace_capability() -> None:
    client = TestClient(create_app(config=CONFIG, sdk_client=FakeSdkClient()))
    denied = client.get("/bff/embed/bootstrap?channels=trace")

    assert denied.status_code == 403
    assert denied.json()["error"]["code"] == "CAPABILITY_DENIED"


def test_event_union_aligns_with_event_schemas_and_aliases() -> None:
    schema_types = {schema["type"] for schema in EVENT_SCHEMAS}
    inventory = {entry["type"]: entry for entry in EVENT_INVENTORY}
    required = {
        "turn.started",
        "item.delta",
        "turn.completed",
        "turn.failed",
        "job.queued",
        "job.running",
        "job.completed",
        "job.failed",
        "job.cancelled",
        "artifact.registered",
        "artifact.updated",
        "artifact.read_blocked",
        "approval.required",
        "approval.approved",
        "approval.rejected",
        "trace.recorded",
        "business.*",
    }

    assert required <= schema_types
    assert "artifact.created" not in schema_types
    assert "artifact.created" in inventory["artifact.registered"]["aliases"]
    assert inventory["business.*"]["status"] == "reserved"


def test_demo_fixture_is_platform_neutral_and_contains_no_secret_material() -> None:
    banned = (
        "meeting",
        "knowledge",
        "data_service",
        "voice_service",
        "funasr",
        "capability_token",
        "subscription_token",
        "upstream.local",
    )
    for path in DEMO.iterdir():
        if path.is_file():
            text = path.read_text(encoding="utf-8").lower()
            for value in banned:
                assert value not in text, f"{path}: {value}"


def test_no_server_internals_imported_by_typescript_embed_contract() -> None:
    text = (ROOT / "sdk/typescript/src/embed.ts").read_text(encoding="utf-8")
    for forbidden in ("apps/", "core/", "GatewayService", "RuntimeAdapter"):
        assert forbidden not in text


def test_docs_record_v3_5_h_complete_and_v3_5_i_current_closeout() -> None:
    for name in [
        "00_README.md",
        "v3_5_current_gap_analysis.md",
        "v3_5_acceptance_plan.md",
        "v3_5_development_plan_application_adaptation_layer.md",
        "v3_5_embed_contract_plan.md",
    ]:
        text = (DOCS / name).read_text(encoding="utf-8")
        assert "V3.5-H" in text
        if name != "v3_5_embed_contract_plan.md":
            assert "V3.5-I Reference App" in text


def _json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _scope(scope: Any) -> dict[str, Any] | None:
    if scope is None:
        return None
    if hasattr(scope, "to_dict"):
        return scope.to_dict()
    return dict(scope)

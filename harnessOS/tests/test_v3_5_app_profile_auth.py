"""V3.5-B AppProfile auth field tests."""

from __future__ import annotations

from core.apps.profiles import AppProfile, build_default_app_registry


def test_app_profile_auth_fields_are_serialized() -> None:
    profile = AppProfile(
        app_id="demo",
        display_name="Demo",
        domain="demo",
        default_pack="demo",
        allowed_origins=("http://localhost:5173",),
        default_capabilities=("sessions", "turns"),
        embed_policy={"allow_iframe": True},
    )
    payload = profile.to_dict()
    assert payload["allowed_origins"] == ["http://localhost:5173"]
    assert payload["default_capabilities"] == ["sessions", "turns"]
    assert payload["embed_policy"] == {"allow_iframe": True}


def test_default_profiles_define_local_auth_bounds() -> None:
    registry = build_default_app_registry()
    for profile in registry.list_profiles():
        assert "http://localhost:5173" in profile["allowed_origins"]
        assert "http://127.0.0.1:5173" in profile["allowed_origins"]
        assert "sessions" in profile["default_capabilities"]
        assert "turns" in profile["default_capabilities"]
        assert "connectors.read" in profile["default_capabilities"]
        assert "packs.read" in profile["default_capabilities"]
        assert "connector_execution" not in profile["default_capabilities"]
        assert "pack_execution" not in profile["default_capabilities"]

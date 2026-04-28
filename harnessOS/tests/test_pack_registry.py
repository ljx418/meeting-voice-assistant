from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from core.packs import build_default_pack_registry


def test_default_pack_registry_loads_active_and_stub_packs():
    registry = build_default_pack_registry()

    packs = registry.list_packs()
    names = {pack["name"] for pack in packs}

    assert names == {"meeting", "knowledge", "investment", "interview", "video_studio"}
    assert {pack["name"] for pack in registry.list_packs(status="active")} == {"meeting", "knowledge"}
    assert {pack["name"] for pack in registry.list_packs(status="stub")} == {
        "investment",
        "interview",
        "video_studio",
    }


def test_pack_registry_resolves_pack_by_domain_and_workflow():
    registry = build_default_pack_registry()

    meeting = registry.get_pack("meeting")
    knowledge = registry.get_workflow_pack("knowledge.workflow")

    assert meeting is not None
    assert meeting.domain == "meeting"
    assert meeting.status == "active"
    assert "meeting.workflow" in meeting.workflows
    assert knowledge is not None
    assert knowledge.name == "knowledge"

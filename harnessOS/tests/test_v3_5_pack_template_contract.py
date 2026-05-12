"""V3.5 pack template contract evidence tests."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.packs import PackRegistry, build_default_pack_registry
from core.protocol.version import HARNESSOS_VERSION


TEMPLATE = ROOT / "templates" / "pack" / "manifest.json"
FIXTURE_ROOT = ROOT / "tests" / "fixtures" / "v3_5"


def test_pack_template_is_not_runtime_discovered() -> None:
    assert "replace_me_pack" not in {pack["name"] for pack in build_default_pack_registry().list_packs()}
    assert PackRegistry.load_from_paths([ROOT / "templates"]).list_packs() == []


def test_pack_template_uses_current_manifest_contract_fields() -> None:
    manifest = json.loads(TEMPLATE.read_text(encoding="utf-8"))
    required = {
        "name",
        "domain",
        "version",
        "manifest_schema_version",
        "workflows",
        "workflow_dsl",
        "skills",
        "policy_bundles",
        "connectors",
        "connector_capabilities",
        "artifact_kinds",
        "artifact_schemas",
        "metadata",
        "min_harnessos_version",
        "target_harnessos_version",
    }
    assert required <= set(manifest)
    assert "compatibility_warnings" not in manifest
    assert "policies" not in manifest
    assert "artifact_types" not in manifest


def test_dummy_pack_external_path_discovery_and_assembly_envelope() -> None:
    registry = PackRegistry.load_from_paths([FIXTURE_ROOT])
    pack = registry.get_pack("dummy_pack")
    assert pack is not None
    assert pack.min_harnessos_version == HARNESSOS_VERSION

    assembled = registry.evaluate_assembly(
        "dummy_pack",
        supported_workflows={"dummy.workflow"},
        available_connectors={"dummy_connector"},
        available_connector_capabilities={"dummy_connector": {"capabilities": {"dummy.run"}, "tools": {"dummy_tool"}}},
        available_policy_bundles={"dummy.default"},
    )
    assert assembled.status == "assembled"

    blocked = registry.evaluate_assembly(
        "dummy_pack",
        supported_workflows={"dummy.workflow"},
        available_connectors=set(),
        available_policy_bundles={"dummy.default"},
    )
    assert blocked.status == "blocked"
    assert blocked.to_dict()["blocked_reason"]
    assert blocked.to_dict()["next_actions"]


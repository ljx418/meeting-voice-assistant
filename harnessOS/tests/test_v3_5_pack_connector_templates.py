"""V3.5-G Pack / Connector template contract tests."""

from __future__ import annotations

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from apps.gateway.connectors import ConnectorRegistry
from core.packs import PackRegistry, build_default_pack_registry
from core.protocol.version import HARNESSOS_VERSION
from core.services import CoreAppService
from core.stores import CoreSQLiteStore


FIXTURES = PROJECT_ROOT / "tests" / "fixtures" / "v3_5"
TEMPLATES = PROJECT_ROOT / "templates"


def _connector_registry(tmp_path: Path, *, descriptor_paths: list[Path] | None = None) -> ConnectorRegistry:
    return ConnectorRegistry(
        core_service=CoreAppService(CoreSQLiteStore(tmp_path / "core.sqlite3")),
        connector_descriptor_paths=descriptor_paths,
    )


def test_templates_are_not_auto_discovered(tmp_path: Path) -> None:
    pack_registry = build_default_pack_registry()
    assert "replace_me_pack" not in {pack["name"] for pack in pack_registry.list_packs()}

    connector_registry = _connector_registry(tmp_path)
    assert "replace_me_connector" not in {
        connector["connector_id"] for connector in connector_registry.list_connectors()
    }


def test_template_metadata_prevents_explicit_template_root_discovery(tmp_path: Path) -> None:
    pack_registry = PackRegistry.load_from_paths([TEMPLATES])
    assert pack_registry.list_packs() == []

    connector_registry = _connector_registry(tmp_path, descriptor_paths=[TEMPLATES])
    assert "replace_me_connector" not in {
        connector["connector_id"] for connector in connector_registry.list_connectors()
    }


def test_dummy_pack_external_path_discovery() -> None:
    registry = PackRegistry.load_from_paths([FIXTURES / "v3_5_missing", FIXTURES])
    pack = registry.get_pack("dummy_pack")
    assert pack is not None
    assert pack.name == "dummy_pack"
    assert pack.domain == "dummy"
    assert pack.manifest_schema_version == "1"
    assert pack.min_harnessos_version == HARNESSOS_VERSION
    assert pack.target_harnessos_version == HARNESSOS_VERSION

    assembly = registry.evaluate_assembly(
        "dummy_pack",
        supported_workflows={"dummy.workflow"},
        available_connectors={"dummy_connector"},
        available_connector_capabilities={
            "dummy_connector": {
                "capabilities": {"dummy.run"},
                "tools": {"dummy_tool"},
            }
        },
        available_policy_bundles={"dummy.default"},
    )
    assert assembly.status == "assembled"
    assert assembly.compatibility_warnings == ()
    assert assembly.to_dict()["compatibility_warnings"] == []


def test_dummy_connector_external_descriptor_discovery(tmp_path: Path) -> None:
    registry = _connector_registry(tmp_path, descriptor_paths=[FIXTURES / "dummy_connector"])
    health = registry.refresh_health("dummy_connector")

    assert health["health"]["status"] == "available"
    assert health["connector"]["connector_id"] == "dummy_connector"
    assert health["connector"]["execution_mode"] == "stub"
    assert health["connector"]["capabilities"]["capabilities"] == ["dummy.run"]
    assert health["health"]["details"]["descriptor_schema_version"] == "1"


def test_connector_descriptor_discovery_does_not_execute_example_modules(tmp_path: Path) -> None:
    registry = _connector_registry(tmp_path, descriptor_paths=[FIXTURES / "dummy_connector"])
    result = registry.refresh_health("dummy_connector")
    assert result["health"]["status"] == "available"


def test_no_hardcoded_dummy_ids_in_core_or_gateway_registries() -> None:
    scanned_paths = [
        PROJECT_ROOT / "core" / "packs" / "registry.py",
        PROJECT_ROOT / "apps" / "gateway" / "connectors.py",
        PROJECT_ROOT / "apps" / "gateway" / "service.py",
    ]
    for path in scanned_paths:
        text = path.read_text(encoding="utf-8")
        assert "dummy_pack" not in text
        assert "dummy_connector" not in text


def test_pack_manifest_field_compatibility() -> None:
    manifest = json.loads((TEMPLATES / "pack" / "manifest.json").read_text(encoding="utf-8"))
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
    assert "policies" not in manifest
    assert "artifact_types" not in manifest
    assert "compatibility_warnings" not in manifest
    assert "app_id" not in manifest


def test_connector_descriptor_security_field_compatibility() -> None:
    descriptor = json.loads((TEMPLATES / "connector" / "descriptor.json").read_text(encoding="utf-8"))
    assert descriptor["descriptor_schema_version"] == "1"
    assert descriptor["execution_mode"] == "stub"
    assert descriptor["health"]["mode"] == "static"
    assert "security" in descriptor
    assert "compatibility_warnings" not in descriptor


def test_platform_neutrality() -> None:
    banned = ("meeting", "knowledge", "data_service", "voice_service", "funasr")
    for path in [
        TEMPLATES / "pack" / "manifest.json",
        TEMPLATES / "connector" / "descriptor.json",
        FIXTURES / "dummy_pack" / "manifest.json",
        FIXTURES / "dummy_connector" / "descriptor.json",
    ]:
        text = path.read_text(encoding="utf-8").lower()
        for value in banned:
            assert value not in text

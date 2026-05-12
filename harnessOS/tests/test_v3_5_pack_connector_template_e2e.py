"""V3.5 pack + connector template E2E evidence tests."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from apps.gateway.connectors import ConnectorRegistry
from core.packs import PackRegistry
from core.services import CoreAppService
from core.stores import CoreSQLiteStore


FIXTURE_ROOT = ROOT / "tests" / "fixtures" / "v3_5"


def test_pack_and_connector_templates_work_as_external_runtime_instances(tmp_path: Path) -> None:
    pack_registry = PackRegistry.load_from_paths([FIXTURE_ROOT])
    connector_registry = ConnectorRegistry(
        core_service=CoreAppService(CoreSQLiteStore(tmp_path / "core.sqlite3")),
        connector_descriptor_paths=[FIXTURE_ROOT / "dummy_connector"],
    )
    connector_health = connector_registry.refresh_health("dummy_connector")

    assembly = pack_registry.evaluate_assembly(
        "dummy_pack",
        supported_workflows={"dummy.workflow"},
        available_connectors={connector_health["connector"]["connector_id"]},
        available_connector_capabilities={
            "dummy_connector": {
                "capabilities": set(connector_health["connector"]["capabilities"]["capabilities"]),
                "tools": set(connector_health["connector"]["capabilities"]["tools"]),
            }
        },
        available_policy_bundles={"dummy.default"},
    )

    assert connector_health["health"]["status"] == "available"
    assert assembly.status == "assembled"
    assert assembly.to_dict()["compatibility_warnings"] == []


def test_template_instances_are_not_hardcoded_in_core_or_gateway() -> None:
    scanned_paths = [
        ROOT / "core" / "packs" / "registry.py",
        ROOT / "apps" / "gateway" / "connectors.py",
        ROOT / "apps" / "gateway" / "service.py",
    ]
    for path in scanned_paths:
        text = path.read_text(encoding="utf-8")
        assert "dummy_pack" not in text
        assert "dummy_connector" not in text
        assert "reference_app_pack" not in text
        assert "reference_app_connector" not in text


"""V3.5 connector template contract evidence tests."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from apps.gateway.connectors import ConnectorRegistry
from core.services import CoreAppService
from core.stores import CoreSQLiteStore


TEMPLATE = ROOT / "templates" / "connector" / "descriptor.json"
FIXTURE = ROOT / "tests" / "fixtures" / "v3_5" / "dummy_connector"


def _registry(tmp_path: Path, paths: list[Path] | None = None) -> ConnectorRegistry:
    return ConnectorRegistry(
        core_service=CoreAppService(CoreSQLiteStore(tmp_path / "core.sqlite3")),
        connector_descriptor_paths=paths,
    )


def test_connector_template_is_not_runtime_discovered(tmp_path: Path) -> None:
    registry = _registry(tmp_path)
    assert "replace_me_connector" not in {connector["connector_id"] for connector in registry.list_connectors()}

    explicit_template = _registry(tmp_path, [ROOT / "templates"])
    assert "replace_me_connector" not in {connector["connector_id"] for connector in explicit_template.list_connectors()}


def test_connector_template_descriptor_security_contract() -> None:
    descriptor = json.loads(TEMPLATE.read_text(encoding="utf-8"))
    assert descriptor["descriptor_schema_version"] == "1"
    assert descriptor["execution_mode"] == "stub"
    assert descriptor["health"]["mode"] == "static"
    assert descriptor["security"]["network_policy"] == "none"
    assert "compatibility_warnings" not in descriptor


def test_dummy_connector_external_descriptor_discovery(tmp_path: Path) -> None:
    registry = _registry(tmp_path, [FIXTURE])
    health = registry.refresh_health("dummy_connector")
    assert health["health"]["status"] == "available"
    assert health["connector"]["connector_id"] == "dummy_connector"
    assert health["connector"]["execution_mode"] == "stub"


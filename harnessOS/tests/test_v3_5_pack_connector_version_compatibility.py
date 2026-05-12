"""V3.5-G Pack / Connector version compatibility tests."""

from __future__ import annotations

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from apps.gateway.connectors import ConnectorRegistry
from core.packs import DomainPackManifest, PackRegistry
from core.protocol.version import HARNESSOS_VERSION
from core.services import CoreAppService
from core.stores import CoreSQLiteStore


def test_pack_min_harnessos_version_above_current_blocks() -> None:
    registry = PackRegistry(
        [
            DomainPackManifest(
                name="future_pack",
                version="0.1.0",
                domain="future",
                status="active",
                workflows=("future.workflow",),
                min_harnessos_version="99.0.0",
                target_harnessos_version=HARNESSOS_VERSION,
            )
        ]
    )

    assembly = registry.evaluate_assembly(
        "future_pack",
        supported_workflows={"future.workflow"},
        available_connectors=set(),
        available_policy_bundles=set(),
    )

    assert assembly.status == "blocked"
    assert "min_harnessos_version:99.0.0" in assembly.missing_dependencies
    assert assembly.to_dict()["blocked_reason"] == "Pack is blocked by an incompatible min_harnessos_version."


def test_pack_target_harnessos_version_mismatch_degrades_with_warning() -> None:
    registry = PackRegistry(
        [
            DomainPackManifest(
                name="older_pack",
                version="0.1.0",
                domain="older",
                status="active",
                workflows=("older.workflow",),
                min_harnessos_version="3.0.0",
                target_harnessos_version="3.4.0",
            )
        ]
    )

    assembly = registry.evaluate_assembly(
        "older_pack",
        supported_workflows={"older.workflow"},
        available_connectors=set(),
        available_policy_bundles=set(),
    )

    assert assembly.status == "degraded"
    assert assembly.missing_dependencies == ("target_harnessos_version:3.4.0",)
    assert assembly.compatibility_warnings
    assert "3.4.0" in assembly.compatibility_warnings[0]


def test_connector_unsupported_descriptor_schema_blocks(tmp_path: Path) -> None:
    descriptor_dir = _write_descriptor(tmp_path, descriptor_schema_version="99")
    registry = _connector_registry(tmp_path, descriptor_dir)

    result = registry.refresh_health("compat_connector")

    assert result["health"]["status"] == "blocked"
    assert "descriptor_schema:99" in result["health"]["details"]["blocked_dependencies"]


def test_connector_target_version_mismatch_degrades_with_warning(tmp_path: Path) -> None:
    descriptor_dir = _write_descriptor(tmp_path, target_harnessos_version="3.4.0")
    registry = _connector_registry(tmp_path, descriptor_dir)

    result = registry.refresh_health("compat_connector")

    assert result["health"]["status"] == "degraded"
    assert "target_harnessos_version:3.4.0" in result["health"]["details"]["degraded_dependencies"]
    assert result["health"]["details"]["compatibility_warnings"]


def test_connector_required_dependency_missing_blocks(tmp_path: Path) -> None:
    descriptor_dir = _write_descriptor(tmp_path, required_dependencies=["command:unlikely_v3_5_missing_binary"])
    registry = _connector_registry(tmp_path, descriptor_dir)

    result = registry.refresh_health("compat_connector")

    assert result["health"]["status"] == "blocked"
    assert "required_dependency:command:unlikely_v3_5_missing_binary" in result["health"]["details"]["blocked_dependencies"]


def test_connector_optional_dependency_missing_degrades(tmp_path: Path) -> None:
    descriptor_dir = _write_descriptor(tmp_path, optional_dependencies=["command:unlikely_v3_5_missing_binary"])
    registry = _connector_registry(tmp_path, descriptor_dir)

    result = registry.refresh_health("compat_connector")

    assert result["health"]["status"] == "degraded"
    assert "optional_dependency:command:unlikely_v3_5_missing_binary" in result["health"]["details"]["degraded_dependencies"]


def _connector_registry(tmp_path: Path, descriptor_dir: Path) -> ConnectorRegistry:
    return ConnectorRegistry(
        core_service=CoreAppService(CoreSQLiteStore(tmp_path / "core.sqlite3")),
        connector_descriptor_paths=[descriptor_dir],
    )


def _write_descriptor(
    tmp_path: Path,
    *,
    descriptor_schema_version: str = "1",
    min_harnessos_version: str = "3.5.0",
    target_harnessos_version: str = "3.5.0",
    required_dependencies: list[str] | None = None,
    optional_dependencies: list[str] | None = None,
) -> Path:
    descriptor_dir = tmp_path / "compat_connector"
    descriptor_dir.mkdir()
    descriptor = {
        "descriptor_schema_version": descriptor_schema_version,
        "connector_id": "compat_connector",
        "domain": "compat",
        "kind": "template_stub",
        "version": "0.1.0",
        "min_harnessos_version": min_harnessos_version,
        "target_harnessos_version": target_harnessos_version,
        "app_scope": ["compat"],
        "capabilities": {"capabilities": ["compat.run"], "tools": ["compat_tool"]},
        "execution_mode": "stub",
        "trust_level": "trusted_local",
        "config_ref": "connectors.compat",
        "health": {
            "mode": "static",
            "status": "available",
            "message": "Compatibility connector is available.",
            "required_dependencies": required_dependencies or [],
            "optional_dependencies": optional_dependencies or [],
        },
        "security": {
            "allowed_commands": [],
            "allowed_paths": [],
            "allowed_network_hosts": [],
            "network_policy": "none",
            "tool_risk_defaults": {"read_only": True},
            "requires_approval_for": [],
        },
        "metadata": {"fixture": True},
    }
    (descriptor_dir / "descriptor.json").write_text(json.dumps(descriptor), encoding="utf-8")
    return descriptor_dir

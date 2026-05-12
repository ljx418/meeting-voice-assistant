"""Connector registry used by the gateway control plane."""

from __future__ import annotations

import json
import os
import shutil
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Optional
from urllib.parse import urlparse

from core.config import (
    ComfyUIConfig,
    DataServiceMcpConfig,
    FunASRMcpConfig,
    MeetingMcpConfig,
    get_comfyui_config,
    get_data_service_mcp_config,
    get_funasr_mcp_config,
    get_meeting_mcp_config,
)
from core.protocol import ConnectorRecord
from core.protocol.version import (
    HARNESSOS_VERSION,
    SUPPORTED_CONNECTOR_DESCRIPTOR_SCHEMA_VERSIONS,
)
from core.services import CoreAppService


MEETING_VOICE_MCP_CONNECTOR_ID = "meeting_voice_mcp"
FUNASR_MCP_CONNECTOR_ID = "funasr_mcp"
DATA_SERVICE_MCP_CONNECTOR_ID = "data_service_mcp"
REMOTE_COMFYUI_CONNECTOR_ID = "remote_comfyui"
LOCAL_KNOWLEDGE_CONNECTOR_ID = "local.knowledge"

DATA_SERVICE_TOOLS = [
    "knowledge_workspace_create",
    "knowledge_workspace_list",
    "knowledge_workspace_describe",
    "knowledge_source_import",
    "knowledge_source_list",
    "knowledge_source_remove",
    "knowledge_build_start",
    "knowledge_build_status",
    "knowledge_build_cancel",
    "knowledge_workspace_archive",
    "knowledge_ingest_v2",
    "knowledge_query_v2",
    "knowledge_quality_summary_v2",
    "knowledge_correction_plan_v2",
    "knowledge_quality_feedback_v2",
    "knowledge_correction_rules_v2",
    "knowledge_review_correction_rule_v2",
    "knowledge_query",
    "knowledge_quality_summary",
    "knowledge_quality_feedback",
    "knowledge_correction_rules",
    "knowledge_review_correction_rule",
    "knowledge_correction_plan",
]

DATA_SERVICE_CAPABILITIES = [
    "knowledge.lifecycle",
    "knowledge.source",
    "knowledge.build",
    "knowledge.query",
    "knowledge.summarize",
    "knowledge.citation",
]


@dataclass(frozen=True)
class ConnectorDefinition:
    """Descriptor-driven definition for one connector contract."""

    connector_id: str
    record_factory: Callable[["ConnectorRegistry", "ConnectorHealth"], ConnectorRecord]
    health_checker: Callable[["ConnectorRegistry"], ConnectorHealth]


@dataclass(frozen=True)
class ConnectorHealth:
    """Health result for one connector."""

    status: str
    message: str
    details: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "message": self.message,
            "details": dict(self.details),
        }


@dataclass(frozen=True)
class ExternalConnectorDescriptor:
    """Static connector descriptor loaded from an explicit descriptor.json path."""

    connector_id: str
    domain: Optional[str]
    kind: str
    version: str
    descriptor_schema_version: str
    capabilities: dict[str, Any]
    execution_mode: str
    trust_level: str
    config_ref: Optional[str]
    app_scope: list[str]
    security: dict[str, Any]
    health: dict[str, Any]
    metadata: dict[str, Any] = field(default_factory=dict)
    min_harnessos_version: str = ""
    target_harnessos_version: str = ""
    descriptor_path: Optional[str] = None


class ConnectorRegistry:
    """Core-backed registry for local MCP, tool, and service connectors."""

    def __init__(
        self,
        *,
        core_service: CoreAppService,
        meeting_config: Optional[MeetingMcpConfig] = None,
        funasr_config: Optional[FunASRMcpConfig] = None,
        data_service_config: Optional[DataServiceMcpConfig] = None,
        comfyui_config: Optional[ComfyUIConfig] = None,
        connector_definitions: Optional[dict[str, ConnectorDefinition]] = None,
        connector_descriptor_paths: Optional[list[Path]] = None,
    ) -> None:
        self.core_service = core_service
        self.meeting_config = meeting_config or get_meeting_mcp_config()
        self.funasr_config = funasr_config or get_funasr_mcp_config()
        self.data_service_config = data_service_config or get_data_service_mcp_config()
        self.comfyui_config = comfyui_config or get_comfyui_config()
        self.connector_definitions = dict(connector_definitions or {
            MEETING_VOICE_MCP_CONNECTOR_ID: ConnectorDefinition(
                connector_id=MEETING_VOICE_MCP_CONNECTOR_ID,
                record_factory=ConnectorRegistry._meeting_mcp_record,
                health_checker=ConnectorRegistry._check_meeting_mcp_health,
            ),
            FUNASR_MCP_CONNECTOR_ID: ConnectorDefinition(
                connector_id=FUNASR_MCP_CONNECTOR_ID,
                record_factory=ConnectorRegistry._funasr_mcp_record,
                health_checker=ConnectorRegistry._check_funasr_mcp_health,
            ),
            DATA_SERVICE_MCP_CONNECTOR_ID: ConnectorDefinition(
                connector_id=DATA_SERVICE_MCP_CONNECTOR_ID,
                record_factory=ConnectorRegistry._data_service_mcp_record,
                health_checker=ConnectorRegistry._check_data_service_mcp_health,
            ),
            LOCAL_KNOWLEDGE_CONNECTOR_ID: ConnectorDefinition(
                connector_id=LOCAL_KNOWLEDGE_CONNECTOR_ID,
                record_factory=ConnectorRegistry._local_knowledge_record,
                health_checker=ConnectorRegistry._check_local_knowledge_health,
            ),
            REMOTE_COMFYUI_CONNECTOR_ID: ConnectorDefinition(
                connector_id=REMOTE_COMFYUI_CONNECTOR_ID,
                record_factory=ConnectorRegistry._remote_comfyui_record,
                health_checker=ConnectorRegistry._check_remote_comfyui_health,
            ),
        })
        self._register_external_descriptor_definitions(connector_descriptor_paths or [])
        self.register_default_connectors()

    def register_default_connectors(self) -> None:
        """Register built-in connector descriptors."""
        for connector_id in self.connector_definitions:
            self.refresh_health(connector_id)

    def list_connectors(
        self,
        *,
        domain: Optional[str] = None,
        kind: Optional[str] = None,
        health: Optional[str] = None,
    ) -> list[dict[str, Any]]:
        """Return connector descriptors."""
        self.register_default_connectors()
        records = self.core_service.list_connectors(domain=domain, kind=kind, health=health)
        return [record.model_dump(mode="json") for record in records]

    def get_connector(self, connector_id: str) -> dict[str, Any]:
        """Return one connector descriptor."""
        self.register_default_connectors()
        return self.core_service.get_connector(connector_id).model_dump(mode="json")

    def refresh_health(self, connector_id: str) -> dict[str, Any]:
        """Refresh connector health and persist the descriptor."""
        definition = self.connector_definitions.get(connector_id)
        if definition is None:
            raise LookupError(f"Connector not found: {connector_id}")
        health = definition.health_checker(self)
        record = definition.record_factory(self, health)
        self.core_service.save_connector(record)
        return {
            "connector": record.model_dump(mode="json"),
            "health": health.to_dict(),
        }

    def _register_external_descriptor_definitions(self, paths: list[Path]) -> None:
        for descriptor_path in _iter_connector_descriptor_paths(paths):
            descriptor = _load_connector_descriptor(descriptor_path)
            self.connector_definitions[descriptor.connector_id] = ConnectorDefinition(
                connector_id=descriptor.connector_id,
                record_factory=_external_connector_record_factory(descriptor),
                health_checker=_external_connector_health_checker(descriptor),
            )

    def require_available(self, connector_id: str) -> None:
        """Raise an explainable error if a connector is not available."""
        result = self.refresh_health(connector_id)
        health = result["health"]
        if health["status"] != "available":
            raise RuntimeError(
                f"Connector {connector_id} is {health['status']}: {health['message']}"
            )

    def _meeting_mcp_record(self, health: ConnectorHealth) -> ConnectorRecord:
        config = self.meeting_config
        module_path = _module_file_from_args(config.argv, Path(config.cwd).expanduser())
        return ConnectorRecord(
            connector_id=MEETING_VOICE_MCP_CONNECTOR_ID,
            kind="mcp_stdio",
            domain="meeting",
            version="0.1.0",
            health=health.status,
            trust_level="trusted_local",
            execution_mode="stdio",
            capabilities={
                "transport": "stdio",
                "capabilities": ["meeting.analyze", "minutes.generate"],
                "tools": [
                    "meeting_process_file",
                    "meeting_analyze_text",
                    "meeting_build_minutes",
                ],
                "resources": ["meeting://agent-guide"],
                "prompts": ["meeting_process_recording"],
                "audio_engines": [config.default_engine],
                "default_language": config.default_language,
                "health_message": health.message,
            },
            config_ref="HARNESS_MEETING_MCP_*",
            secret_ref=None,
            app_scope=["meeting"],
            allowed_commands=_allowed_command_values(config.command),
            allowed_paths=_allowed_paths(
                config.cwd,
                module_path,
                config.audio_dir,
            ),
            network_policy="none",
            tool_risk_defaults={
                "read_only": False,
                "destructive": False,
                "external_side_effect": True,
            },
            requires_approval_for=["external_call"],
            metadata={
                "cwd": config.cwd,
                "command": config.command,
                "args": config.argv,
                "health_details": health.details,
            },
        )

    def _check_meeting_mcp_health(self) -> ConnectorHealth:
        config = self.meeting_config
        cwd = Path(config.cwd).expanduser()
        details: dict[str, Any] = {
            "cwd": str(cwd),
            "command": config.command,
            "args": config.argv,
        }
        if not cwd.exists() or not cwd.is_dir():
            return ConnectorHealth(
                status="missing_dependency",
                message=f"Meeting MCP cwd does not exist: {cwd}",
                details=details,
            )
        if not _command_available(config.command, cwd):
            return ConnectorHealth(
                status="missing_dependency",
                message=f"Meeting MCP command is not available: {config.command}",
                details=details,
            )
        module_path = _module_file_from_args(config.argv, cwd)
        if module_path is not None:
            details["module_path"] = str(module_path)
            if not module_path.exists():
                return ConnectorHealth(
                    status="missing_dependency",
                    message=f"Meeting MCP module file does not exist: {module_path}",
                    details=details,
                )
        return ConnectorHealth(
            status="available",
            message="Meeting MCP stdio connector dependencies are available.",
            details=details,
        )

    def _funasr_mcp_record(self, health: ConnectorHealth) -> ConnectorRecord:
        config = self.funasr_config
        contract_only = config.execution != "stdio"
        module_path = _module_file_from_args(config.argv, Path(config.cwd).expanduser())
        audio_roots = [item for item in config.audio_roots.split(":") if item]
        return ConnectorRecord(
            connector_id=FUNASR_MCP_CONNECTOR_ID,
            kind="mcp_stdio",
            domain="meeting",
            version="0.1.0",
            health=health.status,
            trust_level="trusted_local",
            execution_mode="stdio" if config.execution == "stdio" else "stub",
            capabilities={
                "transport": "stdio",
                "contract_only": contract_only,
                "capabilities": ["audio.transcribe"],
                "tools": [
                    "funasr_health",
                    "funasr_recognize_file",
                ],
                "resources": ["funasr://capabilities"],
                "proxy_endpoint": config.endpoint,
                "audio_roots": config.audio_roots.split(":"),
                "request_timeout": config.request_timeout,
                "max_file_size_mb": config.max_file_size_mb,
                "health_message": health.message,
                "execution_enabled": config.execution == "stdio",
            },
            config_ref="HARNESS_FUNASR_MCP_*",
            secret_ref=None,
            app_scope=["meeting"],
            allowed_commands=_allowed_command_values(config.command),
            allowed_paths=_allowed_paths(config.cwd, module_path, *audio_roots),
            allowed_network_hosts=[_host_from_url(config.endpoint)] if _host_from_url(config.endpoint) else [],
            network_policy="allowlist",
            tool_risk_defaults={
                "read_only": False,
                "destructive": False,
                "external_side_effect": True,
            },
            requires_approval_for=["external_call"],
            metadata={
                "cwd": config.cwd,
                "command": config.command,
                "args": config.argv,
                "execution": "mcp_stdio" if config.execution == "stdio" else "deferred",
                "health_details": health.details,
            },
        )

    def _check_funasr_mcp_health(self) -> ConnectorHealth:
        config = self.funasr_config
        if config.execution != "stdio":
            return ConnectorHealth(
                status="contract_stub",
                message="FunASR MCP connector contract is registered; stdio execution is disabled.",
                details={"contract_only": True, "execution_enabled": False},
            )
        cwd = Path(config.cwd).expanduser()
        details: dict[str, Any] = {
            "cwd": str(cwd),
            "command": config.command,
            "args": config.argv,
            "endpoint": config.endpoint,
        }
        if not cwd.exists() or not cwd.is_dir():
            return ConnectorHealth(
                status="missing_dependency",
                message=f"FunASR MCP cwd does not exist: {cwd}",
                details=details,
            )
        if not _command_available(config.command, cwd):
            return ConnectorHealth(
                status="missing_dependency",
                message=f"FunASR MCP command is not available: {config.command}",
                details=details,
            )
        module_path = _module_file_from_args(config.argv, cwd)
        if module_path is not None:
            details["module_path"] = str(module_path)
            if not module_path.exists():
                return ConnectorHealth(
                    status="missing_dependency",
                    message=f"FunASR MCP module file does not exist: {module_path}",
                    details=details,
                )
        return ConnectorHealth(
            status="available",
            message="FunASR MCP stdio connector dependencies are available.",
            details=details,
        )

    def _data_service_mcp_record(self, health: ConnectorHealth) -> ConnectorRecord:
        config = self.data_service_config
        contract_only = config.execution != "stdio"
        module_path = _module_file_from_args(config.argv, Path(config.cwd).expanduser())
        allowed_roots = [
            path
            for path in (
                config.cwd,
                config.workspace_root,
                config.allowed_workspace_roots,
                config.allowed_source_roots,
            )
            if path
        ]
        return ConnectorRecord(
            connector_id=DATA_SERVICE_MCP_CONNECTOR_ID,
            kind="mcp_stdio",
            domain="knowledge",
            version="0.1.0",
            health=health.status,
            trust_level="trusted_local",
            execution_mode="stdio" if config.execution == "stdio" else "stub",
            capabilities={
                "transport": "stdio",
                "contract_only": contract_only,
                "capabilities": DATA_SERVICE_CAPABILITIES,
                "tools": DATA_SERVICE_TOOLS,
                "resources": [
                    "data_service://summary",
                    "data_service://layout",
                    "data_service://build-status",
                    "data_service://quality-report",
                ],
                "prompts": ["knowledge_lifecycle_runbook", "knowledge_quality_review"],
                "health_message": health.message,
                "execution_enabled": config.execution == "stdio",
            },
            config_ref="HARNESS_DATA_SERVICE_MCP_*",
            secret_ref=None,
            app_scope=["knowledge"],
            allowed_commands=_allowed_command_values(config.command),
            allowed_paths=_allowed_paths(*allowed_roots, module_path),
            network_policy="none",
            tool_risk_defaults={
                "read_only": False,
                "destructive": False,
                "external_side_effect": True,
            },
            requires_approval_for=["external_call"],
            metadata={
                "cwd": config.cwd,
                "command": config.command,
                "args": config.argv,
                "execution": "mcp_stdio" if config.execution == "stdio" else "deferred",
                "request_timeout": config.request_timeout,
                "env": _data_service_env(config),
                "phase": "5-C" if config.execution == "stdio" else "5-A",
                "health_details": health.details,
            },
        )

    def _check_data_service_mcp_health(self) -> ConnectorHealth:
        config = self.data_service_config
        if config.execution != "stdio":
            return ConnectorHealth(
                status="contract_stub",
                message="Data Service MCP connector contract is registered; stdio execution is disabled.",
                details={"contract_only": True, "execution_enabled": False},
            )
        cwd = Path(config.cwd).expanduser()
        details: dict[str, Any] = {
            "cwd": str(cwd),
            "command": config.command,
            "args": config.argv,
            "execution_enabled": True,
        }
        if not cwd.exists() or not cwd.is_dir():
            return ConnectorHealth(
                status="missing_dependency",
                message=f"Data Service MCP cwd does not exist: {cwd}",
                details=details,
            )
        if not _command_available(config.command, cwd):
            return ConnectorHealth(
                status="missing_dependency",
                message=f"Data Service MCP command is not available: {config.command}",
                details=details,
            )
        module_path = _module_file_from_args(config.argv, cwd)
        if module_path is not None:
            details["module_path"] = str(module_path)
            if not module_path.exists():
                return ConnectorHealth(
                    status="missing_dependency",
                    message=f"Data Service MCP module file does not exist: {module_path}",
                    details=details,
                )
        return ConnectorHealth(
            status="available",
            message="Data Service MCP stdio connector dependencies are available.",
            details=details,
        )

    def _remote_comfyui_record(self, health: ConnectorHealth) -> ConnectorRecord:
        config = self.comfyui_config
        allowed_host = _host_from_url(config.base_url) if config.base_url else None
        return ConnectorRecord(
            connector_id=REMOTE_COMFYUI_CONNECTOR_ID,
            kind="http_service",
            domain="video_studio",
            version="0.1.0",
            health=health.status,
            trust_level="remote",
            execution_mode="http",
            capabilities={
                "transport": "http",
                "service": "comfyui",
                "modes": ["txt2img", "txt2video", "image_to_video"],
                "health_message": health.message,
                "configured": bool(config.base_url),
            },
            config_ref="HARNESS_COMFYUI_*",
            secret_ref=None,
            app_scope=["video_studio"],
            allowed_commands=[],
            allowed_paths=[],
            allowed_network_hosts=[allowed_host] if allowed_host else [],
            network_policy="allowlist" if allowed_host else "none",
            tool_risk_defaults={
                "read_only": False,
                "destructive": False,
                "external_side_effect": True,
            },
            requires_approval_for=["external_call"],
            metadata={
                "base_url_configured": bool(config.base_url),
                "base_url": config.base_url,
                "request_timeout": config.request_timeout,
                "health_details": health.details,
            },
        )

    def _local_knowledge_record(self, health: ConnectorHealth) -> ConnectorRecord:
        return ConnectorRecord(
            connector_id=LOCAL_KNOWLEDGE_CONNECTOR_ID,
            kind="native_tool",
            domain="knowledge",
            version="0.1.0",
            health=health.status,
            trust_level="trusted_local",
            execution_mode="stub",
            capabilities={
                "transport": "inprocess",
                "contract_only": True,
                "tools": ["kb_ingest", "kb_search"],
                "health_message": health.message,
                "execution_enabled": False,
            },
            config_ref="HARNESS_LOCAL_KNOWLEDGE_*",
            secret_ref=None,
            app_scope=["knowledge"],
            allowed_commands=[],
            allowed_paths=[],
            allowed_network_hosts=[],
            network_policy="none",
            tool_risk_defaults={
                "read_only": True,
                "destructive": False,
                "external_side_effect": False,
            },
            requires_approval_for=[],
            metadata={
                "execution": "legacy_fallback",
                "health_details": health.details,
            },
        )

    def _check_local_knowledge_health(self) -> ConnectorHealth:
        return ConnectorHealth(
            status="contract_stub",
            message="Local knowledge compatibility connector is registered for legacy fallback only.",
            details={"contract_only": True, "execution_enabled": False},
        )

    def _check_remote_comfyui_health(self) -> ConnectorHealth:
        config = self.comfyui_config
        details: dict[str, Any] = {
            "base_url_configured": bool(config.base_url),
            "request_timeout": config.request_timeout,
        }
        if not config.base_url:
            return ConnectorHealth(
                status="not_configured",
                message="Remote ComfyUI base URL is not configured. Set HARNESS_COMFYUI_BASE_URL to enable it.",
                details=details,
            )
        details["base_url"] = config.base_url
        return ConnectorHealth(
            status="configured",
            message="Remote ComfyUI connector is configured; runtime execution is not enabled in Phase 4-B2 MVP.",
            details=details,
        )


def _module_file_from_args(args: list[str], cwd: Path) -> Optional[Path]:
    if "-m" not in args:
        return None
    index = args.index("-m")
    if index + 1 >= len(args):
        return None
    module = args[index + 1]
    return cwd / Path(*module.split(".")).with_suffix(".py")


def _command_available(command: str, cwd: Path) -> bool:
    command_path = Path(command).expanduser()
    if command_path.is_absolute():
        return command_path.exists()
    if "/" in command:
        return (cwd / command_path).exists()
    return shutil.which(command) is not None


def _data_service_env(config: DataServiceMcpConfig) -> dict[str, str]:
    env: dict[str, str] = {}
    if config.workspace_root:
        env["DATA_SERVICE_WORKSPACE_ROOT"] = config.workspace_root
        env["DATA_SERVICE_WORKSPACE"] = str(Path(config.workspace_root).expanduser() / "default")
    if config.allowed_workspace_roots:
        env["DATA_SERVICE_ALLOWED_WORKSPACE_ROOTS"] = config.allowed_workspace_roots
    if config.allowed_source_roots:
        env["DATA_SERVICE_ALLOWED_SOURCE_ROOTS"] = config.allowed_source_roots
    return env


def _allowed_command_values(command: str) -> list[str]:
    command_path = Path(command).expanduser()
    values = {command}
    if command_path.exists():
        values.add(str(command_path.resolve()))
        values.add(command_path.name)
    return sorted(values)


def _allowed_paths(*paths: Optional[str | Path]) -> list[str]:
    allowed: list[str] = []
    seen: set[str] = set()
    for path in paths:
        if not path:
            continue
        if isinstance(path, str) and os.pathsep in path:
            parts = [item for item in path.split(os.pathsep) if item]
        else:
            parts = [path]
        for item in parts:
            resolved = Path(item).expanduser().resolve()
            value = str(resolved)
            if value not in seen:
                seen.add(value)
                allowed.append(value)
    return allowed


def _iter_connector_descriptor_paths(paths: list[Path]) -> list[Path]:
    descriptor_paths: list[Path] = []
    for raw_path in paths:
        path = Path(raw_path).expanduser().resolve()
        if path.is_dir():
            candidate = path / "descriptor.json"
            if candidate.exists() and not _connector_descriptor_is_template(candidate):
                descriptor_paths.append(candidate)
            for nested in sorted(path.glob("*/descriptor.json")):
                if _connector_descriptor_is_template(nested):
                    continue
                descriptor_paths.append(nested)
            continue
        if path.name == "descriptor.json" and path.exists() and not _connector_descriptor_is_template(path):
            descriptor_paths.append(path)
    seen: set[Path] = set()
    result: list[Path] = []
    for path in descriptor_paths:
        if path in seen:
            continue
        seen.add(path)
        result.append(path)
    return result


def _connector_descriptor_is_template(path: Path) -> bool:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return False
    metadata = data.get("metadata") if isinstance(data, dict) else {}
    return isinstance(metadata, dict) and metadata.get("template") is True


def _load_connector_descriptor(path: Path) -> ExternalConnectorDescriptor:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"Connector descriptor must be an object: {path}")
    security = data.get("security") or {}
    if not isinstance(security, dict):
        raise ValueError("Connector descriptor field security must be an object")
    health = data.get("health") or {}
    if not isinstance(health, dict):
        raise ValueError("Connector descriptor field health must be an object")
    return ExternalConnectorDescriptor(
        connector_id=_required_descriptor_str(data, "connector_id"),
        domain=_optional_descriptor_str(data, "domain"),
        kind=_required_descriptor_str(data, "kind"),
        version=_optional_descriptor_str(data, "version") or "0.1.0",
        descriptor_schema_version=_optional_descriptor_str(data, "descriptor_schema_version") or "1",
        capabilities=_descriptor_capabilities(data.get("capabilities")),
        execution_mode=_optional_descriptor_str(data, "execution_mode") or "stub",
        trust_level=_optional_descriptor_str(data, "trust_level") or "untrusted_local",
        config_ref=_optional_descriptor_str(data, "config_ref"),
        app_scope=_descriptor_string_list(data.get("app_scope"), field_name="app_scope"),
        security=dict(security),
        health=dict(health),
        metadata=dict(data.get("metadata") or {}),
        min_harnessos_version=_optional_descriptor_str(data, "min_harnessos_version") or "",
        target_harnessos_version=_optional_descriptor_str(data, "target_harnessos_version") or "",
        descriptor_path=str(path),
    )


def _external_connector_health_checker(descriptor: ExternalConnectorDescriptor) -> Callable[[ConnectorRegistry], ConnectorHealth]:
    def check(_registry: ConnectorRegistry) -> ConnectorHealth:
        blocked, degraded, warnings = _connector_version_compatibility(descriptor)
        required_dependencies = _descriptor_string_list(
            descriptor.health.get("required_dependencies"),
            field_name="health.required_dependencies",
        )
        optional_dependencies = _descriptor_string_list(
            descriptor.health.get("optional_dependencies"),
            field_name="health.optional_dependencies",
        )
        missing_required = [
            dependency for dependency in required_dependencies if not _static_dependency_available(dependency)
        ]
        missing_optional = [
            dependency for dependency in optional_dependencies if not _static_dependency_available(dependency)
        ]
        if missing_required:
            blocked.extend(f"required_dependency:{dependency}" for dependency in missing_required)
        if missing_optional:
            degraded.extend(f"optional_dependency:{dependency}" for dependency in missing_optional)
            warnings.extend(f"Optional dependency is missing: {dependency}" for dependency in missing_optional)
        details = {
            "descriptor_path": descriptor.descriptor_path,
            "descriptor_schema_version": descriptor.descriptor_schema_version,
            "execution_mode": descriptor.execution_mode,
            "health_mode": descriptor.health.get("mode", "static"),
            "blocked_dependencies": blocked,
            "degraded_dependencies": degraded,
            "compatibility_warnings": warnings,
        }
        if blocked:
            return ConnectorHealth(
                status="blocked",
                message="Connector descriptor is blocked by incompatible versions or missing required dependencies.",
                details=details,
            )
        if degraded:
            return ConnectorHealth(
                status="degraded",
                message="Connector descriptor is available with compatibility warnings.",
                details=details,
            )
        return ConnectorHealth(
            status=str(descriptor.health.get("status") or "available"),
            message=str(descriptor.health.get("message") or "Static connector descriptor is available."),
            details=details,
        )

    return check


def _external_connector_record_factory(
    descriptor: ExternalConnectorDescriptor,
) -> Callable[[ConnectorRegistry, ConnectorHealth], ConnectorRecord]:
    def build(_registry: ConnectorRegistry, health: ConnectorHealth) -> ConnectorRecord:
        return ConnectorRecord(
            connector_id=descriptor.connector_id,
            kind=descriptor.kind,
            domain=descriptor.domain,
            version=descriptor.version,
            health=health.status,
            trust_level=descriptor.trust_level,
            execution_mode=descriptor.execution_mode,
            capabilities={
                **descriptor.capabilities,
                "descriptor_schema_version": descriptor.descriptor_schema_version,
                "health_message": health.message,
            },
            config_ref=descriptor.config_ref,
            secret_ref=None,
            app_scope=list(descriptor.app_scope),
            allowed_commands=_descriptor_string_list(
                descriptor.security.get("allowed_commands"),
                field_name="security.allowed_commands",
            ),
            allowed_paths=_descriptor_string_list(
                descriptor.security.get("allowed_paths"),
                field_name="security.allowed_paths",
            ),
            allowed_network_hosts=_descriptor_string_list(
                descriptor.security.get("allowed_network_hosts"),
                field_name="security.allowed_network_hosts",
            ),
            network_policy=str(descriptor.security.get("network_policy") or "none"),
            tool_risk_defaults=dict(descriptor.security.get("tool_risk_defaults") or {}),
            requires_approval_for=_descriptor_string_list(
                descriptor.security.get("requires_approval_for"),
                field_name="security.requires_approval_for",
            ),
            metadata={
                **dict(descriptor.metadata),
                "descriptor_path": descriptor.descriptor_path,
                "min_harnessos_version": descriptor.min_harnessos_version,
                "target_harnessos_version": descriptor.target_harnessos_version,
                "health_details": health.details,
            },
        )

    return build


def _connector_version_compatibility(descriptor: ExternalConnectorDescriptor) -> tuple[list[str], list[str], list[str]]:
    blocked: list[str] = []
    degraded: list[str] = []
    warnings: list[str] = []
    if descriptor.descriptor_schema_version not in SUPPORTED_CONNECTOR_DESCRIPTOR_SCHEMA_VERSIONS:
        blocked.append(f"descriptor_schema:{descriptor.descriptor_schema_version}")
    if descriptor.min_harnessos_version and _compare_versions(descriptor.min_harnessos_version, HARNESSOS_VERSION) > 0:
        blocked.append(f"min_harnessos_version:{descriptor.min_harnessos_version}")
    if descriptor.target_harnessos_version and descriptor.target_harnessos_version != HARNESSOS_VERSION:
        degraded.append(f"target_harnessos_version:{descriptor.target_harnessos_version}")
        warnings.append(
            f"Connector target_harnessos_version {descriptor.target_harnessos_version} differs from harnessOS {HARNESSOS_VERSION}."
        )
    return blocked, degraded, warnings


def _static_dependency_available(dependency: str) -> bool:
    if dependency == "present":
        return True
    if dependency.startswith("command:"):
        return shutil.which(dependency.removeprefix("command:")) is not None
    if dependency.startswith("path:"):
        return Path(dependency.removeprefix("path:")).expanduser().exists()
    return False


def _required_descriptor_str(data: dict[str, Any], field_name: str) -> str:
    value = data.get(field_name)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"Connector descriptor field {field_name} is required")
    return value


def _optional_descriptor_str(data: dict[str, Any], field_name: str) -> Optional[str]:
    value = data.get(field_name)
    if value is None:
        return None
    if not isinstance(value, str):
        raise ValueError(f"Connector descriptor field {field_name} must be a string")
    return value


def _descriptor_string_list(value: Any, *, field_name: str) -> list[str]:
    if value is None:
        return []
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise ValueError(f"Connector descriptor field {field_name} must be a list of strings")
    return list(value)


def _descriptor_capabilities(value: Any) -> dict[str, Any]:
    if value is None:
        return {"capabilities": []}
    if isinstance(value, list) and all(isinstance(item, str) for item in value):
        return {"capabilities": list(value)}
    if isinstance(value, dict):
        return dict(value)
    raise ValueError("Connector descriptor field capabilities must be a list or object")


def _compare_versions(left: str, right: str) -> int:
    left_parts = _version_parts(left)
    right_parts = _version_parts(right)
    if left_parts > right_parts:
        return 1
    if left_parts < right_parts:
        return -1
    return 0


def _version_parts(value: str) -> tuple[int, int, int]:
    parts = value.split(".")
    parsed: list[int] = []
    for item in parts[:3]:
        digits = ""
        for char in item:
            if not char.isdigit():
                break
            digits += char
        parsed.append(int(digits or "0"))
    while len(parsed) < 3:
        parsed.append(0)
    return tuple(parsed[:3])


def _host_from_url(url: Optional[str]) -> Optional[str]:
    if not url:
        return None
    parsed = urlparse(url)
    return parsed.netloc or None

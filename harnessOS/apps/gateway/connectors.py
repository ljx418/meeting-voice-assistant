"""Connector registry used by the gateway control plane."""

from __future__ import annotations

import os
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional
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
from core.services import CoreAppService


MEETING_VOICE_MCP_CONNECTOR_ID = "meeting_voice_mcp"
FUNASR_MCP_CONNECTOR_ID = "funasr_mcp"
DATA_SERVICE_MCP_CONNECTOR_ID = "data_service_mcp"
REMOTE_COMFYUI_CONNECTOR_ID = "remote_comfyui"


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
    ) -> None:
        self.core_service = core_service
        self.meeting_config = meeting_config or get_meeting_mcp_config()
        self.funasr_config = funasr_config or get_funasr_mcp_config()
        self.data_service_config = data_service_config or get_data_service_mcp_config()
        self.comfyui_config = comfyui_config or get_comfyui_config()
        self.register_default_connectors()

    def register_default_connectors(self) -> None:
        """Register built-in connector descriptors."""
        self.refresh_health(MEETING_VOICE_MCP_CONNECTOR_ID)
        self.refresh_health(FUNASR_MCP_CONNECTOR_ID)
        self.refresh_health(DATA_SERVICE_MCP_CONNECTOR_ID)
        self.refresh_health(REMOTE_COMFYUI_CONNECTOR_ID)

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
        if connector_id == MEETING_VOICE_MCP_CONNECTOR_ID:
            health = self._check_meeting_mcp_health()
            record = self._meeting_mcp_record(health)
        elif connector_id == FUNASR_MCP_CONNECTOR_ID:
            health = self._check_funasr_mcp_health()
            record = self._funasr_mcp_record(health)
        elif connector_id == DATA_SERVICE_MCP_CONNECTOR_ID:
            health = self._check_data_service_mcp_health()
            record = self._data_service_mcp_record(health)
        elif connector_id == REMOTE_COMFYUI_CONNECTOR_ID:
            health = self._check_remote_comfyui_health()
            record = self._remote_comfyui_record(health)
        else:
            raise LookupError(f"Connector not found: {connector_id}")
        self.core_service.save_connector(record)
        return {
            "connector": record.model_dump(mode="json"),
            "health": health.to_dict(),
        }

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
        tools = [
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
                "tools": tools,
                "resources": [
                    "data_service://summary",
                    "data_service://layout",
                    "data_service://build-status",
                    "data_service://quality-report",
                ],
                "prompts": ["knowledge_lifecycle_runbook", "knowledge_quality_review"],
                "health_message": health.message,
                "execution_enabled": config.execution == "stdio",
                "external_agent_guide": (
                    "/Users/Zhuanz/Desktop/workspace/meeting-voice-assistant/"
                    "docs/data_service/MCP-EXTERNAL-AGENT-GUIDE.md"
                ),
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


def _host_from_url(url: Optional[str]) -> Optional[str]:
    if not url:
        return None
    parsed = urlparse(url)
    return parsed.netloc or None

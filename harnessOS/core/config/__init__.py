"""
Configuration management for harnessOS.

Loads settings from environment variables and .env files.
"""

import os
from functools import lru_cache
from pathlib import Path
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


def _preferred_meeting_backend_python() -> str:
    """Prefer the backend-managed Python env when it exists."""
    candidate = Path("/Users/Zhuanz/Desktop/workspace/meeting-voice-assistant/backend/venv312/bin/python")
    return str(candidate) if candidate.exists() else "python3"


def _preferred_voice_service_python() -> str:
    """Prefer the voice-service Python env for FunASR MCP when it exists."""
    candidate = Path("/Users/Zhuanz/Desktop/workspace/voice_service/.venv/bin/python")
    return str(candidate) if candidate.exists() else "python3"


def _preferred_data_service_python() -> str:
    """Prefer the data-service Python env when it exists."""
    candidate = Path("/Users/Zhuanz/Desktop/workspace/data_service/backend/.venv/bin/python")
    return str(candidate) if candidate.exists() else "python3"


class LLMConfig(BaseSettings):
    """LLM provider configuration."""
    provider: str = Field(default="deepseek", description="LLM provider (deepseek, openai, anthropic)")
    api_key: Optional[str] = Field(default=None, description="API key for the LLM provider")
    model: str = Field(default="deepseek-chat", description="Model name")
    base_url: Optional[str] = Field(default=None, description="Base URL for API (for proxies)")

    model_config = SettingsConfigDict(env_prefix="LLM_", extra="ignore")


class DeepAgentsConfig(BaseSettings):
    """Deep Agents configuration."""
    model: str = Field(default="deepseek/deepseek-chat", description="Deep Agents model")
    max_concurrent_agents: int = Field(default=5, description="Max concurrent agents")
    agent_timeout: int = Field(default=300, description="Agent timeout in seconds")

    model_config = SettingsConfigDict(env_prefix="DEEP_AGENTS_", extra="ignore")


class ServerConfig(BaseSettings):
    """Server configuration."""
    host: str = Field(default="0.0.0.0", description="Server host")
    port: int = Field(default=8000, description="Server port")
    cors_origins: list[str] = Field(
        default_factory=lambda: ["http://localhost:5173", "http://localhost:3000"],
        description="Allowed CORS origins"
    )

    model_config = SettingsConfigDict(env_prefix="API_", extra="ignore")


class MemoryConfig(BaseSettings):
    """Memory system configuration."""
    enabled: bool = Field(default=True, description="Enable memory system")
    storage_path: str = Field(default="./data/memory.json", description="Memory storage path")

    model_config = SettingsConfigDict(env_prefix="MEMORY_", extra="ignore")


class WorkspaceConfig(BaseSettings):
    """Workspace configuration."""
    path: str = Field(default="./workspace", description="Workspace directory path")

    model_config = SettingsConfigDict(env_prefix="WORKSPACE_", extra="ignore")


class MeetingMcpConfig(BaseSettings):
    """Meeting MCP integration configuration."""
    cwd: str = Field(
        default="/Users/Zhuanz/Desktop/workspace/meeting-voice-assistant/backend",
        description="Working directory for the meeting MCP server",
    )
    command: str = Field(
        default_factory=_preferred_meeting_backend_python,
        description="Command used to start the meeting MCP server",
    )
    args: str = Field(
        default="-m app.meeting_mcp.mcp_stdio",
        description="Space-separated arguments used to start the meeting MCP server",
    )
    output_root: Optional[str] = Field(default=None, description="Optional Meeting MCP artifact output root")
    audio_dir: str = Field(
        default="/Users/Zhuanz/Desktop/workspace/音频资料",
        description="Directory containing real audio files used for Phase1 acceptance",
    )
    default_engine: str = Field(default="funasr", description="Default ASR engine for meeting acceptance")
    default_language: str = Field(default="en", description="Default language hint for meeting acceptance")
    request_timeout: int = Field(default=3600, description="Meeting MCP request timeout in seconds")

    model_config = SettingsConfigDict(env_prefix="HARNESS_MEETING_MCP_", extra="ignore")

    @property
    def argv(self) -> list[str]:
        """Return parsed MCP server arguments."""
        return [item for item in self.args.split(" ") if item]

    def model_post_init(self, __context) -> None:
        """Support the earlier acceptance env name as a compatibility alias."""
        if "HARNESS_MEETING_MCP_AUDIO_DIR" not in os.environ and "HARNESS_MEETING_AUDIO_DIR" in os.environ:
            self.audio_dir = os.environ["HARNESS_MEETING_AUDIO_DIR"]


class FunASRMcpConfig(BaseSettings):
    """FunASR MCP integration configuration."""

    cwd: str = Field(
        default="/Users/Zhuanz/Desktop/workspace/voice_service",
        description="Working directory for the FunASR MCP server",
    )
    command: str = Field(
        default_factory=_preferred_voice_service_python,
        description="Command used to start the FunASR MCP server",
    )
    args: str = Field(
        default="-m funasr_service.mcp_stdio",
        description="Space-separated arguments used to start the FunASR MCP server",
    )
    execution: str = Field(default="contract_stub", description="Execution mode: contract_stub or stdio")
    endpoint: str = Field(default="http://localhost:8001", description="FunASR HTTP service endpoint")
    audio_roots: str = Field(
        default="/Users/Zhuanz/Desktop/workspace/音频资料:/tmp",
        description="Colon-separated local roots allowed for FunASR MCP file inputs",
    )
    request_timeout: int = Field(default=3600, description="FunASR MCP request timeout in seconds")
    max_file_size_mb: int = Field(default=500, description="Maximum local audio file size in MB")

    model_config = SettingsConfigDict(env_prefix="HARNESS_FUNASR_MCP_", extra="ignore")

    @property
    def argv(self) -> list[str]:
        """Return parsed MCP server arguments."""
        return [item for item in self.args.split(" ") if item]


class DataServiceMcpConfig(BaseSettings):
    """Data Service MCP integration configuration."""

    cwd: str = Field(
        default="/Users/Zhuanz/Desktop/workspace/data_service/backend",
        description="Working directory for the Data Service MCP server",
    )
    command: str = Field(
        default_factory=_preferred_data_service_python,
        description="Command used to start the Data Service MCP server",
    )
    args: str = Field(
        default="-m data_service.mcp_stdio",
        description="Space-separated arguments used to start the Data Service MCP server",
    )
    execution: str = Field(
        default="contract_stub",
        description="Execution mode: contract_stub or stdio",
    )
    request_timeout: int = Field(default=3600, description="Data Service MCP request timeout in seconds")
    workspace_root: Optional[str] = Field(default=None, description="Managed workspace root for Data Service")
    allowed_workspace_roots: Optional[str] = Field(default=None, description="Allowed workspace roots")
    allowed_source_roots: Optional[str] = Field(default=None, description="Allowed source roots")

    model_config = SettingsConfigDict(env_prefix="HARNESS_DATA_SERVICE_MCP_", extra="ignore")

    @property
    def argv(self) -> list[str]:
        """Return parsed MCP server arguments."""
        return [item for item in self.args.split(" ") if item]


class ComfyUIConfig(BaseSettings):
    """Remote ComfyUI connector configuration."""

    base_url: Optional[str] = Field(default=None, description="Base URL for a remote ComfyUI server")
    request_timeout: int = Field(default=300, description="ComfyUI request timeout in seconds")

    model_config = SettingsConfigDict(env_prefix="HARNESS_COMFYUI_", extra="ignore")


class AppConfig(BaseSettings):
    """Main application configuration."""
    llm: LLMConfig = Field(default_factory=LLMConfig)
    deep_agents: DeepAgentsConfig = Field(default_factory=DeepAgentsConfig)
    server: ServerConfig = Field(default_factory=ServerConfig)
    memory: MemoryConfig = Field(default_factory=MemoryConfig)
    workspace: WorkspaceConfig = Field(default_factory=WorkspaceConfig)
    meeting_mcp: MeetingMcpConfig = Field(default_factory=MeetingMcpConfig)
    funasr_mcp: FunASRMcpConfig = Field(default_factory=FunASRMcpConfig)
    data_service_mcp: DataServiceMcpConfig = Field(default_factory=DataServiceMcpConfig)
    comfyui: ComfyUIConfig = Field(default_factory=ComfyUIConfig)

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_app_config() -> AppConfig:
    """Get cached application configuration."""
    return AppConfig()


def get_llm_config() -> LLMConfig:
    """Get LLM configuration."""
    return get_app_config().llm


def get_deep_agents_config() -> DeepAgentsConfig:
    """Get Deep Agents configuration."""
    return get_app_config().deep_agents


def get_server_config() -> ServerConfig:
    """Get server configuration."""
    return get_app_config().server


def get_meeting_mcp_config() -> MeetingMcpConfig:
    """Get Meeting MCP integration configuration."""
    return get_app_config().meeting_mcp


def get_funasr_mcp_config() -> FunASRMcpConfig:
    """Get FunASR MCP integration configuration."""
    return get_app_config().funasr_mcp


def get_data_service_mcp_config() -> DataServiceMcpConfig:
    """Get Data Service MCP integration configuration."""
    return get_app_config().data_service_mcp


def get_comfyui_config() -> ComfyUIConfig:
    """Get remote ComfyUI connector configuration."""
    return get_app_config().comfyui

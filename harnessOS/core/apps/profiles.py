"""Application profiles for multi-app harnessOS deployments."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass(frozen=True)
class AppProfile:
    """Configuration boundary for one app using the shared Core."""

    app_id: str
    display_name: str
    domain: str
    default_pack: str
    connector_refs: tuple[str, ...] = ()
    runtime_adapter: str = "auto"
    default_project_id: Optional[str] = None
    default_workspace_id: Optional[str] = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable profile view."""
        return {
            "app_id": self.app_id,
            "display_name": self.display_name,
            "domain": self.domain,
            "default_pack": self.default_pack,
            "connector_refs": list(self.connector_refs),
            "runtime_adapter": self.runtime_adapter,
            "default_project_id": self.default_project_id,
            "default_workspace_id": self.default_workspace_id,
            "metadata": dict(self.metadata),
        }


class AppRegistry:
    """In-memory registry for app profiles."""

    def __init__(self, profiles: Optional[list[AppProfile]] = None) -> None:
        self._profiles: dict[str, AppProfile] = {}
        for profile in profiles or []:
            self.register(profile)

    def register(self, profile: AppProfile) -> None:
        """Register one app profile."""
        if not profile.app_id.strip():
            raise ValueError("app_id is required")
        self._profiles[profile.app_id] = profile

    def get(self, app_id: str) -> AppProfile:
        """Return one app profile."""
        try:
            return self._profiles[app_id]
        except KeyError as exc:
            raise KeyError(f"Unknown app_id: {app_id}") from exc

    def get_optional(self, app_id: str) -> Optional[AppProfile]:
        """Return one app profile or None."""
        return self._profiles.get(app_id)

    def list_profiles(self) -> list[dict[str, Any]]:
        """Return registered app profiles."""
        return [profile.to_dict() for profile in sorted(self._profiles.values(), key=lambda item: item.app_id)]


def build_default_app_registry() -> AppRegistry:
    """Build the built-in app profile registry."""
    return AppRegistry(
        [
            AppProfile(
                app_id="meeting",
                display_name="会议助手",
                domain="meeting",
                default_pack="meeting",
                connector_refs=("meeting_voice_mcp", "funasr_mcp"),
            ),
            AppProfile(
                app_id="knowledge",
                display_name="个人知识库",
                domain="knowledge",
                default_pack="knowledge",
                connector_refs=("data_service_mcp",),
            ),
            AppProfile(
                app_id="interview",
                display_name="应聘助手",
                domain="interview",
                default_pack="interview",
                connector_refs=(),
                metadata={"status": "planned_v3_1"},
            ),
            AppProfile(
                app_id="investment",
                display_name="投资助手",
                domain="investment",
                default_pack="investment",
                connector_refs=(),
                metadata={"status": "planned_v3_2"},
            ),
            AppProfile(
                app_id="video_studio",
                display_name="AI 文生视频工作流",
                domain="video_studio",
                default_pack="video_studio",
                connector_refs=("remote_comfyui",),
                metadata={"status": "planned_v3_3"},
            ),
        ]
    )

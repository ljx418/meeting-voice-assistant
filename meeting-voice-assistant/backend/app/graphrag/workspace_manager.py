"""Workspace Manager - Session-based GraphRAG workspace lifecycle management.

Each meeting session gets its own isolated workspace with:
- Independent input/ directory
- Independent output/ directory
- Independent graphrag.db database
- Independent settings.yaml

This ensures complete data isolation between sessions.
"""

import logging
import shutil
from pathlib import Path
from typing import Optional
from uuid import uuid4

from .config import settings

logger = logging.getLogger(__name__)


class WorkspaceManager:
    """Manages session-based GraphRAG workspaces."""

    def __init__(self, base_dir: Optional[Path] = None):
        """Initialize workspace manager.

        Args:
            base_dir: Base directory for all session workspaces.
                     Defaults to settings.GRAPHRAG_WORKSPACE
        """
        self.base_dir = base_dir or settings.GRAPHRAG_WORKSPACE
        self._workspaces: dict[str, Path] = {}  # session_id -> workspace_path

    def _get_workspace_name(self, session_id: str) -> str:
        """Generate workspace directory name for a session."""
        return f"session_{session_id}"

    def _get_default_settings(self) -> str:
        """Generate default GraphRAG settings.yaml content."""
        return """encoding_model: cl100k_base
skip_workflow: false

# LLM 配置
llm:
  description: DashScope LLM
  configuration:
    type: openai_chat
    api_key: ${GRAPHRAG_LLM_API_KEY}
    model: qwen-plus
    api_base: https://dashscope.aliyuncs.com

# 嵌入模型配置
embeddings:
  description: DashScope Embeddings
  configuration:
    type: openai_text
    api_key: ${GRAPHRAG_LLM_API_KEY}
    model: text-embedding-v3
    api_base: https://dashscope.aliyuncs.com

# 存储配置
storage:
  type: file
  path: ./output

# 报告配置
reporting:
  type: file
  path: ./output/reports

# 搜索配置
search:
  type: local
  local:
    mode: local
    vectorizer: embed
    max_tokens: 7500
    temperature: 0.0
"""

    def create_workspace(self, session_id: str) -> Path:
        """Create a new isolated workspace for a session.

        Args:
            session_id: Unique session identifier

        Returns:
            Path to the created workspace directory

        Raises:
            FileExistsError: If workspace already exists for this session
        """
        workspace_path = self.base_dir / self._get_workspace_name(session_id)

        if workspace_path.exists():
            logger.warning(f"Workspace already exists for session {session_id}, returning existing")
            self._workspaces[session_id] = workspace_path
            return workspace_path

        # Create workspace structure
        workspace_path.mkdir(parents=True, exist_ok=True)
        (workspace_path / "input").mkdir(exist_ok=True)
        (workspace_path / "output").mkdir(exist_ok=True)

        # Create settings.yaml
        settings_file = workspace_path / "settings.yaml"
        settings_file.write_text(self._get_default_settings())

        # Store in memory
        self._workspaces[session_id] = workspace_path

        logger.info(f"Created workspace for session {session_id}: {workspace_path}")
        return workspace_path

    def get_workspace(self, session_id: str) -> Path:
        """Get workspace path for a session.

        If workspace doesn't exist, creates it automatically.

        Args:
            session_id: Session identifier

        Returns:
            Path to the workspace directory
        """
        if session_id not in self._workspaces:
            workspace_path = self.base_dir / self._get_workspace_name(session_id)
            if workspace_path.exists():
                self._workspaces[session_id] = workspace_path
            else:
                # Auto-create if doesn't exist
                workspace_path = self.create_workspace(session_id)
        return self._workspaces[session_id]

    def workspace_exists(self, session_id: str) -> bool:
        """Check if workspace exists for a session."""
        workspace_path = self.base_dir / self._get_workspace_name(session_id)
        return workspace_path.exists()

    def cleanup_workspace(self, session_id: str) -> dict:
        """Clean up workspace for a session.

        Removes the entire workspace directory including all indexed data.

        Args:
            session_id: Session identifier

        Returns:
            dict with cleanup results (deleted_files, deleted_dirs)
        """
        workspace_path = self.base_dir / self._get_workspace_name(session_id)

        deleted_files = 0
        deleted_dirs = 0

        if workspace_path.exists():
            try:
                # Count items before deletion
                deleted_files = len(list(workspace_path.rglob("*.*")))
                deleted_dirs = len([d for d in workspace_path.rglob("*") if d.is_dir()])

                # Remove workspace directory
                shutil.rmtree(workspace_path)

                # Remove from memory
                self._workspaces.pop(session_id, None)

                logger.info(f"Cleaned up workspace for session {session_id}")
            except Exception as e:
                logger.error(f"Failed to cleanup workspace {session_id}: {e}")
                raise

        return {
            "session_id": session_id,
            "deleted_files": deleted_files,
            "deleted_dirs": deleted_dirs,
            "workspace_path": str(workspace_path),
        }

    def list_workspaces(self) -> list[dict]:
        """List all existing workspaces.

        Returns:
            List of workspace info dicts with session_id and path
        """
        workspaces = []
        if self.base_dir.exists():
            for item in self.base_dir.iterdir():
                if item.is_dir() and item.name.startswith("session_"):
                    session_id = item.name.replace("session_", "")
                    workspaces.append({
                        "session_id": session_id,
                        "path": str(item),
                        "exists": item.exists(),
                    })
        return workspaces

    def generate_session_id(self) -> str:
        """Generate a new unique session ID.

        Returns:
            New session ID string
        """
        return str(uuid4())[:12]  # Short UUID for readability


# Global singleton instance
_workspace_manager: Optional[WorkspaceManager] = None


def get_workspace_manager() -> WorkspaceManager:
    """Get the global WorkspaceManager instance."""
    global _workspace_manager
    if _workspace_manager is None:
        _workspace_manager = WorkspaceManager()
    return _workspace_manager


def create_session_workspace(session_id: str) -> Path:
    """Convenience function to create a workspace for a session."""
    return get_workspace_manager().create_workspace(session_id)


def get_session_workspace(session_id: str) -> Path:
    """Convenience function to get workspace for a session."""
    return get_workspace_manager().get_workspace(session_id)


def cleanup_session_workspace(session_id: str) -> dict:
    """Convenience function to cleanup workspace for a session."""
    return get_workspace_manager().cleanup_workspace(session_id)
"""
Session management for CLI.
"""

import os
import uuid
from datetime import datetime
from typing import Any, Optional

from core.runtime_adapter import create_harness_agent
from tools import get_builtin_tools


def _default_model() -> str:
    """Resolve the default CLI model from current project environment."""
    return (
        os.getenv("LLM_MODEL")
        or os.getenv("DEEP_AGENTS_MODEL")
        or os.getenv("OPENHARNESS_MODEL")
        or "deepseek-chat"
    )


class CLISession:
    """Manages a CLI session with the harnessOS agent."""

    def __init__(self, model: Optional[str] = None):
        """Initialize CLI session.

        Args:
            model: LLM model to use. Defaults to environment configuration.
        """
        self.session_id = str(uuid.uuid4())
        self.created_at = datetime.now()
        self.messages: list = []
        self.model = model or _default_model()

        # Initialize agent with tools
        tools = get_builtin_tools()
        self.agent = create_harness_agent(model=self.model, tools=tools)

    def run(self, user_input: str) -> dict:
        """Run user input through the agent.

        Args:
            user_input: User's input string

        Returns:
            Response dict with status and content
        """
        # Add user message to history
        self.messages.append({
            "role": "user",
            "content": user_input,
            "timestamp": datetime.now().isoformat()
        })

        try:
            # Invoke agent
            result = self.agent.invoke(user_input)

            # Handle both dict responses and object responses
            if isinstance(result, dict):
                response_content = result.get("content", str(result))
                status = result.get("status", "success")
            else:
                response_content = str(result)
                status = "success"

            # Add response to history
            self.messages.append({
                "role": "assistant",
                "content": response_content,
                "timestamp": datetime.now().isoformat()
            })

            return {
                "status": status,
                "content": response_content,
                "session_id": self.session_id
            }

        except Exception as e:
            return {
                "status": "error",
                "content": f"Error: {str(e)}",
                "session_id": self.session_id
            }

    def get_history(self) -> list:
        """Get message history for this session."""
        return self.messages

    def clear_history(self) -> None:
        """Clear message history."""
        self.messages = []

"""
Simple agent runtime for harnessOS Phase 0.

This module provides a lightweight agent runtime that demonstrates
the harnessOS architecture without requiring deepagents installation.

For production, this will be replaced with actual Deep Agents integration.
"""

import os
import re
from typing import Any, Dict, List, Optional

from openai import OpenAI


class SimpleAgent:
    """A simple agent that uses LLM with tool calling capability."""

    def __init__(
        self,
        model: str = "deepseek/deepseek-chat",
        tools: Optional[List[Dict[str, Any]]] = None,
        system_prompt: str = "You are harnessOS, a helpful AI assistant.",
    ):
        """Initialize the agent.

        Args:
            model: LLM model to use
            tools: List of tool definitions
            system_prompt: System prompt for the agent
        """
        self.model_name = model
        self.tools = tools or []
        self.system_prompt = system_prompt
        self.messages: List[Dict[str, str]] = []
        self.api_key = _resolve_api_key()
        self.base_url = _resolve_base_url(model)

        if self.api_key:
            self.client = OpenAI(
                api_key=self.api_key,
                base_url=self.base_url,
            )
            self._has_api = True
        else:
            self._has_api = False

    def invoke(self, user_input: str) -> Dict[str, Any]:
        """Invoke the agent with user input.

        Args:
            user_input: User's input string

        Returns:
            Response dict
        """
        if not self._has_api:
            return self._mock_response(user_input)

        # Build messages
        messages = [{"role": "system", "content": self.system_prompt}]

        # Add conversation history
        for msg in self.messages:
            messages.append({"role": msg["role"], "content": msg["content"]})

        # Add current user input
        messages.append({"role": "user", "content": user_input})

        try:
            # Call LLM
            response = self.client.chat.completions.create(
                model=_normalize_model_name(self.model_name),
                messages=messages,
                temperature=0.7,
            )
            content = _strip_think_blocks(response.choices[0].message.content or "")

            # Save to history
            self.messages.append({"role": "user", "content": user_input})
            self.messages.append({"role": "assistant", "content": content})

            return {
                "status": "success",
                "content": content,
                "model": self.model_name,
            }

        except Exception as e:
            return {
                "status": "error",
                "content": f"Error calling LLM: {str(e)}",
                "model": self.model_name,
            }

    def _mock_response(self, user_input: str) -> Dict[str, Any]:
        """Generate a mock response when no API key is available.

        Args:
            user_input: User's input string

        Returns:
            Mock response
        """
        user_lower = user_input.lower()

        if any(word in user_lower for word in ["hello", "hi", "hey", "help"]):
            response = (
                "Hello! I'm harnessOS Phase 0 Shell.\n\n"
                "I can help you with:\n"
                "- Managing files (workspace_ls, workspace_read_file, workspace_write_file)\n"
                "- Knowledge base (kb_search, kb_ingest)\n"
                "- Saving artifacts (artifact_save)\n\n"
                "Note: No LLM API key detected. Set DEEPSEEK_API_KEY to enable full AI capabilities.\n"
                "Try: export DEEPSEEK_API_KEY='your-key'"
            )
        elif "workspace" in user_lower:
            response = (
                "Workspace tools available:\n"
                "- workspace_ls(directory='.') - List files\n"
                "- workspace_read_file(file_path='path') - Read file\n"
                "- workspace_write_file(file_path='path', content='text') - Write file"
            )
        elif "kb_" in user_lower or "knowledge" in user_lower:
            response = (
                "Knowledge base tools available:\n"
                "- kb_search(query='text') - Search knowledge\n"
                "- kb_ingest(document='text') - Add document\n"
                "- kb_list() - List all documents"
            )
        elif "artifact" in user_lower:
            response = (
                "Artifact tools available:\n"
                "- artifact_save(name='name', content='text') - Save artifact\n"
                "- artifact_list() - List artifacts\n"
                "- artifact_get(id) - Get artifact"
            )
        else:
            response = (
                f"You said: {user_input}\n\n"
                "I'm running in demo mode (no LLM API key detected).\n"
                "Try asking about 'workspace', 'knowledge', or 'artifact' tools.\n"
                "Or set DEEPSEEK_API_KEY for full functionality."
            )

        # Save to history
        self.messages.append({"role": "user", "content": user_input})
        self.messages.append({"role": "assistant", "content": response})

        return {
            "status": "success",
            "content": response,
            "mode": "mock",
        }


def create_simple_agent(
    model: str = "deepseek-chat",
    tools: Optional[List[Dict[str, Any]]] = None,
) -> SimpleAgent:
    """Create a simple harnessOS agent.

    Args:
        model: Model identifier
        tools: Tool definitions (currently unused in simple mode)

    Returns:
        SimpleAgent instance
    """
    system_prompt = """You are harnessOS, an AI assistant built on a multi-agent architecture.

You have access to tools for:
- File operations (workspace_ls, workspace_read_file, workspace_write_file)
- Knowledge management (kb_search, kb_ingest)
- Artifact storage (artifact_save)

Always be helpful, concise, and professional."""
    return SimpleAgent(model=model, tools=tools, system_prompt=system_prompt)


def _resolve_api_key() -> str:
    """Resolve an API key across harnessOS and migrated OpenHarness env names."""
    return (
        os.getenv("DEEPSEEK_API_KEY")
        or os.getenv("MINIMAX_API_KEY")
        or os.getenv("OPENAI_API_KEY")
        or os.getenv("OPENHARNESS_API_KEY")
        or os.getenv("ANTHROPIC_API_KEY")
        or ""
    )


def _resolve_base_url(model: str) -> Optional[str]:
    """Resolve an OpenAI-compatible base URL for the selected model."""
    configured = (
        os.getenv("OPENHARNESS_BASE_URL")
        or os.getenv("OPENAI_BASE_URL")
        or os.getenv("LLM_BASE_URL")
    )
    if configured:
        return configured.rstrip("/")

    model_lower = model.lower()
    if "minimax" in model_lower:
        return "https://api.minimax.chat/v1"
    if "deepseek" in model_lower:
        return "https://api.deepseek.com/v1"
    return None


def _normalize_model_name(model: str) -> str:
    """Convert provider-prefixed model ids into provider API model names."""
    if "/" in model:
        provider, model_name = model.split("/", 1)
        if provider in {"deepseek", "minimax", "openai"}:
            return model_name
    return model


_THINK_RE = re.compile(r"<think>.*?</think>", re.DOTALL)


def _strip_think_blocks(text: str) -> str:
    """Remove inline thinking blocks from provider responses."""
    return _THINK_RE.sub("", text).strip()

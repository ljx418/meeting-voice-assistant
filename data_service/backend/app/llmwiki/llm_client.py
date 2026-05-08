"""LLMWiki LLM provider abstraction."""
import json
import os
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any, Dict, Optional

from .config import LLMWikiConfig


class LLMClientError(RuntimeError):
    """Raised when an LLM request fails."""


@dataclass
class LLMResponse:
    """Normalized LLM response."""

    text: str
    raw: Dict[str, Any]


class BaseLLMClient:
    """Provider interface."""

    def __init__(self, config: LLMWikiConfig):
        self.config = config

    def is_enabled(self) -> bool:
        return False

    def model_name(self) -> str:
        return "null"

    def complete_json(self, system_prompt: str, user_prompt: str) -> LLMResponse:
        raise NotImplementedError


class NullLLMClient(BaseLLMClient):
    """Explicit no-op provider."""

    def complete_json(self, system_prompt: str, user_prompt: str) -> LLMResponse:
        raise LLMClientError("LLM provider is disabled")


class OpenAICompatibleLLMClient(BaseLLMClient):
    """Minimal OpenAI-compatible chat client."""

    def is_enabled(self) -> bool:
        return bool(self.config.llm_api_base and self._api_key())

    def model_name(self) -> str:
        return self.config.llm_model

    def complete_json(self, system_prompt: str, user_prompt: str) -> LLMResponse:
        api_key = self._api_key()
        if not api_key:
            raise LLMClientError(
                f"Missing API key env var: {self.config.llm_api_key_env or '<unset>'}"
            )
        if not self.config.llm_api_base:
            raise LLMClientError("Missing LLM API base")

        payload = {
            "model": self.config.llm_model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": 0.1,
            "response_format": {"type": "json_object"},
        }
        request = urllib.request.Request(
            self.config.llm_api_base.rstrip("/") + "/chat/completions",
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}",
            },
            method="POST",
        )
        last_error: Optional[Exception] = None
        for _ in range(max(1, self.config.llm_max_retries)):
            try:
                with urllib.request.urlopen(request, timeout=self.config.llm_timeout) as response:
                    body = json.loads(response.read().decode("utf-8"))
                text = body["choices"][0]["message"]["content"]
                if not isinstance(text, str):
                    raise LLMClientError("Unexpected response content shape")
                return LLMResponse(text=text, raw=body)
            except (urllib.error.URLError, KeyError, ValueError, LLMClientError) as exc:
                last_error = exc
        raise LLMClientError(str(last_error or "Unknown LLM request failure"))

    def _api_key(self) -> Optional[str]:
        if not self.config.llm_api_key_env:
            return None
        return os.getenv(self.config.llm_api_key_env)


def build_llm_client(config: LLMWikiConfig) -> BaseLLMClient:
    """Create the configured provider."""

    provider = (config.llm_provider or "null").lower()
    if provider in {"http", "openai", "openai-compatible"}:
        return OpenAICompatibleLLMClient(config)
    return NullLLMClient(config)

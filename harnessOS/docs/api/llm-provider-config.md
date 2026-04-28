# LLM Provider Configuration

## Overview

harnessOS supports multiple LLM providers for flexibility and cost optimization. This document describes the provider configuration system.

## Supported Providers

| Provider | Model | Context Window | Vision | Thinking |
|----------|-------|----------------|--------|----------|
| DeepSeek | deepseek-chat, deepseek-coder | 64K | No | Yes |
| MiniMax | MiniMax-M2.1 | 1M | Yes | Yes |
| OpenAI | gpt-4o, gpt-4-turbo | 128K | Yes | No |
| Anthropic | claude-opus-4, claude-sonnet-4 | 200K | Yes | Yes |
| DashScope | qwen-plus, qwen-max | 32K-128K | Yes | Yes |

## Configuration Schema

```yaml
# config.yaml
llm:
  # Default provider
  provider: "deepseek"

  # Provider-specific configuration
  providers:
    deepseek:
      api_key: "${DEEPSEEK_API_KEY}"
      base_url: "https://api.deepseek.com"
      models:
        - name: "deepseek-chat"
          display_name: "DeepSeek V3"
          default: true
        - name: "deepseek-coder"
          display_name: "DeepSeek Coder"

    minimax:
      api_key: "${MINIMAX_API_KEY}"
      base_url: "https://api.minimax.chat"
      models:
        - name: "MiniMax-M2.1"
          display_name: "MiniMax M2.1"
          default: true
          context_window: 1000000

    openai:
      api_key: "${OPENAI_API_KEY}"
      base_url: "https://api.openai.com"
      models:
        - name: "gpt-4o"
          display_name: "GPT-4o"
        - name: "gpt-4-turbo"
          display_name: "GPT-4 Turbo"

    anthropic:
      api_key: "${ANTHROPIC_API_KEY}"
      base_url: "https://api.anthropic.com"
      models:
        - name: "claude-opus-4-7"
          display_name: "Claude Opus 4.7"
        - name: "claude-sonnet-4-6"
          display_name: "Claude Sonnet 4.6"

    dashscope:
      api_key: "${DASHSCOPE_API_KEY}"
      base_url: "https://dashscope.aliyuncs.com"
      models:
        - name: "qwen-plus"
          display_name: "Qwen Plus"
        - name: "qwen-max"
          display_name: "Qwen Max"
```

## Python Configuration

```python
from pydantic import BaseModel
from typing import Optional


class ModelConfig(BaseModel):
    """Configuration for a single model."""
    name: str
    display_name: str
    context_window: int = 64000
    supports_vision: bool = False
    supports_thinking: bool = False
    price_per_1k_input: float = 0.0
    price_per_1k_output: float = 0.0
    default: bool = False


class ProviderConfig(BaseModel):
    """Configuration for an LLM provider."""
    api_key: str
    base_url: str
    models: list[ModelConfig] = []
    extra_headers: dict[str, str] = {}


class LLMConfig(BaseModel):
    """Main LLM configuration."""
    provider: str = "deepseek"
    providers: dict[str, ProviderConfig] = {}
    default_model: Optional[str] = None
```

## Provider Implementation

### DeepSeek

```python
# core/llm/providers/deepseek.py
from openharness.api.openai_client import OpenAICompatibleClient

class DeepSeekProvider:
    """DeepSeek API provider."""

    def __init__(self, api_key: str, base_url: str = "https://api.deepseek.com"):
        self.client = OpenAICompatibleClient(
            api_key=api_key,
            base_url=base_url,
            model_mapping={
                "deepseek-chat": "deepseek-chat",
                "deepseek-coder": "deepseek-coder",
            }
        )

    def create_chat_model(self, model_name: str, **kwargs):
        return self.client.create_chat_model(model_name, **kwargs)
```

### MiniMax

```python
# core/llm/providers/minimax.py
from openharness.api.openai_client import OpenAICompatibleClient

class MiniMaxProvider:
    """MiniMax API provider."""

    def __init__(self, api_key: str, base_url: str = "https://api.minimax.chat"):
        self.client = OpenAICompatibleClient(
            api_key=api_key,
            base_url=base_url,
            model_mapping={
                "MiniMax-M2.1": "MiniMax-M2.1",
            }
        )

    def create_chat_model(self, model_name: str, **kwargs):
        return self.client.create_chat_model(model_name, **kwargs)
```

## Model Factory

```python
# core/llm/factory.py
from typing import Any

class LLMFactory:
    """Factory for creating LLM instances."""

    def __init__(self, config: LLMConfig):
        self.config = config
        self._providers = self._initialize_providers()

    def _initialize_providers(self) -> dict[str, Any]:
        providers = {}
        for name, provider_config in self.config.providers.items():
            if name == "deepseek":
                from core.llm.providers.deepseek import DeepSeekProvider
                providers[name] = DeepSeekProvider(
                    api_key=provider_config.api_key,
                    base_url=provider_config.base_url,
                )
            elif name == "minimax":
                from core.llm.providers.minimax import MiniMaxProvider
                providers[name] = MiniMaxProvider(
                    api_key=provider_config.api_key,
                    base_url=provider_config.base_url,
                )
        return providers

    def create_model(self, provider: str | None = None, model: str | None = None, **kwargs):
        provider = provider or self.config.provider
        model = model or self._get_default_model(provider)
        return self._providers[provider].create_chat_model(model, **kwargs)

    def _get_default_model(self, provider: str) -> str:
        if provider in self._providers:
            for model_config in self.config.providers[provider].models:
                if model_config.default:
                    return model_config.name
        return "default"
```

## Environment Variables

| Variable | Description |
|----------|-------------|
| `DEEPSEEK_API_KEY` | DeepSeek API key |
| `MINIMAX_API_KEY` | MiniMax API key |
| `OPENAI_API_KEY` | OpenAI API key |
| `ANTHROPIC_API_KEY` | Anthropic API key |
| `DASHSCOPE_API_KEY` | DashScope API key |

## Provider-Specific Notes

### DeepSeek
- Supports extended thinking mode for reasoning tasks
- Lower pricing for Coder variant
- Best for: code generation, reasoning tasks

### MiniMax
- 1M token context window
- Excellent for long document processing
- Best for: document analysis, long-context tasks

### DashScope
- Alibaba Cloud service
- Strong Chinese language support
- Best for: multilingual applications

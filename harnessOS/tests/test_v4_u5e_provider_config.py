from pathlib import Path

from core.workflows.v4_u5e_local_document_workflow import load_provider_config


def test_provider_config_prefers_env_local_and_minimax(tmp_path, monkeypatch):
    env = tmp_path / ".env.local"
    env.write_text(
        "\n".join(
            [
                "LLM_PROVIDER=deepseek",
                "V4_U5E_LLM_PROVIDER=minimax",
                "MINIMAX_API_KEY=test-key",
                "MINIMAX_BASE_URL=https://api.minimax.chat/v1",
                "V4_U5E_LLM_MODEL=MiniMax-Test",
                "V4_U5E_REAL_LLM_REQUIRED=true",
            ]
        ),
        encoding="utf-8",
    )
    monkeypatch.chdir(Path.cwd())
    config = load_provider_config(env_files=(str(env),))

    assert config.provider == "minimax"
    assert config.model_ref == "MiniMax-Test"
    assert config.base_url == "https://api.minimax.chat/v1"
    assert config.api_key == "test-key"
    assert config.provider_config_source.endswith(".env.local")
    assert config.real_llm_required is True


def test_provider_config_treats_placeholders_as_missing(tmp_path):
    env = tmp_path / ".env.local"
    env.write_text(
        "V4_U5E_LLM_PROVIDER=minimax\nMINIMAX_API_KEY=your-minimax-api-key-here\nV4_U5E_LLM_MODEL=your-model\n",
        encoding="utf-8",
    )
    config = load_provider_config(env_files=(str(env),))

    assert config.provider == "minimax"
    assert config.api_key == ""
    assert config.model_ref == "MiniMax-M2.1"

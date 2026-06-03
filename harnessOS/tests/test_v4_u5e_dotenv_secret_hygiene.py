from pathlib import Path


def test_env_example_contains_only_placeholders():
    text = Path(".env.example").read_text(encoding="utf-8")

    assert "MINIMAX_API_KEY=your-minimax-api-key-here" in text
    assert "DEEPSEEK_API_KEY=your-deepseek-api-key-here" in text
    assert "sk-" not in text
    assert "V4_U5E_LLM_MODEL=your-minimax-model-ref-here" in text


def test_env_local_is_gitignored():
    text = Path(".gitignore").read_text(encoding="utf-8")

    assert ".env.local" in text

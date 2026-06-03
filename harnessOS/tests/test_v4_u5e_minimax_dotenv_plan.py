from pathlib import Path


PLAN = Path("docs/design/V4.x/v4_u5e_real_llm_local_document_workflow_plan.md")
ACCEPTANCE = Path("docs/design/V4.x/v4_x_unified_experience_acceptance.md")
ENV_EXAMPLE = Path(".env.example")


def test_u5e_plan_uses_minimax_first_with_dotenv_boundary():
    text = PLAN.read_text(encoding="utf-8")

    assert "MiniMax" in text
    assert "MINIMAX_API_KEY" in text
    assert ".env.local" in text
    assert "provider_config_source" in text
    assert "fallback_demo_only 不得作为 real_llm PASS" in text
    assert "不得提交真实 MINIMAX_API_KEY" in text


def test_env_example_has_minimax_placeholders_without_real_key():
    text = ENV_EXAMPLE.read_text(encoding="utf-8")

    assert "LLM_PROVIDER=minimax" in text
    assert "MINIMAX_API_KEY=your-minimax-api-key-here" in text
    assert "MINIMAX_BASE_URL=https://api.minimax.chat/v1" in text
    assert "V4_U5E_LLM_PROVIDER=minimax" in text
    assert "V4_U5E_REAL_LLM_REQUIRED=false" in text
    assert "sk-" not in text


def test_acceptance_requires_minimax_or_openai_compatible_provider_evidence():
    text = ACCEPTANCE.read_text(encoding="utf-8")

    assert "优先使用 MiniMax provider" in text
    assert "OpenAI-compatible provider" in text
    assert "provider_config_source" in text
    assert "不得把缺少 MINIMAX_API_KEY 的场景写成 MiniMax-backed PASS" in text

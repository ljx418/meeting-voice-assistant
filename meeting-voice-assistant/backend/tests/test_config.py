"""
Config 模块测试
"""

import os
import sys
from pathlib import Path

# 将 backend 目录添加到 path
backend_path = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_path))

# 设置测试环境变量
os.environ["ASR_ENGINE"] = "mock"
os.environ["MOCK_ASR_DELAY"] = "0.5"

from app.config import Config


class TestConfig:
    """Config 配置测试"""

    def test_default_values(self):
        """测试默认配置值"""
        config = Config()

        # ASR 配置
        assert config.ASR_ENGINE == "mock"
        assert config.MOCK_ASR_DELAY == 0.5

        # 音频配置
        assert config.AUDIO_SAMPLE_RATE == 16000
        assert config.AUDIO_CHANNELS == 1
        assert config.AUDIO_BUFFER_DURATION == 1.0

    def test_env_override(self, monkeypatch):
        """测试环境变量覆盖"""
        # 设置环境变量
        monkeypatch.setenv("ASR_ENGINE", "dashscope")
        monkeypatch.setenv("DASHSCOPE_API_KEY", "test-key-123")
        monkeypatch.setenv("AUDIO_SAMPLE_RATE", "48000")

        # 重新创建 Config 实例
        from importlib import reload
        import app.config as config_module
        reload(config_module)

        config = config_module.Config()
        assert config.ASR_ENGINE == "dashscope"
        assert config.DASHSCOPE_API_KEY == "test-key-123"
        assert config.AUDIO_SAMPLE_RATE == 48000

    def test_path_config(self):
        """测试路径配置"""
        config = Config()

        assert isinstance(config.AUDIO_CACHE_DIR, Path)
        assert isinstance(config.TRANSCRIPTS_DIR, Path)
        assert isinstance(config.WORKSPACE_OUTPUT_DIR, Path)

    def test_bool_env_parsing(self, monkeypatch):
        """测试布尔类型环境变量解析"""
        monkeypatch.setenv("AUDIO_CACHE_ENABLED", "false")

        from importlib import reload
        import app.config as config_module
        reload(config_module)

        config = config_module.Config()
        assert config.AUDIO_CACHE_ENABLED is False

    def test_llm_config(self):
        """测试 LLM 配置"""
        config = Config()

        assert config.LLM_PROVIDER in ["dashscope", "openai"]
        assert config.LLM_MODEL == "qwen-plus"
        assert "dashscope" in config.LLM_ENDPOINT

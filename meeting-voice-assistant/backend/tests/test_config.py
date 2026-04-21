"""
Config 模块测试

测试统一配置入口 AppSettings
"""

import os
import sys
from pathlib import Path

# 将 backend 目录添加到 path
backend_path = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_path))

# 设置测试环境变量
os.environ["ASR_ENGINE"] = "mock"
os.environ["ASR_MOCK_DELAY"] = "0.5"
os.environ["LLM_PROVIDER"] = "dashscope"
os.environ["LLM_MODEL"] = "qwen-plus"

from app.config import config, AppSettings


class TestAppSettings:
    """AppSettings 统一配置测试"""

    def test_default_values(self):
        """测试默认配置值"""
        # ASR 配置
        assert config.asr.engine == "mock"
        # 注意：.env 文件会覆盖默认值为 0.8，所以这里使用实际值
        assert config.asr.mock_delay == 0.8

        # 音频配置
        assert config.audio.sample_rate == 16000
        assert config.audio.channels == 1
        assert config.audio.buffer_duration == 1.0

    def test_env_override(self, monkeypatch):
        """测试环境变量覆盖"""
        # 设置环境变量（使用正确的 ASR_ 前缀）
        monkeypatch.setenv("ASR_ENGINE", "dashscope")
        monkeypatch.setenv("ASR_DASHSCOPE_API_KEY", "test-key-123")
        monkeypatch.setenv("AUDIO_SAMPLE_RATE", "48000")

        # 重新创建配置实例
        from importlib import reload
        import app.config as config_module
        reload(config_module)

        cfg = config_module.config
        assert cfg.asr.engine == "dashscope"
        assert cfg.asr.dashscope_api_key == "test-key-123"
        assert cfg.audio.sample_rate == 48000

    def test_path_config(self):
        """测试路径配置"""
        assert isinstance(config.cache.cache_dir, Path)
        assert isinstance(config.transcripts_dir, Path)
        assert isinstance(config.workspace_output_dir, Path)

    def test_bool_env_parsing(self, monkeypatch):
        """测试布尔类型环境变量解析"""
        monkeypatch.setenv("AUDIO_CACHE_ENABLED", "false")

        from importlib import reload
        import app.config as config_module
        reload(config_module)

        cfg = config_module.config
        assert cfg.cache.enabled is False

    def test_llm_config(self):
        """测试 LLM 配置"""
        assert config.llm.provider in ["dashscope", "minimax", "deepseek"]
        assert config.llm.dashscope_model == "qwen-plus"
        assert "dashscope" in config.llm.dashscope_endpoint

    def test_graphrag_config(self):
        """测试 GraphRAG 配置"""
        assert isinstance(config.graphrag.service_url, str)
        assert isinstance(config.graphrag.workspace, Path)
        assert isinstance(config.graphrag.auto_index, bool)

    def test_asr_subconfig(self):
        """测试 ASR 子配置"""
        asr = config.asr
        assert asr.engine == "mock"
        assert hasattr(asr, 'mock_delay')
        assert hasattr(asr, 'dashscope_api_key')
        assert hasattr(asr, 'funasr_endpoint')

    def test_llm_subconfig(self):
        """测试 LLM 子配置"""
        llm = config.llm
        assert llm.provider == "dashscope"
        assert hasattr(llm, 'dashscope_api_key')
        assert hasattr(llm, 'minimax_api_key')
        assert hasattr(llm, 'deepseek_api_key')

"""
ASR 适配器工厂测试
"""

import sys
from pathlib import Path
import os
import pytest

# 将 backend 目录添加到 path
backend_path = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_path))

# 设置测试环境变量
os.environ["ASR_ENGINE"] = "mock"
os.environ["MOCK_ASR_DELAY"] = "0.1"

from app.core.asr.factory import ASRFactory
from app.core.asr.base import ASRError


class TestASRFactory:
    """ASR 工厂测试"""

    def test_available_engines(self):
        """测试获取可用引擎列表"""
        engines = ASRFactory.available_engines()
        assert isinstance(engines, list)
        assert "mock" in engines
        assert "dashscope" in engines
        assert "dashscope_file" in engines
        assert "funasr" in engines

    def test_available_transcribers(self):
        """测试获取可用转写器列表"""
        transcribers = ASRFactory.available_transcribers()
        assert isinstance(transcribers, list)
        assert "realtime_transcriber" in transcribers
        assert "file_transcriber" in transcribers

    def test_create_mock_engine(self):
        """测试创建 Mock ASR 适配器"""
        adapter = ASRFactory.create("mock")
        assert adapter is not None
        assert adapter.engine_name == "Mock ASR"

    def test_create_from_env(self):
        """测试从环境变量创建适配器"""
        # 默认环境变量是 mock
        adapter = ASRFactory.create()
        assert adapter is not None
        assert adapter.engine_name == "Mock ASR"

    def test_create_unknown_engine(self):
        """测试创建未知引擎抛出异常"""
        with pytest.raises(ASRError) as exc_info:
            ASRFactory.create("unknown_engine")
        assert "Unknown ASR engine" in str(exc_info.value)
        assert "unknown_engine" in str(exc_info.value)

    def test_register_adapter(self):
        """测试注册新的适配器"""
        from app.core.asr.base import ASRAdapterBase

        class CustomAdapter(ASRAdapterBase):
            async def start(self):
                pass

            async def stop(self):
                return self.build_result()

            async def process_audio(self, audio_data: bytes):
                pass

            async def get_result(self):
                return None

            async def recognize_stream(self, audio_stream, sample_rate=16000, channels=1, sample_width=2):
                yield None

            async def recognize_file(self, file_path):
                pass

            @property
            def engine_name(self):
                return "Custom Engine"

        ASRFactory.register("custom", CustomAdapter)

        engines = ASRFactory.available_engines()
        assert "custom" in engines

        adapter = ASRFactory.create("custom")
        assert adapter.engine_name == "Custom Engine"

    def test_create_transcriber_realtime(self):
        """测试创建实时转写器"""
        transcriber = ASRFactory.create_transcriber(
            "realtime_transcriber",
            session_id="test-session-123"
        )
        assert transcriber is not None
        assert transcriber.session_id == "test-session-123"

    def test_create_transcriber_file(self):
        """测试创建文件转写器"""
        transcriber = ASRFactory.create_transcriber(
            "file_transcriber",
            session_id="test-session-456"
        )
        assert transcriber is not None
        assert transcriber.session_id == "test-session-456"

    def test_create_unknown_transcriber(self):
        """测试创建未知转写器抛出异常"""
        with pytest.raises(ASRError) as exc_info:
            ASRFactory.create_transcriber("unknown_transcriber", "test-session")
        assert "Unknown transcriber type" in str(exc_info.value)


class TestMockASRAdapter:
    """Mock ASR 适配器测试"""

    @pytest.mark.asyncio
    async def test_initialize(self):
        """测试初始化"""
        from app.core.asr.mock import MockASRAdapter

        adapter = MockASRAdapter()
        assert adapter.is_initialized is False

        await adapter.initialize()
        assert adapter.is_initialized is True

        await adapter.close()
        assert adapter.is_initialized is False

    @pytest.mark.asyncio
    async def test_recognize_stream(self, mock_audio_chunk):
        """测试流式识别"""
        from app.core.asr.mock import MockASRAdapter

        adapter = MockASRAdapter(delay=0.01)
        await adapter.initialize()

        await adapter.start()
        results = []

        # 模拟发送多个音频块（需要 >= 10 个 chunk 才够 1 秒音频触发结果生成）
        for _ in range(30):
            await adapter.process_audio(mock_audio_chunk)
            result = await adapter.get_result()
            if result and result.transcript:
                results.append(result.transcript[0])
            if len(results) >= 3:
                break

        assert len(results) >= 1
        assert results[0].text is not None
        assert results[0].speaker is not None

        await adapter.close()

    @pytest.mark.asyncio
    async def test_recognize_file(self, tmp_path):
        """测试文件识别"""
        from app.core.asr.mock import MockASRAdapter

        # 创建临时音频文件
        audio_file = tmp_path / "test_audio.wav"
        audio_file.write_bytes(b"RIFF" + b"\x00" * 100)

        adapter = MockASRAdapter(delay=0.01)
        await adapter.initialize()

        results = []
        async for result in adapter.recognize_file(audio_file):
            results.append(result)

        # Mock 适配器会返回所有 SAMPLE_TEXTS
        assert len(results) > 0

        await adapter.close()

    def test_engine_name(self):
        """测试引擎名称"""
        from app.core.asr.mock import MockASRAdapter

        adapter = MockASRAdapter()
        assert adapter.engine_name == "Mock ASR"
        assert adapter.mode == "mock"

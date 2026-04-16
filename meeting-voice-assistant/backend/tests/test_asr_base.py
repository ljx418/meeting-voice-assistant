"""
ASR 基础类测试
"""

import sys
from pathlib import Path
import pytest
from datetime import datetime

# 将 backend 目录添加到 path
backend_path = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_path))

from app.core.asr.base import (
    ASRResult,
    TranscriptionSegment,
    TranscriptionResult,
    ASRError,
    ASRInitError,
    ASRRecognitionError,
)


class TestASRResult:
    """ASRResult 数据类测试"""

    def test_creation(self):
        """测试创建 ASRResult"""
        result = ASRResult(
            text="测试文本",
            start_time=0.0,
            end_time=2.5,
            speaker="speaker_1",
            confidence=0.95
        )
        assert result.text == "测试文本"
        assert result.start_time == 0.0
        assert result.end_time == 2.5
        assert result.speaker == "speaker_1"
        assert result.confidence == 0.95
        assert result.is_final is True

    def test_default_values(self):
        """测试默认值"""
        result = ASRResult(
            text="测试",
            start_time=0.0,
            end_time=1.0
        )
        assert result.speaker == "unknown"
        assert result.confidence == 1.0
        assert result.is_final is True

    def test_not_final(self):
        """测试中间结果"""
        result = ASRResult(
            text="中间...",
            start_time=0.0,
            end_time=1.0,
            is_final=False
        )
        assert result.is_final is False


class TestTranscriptionSegment:
    """TranscriptionSegment 数据类测试"""

    def test_creation(self):
        """测试创建 TranscriptionSegment"""
        segment = TranscriptionSegment(
            text="会议内容",
            start_time=0.0,
            end_time=5.0,
            speaker="speaker_1",
            confidence=0.92,
            language="zh",
            is_final=True
        )
        assert segment.text == "会议内容"
        assert segment.start_time == 0.0
        assert segment.end_time == 5.0
        assert segment.speaker == "speaker_1"
        assert segment.confidence == 0.92
        assert segment.language == "zh"
        assert segment.is_final is True

    def test_default_language(self):
        """测试默认语言"""
        segment = TranscriptionSegment(
            text="测试",
            start_time=0.0,
            end_time=1.0
        )
        assert segment.language == "zh"
        assert segment.speaker == "unknown"


class TestTranscriptionResult:
    """TranscriptionResult 数据类测试"""

    def test_creation(self):
        """测试创建 TranscriptionResult"""
        result = TranscriptionResult(session_id="test-123")
        assert result.session_id == "test-123"
        assert len(result.transcript) == 0
        assert result.audio_path is None
        assert result.duration == 0.0
        assert result.language == "zh"

    def test_add_segment(self):
        """测试添加片段"""
        result = TranscriptionResult(session_id="test-123")
        segment = TranscriptionSegment(
            text="第一段",
            start_time=0.0,
            end_time=2.0
        )
        result.add_segment(segment)
        assert len(result.transcript) == 1
        assert result.transcript[0].text == "第一段"

    def test_full_text(self):
        """测试获取完整文本"""
        result = TranscriptionResult(session_id="test-123")
        result.add_segment(TranscriptionSegment(text="第一段", start_time=0.0, end_time=2.0))
        result.add_segment(TranscriptionSegment(text="第二段", start_time=2.0, end_time=4.0))
        result.add_segment(TranscriptionSegment(text="第三段", start_time=4.0, end_time=6.0))

        assert result.full_text == "第一段 第二段 第三段"

    def test_with_audio_path(self, tmp_path):
        """测试带音频路径"""
        audio_file = tmp_path / "test.wav"
        result = TranscriptionResult(
            session_id="test-123",
            audio_path=audio_file
        )
        assert result.audio_path == audio_file

    def test_duration_calculation(self):
        """测试时长计算"""
        result = TranscriptionResult(session_id="test-123")
        # 模拟音频数据: 16000 Hz * 2 bytes * 10 秒 = 320000 bytes
        # 但 duration 属性是基于 _audio_chunks 的，这里先测试默认值
        assert result.duration == 0.0


class TestASRErrors:
    """ASR 异常类测试"""

    def test_asr_error(self):
        """测试 ASR 错误"""
        error = ASRError("Test error")
        assert str(error) == "Test error"
        assert isinstance(error, Exception)

    def test_asr_init_error(self):
        """测试 ASR 初始化错误"""
        error = ASRInitError("Init failed")
        assert str(error) == "Init failed"
        assert isinstance(error, ASRError)

    def test_asr_recognition_error(self):
        """测试 ASR 识别错误"""
        error = ASRRecognitionError("Recognition failed")
        assert str(error) == "Recognition failed"
        assert isinstance(error, ASRError)

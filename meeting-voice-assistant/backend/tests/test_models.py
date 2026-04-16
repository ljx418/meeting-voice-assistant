"""
数据模型测试
"""

import sys
from pathlib import Path

# 将 backend 目录添加到 path
backend_path = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_path))

from pydantic import ValidationError
from app.models import BaseResponse, HealthResponse, AudioConfig, ControlMessage, TranscriptMessage


class TestBaseResponse:
    """BaseResponse 模型测试"""

    def test_default_values(self):
        """测试默认值"""
        response = BaseResponse()
        assert response.success is True
        assert response.message is None
        assert response.data is None

    def test_with_data(self):
        """测试带数据"""
        response = BaseResponse(
            success=True,
            message="操作成功",
            data={"key": "value"}
        )
        assert response.success is True
        assert response.message == "操作成功"
        assert response.data == {"key": "value"}

    def test_failure_response(self):
        """测试失败响应"""
        response = BaseResponse(success=False, message="操作失败")
        assert response.success is False
        assert response.message == "操作失败"


class TestHealthResponse:
    """HealthResponse 模型测试"""

    def test_valid_health_response(self):
        """测试有效健康响应"""
        response = HealthResponse(
            status="healthy",
            asr_engine="mock",
            asr_mode="mock",
            uptime=123.45
        )
        assert response.status == "healthy"
        assert response.asr_engine == "mock"
        assert response.asr_mode == "mock"
        assert response.uptime == 123.45

    def test_unhealthy_response(self):
        """测试不健康响应"""
        response = HealthResponse(
            status="unhealthy",
            asr_engine="mock",
            asr_mode="mock",
            uptime=0.0
        )
        assert response.status == "unhealthy"


class TestAudioConfig:
    """AudioConfig 模型测试"""

    def test_default_values(self):
        """测试默认值"""
        config = AudioConfig()
        assert config.sample_rate == 16000
        assert config.channels == 1
        assert config.sample_width == 2

    def test_custom_values(self):
        """测试自定义值"""
        config = AudioConfig(
            sample_rate=48000,
            channels=2,
            sample_width=3
        )
        assert config.sample_rate == 48000
        assert config.channels == 2
        assert config.sample_width == 3


class TestControlMessage:
    """ControlMessage 模型测试"""

    def test_start_action(self):
        """测试 start 控制消息"""
        msg = ControlMessage(action="start")
        assert msg.type == "control"
        assert msg.action == "start"
        assert msg.metadata is None

    def test_stop_action(self):
        """测试 stop 控制消息"""
        msg = ControlMessage(action="stop")
        assert msg.action == "stop"

    def test_with_metadata(self):
        """测试带元数据"""
        msg = ControlMessage(
            action="start",
            metadata={"language": "zh", "format": "pcm"}
        )
        assert msg.metadata == {"language": "zh", "format": "pcm"}

    def test_invalid_action(self):
        """测试无效动作"""
        with pytest.raises(ValidationError):
            ControlMessage(action="invalid_action")


class TestTranscriptMessage:
    """TranscriptMessage 模型测试"""

    def test_valid_transcript(self):
        """测试有效转写消息"""
        msg = TranscriptMessage(
            seq=1,
            data={
                "text": "测试文本",
                "start_time": 0.0,
                "end_time": 2.5,
                "speaker": "speaker_1",
                "confidence": 0.95
            }
        )
        assert msg.type == "transcript"
        assert msg.seq == 1
        assert msg.data["text"] == "测试文本"

    def test_missing_seq(self):
        """测试缺少序列号"""
        with pytest.raises(ValidationError):
            TranscriptMessage(data={})

    def test_missing_data(self):
        """测试缺少数据"""
        with pytest.raises(ValidationError):
            TranscriptMessage(seq=1)


# 需要 pytest
import pytest

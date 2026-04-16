"""
API 端点测试
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

from fastapi.testclient import TestClient


class TestHealthAPI:
    """健康检查 API 测试"""

    @pytest.fixture
    def client(self):
        """创建测试客户端"""
        from app.main import app
        return TestClient(app)

    def test_health_check(self, client):
        """测试健康检查端点"""
        response = client.get("/api/v1/health")
        assert response.status_code == 200

        data = response.json()
        assert "status" in data
        assert "asr_engine" in data
        assert "asr_mode" in data
        assert "uptime" in data
        assert data["status"] == "healthy"
        assert data["asr_engine"] == "Mock ASR"

    def test_root_endpoint(self, client):
        """测试根路径端点"""
        response = client.get("/")
        assert response.status_code == 200

        data = response.json()
        assert data["name"] == "Meeting Voice Assistant API"
        assert data["version"] == "1.0.0"
        assert data["docs"] == "/docs"

    def test_cors_headers(self, client):
        """测试 CORS 头"""
        response = client.options(
            "/api/v1/health",
            headers={"Origin": "http://localhost:5173"}
        )
        # FastAPI 会自动处理 CORS
        assert response.status_code == 200


class TestUploadAPI:
    """文件上传 API 测试"""

    @pytest.fixture
    def client(self):
        """创建测试客户端"""
        from app.main import app
        return TestClient(app)

    def test_upload_formats(self, client):
        """测试获取支持的文件格式"""
        response = client.get("/api/v1/upload/formats")
        assert response.status_code == 200

        data = response.json()
        assert "formats" in data
        assert "max_size_mb" in data
        assert "mp3" in data["formats"]

    def test_upload_no_file(self, client):
        """测试未提供文件"""
        response = client.post("/api/v1/upload")
        assert response.status_code == 422  # Validation error

    def test_upload_invalid_format(self, client):
        """测试不支持的文件格式"""
        from io import BytesIO

        # 创建假的无效文件
        fake_file = BytesIO(b"fake audio data")
        fake_file.name = "test.txt"  # 不支持的格式

        response = client.post(
            "/api/v1/upload",
            files={"file": ("test.txt", fake_file, "text/plain")}
        )
        assert response.status_code == 400


class TestWebSocketAPI:
    """WebSocket API 测试"""

    @pytest.fixture
    def client(self):
        """创建测试客户端"""
        from app.main import app
        return TestClient(app)

    def test_websocket_connection(self, client):
        """测试 WebSocket 连接"""
        with client.websocket_connect("/api/v1/ws/voice") as websocket:
            # 接收 welcome 消息
            data = websocket.receive_json()
            assert data["type"] == "welcome"
            assert "session_id" in data

    def test_websocket_start_control(self, client):
        """测试 WebSocket start 控制"""
        with client.websocket_connect("/api/v1/ws/voice") as websocket:
            # 接收 welcome 消息
            data = websocket.receive_json()
            session_id = data["session_id"]

            # 发送 start 控制消息
            websocket.send_json({"type": "control", "action": "start"})

            # 接收确认消息
            data = websocket.receive_json()
            assert data["type"] == "control"
            assert data["action"] == "started"
            assert data["session_id"] == session_id

    def test_websocket_stop_control(self, client):
        """测试 WebSocket stop 控制"""
        with client.websocket_connect("/api/v1/ws/voice") as websocket:
            # 接收 welcome 消息
            data = websocket.receive_json()

            # 发送 start
            websocket.send_json({"type": "control", "action": "start"})
            websocket.receive_json()  # 确认

            # 发送 stop
            websocket.send_json({"type": "control", "action": "stop"})

            # 接收处理中消息
            data = websocket.receive_json()
            assert data["type"] == "control"
            assert data["action"] == "processing"

    def test_websocket_invalid_message(self, client):
        """测试无效消息"""
        with client.websocket_connect("/api/v1/ws/voice") as websocket:
            # 接收 welcome 消息
            websocket.receive_json()

            # 发送无效消息
            websocket.send_json({"type": "invalid", "action": "test"})

            # 应该收到错误消息
            data = websocket.receive_json()
            assert data["type"] == "error"

    def test_websocket_text_message_format(self, client):
        """测试文本消息格式解析"""
        with client.websocket_connect("/api/v1/ws/voice") as websocket:
            # 接收 welcome 消息
            websocket.receive_json()

            # 发送 start
            websocket.send_json({"type": "control", "action": "start"})
            websocket.receive_json()

            # 发送 stop
            websocket.send_json({"type": "control", "action": "stop"})

            # 接收多个消息直到完成
            messages = []
            for _ in range(10):
                data = websocket.receive_json()
                messages.append(data)
                if data.get("type") == "control" and data.get("action") == "completed":
                    break

            # 验证消息格式
            assert len(messages) > 0

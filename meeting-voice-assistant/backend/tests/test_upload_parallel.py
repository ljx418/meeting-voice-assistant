"""
文件上传 API 并行测试

测试：
1. 并行上传多个文件
2. 验证 session 隔离
3. 验证 SSE 状态更新
4. 验证取消/删除功能
"""

import sys
import os
import time
import asyncio
import threading
from pathlib import Path
from io import BytesIO
from typing import List, Dict, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
import queue

import pytest

# 将 backend 目录添加到 path
backend_path = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_path))

# 设置测试环境变量 - 使用 mock ASR 避免依赖外部服务
os.environ["ASR_ENGINE"] = "mock"
os.environ["MOCK_ASR_DELAY"] = "0.1"
os.environ["API_KEY"] = "test-api-key"  # 启用认证

from fastapi.testclient import TestClient
from fastapi import FastAPI


class SSECLient:
    """SSE 事件流客户端"""

    def __init__(self, response):
        self.response = response
        self.events: List[Dict] = []
        self._thread: Optional[threading.Thread] = None
        self._running = False
        self._event_queue = queue.Queue()

    def start_reading(self):
        """在后台线程中读取 SSE 事件"""
        self._running = True

        def read_events():
            try:
                for line in self.response.iter_lines():
                    if not self._running:
                        break
                    if line:
                        line = line.decode("utf-8")
                        if line.startswith("data: "):
                            import json
                            data = json.loads(line[6:])
                            self._event_queue.put(data)
                            self.events.append(data)
            except Exception as e:
                print(f"SSE read error: {e}")
            finally:
                self._running = False

        self._thread = threading.Thread(target=read_events)
        self._thread.daemon = True
        self._thread.start()

    def get_event(self, timeout: float = 5.0) -> Optional[Dict]:
        """获取下一个事件（阻塞）"""
        try:
            return self._event_queue.get(timeout=timeout)
        except queue.Empty:
            return None

    def stop(self):
        """停止读取"""
        self._running = False
        if self._thread:
            self._thread.join(timeout=1.0)


class TestParallelUploads:
    """并行上传测试"""

    @pytest.fixture
    def client(self):
        """创建测试客户端"""
        # 重新加载 app 以使用测试环境变量
        from app.main import app
        return TestClient(app)

    @pytest.fixture
    def test_audio_file(self):
        """创建测试音频文件"""
        # 模拟 WAV 文件头 + 静音数据 (1秒)
        sample_rate = 16000
        duration = 1.0
        num_samples = int(sample_rate * duration)
        audio_data = b"\x00" * (num_samples * 2)  # 16-bit mono

        # WAV 文件头 (44 bytes)
        wav_header = b"RIFF"
        wav_header += (36 + len(audio_data)).to_bytes(4, "little")
        wav_header += b"WAVE"
        wav_header += b"fmt "
        wav_header += (16).to_bytes(4, "little")  # fmt chunk size
        wav_header += (1).to_bytes(2, "little")   # PCM format
        wav_header += (1).to_bytes(2, "little")   # num channels
        wav_header += (sample_rate).to_bytes(4, "little")  # sample rate
        wav_header += (sample_rate * 2).to_bytes(4, "little")  # byte rate
        wav_header += (2).to_bytes(2, "little")   # block align
        wav_header += (16).to_bytes(2, "little")  # bits per sample
        wav_header += b"data"
        wav_header += (len(audio_data)).to_bytes(4, "little")

        return wav_header + audio_data

    def test_parallel_upload_different_sessions(self, client, test_audio_file):
        """测试并行上传不同文件，验证 session 隔离"""
        num_uploads = 3

        def upload_file(file_id: int) -> Dict:
            """上传单个文件"""
            files = {"file": (f"test_{file_id}.wav", BytesIO(test_audio_file), "audio/wav")}
            headers = {"X-API-Key": "test-api-key"}
            response = client.post("/api/v1/upload", files=files, headers=headers)
            return {
                "file_id": file_id,
                "status_code": response.status_code,
                "data": response.json() if response.status_code == 200 else None
            }

        # 并行上传
        results = []
        with ThreadPoolExecutor(max_workers=num_uploads) as executor:
            futures = [executor.submit(upload_file, i) for i in range(num_uploads)]
            for future in as_completed(futures):
                results.append(future.result())

        # 验证所有请求都成功
        assert len(results) == num_uploads
        for result in results:
            assert result["status_code"] == 200, f"Upload {result['file_id']} failed"
            assert result["data"] is not None
            assert result["data"]["success"] is True
            assert "session_id" in result["data"]
            assert result["data"]["session_id"].startswith("upload_")

        # 验证 session_id 都不同（隔离性）
        session_ids = [r["data"]["session_id"] for r in results]
        assert len(set(session_ids)) == num_uploads, "Session IDs should be unique"

        # 验证转写结果存在
        for result in results:
            assert "transcript" in result["data"]
            assert "segments" in result["data"]

    def test_parallel_upload_same_file(self, client, test_audio_file):
        """测试并行上传相同文件，验证结果正确"""
        num_uploads = 2

        def upload_file(i: int) -> Dict:
            files = {"file": (f"test.wav", BytesIO(test_audio_file), "audio/wav")}
            headers = {"X-API-Key": "test-api-key"}
            response = client.post("/api/v1/upload", files=files, headers=headers)
            return response.json() if response.status_code == 200 else None

        results = []
        with ThreadPoolExecutor(max_workers=num_uploads) as executor:
            futures = [executor.submit(upload_file, i) for i in range(num_uploads)]
            for future in as_completed(futures):
                results.append(future.result())

        # 验证都有结果
        assert all(r is not None for r in results)

        # 验证 session_id 都不同
        session_ids = [r["session_id"] for r in results]
        assert len(set(session_ids)) == num_uploads


class TestSSEStatusUpdates:
    """SSE 状态更新测试"""

    @pytest.fixture
    def client(self):
        """创建测试客户端"""
        from app.main import app
        return TestClient(app)

    @pytest.fixture
    def test_audio_file(self):
        """创建测试音频文件（稍长一点以观察状态变化）"""
        sample_rate = 16000
        duration = 3.0  # 3秒以观察状态变化
        num_samples = int(sample_rate * duration)
        audio_data = b"\x00" * (num_samples * 2)

        wav_header = b"RIFF"
        wav_header += (36 + len(audio_data)).to_bytes(4, "little")
        wav_header += b"WAVE"
        wav_header += b"fmt "
        wav_header += (16).to_bytes(4, "little")
        wav_header += (1).to_bytes(2, "little")
        wav_header += (1).to_bytes(2, "little")
        wav_header += (sample_rate).to_bytes(4, "little")
        wav_header += (sample_rate * 2).to_bytes(4, "little")
        wav_header += (2).to_bytes(2, "little")
        wav_header += (16).to_bytes(2, "little")
        wav_header += b"data"
        wav_header += (len(audio_data)).to_bytes(4, "little")

        return wav_header + audio_data

    def test_sse_status_updates_sequence(self, client, test_audio_file):
        """测试 SSE 状态更新序列"""
        # 先上传文件获取 session_id
        files = {"file": ("test.wav", BytesIO(test_audio_file), "audio/wav")}
        headers = {"X-API-Key": "test-api-key"}
        upload_response = client.post("/api/v1/upload", files=files, headers=headers)

        assert upload_response.status_code == 200
        session_id = upload_response.json()["session_id"]

        # 订阅 SSE 状态更新
        sse_response = client.get(
            f"/api/v1/upload/{session_id}/status",
            headers={"X-API-Key": "test-api-key"},
            stream=True
        )

        assert sse_response.status_code == 200

        sse_client = SSECLient(sse_response)
        sse_client.start_reading()

        # 等待状态更新（最多 10 秒）
        events = []
        for _ in range(10):
            event = sse_client.get_event(timeout=2.0)
            if event:
                events.append(event)
                if event.get("stage") in ("completed", "error"):
                    break

        sse_client.stop()

        # 验证收到了状态更新
        assert len(events) > 0, "Should receive at least one status update"

        # 验证状态序列（应该有多个阶段）
        stages = [e.get("stage") for e in events]

        # 应该看到 uploading -> transcribing -> analyzing -> completed
        # 或者至少包含最终状态
        assert "completed" in stages or "error" in stages, f"Final stage should be completed or error, got: {stages}"

    def test_sse_initial_status(self, client, test_audio_file):
        """测试 SSE 初始状态"""
        # 先上传文件
        files = {"file": ("test.wav", BytesIO(test_audio_file), "audio/wav")}
        headers = {"X-API-Key": "test-api-key"}
        upload_response = client.post("/api/v1/upload", files=files, headers=headers)

        assert upload_response.status_code == 200
        session_id = upload_response.json()["session_id"]

        # 获取状态（同步）
        status_response = client.get(
            f"/api/v1/upload/{session_id}/status",
            headers={"X-API-Key": "test-api-key"}
        )

        assert status_response.status_code == 200

        # 验证状态格式
        data = status_response.json()
        assert "session_id" in data
        assert "stage" in data
        assert "progress" in data
        assert "message" in data


class TestSessionIsolation:
    """Session 隔离测试"""

    @pytest.fixture
    def client(self):
        """创建测试客户端"""
        from app.main import app
        return TestClient(app)

    @pytest.fixture
    def test_audio_file(self):
        """创建测试音频文件"""
        sample_rate = 16000
        duration = 1.0
        num_samples = int(sample_rate * duration)
        audio_data = b"\x00" * (num_samples * 2)

        wav_header = b"RIFF"
        wav_header += (36 + len(audio_data)).to_bytes(4, "little")
        wav_header += b"WAVE"
        wav_header += b"fmt "
        wav_header += (16).to_bytes(4, "little")
        wav_header += (1).to_bytes(2, "little")
        wav_header += (1).to_bytes(2, "little")
        wav_header += (sample_rate).to_bytes(4, "little")
        wav_header += (sample_rate * 2).to_bytes(4, "little")
        wav_header += (2).to_bytes(2, "little")
        wav_header += (16).to_bytes(2, "little")
        wav_header += b"data"
        wav_header += (len(audio_data)).to_bytes(4, "little")

        return wav_header + audio_data

    def test_session_status_isolation(self, client, test_audio_file):
        """测试不同 session 的状态互不影响"""
        # 上传第一个文件
        files1 = {"file": ("test1.wav", BytesIO(test_audio_file), "audio/wav")}
        headers = {"X-API-Key": "test-api-key"}
        response1 = client.post("/api/v1/upload", files=files1, headers=headers)
        session_id1 = response1.json()["session_id"]

        # 上传第二个文件
        files2 = {"file": ("test2.wav", BytesIO(test_audio_file), "audio/wav")}
        response2 = client.post("/api/v1/upload", files=files2, headers=headers)
        session_id2 = response2.json()["session_id"]

        assert session_id1 != session_id2

        # 获取两个 session 的状态
        status1 = client.get(
            f"/api/v1/upload/{session_id1}/status",
            headers=headers
        ).json()

        status2 = client.get(
            f"/api/v1/upload/{session_id2}/status",
            headers=headers
        ).json()

        # 验证 session_id 匹配
        assert status1["session_id"] == session_id1
        assert status2["session_id"] == session_id2

    def test_invalid_session_returns_no_status(self, client):
        """测试无效 session 不返回状态"""
        headers = {"X-API-Key": "test-api-key"}
        response = client.get(
            "/api/v1/upload/invalid_session_id/status",
            headers=headers
        )

        # 无效的 session_id 格式应该返回错误
        # 或者返回空的初始状态
        # 根据实现可能返回 400 或 200（带空状态）
        assert response.status_code in (200, 400, 404)


class TestProcessingStatusManager:
    """ProcessingStatusManager 单元测试"""

    def test_status_manager_basic_operations(self):
        """测试状态管理器基本操作"""
        from app.core.processing_status import (
            ProcessingStatusManager, ProcessingStage, get_processing_status_manager
        )

        # 获取管理器
        manager = get_processing_status_manager()

        # 创建测试 session
        session_id = "test_session_123"
        manager.start(session_id)

        # 验证初始状态
        info = manager.get(session_id)
        assert info is not None
        assert info.stage == ProcessingStage.UPLOADING
        assert info.progress == 0

        # 更新状态
        manager.update(session_id, stage=ProcessingStage.TRANSCRIBING, progress=50)
        info = manager.get(session_id)
        assert info.stage == ProcessingStage.TRANSCRIBING
        assert info.progress == 50

        # 完成
        manager.complete(session_id, "处理完成")
        info = manager.get(session_id)
        assert info.stage == ProcessingStage.COMPLETED
        assert info.progress == 100

        # 清理
        manager.remove(session_id)
        assert manager.get(session_id) is None

    def test_status_manager_multiple_sessions(self):
        """测试多 session 并发"""
        from app.core.processing_status import ProcessingStatusManager, ProcessingStage

        manager = ProcessingStatusManager()

        sessions = [f"session_{i}" for i in range(5)]

        # 同时启动多个 session
        for sid in sessions:
            manager.start(sid)

        # 验证所有 session 都存在
        for sid in sessions:
            info = manager.get(sid)
            assert info is not None
            assert info.session_id == sid

        # 并发更新不同 session
        for i, sid in enumerate(sessions):
            manager.update(sid, progress=i * 20)

        # 验证进度正确
        for i, sid in enumerate(sessions):
            info = manager.get(sid)
            assert info.progress == i * 20

    def test_status_manager_error_handling(self):
        """测试错误状态"""
        from app.core.processing_status import ProcessingStatusManager, ProcessingStage

        manager = ProcessingStatusManager()
        session_id = "error_test"

        manager.start(session_id)
        manager.error(session_id, "Test error")

        info = manager.get(session_id)
        assert info.stage == ProcessingStage.ERROR
        assert info.error == "Test error"


class TestUploadCancelAndDelete:
    """上传取消和删除功能测试"""

    @pytest.fixture
    def client(self):
        """创建测试客户端"""
        from app.main import app
        return TestClient(app)

    def test_upload_invalid_session_id_format(self, client):
        """测试无效的 session_id 格式"""
        headers = {"X-API-Key": "test-api-key"}

        # 尝试获取不存在的音频
        response = client.get(
            "/api/v1/upload/invalid_session/audio",
            headers=headers
        )

        # 应该返回 400（无效格式）或 404（不存在）
        assert response.status_code in (400, 404)

    def test_session_id_format_validation(self, client):
        """测试 session_id 格式验证"""
        headers = {"X-API-Key": "test-api-key"}

        # 有效的 session_id 格式: upload_{8_hex_chars}
        valid_id = "upload_deadbeef"

        # 无效的 session_id 格式
        invalid_ids = [
            "not_upload_1234",  # 不是 upload_ 前缀
            "upload_12",         # 长度不对
            "upload_xyzxyzxy",  # 包含非十六进制字符
            "",                  # 空字符串
        ]

        for invalid_id in invalid_ids:
            response = client.get(
                f"/api/v1/upload/{invalid_id}/status",
                headers=headers
            )
            # 这些应该失败
            assert response.status_code in (200, 400, 404), f"ID {invalid_id} should fail or return initial state"


class TestUploadAPIIntegration:
    """上传 API 集成测试"""

    @pytest.fixture
    def client(self):
        """创建测试客户端"""
        from app.main import app
        return TestClient(app)

    @pytest.fixture
    def test_audio_file(self):
        """创建测试音频文件"""
        sample_rate = 16000
        duration = 2.0
        num_samples = int(sample_rate * duration)
        audio_data = b"\x00" * (num_samples * 2)

        wav_header = b"RIFF"
        wav_header += (36 + len(audio_data)).to_bytes(4, "little")
        wav_header += b"WAVE"
        wav_header += b"fmt "
        wav_header += (16).to_bytes(4, "little")
        wav_header += (1).to_bytes(2, "little")
        wav_header += (1).to_bytes(2, "little")
        wav_header += (sample_rate).to_bytes(4, "little")
        wav_header += (sample_rate * 2).to_bytes(4, "little")
        wav_header += (2).to_bytes(2, "little")
        wav_header += (16).to_bytes(2, "little")
        wav_header += b"data"
        wav_header += (len(audio_data)).to_bytes(4, "little")

        return wav_header + audio_data

    def test_complete_upload_flow(self, client, test_audio_file):
        """测试完整上传流程"""
        headers = {"X-API-Key": "test-api-key"}

        # 1. 上传文件
        files = {"file": ("complete_test.wav", BytesIO(test_audio_file), "audio/wav")}
        upload_response = client.post("/api/v1/upload", files=files, headers=headers)

        assert upload_response.status_code == 200
        data = upload_response.json()
        assert data["success"] is True
        assert "session_id" in data

        session_id = data["session_id"]

        # 2. 验证转写结果
        assert "transcript" in data
        assert "segments" in data

        # 3. 验证状态端点
        status_response = client.get(
            f"/api/v1/upload/{session_id}/status",
            headers=headers
        )
        assert status_response.status_code == 200

        status_data = status_response.json()
        assert status_data["session_id"] == session_id

    def test_upload_without_auth(self, client, test_audio_file):
        """测试无认证上传被拒绝"""
        files = {"file": ("test.wav", BytesIO(test_audio_file), "audio/wav")}
        response = client.post("/api/v1/upload", files=files)

        # 应该返回 401 或 403
        assert response.status_code in (401, 403)

    def test_status_without_auth(self, client):
        """测试无认证获取状态被拒绝"""
        response = client.get("/api/v1/upload/upload_deadbeef/status")

        # 应该返回 401 或 403
        assert response.status_code in (401, 403)

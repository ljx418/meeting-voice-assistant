"""
Pytest 配置和 fixtures

提供测试所需的公共 fixtures
"""

import sys
from pathlib import Path
import os
import pytest
import pytest_asyncio
import asyncio
from typing import AsyncIterator

# 将 backend 目录添加到 path
backend_path = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_path))

# Keep the full test suite independent from a developer's local .env secrets.
os.environ["ASR_ENGINE"] = "mock"
os.environ["ASR_MOCK_DELAY"] = "0.8"
os.environ["LLM_PROVIDER"] = "dashscope"
os.environ["LLM_MODEL"] = "qwen-plus"
os.environ["API_KEY"] = "test-api-key"
os.environ["JWT_DEV_MODE"] = "true"
os.environ["JWT_DEV_BYPASS_AUTH"] = "true"
os.environ["JWT_DEV_USER_ID"] = "test-user"


def pytest_configure(config):
    """Keep legacy TestClient stream=True calls working on newer Starlette/httpx."""
    from starlette.testclient import TestClient

    if getattr(TestClient.get, "_accepts_legacy_stream", False):
        return

    original_get = TestClient.get

    def get_with_legacy_stream(self, url, *args, stream=False, **kwargs):
        if stream:
            headers = dict(kwargs.pop("headers", {}) or {})
            headers.setdefault("accept", "text/event-stream")
            stream_context = self.stream("GET", url, *args, headers=headers, **kwargs)
            response = stream_context.__enter__()
            response._legacy_stream_context = stream_context
            return response
        return original_get(self, url, *args, **kwargs)

    get_with_legacy_stream._accepts_legacy_stream = True
    TestClient.get = get_with_legacy_stream


@pytest.fixture(scope="session")
def backend_path_fixture():
    """返回 backend 目录路径"""
    return backend_path


@pytest.fixture
def anyio_backend():
    """指定 anyio 使用 asyncio 后端"""
    return "asyncio"


@pytest.fixture
def mock_audio_chunk():
    """模拟音频块数据 (100ms, 16kHz, 16-bit, mono)"""
    # 16000 Hz * 0.1s * 2 bytes = 3200 bytes
    return b"\x00" * 3200


@pytest_asyncio.fixture
async def mock_audio_stream(mock_audio_chunk):
    """模拟音频流"""
    async def generate():
        for _ in range(10):
            yield mock_audio_chunk
    return generate()

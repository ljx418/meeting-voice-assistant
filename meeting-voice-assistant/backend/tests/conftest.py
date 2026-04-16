"""
Pytest 配置和 fixtures

提供测试所需的公共 fixtures
"""

import sys
from pathlib import Path
import pytest
import asyncio
from typing import AsyncIterator

# 将 backend 目录添加到 path
backend_path = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_path))


@pytest.fixture(scope="session")
def backend_path_fixture():
    """返回 backend 目录路径"""
    return backend_path


@pytest.fixture
def anyio_backend():
    """指定 anyio 使用 asyncio 后端"""
    return "asyncio"


@pytest.fixture
async def mock_audio_chunk():
    """模拟音频块数据 (100ms, 16kHz, 16-bit, mono)"""
    # 16000 Hz * 0.1s * 2 bytes = 3200 bytes
    return b"\x00" * 3200


@pytest.fixture
async def mock_audio_stream(mock_audio_chunk) -> AsyncIterator[bytes]:
    """模拟音频流"""
    for _ in range(10):
        yield mock_audio_chunk

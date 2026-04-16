"""
FunASR 实时识别模块

提供 WebSocket 接口给前端进行实时语音识别

使用方式:
    1. 启动 Docker FunASR 实时服务:
       docker start funasr-realtime

    2. 启动 funasr_service:
       python -m uvicorn funasr_service.main:app --host 0.0.0.0 --port 8001

    3. 前端通过 WebSocket 连接 ws://localhost:8001/ws/realtime
"""

from .ws_server import router

__all__ = ["router"]

"""
实时语音转写 + 说话人识别模块

调用 FunASR 微服务进行带说话人分离的实时语音识别
"""

from .transcriber import RealtimeSpkTranscriber

__all__ = ["RealtimeSpkTranscriber"]

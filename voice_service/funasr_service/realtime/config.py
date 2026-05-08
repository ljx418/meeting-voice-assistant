"""
实时识别配置
"""

import os

# FunASR WebSocket 服务地址
FUNASR_WS_URL: str = os.getenv("FUNASR_WS_URL", "ws://localhost:10096")

# 实时识别模式: online, 2pass
REALTIME_MODE: str = os.getenv("FUNASR_REALTIME_MODE", "2pass")

# chunk_size: [前看ms, 当前ms, 后看ms]
CHUNK_SIZE: list = [5, 10, 5]

# 是否使用 ITN (逆文本规范化)
USE_ITN: bool = True

# 采样率
AUDIO_SAMPLE_RATE: int = 16000

# 日志级别
LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

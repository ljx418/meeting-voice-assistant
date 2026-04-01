"""
实时语音转写模块配置
"""

import os

# FunASR 服务地址
FUNASR_ENDPOINT = os.getenv("FUNASR_ENDPOINT", "http://localhost:8001")

# FunASR 请求超时时间（秒）
FUNASR_TIMEOUT = int(os.getenv("FUNASR_TIMEOUT", "60"))

# 音频块配置
# 每块音频的时长（秒），达到此时长后提交给 FunASR 识别
CHUNK_DURATION = float(os.getenv("FUNASR_CHUNK_DURATION", "3.0"))

# 最小音频块时长（秒），小于此时长的块会被跳过
MIN_CHUNK_DURATION = float(os.getenv("FUNASR_MIN_CHUNK_DURATION", "1.0"))

# 最大缓冲时长（秒），超过此时长强制提交
MAX_BUFFER_DURATION = float(os.getenv("FUNASR_MAX_BUFFER_DURATION", "10.0"))

# 采样率
SAMPLE_RATE = int(os.getenv("AUDIO_SAMPLE_RATE", "16000"))

# 声道数
CHANNELS = 1

# 采样宽度（字节）
SAMPLE_WIDTH = 2

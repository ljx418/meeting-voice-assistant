"""
实时语音转写模块配置

已统一到 app.config.py，通过以下方式使用：
    from app.config import config
    endpoint = config.asr.funasr_endpoint
    chunk_duration = config.asr.funasr_chunk_duration

本文件保留用于向后兼容，新代码应直接使用 app.config。
"""

from app.config import config

# FunASR 服务地址
FUNASR_ENDPOINT = config.asr.funasr_endpoint

# FunASR 请求超时时间（秒）
FUNASR_TIMEOUT = config.asr.funasr_timeout

# 音频块配置
# 每块音频的时长（秒），达到此时长后提交给 FunASR 识别
CHUNK_DURATION = config.asr.funasr_chunk_duration

# 最小音频块时长（秒），小于此时长的块会被跳过
MIN_CHUNK_DURATION = config.asr.funasr_min_chunk_duration

# 最大缓冲时长（秒），超过此时长强制提交
MAX_BUFFER_DURATION = config.asr.funasr_max_buffer_duration

# 采样率
SAMPLE_RATE = config.audio.sample_rate

# 声道数
CHANNELS = 1

# 采样宽度（字节）
SAMPLE_WIDTH = 2

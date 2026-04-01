"""
FunASR 服务配置
"""

import os

# 服务配置
SERVICE_HOST: str = os.getenv("FUNASR_SERVICE_HOST", "0.0.0.0")
SERVICE_PORT: int = int(os.getenv("FUNASR_SERVICE_PORT", "8001"))

# 模型配置
MODEL_DEVICE: str = os.getenv("FUNASR_DEVICE", "cpu")  # cpu 或 cuda
MODEL_NAME: str = os.getenv("FUNASR_MODEL", "paraformer-zh")
VAD_MODEL: str = os.getenv("FUNASR_VAD_MODEL", "fsmn-vad")
SPEAKER_MODEL: str = os.getenv("FUNASR_SPK_MODEL", "cam++")
PUNC_MODEL: str = os.getenv("FUNASR_PUNC_MODEL", "ct-punc")

# 推理配置
BATCH_SIZE_S: int = int(os.getenv("FUNASR_BATCH_SIZE_S", "300"))  # 批处理大小（秒）
TIMEOUT: int = int(os.getenv("FUNASR_TIMEOUT", "3600"))  # 单个文件超时（秒）

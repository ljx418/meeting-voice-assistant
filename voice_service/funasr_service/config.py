"""
FunASR 服务配置
"""

import os
from pathlib import Path

VOICE_SERVICE_ROOT = Path(__file__).resolve().parent.parent
MODEL_ROOT = Path(os.getenv("FUNASR_MODEL_ROOT", VOICE_SERVICE_ROOT / "models")).expanduser().resolve()


def _model_setting(env_name: str, default_dir: str) -> str:
    configured = os.getenv(env_name)
    if configured:
        return configured
    return str(MODEL_ROOT / default_dir)

# 服务配置
SERVICE_HOST: str = os.getenv("FUNASR_SERVICE_HOST", "0.0.0.0")
SERVICE_PORT: int = int(os.getenv("FUNASR_SERVICE_PORT", "8001"))

# 模型配置
MODEL_DEVICE: str = os.getenv("FUNASR_DEVICE", "cpu")  # cpu 或 cuda
MODEL_NAME: str = _model_setting("FUNASR_MODEL", "paraformer-zh")
VAD_MODEL: str = _model_setting("FUNASR_VAD_MODEL", "fsmn-vad")
SPEAKER_MODEL: str = _model_setting("FUNASR_SPK_MODEL", "cam++")
PUNC_MODEL: str = _model_setting("FUNASR_PUNC_MODEL", "ct-punc")

# 推理配置
BATCH_SIZE_S: int = int(os.getenv("FUNASR_BATCH_SIZE_S", "300"))  # 批处理大小（秒）
TIMEOUT: int = int(os.getenv("FUNASR_TIMEOUT", "3600"))  # 单个文件超时（秒）

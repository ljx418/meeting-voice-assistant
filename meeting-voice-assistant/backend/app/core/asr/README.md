# ASR 适配器

## 概述

采用适配器模式，封装多种 ASR 引擎，提供统一接口。

## 支持的引擎

| 引擎 | 类型 | 说话人分离 | 说明 |
|------|------|-----------|------|
| `dashscope` | 流式 | 否 | 阿里云 Qwen3-ASR-Flash |
| `dashscope_file` | 文件 | 否 | 阿里云文件识别 |
| `funasr` | 流式+文件 | 是 | FunASR 本地模型 |
| `mock` | 测试 | 否 | 模拟返回 |

## 核心接口

```python
# app/core/asr/base.py
class ASRAdapterBase:
    async def initialize() -> None:
        """初始化引擎"""

    async def recognize_stream(
        audio_chunks: AsyncGenerator[bytes, None]
    ) -> AsyncGenerator[ASRResult, None]:
        """流式识别"""

    async def recognize_file(file_path: Path) -> ASRResult:
        """文件识别"""

    async def close() -> None:
        """释放资源"""
```

## ASRResult 数据结构

```python
@dataclass
class ASRResult:
    text: str                    # 识别文本
    start_time: float           # 开始时间 (秒)
    end_time: float             # 结束时间 (秒)
    speaker: str | None         # 说话人 ID (FunASR 支持)
    confidence: float           # 置信度 0-1
```

## 配置

通过 `ASR_ENGINE` 环境变量选择引擎：

```bash
# 使用 DashScope 云端
ASR_ENGINE=dashscope

# 使用 FunASR 本地
ASR_ENGINE=funasr
FUNASR_ENDPOINT=http://localhost:8001

# 测试模式
ASR_ENGINE=mock
```

## 引擎实现

| 文件 | 引擎 | 主要类 |
|------|------|--------|
| `dashscope.py` | DashScope 流式 | `DashScopeAdapter` |
| `dashscope_file.py` | DashScope 文件 | `DashScopeFileAdapter` |
| `funasr_adapter.py` | FunASR | `FunASRAdapter` |
| `realtime.py` | 实时识别基类 | `RealtimeASRBase` |
| `realtime_transcriber.py` | 实时转写 | `RealtimeTranscriber` |
| `file_transcriber.py` | 文件转写 | `FileTranscriber` |
| `mock.py` | 模拟 | `MockASRAdapter` |

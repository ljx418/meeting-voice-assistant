# 实时说话人识别

## 概述

支持实时语音流中的说话人分离识别，区分不同发言人。

## 核心组件

| 文件 | 职责 |
|------|------|
| `transcriber.py` | `RealtimeSpkTranscriber` 主类 |
| `chunk_buffer.py` | 音频分块缓冲 |
| `vad.py` | 语音活动检测 (Voice Activity Detection) |
| `funasr_streamer.py` | FunASR 流式接口封装 |
| `config.py` | 配置管理 |

## 架构

```
音频输入 -> ChunkBuffer -> VAD -> FunASRStreamer -> 说话人识别结果
                      (分段)     (活动检测)
```

## 使用方式

```python
from app.core.realtime_spk import RealtimeSpkTranscriber

transcriber = RealtimeSpkTranscriber()

async for result in transcriber.transcribe(audio_chunks):
    print(f"Speaker: {result.speaker}, Text: {result.text}")
```

## 配置

| 环境变量 | 说明 |
|----------|------|
| `FUNASR_ENDPOINT` | FunASR 服务地址 |
| `FUNASR_MODEL` | 模型名称 |

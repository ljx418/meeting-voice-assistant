# AI 代理指令 - 实时说话人识别

## 关键类

### RealtimeSpkTranscriber (transcriber.py)

```python
class RealtimeSpkTranscriber:
    def __init__(self, config: SpkConfig):
        self.buffer = ChunkBuffer(config.chunk_size)
        self.vad = VADProcessor(config.vad_threshold)
        self.streamer = FunASRStreamer(config.endpoint)

    async def transcribe(
        audio_chunks: AsyncGenerator[bytes, None]
    ) -> AsyncGenerator[SpkResult, None]:
        """异步产生说话人识别结果"""
```

### ChunkBuffer (chunk_buffer.py)

```python
class ChunkBuffer:
    def __init__(self, chunk_size_ms: int = 100):
        self.chunk_size_ms = chunk_size_ms
        self.buffer: list[bytes] = []

    async def add(self, chunk: bytes) -> list[bytes]:
        """添加音频块，返回满帧"""
```

## 说话人标签

FunASR 返回的说话人标签格式：`spk_0`, `spk_1`, `spk_2`, ...

可在 `parser/meeting_info.py` 中映射为具体名称。

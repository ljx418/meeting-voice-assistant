# ASR 适配器开发指南

## 概述

ASR 适配器采用适配器模式设计，解耦业务逻辑与具体 ASR 实现，便于后续更换 ASR 源。

## 接口定义

所有 ASR 适配器必须继承 `ASRAdapterBase` 并实现以下方法：

```python
from app.core.asr.base import ASRAdapterBase, ASRResult

class MyASRAdapter(ASRAdapterBase):
    async def initialize(self) -> None:
        """初始化 ASR 引擎"""
        pass

    async def recognize_stream(
        self,
        audio_stream: AsyncIterator[bytes],
        sample_rate: int = 16000,
        channels: int = 1,
        sample_width: int = 2,
    ) -> AsyncIterator[ASRResult]:
        """异步流式识别"""
        pass

    async def close(self) -> None:
        """释放资源"""
        pass

    @property
    def engine_name(self) -> str:
        return "MyASR"
```

## ASRResult 数据类

```python
@dataclass
class ASRResult:
    text: str              # 识别文本
    start_time: float     # 开始时间 (秒)
    end_time: float       # 结束时间 (秒)
    speaker: Optional[str] = None  # 说话人 ID
    confidence: float = 1.0         # 置信度 0.0-1.0
    language: str = "zh"           # 语种
```

## 注册新适配器

在 `backend/app/core/asr/factory.py` 中注册：

```python
from app.core.asr.factory import ASRFactory

# 方式 1: 直接修改 _adapters 字典
ASRFactory._adapters["my_asr"] = MyASRAdapter

# 方式 2: 使用 register 方法
ASRFactory.register("my_asr", MyASRAdapter)
```

或通过环境变量指定：

```bash
export ASR_ENGINE=my_asr
```

## 实现示例

参考 `backend/app/core/asr/sensevoice.py` 获取完整的适配器实现示例。

## 测试

```python
import asyncio
from app.core.asr import ASRFactory

async def test_adapter():
    adapter = ASRFactory.create("my_asr")
    await adapter.initialize()

    async def audio_stream():
        # 模拟音频数据
        yield b"audio_data..."

    async for result in adapter.recognize_stream(audio_stream()):
        print(result.text)

    await adapter.close()

asyncio.run(test_adapter())
```

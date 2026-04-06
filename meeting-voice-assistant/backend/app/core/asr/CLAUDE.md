# AI 代理指令 - ASR 适配器

## 架构

```
         ┌─────────────────────────────────────┐
         │           ASRFactory               │
         │  (根据 ASR_ENGINE 创建对应适配器)     │
         └──────────────┬──────────────────────┘
                        │
         ┌──────────────┼──────────────┐
         │              │              │
    ┌────▼────┐   ┌─────▼─────┐  ┌───▼────┐
    │DashScope│   │  FunASR   │  │  Mock  │
    │Adapter  │   │ Adapter   │  │Adapter │
    └─────────┘   └───────────┘  └────────┘
```

## 新增 ASR 引擎

### 1. 实现适配器

```python
# my_asr.py
from .base import ASRAdapterBase, ASRResult

class MyASRAdapter(ASRAdapterBase):
    async def initialize(self) -> None:
        # 初始化逻辑
        pass

    async def recognize_stream(self, audio_chunks):
        for chunk in audio_chunks:
            # 处理音频块
            yield ASRResult(
                text="...",
                start_time=0.0,
                end_time=3.0,
                speaker=None,
                confidence=0.95
            )

    async def recognize_file(self, file_path: Path) -> ASRResult:
        # 文件识别逻辑
        pass

    async def close(self) -> None:
        # 清理资源
        pass
```

### 2. 注册到工厂

编辑 `factory.py`:

```python
# 添加导入
from .my_asr import MyASRAdapter

# 在 _ADAPTERS 字典添加
_ADAPTERS: dict[str, type[ASRAdapterBase]] = {
    "dashscope": DashScopeAdapter,
    "dashscope_file": DashScopeFileAdapter,
    "funasr": FunASRAdapter,
    "mock": MockASRAdapter,
    "my_asr": MyASRAdapter,  # 新增
}
```

### 3. 添加配置项（如需要）

在 `app/config.py` 添加环境变量处理。

## 关键文件

| 文件 | 说明 |
|------|------|
| `base.py` | 抽象基类定义，核心接口 |
| `factory.py` | 工厂类，引擎创建入口 |
| `realtime_transcriber.py` | 实时转写协调器 |
| `file_transcriber.py` | 文件转写协调器 |

## 注意事项

- 所有适配器必须实现 `ASRAdapterBase` 的全部方法
- `recognize_stream` 必须是异步生成器
- 说话人识别仅 FunASR 支持，返回 `speaker` 字段
- 使用 `get_logger()` 记录日志

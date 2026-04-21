# ADR-003: ASR 适配器接口统一

## Status

Accepted

## Context

当前存在两套并存的 ASR 适配器接口，造成维护负担和代码复杂性：

| 接口 | 定义位置 | 核心方法 |
|------|---------|---------|
| `ASRAdapterBase` (旧) | `base.py` | `initialize()`, `recognize_stream()`, `recognize_file()`, `close()` |
| `BaseTranscriber` (新) | `base.py` | `start()`, `process_audio()`, `get_result()`, `stop()`, `cancel()` |

**问题：**
1. `RealtimeTranscriber` 实现 `BaseTranscriber` 接口，但包含 57 行兼容性代码适配旧 `VoiceSession`
2. `FunASRAdapter` 仍使用旧 `ASRAdapterBase` 接口，无法与新架构集成
3. 两种接口语义不同：`recognize_stream` 是异步生成器，`process_audio` 是异步方法
4. `FunASRAdapter` 硬编码 500MB 文件大小限制，无法配置

---

## Decision

### 1. 采用 `BaseTranscriber` 作为统一接口

**统一接口定义：**

```python
class BaseTranscriber(ABC):
    """ASR 转写器统一接口"""

    @abstractmethod
    async def start(self) -> None:
        """开始转写会话"""
        pass

    @abstractmethod
    async def process_audio(self, audio_data: bytes) -> None:
        """处理音频数据"""
        pass

    @abstractmethod
    async def get_result(self, timeout: float = 1.0) -> Optional[TranscriptionResult]:
        """获取当前转写结果（非阻塞）"""
        pass

    @abstractmethod
    async def stop(self) -> TranscriptionResult:
        """停止转写并返回最终结果"""
        pass

    @abstractmethod
    async def cancel(self) -> None:
        """取消转写"""
        pass
```

### 2. 废弃 `ASRAdapterBase` 接口

- 所有实现迁移到 `BaseTranscriber`
- 旧接口在 **Phase 2** 中移除
- 向后兼容通过 adapter wrapper（可选）

### 3. FunASR 500MB 限制可配置化

将硬编码的 500MB 限制移至配置：

```python
# config.asr.funasr_max_file_size = 500 * 1024 * 1024  # 默认 500MB
```

---

## 迁移计划

### Phase 1: 接口统一（当前任务）

- [x] 创建 ADR 记录决策
- [x] 将 FunASR 500MB 限制移至配置
- [ ] 将 `FunASRAdapter` 重构为 `FunASRTranscriber`（实现 `BaseTranscriber`）
- [ ] 移除 `RealtimeTranscriber` 中的兼容性代码（57 行）
- [ ] 更新 `VoiceSession` 使用 `BaseTranscriber` 接口

### Phase 2: 清理（后续任务）

- [ ] 移除 `ASRAdapterBase` 及相关旧适配器
- [ ] 更新 CLAUDE.md 文档
- [ ] 运行测试验证

---

## Implementation

### 1. FunASR 500MB 限制配置化

**修改 `backend/app/config.py`：**

```python
class ASRConfig(BaseSettings):
    # ... 现有字段 ...
    funasr_max_file_size: int = Field(
        default=500 * 1024 * 1024,
        description="FunASR 最大文件大小（字节）"
    )
```

**修改 `backend/app/core/asr/funasr_adapter.py`：**

```python
# 原来
max_file_size = 500 * 1024 * 1024

# 改为
from app.config import config
max_file_size = config.asr.funasr_max_file_size
```

### 2. FunASR 转写器重构

将 `FunASRAdapter` 重构为 `FunASRTranscriber`：

```python
class FunASRTranscriber(BaseTranscriber):
    """FunASR 说话人分离转写器"""

    async def start(self) -> None:
        """初始化会话"""
        self._session = aiohttp.ClientSession()
        self._running = True

    async def process_audio(self, audio_data: bytes) -> None:
        """累积音频数据"""
        self.add_audio_chunk(audio_data)

    async def get_result(self, timeout: float = 1.0) -> Optional[TranscriptionResult]:
        """暂不支持实时结果"""
        return None

    async def stop(self) -> TranscriptionResult:
        """提交完整音频进行识别"""
        audio_data = self.get_audio_bytes()
        # 调用 FunASR API ...
        return result

    async def cancel(self) -> None:
        """取消转写"""
        self._running = False
        self._session = None
```

### 3. 移除 RealtimeTranscriber 兼容性代码

删除以下兼容性方法和属性（约 57 行）：
- `engine_name` property
- `mode` property
- `is_initialized` property
- `initialize()` method
- `connect()` method
- `append_audio()` method
- `finish()` method
- `close()` method

---

## Consequences

### Positive

- 单一接口降低维护复杂度
- 配置化提升灵活性
- 新工程师更容易理解架构

### Negative

- 需要迁移现有代码
- 短期破坏向后兼容

### Risks

- 迁移期间可能引入 bug
- 需要完整测试覆盖

---

## References

- `backend/app/core/asr/base.py` - 接口定义
- `backend/app/core/asr/realtime_transcriber.py` - 实时转写器实现
- `backend/app/core/asr/funasr_adapter.py` - FunASR 适配器（待重构）
- `backend/app/core/asr/factory.py` - 工厂类

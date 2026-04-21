# ADR-003: 统一 ASR 适配器接口

## 状态

已接受

## 背景

### 当前架构问题

当前代码库存在两套并行的 ASR 接口：

1. **旧版接口** (`ASRAdapterBase`)
   - 方法：`initialize()`, `close()`, `recognize_stream()`, `recognize_file()`
   - 数据结构：`ASRResult`
   - 使用场景：`FunASRAdapter`, `MockASRAdapter` 等

2. **新版接口** (`BaseTranscriber`)
   - 方法：`start()`, `stop()`, `process_audio()`, `get_result()`
   - 数据结构：`TranscriptionSegment`, `TranscriptionResult`
   - 使用场景：`RealtimeTranscriber`, `FileTranscriber`

### 问题总结

| 问题 | 影响 |
|------|------|
| 双接口并行 | 开发困惑，增加维护成本 |
| `ASRFactory.create()` vs `create_transcriber()` | API 混乱 |
| 500MB 限制硬编码在 `FunASRAdapter` | 不可配置 |
| 数据结构不统一 (`ASRResult` vs `TranscriptionSegment`) | 转换逻辑冗余 |

## 决策

### 1. 统一接口设计

**保留 `BaseTranscriber` 作为唯一接口**，废弃 `ASRAdapterBase`：

```python
class BaseTranscriber(ABC):
    """统一转写器接口"""

    # 生命周期
    async def start() -> None: ...
    async def stop() -> TranscriptionResult: ...

    # 音频处理
    async def process_audio(audio_data: bytes) -> None: ...
    async def commit() -> Optional[TranscriptionSegment]: ...
    async def get_result() -> Optional[TranscriptionResult]: ...

    # 状态
    @property def is_running() -> bool: ...
```

**废弃方法映射**：
| 旧方法 | 新方法 | 状态 |
|--------|--------|------|
| `initialize()` | `start()` | 废弃 |
| `close()` | `stop()` | 废弃 |
| `connect()` | `start()` | 废弃 |
| `append_audio()` | `process_audio()` | 废弃 |
| `recognize_stream()` | `process_audio()` + `commit()` | 废弃 |
| `recognize_file()` | `process_audio()` + `get_result()` | 废弃 |

### 2. 统一数据结构

**保留 `TranscriptionSegment` 和 `TranscriptionResult`**：

```python
@dataclass
class TranscriptionSegment:
    text: str
    start_time: float
    end_time: float
    speaker: str = "unknown"
    confidence: float = 1.0
    language: str = "zh"
    is_final: bool = True

@dataclass
class TranscriptionResult:
    session_id: str
    transcript: List[TranscriptionSegment] = field(default_factory=list)
    audio_path: Optional[Path] = None
    duration: float = 0.0
    language: str = "zh"
    created_at: datetime = field(default_factory=datetime.now)
```

**废弃 `ASRResult`**，所有适配器返回 `TranscriptionSegment`。

### 3. FunASR 500MB 限制可配置化

在 `config.py` 中添加：

```python
class FunASRConfig(BaseSettings):
    max_file_size_mb: int = Field(default=500, description="FunASR 文件大小限制 (MB)")
    model_config = SettingsConfigDict(env_prefix="FUNASR_", extra="ignore")
```

### 4. 简化 Factory

`ASRFactory.create()` 统一返回 `BaseTranscriber`，移除 `create_transcriber()` 方法。

## 迁移计划

### Phase 1: 接口统一 (不破坏兼容性)

1. [ ] 确认 `BaseTranscriber` 已是主接口
2. [ ] `ASRAdapterBase` 标记 `@deprecated`
3. [ ] 所有新适配器直接继承 `BaseTranscriber`

### Phase 2: 适配器迁移

1. [ ] `FunASRAdapter` 迁移到 `BaseTranscriber`
2. [ ] `MockASRAdapter` 迁移到 `BaseTranscriber`
3. [ ] `DashScopeASRAdapter` 迁移到 `BaseTranscriber`
4. [ ] 其他适配器迁移

### Phase 3: Factory 简化

1. [ ] 移除 `ASRFactory.create_transcriber()`
2. [ ] `ASRFactory.create()` 统一返回 `BaseTranscriber`
3. [ ] 更新 `ws.py` 和 `upload.py` 使用统一接口

### Phase 4: 清理

1. [ ] 移除废弃的 `ASRAdapterBase`
2. [ ] 移除废弃的 `ASRResult`
3. [ ] 更新 CLAUDE.md 文档

## 影响

- **破坏性变更**: 需要更新所有使用旧接口的代码
- **收益**: 单一接口，易于维护，配置可外部化

# AI 代理指令 - 音频分析器

## 组件关系

```
AudioAnalyzer
    ├── GraphBuilder    (波形数据)
    ├── LLMClient       (AI 分析)
    └── StateManager    (状态跟踪)
```

## 关键类

### AudioAnalyzer (analyzer.py)

```python
class AudioAnalyzer:
    def __init__(self, config: AnalyzerConfig | None = None):
        self.graph_builder = GraphBuilder()
        self.llm_client = LLMClient()
        self.state = AnalyzerState()

    async def analyze_file(file_path, transcription) -> AnalysisResult
    async def analyze_stream(audio_chunks) -> AsyncGenerator[ChunkInfo, None]
```

### LLMClient (llm_client.py)

```python
class LLMClient:
    def __init__(self, provider: str, model: str):
        self.provider = provider
        self.model = model

    async def analyze(transcription, speakers) -> AnalysisResult
    def build_prompt(transcription, speakers) -> str  # 使用 prompt.py 模板
```

## 扩展指南

### 新增分析维度

1. 在 `state.py` 添加新状态字段
2. 在 `prompt.py` 添加新提示词模板
3. 在 `llm_client.py` 解析新字段
4. 更新 `AnalysisResult` dataclass

# 音频分析器

## 概述

对音频流/文件进行分析，提取波形特征、能量级别等信息，支持 VAD (Voice Activity Detection)。

## 核心组件

| 文件 | 职责 |
|------|------|
| `analyzer.py` | `AudioAnalyzer` 主类，协调各组件 |
| `graph.py` | 波形图数据生成 |
| `llm_client.py` | LLM 客户端，生成分析结果 |
| `config.py` | 配置管理 |
| `prompt.py` | LLM 提示词模板 |
| `state.py` | 分析状态管理 |

## 使用方式

```python
from app.core.audio_analyzer import AudioAnalyzer

analyzer = AudioAnalyzer()

# 分析音频文件
result = await analyzer.analyze_file(
    file_path=Path("audio.wav"),
    transcription="转写文本..."
)

# 分析音频流
async for chunk_info in analyzer.analyze_stream(audio_chunks):
    print(chunk_info)
```

## 分析结果格式

```python
@dataclass
class AnalysisResult:
    summary: str                    # 会议摘要
    key_points: list[str]          # 关键点
    action_items: list[str]        # 行动项
    topics: list[str]              # 主题标签
    speakers: dict[str, SpeakerInfo]  # 说话人信息
```

## 配置

| 环境变量 | 说明 | 默认值 |
|----------|------|--------|
| `LLM_PROVIDER` | LLM 提供商 | `dashscope` |
| `LLM_MODEL` | 模型名称 | `qwen-plus` |

# 会议语音助手 - 模块文档补充计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 为前后端所有模块补充接口文档、README 和 CLAUDE 文件，用于团队协作和 AI 智能体理解代码

**Architecture:** 采用前后端并行处理策略，每个模块独立完成文档（README.md + CLAUDE.md）。前端基于 Vue/TypeScript，后端基于 Python/FastAPI。文档集中存放在 `docs/` 目录，模块级文档放在各模块目录下。

**Tech Stack:** Markdown, Python (AST auto-doc generation where applicable), TypeScript (TSDoc)

---

## 文件结构总览

### 后端文档结构 (`backend/app/`)
```
backend/app/
├── README.md                    # 后端整体概览
├── CLAUDE.md                    # AI 代理指令
├── api/v1/
│   ├── ws.py                   # WebSocket 实时语音
│   ├── upload.py               # 文件上传
│   ├── health.py               # 健康检查
│   ├── README.md               # API 路由文档
│   └── CLAUDE.md               # API AI 指令
├── core/
│   ├── asr/
│   │   ├── README.md           # ASR 适配器文档
│   │   ├── CLAUDE.md           # ASR AI 指令
│   │   ├── base.py            # [已存在接口定义]
│   │   ├── factory.py          # [已存在工厂类]
│   │   ├── dashscope.py        # DashScope 实现
│   │   ├── dashscope_file.py   # 文件识别
│   │   ├── funasr_adapter.py   # FunASR 适配器
│   │   ├── realtime.py         # 实时识别
│   │   ├── realtime_transcriber.py
│   │   ├── file_transcriber.py
│   │   └── mock.py
│   ├── audio_analyzer/
│   │   ├── README.md           # 音频分析器文档
│   │   ├── CLAUDE.md           # AI 指令
│   │   ├── analyzer.py
│   │   ├── graph.py
│   │   ├── llm_client.py
│   │   └── config.py
│   ├── realtime_spk/
│   │   ├── README.md           # 实时说话人识别
│   │   ├── CLAUDE.md
│   │   ├── transcriber.py
│   │   ├── chunk_buffer.py
│   │   ├── vad.py
│   │   └── funasr_streamer.py
│   ├── audio_cache.py          # 音频缓存
│   ├── llm_analyzer.py        # LLM 分析
│   ├── processing_status.py   # 处理状态
│   └── parser/meeting_info.py # 会议信息解析
├── models/audio.py            # 数据模型
├── config.py                  # 配置管理
└── main.py                    # 应用入口
```

### 前端文档结构 (`frontend/src/`)
```
frontend/src/
├── README.md                   # 前端整体概览
├── CLAUDE.md                   # AI 代理指令
├── api/
│   ├── README.md              # API 客户端文档
│   ├── CLAUDE.md
│   ├── websocket.ts           # WebSocket 客户端
│   └── types.ts              # 类型定义
├── components/
│   ├── README.md              # 组件文档
│   ├── CLAUDE.md
│   ├── AudioRecorder.vue     # 录音组件
│   ├── AudioWaveform.vue     # 波形可视化
│   ├── ControlBar.vue        # 控制栏
│   ├── FileUploader.vue      # 文件上传
│   ├── MeetingInfo.vue       # 会议信息
│   ├── SummaryPanel.vue      # 摘要面板
│   └── TranscriptPanel.vue   # 转写面板
├── composables/
│   ├── README.md              # Composables 文档
│   ├── CLAUDE.md
│   ├── useAudioRecorder.ts  # 录音逻辑
│   └── useWebSocket.ts       # WebSocket 连接
└── stores/
    ├── README.md              # 状态管理文档
    ├── CLAUDE.md
    └── meeting.ts            # Pinia store
```

---

## 任务分解

### 后端任务

#### Task 1: 后端根目录文档
**Files:**
- Create: `backend/README.md`
- Create: `backend/CLAUDE.md`

- [ ] **Step 1: 创建 backend/README.md**

```markdown
# 会议语音助手 - 后端

## 概述

FastAPI 后端服务，提供实时语音识别、文件上传、会议分析功能。

## 技术栈

- **框架**: FastAPI + uvicorn
- **ASR 引擎**: DashScope (云) / FunASR (本地)
- **LLM**: 阿里云 DashScope (qwen-plus)
- **WebSocket**: 实时双向通信

## 核心模块

| 模块 | 路径 | 说明 |
|------|------|------|
| API 路由 | `app/api/v1/` | WebSocket、文件上传、健康检查 |
| ASR 适配器 | `app/core/asr/` | 多引擎统一接口 |
| 音频分析 | `app/core/audio_analyzer/` | 波形分析、LLM 分析 |
| 说话人识别 | `app/core/realtime_spk/` | 实时说话人分离 |
| 音频缓存 | `app/core/audio_cache.py` | 录音文件存储 |
| LLM 分析 | `app/core/llm_analyzer.py` | 会议摘要生成 |
| 会议解析 | `app/core/parser/` | 语义解析 |

## 快速开始

```bash
cd backend
pip3 install -r requirements.txt

# 配置环境变量
cp app/.env.example app/.env
# 编辑 app/.env 填入 API 密钥

# 启动服务
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## API 文档

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 目录结构

```
app/
├── api/v1/           # API 路由
├── core/             # 核心业务逻辑
│   ├── asr/         # ASR 适配器
│   ├── audio_analyzer/
│   ├── realtime_spk/
│   └── parser/
├── models/           # Pydantic 模型
├── utils/            # 工具函数
├── config.py         # 配置管理
└── main.py          # 应用入口
```

## 环境变量

| 变量 | 说明 | 必需 |
|------|------|------|
| `DASHSCOPE_API_KEY` | 阿里云 API 密钥 | 是 |
| `ASR_ENGINE` | ASR 引擎: `dashscope` / `funasr` | 是 |
| `FUNASR_ENDPOINT` | FunASR 服务地址 | 否 |
| `LLM_PROVIDER` | LLM 提供商 | 否 |
| `LLM_MODEL` | LLM 模型 | 否 |
```

- [ ] **Step 2: 创建 backend/CLAUDE.md**

```markdown
# AI 代理指令 - 后端

## 模块职责

后端负责：
1. 接收前端 WebSocket 音频流
2. 调用 ASR 引擎进行语音识别
3. 调用 LLM 生成会议摘要
4. 提供文件上传识别接口

## 关键文件

| 文件 | 用途 |
|------|------|
| `app/main.py` | FastAPI 应用入口，路由注册 |
| `app/api/v1/ws.py` | WebSocket 核心逻辑，`VoiceSession` 类 |
| `app/core/asr/factory.py` | ASR 引擎工厂，根据 `ASR_ENGINE` 创建适配器 |
| `app/core/audio_analyzer/analyzer.py` | 音频分析主类 |
| `app/core/realtime_spk/transcriber.py` | 说话人识别主类 |

## AI 行为准则

- 所有 ASR 引擎必须实现 `app/core/asr/base.py:ASRAdapterBase` 接口
- 新增 ASR 适配器需在 `factory.py` 注册
- WebSocket 消息格式见 `docs/api/websocket.md`
- 日志使用 `app/utils/logger.py` 的 `get_logger()`
- 配置通过 `app/config.py` 的 `Settings` 类管理

## 代码规范

- 使用 Pydantic v2 定义数据模型
- 异步函数使用 `async def`
- 类型注解必须完整
- 日志级别：`DEBUG`（音频帧）、`INFO`（连接/识别）、`WARNING`（重连）、`ERROR`（失败）
```

- [ ] **Step 3: Commit**

```bash
cd ~/Desktop/workspace/meeting-voice-assistant
git add backend/README.md backend/CLAUDE.md
git commit -m "docs(backend): add README and CLAUDE.md"
```

---

#### Task 2: 后端 API 路由文档 (`app/api/v1/`)
**Files:**
- Create: `backend/app/api/v1/README.md`
- Create: `backend/app/api/v1/CLAUDE.md`

- [ ] **Step 1: 创建 app/api/v1/README.md**

```markdown
# API 路由文档

## 概述

提供 RESTful 和 WebSocket 接口，用于前端通信。

## 端点列表

| 端点 | 方法 | 描述 |
|------|------|------|
| `/api/v1/ws/voice` | WebSocket | 实时语音识别 |
| `/api/v1/upload` | POST | 文件上传识别 |
| `/api/v1/upload/formats` | GET | 支持的文件格式 |
| `/api/v1/health` | GET | 服务健康检查 |
| `/api/v1/health/detailed` | GET | 详细健康状态 |

## WebSocket 消息协议

### 连接建立

```
Client -> Server: WebSocket 连接
Server -> Client: {"type": "welcome", "session_id": "xxx", "config": {...}}
```

### 控制消息

```json
// 开始录音
{"type": "control", "action": "start"}

// 停止录音
{"type": "control", "action": "stop"}

// 获取状态
{"type": "status"}
```

### 音频消息

```json
// 发送二进制音频数据 (PCM 16kHz mono)
{"type": "audio", "data": "<base64>"}

// 或直接发送二进制帧
```

### 识别结果

```json
// 中间结果
{"type": "transcript", "data": {"text": "...", "start_time": 0.0, "end_time": 3.0}}

// 最终结果
{"type": "final", "data": {"text": "...", "segments": [...]}}

// 会议摘要
{"type": "summary", "data": {"summary": "...", "key_points": [...], "action_items": [...]}}

// 错误
{"type": "error", "message": "..."}
```

## 文件上传

**请求**: `POST /api/v1/upload`
**Content-Type**: `multipart/form-data`
**表单字段**:
- `file`: 音频文件 (最大 512MB)
- `engine`: 可选，指定 ASR 引擎

**响应**:
```json
{
  "session_id": "xxx",
  "status": "processing"
}
```

轮询或使用 WebSocket 获取结果。

## 健康检查

**响应**:
```json
{
  "status": "healthy",
  "timestamp": "2026-04-06T10:00:00Z",
  "version": "1.0.0"
}
```
```

- [ ] **Step 2: 创建 app/api/v1/CLAUDE.md**

```markdown
# AI 代理指令 - API 路由

## 文件说明

| 文件 | 职责 |
|------|------|
| `ws.py` | WebSocket 实时语音识别，`VoiceSession` 管理会话生命周期 |
| `upload.py` | 文件上传处理，`FileUploadSession` 管理上传会话 |
| `health.py` | 健康检查端点 |

## VoiceSession 状态机

```
IDLE -> CONNECTED -> RECORDING -> PROCESSING -> COMPLETED
                  \-> ERROR -> IDLE
```

## 关键类

### VoiceSession (ws.py)

```python
class VoiceSession:
    session_id: str
    status: SessionStatus
    audio_chunks: list[bytes]  # 累积的音频数据

    async def handle_control(action: str)    # 处理 start/stop
    async def process_audio(data: bytes)    # 处理音频帧
    async def run_recognition()              # 实时识别循环
    async def _process_after_stop()         # stop 后处理
```

### FileUploadSession (upload.py)

```python
class FileUploadSession:
    session_id: str
    file_path: Path
    status: UploadStatus

    async def process_file()  # 执行识别和分析
    async def get_result()    # 获取结果
```

## 扩展指南

### 新增 API 端点

1. 在 `app/api/v1/` 创建新文件
2. 在 `app/api/v1/__init__.py` 注册路由
3. 使用 Pydantic 定义请求/响应模型
4. 添加类型注解和文档字符串

### WebSocket 新消息类型

1. 在 `ws.py` 的 `handle_message()` 添加处理逻辑
2. 在 `frontend/src/api/types.ts` 添加对应类型
3. 更新本文档的消息协议部分
```
```

- [ ] **Step 3: Commit**

```bash
git add backend/app/api/v1/README.md backend/app/api/v1/CLAUDE.md
git commit -m "docs(backend/api): add README and CLAUDE.md"
```

---

#### Task 3: ASR 适配器文档 (`app/core/asr/`)
**Files:**
- Create: `backend/app/core/asr/README.md`
- Create: `backend/app/core/asr/CLAUDE.md`

- [ ] **Step 1: 创建 app/core/asr/README.md**

```markdown
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
```

- [ ] **Step 2: 创建 app/core/asr/CLAUDE.md**

```markdown
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
```
```

- [ ] **Step 3: Commit**

```bash
git add backend/app/core/asr/README.md backend/app/core/asr/CLAUDE.md
git commit -m "docs(backend/asr): add README and CLAUDE.md"
```

---

#### Task 4: 音频分析器文档 (`app/core/audio_analyzer/`)
**Files:**
- Create: `backend/app/core/audio_analyzer/README.md`
- Create: `backend/app/core/audio_analyzer/CLAUDE.md`

- [ ] **Step 1: 创建 app/core/audio_analyzer/README.md**

```markdown
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
```
```

- [ ] **Step 2: 创建 app/core/audio_analyzer/CLAUDE.md**

```markdown
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
```
```

- [ ] **Step 3: Commit**

```bash
git add backend/app/core/audio_analyzer/README.md backend/app/core/audio_analyzer/CLAUDE.md
git commit -m "docs(backend/audio_analyzer): add README and CLAUDE.md"
```

---

#### Task 5: 实时说话人识别文档 (`app/core/realtime_spk/`)
**Files:**
- Create: `backend/app/core/realtime_spk/README.md`
- Create: `backend/app/core/realtime_spk/CLAUDE.md`

- [ ] **Step 1: 创建 app/core/realtime_spk/README.md**

```markdown
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
```
```

- [ ] **Step 2: 创建 app/core/realtime_spk/CLAUDE.md**

```markdown
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
```
```

- [ ] **Step 3: Commit**

```bash
git add backend/app/core/realtime_spk/README.md backend/app/core/realtime_spk/CLAUDE.md
git commit -m "docs(backend/realtime_spk): add README and CLAUDE.md"
```

---

#### Task 6: 其他后端模块文档
**Files:**
- Create: `backend/app/core/audio_cache.py` 的文档注释
- Create: `backend/app/core/llm_analyzer.py` 的文档注释
- Create: `backend/app/core/parser/meeting_info.py` 的文档注释
- Create: `backend/app/models/audio.py` 的文档注释
- Modify: `backend/app/config.py` (如需要)

- [ ] **Step 1: 为 audio_cache.py 添加 docstring**

检查文件并添加模块级文档：

```python
"""
音频缓存模块

将录音数据保存到本地文件系统，支持 WAV 格式转换。

使用方式:
    from app.core.audio_cache import AudioCache

    cache = AudioCache(cache_dir=Path("audio_cache"))
    file_path = await cache.save_audio(audio_data, session_id)
```

- [ ] **Step 2: 为 llm_analyzer.py 添加 docstring**

```python
"""
LLM 分析模块

调用 LLM 生成会议摘要、关键点、行动项。

支持多种 LLM 提供商，通过 LLM_PROVIDER 环境变量配置。
```

- [ ] **Step 3: 为 parser/meeting_info.py 添加 docstring**

```python
"""
会议信息解析模块

从识别文本中提取：
- 说话人名称 (speaker)
- 会议主题 (topic)
- 章节结构 (chapter)
- 角色 (role)
```

- [ ] **Step 4: 为 models/audio.py 添加 docstring**

```python
"""
数据模型定义

Pydantic 模型用于 API 请求/响应验证。
```

- [ ] **Step 5: Commit**

```bash
git add backend/app/core/audio_cache.py backend/app/core/llm_analyzer.py
git add backend/app/core/parser/meeting_info.py backend/app/models/audio.py
git commit -m "docs(backend): add docstrings to core modules"
```

---

### 前端任务

#### Task 7: 前端根目录文档 (`frontend/src/`)
**Files:**
- Create: `frontend/README.md`
- Create: `frontend/CLAUDE.md`

- [ ] **Step 1: 创建 frontend/README.md**

```markdown
# 会议语音助手 - 前端

## 概述

Vue 3 + TypeScript 前端，提供实时语音识别界面。

## 技术栈

- **框架**: Vue 3 (Composition API)
- **构建**: Vite
- **状态管理**: Pinia
- **样式**: CSS (自定义)

## 核心功能

| 功能 | 组件/模块 |
|------|-----------|
| 录音控制 | `AudioRecorder.vue`, `useAudioRecorder.ts` |
| WebSocket 通信 | `useWebSocket.ts`, `api/websocket.ts` |
| 实时转写 | `TranscriptPanel.vue` |
| 波形显示 | `AudioWaveform.vue` |
| 会议信息 | `MeetingInfo.vue` |
| 摘要展示 | `SummaryPanel.vue` |
| 文件上传 | `FileUploader.vue` |

## 快速开始

```bash
cd frontend
npm install
npm run dev
```

访问 http://localhost:5173

## 目录结构

```
src/
├── api/
│   ├── websocket.ts    # WebSocket 客户端封装
│   └── types.ts        # TypeScript 类型定义
├── components/         # Vue 组件
├── composables/        # 组合式函数
│   ├── useAudioRecorder.ts  # 录音逻辑
│   └── useWebSocket.ts       # WebSocket 连接
├── stores/
│   └── meeting.ts      # Pinia 状态管理
├── App.vue
└── main.ts
```

## 状态管理 (Pinia Store)

`meeting.ts` store 管理以下状态：

```typescript
interface MeetingState {
  status: 'idle' | 'connecting' | 'connected' | 'recording' | 'processing' | 'completed' | 'error'
  sessionId: string | null
  transcripts: TranscriptSegment[]
  summary: MeetingSummary | null
  speakers: Speaker[]
}
```
```

- [ ] **Step 2: 创建 frontend/CLAUDE.md**

```markdown
# AI 代理指令 - 前端

## 模块职责

前端负责：
1. 录音采集 (MediaRecorder API)
2. WebSocket 实时通信
3. 识别结果实时展示
4. 状态管理 (Pinia)

## 关键文件

| 文件 | 用途 |
|------|------|
| `composables/useAudioRecorder.ts` | 录音控制核心 |
| `composables/useWebSocket.ts` | WebSocket 连接管理 |
| `stores/meeting.ts` | 全局状态 |
| `api/websocket.ts` | WebSocket 客户端封装 |
| `api/types.ts` | 类型定义 |

## 组件关系

```
App.vue
├── ControlBar.vue           # 连接/录音控制
├── AudioRecorder.vue        # 录音按钮
│   └── AudioWaveform.vue    # 波形显示
├── TranscriptPanel.vue       # 转写结果
├── MeetingInfo.vue          # 会议信息
├── SummaryPanel.vue         # 摘要结果
└── FileUploader.vue         # 文件上传
```

## WebSocket 消息流

```typescript
// 连接
const ws = useWebSocket()
await ws.connect()

// 发送控制
ws.send({ type: 'control', action: 'start' })

// 发送音频 (每 100ms)
ws.sendAudio(audioChunk)

// 接收结果
ws.onMessage((msg) => {
  if (msg.type === 'transcript') {
    store.addTranscript(msg.data)
  }
})
```

## 代码规范

- 使用 `<script setup lang="ts">` 语法
- 组件文件名使用 PascalCase
- Composables 使用 use 前缀
- 类型定义放在 `api/types.ts`
```

- [ ] **Step 3: Commit**

```bash
git add frontend/README.md frontend/CLAUDE.md
git commit -m "docs(frontend): add README and CLAUDE.md"
```

---

#### Task 8: 前端 API 模块文档 (`frontend/src/api/`)
**Files:**
- Create: `frontend/src/api/README.md`
- Create: `frontend/src/api/CLAUDE.md`

- [ ] **Step 1: 创建 frontend/src/api/README.md**

```markdown
# API 客户端文档

## 概述

封装 WebSocket 通信和类型定义。

## 文件

| 文件 | 职责 |
|------|------|
| `websocket.ts` | WebSocket 客户端封装 |
| `types.ts` | TypeScript 类型定义 |

## WebSocket 使用方式

```typescript
import { useWebSocket } from './composables/useWebSocket'

const ws = useWebSocket({
  url: 'ws://localhost:8000/api/v1/ws/voice',
  onMessage: (msg) => {
    console.log('Received:', msg)
  },
  onError: (err) => {
    console.error('Error:', err)
  },
  onOpen: () => {
    console.log('Connected')
  },
})

// 连接
await ws.connect()

// 发送控制消息
ws.send({ type: 'control', action: 'start' })

// 发送音频数据
ws.sendAudio(audioChunk: Blob)

// 断开
ws.disconnect()
```

## 消息类型 (types.ts)

```typescript
// 客户端 -> 服务端
type ClientMessage =
  | { type: 'control'; action: 'start' | 'stop' | 'status' }
  | { type: 'audio'; data: string }  // base64

// 服务端 -> 客户端
type ServerMessage =
  | { type: 'welcome'; session_id: string; config: Config }
  | { type: 'transcript'; data: TranscriptSegment }
  | { type: 'final'; data: TranscriptResult }
  | { type: 'summary'; data: MeetingSummary }
  | { type: 'error'; message: string }
```

## 配置

`VITE_WS_URL` 环境变量配置 WebSocket 地址，默认 `ws://localhost:8000/api/v1/ws/voice`。
```

- [ ] **Step 2: 创建 frontend/src/api/CLAUDE.md**

```markdown
# AI 代理指令 - API 模块

## WebSocket 客户端 (websocket.ts)

```typescript
interface UseWebSocketOptions {
  url: string
  onMessage: (msg: ServerMessage) => void
  onError?: (err: Event) => void
  onOpen?: () => void
  onClose?: () => void
}

function useWebSocket(options: UseWebSocketOptions): {
  connect(): Promise<void>
  send(msg: object): void
  sendAudio(chunk: Blob): void
  disconnect(): void
  isConnected(): boolean
}
```

## 消息处理流程

1. `useWebSocket` 接收原始消息
2. 根据 `msg.type` 分发到对应处理器
3. 组件通过 `onMessage` 回调接收

## 扩展指南

### 新增消息类型

1. 在 `types.ts` 添加新类型定义
2. 在 `useWebSocket.ts` 添加处理逻辑
3. 更新本文档

### 二进制数据

音频数据使用 `sendAudio(chunk: Blob)` 发送，内部自动处理 base64 编码。
```
```

- [ ] **Step 3: Commit**

```bash
git add frontend/src/api/README.md frontend/src/api/CLAUDE.md
git commit -m "docs(frontend/api): add README and CLAUDE.md"
```

---

#### Task 9: 前端 Composables 文档 (`frontend/src/composables/`)
**Files:**
- Create: `frontend/src/composables/README.md`
- Create: `frontend/src/composables/CLAUDE.md`

- [ ] **Step 1: 创建 frontend/src/composables/README.md**

```markdown
# Composables 文档

## 概述

Vue 3 组合式函数封装复用逻辑。

## 文件

| 文件 | 职责 |
|------|------|
| `useAudioRecorder.ts` | 录音采集控制 |
| `useWebSocket.ts` | WebSocket 连接管理 |

## useAudioRecorder

```typescript
const {
  isRecording,        // 是否正在录音
  audioLevel,         // 当前音频级别 (0-1)
  startRecording,     // 开始录音
  stopRecording,      // 停止录音
  getAudioChunk,      // 获取音频块 (Promise)
} = useAudioRecorder({
  onAudioData?: (chunk: Blob) => void
})
```

### 使用示例

```typescript
const recorder = useAudioRecorder({
  onAudioData: (chunk) => {
    ws.sendAudio(chunk)
  }
})

// 开始
await recorder.startRecording()

// 停止
const finalChunk = await recorder.stopRecording()
```

## useWebSocket

```typescript
const {
  isConnected,       // 连接状态
  connect,            // 建立连接
  disconnect,         // 断开连接
  send,               // 发送消息
  sendAudio,          // 发送音频
  onMessage,          // 消息回调
} = useWebSocket(options)
```

### 使用示例

```typescript
const ws = useWebSocket({
  url: 'ws://localhost:8000/api/v1/ws/voice',
  onMessage: (msg) => {
    if (msg.type === 'transcript') {
      store.addTranscript(msg.data)
    }
  }
})

await ws.connect()
ws.send({ type: 'control', action: 'start' })
```
```

- [ ] **Step 2: 创建 frontend/src/composables/CLAUDE.md**

```markdown
# AI 代理指令 - Composables

## useAudioRecorder

### 实现细节

使用 Web Audio API 和 MediaRecorder API：

```typescript
// 内部实现
const audioContext = new AudioContext()
const mediaStream = await navigator.mediaDevices.getUserMedia({ audio: true })
const mediaRecorder = new MediaRecorder(mediaStream, {
  mimeType: 'audio/webm;codecs=opus'
})
```

### 配置选项

```typescript
interface RecorderOptions {
  onAudioData?: (chunk: Blob) => void  // 音频数据回调
  audioBitsPerSecond?: number           // 码率，默认 128000
  sampleRate?: number                   // 采样率，默认 16000
}
```

### 音频格式

输出：WebM/Opus 格式，前端通过 MediaRecorder 采集。

## useWebSocket

### 重连机制

自动重连：连接断开后最多重试 3 次，间隔 1s/2s/3s。

### 消息队列

连接断开时，发送的消息会进入队列，重连后自动发送。

## 注意事项

- `useAudioRecorder` 在 `stopRecording()` 后需要重新创建
- `getAudioChunk()` 返回 Promise，需 await
- 组件卸载时自动清理资源
```
```

- [ ] **Step 3: Commit**

```bash
git add frontend/src/composables/README.md frontend/src/composables/CLAUDE.md
git commit -m "docs(frontend/composables): add README and CLAUDE.md"
```

---

#### Task 10: 前端组件文档 (`frontend/src/components/`)
**Files:**
- Create: `frontend/src/components/README.md`
- Create: `frontend/src/components/CLAUDE.md`

- [ ] **Step 1: 创建 frontend/src/components/README.md**

```markdown
# 组件文档

## 组件列表

| 组件 | 文件 | 描述 |
|------|------|------|
| AudioRecorder | `AudioRecorder.vue` | 录音按钮 + 状态显示 |
| AudioWaveform | `AudioWaveform.vue` | 音频波形可视化 |
| ControlBar | `ControlBar.vue` | 连接控制栏 |
| FileUploader | `FileUploader.vue` | 文件上传组件 |
| MeetingInfo | `MeetingInfo.vue` | 会议信息展示 |
| SummaryPanel | `SummaryPanel.vue` | 摘要展示面板 |
| TranscriptPanel | `TranscriptPanel.vue` | 转写结果面板 |

## 组件关系

```
ControlBar
├── AudioRecorder
│   └── AudioWaveform
├── FileUploader
└── MeetingInfo

TranscriptPanel
SummaryPanel
```

## AudioRecorder

录音按钮组件，显示录音状态和音频级别。

**Props:**
```typescript
interface Props {
  isRecording: boolean
  audioLevel: number  // 0-1
}
```

**Events:**
```typescript
interface Emits {
  (e: 'start'): void
  (e: 'stop'): void
}
```

## TranscriptPanel

实时显示转写结果，支持多段落展示。

**Props:**
```typescript
interface Props {
  segments: TranscriptSegment[]
}
```

## SummaryPanel

显示会议摘要、关键点、行动项。

**Props:**
```typescript
interface Props {
  summary: MeetingSummary | null
}
```

## FileUploader

文件上传组件，支持拖拽。

**Props:**
```typescript
interface Props {
  uploading: boolean
  progress: number  // 0-100
}
```

**Events:**
```typescript
interface Emits {
  (e: 'upload', file: File): void
}
```
```

- [ ] **Step 2: 创建 frontend/src/components/CLAUDE.md**

```markdown
# AI 代理指令 - 组件

## 组件开发规范

### 命名

- 文件名：PascalCase (如 `AudioRecorder.vue`)
- 组件名：PascalCase
- Props/Emits：camelCase

### Props 定义

```typescript
<script setup lang="ts">
interface Props {
  title: string
  count?: number  // 可选 prop
}

const props = withDefaults(defineProps<Props>(), {
  count: 0
})
</script>
```

### Emits 定义

```typescript
const emit = defineEmits<{
  (e: 'update', value: string): void
  (e: 'delete'): void
}>()
```

## 状态来源

组件状态来自 `stores/meeting.ts` Pinia store：

```typescript
import { useMeetingStore } from '@/stores/meeting'

const store = useMeetingStore()
```

## 样式规范

- 使用 scoped CSS
- CSS 变量用于主题色
- 组件根元素使用 `class="component-name"`
```

- [ ] **Step 3: Commit**

```bash
git add frontend/src/components/README.md frontend/src/components/CLAUDE.md
git commit -m "docs(frontend/components): add README and CLAUDE.md"
```

---

#### Task 11: 前端 Store 文档 (`frontend/src/stores/`)
**Files:**
- Create: `frontend/src/stores/README.md`
- Create: `frontend/src/stores/CLAUDE.md`

- [ ] **Step 1: 创建 frontend/src/stores/README.md**

```markdown
# 状态管理文档

## 概述

使用 Pinia 管理全局状态。

## Store: meeting

### State

```typescript
interface MeetingState {
  status: SessionStatus
  sessionId: string | null
  transcripts: TranscriptSegment[]
  summary: MeetingSummary | null
  speakers: Speaker[]
  error: string | null
}

type SessionStatus =
  | 'idle'
  | 'connecting'
  | 'connected'
  | 'recording'
  | 'processing'
  | 'completed'
  | 'error'
```

### Actions

```typescript
// 连接 WebSocket
async function connect(): Promise<void>

// 断开连接
function disconnect(): void

// 开始录音
async function startRecording(): Promise<void>

// 停止录音
async function stopRecording(): Promise<void>

// 添加转写段落
function addTranscript(segment: TranscriptSegment): void

// 设置摘要
function setSummary(summary: MeetingSummary): void

// 清空状态
function reset(): void
```

### Getters

```typescript
// 是否可以开始录音
const canStartRecording: boolean

// 转写文本（合并所有段落）
const fullText: string

// 错误信息
const errorMessage: string | null
```
```

- [ ] **Step 2: 创建 frontend/src/stores/CLAUDE.md**

```markdown
# AI 代理指令 - Store

## Pinia Store 规范

### Store 定义

```typescript
// stores/meeting.ts
import { defineStore } from 'pinia'

export const useMeetingStore = defineStore('meeting', () => {
  // State
  const status = ref<SessionStatus>('idle')
  const sessionId = ref<string | null>(null)
  // ...

  // Getters
  const canStartRecording = computed(() =>
    status.value === 'connected'
  )

  // Actions
  async function connect() {
    // ...
  }

  return {
    status,
    sessionId,
    canStartRecording,
    connect,
    // ...
  }
})
```

## 使用方式

```typescript
// 组件中
import { useMeetingStore } from '@/stores/meeting'

const store = useMeetingStore()

// 直接使用
console.log(store.status)
store.startRecording()
```

## 持久化

当前状态不持久化，刷新页面会重置。

如需持久化，使用 `pinia-plugin-persistedstate`。
```
```

- [ ] **Step 3: Commit**

```bash
git add frontend/src/stores/README.md frontend/src/stores/CLAUDE.md
git commit -m "docs(frontend/stores): add README and CLAUDE.md"
```

---

#### Task 12: FunASR 服务文档 (`backend/funasr_service/`)
**Files:**
- Create: `backend/funasr_service/README.md`
- Create: `backend/funasr_service/CLAUDE.md`

- [ ] **Step 1: 创建 funasr_service/README.md**

```markdown
# FunASR 服务

## 概述

独立的 FunASR 说话人分离服务，提供 WebSocket 接口。

## 架构

```
主后端 (8000)  --WebSocket-->  FunASR 服务 (8001)
                                   |
                                   v
                            FunASR 模型 (本地)
```

## 启动

```bash
cd backend/funasr_service
pip3 install -r requirements.txt
python3 -m uvicorn main:app --host 0.0.0.0 --port 8001
```

## API 端点

| 端点 | 方法 | 描述 |
|------|------|------|
| `/asr` | WebSocket | 流式 ASR 识别 |
| `/health` | GET | 健康检查 |

## WebSocket 消息

### 请求
```json
{"audio": "<base64>", "enable_spks": true}
```

### 响应
```json
{
  "text": "识别文本",
  "spks": [{"id": 0, "name": "spk_0"}],
  "start_time": 0.0,
  "end_time": 3.0
}
```
```

- [ ] **Step 2: 创建 funasr_service/CLAUDE.md**

```markdown
# AI 代理指令 - FunASR 服务

## 文件结构

| 文件 | 职责 |
|------|------|
| `main.py` | FastAPI 应用入口 |
| `api.py` | WebSocket 路由 |
| `model_loader.py` | 模型加载管理 |
| `realtime/` | 实时识别相关 |

## 扩展

如需更换模型，修改 `model_loader.py` 中的模型路径和配置。
```
```

- [ ] **Step 3: Commit**

```bash
git add backend/funasr_service/README.md backend/funasr_service/CLAUDE.md
git commit -m "docs(funasr_service): add README and CLAUDE.md"
```

---

## 任务总结

| 序号 | 模块 | 文件数 | 状态 |
|------|------|--------|------|
| 1 | 后端根目录 | 2 | ⬜ |
| 2 | API 路由 | 2 | ⬜ |
| 3 | ASR 适配器 | 2 | ⬜ |
| 4 | 音频分析器 | 2 | ⬜ |
| 5 | 说话人识别 | 2 | ⬜ |
| 6 | 其他核心模块 | 4 | ⬜ |
| 7 | 前端根目录 | 2 | ⬜ |
| 8 | API 模块 | 2 | ⬜ |
| 9 | Composables | 2 | ⬜ |
| 10 | 组件 | 2 | ⬜ |
| 11 | Store | 2 | ⬜ |
| 12 | FunASR 服务 | 2 | ⬜ |

**总计**: 26 个新文档文件

---

## 自检清单

- [ ] 所有 README.md 包含：概述、目录结构、快速开始
- [ ] 所有 CLAUDE.md 包含：AI 代理指令、关键类/函数说明、扩展指南
- [ ] 所有文件使用中文
- [ ] 代码示例经过验证
- [ ] Commit 消息符合规范

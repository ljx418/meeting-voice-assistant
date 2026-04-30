# 架构概述

## 系统架构图

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              前端 (Vue + Vite)                              │
├─────────────────────────────────────────────────────────────────────────────┤
│  [麦克风] --> [MediaRecorder] --> [AudioContext]                            │
│       │              │                                                       │
│       │              ▼                                                       │
│       │       [WebSocket Client]                                           │
│       │             │     │                                                 │
│       │             │     │ (音频流)                                        │
│       │             │     ▼                                                 │
│       │             │  [后端 WebSocket]                                     │
│       │             │                                                       │
│       │             │ (识别结果)                                             │
│       │             ▼                                                       │
│       └──────> [TranscriptPanel]                                           │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
                              │
                              │ HTTP/WS
                              ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              后端 (FastAPI)                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  [WebSocket Endpoint]                                                        │
│         │                                                                   │
│         ▼                                                                   │
│  [Audio Processor]  ──> [Buffer Management]                                 │
│         │                         │                                        │
│         │                         │ (处理后音频)                            │
│         ▼                         ▼                                        │
│  [ASR Adapter Interface]  ──> [ASR Engine: DashScope / FunASR / Mock]                                               │
│         │                                                                   │
│         │ (原始识别结果)                                                      │
│         ▼                                                                   │
│  [Semantic Parser]                                                          │
│  - SpeakerParser                                                           │
│  - RoleParser                                                              │
│  - ChapterParser                                                           │
│  - TopicParser                                                             │
│         │                                                                   │
│         ▼                                                                   │
│  [Response Formatter]                                                       │
│         │                                                                   │
│         ▼                                                                   │
│  [WebSocket Push]  ──> [前端]                                                │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

## 知识双引擎架构

项目当前除了实时会议语音链路，还增加了一条知识侧双引擎架构：

- `backend/data_service`
- `backend/app/llmwiki`
- `backend/app/graphrag`
- `/api/v1/knowledge/*`
- `/knowledge`

对应文档入口：

- [Data Service 当前架构状态](../data_service/CURRENT-STATUS.md)
- [Data Service 当前与目标差距分析](../data_service/current-vs-target-gap.md)

## 核心设计原则

### 1. 前后端分离

- 前端：Vue 3 SPA，负责 UI 交互和音频采集
- 后端：FastAPI，负责语音识别和语义解析
- 通信：WebSocket 实时传输音频和识别结果

### 2. ASR 适配器模式

```
┌─────────────────┐
│   Business Logic│
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  ASR Adapter    │  <-- 接口抽象
│     Base       │
└────────┬────────┘
         │
         ▼
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  DashScope     │     │   FunASR        │     │    Mock         │
│   Adapter      │     │   Adapter       │     │   Adapter       │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

**支持的引擎**:

| 引擎 | 说明 | 说话人分离 | 文件大小限制 |
|------|------|-----------|-------------|
| `mock` | Mock 模拟器 (默认，用于测试) | ❌ | 无限制 |
| `dashscope_realtime` | DashScope Qwen3-ASR-Flash 实时流式识别 | ❌ | 无限制 |
| `dashscope_file` | DashScope 大文件识别 (qwen3-asr-flash-filetrans) | ❌ | 512MB |
| `funasr` | FunASR 本地说话人分离 (Paraformer + CAM++) | ✅ | 无限制 |
| `funasr_realtime` | FunASR 实时语音转写 + 说话人分离 | ✅ | 无限制 |

### 3. DFX 设计

- **日志**: 分级日志 (DEBUG/INFO/WARNING/ERROR)
- **接口文档**: 自动生成 OpenAPI/Swagger
- **错误处理**: 统一的错误码和消息格式
- **健康检查**: `/api/v1/health` 端点

## 目录结构

```
meeting-voice-assistant/
├── frontend/                    # Vue + Vite 前端
│   ├── src/
│   │   ├── api/                 # API 客户端
│   │   ├── components/          # Vue 组件
│   │   ├── composables/         # Vue Composables
│   │   ├── stores/              # Pinia 状态
│   │   └── App.vue
│   └── package.json
│
├── backend/                     # Python FastAPI 后端
│   ├── app/
│   │   ├── api/                 # API 路由
│   │   ├── core/                # 核心业务
│   │   │   ├── asr/             # ASR 适配器
│   │   │   ├── parser/           # 语义解析
│   │   │   └── processor/        # 音频处理
│   │   ├── models/              # Pydantic 模型
│   │   └── utils/               # 工具函数
│   └── requirements.txt
│
└── docs/                        # 技术文档
```

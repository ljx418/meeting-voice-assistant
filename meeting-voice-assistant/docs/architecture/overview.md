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
│  [ASR Adapter Interface]  ──> [ASR Engine: SenseVoice]                       │
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
┌─────────────────┐     ┌─────────────────┐
│  SenseVoice    │     │   Whisper      │  <- 可扩展
│   Adapter      │     │   Adapter      │
└─────────────────┘     └─────────────────┘
```

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

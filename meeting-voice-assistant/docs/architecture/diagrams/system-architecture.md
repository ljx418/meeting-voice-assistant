# 会议语音助手 - 系统架构图

## 架构概览

```mermaid
graph TB
    subgraph Frontend["🌐 前端 Frontend (Vue 3 + Vite)"]
        Mic["🎤 麦克风<br/>(MediaRecorder)"]
        Waveform["📊 波形图<br/>(AudioWaveform)"]
        FileUploader["📁 文件上传<br/>(FileUploader)"]
        TranscriptPanel["📝 转写面板<br/>(TranscriptPanel)"]
        MeetingInfo["ℹ️ 会议信息<br/>(MeetingInfo)"]
        WSClient["🔌 WebSocket<br/>Client"]
    end

    subgraph Backend["⚙️ 后端 Backend (FastAPI)"]
        WSEndpoint["🌐 WebSocket<br/>/ws/voice"]
        UploadEndpoint["📤 Upload<br/>/upload"]
        AudioCache["💾 音频缓存"]
        LLMAnalyzer["🤖 LLM 分析器<br/>(qwen-plus/minimax/deepseek)"]
        ASRFactory["⚙️ ASR Factory"]
    end

    subgraph FunASRService["🔥 FunASR Service (Port 8001)"]
        FunASRAPI["🔌 API Router<br/>/recognize"]
        M4AConverter["🔄 m4a→wav<br/>(ffmpeg)"]
        FunASRModel["🧠 FunASR Model<br/>Paraformer + CAM++"]
        VAD["🎯 VAD (fsmn-vad)"]
        SPK["👥 说话人分离<br/>(CAM++)"]
        PUNC["📖 标点恢复<br/>(ct-punc)"]
    end

    subgraph CloudServices["☁️ 外部云服务"]
        DashScope["阿里云 DashScope<br/>(LLM API)"]
        MiniMax["MiniMax API"]
        DeepSeek["DeepSeek API"]
    end

    %% Frontend connections
    Mic -->|"实时音频"| WSClient
    WSClient -->|"WebSocket"| WSEndpoint
    FileUploader -->|"HTTP上传"| UploadEndpoint
    MeetingInfo --> TranscriptPanel
    WSEndpoint --> TranscriptPanel

    %% Backend connections
    WSEndpoint --> ASRFactory
    UploadEndpoint --> FunASRAPI
    AudioCache --> FunASRService
    LLMAnalyzer --> DashScope
    LLMAnalyzer --> MiniMax
    LLMAnalyzer --> DeepSeek

    %% FunASR Service connections
    FunASRAPI --> M4AConverter
    M4AConverter --> FunASRModel
    FunASRModel --> VAD
    FunASRModel --> SPK
    FunASRModel --> PUNC

    style Frontend fill:#E3F2FD,stroke:#1976D2,stroke-width:2px
    style Backend fill:#E8F5E9,stroke:#388E3C,stroke-width:2px
    style FunASRService fill:#FCE4EC,stroke:#C2185B,stroke-width:2px
    style CloudServices fill:#E1BEE7,stroke:#7B1FA2,stroke-width:2px,dashed:1
```

## 核心数据流

```mermaid
sequenceDiagram
    participant User as 用户
    participant Frontend as 前端 Vue
    participant Backend as 后端 FastAPI
    participant FunASR as FunASR Service
    participant LLM as LLM 分析器

    Note over User,LLM: 实时语音识别流程

    User->>Frontend: 开启录音
    Frontend->>Frontend: MediaRecorder 采集音频
    Frontend->>Backend: WebSocket 发送音频流
    Backend->>FunASR: 实时流式识别

    loop 实时识别
        FunASR-->>Backend: 返回带说话人的识别结果
        Backend-->>Frontend: WebSocket 推送转写片段
        Frontend->>Frontend: 实时更新转写面板
    end

    User->>Frontend: 停止录音
    Frontend->>Backend: 发送 stop 信号
    Backend->>Backend: 保存音频到缓存
    Backend->>FunASR: 文件识别（完整转写）
    FunASR-->>Backend: 完整转写结果
    Backend->>LLM: 发送转写文本
    LLM-->>Backend: 分析结果（摘要、关键点、行动项）
    Backend-->>Frontend: 最终分析结果
```

## ASR 适配器工厂模式

```mermaid
classDiagram
    class ASRAdapterBase {
        <<interface>>
        +initialize()
        +close()
        +recognize_stream()
        +recognize_file()
    }

    class FunASRAdapter {
        +endpoint: str
        +recognize_file()
    }

    class DashScopeAdapter {
        +recognize_file()
    }

    class SenseVoiceAdapter {
        +recognize_file()
    }

    class ASRFactory {
        +create(engine: str) ASRAdapterBase
    }

    ASRFactory ..> ASRAdapterBase : creates
    FunASRAdapter ..|> ASRAdapterBase
    DashScopeAdapter ..|> ASRAdapterBase
    SenseVoiceAdapter ..|> ASRAdapterBase
```

## 目录结构

```
meeting-voice-assistant/
├── frontend/                    # Vue 3 + Vite 前端
│   └── src/
│       ├── components/           # Vue 组件
│       │   ├── AudioRecorder.vue
│       │   ├── AudioWaveform.vue
│       │   ├── FileUploader.vue
│       │   ├── TranscriptPanel.vue
│       │   └── MeetingInfo.vue
│       ├── composables/           # 组合式函数
│       │   ├── useAudioRecorder.ts
│       │   └── useWebSocket.ts
│       └── stores/               # Pinia 状态
│
├── backend/                     # Python FastAPI 后端
│   ├── app/
│   │   ├── api/v1/
│   │   │   ├── ws.py            # WebSocket 端点
│   │   │   └── upload.py        # 文件上传端点
│   │   ├── core/
│   │   │   ├── asr/             # ASR 适配器
│   │   │   │   ├── base.py
│   │   │   │   ├── factory.py
│   │   │   │   ├── funasr_adapter.py
│   │   │   │   ├── dashscope.py
│   │   │   │   └── sensevoice.py
│   │   │   ├── realtime_spk/    # 实时说话人分离
│   │   │   ├── llm_analyzer.py  # LLM 分析
│   │   │   └── audio_cache.py   # 音频缓存
│   │   └── config.py
│   └── funasr_service/          # FunASR 微服务
│       ├── main.py
│       ├── api.py
│       └── model_loader.py
│
└── docs/architecture/
    └── diagrams/               # 架构图
        ├── system-architecture.drawio
        └── system-architecture.md
```

## 技术栈

| 层级 | 技术 | 说明 |
|------|------|------|
| 前端框架 | Vue 3 + TypeScript | SPA 应用 |
| 前端构建 | Vite | 开发服务器和构建工具 |
| 后端框架 | FastAPI | Python ASGI 框架 |
| 实时通信 | WebSocket | 音频流传输 |
| ASR 引擎 | FunASR | 阿里云开源语音识别 |
| 说话人分离 | CAM++ | FunASR 内置模型 |
| LLM | qwen-plus / MiniMax / DeepSeek | 会议分析 |

# CLAUDE.md

会议语音助手项目 - Claude Code 工作指南

## 项目概述

基于 Web 的实时语音识别会议助手，支持实时语音转文本、LLM 会议分析和 GraphRAG 知识图谱管理。

## 技术栈

- **前端**: Vue 3 + TypeScript + Vite + Pinia + Vue Router
- **后端**: Python FastAPI + WebSocket + SQLAlchemy
- **ASR 引擎**: 阿里云 DashScope (Qwen3-ASR-Flash) / FunASR (本地说话人分离)
- **LLM**: 阿里云 DashScope (qwen-plus)
- **知识管理**: Microsoft GraphRAG + SQLite

## 服务架构

```
┌─────────────────────────────────────────────────────────────────┐
│                     前端 (http://localhost:5173)                 │
└─────────────────────────┬───────────────────────────────────────┘
                          │ WebSocket + HTTP
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                   主后端 (localhost:8000)                         │
│  ├── /api/v1/ws/voice     WebSocket 实时语音识别                  │
│  ├── /api/v1/upload       文件上传识别                           │
│  └── /api/v1/health       健康检查                               │
├─────────────────────────────────────────────────────────────────┤
│  依赖服务                                                        │
│  ├── FunASR 服务 (localhost:8001) - 说话人分离                   │
│  └── GraphRAG 服务 (localhost:8002) - 知识图谱                    │
└─────────────────────────────────────────────────────────────────┘
```

## 目录结构

```
meeting-voice-assistant/
├── backend/
│   ├── app/
│   │   ├── api/v1/              # API 路由 (ws, upload, health)
│   │   ├── core/
│   │   │   ├── asr/             # ASR 适配器 (DashScope, FunASR, Mock)
│   │   │   ├── audio_cache.py   # 音频缓存
│   │   │   ├── llm_analyzer.py  # LLM 会议分析
│   │   │   ├── audio_analyzer/  # 深度分析 (LangChain/LangGraph)
│   │   │   ├── parser/          # 会议信息解析
│   │   │   └── realtime_spk/    # 实时说话人分离
│   │   ├── graphrag/            # GraphRAG 知识管理模块
│   │   ├── config.py            # 配置管理
│   │   └── main.py              # FastAPI 入口
│   ├── funasr_service/          # FunASR 微服务 (port 8001)
│   ├── rag_workspace/           # GraphRAG 工作目录
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── api/                 # WebSocket 客户端
│   │   ├── components/          # Vue 组件
│   │   ├── composables/         # useAudioRecorder, useWebSocket
│   │   ├── stores/              # Pinia store
│   │   ├── pages/               # MeetingPage, MeetingConsolePage, GraphRAGPage
│   │   └── router/              # Vue Router
│   └── package.json
├── docs/                         # 技术文档
└── docker-compose.yml
```

## 运行命令

需要同时启动 4 个服务：

```bash
# 1. FunASR 服务 (说话人分离, port 8001)
cd backend
python3 -m uvicorn funasr_service.main:app --host 0.0.0.0 --port 8001

# 2. 主后端 (语音识别 API, port 8000)
cd backend
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000

# 3. GraphRAG 服务 (知识图谱, port 8002)
cd backend
python3 -m uvicorn app.graphrag.main:app --host 0.0.0.0 --port 8002

# 4. 前端 (port 5173)
cd frontend
npm run dev
```

访问地址：
- 前端: http://localhost:5173
- 后端 API: http://localhost:8000
- GraphRAG API: http://localhost:8002
- FunASR 服务: http://localhost:8001

## 核心功能

### 1. 实时语音识别 (WebSocket)

**流程**: 前端 → `ws://localhost:8000/api/v1/ws/voice` → 实时转写 → 返回结果

- 音频格式: 16kHz, 16-bit mono PCM
- 控制消息: `{"type": "control", "action": "start|stop|pause|resume"}`
- 二进制音频数据每 100ms 发送一次
- 后端使用 VAD (语音活动检测) 决定提交时机

**关键文件**:
- `backend/app/api/v1/ws.py` - VoiceSession 类，核心会话逻辑
- `frontend/src/composables/useAudioRecorder.ts` - 录音逻辑
- `frontend/src/api/websocket.ts` - WebSocket 客户端

### 2. 文件上传识别

- 端点: `POST /api/v1/upload`
- 支持格式: mp3, mp4, wav, m4a, ogg, flac, webm
- 最大文件: 512MB
- 支持说话人分离 (使用 FunASR)

### 3. ASR 引擎选择

| 引擎 | 说话人分离 | 文件大小 | 延迟 | 需要服务 |
|------|-----------|---------|------|---------|
| `dashscope_realtime` | ❌ | 无限制 | ~2秒 | DashScope API |
| `dashscope_file` | ❌ | 512MB | 取决于文件 | DashScope API |
| `funasr` | ✅ | 无限制 | 较慢 | FunASR (port 8001) |

配置: `ASR_ENGINE` 环境变量 (见 `backend/app/.env`)

### 4. LLM 会议分析

- 模型: qwen-plus (DashScope)
- 分析内容: 摘要、关键点、行动项、主题
- 深度分析: 章节检测、说话人角色识别

### 5. GraphRAG 知识管理

GraphRAG 服务运行在 port 8002，提供知识图谱功能：

- 文档索引 (实体、关系抽取)
- 知识查询 (local/global 方法)
- 图谱可视化
- 社区检测与摘要

**API 端点**:
- `POST /api/v1/index/` - 文档索引
- `POST /api/v1/query/` - 知识查询
- `GET /api/v1/graph/` - 图谱数据

## 配置说明

### 后端环境变量 (`backend/app/.env`)

```env
# ASR 引擎
ASR_ENGINE=funasr                    # mock, dashscope, dashscope_file, dashscope_realtime, funasr
FUNASR_ENDPOINT=http://localhost:8001
DASHSCOPE_API_KEY=sk-xxx

# LLM
LLM_PROVIDER=dashscope
LLM_API_KEY=sk-xxx
LLM_MODEL=qwen-plus

# 音频缓存
AUDIO_CACHE_ENABLED=true
AUDIO_CACHE_DIR=./audio_cache
```

### GraphRAG 配置 (`backend/app/graphrag/config.py`)

```env
GRAPHRAG_SERVICE_PORT=8002
LLM_PROVIDER=minimax
LLM_MODEL=MiniMax-M2.1
GRAPHRAG_WORKSPACE=./rag_workspace
```

## 前端路由

| 路由 | 页面 | 描述 |
|------|------|------|
| `/` | MeetingPage | 会议助手主页面 |
| `/console` | MeetingConsolePage | 上传文件管理 (深色主题) |
| `/graphrag` | GraphRAGPage | 知识图谱管理页面 |

## 已知问题

### 1. macOS 系统代理导致 Ollama embeddings 502 错误

**问题**: macOS 网络代理拦截 HTTP 请求，httpx 默认使用系统代理
**解决方案**: 创建 patch 脚本禁用 httpx 的 trust_env，参见 `backend/app/graphrag/core/microsoft/adapter.py`

### 2. GraphRAG 文档删除

删除源文件后索引数据仍保留在 output 目录，无法单独删除某个文档的索引。

## 子目录 CLAUDE.md

项目各子目录有独立的 CLAUDE.md 提供详细指导：

- `backend/CLAUDE.md` - 后端整体架构、ASR 适配器、GraphRAG 详细文档
- `backend/app/api/v1/CLAUDE.md` - API 路由详细说明
- `backend/app/core/asr/CLAUDE.md` - ASR 适配器开发指南
- `backend/app/core/audio_analyzer/CLAUDE.md` - 深度音频分析
- `backend/funasr_service/CLAUDE.md` - FunASR 微服务
- `frontend/CLAUDE.md` - 前端整体说明
- `frontend/src/components/CLAUDE.md` - Vue 组件说明
- `frontend/src/composables/CLAUDE.md` - Composables 说明
- `frontend/src/stores/CLAUDE.md` - Pinia Store 说明

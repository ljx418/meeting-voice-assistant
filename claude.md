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

## 认证机制

项目采用 **静态 API Key** 认证方案（参见 `docs/architecture/ADR-001-api-authentication.md`，状态：Accepted）。

### 工作原理

```env
# 后端 .env - 留空则禁用认证（本地开发模式）
API_KEY=your-secret-api-key-here

# 前端 .env
VITE_API_KEY=your-secret-api-key-here
```

### 认证方式

| 端点 | 认证方式 |
|------|---------|
| WebSocket `ws://host/api/v1/ws/voice` | URL query param: `?api_key=<key>` |
| HTTP 请求 | Header: `X-API-Key: <key>` |
| `GET /health` | **不保护** - 健康检查需公开 |
| `GET /upload/formats` | **不保护** - 公开信息 |

### WebSocket 认证示例

```typescript
// 前端 WebSocket 连接
const wsUrl = apiKey
  ? `ws://localhost:8000/api/v1/ws/voice?api_key=${encodeURIComponent(apiKey)}`
  : 'ws://localhost:8000/api/v1/ws/voice'
```

### 未受保护的端点

以下端点无需认证：
- `GET /api/v1/health` - 健康检查
- `GET /api/v1/upload/formats` - 支持的音频格式

### 安全注意事项

- API Key 在 URL query 中传输，服务器日志会记录，需配置日志过滤
- 密钥无过期，轮换需重启服务
- 未来升级路径：多用户需求触发时迁移至 JWT（见 ADR-001 Migration Path）

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

## AgentTeam 团队

项目有一个预配置的 AgentTeam，可用于真正的协作开发。

**团队名称**: **`meeting-assistant`**

### ⚠️ 核心定义：激活团队 = AgentTeam 协作

**当用户说"激活团队"、"启动团队"或类似指令时，必须使用 AgentTeam 协作模式：**

1. **第一步**：用 `Agent` 工具创建并启动团队成员
2. **第二步**：主对话框直接承担 team-lead 角色，向各成员发送讨论任务并汇总结果

### AgentTeam 协作流程

```
用户: "激活团队，讨论 V2.0 计划"
    ↓
1. 用 Agent 工具启动所有团队成员（run_in_background: true）
2. 主对话框直接向各成员发送讨论任务（无需经过 team-lead）
3. 成员分析后，SendMessage 回复给主对话框
4. 主对话框汇总所有成员的讨论意见
5. 主对话框生成完整报告给用户
```

### 关键原则

| 原则 | 说明 |
|------|------|
| 主对话框 = team-lead | 激活团队时，主对话框直接承担协调者角色，无需另找 team-lead |
| 先创建后通信 | 必须先用 Agent 工具创建成员，才能用 SendMessage 与其通信 |
| 主对话框直接协调 | 主对话框直接向各成员发送任务并收集反馈，不经过中间人 |

### 激活团队完整步骤

当用户说"激活团队"时，执行：

```typescript
// 1. 先创建并启动所有团队成员（run_in_background: true）
Agent({ name: "backend-dev", run_in_background: true, ... })
Agent({ name: "frontend-dev", run_in_background: true, ... })
Agent({ name: "architect", run_in_background: true, ... })
Agent({ name: "product-manager", run_in_background: true, ... })
Agent({ name: "code-reviewer", run_in_background: true, ... })

// 2. 主对话框直接承担 team-lead 角色，向各成员发送讨论任务
SendMessage({
  to: "backend-dev",
  message: "讨论主题：后端开发计划"
})
SendMessage({
  to: "frontend-dev",
  message: "讨论主题：前端开发计划"
})
// ... 向其他成员发送任务

// 3. 收到各成员回复后，主对话框汇总结果生成报告
```

### 常驻团队成员（5人）

"激活团队"时，以下成员**必须在线**：

| Agent | 角色 | 工作目录 |
|-------|------|---------|
| `backend-dev` | 后端开发工程师 | backend |
| `frontend-dev` | 前端开发工程师 | frontend |
| `architect` | 软件架构师 | 项目根目录 |
| `product-manager` | 产品经理 | 项目根目录 |
| `code-reviewer` | 代码审查专家 | 项目根目录 |

### 全部团队成员（5人）

激活团队时，向以下**所有**成员发送讨论任务：

| Agent | 角色 |
|-------|------|
| `backend-dev` | 后端开发工程师 |
| `frontend-dev` | 前端开发工程师 |
| `architect` | 软件架构师 |
| `product-manager` | 产品经理 |
| `code-reviewer` | 代码审查专家 |

### 工作规则

**优先使用本项目团队成员**：
- 优先使用本项目已经存在的团队成员
- 优先使用本项目团队的成员描述（见下方团队职责表格）
- 避免创建新的临时 agent，优先复用现有成员

**API 访问重试规则**：
- 如果 leader 发现团队成员无法访问 API，应让该成员重试
- 重试最多 3 次
- 如果 3 次重试都失败，需要在控制台反馈此问题

### 全部团队成员

| Agent | 角色 | 工作目录 |
|-------|------|---------|
| `team-lead` | 团队负责人 | 项目根目录 |
| `backend-dev` | 后端开发工程师 | backend |
| `frontend-dev` | 前端开发工程师 | frontend |
| `architect` | 软件架构师 | 项目根目录 |
| `product-manager` | 产品经理 | 项目根目录 |
| `code-reviewer` | 代码审查专家 | 项目根目录 |

### 激活团队（真正的协作）

当用户说"激活团队"、"启动团队"或类似指令时：

1. 主对话框直接向所有成员发送讨论任务
2. 各成员通过 `SendMessage` 回复分析
3. 主对话框汇总结果

**示例**：
```
SendMessage({
  to: "backend-dev",
  message: "讨论主题：Sprint 3 后端开发计划"
})
SendMessage({
  to: "frontend-dev",
  message: "讨论主题：Sprint 3 前端开发计划"
})
```

**注意**：所有 5 个成员必须在线参与讨论。

配置文件位置：`.claude/teams/assistant/config.json`

### 团队职责

| Agent | 职责 |
|-------|------|
| `backend-dev` | API开发、ASR适配器、LLM模块、GraphRAG，可自主创建 subagent |
| `frontend-dev` | Vue组件开发、WebSocket实时通信、UI优化，可自主创建 subagent |
| `architect` | 技术规范制定、复杂问题解决 |
| `product-manager` | 产品规划、需求分析、PRD编写、优先级 |
| `code-reviewer` | 代码质量评审、安全检查、性能评估 |

### 后端/前端开发自主创建 subagent

**backend-dev 和 frontend-dev 被授权可以自行创建 subagent**：

当遇到以下情况时，可以创建临时 subagent：
- 需要并行处理多个独立任务
- 需要特定领域专家协助分析
- 需要加速开发进度

**创建方式**：
```typescript
// backend-dev 或 frontend-dev 可以直接使用
Agent({
  description: "任务描述",
  prompt: "具体任务...",
  run_in_background: true,
  subagent_type: "general-purpose"
})
```

**约束**：
- 只创建与当前任务相关的 subagent
- 避免创建持久化 Agent（除非明确需要）
- subagent 完成工作后自动结束

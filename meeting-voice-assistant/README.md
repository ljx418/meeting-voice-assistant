# 会议语音助手

> 基于 Web 的实时语音识别会议助手，融合 LLM 智能分析与 GraphRAG 知识图谱技术

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Vue 3](https://img.shields.io/badge/Vue-3-42b883.svg)](https://vuejs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688.svg)](https://fastapi.tiangolo.com/)

---

## 核心功能

### 1. 实时语音识别
- WebSocket 实时转写，延迟 ~2-3 秒
- 支持中英文混合识别
- 语音活动检测（VAD），自动断句

### 2. 说话人分离
- FunASR 本地模型，识别不同发言人
- 自动标注 "发言人 A/B/C..."
- 说话人时间统计与可视化

### 3. 智能会议分析
- LLM 自动生成会议摘要
- 关键决策点提取
- 行动项（待办）识别
- 主题章节自动划分

### 4. 知识图谱管理（GraphRAG）
- 会议内容向量化索引
- 基于知识图谱的智能问答
- 社区检测与语义聚类
- 图谱可视化

### 5. 音频播控
- 支持全时长拖拽定位
- 章节级跳转
- 说话人时段高亮

---

## 系统架构

```
┌─────────────────────────────────────────────────────────────────┐
│                     前端 (http://localhost:5173)                  │
│              Vue 3 + TypeScript + Pinia + Vue Router             │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────┐  │
│  │   MeetingPage     │  │ MeetingConsolePage│  │  GraphRAGPage │  │
│  │   (上传/录音)     │  │   (会议回放)     │  │  (知识图谱)  │  │
│  └────────┬─────────┘  └────────┬─────────┘  └──────┬───────┘  │
│           │                    │                    │           │
│           └────────────────────┼────────────────────┘           │
│                                │                                │
│              WebSocket (实时)  │  HTTP REST                   │
├────────────────────────────────┼───────────────────────────────┤
│                          主后端 (8000)                            │
│                      FastAPI + ASR + LLM                         │
│  ┌─────────────┐  ┌──────────────┐  ┌─────────────────────────┐  │
│  │ WS 实时识别  │  │  文件上传API  │  │   LLM 会议分析          │  │
│  └──────┬──────┘  └──────┬───────┘  └───────────┬─────────────┘  │
│         │                │                       │                 │
│         └────────────────┼───────────────────────┘                 │
│                          │                                         │
│         ┌────────────────┴────────────────┐                     │
│         ▼                                 ▼                     │
│  ┌─────────────┐               ┌─────────────────┐              │
│  │  FunASR     │               │   DashScope     │              │
│  │  (8001)     │               │   (云 API)      │              │
│  │  说话人分离  │               │   ASR/LLM       │              │
│  └─────────────┘               └─────────────────┘              │
│                                                                   │
│                          GraphRAG (8002)                          │
│                    Microsoft GraphRAG + SQLite                   │
└─────────────────────────────────────────────────────────────────┘
```

---

## 技术栈

### 前端
| 技术 | 说明 |
|------|------|
| Vue 3.4+ | 渐进式前端框架 |
| TypeScript 5 | 类型安全 |
| Vite 5 | 快速构建工具 |
| Pinia | 状态管理 |
| Vue Router 4 | 页面路由 |
| D3.js | 知识图谱可视化 |

### 后端
| 技术 | 说明 |
|------|------|
| Python 3.11 | 运行环境 |
| FastAPI | 高性能 Web 框架 |
| WebSocket | 实时双向通信 |
| SQLAlchemy | 异步数据库 ORM |
| Pydantic | 数据验证 |

### AI 引擎
| 技术 | 说明 |
|------|------|
| DashScope (qwen3-asr-flash) | 云端 ASR 识别 |
| FunASR (Paraformer + CAM++) | 本地说话人分离 |
| DashScope (qwen-plus) | LLM 会议分析 |
| Microsoft GraphRAG | 知识图谱索引与检索 |

---

## 目录结构

```
meeting-voice-assistant/
├── backend/
│   ├── app/
│   │   ├── api/v1/              # REST/WebSocket API
│   │   │   ├── ws.py           # 实时语音识别
│   │   │   ├── upload.py       # 文件上传与处理
│   │   │   └── health.py        # 健康检查
│   │   ├── core/
│   │   │   ├── asr/            # ASR 引擎适配器
│   │   │   │   ├── factory.py   # 工厂模式创建引擎
│   │   │   │   ├── dashscope.py
│   │   │   │   ├── funasr_adapter.py
│   │   │   │   └── mock.py      # 测试用 Mock
│   │   │   ├── llm_analyzer.py # LLM 会议分析
│   │   │   ├── audio_analyzer/ # 深度音频分析
│   │   │   ├── parser/          # 会议信息解析
│   │   │   └── realtime_spk/    # 实时说话人分离
│   │   ├── graphrag/           # GraphRAG 知识管理
│   │   ├── config.py           # 配置管理
│   │   └── main.py             # FastAPI 入口
│   ├── funasr_service/         # FunASR 微服务 (port 8001)
│   ├── rag_workspace/           # GraphRAG 工作目录
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── api/                # API 客户端封装
│   │   ├── components/          # Vue 组件
│   │   │   ├── AudioTimeline.vue    # 音频时间线
│   │   │   ├── ChapterList.vue      # 章节列表
│   │   │   ├── FileUploader.vue     # 文件上传
│   │   │   ├── GraphRAGPanel.vue   # 知识图谱面板
│   │   │   ├── NotesPanel.vue       # AI 纪要
│   │   │   └── SummaryPanel.vue     # 摘要面板
│   │   ├── composables/         # 组合式函数
│   │   │   ├── useAudioRecorder.ts
│   │   │   └── useWebSocket.ts
│   │   ├── pages/              # 页面组件
│   │   │   ├── MeetingPage.vue      # 主页面（上传/录音）
│   │   │   ├── MeetingConsolePage.vue # 会议控制台
│   │   │   └── GraphRAGPage.vue     # 知识图谱管理
│   │   ├── stores/              # Pinia 状态管理
│   │   └── router/              # Vue Router 配置
│   └── package.json
│
├── docs/                        # 技术文档
│   └── architecture.drawio      # 架构图
└── README.md
```

---

## 快速开始

### 1. 环境要求

- Python 3.11+
- Node.js 18+
- npm 或 yarn

### 2. 安装依赖

```bash
# 前端
cd frontend && npm install

# 后端
cd backend && pip install -r requirements.txt
```

### 3. 配置环境变量

创建 `backend/app/.env`:

```env
# ASR 引擎: mock, dashscope, dashscope_file, dashscope_realtime, funasr
ASR_ENGINE=funasr

# DashScope API
DASHSCOPE_API_KEY=sk-xxxxxxxxxxxx

# FunASR 服务地址
FUNASR_ENDPOINT=http://localhost:8001

# LLM 配置
LLM_PROVIDER=dashscope
LLM_API_KEY=sk-xxxxxxxxxxxx
LLM_MODEL=qwen-plus
```

### 4. 启动服务

```bash
# 终端 1: FunASR 服务 (说话人分离, port 8001)
cd backend
python3 -m uvicorn funasr_service.main:app --host 0.0.0.0 --port 8001

# 终端 2: 主后端 (port 8000)
cd backend
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000

# 终端 3: GraphRAG 服务 (port 8002)
cd backend
python3 -m uvicorn app.graphrag.main:app --host 0.0.0.0 --port 8002

# 终端 4: 前端 (port 5173)
cd frontend && npm run dev
```

### 5. 访问应用

| 服务 | 地址 |
|------|------|
| 前端 | http://localhost:5173 |
| 后端 API | http://localhost:8000 |
| GraphRAG API | http://localhost:8002 |
| FunASR 服务 | http://localhost:8001 |

---

## 使用流程

### 实时录音

1. 打开 http://localhost:5173
2. 点击「开始录音」按钮
3. 发言，系统实时显示转写文本
4. 点击「停止」，获取 AI 生成的会议摘要

### 文件上传

1. 点击「上传文件」或拖拽音频文件到页面
2. 支持格式: mp3, mp4, wav, m4a, ogg, flac, webm (最大 512MB)
3. 等待识别分析完成
4. 进入会议控制台查看详情

### 会议控制台

1. 查看章节列表与摘要
2. 点击章节跳转至对应音频位置
3. 点击说话人色条跳转至该时段
4. 使用时间线拖拽定位

### 知识图谱

1. 进入 GraphRAG 页面
2. 上传文档进行索引
3. 使用自然语言查询知识库
4. 查看实体关系图谱

---

## API 接口

### 主后端 (8000)

| 端点 | 方法 | 描述 |
|------|------|------|
| `/api/v1/ws/voice` | WebSocket | 实时语音识别 |
| `/api/v1/upload` | POST | 文件上传识别 |
| `/api/v1/upload/{session_id}/status` | GET | 上传状态查询 |
| `/api/v1/upload/{session_id}` | GET | 获取完整分析结果 |
| `/api/v1/upload/formats` | GET | 支持的音频格式 |
| `/api/v1/health` | GET | 健康检查 |

### GraphRAG 服务 (8002)

| 端点 | 方法 | 描述 |
|------|------|------|
| `/api/v1/index/` | POST | 文档索引 |
| `/api/v1/query/` | POST | 知识查询 |
| `/api/v1/summarize/` | POST | 全局摘要 |
| `/api/v1/graph/` | GET | 图谱数据 |
| `/api/v1/documents/` | GET | 文档列表 |
| `/api/v1/documents/{id}` | DELETE | 删除文档 |

---

## WebSocket 协议

### 客户端 → 服务端

```json
// 开始录音
{"type": "control", "action": "start"}

// 停止录音
{"type": "control", "action": "stop"}

// 音频数据（二进制 PCM 16kHz 16-bit mono）
<binary audio data>
```

### 服务端 → 客户端

```json
// 欢迎消息
{"type": "welcome", "session_id": "xxx"}

// 实时转写
{"type": "transcript", "data": {"text": "...", "start_time": 0.0, "end_time": 2.5, "speaker": "speaker_0"}}

// 处理状态
{"type": "status", "stage": "transcribing", "progress": 45}

// 分析结果
{"type": "analysis_result", "data": {...}}

// 错误消息
{"type": "error", "code": "ASR_ERROR", "message": "..."}
```

---

## ASR 引擎对比

| 引擎 | 说话人分离 | 文件大小限制 | 延迟 | 部署方式 |
|------|-----------|-------------|------|---------|
| `dashscope_file` | ❌ | 512MB | 取决于文件大小 | 云端 |
| `dashscope_realtime` | ❌ | 无限制 | ~2秒 | 云端 |
| `funasr` | ✅ | 无限制 | CPU 较慢 | 本地 (port 8001) |
| `mock` | ❌ | 无限制 | 即时 | 本地（测试用） |

---

## 配置说明

### ASR 引擎选择

```env
# 无需说话人分离，使用云端高速识别
ASR_ENGINE=dashscope_file

# 需要说话人分离，使用本地 FunASR
ASR_ENGINE=funasr
```

### 音频缓存

```env
AUDIO_CACHE_ENABLED=true
AUDIO_CACHE_DIR=./audio_cache
```

---

## 常见问题

**Q: FunASR 需要 GPU 吗？**
A: 不需要，CPU 推理即可（约 0.5x 实时速度）。

**Q: 支持哪些音频格式？**
A: mp3, mp4, wav, m4a, ogg, flac, webm，最大 512MB。

**Q: 如何区分不同发言人？**
A: 使用 `ASR_ENGINE=funasr`，FunASR 会自动标注发言人。

**Q: GraphRAG 查询返回 502 错误？**
A: 检查 Ollama embedding 服务是否正常运行，macOS 需要禁用系统代理。

---

## License

MIT License - 详见 [LICENSE](LICENSE) 文件

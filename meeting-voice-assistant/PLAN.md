# 会议语音助手 - 语音识别模块实现计划

## Context

用户需要一个会议语音助手的语音识别模块，用于：
1. 实时读取用户语音并转化为文本
2. 识别与会人、会议角色、说话时间戳、会议章节、会议主题
3. 生成本模块的完整技术文档
4. 实现前后端分离的系统，前端Vue+Vite，后端Python FastAPI
5. ASR引擎使用SenseVoice（阿里开源，支持本地部署）
6. 代码设计需考虑DFX标准（接口文档、注释、日志）

**技术选型（已确认）:**
- ASR引擎: SenseVoice
- 前端框架: Vue + Vite
- 后端框架: Python FastAPI

---

## 项目目录结构

```
meeting-voice-assistant/
├── README.md
├── docker-compose.yml
├── Makefile
│
├── frontend/                       # Vue + Vite 前端
│   ├── src/
│   │   ├── api/
│   │   │   ├── websocket.ts       # WebSocket 客户端
│   │   │   └── types.ts           # 类型定义
│   │   ├── components/
│   │   │   ├── AudioRecorder.vue  # 录音组件
│   │   │   ├── TranscriptPanel.vue
│   │   │   ├── MeetingInfo.vue
│   │   │   └── ControlBar.vue
│   │   ├── composables/
│   │   │   ├── useAudioRecorder.ts
│   │   │   └── useWebSocket.ts
│   │   ├── stores/
│   │   │   └── meeting.ts         # Pinia 状态
│   │   ├── App.vue
│   │   └── main.ts
│   ├── index.html
│   ├── vite.config.ts
│   └── package.json
│
├── backend/                       # Python FastAPI 后端
│   ├── app/
│   │   ├── main.py               # FastAPI 入口
│   │   ├── config.py             # 配置管理
│   │   ├── api/
│   │   │   ├── v1/
│   │   │   │   ├── ws.py         # WebSocket 路由
│   │   │   │   └── health.py     # 健康检查
│   │   │   └── router.py
│   │   ├── core/
│   │   │   ├── asr/              # ASR 适配器
│   │   │   │   ├── base.py       # 基类接口
│   │   │   │   ├── sensevoice.py # SenseVoice 实现
│   │   │   │   └── factory.py    # 工厂
│   │   │   ├── processor/
│   │   │   │   └── audio_processor.py
│   │   │   └── parser/           # 语义解析
│   │   │       ├── speaker.py
│   │   │       ├── topic.py
│   │   │       └── meeting_info.py
│   │   ├── models/               # Pydantic 模型
│   │   ├── schemas/              # OpenAPI 扩展
│   │   ├── middleware/
│   │   │   ├── logging.py
│   │   │   └── cors.py
│   │   └── utils/
│   │       └── logger.py
│   ├── tests/
│   ├── requirements.txt
│   └── pyproject.toml
│
├── docs/                          # 技术文档
│   ├── README.md
│   ├── architecture/
│   │   ├── overview.md
│   │   ├── dataflow.md
│   │   └── module-design.md
│   ├── api/
│   │   ├── websocket.md
│   │   └── restful.md
│   └── guides/
│       ├── asr-adapter-guide.md
│       └── frontend-dev-guide.md
│
└── scripts/
    ├── setup.sh
    └── download-sensevoice.sh
```

---

## 核心模块设计

### 1. ASR 适配器接口 (Adapter Pattern)

```
backend/app/core/asr/base.py     # ASRAdapterBase 抽象基类
backend/app/core/asr/sensevoice.py # SenseVoiceAdapter 实现
backend/app/core/asr/factory.py    # ASRFactory 工厂类
```

**设计要点:**
- `ASRAdapterBase` 定义标准接口: `initialize()`, `recognize_stream()`, `close()`
- `ASRResult` 数据类: `text`, `start_time`, `end_time`, `speaker`, `confidence`
- `ASRFactory` 根据配置创建对应适配器，便于后续换源

### 2. WebSocket API

```
端点: ws://host:port/api/v1/ws/voice

消息流程:
1. Client 连接 -> Server 返回 {session_id, config}
2. Client 发送 {type: "control", action: "start"}
3. Client 发送二进制音频帧 (PCM 16kHz mono)
4. Server 返回 {type: "transcript", data: {...}}
5. Client 发送 {type: "control", action: "stop"}
6. Server 返回 {type: "meeting_info", data: {...}}
```

### 3. 语义解析模块

```
backend/app/core/parser/
├── speaker.py      # 说话人识别 ("张三说:" -> speaker: 张三)
├── topic.py        # 主题提取 (从文本推断会议主题)
└── meeting_info.py # 会议信息整合
```

### 4. 前端核心组件

```
frontend/src/
├── api/websocket.ts           # WebSocket 客户端封装
├── composables/useAudioRecorder.ts  # 录音 Hook
├── stores/meeting.ts         # Pinia 状态管理
└── components/
    ├── AudioRecorder.vue      # 录音按钮+音量显示
    ├── TranscriptPanel.vue     # 实时转写展示
    └── MeetingInfo.vue         # 会议信息展示
```

---

## 技术文档大纲 (保存到 docs/)

```markdown
# 会议语音助手 - 技术文档

## 目录
1. 概述
2. 快速开始
3. 架构设计
4. API 参考
5. 数据流
6. 模块详细设计
7. 配置说明
8. 开发指南
9. 部署指南
10. 扩展指南
```

---

## 实现阶段

### 阶段一: 基础框架 (第1-2天)
- [ ] 搭建前端 Vue + Vite 项目
- [ ] 搭建后端 FastAPI 项目
- [ ] 实现基础 WebSocket 连接
- [ ] 配置日志和 OpenAPI 文档

### 阶段二: ASR 适配器 (第3-5天)
- [ ] 实现 ASR 适配器基类接口
- [ ] 实现 SenseVoice 适配器
- [ ] 实现 ASR 工厂
- [ ] 集成测试 ASR 模块

### 阶段三: 前端功能 (第6-8天)
- [ ] 实现音频录制组件
- [ ] 实现 WebSocket 音频传输
- [ ] 实现识别结果展示

### 阶段四: 语义解析 (第9-10天)
- [ ] 实现说话人解析器
- [ ] 实现角色/章节/主题解析
- [ ] 端到端集成测试

### 阶段五: 文档与部署 (第11-12天)
- [ ] 完善技术文档
- [ ] 编写部署脚本

---

## 关键文件清单

| 文件路径 | 说明 |
|---------|------|
| `backend/app/core/asr/base.py` | ASR 适配器基类，核心接口 |
| `backend/app/core/asr/sensevoice.py` | SenseVoice 实现 |
| `backend/app/api/v1/ws.py` | WebSocket 路由 |
| `frontend/src/composables/useAudioRecorder.ts` | 前端录音核心 |
| `backend/app/core/parser/meeting_info.py` | 会议信息解析 |

---

## DFX 设计要点

### 日志规范
- `DEBUG`: 音频帧数量、大小
- `INFO`: 连接建立、识别开始/结束
- `WARNING`: 重连、fallback
- `ERROR`: ASR 失败、数据格式错误

### 接口文档
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

---

## 验证方式

1. **后端启动**: `cd backend && uvicorn app.main:app --reload`
2. **前端启动**: `cd frontend && npm run dev`
3. **浏览器访问**: `http://localhost:5173`
4. **测试录音**: 点击录音按钮，对着麦克风说话，观察实时转写
5. **验证WebSocket**: 检查后端日志中的音频帧接收和识别结果输出

---

## GraphRAG 知识管理模块（已实现）

详见：`backend/app/graphrag/` 和 `docs/superpowers/specs/2026-04-08-graphrag-design.md`

### 核心功能

| 功能 | 端点 | 状态 |
|------|------|------|
| 文档索引 | POST /api/v1/index | ✅ 已实现 |
| 知识查询 | POST /api/v1/query | ✅ 已实现 |
| 动态 top_k | query.top_k 参数 | ✅ 已实现 |
| 全局汇总 | POST /api/v1/summarize | ✅ 已实现 |
| 图谱可视化 | GET /api/v1/graph | ✅ 已实现 |
| 实时上下文注入 | POST /api/v1/realtime/query | ✅ 已实现 |
| 文档管理 | GET/DELETE /api/v1/documents | ✅ 已实现 |

### 启动方式

```bash
cd backend
python3 -m uvicorn app.graphrag.main:app --host 0.0.0.0 --port 8002
```

### 与会议助手集成

在实时转写过程中，可调用 GraphRAG 服务查询领域知识：

```python
# 实时转写时查询知识
response = await query_knowledge_during_transcription(
    query="当前话题相关知识",
    context="会议正在讨论 GraphRAG 索引构建流程"
)
```

### 前端路由

前端采用 vue-router 实现双页面路由：

| 路由 | 页面 | 描述 |
|------|------|------|
| `/` | MeetingPage | 会议助手主页面 |
| `/graphrag` | GraphRAGPage | 知识图谱管理页面 |

### 完整项目结构

```
meeting-voice-assistant/          # 会议语音助手
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   │   ├── MeetingPage.vue     # 会议助手页面
│   │   │   └── GraphRAGPage.vue   # 知识图谱管理页面
│   │   ├── router/
│   │   │   └── index.ts           # vue-router 配置
│   │   ├── components/           # UI 组件
│   │   ├── composables/          # 组合式函数
│   │   ├── stores/               # Pinia 状态
│   │   ├── api/                  # API 客户端
│   │   ├── App.vue               # 根组件
│   │   └── main.ts               # 入口
│   └── package.json
│
├── backend/                      # FastAPI 后端
│   ├── app/
│   │   ├── api/v1/              # 语音识别 API
│   │   ├── core/                 # ASR 适配器、LLM 分析
│   │   ├── graphrag/            # GraphRAG 知识管理模块
│   │   │   ├── api/v1/          # GraphRAG API 端点
│   │   │   ├── core/            # GraphRAG Core 抽象 + Microsoft 实现
│   │   │   └── storage/         # SQLite 存储层
│   │   └── config.py             # 配置管理
│   ├── rag_workspace/           # GraphRAG 工作目录
│   └── requirements.txt
│
└── docs/                         # 技术文档
```

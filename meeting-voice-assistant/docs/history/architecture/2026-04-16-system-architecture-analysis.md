# 会议语音助手 - 系统架构分析报告

**日期**: 2026-04-16
**分析人**: Software Architect Agent
**版本**: v1.0

---

## 一、整体架构概览

### 1.1 系统架构图

```
┌─────────────────────────────────────────────────────────────────┐
│                     前端 (http://localhost:5173)                 │
│                   Vue 3 + TypeScript + Pinia                     │
└─────────────────────────┬───────────────────────────────────────┘
                          │ WebSocket (ws://localhost:8000/api/v1/ws/voice)
                          │ HTTP (POST /api/v1/upload)
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                主后端 (localhost:8000)                            │
│                FastAPI + WebSocket + SQLAlchemy                 │
├─────────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │ VoiceSession │  │FileUpload    │  │ LLMAnalyzer          │  │
│  │ (ws.py)      │  │Session       │  │ (会议分析)            │  │
│  │              │  │(upload.py)   │  │                      │  │
│  └──────┬───────┘  └──────┬───────┘  └──────────┬───────────┘  │
│         │                  │                      │              │
│         └──────────────────┼──────────────────────┘              │
│                            │                                      │
│  ┌─────────────────────────▼─────────────────────────────────┐  │
│  │              ASRFactory (ASR 适配器工厂)                    │  │
│  │  ┌─────────────┐ ┌──────────────┐ ┌────────────────────┐  │  │
│  │  │DashScope    │ │FunASRAdapter │ │RealtimeTranscriber │  │  │
│  │  │ASRAdapter   │ │(说话人分离)   │ │(qwen3-asr-flash)   │  │  │
│  │  └─────────────┘ └──────────────┘ └────────────────────┘  │  │
│  └───────────────────────────────────────────────────────────┘  │
├─────────────────────────────────────────────────────────────────┤
│                           │                                      │
│         ┌─────────────────┼─────────────────┐                   │
│         ▼                 ▼                 ▼                   │
│  ┌─────────────┐   ┌─────────────┐   ┌─────────────┐            │
│  │ FunASR      │   │ GraphRAG    │   │ DashScope   │            │
│  │ Service     │   │ Service     │   │ API         │            │
│  │ (:8001)     │   │ (:8002)     │   │ (External)   │            │
│  │ 说话人分离   │   │ 知识图谱     │   │ LLM/ASR     │            │
│  └─────────────┘   └─────────────┘   └─────────────┘            │
└─────────────────────────────────────────────────────────────────┘
```

### 1.2 核心数据流

```
[前端录音] → MediaRecorder API → WebSocket二进制帧 → [后端处理]
                                                          │
                                                          ▼
                                               ┌─────────────────────┐
                                               │ VoiceSession        │
                                               │ 1. process_audio()  │
                                               │ 2. asr_adapter      │
                                               │     .append_audio() │
                                               │ 3. commit() + VAD   │
                                               └─────────────────────┘
                                                          │
                                                          ▼
                                               ┌─────────────────────┐
                                               │ 实时转写结果         │
                                               │ (transcript)        │
                                               └─────────────────────┘
                                                          │
                                                          ▼
                                               ┌─────────────────────┐
                                               │ stop 控制消息       │
                                               │ → _process_after_   │
                                               │   stop()            │
                                               ├─────────────────────┤
                                               │ 1. 保存音频缓存      │
                                               │ 2. _finish_recog()  │
                                               │ 3. LLMAnalyzer       │
                                               │    .analyze_meeting │
                                               │ 4. 返回分析结果      │
                                               └─────────────────────┘
```

---

## 二、前后端通信架构分析

### 2.1 WebSocket 通信协议

**端点**: `ws://localhost:8000/api/v1/ws/voice`

#### 消息类型 (双向)

| 方向 | 消息类型 | 说明 |
|------|---------|------|
| 服务端 → 客户端 | `welcome` | 连接建立后发送，包含 session_id 和音频配置 |
| 客户端 → 服务端 | `control` | 控制消息 (start/stop/pause/resume) |
| 客户端 → 服务端 | 二进制音频 | 16kHz, 16-bit mono PCM，每约100ms发送一次 |
| 服务端 → 客户端 | `transcript` | 实时转写结果 |
| 服务端 → 客户端 | `status` | 处理状态 (processing/transcribing/analyzing/completed) |
| 服务端 → 客户端 | `analysis_result` | LLM 分析结果 |
| 服务端 → 客户端 | `ack` | 控制命令确认 |
| 服务端 → 客户端 | `error` | 错误消息 |

#### 核心问题分析

**问题1: 混合消息协议**

当前设计混合了二进制音频流和 JSON 文本消息，这导致：
- WebSocket 帧类型需要通过 `data.keys()` 判断 ("bytes" vs "text")
- 前端需要同时处理 `ArrayBuffer` 和字符串消息
- 协议边界不够清晰

**建议**: 考虑统一为一种消息类型，例如将音频 base64 编码后通过 JSON 传输，或使用单独的音频 WebSocket 通道。

**问题2: 重连机制**

当前前端实现了简单的指数退避重连 (`handleReconnect`)，但：
- 最大重试次数硬编码为 5
- 没有心跳保活机制
- 重连时 session 状态完全丢失

**建议**: 增加心跳 ping/pong，session 状态持久化到 localStorage。

### 2.2 HTTP API

| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/v1/upload` | POST | 文件上传识别 |
| `/api/v1/health` | GET | 健康检查 |
| `/api/v1/test-write` | GET | 调试用 |

### 2.3 CORS 配置

当前配置允许所有来源 (`allow_origins=["*"]`)，这对开发环境可接受，但生产环境应限制具体域名。

---

## 三、ASR 引擎选择策略

### 3.1 支持的 ASR 引擎

| 引擎 | 配置值 | 说话人分离 | 文件大小限制 | 实时性 | 延迟 |
|------|--------|-----------|-------------|--------|------|
| Mock | `mock` | ❌ | 无 | - | 模拟 0.8s |
| DashScope 实时 | `dashscope_realtime` | ❌ | 无限制 | ✅ | ~2s |
| DashScope 文件 | `dashscope_file` | ❌ | 512MB | ❌ | 取决于文件 |
| FunASR | `funasr` | ✅ | 无限制 | ❌ | 较慢 |
| FunASR 实时 | `funasr_realtime` | ✅ | 无限制 | ✅ | 中等 |

### 3.2 引擎选择矩阵

```
                    说话人分离需求
                    ┌──────────┬──────────┐
                    │    无     │    有     │
         ┌──────────┼──────────┼──────────┤
    小   │ DashScope│DashScope │  FunASR  │
   文件  │   文件    │  实时     │          │
         ├──────────┼──────────┼──────────┤
   大   │ DashScope │DashScope │  FunASR  │
   文件  │   文件    │  实时     │          │
         └──────────┴──────────┴──────────┘
```

### 3.3 架构问题

**问题1: 适配器接口不一致**

通过阅读 `factory.py` 发现存在两套接口：
1. `ASRAdapterBase` (旧) - 使用 `append_audio()`, `commit()`, `get_result()`
2. `BaseTranscriber` (新) - 使用 `RealtimeTranscriber`, `FileTranscriber`

两套接口并存导致维护成本增加，且 `VoiceSession` 仍使用旧接口。

**问题2: FunASR 服务耦合**

FunASR 作为独立微服务 (port 8001)，但当前实现中 `FunASRAdapter` 直接调用其 HTTP API：
```python
# backend/app/core/asr/funasr_adapter.py
endpoint=os.getenv("FUNASR_ENDPOINT", "http://localhost:8001")
```

这导致：
- FunASR 服务不可用时整个 ASR 功能受影响
- 部署复杂，需要同时启动 3 个服务

**建议**:
- FunASR 作为可选依赖，配置禁用时回退到 DashScope
- 考虑 Docker Compose 编排

---

## 四、GraphRAG 集成方案

### 4.1 架构分层

```
┌─────────────────────────────────────────┐
│  GraphRAG API (:8002)                    │
│  ├── /api/v1/index     文档索引          │
│  ├── /api/v1/query     知识查询          │
│  ├── /api/v1/graph     图谱数据          │
│  ├── /api/v1/community 社区检测          │
│  └── /api/v1/realtime  实时索引入度      │
└──────────────────┬──────────────────────┘
                   │
┌──────────────────▼──────────────────────┐
│  GraphRAG Core                           │
│  ├── Microsoft GraphRAG (主框架)          │
│  ├── Storage/Database (SQLite)           │
│  └── LLM Adapter (DashScope/MiniMax)     │
└──────────────────┬──────────────────────┘
                   │
┌──────────────────▼──────────────────────┐
│  RAG Workspace                           │
│  └── ./rag_workspace/                    │
│      ├── input/     原始文档              │
│      └── output/    索引数据              │
└─────────────────────────────────────────┘
```

### 4.2 与主应用的集成方式

**当前方式**: 通过 HTTP API 调用独立服务
```python
# 主后端 → GraphRAG 服务
POST http://localhost:8002/api/v1/index/
POST http://localhost:8002/api/v1/query/
```

**优点**:
- 服务解耦，独立部署
- 可以单独扩展 GraphRAG 服务

**缺点**:
- 跨服务调用增加延迟
- 需要管理两个独立的服务进程
- 数据一致性挑战 (音频/转写 vs 图谱索引)

### 4.3 问题分析

**问题1: 索引触发时机模糊**

当前 `VoiceSession._process_after_stop()` 调用 `LLMAnalyzer.analyze_meeting()`，但没有看到自动触发 GraphRAG 索引的逻辑。GraphRAG 索引需要手动调用 `/api/v1/index/` 端点。

**问题2: context_injector 的作用**

`backend/app/graphrag/service/context_injector.py` 存在但内容未知，可能是用于向 LLM 注入上下文，但与主后端的集成链路不清晰。

**问题3: macOS 代理问题**

已知问题: macOS 系统代理导致 Ollama embeddings 502 错误。当前 patch 在 `adapter.py` 中禁用 `trust_env`，但如果使用其他 LLM provider 可能仍有此问题。

---

## 五、架构优化建议

### 5.1 高优先级优化

#### 建议1: 统一 ASR 适配器接口

**问题**: 两套 ASR 接口并存，增加维护成本

**方案**: 保留 `BaseTranscriber` (新架构)，将所有现有适配器迁移到新接口

```python
# 目标接口
class BaseTranscriber(ABC):
    @abstractmethod
    async def start(self) -> None: ...

    @abstractmethod
    async def append_audio(self, audio: bytes) -> None: ...

    @abstractmethod
    async def commit(self) -> TranscriptionResult: ...

    @abstractmethod
    async def finish(self) -> None: ...
```

#### 建议2: 引入消息队列解耦

**问题**: 当前 ASR 处理是同步的，请求-响应模式

**方案**: 引入 Redis/RabbitMQ 作为消息队列
- 音频帧 → 队列 → ASR Worker → 结果队列 → WebSocket 推送
- 支持水平扩展 ASR 处理能力

#### 建议3: GraphRAG 与主应用整合

**问题**: GraphRAG 索引未自动化

**方案**: 在 `_process_after_stop()` 末尾自动触发索引
```python
async def _process_after_stop(self) -> None:
    # ... 现有逻辑 ...
    # 新增: 触发 GraphRAG 索引
    if config.GRAPHRAG_AUTO_INDEX:
        await self._trigger_graphrag_index(audio_path, transcript_text)
```

### 5.2 中优先级优化

#### 建议4: 会话状态持久化

**问题**: 重连后 session 丢失

**方案**: 将 session 状态 (transcripts, audio_chunks) 存储到 Redis
```python
class VoiceSession:
    session_id: str  # 可用于 Redis key
    _state: dict  # {transcripts: [], audio_chunks: [], status: str}
```

#### 建议5: 添加指标采集

**当前**: 无可观测性

**方案**: 集成 Prometheus metrics
- `asr_request_duration_seconds`
- `ws_connections_active`
- `audio_chunks_processed_total`

#### 建议6: 配置外部化

**问题**: 配置分散在多个 `.env` 文件

**方案**: 统一配置管理
- 主后端: `backend/app/.env`
- GraphRAG: `backend/app/graphrag/.env` (已有)
- FunASR: `backend/funasr_service/.env`

建议合并为项目根目录 `.env`，按服务分组

### 5.3 低优先级优化 (长期)

| 建议 | 描述 | 复杂度 |
|------|------|--------|
| 服务网格 | 引入 Istio 管理服务间通信 | 高 |
| 事件溯源 | 使用 Event Sourcing 记录所有状态变更 | 高 |
| CQRS | 分离读、写模型，优化查询性能 | 中 |

---

## 六、部署架构建议

### 当前 (开发模式)

```
localhost:5173  (前端)
localhost:8000  (主后端)
localhost:8001  (FunASR)
localhost:8002  (GraphRAG)
```

### 建议 (生产模式)

```yaml
# docker-compose.yml
services:
  frontend:
    build: ./frontend
    ports:
      - "80:80"

  backend:
    build: ./backend
    ports:
      - "8000:8000"
    depends_on:
      - redis
      - funasr

  funasr:
    build: ./backend/funasr_service
    ports:
      - "8001:8001"

  graphrag:
    build: ./backend
    command: python -m app.graphrag.main
    ports:
      - "8002:8002"

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
```

---

## 七、安全考量

### 7.1 当前问题

1. **CORS**: `allow_origins=["*"]` - 生产环境应限制
2. **无认证**: 所有 API 无认证机制
3. **文件上传**: 无大小限制校验 (虽然代码有 512MB 限制，但未在代码中显式校验)

### 7.2 建议

1. 添加 JWT/API Key 认证
2. 文件上传增加大小校验和类型检测
3. 敏感配置 (API keys) 使用 Kubernetes Secret 或 Vault

---

## 八、总结

### 架构评分

| 维度 | 评分 (1-5) | 说明 |
|------|-----------|------|
| 模块化 | 4 | 清晰的模块划分，ASR 适配器工厂模式良好 |
| 可扩展性 | 3 | 添加新 ASR 引擎方便，但 GraphRAG 集成欠佳 |
| 性能 | 3 | 实时性依赖 ASR 服务，无缓存/队列优化 |
| 可维护性 | 3 | 两套 ASR 接口需统一，日志分散 |
| 可部署性 | 2 | 多服务手动启动，缺少容器化编排 |

### 核心改进方向

1. **统一 ASR 接口** - 消除技术债务
2. **引入消息队列** - 解耦和水平扩展
3. **自动化 GraphRAG 索引** - 完善知识管理流程
4. **容器化部署** - Docker Compose 一键启动
5. **添加监控指标** - 可观测性建设

---

*本报告基于代码审查生成，具体实现细节请参考对应源文件。*

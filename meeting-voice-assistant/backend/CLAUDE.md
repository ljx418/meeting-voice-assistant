# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

这是一个基于 Web 的实时语音识别会议助手，采用前后端分离架构。

- **前端**: Vue 3 + TypeScript + Vite
- **后端**: Python FastAPI + WebSocket
- **ASR 引擎**: 阿里云 DashScope / FunASR (本地说话人分离)
- **LLM**: 阿里云 DashScope (qwen-plus)
- **知识管理**: GraphRAG 模块 (内置于后端, port 8002)

## 技术路线

### ASR 引擎

| 引擎 | 模型 | 接口 | 文件大小限制 | 说话人分离 | 延迟 |
|------|------|------|-------------|-----------|------|
| `dashscope_file` | qwen3-asr-flash | HTTP | 512MB | ❌ | 取决于文件大小 |
| `dashscope_realtime` | qwen3-asr-flash-realtime | WebSocket | 无限制 | ❌ | ~2秒 |
| `funasr` | Paraformer + CAM++ | HTTP | 无限制 | ✅ | CPU 较慢 |

**推荐**: 需要说话人分离时使用 `funasr`，否则使用 `dashscope_file`。

### LLM 分析

- 模型: `qwen-plus` (DashScope)
- 用途: 会议摘要、关键点提取、行动项识别、主题分类

## 运行命令

```bash
# 后端 (主服务 - 语音识别 API)
cd backend
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000

# GraphRAG 服务 (知识图谱管理 API)
cd backend
python3 -m uvicorn app.graphrag.main:app --host 0.0.0.0 --port 8002

# FunASR 服务 (说话人分离，需要单独启动)
cd backend
python3 -m uvicorn funasr_service.main:app --host 0.0.0.0 --port 8001

# 前端
cd frontend
npm run dev
```

## 目录结构

```
backend/
├── app/
│   ├── api/v1/
│   │   ├── ws.py              # WebSocket 语音识别
│   │   ├── upload.py          # 文件上传
│   │   └── health.py          # 健康检查
│   ├── core/
│   │   ├── asr/               # ASR 适配器
│   │   │   ├── base.py        # 基类定义 (ASRAdapterBase, ASRResult)
│   │   │   ├── factory.py     # 工厂类 (ASRFactory)
│   │   │   ├── dashscope.py   # DashScope 文件识别 (6MB)
│   │   │   ├── dashscope_file.py  # DashScope 大文件识别 (512MB)
│   │   │   ├── realtime.py    # DashScope 实时识别
│   │   │   ├── funasr_adapter.py  # FunASR 本地说话人分离
│   │   │   └── mock.py        # Mock 测试
│   │   ├── audio_cache.py     # 音频缓存
│   │   ├── llm_analyzer.py    # LLM 分析
│   │   └── parser/             # 会议信息解析
│   ├── graphrag/              # GraphRAG 知识管理模块
│   │   ├── api/v1/            # API 端点 (index, query, summarize, graph, document, realtime)
│   │   ├── core/              # GraphRAG Core 抽象 + Microsoft 实现
│   │   │   ├── base.py        # GraphRAGCore 抽象基类
│   │   │   ├── registry.py    # 实现注册表
│   │   │   └── microsoft/    # Microsoft GraphRAG 适配器
│   │   ├── storage/           # SQLite 存储层
│   │   │   ├── database.py    # 异步数据库操作
│   │   │   └── models.py      # SQLAlchemy 模型
│   │   ├── service/           # 业务服务
│   │   │   └── context_injector.py  # 实时上下文注入
│   │   ├── config.py          # GraphRAG 配置
│   │   └── main.py           # GraphRAG 服务入口
│   ├── config.py              # 配置管理
│   └── main.py                # FastAPI 入口
├── funasr_service/            # FunASR 说话人分离微服务
│   ├── main.py                # FastAPI 入口
│   ├── api.py                 # API 路由
│   ├── model_loader.py         # 模型加载
│   └── config.py              # 服务配置
├── rag_workspace/             # GraphRAG 工作目录
├── audio_cache/               # 音频缓存目录
├── transcripts/               # 转写文本保存目录
└── requirements.txt
```

## 配置说明

### 环境变量 (.env) - `backend/app/.env`

```env
# ASR 引擎: mock, dashscope, dashscope_file, dashscope_realtime, funasr
ASR_ENGINE=funasr

# FunASR 配置 (当 ASR_ENGINE=funasr 时使用)
FUNASR_ENDPOINT=http://localhost:8001

# DashScope 配置 (当使用 DashScope 引擎时使用)
DASHSCOPE_API_KEY=sk-xxx

# LLM 配置
LLM_PROVIDER=dashscope
LLM_API_KEY=sk-xxx
LLM_MODEL=qwen-plus

# 音频配置
AUDIO_CACHE_ENABLED=true
AUDIO_CACHE_DIR=./audio_cache
```

## 核心架构

### ASR 适配器模式

所有 ASR 引擎实现统一的 `ASRAdapterBase` 接口：

```python
class ASRAdapterBase:
    async def initialize() -> None
    async def close() -> None
    async def recognize_stream(...) -> AsyncGenerator[ASRResult, None]
    async def recognize_file(file_path: Path) -> AsyncGenerator[ASRResult, None]
```

使用 `ASRFactory.create("engine_name")` 创建适配器实例。

### ASRResult 数据结构

```python
@dataclass
class ASRResult:
    text: str           # 识别文本
    start_time: float   # 开始时间 (秒)
    end_time: float     # 结束时间 (秒)
    speaker: str         # 说话人 ID ("speaker_0", "speaker_1")
    confidence: float   # 置信度
    is_final: bool      # 是否最终结果
```

## API 端点

| 端点 | 方法 | 描述 |
|------|------|------|
| `/api/v1/ws/voice` | WebSocket | 实时语音识别 |
| `/api/v1/upload` | POST | 文件上传 (最大512MB) |
| `/api/v1/health` | GET | 健康检查 |

## FunASR 服务

FunASR 提供本地说话人分离功能，需要独立部署：

```bash
# 启动 FunASR 服务
cd backend
python3 -m uvicorn funasr_service.main:app --host 0.0.0.0 --port 8001

# 测试
curl http://localhost:8001/health
```

**注意**: 首次运行会自动下载模型（约 1GB），需要网络连接。

## WebSocket 消息格式

### 客户端 → 服务端

```json
{"type": "control", "action": "start"}
{"type": "control", "action": "stop"}
```

音频数据: 二进制 (PCM 16kHz 16-bit mono)

### 服务端 → 客户端

```json
{
  "type": "transcript",
  "data": {
    "text": "识别文本",
    "start_time": 0.0,
    "end_time": 2.5,
    "speaker": "speaker_1",
    "confidence": 0.95
  }
}
```

## GraphRAG 知识服务

GraphRAG 模块已集成到 `backend/app/graphrag/` 目录，作为独立服务运行在 port 8002。

### 架构概览

```
┌─────────────────────────────────────────────────────────────┐
│                    GraphRAG 服务 (port 8002)                 │
├─────────────────────────────────────────────────────────────┤
│  API Layer (FastAPI)                                         │
│  └── /api/v1/                                               │
│      ├── index/        # 文档索引                            │
│      ├── query/        # 知识查询                            │
│      ├── summarize/    # 全局汇总                            │
│      ├── graph/        # 图谱可视化数据                       │
│      ├── community/   # 社区信息                            │
│      ├── documents/    # 文档管理                            │
│      └── realtime/     # 实时上下文注入查询                   │
├─────────────────────────────────────────────────────────────┤
│  Core Layer                                                  │
│  └── MicrosoftGraphRAGAdapter                               │
│      ├── index_document()      # 文档索引                    │
│      ├── query()                # 知识查询                    │
│      ├── summarize()            # 全局摘要                    │
│      └── get_graph_data()       # 图谱数据                    │
├─────────────────────────────────────────────────────────────┤
│  Storage Layer (SQLite)                                      │
│  └── database.py (异步 SQLAlchemy)                          │
│      ├── entities, relationships, communities 表            │
│      └── documents 表                                       │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│            Microsoft GraphRAG CLI (子进程)                   │
├─────────────────────────────────────────────────────────────┤
│  graphrag index --root ./rag_workspace --skip-validation     │
│  graphrag query --root ./rag_workspace --method local/global │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    LLM Provider (LiteLLM)                    │
├─────────────────────────────────────────────────────────────┤
│  LLM: MiniMax M2.1 (api.minimax.chat) - 实体/关系提取        │
│  Embedding: Ollama nomic-embed-text (localhost:11434)       │
│              ⚠️ LiteLLM 调用 Ollama 有 502 兼容性 bug        │
└─────────────────────────────────────────────────────────────┘
```

### 目录结构

```
app/graphrag/
├── main.py                 # FastAPI 入口
├── config.py               # 配置管理
├── api/v1/
│   ├── __init__.py
│   ├── router.py           # API 路由聚合
│   ├── index.py            # 文档索引端点
│   ├── query.py            # 查询端点
│   ├── summarize.py        # 汇总端点
│   ├── graph.py            # 图谱数据端点
│   ├── community.py        # 社区信息端点
│   └── document.py         # 文档管理端点
├── core/
│   ├── __init__.py
│   ├── base.py             # GraphRAGCore 抽象基类
│   ├── registry.py         # 实现注册表
│   ├── language_detector.py # 语言检测
│   └── microsoft/
│       ├── __init__.py
│       └── adapter.py      # Microsoft GraphRAG 适配器
├── storage/
│   ├── __init__.py
│   ├── models.py           # SQLAlchemy 模型
│   └── database.py         # 异步数据库操作
└── service/
    └── context_injector.py  # 实时上下文注入
```

### GraphRAG API 端点

| 端点 | 方法 | 描述 |
|------|------|------|
| `/api/v1/index/` | POST | 文档索引 (multipart/form-data) |
| `/api/v1/index/batch` | POST | 批量索引 |
| `/api/v1/query/` | POST | 知识查询 (local/global) |
| `/api/v1/summarize/` | POST | 全局汇总 |
| `/api/v1/graph/` | GET | 图谱可视化数据 |
| `/api/v1/community/{id}/summary` | GET | 社区摘要 |
| `/api/v1/documents/` | GET | 文档列表 |
| `/api/v1/documents/{id}` | DELETE | 删除文档 |
| `/api/v1/realtime/query/` | POST | 实时上下文注入 |

### 数据流

#### 文档索引流程

```
1. POST /api/v1/index/ (上传文件)
       │
       ▼
2. MicrosoftGraphRAGAdapter.index_document()
       │  保存文件到 rag_workspace/input/
       │  执行 graphrag index --root . (通过 wrapper 自动禁用系统代理)
       ▼
3. 解析 output/ 目录下的 parquet 文件
       │  entities.parquet, relationships.parquet
       │  communities.parquet
       ▼
4. 保存到 SQLite 数据库
       │  entities, relationships, communities 表
       ▼
5. 返回索引结果 (实体数/关系数/社区数)
```

#### 查询流程

```
1. POST /api/v1/query/ (查询文本)
       │
       ▼
2. MicrosoftGraphRAGAdapter.query()
       │  执行 graphrag query --method local
       ▼
3. 解析 JSON 结果返回
```

### GraphRAG 配置

#### 环境变量 (backend/app/graphrag/config.py)

```env
GRAPHRAG_SERVICE_PORT=8002
LLM_PROVIDER=minimax          # LLM 提供商
LLM_API_KEY=sk-xxx            # API Key
LLM_MODEL=MiniMax-M2.1       # 模型名称
LLM_BASE_URL=https://api.minimax.chat/v1  # API 端点
GRAPHRAG_WORKSPACE=./rag_workspace
```

#### settings.yaml (rag_workspace/settings.yaml)

```yaml
# LLM 配置 (completion)
completion_models:
  default_completion_model:
    type: litellm
    model_provider: minimax
    model: MiniMax-M2.1
    api_key: sk-xxx
    api_base: https://api.minimax.chat/v1

# Embedding 配置
embedding_models:
  default_embedding_model:
    type: litellm
    model_provider: ollama
    model: nomic-embed-text
    api_base: http://localhost:11434
    api_key: ollama

# 搜索配置
search:
  type: local
  local:
    mode: local
    vectorizer: embed
    max_tokens: 7500
    temperature: 0.0
```

### 已知问题与解决方案

#### 1. macOS 系统代理导致 Ollama embeddings 502 错误 (已解决)

**问题描述**:
- macOS 的 `networkserviceproxy` (NSS) 在系统级别拦截 HTTP 请求
- httpx 默认使用 `trust_env=True`，读取系统代理设置
- Ollama 不支持代理协议，导致 502 Bad Gateway

**解决方案**:
创建 `/tmp/graphrag_patched.py` 包装脚本，在导入 litellm 之前 patch httpx：

```python
import httpx

_OriginalClient = httpx.Client
_OriginalAsyncClient = httpx.AsyncClient

class FixedClient(_OriginalClient):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('trust_env', False)  # 禁用系统代理
        super().__init__(*args, **kwargs)

httpx.Client = FixedClient
httpx.AsyncClient = FixedAsyncClient
```

将 `/usr/local/bin/graphrag` 替换为调用此脚本的 wrapper。

**状态**: ✅ 已解决 - 完全支持 Ollama embeddings

#### 2. 环境隔离（替代 Namespace 方案）

**方案**: 通过不同的 `GRAPHRAG_WORKSPACE` 目录实现环境隔离

| 环境 | GRAPHRAG_WORKSPACE |
|------|-------------------|
| 开发环境 | `./rag_workspace_dev` |
| 生产环境 | `./rag_workspace_prod` |

每个环境有独立的：
- `input/` 目录 — 存放待索引文档（直接存放，不分子目录）
- `output/` 目录 — GraphRAG 索引输出
- `graphrag.db` — SQLite 数据库

**优点**:
- 简化 API（无需 namespace 参数）
- 目录结构扁平清晰
- 环境隔离完全由文件系统保证

#### 3. 文档删除限制

**问题描述**:
- 删除源文件后，GraphRAG 索引数据仍保留在 output 目录
- 无法单独删除某个文档的索引

**解决方案**:
- 删除整个 output 目录后重新索引
- 或为每个环境使用独立的 workspace

### 启动和测试

```bash
# 启动 GraphRAG 服务
cd backend
source venv312/bin/activate
python3 -m uvicorn app.graphrag.main:app --host 0.0.0.0 --port 8002

# 测试索引（无需 namespace 参数）
echo "test content" > /tmp/test.txt
curl -s -L -X POST "http://localhost:8002/api/v1/index/" -F "doc=@/tmp/test.txt"

# 测试图谱查询
curl -s "http://localhost:8002/api/v1/graph/?max_nodes=50"
```

## 前端路由

前端采用 vue-router 实现双页面路由：

| 路由 | 页面 | 描述 |
|------|------|------|
| `/` | MeetingPage | 会议助手主页面 |
| `/graphrag` | GraphRAGPage | 知识图谱管理页面 |

页面间可通过头部导航按钮切换。

# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

GraphRAG 知识管理服务，提供文档索引、知识查询、图谱可视化和实时上下文注入能力。

- **技术栈**: Python 3.9+, FastAPI, 微软 GraphRAG, SQLite, Pydantic
- **LLM**: 阿里云 DashScope (qwen-plus)
- **端口**: 8002

## 运行命令

```bash
cd graphrag-service
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8002

# 访问文档
open http://localhost:8002/docs
```

## 目录结构

```
graphrag-service/
├── app/
│   ├── main.py              # FastAPI 入口
│   ├── config.py           # pydantic-settings 配置
│   ├── api/v1/
│   │   ├── index.py       # POST /api/v1/index - 文档索引
│   │   ├── query.py       # POST /api/v1/query - 知识查询
│   │   ├── summarize.py    # POST /api/v1/summarize - 全局汇总
│   │   ├── graph.py       # GET /api/v1/graph - 图谱可视化
│   │   ├── document.py    # GET/DELETE /api/v1/documents - 文档管理
│   │   └── realtime.py    # POST /api/v1/realtime/query - 实时上下文注入
│   ├── core/
│   │   ├── base.py        # GraphRAGCore 抽象基类 + dataclasses
│   │   ├── registry.py    # Core 实例注册表
│   │   └── microsoft/
│   │       └── adapter.py  # MicrosoftGraphRAGAdapter 实现
│   ├── storage/
│   │   ├── database.py     # SQLite CRUD 操作
│   │   └── models.py      # SQLAlchemy ORM 模型
│   └── service/
│       └── context_injector.py  # 实时上下文注入器
├── rag_workspace/          # GraphRAG 工作目录
│   ├── input/              # 原始文档
│   └── output/             # 索引输出
└── requirements.txt
```

## 配置说明

### 环境变量 (.env)

```env
GRAPHRAG_SERVICE_PORT=8002
LLM_PROVIDER=dashscope
LLM_API_KEY=sk-xxx
LLM_BASE_URL=https://dashscope.aliyuncs.com
LLM_MODEL=qwen-plus
GRAPHRAG_WORKSPACE=./rag_workspace
DEFAULT_TOP_K=10
```

## 核心架构

### GraphRAGCore 抽象接口

所有实现必须实现 `GraphRAGCore` 抽象基类：

```python
class GraphRAGCore(ABC):
    async def index_document(self, doc_path: Path, namespace: str) -> IndexResult
    async def index_documents_batch(self, doc_paths: list[Path], namespace: str) -> BatchIndexResult
    async def query(self, query_text: str, namespace: str, top_k: int = 10, context: str | None = None) -> QueryResult
    async def summarize(self, namespace: str, query: str | None = None) -> SummaryResult
    async def get_graph_data(self, namespace: str, max_nodes: int = 100) -> GraphData
    async def delete_document(self, doc_id: str, namespace: str) -> None
```

使用 `GraphRAGRegistry.get_instance()` 获取当前实现。

## API 端点

| 端点 | 方法 | 描述 |
|------|------|------|
| `/api/v1/index` | POST | 索引文档 (multipart/form-data) |
| `/api/v1/query` | POST | 知识查询 (含动态 top_k, context) |
| `/api/v1/summarize` | POST | 全局汇总 |
| `/api/v1/graph` | GET | 图谱可视化 (节点+边) |
| `/api/v1/documents` | GET | 文档列表 |
| `/api/v1/documents/{id}` | DELETE | 删除文档 |
| `/api/v1/realtime/query` | POST | 实时上下文注入查询 |

## API 使用示例

### 索引文档

```bash
curl -X POST http://localhost:8002/api/v1/index \
  -F "doc=@./document.pdf" \
  -F "namespace=default"
```

### 查询知识

```bash
curl -X POST http://localhost:8002/api/v1/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "项目用了哪些技术？",
    "namespace": "default",
    "top_k": 10
  }'
```

### 实时上下文注入查询

```bash
curl -X POST http://localhost:8002/api/v1/realtime/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "这个概念是什么？",
    "context": "会议正在讨论 GraphRAG 的索引构建",
    "namespace": "default",
    "top_k": 5
  }'
```

### 获取图谱数据

```bash
curl "http://localhost:8002/api/v1/graph?namespace=default&max_nodes=100"
```

## 与 meeting-voice-assistant 集成

GraphRAG 服务与会议语音助手通过 HTTP 通信：

```python
import httpx

async def query_knowledge_during_transcription(query: str, context: str):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8002/api/v1/realtime/query",
            json={
                "query": query,
                "context": context,
                "top_k": 5
            }
        )
        return response.json()
```

## 已知限制

### Namespace 隔离

当前 `graphrag index` CLI 处理整个 workspace/input 目录，非特定 namespace 子目录。生产部署建议使用：
- 按 namespace 分开部署
- 或在索引前清空 workspace

### GraphRAG 依赖

需要预先安装 graphrag CLI：
```bash
pip install graphrag>=0.3.0
```

# GraphRAG 知识管理模块设计

## 1. 背景与目标

### 1.1 问题陈述

现有 `meeting-voice-assistant` 系统仅依赖 LLM（qwen-plus）的内部知识进行生成，在处理垂直领域专业知识时准确性不足。需要引入 GraphRAG 能力，对存量多模知识（文档、录音转写稿等）进行结构化索引和知识图谱构建，增强生成内容的准确性。

### 1.2 核心需求

| 需求 | 描述 |
|------|------|
| 知识查询 | 对已索引文档进行语义检索，返回知识片段 |
| 知识汇总 | 对文档集合进行全局归纳总结 |
| 知识图谱绘制 | 可视化实体-关系网络 |
| API 对外服务 | 通过 REST API 暴露所有能力 |
| 实时转写查询 | 转写过程中可动态注入 context 并查询领域知识 |
| 动态 top-k | 召回时参数可动态调整 |

### 1.3 设计约束

| 约束 | 说明 |
|------|------|
| 文档规模 | 初期 100 份，短期扩至 1000 份 |
| 部署方式 | 优先独立部署服务，本地优先使用 API 实现 |
| 多租户 | 暂不实现，未来通过 namespace 扩展 |
| 技术选型 | 基于微软 GraphRAG，预留自研迁移空间 |

---

## 2. 技术选型

### 2.1 GraphRAG 框架

**选型：微软 GraphRAG（选项 A）**

原因：
- 成熟的索引 + 查询Pipeline，开箱即用
- 社区检测（Leiden）、社区摘要内置
- 插件式 LLM 配置，可对接 DashScope qwen-plus
- 本地部署可行，不依赖云服务

**预留迁移到选项 C 的扩展性：**
- Core 层通过 `GraphRAGCore` 抽象接口
- 索引链路各阶段（切分、实体提取、图构建、摘要）均有独立抽象
- 迁移时只需替换 Core 实现，Service 层接口不变

### 2.2 部署架构

**独立服务部署**，服务名：`graphrag-service`

```
┌─────────────────────────────────────────────────────┐
│                  graphrag-service                    │
│                   (localhost:8002)                   │
│                                                      │
│  ┌────────────────────────────────────────────────┐ │
│  │            Service Layer（适配层）               │ │
│  │  - API 参数 → Core 参数 桥接                      │ │
│  │  - 多租户 namespace 扩展点                       │ │
│  │  - 流式响应封装                                  │ │
│  └─────────────────────┬──────────────────────────┘ │
│                        │                             │
│  ┌─────────────────────▼──────────────────────────┐│
│  │              GraphRAG Core（核心）               ││
│  │  - Indexer（索引构建）                           ││
│  │  - Query Engine（查询引擎）                       ││
│  │  - Community Manager（社区管理）                  ││
│  │  - 接口抽象，支持替换为自研实现                   ││
│  └─────────────────────┬──────────────────────────┘ │
│                        │                             │
│  ┌─────────────────────▼──────────────────────────┐│
│  │             Storage Layer（存储层）             ││
│  │  - SQLite：实体、关系、社区、文档表              ││
│  │  - 文件系统：社区摘要文本                        ││
│  └────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────┘
                          │
           HTTP/WebSocket │ (与 meeting-voice-assistant 通信)
                          ▼
┌──────────────────────────────────────────────────────┐
│              meeting-voice-assistant                  │
│                   (localhost:8000)                   │
│                                                      │
│  ┌─────────────────┐    ┌──────────────────────────┐│
│  │   WebSocket     │    │   REST API Client        ││
│  │  (实时转写)      │    │  (上传/查询)              ││
│  └─────────────────┘    └──────────────────────────┘│
└──────────────────────────────────────────────────────┘
```

### 2.3 可视化方案

**前端渲染（选项 A）**：后端返回节点/边 JSON，前端用 ECharts（与 Vue 3 集成良好）渲染交互式知识图谱。

---

## 3. 系统设计

### 3.1 目录结构

```
graphrag-service/
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── router.py           # 路由汇总
│   │       ├── index.py            # 索引构建 API
│   │       ├── query.py            # 知识查询 API
│   │       ├── summarize.py        # 汇总 API
│   │       ├── graph.py            # 图谱可视化 API
│   │       ├── document.py         # 文档管理 API
│   │       └── realtime.py         # 实时上下文注入 API
│   ├── core/
│   │   ├── __init__.py
│   │   ├── base.py                 # GraphRAGCore 抽象基类
│   │   ├── microsoft/              # 微软 GraphRAG 实现
│   │   │   ├── __init__.py
│   │   │   ├── indexer.py          # 索引构建器
│   │   │   ├── query_engine.py     # 查询引擎
│   │   │   └── adapter.py          # 参数适配层
│   │   └── future/                 # 未来自研实现扩展点
│   │       ├── __init__.py
│   │       └── custom_core.py
│   ├── storage/
│   │   ├── __init__.py
│   │   ├── database.py             # SQLite 连接管理
│   │   └── models.py               # 数据模型
│   ├── service/
│   │   ├── __init__.py
│   │   └── context_injector.py    # 实时上下文注入器
│   ├── config.py                   # 配置管理
│   └── main.py                     # FastAPI 入口
├── rag_workspace/                   # GraphRAG 工作目录
│   ├── input/                       # 原始文档
│   ├── output/                      # 索引输出
│   └── prompts/                     # LLM prompt 模板
├── tests/
├── requirements.txt
└── .env
```

### 3.2 核心抽象接口（GraphRAGCore）

```python
class GraphRAGCore(ABC):
    """GraphRAG 核心抽象，所有实现必须实现此接口"""

    @abstractmethod
    async def index_document(self, doc_path: Path, namespace: str) -> IndexResult:
        """索引单个文档"""
        pass

    @abstractmethod
    async def index_documents_batch(self, doc_paths: list[Path], namespace: str) -> BatchIndexResult:
        """批量索引文档"""
        pass

    @abstractmethod
    async def query(
        self,
        query_text: str,
        namespace: str,
        top_k: int = 10,
        context: str | None = None,
    ) -> QueryResult:
        """知识查询"""
        pass

    @abstractmethod
    async def summarize(self, namespace: str, query: str | None = None) -> SummaryResult:
        """全局汇总"""
        pass

    @abstractmethod
    async def get_graph_data(self, namespace: str, max_nodes: int = 100) -> GraphData:
        """获取图谱数据（节点+边）"""
        pass

    @abstractmethod
    async def delete_document(self, doc_id: str, namespace: str) -> None:
        """删除文档及其关联实体"""
        pass
```

### 3.3 API 层设计

#### 索引构建

```
POST /api/v1/index
Content-Type: multipart/form-data

doc: File (pdf, txt, md, docx)

Response 200:
{
  "doc_id": "uuid",
  "status": "completed",
  "entities_count": 42,
  "relationships_count": 15,
  "communities_count": 3
}
```

#### 知识查询

```
POST /api/v1/query
Content-Type: application/json

{
  "query": "这个项目的技术架构是什么？",
  "namespace": "default",
  "top_k": 10,          // 动态参数
  "context": null       // 实时注入的上下文（如当前转写话题）
}

Response 200:
{
  "answer": "根据知识图谱，该项目采用...",
  "sources": [
    {"doc_id": "xxx", "chunk": "...", "similarity": 0.92}
  ],
  "entities": [
    {"name": "FastAPI", "type": "TOOL", "description": "..."}
  ]
}
```

#### 全局汇总

```
POST /api/v1/summarize
Content-Type: application/json

{
  "namespace": "default",
  "query": "总结本项目的主要内容"  // 可选，无 query 时做全面总结
}

Response 200:
{
  "summary": "本项目是一个...",
  "communities": [
    {"id": 0, "level": 0, "summary": "...", "entities_count": 15}
  ]
}
```

#### 图谱可视化

```
GET /api/v1/graph?namespace=default&max_nodes=100

Response 200:
{
  "nodes": [
    {"id": "entity_1", "name": "FastAPI", "type": "TOOL", "size": 10}
  ],
  "edges": [
    {"source": "entity_1", "target": "entity_2", "relation": "USES"}
  ]
}
```

#### 文档管理

```
DELETE /api/v1/documents/{doc_id}?namespace=default
GET /api/v1/documents?namespace=default
```

#### 实时上下文注入

```
POST /api/v1/realtime/query
Content-Type: application/json

{
  "query": "当前会议话题相关知识",
  "context": "会议正在讨论 GraphRAG 的索引构建流程",
  "namespace": "default",
  "top_k": 5
}
```

### 3.4 微软 GraphRAG 适配层

核心职责：**将 API 参数桥接到 GraphRAG 参数**

```python
class MicrosoftGraphRAGAdapter:
    """微软 GraphRAG 实现 + 参数适配"""

    def __init__(self, config: GraphRAGConfig):
        self.config = config
        # 初始化微软 graphrag workspace
        # 加载 prompts

    async def query(
        self,
        query_text: str,
        namespace: str,
        top_k: int,
        context: str | None,
    ) -> QueryResult:
        # 1. 参数映射
        #    API top_k → graphrag 的 max_entities / max_covRE
        #    context → 注入到 query prompt 前

        # 2. 调用 graphrag query engine
        #    local_search 或 global_search

        # 3. 结果映射
        #    GraphRAG Output → 统一 QueryResult
        pass
```

**参数映射规则：**

| API 参数 | GraphRAG 参数 | 说明 |
|---------|--------------|------|
| `top_k` | `max_entities`, `max_relationships` | 控制召回实体数量 |
| `context` | 注入到 query prompt | 作为 prefix 拼接到查询文本 |
| `namespace` | subdir under workspace | 通过目录隔离不同 namespace |
| `max_nodes` | `max_nodes` | 图可视化节点上限 |

### 3.5 实时上下文注入设计

```python
class RealtimeContext:
    """实时转写场景下的上下文"""

    def __init__(self, topic: str, speakers: list[str], timestamps: list[TimeRange]):
        self.topic = topic
        self.speakers = speakers
        self.timestamps = timestamps

class ContextInjector:
    """上下文注入器"""

    def inject(self, query: str, context: RealtimeContext) -> str:
        """将实时上下文注入到查询文本"""
        prompt = f"""当前会议背景：
- 话题：{context.topic}
- 与会人：{', '.join(context.speakers)}

用户查询：{query}"""
        return prompt
```

调用链：
```
WebSocket 转写服务
    → 检测到用户查询意图
    → 调用 POST /api/v1/realtime/query
    → ContextInjector 拼接 context + query
    → GraphRAG Core 查询
    → 返回知识提示
    → WebSocket 推送给前端
```

---

## 4. 数据模型

### 4.1 SQLite Schema

```sql
-- 文档表
CREATE TABLE documents (
    id TEXT PRIMARY KEY,
    namespace TEXT NOT NULL,
    filename TEXT NOT NULL,
    file_path TEXT NOT NULL,
    indexed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    chunk_count INTEGER,
    entity_count INTEGER
);

-- 实体表
CREATE TABLE entities (
    id TEXT PRIMARY KEY,
    doc_id TEXT REFERENCES documents(id),
    namespace TEXT NOT NULL,
    name TEXT NOT NULL,
    type TEXT,
    description TEXT,
    community_id TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 关系表
CREATE TABLE relationships (
    id TEXT PRIMARY KEY,
    source_entity_id TEXT REFERENCES entities(id),
    target_entity_id TEXT REFERENCES entities(id),
    relation_type TEXT,
    description TEXT,
    weight REAL DEFAULT 1.0,
    namespace TEXT NOT NULL
);

-- 社区表
CREATE TABLE communities (
    id TEXT PRIMARY KEY,
    namespace TEXT NOT NULL,
    level INTEGER,
    summary TEXT,
    parent_id TEXT
);

CREATE INDEX idx_entities_namespace ON entities(namespace);
CREATE INDEX idx_relationships_namespace ON relationships(namespace);
CREATE INDEX idx_communities_namespace ON communities(namespace);
```

---

## 5. 配置设计

### 5.1 环境变量

```env
# graphrag-service 配置
GRAPHRAG_SERVICE_PORT=8002

# GraphRAG LLM 配置（复用 meeting-assistant 的 DashScope）
LLM_PROVIDER=dashscope
LLM_API_KEY=sk-xxx
LLM_BASE_URL=https://dashscope.aliyuncs.com
LLM_MODEL=qwen-plus

# GraphRAG Workspace
GRAPHRAG_WORKSPACE=./rag_workspace

# 本地 API 模式（本地部署时优先使用 API）
USE_LOCAL_API=false
LOCAL_API_ENDPOINT=http://localhost:8002

# top_k 默认值
DEFAULT_TOP_K=10
```

---

## 6. 未来迁移到选项 C 的扩展点

| 模块 | 当前实现（选项 A） | 迁移到选项 C 的改动 |
|------|------------------|-------------------|
| Core 抽象 | `GraphRAGCore` 基类 | 不变 |
| 索引器 | `MicrosoftGraphRAGAdapter.index_*` | 替换为 `CustomIndexer` |
| 实体提取 | 微软 prompt | 自定义 Chinese prompt 或 NER 模型 |
| 图存储 | SQLite + GraphRAG Parquet | Neo4j 或增强 SQLite |
| 查询引擎 | GraphRAG local/global search | 自研检索 + 重新排序 |
| 摘要生成 | 微软 prompt | 中文优化 prompt |

**迁移原则**：Service 层 API 接口保持不变，只需替换 `GraphRAGCore` 的具体实现类。

---

## 7. 实施阶段

### 第一阶段（1-2 周）：基础框架

- [ ] 项目脚手架：`graphrag-service` 目录结构
- [ ] `GraphRAGCore` 抽象接口定义
- [ ] 微软 GraphRAG 适配层实现
- [ ] SQLite 存储层
- [ ] 基础配置管理

### 第二阶段（2-3 周）：核心 API

- [ ] 索引 API（`POST /api/v1/index`）
- [ ] 查询 API（`POST /api/v1/query`，含 top_k）
- [ ] 汇总 API（`POST /api/v1/summarize`）
- [ ] 文档管理 API（DELETE /api/v1/documents/{id}`）

### 第三阶段（1 周）：图谱与可视化

- [ ] 图数据 API（`GET /api/v1/graph`）
- [ ] ECharts 前端知识图谱组件

### 第四阶段（1 周）：实时集成

- [ ] 实时上下文注入 API（`POST /api/v1/realtime/query`）
- [ ] `ContextInjector` 实现
- [ ] 与 meeting-voice-assistant 的集成联调

### 第五阶段（0.5 周）：文档与部署

- [ ] 配置文件与部署脚本
- [ ] 接口文档（OpenAPI）

---

## 8. 验证方式

```bash
# 1. 启动服务
cd graphrag-service
uvicorn app.main:app --host 0.0.0.0 --port 8002

# 2. 上传文档索引
curl -X POST http://localhost:8002/api/v1/index \
  -F "doc=@./test_doc.pdf"

# 3. 查询知识
curl -X POST http://localhost:8002/api/v1/query \
  -H "Content-Type: application/json" \
  -d '{"query": "项目用了哪些技术？", "top_k": 5}'

# 4. 获取图谱数据
curl http://localhost:8002/api/v1/graph?namespace=default

# 5. 验证 meeting-assistant 集成
# 在转写过程中调用 /api/v1/realtime/query 验证上下文注入
```

---

## 附录：选型决策记录

| 决策点 | 选项 | 原因 |
|-------|------|------|
| GraphRAG 实现 | **选项 A**（微软 GraphRAG） | 快速落地，预留迁移空间 |
| 部署方式 | **独立服务**（port 8002） | 独立迭代、独立扩容 |
| 多租户 | **暂不需要** | 100 文档规模暂不需要 |
| 可视化 | **前端渲染**（ECharts） | Vue 栈统一，技术成熟 |
| 实时查询 | **独立接口 + 调用方注入 context** | 解耦低，扩展灵活 |

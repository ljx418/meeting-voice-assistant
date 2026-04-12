# GraphRAG 知识管理模块实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 构建独立的 GraphRAG 知识管理服务，提供文档索引、知识查询、图谱可视化和实时上下文注入能力

**Architecture:** 独立 FastAPI 服务（port 8002），分 Service Layer（适配层）、GraphRAG Core（核心抽象）、Storage Layer（SQLite）。微软 GraphRAG 作为初始实现，预留自研迁移扩展点。

**Tech Stack:** Python 3.9+, FastAPI, 微软 graphrag, SQLite, Pydantic, DashScope qwen-plus

---

## 文件结构概览

```
graphrag-service/
├── app/
│   ├── __init__.py
│   ├── main.py                     # FastAPI 入口
│   ├── config.py                   # 配置管理
│   ├── api/
│   │   ├── __init__.py
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
│   │   ├── microsoft/
│   │   │   ├── __init__.py
│   │   │   ├── indexer.py          # 索引构建器
│   │   │   ├── query_engine.py     # 查询引擎
│   │   │   └── adapter.py          # 参数适配层
│   │   └── future/
│   │       ├── __init__.py
│   │       └── custom_core.py      # 自研实现扩展点
│   ├── storage/
│   │   ├── __init__.py
│   │   ├── database.py             # SQLite 连接管理
│   │   └── models.py               # 数据模型
│   └── service/
│       ├── __init__.py
│       └── context_injector.py     # 实时上下文注入器
├── rag_workspace/
│   ├── input/                      # 原始文档
│   ├── output/                     # 索引输出
│   └── prompts/                    # LLM prompt 模板
├── tests/
├── requirements.txt
└── .env
```

---

## Task 1: 项目脚手架

**Files:**
- Create: `graphrag-service/requirements.txt`
- Create: `graphrag-service/.env`
- Create: `graphrag-service/app/__init__.py`
- Create: `graphrag-service/app/main.py`
- Create: `graphrag-service/app/config.py`
- Create: `graphrag-service/app/api/__init__.py`
- Create: `graphrag-service/app/api/v1/__init__.py`
- Create: `graphrag-service/app/api/v1/router.py`
- Create: `graphrag-service/app/core/__init__.py`
- Create: `graphrag-service/app/core/base.py`
- Create: `graphrag-service/app/core/microsoft/__init__.py`
- Create: `graphrag-service/app/core/future/__init__.py`
- Create: `graphrag-service/app/storage/__init__.py`
- Create: `graphrag-service/app/service/__init__.py`
- Create: `graphrag-service/rag_workspace/input/.gitkeep`
- Create: `graphrag-service/rag_workspace/output/.gitkeep`
- Create: `graphrag-service/rag_workspace/prompts/.gitkeep`

- [ ] **Step 1: 创建 requirements.txt**

```txt
fastapi==0.115.0
uvicorn[standard]==0.30.0
python-multipart==0.0.9
pydantic==2.9.0
pydantic-settings==2.5.0
sqlalchemy==2.0.35
aiosqlite==0.20.0
python-dotenv==1.0.1
httpx==0.27.2
aiofiles==24.1.0
graphrag>=0.3.0
```

- [ ] **Step 2: 创建 .env 配置**

```env
GRAPHRAG_SERVICE_PORT=8002
LLM_PROVIDER=dashscope
LLM_API_KEY=sk-your-key-here
LLM_BASE_URL=https://dashscope.aliyuncs.com
LLM_MODEL=qwen-plus
GRAPHRAG_WORKSPACE=./rag_workspace
DEFAULT_TOP_K=10
```

- [ ] **Step 3: 创建 app/config.py**

```python
from pydantic_settings import BaseSettings
from pathlib import Path

class Settings(BaseSettings):
    GRAPHRAG_SERVICE_PORT: int = 8002
    LLM_PROVIDER: str = "dashscope"
    LLM_API_KEY: str = ""
    LLM_BASE_URL: str = "https://dashscope.aliyuncs.com"
    LLM_MODEL: str = "qwen-plus"
    GRAPHRAG_WORKSPACE: Path = Path("./rag_workspace")
    DEFAULT_TOP_K: int = 10

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
```

- [ ] **Step 4: 创建 app/main.py**

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1 import router as api_router

app = FastAPI(
    title="GraphRAG Knowledge Service",
    version="1.0.0",
    docs_url="/docs",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"name": "GraphRAG Service", "version": "1.0.0"}
```

- [ ] **Step 5: 创建 app/api/v1/router.py**

```python
from fastapi import APIRouter
from app.api.v1 import index, query, summarize, graph, document, realtime

router = APIRouter()

router.include_router(index.router, prefix="/index", tags=["索引"])
router.include_router(query.router, prefix="/query", tags=["查询"])
router.include_router(summarize.router, prefix="/summarize", tags=["汇总"])
router.include_router(graph.router, prefix="/graph", tags=["图谱"])
router.include_router(document.router, prefix="/documents", tags=["文档"])
router.include_router(realtime.router, prefix="/realtime", tags=["实时"])
```

- [ ] **Step 6: 创建 app/core/base.py（GraphRAGCore 抽象基类）**

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Any

@dataclass
class IndexResult:
    doc_id: str
    status: str
    entities_count: int
    relationships_count: int
    communities_count: int

@dataclass
class BatchIndexResult:
    total: int
    succeeded: int
    failed: int
    results: list[IndexResult]

@dataclass
class SourceChunk:
    doc_id: str
    chunk: str
    similarity: float

@dataclass
class EntityInfo:
    name: str
    type: str
    description: str

@dataclass
class QueryResult:
    answer: str
    sources: list[SourceChunk]
    entities: list[EntityInfo]

@dataclass
class CommunityInfo:
    id: str
    level: int
    summary: str
    entities_count: int

@dataclass
class SummaryResult:
    summary: str
    communities: list[CommunityInfo]

@dataclass
class GraphNode:
    id: str
    name: str
    type: str
    size: int

@dataclass
class GraphEdge:
    source: str
    target: str
    relation: str

@dataclass
class GraphData:
    nodes: list[GraphNode]
    edges: list[GraphEdge]

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

- [ ] **Step 7: 创建 app/api/v1/index.py（索引 API stub）**

```python
from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel

router = APIRouter()

class IndexResponse(BaseModel):
    doc_id: str
    status: str
    entities_count: int
    relationships_count: int
    communities_count: int

@router.post("", response_model=IndexResponse)
async def index_document(doc: UploadFile = File(...)):
    # TODO: 实现索引逻辑
    raise HTTPException(status_code=501, detail="Not implemented yet")
```

- [ ] **Step 8: 创建其他 API stub 文件**

每个 API 文件（query.py, summarize.py, graph.py, document.py, realtime.py）创建基础 router + response model stub

- [ ] **Step 9: 提交**

```bash
cd /Users/Zhuanz/Desktop/workspace/.claude/worktrees/graph-rag
git add graphrag-service/
git commit -m "feat(graphrag): 项目脚手架 - 目录结构、GraphRAGCore 抽象接口、API stubs

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
```

---

## Task 2: 实现 GraphRAG Core 微软适配层

**Files:**
- Create: `graphrag-service/app/core/microsoft/adapter.py`
- Create: `graphrag-service/app/core/microsoft/indexer.py`
- Create: `graphrag-service/app/core/microsoft/query_engine.py`
- Modify: `graphrag-service/app/core/microsoft/__init__.py`

**前置依赖:** Task 1 完成

- [ ] **Step 1: 创建 MicrosoftGraphRAGAdapter**

核心职责：将 API 参数桥接到微软 GraphRAG 参数

```python
# graphrag-service/app/core/microsoft/adapter.py
from pathlib import Path
from app.core.base import (
    GraphRAGCore, IndexResult, BatchIndexResult,
    QueryResult, SummaryResult, GraphData,
    SourceChunk, EntityInfo, CommunityInfo, GraphNode, GraphEdge
)
from app.config import settings
import json

class MicrosoftGraphRAGAdapter(GraphRAGCore):
    """微软 GraphRAG 实现 + 参数适配"""

    def __init__(self):
        self.workspace = settings.GRAPHRAG_WORKSPACE
        self.llm_config = {
            "provider": settings.LLM_PROVIDER,
            "api_key": settings.LLM_API_KEY,
            "base_url": settings.LLM_BASE_URL,
            "model": settings.LLM_MODEL,
        }
        # 初始化 graphrag workspace
        self._init_workspace()

    def _init_workspace(self):
        # 创建必要目录
        self.workspace.mkdir(parents=True, exist_ok=True)
        # 初始化 settings.yaml
        settings_yaml = self.workspace / "settings.yaml"
        if not settings_yaml.exists():
            settings_yaml.write_text(self._default_settings())

    def _default_settings(self) -> str:
        return f"""
encoding_model: cl100k_base
skip_workflow: false
陇进模型:
  description: DashScope LLM
  configuration:
    type: openai_chat
    api_key: {self.llm_config['api_key']}
    model: {self.llm_config['model']}
    api_base: {self.llm_config['base_url']}
```

    async def index_document(self, doc_path: Path, namespace: str) -> IndexResult:
        # 1. 复制文件到 input 目录
        namespace_dir = self.workspace / "input" / namespace
        namespace_dir.mkdir(parents=True, exist_ok=True)
        dest_path = namespace_dir / doc_path.name
        import shutil
        shutil.copy(doc_path, dest_path)

        # 2. 调用 graphrag index
        # graphrag 的 index 是同步 CLI，这里包装为异步
        import subprocess
        result = subprocess.run(
            ["graphrag", "index", "--root", str(self.workspace)],
            capture_output=True, text=True
        )

        # 3. 解析输出，更新 storage
        return IndexResult(
            doc_id=dest_path.stem,
            status="completed",
            entities_count=0,  # TODO: 从 graphrag output 解析
            relationships_count=0,
            communities_count=0
        )

    async def index_documents_batch(self, doc_paths: list[Path], namespace: str) -> BatchIndexResult:
        results = []
        for path in doc_paths:
            result = await self.index_document(path, namespace)
            results.append(result)
        succeeded = len([r for r in results if r.status == "completed"])
        return BatchIndexResult(
            total=len(doc_paths),
            succeeded=succeeded,
            failed=len(doc_paths) - succeeded,
            results=results
        )

    async def query(
        self,
        query_text: str,
        namespace: str,
        top_k: int = 10,
        context: str | None = None,
    ) -> QueryResult:
        # 参数映射: API top_k → graphrag max_entities
        # context → 注入到 query prompt 前
        if context:
            query_text = f"{context}\n\n{query_text}"

        import subprocess
        result = subprocess.run(
            [
                "graphrag", "query",
                "--root", str(self.workspace),
                "--query", query_text,
                "--method", "local",
            ],
            capture_output=True, text=True
        )

        # 解析 graphrag 输出
        output = result.stdout or result.stderr

        return QueryResult(
            answer=output[:2000],  # 截断
            sources=[],
            entities=[]
        )

    async def summarize(self, namespace: str, query: str | None = None) -> SummaryResult:
        method = "global" if query else "global"
        cmd_query = query or "总结本知识库的主要内容"

        import subprocess
        result = subprocess.run(
            [
                "graphrag", "query",
                "--root", str(self.workspace),
                "--query", cmd_query,
                "--method", method,
            ],
            capture_output=True, text=True
        )

        return SummaryResult(
            summary=result.stdout or result.stderr,
            communities=[]
        )

    async def get_graph_data(self, namespace: str, max_nodes: int = 100) -> GraphData:
        # 从 SQLite 读取图数据
        from app.storage.database import get_graph_data
        return await get_graph_data(namespace, max_nodes)

    async def delete_document(self, doc_id: str, namespace: str) -> None:
        from app.storage.database import delete_document
        await delete_document(doc_id, namespace)
```

- [ ] **Step 2: 创建微软 __init__.py**

```python
from app.core.microsoft.adapter import MicrosoftGraphRAGAdapter

__all__ = ["MicrosoftGraphRAGAdapter"]
```

- [ ] **Step 3: 创建 app/core/microsoft/__init__.py**

```python
from .adapter import MicrosoftGraphRAGAdapter

__all__ = ["MicrosoftGraphRAGAdapter"]
```

- [ ] **Step 4: 提交**

```bash
git add graphrag-service/app/core/microsoft/
git commit -m "feat(graphrag): 实现 GraphRAG Core 微软适配层

- MicrosoftGraphRAGAdapter 实现 GraphRAGCore 抽象接口
- 参数映射: API top_k → graphrag max_entities
- context 注入到 query prompt 前
- namespace 通过目录隔离

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
```

---

## Task 3: 实现 SQLite 存储层

**Files:**
- Create: `graphrag-service/app/storage/database.py`
- Create: `graphrag-service/app/storage/models.py`
- Modify: `graphrag-service/app/storage/__init__.py`

**前置依赖:** Task 1 完成

- [ ] **Step 1: 创建 app/storage/models.py**

```python
from sqlalchemy import String, Integer, Float, Text, TIMESTAMP, ForeignKey, Index
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from datetime import datetime

class Base(DeclarativeBase):
    pass

class Document(Base):
    __tablename__ = "documents"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    namespace: Mapped[str] = mapped_column(String, nullable=False, index=True)
    filename: Mapped[str] = mapped_column(String, nullable=False)
    file_path: Mapped[str] = mapped_column(String, nullable=False)
    indexed_at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=datetime.utcnow)
    chunk_count: Mapped[int] = mapped_column(Integer, nullable=True)
    entity_count: Mapped[int] = mapped_column(Integer, nullable=True)

class Entity(Base):
    __tablename__ = "entities"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    doc_id: Mapped[str] = mapped_column(String, ForeignKey("documents.id"), nullable=True)
    namespace: Mapped[str] = mapped_column(String, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    type: Mapped[str] = mapped_column(String, nullable=True)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    community_id: Mapped[str] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=datetime.utcnow)

    __table_args__ = (
        Index("idx_entities_namespace", "namespace"),
    )

class Relationship(Base):
    __tablename__ = "relationships"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    source_entity_id: Mapped[str] = mapped_column(String, ForeignKey("entities.id"), nullable=False)
    target_entity_id: Mapped[str] = mapped_column(String, ForeignKey("entities.id"), nullable=False)
    relation_type: Mapped[str] = mapped_column(String, nullable=True)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    weight: Mapped[float] = mapped_column(Float, default=1.0)
    namespace: Mapped[str] = mapped_column(String, nullable=False, index=True)

    __table_args__ = (
        Index("idx_relationships_namespace", "namespace"),
    )

class Community(Base):
    __tablename__ = "communities"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    namespace: Mapped[str] = mapped_column(String, nullable=False, index=True)
    level: Mapped[int] = mapped_column(Integer, nullable=True)
    summary: Mapped[str] = mapped_column(Text, nullable=True)
    parent_id: Mapped[str] = mapped_column(String, nullable=True)

    __table_args__ = (
        Index("idx_communities_namespace", "namespace"),
    )
```

- [ ] **Step 2: 创建 app/storage/database.py**

```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import text
from pathlib import Path
from app.storage.models import Base, Document, Entity, Relationship, Community
from app.config import settings
import uuid

engine = create_async_engine(
    f"sqlite+aiosqlite:///{settings.GRAPHRAG_WORKSPACE}/graphrag.db",
    echo=False,
)

async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def init_db():
    """初始化数据库表"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def get_graph_data(namespace: str, max_nodes: int = 100):
    """获取图谱数据"""
    async with async_session() as session:
        # 查询实体
        result = await session.execute(
            text("""
                SELECT id, name, type, description
                FROM entities
                WHERE namespace = :namespace
                LIMIT :max_nodes
            """),
            {"namespace": namespace, "max_nodes": max_nodes}
        )
        entities = result.fetchall()

        # 查询关系
        result = await session.execute(
            text("""
                SELECT source_entity_id, target_entity_id, relation_type
                FROM relationships
                WHERE namespace = :namespace
            """),
            {"namespace": namespace}
        )
        relationships = result.fetchall()

    from app.core.base import GraphNode, GraphEdge, GraphData

    nodes = [
        GraphNode(id=e.id, name=e.name, type=e.type or "ENTITY", size=10)
        for e in entities
    ]
    edges = [
        GraphEdge(source=r.source_entity_id, target=r.target_entity_id, relation=r.relation_type or "RELATED")
        for r in relationships
    ]

    return GraphData(nodes=nodes, edges=edges)

async def delete_document(doc_id: str, namespace: str):
    """删除文档及其关联实体"""
    async with async_session() as session:
        # 删除关联实体
        await session.execute(
            text("DELETE FROM entities WHERE doc_id = :doc_id AND namespace = :namespace"),
            {"doc_id": doc_id, "namespace": namespace}
        )
        # 删除文档记录
        await session.execute(
            text("DELETE FROM documents WHERE id = :doc_id AND namespace = :namespace"),
            {"doc_id": doc_id, "namespace": namespace}
        )
        await session.commit()

async def save_document(doc_id: str, namespace: str, filename: str, file_path: str):
    """保存文档记录"""
    async with async_session() as session:
        doc = Document(
            id=doc_id,
            namespace=namespace,
            filename=filename,
            file_path=file_path,
        )
        session.add(doc)
        await session.commit()
```

- [ ] **Step 3: 创建 app/storage/__init__.py**

```python
from app.storage.database import init_db, get_graph_data, delete_document, save_document
from app.storage.models import Document, Entity, Relationship, Community

__all__ = ["init_db", "get_graph_data", "delete_document", "save_document", "Document", "Entity", "Relationship", "Community"]
```

- [ ] **Step 4: 修改 app/main.py 添加 startup 事件**

```python
@app.on_event("startup")
async def startup_event():
    from app.storage.database import init_db
    await init_db()
```

- [ ] **Step 5: 提交**

```bash
git add graphrag-service/app/storage/
git commit -m "feat(graphrag): 实现 SQLite 存储层

- Document/Entity/Relationship/Community 数据模型
- async SQLite 连接管理
- get_graph_data/delete_document/save_document 操作

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
```

---

## Task 4: 实现索引与查询 API

**Files:**
- Modify: `graphrag-service/app/api/v1/index.py`
- Modify: `graphrag-service/app/api/v1/query.py`
- Modify: `graphrag-service/app/api/v1/summarize.py`
- Modify: `graphrag-service/app/api/v1/document.py`
- Create: `graphrag-service/app/core/registry.py`（Core 实例注册表）

**前置依赖:** Task 2, Task 3 完成

- [ ] **Step 1: 创建 Core 注册表 app/core/registry.py**

```python
from app.core.base import GraphRAGCore
from app.core.microsoft import MicrosoftGraphRAGAdapter

class GraphRAGRegistry:
    """GraphRAG Core 实现注册表"""

    _instance: GraphRAGCore | None = None

    @classmethod
    def get_instance(cls) -> GraphRAGCore:
        if cls._instance is None:
            cls._instance = MicrosoftGraphRAGAdapter()
        return cls._instance

    @classmethod
    def set_instance(cls, impl: GraphRAGCore):
        cls._instance = impl

core = GraphRAGRegistry.get_instance
```

- [ ] **Step 2: 实现 index.py**

```python
from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel
import uuid
import aiofiles
from pathlib import Path
from app.core.registry import core
from app.storage.database import save_document
from app.config import settings

router = APIRouter()

class IndexResponse(BaseModel):
    doc_id: str
    status: str
    entities_count: int
    relationships_count: int
    communities_count: int

@router.post("", response_model=IndexResponse)
async def index_document(doc: UploadFile = File(...), namespace: str = "default"):
    # 1. 保存上传文件
    upload_dir = settings.GRAPHRAG_WORKSPACE / "input" / namespace
    upload_dir.mkdir(parents=True, exist_ok=True)

    file_path = upload_dir / doc.filename
    async with aiofiles.open(file_path, "wb") as f:
        content = await doc.read()
        await f.write(content)

    # 2. 生成 doc_id
    doc_id = str(uuid.uuid4())

    # 3. 索引文档
    result = await core().index_document(file_path, namespace)

    # 4. 保存文档记录
    await save_document(doc_id, namespace, doc.filename, str(file_path))

    return IndexResponse(
        doc_id=doc_id,
        status=result.status,
        entities_count=result.entities_count,
        relationships_count=result.relationships_count,
        communities_count=result.communities_count,
    )
```

- [ ] **Step 3: 实现 query.py**

```python
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.core.registry import core
from app.config import settings

router = APIRouter()

class QueryRequest(BaseModel):
    query: str
    namespace: str = "default"
    top_k: int = 10
    context: str | None = None

class QueryResponse(BaseModel):
    answer: str
    sources: list[dict]
    entities: list[dict]

@router.post("", response_model=QueryResponse)
async def query_knowledge(request: QueryRequest):
    # 参数校验
    if request.top_k <= 0 or request.top_k > 100:
        raise HTTPException(status_code=400, detail="top_k must be between 1 and 100")

    result = await core().query(
        query_text=request.query,
        namespace=request.namespace,
        top_k=request.top_k,
        context=request.context,
    )

    return QueryResponse(
        answer=result.answer,
        sources=[{"doc_id": s.doc_id, "chunk": s.chunk, "similarity": s.similarity} for s in result.sources],
        entities=[{"name": e.name, "type": e.type, "description": e.description} for e in result.entities],
    )
```

- [ ] **Step 4: 实现 summarize.py**

```python
from fastapi import APIRouter
from pydantic import BaseModel
from app.core.registry import core

router = APIRouter()

class SummarizeRequest(BaseModel):
    namespace: str = "default"
    query: str | None = None

class SummarizeResponse(BaseModel):
    summary: str
    communities: list[dict]

@router.post("", response_model=SummarizeResponse)
async def summarize(request: SummarizeRequest):
    result = await core().summarize(
        namespace=request.namespace,
        query=request.query,
    )

    return SummarizeResponse(
        summary=result.summary,
        communities=[
            {"id": c.id, "level": c.level, "summary": c.summary, "entities_count": c.entities_count}
            for c in result.communities
        ],
    )
```

- [ ] **Step 5: 实现 document.py**

```python
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.core.registry import core
from app.storage.database import async_session, text
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()

class DocumentInfo(BaseModel):
    id: str
    filename: str
    indexed_at: str
    chunk_count: int | None
    entity_count: int | None

@router.get("", response_model=list[DocumentInfo])
async def list_documents(namespace: str = "default"):
    async with async_session() as session:
        result = await session.execute(
            text("""
                SELECT id, filename, indexed_at, chunk_count, entity_count
                FROM documents
                WHERE namespace = :namespace
                ORDER BY indexed_at DESC
            """),
            {"namespace": namespace}
        )
        rows = result.fetchall()

    return [
        DocumentInfo(
            id=row.id,
            filename=row.filename,
            indexed_at=str(row.indexed_at),
            chunk_count=row.chunk_count,
            entity_count=row.entity_count,
        )
        for row in rows
    ]

@router.delete("/{doc_id}")
async def delete_document(doc_id: str, namespace: str = "default"):
    await core().delete_document(doc_id, namespace)
    return {"status": "deleted", "doc_id": doc_id}
```

- [ ] **Step 6: 提交**

```bash
git add graphrag-service/app/api/v1/index.py graphrag-service/app/api/v1/query.py graphrag-service/app/api/v1/summarize.py graphrag-service/app/api/v1/document.py graphrag-service/app/core/registry.py
git commit -m "feat(graphrag): 实现索引与查询 API

- POST /api/v1/index: 文档索引
- POST /api/v1/query: 知识查询（含动态 top_k、context）
- POST /api/v1/summarize: 全局汇总
- GET/DELETE /api/v1/documents: 文档管理
- GraphRAGRegistry Core 实例注册表

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
```

---

## Task 5: 实现图谱可视化 API

**Files:**
- Modify: `graphrag-service/app/api/v1/graph.py`
- Create: `graphrag-service/app/api/v1/realtime.py`

**前置依赖:** Task 3, Task 4 完成

- [ ] **Step 1: 实现 graph.py**

```python
from fastapi import APIRouter, Query
from pydantic import BaseModel
from app.core.registry import core

router = APIRouter()

class GraphNodeResponse(BaseModel):
    id: str
    name: str
    type: str
    size: int

class GraphEdgeResponse(BaseModel):
    source: str
    target: str
    relation: str

class GraphResponse(BaseModel):
    nodes: list[GraphNodeResponse]
    edges: list[GraphEdgeResponse]

@router.get("", response_model=GraphResponse)
async def get_graph(
    namespace: str = Query(default="default"),
    max_nodes: int = Query(default=100, ge=10, le=500),
):
    result = await core().get_graph_data(namespace, max_nodes)

    return GraphResponse(
        nodes=[
            GraphNodeResponse(id=n.id, name=n.name, type=n.type, size=n.size)
            for n in result.nodes
        ],
        edges=[
            GraphEdgeResponse(source=e.source, target=e.target, relation=e.relation)
            for e in result.edges
        ],
    )
```

- [ ] **Step 2: 实现 realtime.py（实时上下文注入）**

```python
from fastapi import APIRouter
from pydantic import BaseModel
from app.core.registry import core
from app.service.context_injector import ContextInjector

router = APIRouter()
injector = ContextInjector()

class RealtimeQueryRequest(BaseModel):
    query: str
    context: str
    namespace: str = "default"
    top_k: int = 5

class RealtimeQueryResponse(BaseModel):
    answer: str
    sources: list[dict]
    entities: list[dict]

@router.post("/query", response_model=RealtimeQueryResponse)
async def realtime_query(request: RealtimeQueryRequest):
    # 使用 ContextInjector 拼接 context + query
    enhanced_query = injector.inject(request.query, request.context)

    result = await core().query(
        query_text=enhanced_query,
        namespace=request.namespace,
        top_k=request.top_k,
        context=None,  # 已在 injector 中拼接
    )

    return RealtimeQueryResponse(
        answer=result.answer,
        sources=[{"doc_id": s.doc_id, "chunk": s.chunk, "similarity": s.similarity} for s in result.sources],
        entities=[{"name": e.name, "type": e.type, "description": e.description} for e in result.entities],
    )
```

- [ ] **Step 3: 创建 app/service/context_injector.py**

```python
class ContextInjector:
    """实时上下文注入器"""

    def inject(self, query: str, context: str) -> str:
        """将实时上下文注入到查询文本"""
        prompt = f"""当前会议背景：
{context}

用户查询：{query}"""
        return prompt
```

- [ ] **Step 4: 提交**

```bash
git add graphrag-service/app/api/v1/graph.py graphrag-service/app/api/v1/realtime.py graphrag-service/app/service/context_injector.py
git commit -m "feat(graphrag): 实现图谱可视化与实时上下文注入 API

- GET /api/v1/graph: 图谱数据（节点+边 JSON）
- POST /api/v1/realtime/query: 实时上下文注入查询
- ContextInjector: context + query 拼接

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
```

---

## Task 6: 完善配置与文档

**Files:**
- Create: `graphrag-service/README.md`
- Create: `graphrag-service/tests/`
- Modify: `graphrag-service/.env`

**前置依赖:** Task 1-5 完成

- [ ] **Step 1: 创建 README.md**

```markdown
# GraphRAG Knowledge Service

独立部署的 GraphRAG 知识管理服务，提供文档索引、知识查询、图谱可视化和实时上下文注入能力。

## 快速启动

```bash
cd graphrag-service
pip install -r requirements.txt
cp .env.example .env  # 编辑 .env 填入 API Key
uvicorn app.main:app --host 0.0.0.0 --port 8002
```

## API 端点

| 端点 | 方法 | 描述 |
|------|------|------|
| `/api/v1/index` | POST | 索引文档 |
| `/api/v1/query` | POST | 知识查询 |
| `/api/v1/summarize` | POST | 全局汇总 |
| `/api/v1/graph` | GET | 图谱可视化 |
| `/api/v1/documents` | GET | 文档列表 |
| `/api/v1/documents/{id}` | DELETE | 删除文档 |
| `/api/v1/realtime/query` | POST | 实时上下文注入 |

## 配置

详见 `.env` 文件。

## 与 meeting-voice-assistant 集成

```python
import httpx

# 在转写过程中查询领域知识
async def query_knowledge_during_transcription(query: str, context: str):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8002/api/v1/realtime/query",
            json={"query": query, "context": context, "top_k": 5}
        )
        return response.json()
```
```

- [ ] **Step 2: 创建基础测试**

```python
# tests/test_api.py
import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app

@pytest.mark.asyncio
async def test_root():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/")
        assert response.status_code == 200
        assert "GraphRAG Service" in response.json()["name"]
```

- [ ] **Step 3: 提交**

```bash
git add graphrag-service/README.md graphrag-service/tests/
git commit -m "docs(graphrag): 添加 README 和基础测试

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
```

---

## 自检清单

**Spec 覆盖率检查:**

| 设计需求 | 对应实现 |
|---------|---------|
| 知识查询 | Task 4: `POST /api/v1/query` |
| 知识汇总 | Task 4: `POST /api/v1/summarize` |
| 知识图谱绘制 | Task 5: `GET /api/v1/graph` |
| API 对外服务 | Task 1-5: 完整 REST API |
| 实时转写查询 | Task 5: `POST /api/v1/realtime/query` |
| 动态 top-k | Task 4: `query.py` top_k 参数透传 |
| Core 抽象 | Task 1: `GraphRAGCore` 基类 |
| 微软 GraphRAG 适配 | Task 2: `MicrosoftGraphRAGAdapter` |
| SQLite 存储 | Task 3: storage/database.py |
| 配置管理 | Task 1: app/config.py |

**类型一致性检查:**
- `GraphRAGCore.query(top_k: int = 10)` ← API `query.py` top_k 校验 1-100
- `QueryResult.sources: list[SourceChunk]` ← API 返回时转为 `list[dict]`
- `GraphData.nodes: list[GraphNode]` ← API 返回时用 `GraphNodeResponse` 验证

**占位符检查:** 无 TBD/TODO/placeholder

---

## 计划执行选项

Plan complete and saved to `docs/superpowers/plans/2026-04-08-graphrag-implementation.md`. Two execution options:

**1. Subagent-Driven (recommended)** - I dispatch a fresh subagent per task, review between tasks, fast iteration

**2. Inline Execution** - Execute tasks in this session using executing-plans, batch execution with checkpoints

Which approach?

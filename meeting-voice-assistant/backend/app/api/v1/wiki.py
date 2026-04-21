"""
Wiki API 路由

基于 ADR-002 设计文档实现
Wiki 与 GraphRAG 集成：
- 实体识别、关系提取
- 长期任务（SSE 流式索引）
- 工作流识别
"""

import asyncio
import json
import httpx
from fastapi import APIRouter, HTTPException, Query, Path
from fastapi.responses import StreamingResponse
from typing import Optional, List
from pathlib import Path
import logging

logger = logging.getLogger("wiki.api")

from app.models.wiki import (
    WikiDocumentCreate,
    WikiDocumentUpdate,
    WikiDocument,
    WikiDocumentVersion,
    WikiSearchResponse,
    WikiIndexResponse,
    WikiFromMeetingRequest,
    APIResponse,
    PaginatedResponse,
)
from app.db.wiki_repository import WikiRepository
from app.config import config

router = APIRouter(prefix="/wiki", tags=["wiki"])

# 全局仓库实例
_wiki_repo: Optional[WikiRepository] = None


def get_wiki_repo() -> WikiRepository:
    """获取 Wiki 仓库实例"""
    global _wiki_repo
    if _wiki_repo is None:
        _wiki_repo = WikiRepository()
    return _wiki_repo


# ========== 文档管理 ==========

@router.post("/docs", response_model=APIResponse, status_code=201)
async def create_document(doc: WikiDocumentCreate, auto_index: bool = Query(False, description="是否自动索引到 GraphRAG")):
    """创建 Wiki 文档"""
    repo = get_wiki_repo()
    result = repo.create_document(
        title=doc.title,
        content=doc.content,
        doc_type=doc.doc_type.value,
        parent_id=doc.parent_id,
        meeting_id=doc.meeting_id,
        tags=doc.tags,
    )

    # 如果启用自动索引，在后台触发
    if auto_index:
        asyncio.create_task(_auto_index_document(result["id"]))

    return APIResponse(success=True, data=result, message="Document created")


async def _auto_index_document(doc_id: str) -> None:
    """自动索引文档到 GraphRAG（后台任务）"""
    try:
        await asyncio.sleep(1)  # 等待文档创建完成
        repo = get_wiki_repo()
        doc = repo.get_document(doc_id)
        if not doc:
            return

        result = await _index_doc_to_graphrag(doc, doc_id)
        if result.get("success"):
            repo.update_graphrag_index(
                doc_id=doc_id,
                entities=result.get("entities", []),
                relationships=result.get("relationships", []),
                graphrag_doc_id=result.get("graphrag_doc_id")
            )
    except Exception as e:
        logger.error(f"[Wiki] Auto-index failed for {doc_id}: {e}")


@router.get("/docs", response_model=PaginatedResponse)
async def list_documents(
    doc_type: Optional[str] = Query(None, description="文档类型过滤"),
    meeting_id: Optional[str] = Query(None, description="会议 ID 过滤"),
    parent_id: Optional[str] = Query(None, description="父文档 ID"),
    tags: Optional[str] = Query(None, description="标签过滤，逗号分隔"),
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=100, description="每页数量"),
):
    """列出文档（支持分页和过滤）"""
    repo = get_wiki_repo()
    tag_list = tags.split(",") if tags else None
    items, total = repo.list_documents(
        doc_type=doc_type,
        meeting_id=meeting_id,
        parent_id=parent_id,
        tags=tag_list,
        page=page,
        size=size,
    )
    return PaginatedResponse(items=items, total=total, page=page, size=size)


@router.get("/docs/{doc_id}", response_model=APIResponse)
async def get_document(doc_id: str = Path(..., description="文档 ID")):
    """获取文档详情"""
    repo = get_wiki_repo()
    doc = repo.get_document(doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return APIResponse(success=True, data=doc)


@router.put("/docs/{doc_id}", response_model=APIResponse)
async def update_document(
    doc_id: str,
    update: WikiDocumentUpdate,
    auto_index: bool = Query(False, description="是否自动索引到 GraphRAG"),
):
    """更新文档（自动创建版本快照）"""
    repo = get_wiki_repo()
    current = repo.get_document(doc_id)
    if not current:
        raise HTTPException(status_code=404, detail="Document not found")

    result = repo.update_document(
        doc_id=doc_id,
        title=update.title,
        content=update.content,
        tags=update.tags,
        parent_id=update.parent_id,
        change_summary=update.change_summary,
    )
    if not result:
        raise HTTPException(status_code=500, detail="Failed to update document")

    # 如果启用自动索引，在后台触发
    if auto_index:
        asyncio.create_task(_auto_index_document(doc_id))

    return APIResponse(
        success=True,
        data={"id": doc_id, "version": result["version"]},
        message=f"Document updated. Version {result['version']} created."
    )


@router.delete("/docs/{doc_id}", response_model=APIResponse)
async def delete_document(doc_id: str):
    """删除文档（软删除）"""
    repo = get_wiki_repo()
    success = repo.delete_document(doc_id)
    if not success:
        raise HTTPException(status_code=404, detail="Document not found")
    return APIResponse(success=True, message="Document deleted")


# ========== 版本管理 ==========

@router.get("/docs/{doc_id}/versions", response_model=APIResponse)
async def get_document_versions(doc_id: str):
    """获取文档版本历史"""
    repo = get_wiki_repo()
    doc = repo.get_document(doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    versions = repo.get_document_versions(doc_id)
    return APIResponse(success=True, data=versions)


@router.post("/docs/{doc_id}/restore/{version}", response_model=APIResponse)
async def restore_version(doc_id: str, version: int):
    """恢复到指定版本"""
    repo = get_wiki_repo()
    doc = repo.get_document(doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    result = repo.restore_version(doc_id, version)
    if not result:
        raise HTTPException(status_code=404, detail="Version not found")

    return APIResponse(
        success=True,
        data={"id": doc_id, "version": result["version"]},
        message=f"Restored to version {version}"
    )


# ========== 搜索与查询 ==========

@router.get("/search", response_model=WikiSearchResponse)
async def search_documents(
    q: str = Query(..., description="搜索关键词"),
    doc_type: Optional[str] = Query(None, description="文档类型过滤"),
    tags: Optional[str] = Query(None, description="标签过滤"),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
):
    """全文搜索文档"""
    repo = get_wiki_repo()
    tag_list = tags.split(",") if tags else None

    items, total = repo.search(
        query=q,
        doc_type=doc_type,
        tags=tag_list,
        page=page,
        size=size,
    )

    return WikiSearchResponse(
        items=items,
        total=total,
        page=page,
        size=size,
    )


@router.get("/docs/{doc_id}/children", response_model=APIResponse)
async def get_document_children(doc_id: str):
    """获取子文档"""
    repo = get_wiki_repo()
    doc = repo.get_document(doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    children = repo.get_document_children(doc_id)
    return APIResponse(success=True, data=children)


@router.get("/tags", response_model=APIResponse)
async def get_all_tags():
    """获取所有标签"""
    repo = get_wiki_repo()
    tags = repo.get_all_tags()
    return APIResponse(success=True, data=tags)


# ========== 会议集成 ==========

@router.post("/from-meeting/{meeting_id}", response_model=APIResponse, status_code=202)
async def create_wiki_from_meeting(
    meeting_id: str,
    request: WikiFromMeetingRequest,
):
    """
    从会议生成 Wiki 文档

    注意：此功能需要会议数据支持，当前为占位实现
    """
    # TODO: 集成会议数据获取
    # 1. 从会议存储获取会议转写和分析结果
    # 2. 根据 doc_type 生成对应格式的 Wiki 文档
    # 3. 自动创建章节结构

    repo = get_wiki_repo()

    # 临时实现：创建占位文档
    result = repo.create_document(
        title=f"Meeting {meeting_id} Wiki",
        content=f"# Meeting {meeting_id}\n\nAuto-generated wiki from meeting.",
        doc_type=request.doc_type.value,
        meeting_id=meeting_id,
        tags=request.tags or ["auto-generated"],
    )

    return APIResponse(
        success=True,
        data={"job_id": f"job_{meeting_id}", "document_id": result["id"]},
        message="Wiki document generation started"
    )


@router.get("/by-meeting/{meeting_id}", response_model=APIResponse)
async def get_documents_by_meeting(meeting_id: str):
    """获取会议关联的文档"""
    repo = get_wiki_repo()
    items, total = repo.list_documents(meeting_id=meeting_id, page=1, size=100)
    return APIResponse(success=True, data={"items": items, "total": total})


# ========== GraphRAG 集成 ==========

async def _index_doc_to_graphrag(doc: dict, doc_id: str) -> dict:
    """索引文档到 GraphRAG 并返回结果"""
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            import tempfile

            # 保存临时文件
            with tempfile.NamedTemporaryFile(
                mode='w',
                suffix='.txt',
                prefix=f'wiki_{doc_id}_',
                delete=False,
            ) as f:
                f.write(f"# {doc['title']}\n\n{doc['content']}")
                temp_path = f.name

            with open(temp_path, 'rb') as f:
                files = {'doc': (f'{doc_id}.txt', f, 'text/plain')}
                response = await client.post(
                    f"{config.graphrag.service_url}/api/v1/index/",
                    files=files
                )

            # 清理临时文件
            Path(temp_path).unlink(missing_ok=True)

            if response.status_code == 200:
                result = response.json()
                # 获取实体和关系信息
                entities = await _get_graphrag_entities(doc_id)
                relationships = await _get_graphrag_relationships(doc_id)

                return {
                    "success": True,
                    "entities_count": result.get("entities_count", 0),
                    "relationships_count": result.get("relationships_count", 0),
                    "entities": entities,
                    "relationships": relationships,
                    "graphrag_doc_id": result.get("doc_id")
                }
            else:
                return {
                    "success": False,
                    "message": f"Index failed: {response.status_code}"
                }
    except Exception as e:
        return {"success": False, "message": f"Index error: {str(e)}"}


async def _get_graphrag_entities(doc_id: str) -> List[dict]:
    """从 GraphRAG 获取文档的实体"""
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            # 查询该文档相关的实体
            response = await client.get(
                f"{config.graphrag.service_url}/api/v1/graph/",
                params={"max_nodes": 100}
            )
            if response.status_code == 200:
                data = response.json()
                nodes = data.get("nodes", [])
                # 过滤与当前文档相关的实体（通过名称匹配）
                return [n for n in nodes if doc_id in str(n.get("attributes", {}))]
    except:
        pass
    return []


async def _get_graphrag_relationships(doc_id: str) -> List[dict]:
    """从 GraphRAG 获取文档的关系"""
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                f"{config.graphrag.service_url}/api/v1/graph/",
                params={"max_edges": 200}
            )
            if response.status_code == 200:
                data = response.json()
                edges = data.get("edges", [])
                return [e for e in edges if doc_id in str(e.get("attributes", {}))]
    except:
        pass
    return []


@router.post("/docs/{doc_id}/index", response_model=WikiIndexResponse)
async def index_document(doc_id: str):
    """手动触发文档索引到 GraphRAG"""
    repo = get_wiki_repo()
    doc = repo.get_document(doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    result = await _index_doc_to_graphrag(doc, doc_id)

    if result.get("success"):
        # 更新文档的 GraphRAG 信息
        repo.update_graphrag_index(
            doc_id=doc_id,
            entities=result.get("entities", []),
            relationships=result.get("relationships", []),
            graphrag_doc_id=result.get("graphrag_doc_id")
        )

        return WikiIndexResponse(
            success=True,
            document_id=doc_id,
            entities_count=result.get("entities_count", 0),
            relationships_count=result.get("relationships_count", 0),
            message="Document indexed successfully"
        )
    else:
        return WikiIndexResponse(
            success=False,
            document_id=doc_id,
            message=result.get("message", "Index failed")
        )


@router.post("/docs/{doc_id}/index/stream")
async def index_document_stream(doc_id: str):
    """流式触发文档索引到 GraphRAG（SSE）"""
    repo = get_wiki_repo()
    doc = repo.get_document(doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    async def event_generator():
        yield f"data: {json.dumps({'stage': 'preparing', 'progress': 0, 'message': 'Preparing document...'})}\n\n"

        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                import tempfile

                # 保存临时文件
                with tempfile.NamedTemporaryFile(
                    mode='w',
                    suffix='.txt',
                    prefix=f'wiki_{doc_id}_',
                    delete=False,
                ) as f:
                    f.write(f"# {doc['title']}\n\n{doc['content']}")
                    temp_path = f.name

                yield f"data: {json.dumps({'stage': 'uploading', 'progress': 20, 'message': 'Uploading to GraphRAG...'})}\n\n"

                with open(temp_path, 'rb') as f:
                    files = {'doc': (f'{doc_id}.txt', f, 'text/plain')}
                    response = await client.post(
                        f"{config.graphrag.service_url}/api/v1/index/stream",
                        files=files
                    )

                Path(temp_path).unlink(missing_ok=True)

                if response.status_code == 200:
                    # 处理 SSE 流
                    async for line in response.aiter_lines():
                        if line.startswith("data: "):
                            yield line + "\n\n"

                    # 完成后更新数据库
                    yield f"data: {json.dumps({'stage': 'saving', 'progress': 95, 'message': 'Saving entity data...'})}\n\n"

                    # 获取实体和关系
                    entities = await _get_graphrag_entities(doc_id)
                    relationships = await _get_graphrag_relationships(doc_id)

                    repo.update_graphrag_index(
                        doc_id=doc_id,
                        entities=entities,
                        relationships=relationships
                    )

                    yield f"data: {json.dumps({'stage': 'complete', 'progress': 100, 'message': 'Indexing complete'})}\n\n"
                else:
                    yield f"data: {json.dumps({'stage': 'error', 'progress': 0, 'message': f'Index failed: {response.status_code}'})}\n\n"

        except Exception as e:
            yield f"data: {json.dumps({'stage': 'error', 'progress': 0, 'message': str(e)})}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )


@router.get("/docs/{doc_id}/entities", response_model=APIResponse)
async def get_document_entities(doc_id: str):
    """获取文档的实体列表"""
    repo = get_wiki_repo()
    doc = repo.get_document(doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    entities = doc.get("entities", [])
    return APIResponse(success=True, data={"entities": entities, "count": len(entities)})


@router.get("/docs/{doc_id}/relationships", response_model=APIResponse)
async def get_document_relationships(doc_id: str):
    """获取文档的关系列表"""
    repo = get_wiki_repo()
    doc = repo.get_document(doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    relationships = doc.get("relationships", [])
    return APIResponse(success=True, data={"relationships": relationships, "count": len(relationships)})


@router.get("/docs/{doc_id}/graph", response_model=APIResponse)
async def get_document_graph(doc_id: str):
    """获取文档的实体关系图"""
    repo = get_wiki_repo()
    doc = repo.get_document(doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    entities = doc.get("entities", [])
    relationships = doc.get("relationships", [])

    # 构建图数据
    nodes = [
        {"id": e.get("entity_id", e.get("id", i)),
         "label": e.get("name", e.get("entity_id", "")),
         "type": e.get("entity_type", "unknown")}
        for i, e in enumerate(entities)
    ]

    edges = [
        {"id": i, "source": r.get("source_id", ""), "target": r.get("target_id", ""),
         "relationship": r.get("relationship", r.get("relation_type", ""))}
        for i, r in enumerate(relationships)
    ]

    return APIResponse(success=True, data={
        "nodes": nodes,
        "edges": edges,
        "stats": {
            "entities": len(nodes),
            "relationships": len(edges)
        }
    })


@router.post("/docs/{doc_id}/reindex", response_model=WikiIndexResponse)
async def reindex_document(doc_id: str):
    """重新索引文档（清除旧索引并重新索引）"""
    repo = get_wiki_repo()
    doc = repo.get_document(doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    # 清除旧索引
    repo.clear_graphrag_index(doc_id)

    # 重新索引
    return await index_document(doc_id)


@router.post("/index-all", response_model=APIResponse)
async def index_all_documents():
    """批量索引所有 Wiki 文档"""
    repo = get_wiki_repo()
    items, _ = repo.list_documents(page=1, size=1000)

    indexed = 0
    failed = 0

    for doc in items:
        try:
            # 调用 GraphRAG 索引 API
            async with httpx.AsyncClient(timeout=30.0) as client:
                import tempfile
                from pathlib import Path

                with tempfile.NamedTemporaryFile(
                    mode='w',
                    suffix='.txt',
                    prefix=f'wiki_{doc["id"]}_',
                    delete=False,
                ) as f:
                    f.write(f"# {doc['title']}\n\n{doc['content']}")
                    temp_path = f.name

                with open(temp_path, 'rb') as f:
                    files = {'doc': (f'{doc["id"]}.txt', f, 'text/plain')}
                    response = await client.post(
                        f"{config.graphrag.service_url}/api/v1/index/",
                        files=files
                    )

                Path(temp_path).unlink(missing_ok=True)

                if response.status_code == 200:
                    indexed += 1
                else:
                    failed += 1

        except Exception:
            failed += 1

    return APIResponse(
        success=True,
        data={"indexed": indexed, "failed": failed},
        message=f"Batch index completed: {indexed} indexed, {failed} failed"
    )


# ========== 长期任务和工作流识别 ==========

@router.get("/workflows", response_model=APIResponse)
async def get_workflows():
    """从 GraphRAG 社区检测中识别工作流"""
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                f"{config.graphrag.service_url}/api/v1/community/"
            )
            if response.status_code == 200:
                communities = response.json()
                # 分析社区，提取可能的工作流
                workflows = []
                for community in communities.get("communities", []):
                    if _is_workflow_community(community):
                        workflows.append({
                            "id": community.get("id"),
                            "title": community.get("title", "Untitled Workflow"),
                            "summary": community.get("summary", ""),
                            "level": community.get("level", 0),
                            "entities": community.get("entity_ids", [])[:10]  # 限制数量
                        })
                return APIResponse(
                    success=True,
                    data={"workflows": workflows, "count": len(workflows)}
                )
    except Exception as e:
        logger.error(f"[Wiki] Get workflows error: {e}")

    return APIResponse(success=True, data={"workflows": [], "count": 0})


def _is_workflow_community(community: dict) -> bool:
    """判断社区是否为工作流相关"""
    # 基于标题/摘要关键词判断
    title = community.get("title", "").lower()
    summary = community.get("summary", "").lower()

    workflow_keywords = ["task", "process", "workflow", "step", "phase", "stage",
                         "任务", "流程", "步骤", "阶段", "工作流"]

    for keyword in workflow_keywords:
        if keyword in title or keyword in summary:
            return True

    # 检查实体类型
    entity_ids = community.get("entity_ids", [])
    if any("task" in str(e).lower() or "step" in str(e).lower() for e in entity_ids):
        return True

    return False


@router.get("/long-term-tasks", response_model=APIResponse)
async def get_long_term_tasks():
    """识别跨多个 Wiki 页面的长期任务"""
    try:
        # 获取所有已索引的文档
        repo = get_wiki_repo()
        items, _ = repo.list_documents(page=1, size=100)

        # 分析每个文档的行动项
        all_tasks = []
        for doc in items:
            tasks = _extract_tasks_from_document(doc)
            for task in tasks:
                task["source_doc"] = {"id": doc["id"], "title": doc["title"]}
                all_tasks.append(task)

        # 识别长期任务（跨多个文档的任务）
        task_signatures = {}
        for task in all_tasks:
            # 简化任务签名用于比较
            sig = _normalize_task_signature(task.get("text", ""))
            if sig not in task_signatures:
                task_signatures[sig] = []
            task_signatures[sig].append(task)

        # 长期任务：在多个文档中出现的相似任务
        long_term_tasks = [
            {
                "signature": sig,
                "occurrences": tasks,
                "count": len(tasks),
                "status": tasks[0].get("status", "unknown")
            }
            for sig, tasks in task_signatures.items()
            if len(tasks) >= 2  # 至少在2个文档中出现
        ]

        return APIResponse(
            success=True,
            data={
                "long_term_tasks": long_term_tasks,
                "count": len(long_term_tasks)
            }
        )

    except Exception as e:
        logger.error(f"[Wiki] Get long-term tasks error: {e}")
        return APIResponse(success=True, data={"long_term_tasks": [], "count": 0})


def _extract_tasks_from_document(doc: dict) -> List[dict]:
    """从文档中提取任务"""
    tasks = []
    content = doc.get("content", "")

    # 简单的任务提取（基于 markdown 任务列表格式）
    import re
    # 匹配 - [ ] task 或 - [x] task
    pattern = r'-\s*\[([ x])\]\s*(.+)'
    matches = re.findall(pattern, content)

    for status, text in matches:
        tasks.append({
            "text": text.strip(),
            "status": "done" if status.lower() == "x" else "pending"
        })

    return tasks


def _normalize_task_signature(task_text: str) -> str:
    """规范化任务签名用于比较"""
    import re
    # 转小写，移除数字和特殊字符
    sig = task_text.lower()
    sig = re.sub(r'[0-9#*]', '', sig)
    sig = re.sub(r'\s+', ' ', sig).strip()
    return sig


@router.post("/workflows/analyze", response_model=APIResponse)
async def analyze_workflow(doc_ids: List[str] = Query(..., description="要分析的文档 ID 列表")):
    """分析指定文档之间的工作流关系"""
    try:
        repo = get_wiki_repo()
        docs = []
        for doc_id in doc_ids:
            doc = repo.get_document(doc_id)
            if doc:
                docs.append(doc)

        if not docs:
            raise HTTPException(status_code=404, detail="No documents found")

        # 构建文档关系图
        nodes = []
        edges = []
        all_entities = set()

        for doc in docs:
            nodes.append({
                "id": doc["id"],
                "title": doc["title"],
                "entities": doc.get("entities", [])
            })
            for entity in doc.get("entities", []):
                all_entities.add(entity.get("name", ""))

        # 基于共享实体建立边
        for i, doc1 in enumerate(docs):
            for j, doc2 in enumerate(docs):
                if i >= j:
                    continue
                entities1 = {e.get("name", "") for e in doc1.get("entities", [])}
                entities2 = {e.get("name", "") for e in doc2.get("entities", [])}
                shared = entities1 & entities2
                if shared:
                    edges.append({
                        "source": doc1["id"],
                        "target": doc2["id"],
                        "shared_entities": list(shared)[:5]  # 限制数量
                    })

        return APIResponse(success=True, data={
            "nodes": nodes,
            "edges": edges,
            "stats": {
                "documents": len(nodes),
                "shared_entities": len(all_entities),
                "relationships": len(edges)
            }
        })

    except Exception as e:
        logger.error(f"[Wiki] Analyze workflow error: {e}")
        return APIResponse(success=False, data={"error": str(e)})
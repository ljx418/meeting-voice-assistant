"""
Wiki Generation API

基于 ADR-002 设计文档实现
Wiki 与 GraphRAG 集成：
- 实体识别、关系提取
- 长期任务（SSE 流式索引）
- 工作流识别
"""

import asyncio
import json
import httpx
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from typing import Optional, List
from pathlib import Path

from app.core.wiki.service import get_wiki_service
from app.models.wiki import WikiFromMeetingRequest, WikiIndexResponse, APIResponse
from app.config import config

router = APIRouter(prefix="/generate", tags=["Wiki Generation"])


@router.post("")
async def generate_from_meeting(request: WikiFromMeetingRequest):
    """从会议生成 Wiki 页面"""
    service = get_wiki_service()

    try:
        result = await service.generate_from_meeting(
            meeting_id=request.meeting_id,
            title=request.title,
            category_id=request.category_id,
            tags=request.tags,
            include_transcript=True,
            include_analysis=True
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Generation failed: {str(e)}")


@router.post("/{page_id}/index")
async def index_page_to_graphrag(page_id: str):
    """将 Wiki 页面索引到 GraphRAG"""
    service = get_wiki_service()
    result = await service.index_to_graphrag(page_id)
    return result


@router.post("/{page_id}/index/stream")
async def index_page_to_graphrag_stream(page_id: str):
    """
    流式将 Wiki 页面索引到 GraphRAG（SSE）

    返回 Server-Sent Events 流，包含进度更新。

    Event stages:
    - preparing (5%): 准备索引文件
    - uploading (15%): 上传文档
    - indexing (20-95%): GraphRAG 索引处理中
    - complete (100%): 索引完成
    - error: 索引失败
    """
    service = get_wiki_service()
    page = service.get_page(page_id)
    if not page:
        raise HTTPException(status_code=404, detail="Page not found")

    async def event_generator():
        import tempfile

        yield f"data: {json.dumps({'stage': 'preparing', 'progress': 5, 'message': '准备索引文件...'})}\n\n"

        try:
            # 创建临时文件
            with tempfile.NamedTemporaryFile(
                mode='w',
                suffix='.txt',
                prefix=f'wiki_{page_id}_',
                delete=False,
            ) as f:
                f.write(f"# {page.title}\n\n{page.content}")
                temp_path = f.name

            yield f"data: {json.dumps({'stage': 'uploading', 'progress': 15, 'message': '上传到 GraphRAG...'})}\n\n"

            # 调用 GraphRAG 流式索引 API
            async with httpx.AsyncClient(timeout=300.0) as client:
                with open(temp_path, 'rb') as f:
                    files = {'doc': (f'{page_id}.txt', f, 'text/plain')}
                    async with client.post(
                        f"{config.graphrag.service_url}/api/v1/index/stream",
                        files=files,
                        timeout=300.0
                    ) as response:
                        if response.status_code != 200:
                            yield f"data: {json.dumps({'stage': 'error', 'progress': 0, 'message': f'GraphRAG 服务错误: {response.status_code}'})}\n\n"
                            return

                        # 转发 SSE 流
                        async for line in response.aiter_lines():
                            if line.startswith("data: "):
                                yield line + "\n\n"

            # 清理临时文件
            Path(temp_path).unlink(missing_ok=True)

            yield f"data: {json.dumps({'stage': 'complete', 'progress': 100, 'message': '索引完成'})}\n\n"

        except Exception as e:
            yield f"data: {json.dumps({'stage': 'error', 'progress': 0, 'message': f'索引失败: {str(e)}'})}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.post("/{page_id}/extract")
async def extract_page_entities_and_relations(page_id: str):
    """
    提取 Wiki 页面的实体、关系、任务和工作流

    这会：
    1. 索引页面到 GraphRAG
    2. 从内容中提取实体
    3. 提取实体关系
    4. 提取长期任务
    5. 识别工作流模式
    """
    service = get_wiki_service()
    result = await service.index_page_and_extract_entities(page_id)
    if not result.get("success", True) and "not found" in result.get("message", "").lower():
        raise HTTPException(status_code=404, detail=result.get("message"))
    return result


@router.get("/{page_id}/graphrag")
async def get_page_graphrag_data(page_id: str):
    """
    获取页面的 GraphRAG 数据

    返回：
    - 实体列表
    - 实体关系
    - 跟踪的任务
    - 工作流模式
    """
    service = get_wiki_service()
    data = service.get_page_graphrag_data(page_id)
    if not data:
        raise HTTPException(status_code=404, detail="Page not found")
    return data


@router.post("/{page_id}/query")
async def query_graphrag_for_page(page_id: str, query: str):
    """
    对页面相关的 GraphRAG 数据执行查询

    - **page_id**: Wiki 页面 ID
    - **query**: 查询文本
    """
    service = get_wiki_service()
    result = await service.query_graphrag_for_page(page_id, query)
    return result


@router.get("/tasks")
async def get_tracked_tasks(
    page_id: str = None,
    status: str = None
):
    """
    获取跟踪的任务

    - **page_id**: 可选，按页面过滤
    - **status**: 可选，按状态过滤 (pending/in_progress/completed)
    """
    service = get_wiki_service()
    tasks = service.db.get_tracked_tasks(page_id=page_id, status=status)
    return {"items": tasks}


@router.put("/tasks/{task_id}/status")
async def update_task_status(task_id: str, status: str):
    """
    更新任务状态

    - **task_id**: 任务 ID
    - **status**: 新状态 (pending/in_progress/completed)
    """
    service = get_wiki_service()
    success = service.db.update_task_status(task_id, status)
    if not success:
        raise HTTPException(status_code=404, detail="Task not found")
    return APIResponse(success=True)


@router.delete("/tasks/{task_id}")
async def delete_tracked_task(task_id: str):
    """删除跟踪的任务"""
    service = get_wiki_service()
    success = service.db.delete_tracked_task(task_id)
    if not success:
        raise HTTPException(status_code=404, detail="Task not found")
    return APIResponse(success=True, message="Task deleted")


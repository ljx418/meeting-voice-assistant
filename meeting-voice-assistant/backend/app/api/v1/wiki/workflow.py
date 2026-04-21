"""
Wiki Workflow API

Wiki 与 GraphRAG 集成 - 工作流识别和长期任务
"""

import re
from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List

from app.core.wiki.service import get_wiki_service
from app.config import config

router = APIRouter(prefix="/workflows", tags=["Wiki Workflow"])


class WorkflowEntity:
    """工作流实体"""
    def __init__(self, type: str, value: str, confidence: float, context: Optional[str] = None):
        self.type = type
        self.value = value
        self.confidence = confidence
        self.context = context


def _identify_workflow_entities(content: str) -> List[WorkflowEntity]:
    """从内容中识别工作流实体"""
    entities = []

    # 决策模式
    decision_patterns = [
        r'([决定|确定|方案|同意|批准|通过|确认])[：:]\s*([^。\n]+)',
        r'(最终[方案|决定])[：:]\s*([^。\n]+)',
    ]
    for pattern in decision_patterns:
        for match in re.finditer(pattern, content):
            entities.append(WorkflowEntity(
                type="decision",
                value=match.group(0)[:100],
                confidence=0.8,
                context=match.group(0)[:50]
            ))

    # 行动项模式
    action_patterns = [
        r'(待[办|处理])[：:]\s*([^。\n]+)',
        r'(需要|应该)[^。\n]+',
        r'(下周)[^。\n]+',
        r'- \[ \]',  # 未完成的行动项
    ]
    for pattern in action_patterns:
        for match in re.finditer(pattern, content):
            entities.append(WorkflowEntity(
                type="action_item",
                value=match.group(0)[:100],
                confidence=0.7,
                context=match.group(0)[:50]
            ))

    # 会议模式
    meeting_patterns = [
        r'([参会|会议|讨论])[：:]\s*([^。\n]+)',
    ]
    for pattern in meeting_patterns:
        for match in re.finditer(pattern, content):
            entities.append(WorkflowEntity(
                type="meeting",
                value=match.group(0)[:100],
                confidence=0.9,
                context=match.group(0)[:50]
            ))

    return entities[:20]


def _identify_workflow_type(content: str) -> Optional[str]:
    """识别工作流类型"""
    content_lower = content.lower()

    if any(k in content_lower for k in ['会议', '参会', '讨论', '议题']):
        return "meeting"
    elif any(k in content_lower for k in ['计划', '规划', '目标', '季度']):
        return "planning"
    elif any(k in content_lower for k in ['评审', '审查', '评估', '通过']):
        return "review"
    elif any(k in content_lower for k in ['决策', '决定', '方案', '选择']):
        return "decision"

    return None


@router.get("")
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
                            "entities": community.get("entity_ids", [])[:10]
                        })
                return {
                    "success": True,
                    "data": {"workflows": workflows, "count": len(workflows)}
                }
    except Exception as e:
        pass

    return {"success": True, "data": {"workflows": [], "count": 0}}


def _is_workflow_community(community: dict) -> bool:
    """判断社区是否为工作流相关"""
    title = community.get("title", "").lower()
    summary = community.get("summary", "").lower()

    workflow_keywords = ["task", "process", "workflow", "step", "phase", "stage",
                         "任务", "流程", "步骤", "阶段", "工作流"]

    for keyword in workflow_keywords:
        if keyword in title or keyword in summary:
            return True

    entity_ids = community.get("entity_ids", [])
    if any("task" in str(e).lower() or "step" in str(e).lower() for e in entity_ids):
        return True

    return False


@router.get("/long-term-tasks")
async def get_long_term_tasks():
    """识别跨多个 Wiki 页面的长期任务"""
    try:
        service = get_wiki_service()
        items, _ = service.list_pages(page=1, page_size=100)

        # 分析每个文档的行动项
        all_tasks = []
        for page in items:
            tasks = _extract_tasks_from_document(page)
            for task in tasks:
                task["source_page"] = {"id": page.id, "title": page.title}
                all_tasks.append(task)

        # 识别长期任务（跨多个文档的任务）
        task_signatures = {}
        for task in all_tasks:
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
            if len(tasks) >= 2
        ]

        return {
            "success": True,
            "data": {
                "long_term_tasks": long_term_tasks,
                "count": len(long_term_tasks)
            }
        }

    except Exception as e:
        return {"success": True, "data": {"long_term_tasks": [], "count": 0}}


def _extract_tasks_from_document(page) -> List[dict]:
    """从文档中提取任务"""
    tasks = []
    content = page.content if hasattr(page, 'content') else ""

    # 简单的任务提取（基于 markdown 任务列表格式）
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
    sig = task_text.lower()
    sig = re.sub(r'[0-9#*]', '', sig)
    sig = re.sub(r'\s+', ' ', sig).strip()
    return sig


@router.post("/analyze")
async def analyze_workflow(page_ids: List[str] = Query(..., description="要分析的页面 ID 列表")):
    """分析指定页面之间的工作流关系"""
    try:
        service = get_wiki_service()
        pages = []
        for page_id in page_ids:
            page = service.get_page(page_id)
            if page:
                pages.append(page)

        if not pages:
            raise HTTPException(status_code=404, detail="No pages found")

        # 构建页面关系图
        nodes = []
        edges = []
        all_entities = set()

        for page in pages:
            entities = _identify_workflow_entities(page.content)
            nodes.append({
                "id": page.id,
                "title": page.title,
                "workflow_type": _identify_workflow_type(page.content),
                "entities": [
                    {"type": e.type, "value": e.value, "confidence": e.confidence}
                    for e in entities
                ]
            })
            for entity in entities:
                all_entities.add(entity.value)

        # 基于共享实体建立边
        for i, page1 in enumerate(pages):
            for j, page2 in enumerate(pages):
                if i >= j:
                    continue
                entities1 = {e.value for e in _identify_workflow_entities(page1.content)}
                entities2 = {e.value for e in _identify_workflow_entities(page2.content)}
                shared = entities1 & entities2
                if shared:
                    edges.append({
                        "source": page1.id,
                        "target": page2.id,
                        "shared_entities": list(shared)[:5]
                    })

        return {
            "success": True,
            "data": {
                "nodes": nodes,
                "edges": edges,
                "stats": {
                    "pages": len(nodes),
                    "unique_entities": len(all_entities),
                    "relationships": len(edges)
                }
            }
        }

    except Exception as e:
        return {"success": False, "data": {"error": str(e)}}


@router.post("/analyze/{page_id}")
async def analyze_single_workflow(page_id: str):
    """分析单个页面的工作流"""
    service = get_wiki_service()
    page = service.get_page(page_id)
    if not page:
        raise HTTPException(status_code=404, detail="Page not found")

    content = page.content
    entities = _identify_workflow_entities(content)
    workflow_type = _identify_workflow_type(content)
    summary = content[:200] + "..." if len(content) > 200 else content

    return {
        "success": True,
        "data": {
            "page_id": page.id,
            "title": page.title,
            "workflow_type": workflow_type,
            "entities": [
                {"type": e.type, "value": e.value, "confidence": e.confidence, "context": e.context}
                for e in entities
            ],
            "summary": summary
        }
    }
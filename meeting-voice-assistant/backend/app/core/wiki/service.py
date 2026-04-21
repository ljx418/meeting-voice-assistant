"""
Wiki 服务层

提供 Wiki 页面 CRUD、生成和搜索功能
"""

import re
import asyncio
import httpx
from typing import Optional, List, Tuple, Any
from pathlib import Path
import logging

from app.storage.wiki_db import get_wiki_db, WikiDatabase
from app.models.wiki import (
    WikiDocument, WikiDocumentCreate, WikiDocumentUpdate,
    WikiDocumentVersion, WikiSearchResult, WikiSearchResponse,
    WikiIndexRequest, WikiIndexResponse, WikiFromMeetingRequest,
    APIResponse, PaginatedResponse
)
from app.config import config

logger = logging.getLogger("wiki.service")


class WikiService:
    """Wiki 服务类"""

    def __init__(self):
        self.db = get_wiki_db()

    # ========== 页面操作 ==========

    def create_page(
        self,
        title: str,
        content: str,
        category_id: Optional[str] = None,
        meeting_id: Optional[str] = None,
        tags: Optional[List[str]] = None,
        is_published: bool = False,
        created_by: str = "system"
    ) -> WikiDocument:
        """创建 Wiki 页面"""
        # 生成 slug
        base_slug = self._generate_slug(title)
        slug = self.db.generate_unique_slug(base_slug)

        # 创建页面
        page_id = self.db.create_page(
            title=title,
            content=content,
            slug=slug,
            category_id=category_id,
            meeting_id=meeting_id,
            created_by=created_by,
            summary=self._generate_summary(content),
            is_published=is_published
        )

        # 设置标签
        if tags:
            tag_ids = []
            for tag_name in tags:
                tag_id = self.db.get_or_create_tag(tag_name)
                tag_ids.append(tag_id)
            self.db.set_page_tags(page_id, tag_ids)

        # 返回完整页面
        return self._build_page_response(page_id)

    def get_page(self, page_id: str) -> Optional[WikiDocument]:
        """获取页面"""
        page = self.db.get_page(page_id)
        if not page:
            return None
        return self._build_page_response(page_id, page)

    def get_page_by_slug(self, slug: str) -> Optional[WikiDocument]:
        """通过 slug 获取页面"""
        page = self.db.get_page_by_slug(slug)
        if not page:
            return None
        return self._build_page_response(page["id"], page)

    def update_page(
        self,
        page_id: str,
        title: Optional[str] = None,
        content: Optional[str] = None,
        category_id: Optional[str] = None,
        tags: Optional[List[str]] = None,
        is_published: Optional[bool] = None,
        change_summary: Optional[str] = None
    ) -> Optional[WikiDocument]:
        """更新页面"""
        # 如果标题变更，需要更新 slug
        if title:
            current = self.db.get_page(page_id)
            if current and current["title"] != title:
                # 标题变更，生成新 slug
                base_slug = self._generate_slug(title)
                slug = self.db.generate_unique_slug(base_slug)
                # 需要直接更新 slug
                import sqlite3
                conn = self.db._get_connection()
                cursor = conn.cursor()
                cursor.execute("UPDATE wiki_pages SET slug = ? WHERE id = ?", (slug, page_id))
                conn.commit()

        # 更新页面
        success = self.db.update_page(
            page_id=page_id,
            title=title,
            content=content,
            category_id=category_id,
            summary=self._generate_summary(content) if content else None,
            is_published=is_published,
            change_summary=change_summary
        )

        if not success:
            return None

        # 更新标签
        if tags is not None:
            tag_ids = []
            for tag_name in tags:
                tag_id = self.db.get_or_create_tag(tag_name)
                tag_ids.append(tag_id)
            self.db.set_page_tags(page_id, tag_ids)

        return self._build_page_response(page_id)

    def delete_page(self, page_id: str) -> bool:
        """删除页面"""
        return self.db.delete_page(page_id)

    def list_pages(
        self,
        page: int = 1,
        page_size: int = 20,
        category_id: Optional[str] = None,
        tag_id: Optional[str] = None,
        search: Optional[str] = None,
        include_unpublished: bool = False
    ) -> Tuple[List[WikiDocument], int]:
        """列出页面（支持分页和过滤）"""
        pages, total = self.db.list_pages(
            page=page,
            page_size=page_size,
            category_id=category_id,
            tag_id=tag_id,
            search=search,
            include_unpublished=include_unpublished
        )

        result = []
        for p in pages:
            doc = self._build_page_response(p["id"], p)
            if doc:
                result.append(doc)

        return result, total

    # ========== 分类操作 ==========

    def create_category(
        self,
        name: str,
        description: Optional[str] = None,
        parent_id: Optional[str] = None,
        sort_order: int = 0
    ) -> dict:
        """创建分类"""
        slug = self._generate_slug(name)
        cat_id = self.db.create_category(
            name=name,
            slug=slug,
            description=description,
            parent_id=parent_id,
            sort_order=sort_order
        )
        return self.db.get_category(cat_id)

    def get_category(self, cat_id: str) -> Optional[dict]:
        """获取分类"""
        return self.db.get_category(cat_id)

    def update_category(
        self,
        cat_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        parent_id: Optional[str] = None,
        sort_order: Optional[int] = None
    ) -> bool:
        """更新分类"""
        return self.db.update_category(
            cat_id=cat_id,
            name=name,
            description=description,
            parent_id=parent_id,
            sort_order=sort_order
        )

    def delete_category(self, cat_id: str) -> bool:
        """删除分类"""
        return self.db.delete_category(cat_id)

    def list_categories(self) -> List[dict]:
        """列出分类"""
        return self.db.list_categories()

    def get_category_tree(self) -> List[dict]:
        """获取分类树"""
        return self.db.get_category_tree()

    # ========== 标签操作 ==========

    def create_tag(self, name: str, color: str = "#6B7280") -> dict:
        """创建标签"""
        slug = self._generate_slug(name)
        tag_id = self.db.create_tag(name=name, slug=slug, color=color)
        return self.db.get_tag(tag_id)

    def get_tag(self, tag_id: str) -> Optional[dict]:
        """获取标签"""
        return self.db.get_tag(tag_id)

    def update_tag(self, tag_id: str, name: Optional[str] = None, color: Optional[str] = None) -> bool:
        """更新标签"""
        return self.db.update_tag(tag_id, name=name, color=color)

    def delete_tag(self, tag_id: str) -> bool:
        """删除标签"""
        return self.db.delete_tag(tag_id)

    def list_tags(self) -> List[dict]:
        """列出标签"""
        return self.db.list_tags()

    # ========== 版本控制 ==========

    def get_page_versions(self, page_id: str) -> List[WikiDocumentVersion]:
        """获取版本历史"""
        versions = self.db.get_page_versions(page_id)
        return [
            WikiDocumentVersion(
                id=v["id"],
                document_id=v["page_id"],
                version=v["version"],
                title=v["title"],
                content=v["content"],
                change_summary=v.get("change_summary"),
                created_at=v["created_at"],
                created_by=v.get("created_by")
            )
            for v in versions
        ]

    def revert_to_version(self, page_id: str, version: int) -> Optional[WikiDocument]:
        """恢复到指定版本"""
        success = self.db.revert_to_version(page_id, version)
        if success:
            return self.get_page(page_id)
        return None

    # ========== 搜索 ==========

    def search(self, query: str, category_id: Optional[str] = None, limit: int = 10) -> List[WikiSearchResult]:
        """全文搜索"""
        results = self.db.search_pages(query, category_id, limit)
        return [
            WikiSearchResult(
                id=r["id"],
                title=r["title"],
                snippet=r.get("snippet", ""),
                doc_type="page",
                tags=[],  # 简化，不返回完整标签
                updated_at=r["updated_at"]
            )
            for r in results
        ]

    async def semantic_search(
        self,
        query: str,
        category_id: Optional[str] = None,
        limit: int = 10
    ) -> dict:
        """GraphRAG 语义搜索"""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{config.graphrag.service_url}/api/v1/query/",
                    json={
                        "query": query,
                        "method": "local",
                        "limit": limit
                    }
                )
                if response.status_code == 200:
                    data = response.json()
                    return {
                        "query": query,
                        "results": data.get("results", []),
                        "graph_context": data.get("graph_context", {})
                    }
        except Exception as e:
            logger.error(f"[WikiService] Semantic search error: {e}")

        return {"query": query, "results": [], "graph_context": {}}

    # ========== Wiki 生成 ==========

    async def generate_from_meeting(
        self,
        meeting_id: str,
        title: str,
        category_id: Optional[str] = None,
        tags: Optional[List[str]] = None,
        include_transcript: bool = True,
        include_analysis: bool = True
    ) -> dict:
        """从会议生成 Wiki 页面"""
        import time
        start_time = time.time()

        # 1. 获取会议数据
        from app.core.session_store import get_session_store_sync
        session_store = get_session_store_sync()
        session = session_store.get_session(meeting_id)

        if not session:
            raise ValueError(f"Meeting not found: {meeting_id}")

        # 2. 获取转写和分析结果
        transcripts = session.get_transcripts()
        analysis_result = session.get_analysis_result() if hasattr(session, 'get_analysis_result') else None

        # 3. 生成 Wiki 内容
        content = await self._generate_wiki_content(
            title=title,
            transcripts=transcripts,
            analysis_result=analysis_result,
            include_transcript=include_transcript,
            include_analysis=include_analysis
        )

        # 4. 创建 Wiki 页面
        page = self.create_page(
            title=title,
            content=content,
            category_id=category_id,
            meeting_id=meeting_id,
            tags=tags,
            is_published=True
        )

        processing_time = int((time.time() - start_time) * 1000)

        return {
            "page": page,
            "generation_stats": {
                "transcript_length": sum(len(t.text) for t in transcripts) if transcripts else 0,
                "generated_length": len(content),
                "processing_time_ms": processing_time
            }
        }

    async def _generate_wiki_content(
        self,
        title: str,
        transcripts: List[Any],
        analysis_result: Optional[Any],
        include_transcript: bool = True,
        include_analysis: bool = True
    ) -> str:
        """使用 LLM 生成 Wiki 内容"""
        # 构建提示词
        prompt = f"""你是一个专业的会议记录助手。请根据以下会议信息生成结构化的 Wiki 页面内容。

## 会议主题: {title}

"""

        if analysis_result:
            if hasattr(analysis_result, 'summary') and analysis_result.summary:
                prompt += f"## 会议摘要\n{analysis_result.summary}\n\n"
            if hasattr(analysis_result, 'key_points') and analysis_result.key_points:
                prompt += "## 关键点\n"
                for point in analysis_result.key_points:
                    prompt += f"- {point}\n"
                prompt += "\n"
            if hasattr(analysis_result, 'action_items') and analysis_result.action_items:
                prompt += "## 行动项\n"
                for item in analysis_result.action_items:
                    prompt += f"- [ ] {item}\n"
                prompt += "\n"
            if hasattr(analysis_result, 'topics') and analysis_result.topics:
                prompt += f"## 主题标签: {', '.join(analysis_result.topics)}\n\n"

        if include_transcript and transcripts:
            prompt += "## 转写记录\n"
            for t in transcripts:
                speaker = getattr(t, 'speaker', 'unknown') or 'unknown'
                text = getattr(t, 'text', '')
                start = getattr(t, 'start_time', 0)
                prompt += f"- [{start:.1f}s] {speaker}: {text}\n"
            prompt += "\n"

        prompt += """请生成符合以下格式的 Wiki 页面:
1. 使用 Markdown 格式
2. 包含摘要、关键点、行动项等标准章节
3. 使用适当的标题层级 (h1, h2, h3)
4. 行动项使用 - [ ] 未完成 / - [x] 已完成 格式
5. 保留关键引述
6. 生成目录链接
"""

        # 调用 LLM 生成
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{config.llm.dashscope_endpoint}",
                    json={
                        "model": config.llm.dashscope_model,
                        "messages": [{"role": "user", "content": prompt}]
                    },
                    headers={"Authorization": f"Bearer {config.llm.dashscope_api_key}"}
                )
                if response.status_code == 200:
                    data = response.json()
                    content = data.get("output", {}).get("text", "") or data.get("choices", [{}])[0].get("message", {}).get("content", "")
                    if content:
                        return content
        except Exception as e:
            logger.error(f"[WikiService] LLM generation error: {e}")

        # 如果 LLM 调用失败，生成简单内容
        return self._generate_simple_content(title, transcripts, analysis_result, include_transcript, include_analysis)

    def _generate_simple_content(
        self,
        title: str,
        transcripts: List[Any],
        analysis_result: Optional[Any],
        include_transcript: bool,
        include_analysis: bool
    ) -> str:
        """生成简单的 Wiki 内容（当 LLM 不可用时）"""
        lines = [f"# {title}\n"]

        if analysis_result:
            if hasattr(analysis_result, 'summary') and analysis_result.summary:
                lines.append("## 摘要\n")
                lines.append(f"{analysis_result.summary}\n")
            if hasattr(analysis_result, 'key_points') and analysis_result.key_points:
                lines.append("## 关键点\n")
                for point in analysis_result.key_points:
                    lines.append(f"- {point}\n")
                lines.append("\n")
            if hasattr(analysis_result, 'action_items') and analysis_result.action_items:
                lines.append("## 行动项\n")
                for item in analysis_result.action_items:
                    lines.append(f"- [ ] {item}\n")
                lines.append("\n")

        if include_transcript and transcripts:
            lines.append("## 转写记录\n")
            for t in transcripts:
                speaker = getattr(t, 'speaker', 'unknown') or 'unknown'
                text = getattr(t, 'text', '')
                start = getattr(t, 'start_time', 0)
                lines.append(f"- [{start:.1f}s] {speaker}: {text}\n")

        return "".join(lines)

    # ========== GraphRAG 索引 ==========

    async def index_to_graphrag(self, page_id: str) -> WikiIndexResponse:
        """将 Wiki 页面索引到 GraphRAG"""
        page = self.db.get_page(page_id)
        if not page:
            return WikiIndexResponse(
                success=False,
                document_id=page_id,
                message="Page not found"
            )

        try:
            # 调用 GraphRAG 索引 API
            async with httpx.AsyncClient(timeout=60.0) as client:
                # 构建索引内容
                content = f"# {page['title']}\n\n{page['content']}"

                import tempfile
                with tempfile.NamedTemporaryFile(
                    mode='w',
                    suffix='.txt',
                    prefix=f'wiki_{page_id}_',
                    delete=False,
                    encoding='utf-8'
                ) as f:
                    f.write(content)
                    temp_path = f.name

                with open(temp_path, 'rb') as f:
                    files = {'doc': (f'{page_id}_wiki.txt', f, 'text/plain')}
                    response = await client.post(
                        f"{config.graphrag.service_url}/api/v1/index/",
                        files=files
                    )

                # 清理临时文件
                Path(temp_path).unlink(missing_ok=True)

                if response.status_code == 200:
                    data = response.json()
                    return WikiIndexResponse(
                        success=True,
                        document_id=page_id,
                        entities_count=data.get("entities_count", 0),
                        relationships_count=data.get("relationships_count", 0),
                        message="Indexed successfully"
                    )
                else:
                    return WikiIndexResponse(
                        success=False,
                        document_id=page_id,
                        message=f"Index failed: {response.status_code}"
                    )

        except Exception as e:
            logger.error(f"[WikiService] GraphRAG index error: {e}")
            return WikiIndexResponse(
                success=False,
                document_id=page_id,
                message=str(e)
            )

    # ========== Wiki-GraphRAG 集成 ==========

    async def index_page_and_extract_entities(self, page_id: str) -> dict:
        """索引 Wiki 页面到 GraphRAG 并提取实体和关系"""
        page = self.db.get_page(page_id)
        if not page:
            return {"success": False, "message": "Page not found"}

        # 1. 先索引到 GraphRAG
        index_result = await self.index_to_graphrag(page_id)
        if not index_result.success:
            return {"success": False, "message": f"GraphRAG index failed: {index_result.message}"}

        # 2. 从 GraphRAG 获取实体数据
        entities = await self._extract_entities_from_graphrag(page["content"], page["title"])

        # 3. 保存实体到 Wiki 数据库
        self.db.delete_page_entities(page_id)
        for ent in entities:
            self.db.save_entity(
                page_id=page_id,
                name=ent["name"],
                entity_type=ent["type"],
                description=ent.get("description"),
                properties=ent.get("properties"),
                confidence=ent.get("confidence", 1.0)
            )

        # 4. 提取关系
        relationships = await self._extract_relationships_from_llm(page["content"], entities)
        self.db.delete_page_relationships(page_id)
        for rel in relationships:
            self.db.save_entity_relationship(
                page_id=page_id,
                source_entity_id=rel["source"],
                target_entity_id=rel["target"],
                relationship_type=rel["type"],
                description=rel.get("description")
            )

        # 5. 提取跟踪任务
        tasks = await self._extract_tracked_tasks(page["content"])
        for task in tasks:
            self.db.save_tracked_task(
                page_id=page_id,
                title=task["title"],
                description=task.get("description"),
                assignee=task.get("assignee"),
                due_date=task.get("due_date"),
                priority=task.get("priority", "medium"),
                source_text=task.get("source_text")
            )

        # 6. 提取工作流模式
        workflows = await self._extract_workflow_patterns(page["content"])
        for wf in workflows:
            self.db.save_workflow_pattern(
                page_id=page_id,
                workflow_type=wf["type"],
                name=wf["name"],
                steps=wf["steps"],
                description=wf.get("description"),
                entities=wf.get("entities")
            )

        return {
            "success": True,
            "entities_count": len(entities),
            "relationships_count": len(relationships),
            "tasks_count": len(tasks),
            "workflows_count": len(workflows)
        }

    async def _extract_entities_from_graphrag(self, content: str, title: str) -> List[dict]:
        """从 GraphRAG 获取实体（通过查询接口）"""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                # 使用 GraphRAG 查询接口获取相关实体
                response = await client.post(
                    f"{config.graphrag.service_url}/api/v1/query/",
                    json={
                        "query": f"从以下内容中提取所有实体：{title}。{content[:2000]}",
                        "method": "local",
                        "limit": 20
                    }
                )
                if response.status_code == 200:
                    data = response.json()
                    entities = []
                    for item in data.get("results", []):
                        if "entity" in item:
                            ent = item["entity"]
                            entities.append({
                                "name": ent.get("name", ""),
                                "type": ent.get("type", "unknown"),
                                "description": ent.get("description"),
                                "properties": {},
                                "confidence": 0.9
                            })
                    return entities
        except Exception as e:
            logger.error(f"[WikiService] Extract entities error: {e}")

        # LLM 直接提取作为后备
        return await self._extract_entities_from_llm(content, title)

    async def _extract_entities_from_llm(self, content: str, title: str) -> List[dict]:
        """使用 LLM 从内容中提取实体"""
        prompt = f"""从以下文本中提取所有实体（人物、组织、项目、任务等）。

标题: {title}

内容:
{content[:3000]}

请以 JSON 格式返回实体列表，格式如下：
[
  {{"name": "实体名称", "type": "实体类型", "description": "描述"}}
]

只返回 JSON，不要其他文字。"""

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{config.llm.dashscope_endpoint}",
                    json={
                        "model": config.llm.dashscope_model,
                        "messages": [{"role": "user", "content": prompt}]
                    },
                    headers={"Authorization": f"Bearer {config.llm.dashscope_api_key}"}
                )
                if response.status_code == 200:
                    data = response.json()
                    text = data.get("output", {}).get("text", "") or data.get("choices", [{}])[0].get("message", {}).get("content", "")
                    # 解析 JSON
                    import json
                    entities = json.loads(text)
                    return entities if isinstance(entities, list) else []
        except Exception as e:
            logger.error(f"[WikiService] LLM entity extraction error: {e}")
        return []

    async def _extract_relationships_from_llm(self, content: str, entities: List[dict]) -> List[dict]:
        """使用 LLM 从内容中提取实体关系"""
        if not entities:
            return []

        entity_names = [e["name"] for e in entities[:10]]
        prompt = f"""从以下内容中提取实体之间的关系。

内容:
{content[:2000]}

已知实体: {', '.join(entity_names)}

请以 JSON 格式返回关系列表：
[
  {{"source": "实体A", "target": "实体B", "type": "关系类型", "description": "关系描述"}}
]

只返回 JSON。"""

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{config.llm.dashscope_endpoint}",
                    json={
                        "model": config.llm.dashscope_model,
                        "messages": [{"role": "user", "content": prompt}]
                    },
                    headers={"Authorization": f"Bearer {config.llm.dashscope_api_key}"}
                )
                if response.status_code == 200:
                    data = response.json()
                    text = data.get("output", {}).get("text", "") or data.get("choices", [{}])[0].get("message", {}).get("content", "")
                    import json
                    relationships = json.loads(text)
                    return relationships if isinstance(relationships, list) else []
        except Exception as e:
            logger.error(f"[WikiService] LLM relationship extraction error: {e}")
        return []

    async def _extract_tracked_tasks(self, content: str) -> List[dict]:
        """从内容中提取长期跟踪任务"""
        prompt = f"""从以下文本中提取所有可跟踪的任务/行动项。

内容:
{content[:3000]}

请以 JSON 格式返回任务列表：
[
  {{
    "title": "任务标题",
    "description": "任务描述",
    "assignee": "负责人（如果有）",
    "due_date": "截止日期（如果有）",
    "priority": "high/medium/low",
    "source_text": "原文"
  }}
]

只返回 JSON。"""

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{config.llm.dashscope_endpoint}",
                    json={
                        "model": config.llm.dashscope_model,
                        "messages": [{"role": "user", "content": prompt}]
                    },
                    headers={"Authorization": f"Bearer {config.llm.dashscope_api_key}"}
                )
                if response.status_code == 200:
                    data = response.json()
                    text = data.get("output", {}).get("text", "") or data.get("choices", [{}])[0].get("message", {}).get("content", "")
                    import json
                    tasks = json.loads(text)
                    return tasks if isinstance(tasks, list) else []
        except Exception as e:
            logger.error(f"[WikiService] LLM task extraction error: {e}")
        return []

    async def _extract_workflow_patterns(self, content: str) -> List[dict]:
        """从内容中提取工作流模式"""
        prompt = f"""从以下文本中识别和提取工作流程/步骤序列。

内容:
{content[:3000]}

常见工作流类型：
- 会议流程 (meeting_flow)
- 开发流程 (development_flow)
- 审批流程 (approval_flow)
- 决策流程 (decision_flow)
- 问题解决流程 (problem_solving_flow)

请以 JSON 格式返回工作流列表：
[
  {{
    "type": "工作流类型",
    "name": "工作流名称",
    "description": "描述",
    "steps": [
      {{"step": 1, "name": "步骤名称", "description": "步骤描述"}}
    ],
    "entities": ["涉及的实体"]
  }}
]

只返回 JSON。"""

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{config.llm.dashscope_endpoint}",
                    json={
                        "model": config.llm.dashscope_model,
                        "messages": [{"role": "user", "content": prompt}]
                    },
                    headers={"Authorization": f"Bearer {config.llm.dashscope_api_key}"}
                )
                if response.status_code == 200:
                    data = response.json()
                    text = data.get("output", {}).get("text", "") or data.get("choices", [{}])[0].get("message", {}).get("content", "")
                    import json
                    workflows = json.loads(text)
                    return workflows if isinstance(workflows, list) else []
        except Exception as e:
            logger.error(f"[WikiService] LLM workflow extraction error: {e}")
        return []

    def get_page_graphrag_data(self, page_id: str) -> dict:
        """获取页面的 GraphRAG 数据"""
        page = self.db.get_page(page_id)
        if not page:
            return None

        entities = self.db.get_page_entities(page_id)
        relationships = self.db.get_page_relationships(page_id)
        tasks = self.db.get_tracked_tasks(page_id=page_id)
        workflows = self.db.get_page_workflows(page_id)

        return {
            "page_id": page_id,
            "title": page["title"],
            "entities": entities,
            "relationships": relationships,
            "tasks": tasks,
            "workflows": workflows
        }

    async def query_graphrag_for_page(self, page_id: str, query: str) -> dict:
        """查询 GraphRAG 并返回与页面相关的结果"""
        page = self.db.get_page(page_id)
        if not page:
            return {"results": [], "message": "Page not found"}

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{config.graphrag.service_url}/api/v1/query/",
                    json={
                        "query": query,
                        "method": "local",
                        "limit": 10
                    }
                )
                if response.status_code == 200:
                    data = response.json()
                    return {
                        "results": data.get("results", []),
                        "graph_context": data.get("graph_context", {})
                    }
        except Exception as e:
            logger.error(f"[WikiService] GraphRAG query error: {e}")
        return {"results": [], "graph_context": {}}

    # ========== 辅助方法 ==========

    def _generate_slug(self, text: str) -> str:
        """生成 URL 友好的 slug"""
        slug = text.lower()
        slug = re.sub(r'\s+', '-', slug)
        slug = re.sub(r'[^a-z0-9\-]', '', slug)
        slug = re.sub(r'-+', '-', slug)
        slug = slug.strip('-')
        return slug

    def _generate_summary(self, content: str, max_length: int = 200) -> str:
        """生成摘要"""
        if not content:
            return ""

        # 取前 max_length 个字符
        summary = content[:max_length]
        if len(content) > max_length:
            summary += "..."
        return summary

    def _build_page_response(self, page_id: str, page_data: Optional[dict] = None) -> Optional[WikiDocument]:
        """构建页面响应"""
        if page_data is None:
            page_data = self.db.get_page(page_id)
        if not page_data:
            return None

        tags = self.db.get_page_tags(page_id)

        return WikiDocument(
            id=page_data["id"],
            title=page_data["title"],
            content=page_data["content"],
            doc_type="page",
            parent_id=page_data.get("parent_id"),
            meeting_id=page_data.get("meeting_id"),
            tags=[t["name"] for t in tags],
            version=page_data["version"],
            is_deleted=bool(page_data.get("is_deleted", 0)),
            created_at=page_data["created_at"],
            updated_at=page_data["updated_at"],
            created_by=page_data.get("created_by")
        )


# 全局实例
_wiki_service: Optional[WikiService] = None


def get_wiki_service() -> WikiService:
    """获取 Wiki 服务实例"""
    global _wiki_service
    if _wiki_service is None:
        _wiki_service = WikiService()
    return _wiki_service
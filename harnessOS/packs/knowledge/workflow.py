"""Knowledge domain workflow implementation."""

from __future__ import annotations

from typing import Any

from tools.knowledge import kb_ingest, kb_search


class KnowledgeWorkflow:
    """Minimal knowledge workflow backed by existing kb tools."""

    workflow_id = "knowledge.workflow"
    domain = "knowledge"
    priority = 50

    def should_handle(self, user_input: str, context: Any) -> bool:
        if context.domain == "knowledge":
            return True
        if context.domain and context.domain != "knowledge":
            return False
        lowered = user_input.lower()
        return any(keyword in lowered for keyword in ("knowledge", "知识", "知识库", "检索", "搜索", "查询", "wiki"))

    async def run(self, user_input: str, context: Any) -> dict[str, Any]:
        if _looks_like_ingest(user_input):
            document = _extract_document(user_input)
            result = kb_ingest(document, title="Knowledge Workflow Note")
            content = f"知识库内容已登记。\n{result}"
            return {
                "status": "success",
                "content": content,
                "knowledge": {"operation": "ingest", "result": result, "sources": []},
            }

        result = kb_search(user_input, top_k=5)
        content = f"知识检索已完成。\n{result}"
        return {
            "status": "success",
            "content": content,
            "knowledge": {
                "operation": "search",
                "query": user_input,
                "result": result,
                "sources": _extract_source_lines(result),
            },
        }


def _looks_like_ingest(user_input: str) -> bool:
    lowered = user_input.lower()
    return any(keyword in lowered for keyword in ("ingest", "录入", "写入知识库", "加入知识库", "保存到知识库"))


def _extract_document(user_input: str) -> str:
    for marker in ("：", ":", "\n"):
        if marker in user_input:
            candidate = user_input.split(marker, 1)[1].strip()
            if candidate:
                return candidate
    return user_input.strip()


def _extract_source_lines(result: str) -> list[str]:
    return [line.strip() for line in result.splitlines() if line.strip().startswith("ID:")]

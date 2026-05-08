"""Knowledge domain workflow implementation."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Optional

from apps.gateway.connector_execution import ConnectorExecutionRuntime
from apps.gateway.knowledge_mcp_workflow import DATA_SERVICE_CONNECTOR_ID
from tools.knowledge import kb_ingest, kb_search


class KnowledgeWorkflow:
    """Knowledge workflow that prefers the connector-backed standard entry."""

    workflow_id = "knowledge.workflow"
    domain = "knowledge"
    priority = 50

    def __init__(
        self,
        connector_execution_runtime: Optional[ConnectorExecutionRuntime] = None,
    ) -> None:
        self.connector_execution_runtime = connector_execution_runtime

    def should_handle(self, user_input: str, context: Any) -> bool:
        if context.domain == "knowledge":
            return True
        if context.domain and context.domain != "knowledge":
            return False
        lowered = user_input.lower()
        return any(keyword in lowered for keyword in ("knowledge", "知识", "知识库", "检索", "搜索", "查询", "wiki"))

    async def run(self, user_input: str, context: Any) -> dict[str, Any]:
        if self.connector_execution_runtime is not None:
            return self._run_via_connector(user_input, context)
        return self._run_legacy(user_input)

    def _run_via_connector(self, user_input: str, context: Any) -> dict[str, Any]:
        ingest_mode = _looks_like_ingest(user_input)
        if ingest_mode:
            tool = "knowledge_ingest_v2"
            payload = {
                "title": "Knowledge Workflow Note",
                "content": _extract_document(user_input),
            }
        else:
            tool = "knowledge_query_v2"
            payload = {"query": user_input, "mode": "hybrid", "top_k": 5}

        submitted = self.connector_execution_runtime.submit(
            connector_id=DATA_SERVICE_CONNECTOR_ID,
            tool=tool,
            payload=payload,
            session_id=context.session_id,
            turn_id=context.turn_id,
            scope=context.scope,
            approval_id=getattr(context, "approval_id", None),
        )
        if submitted.get("approval_required"):
            approval = submitted.get("approval") or {}
            approval_id = approval.get("approval_id")
            return {
                "status": "success",
                "content": f"操作需要审批。Approval ID: {approval_id}",
                "approval_required": True,
                "approval": approval,
                "retry_context": submitted.get("retry_context"),
                "knowledge": {
                    "operation": "ingest" if ingest_mode else "search",
                    "tool": tool,
                    "input": payload,
                    "connector_id": DATA_SERVICE_CONNECTOR_ID,
                    "job": submitted.get("job"),
                },
            }
        artifact = submitted.get("artifact") or {}
        envelope = _read_connector_result_envelope(artifact.get("path"))
        lines = [
            "知识库内容已登记。" if ingest_mode else "知识检索已完成。",
            f"标准入口：connector {DATA_SERVICE_CONNECTOR_ID}.{tool}",
        ]
        summary = _summarize_envelope(envelope)
        if summary:
            lines.append(summary)
        if artifact.get("artifact_id"):
            lines.append(f"Artifact：{artifact.get('artifact_id')}")

        sources = _extract_sources_from_envelope(envelope)
        return {
            "status": "success",
            "content": "\n".join(lines),
            "knowledge": {
                "operation": "ingest" if ingest_mode else "search",
                "tool": tool,
                "input": payload,
                "connector_id": DATA_SERVICE_CONNECTOR_ID,
                "job": submitted.get("job"),
                "artifact": artifact,
                "result": envelope,
                "sources": sources,
            },
        }

    def _run_legacy(self, user_input: str) -> dict[str, Any]:
        if _looks_like_ingest(user_input):
            document = _extract_document(user_input)
            result = kb_ingest(document, title="Knowledge Workflow Note")
            content = f"知识库内容已登记。\n{result}"
            return {
                "status": "success",
                "content": content,
                "knowledge": {
                    "operation": "ingest",
                    "result": result,
                    "sources": [],
                    "execution_mode": "legacy_fallback",
                },
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
                "execution_mode": "legacy_fallback",
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


def _read_connector_result_envelope(path: Optional[str]) -> dict[str, Any]:
    if not isinstance(path, str) or not path:
        return {}
    artifact_path = Path(path).expanduser()
    if not artifact_path.exists():
        return {}
    payload = json.loads(artifact_path.read_text(encoding="utf-8"))
    result = payload.get("result")
    if isinstance(result, dict):
        return result
    return {}


def _summarize_envelope(envelope: dict[str, Any]) -> str:
    content = envelope.get("content")
    if isinstance(content, str) and content.strip():
        return content.strip()
    if isinstance(content, list):
        snippets: list[str] = []
        for item in content:
            if not isinstance(item, dict):
                continue
            if isinstance(item.get("text"), str) and item["text"].strip():
                snippets.append(item["text"].strip())
            data = item.get("data")
            if isinstance(data, dict):
                if isinstance(data.get("answer"), str) and data["answer"].strip():
                    snippets.append(data["answer"].strip())
                elif isinstance(data.get("summary"), str) and data["summary"].strip():
                    snippets.append(data["summary"].strip())
        if snippets:
            return "\n".join(snippets[:3])
    if isinstance(envelope.get("message"), str) and envelope["message"].strip():
        return envelope["message"].strip()
    data = envelope.get("data")
    if isinstance(data, dict):
        if isinstance(data.get("answer"), str) and data["answer"].strip():
            return data["answer"].strip()
        if isinstance(data.get("summary"), str) and data["summary"].strip():
            return data["summary"].strip()
    return ""


def _extract_sources_from_envelope(envelope: dict[str, Any]) -> list[str]:
    data = envelope.get("data")
    if not isinstance(data, dict):
        return []
    citations = data.get("citations")
    if not isinstance(citations, list):
        return []
    sources: list[str] = []
    for citation in citations:
        if not isinstance(citation, dict):
            continue
        title = citation.get("title") or citation.get("source") or citation.get("id")
        if isinstance(title, str) and title.strip():
            sources.append(title.strip())
    return sources

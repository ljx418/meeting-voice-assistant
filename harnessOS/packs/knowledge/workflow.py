"""Knowledge domain workflow implementation."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Optional

from apps.gateway.artifacts import ArtifactError, ArtifactRegistry
from apps.gateway.connector_execution import ConnectorExecutionRuntime
from apps.gateway.knowledge_mcp_workflow import DATA_SERVICE_CONNECTOR_ID
from core.apps import ScopeContext
from core.config import get_data_service_mcp_config
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
            source_path = _extract_existing_source_path(user_input)
            if source_path is not None:
                _validate_source_path(source_path)
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
        registered = register_knowledge_artifacts(
            {
                "operation": "ingest" if ingest_mode else "search",
                "tool": tool,
                "input": payload,
                "result": envelope,
                "sources": sources,
                "connector_artifact_id": artifact.get("artifact_id"),
            },
            artifact_registry=context.artifact_registry,
            session_id=context.session_id,
            turn_id=context.turn_id,
            scope=context.scope,
        )
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
                "artifacts": registered,
                "artifact_records": {kind: item["record"] for kind, item in registered.items()},
                "result": envelope,
                "sources": sources,
            },
            "artifact_records": {kind: item["record"] for kind, item in registered.items()},
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


def register_knowledge_artifacts(
    result: dict[str, Any],
    *,
    artifact_registry: Optional[ArtifactRegistry],
    session_id: Optional[str],
    turn_id: Optional[str],
    scope: ScopeContext,
) -> dict[str, Any]:
    """Register normalized Knowledge Pack artifacts."""
    if artifact_registry is None:
        return {}
    output_dir = artifact_registry.root / "knowledge" / str(session_id or "session") / str(turn_id or "turn")
    output_dir.mkdir(parents=True, exist_ok=True)
    payloads = _knowledge_artifact_payloads(result)
    registered: dict[str, Any] = {}
    parent_by_kind = {
        "note": "source_reference",
        "brief": "source_reference",
        "citation_bundle": "brief",
    }
    for kind in ("source_reference", "note", "brief", "citation_bundle"):
        path = output_dir / f"{kind}.json"
        path.write_text(json.dumps(payloads[kind], ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        parent_kind = parent_by_kind.get(kind)
        metadata = {
            "lineage_step": kind,
            "connector_id": DATA_SERVICE_CONNECTOR_ID,
            "connector_tool": result.get("tool"),
            "connector_artifact_id": result.get("connector_artifact_id"),
            "execution_mode": "data_service_mcp",
        }
        if parent_kind in registered:
            parent_artifact_id = registered[parent_kind]["artifact_id"]
            metadata["source_artifact_id"] = parent_artifact_id
            metadata["parent_artifact_ids"] = [parent_artifact_id]
        try:
            record = artifact_registry.register_file(
                str(path),
                session_id=session_id,
                turn_id=turn_id,
                app_id=scope.app_id,
                project_id=scope.project_id,
                workspace_id=scope.workspace_id,
                domain="knowledge",
                kind=kind,
                metadata=metadata,
            )
        except ArtifactError:
            continue
        registered[kind] = {"path": str(path), "artifact_id": record["artifact_id"], "record": record}
    return registered


def _knowledge_artifact_payloads(result: dict[str, Any]) -> dict[str, dict[str, Any]]:
    envelope = result.get("result") if isinstance(result.get("result"), dict) else {}
    data = envelope.get("data") if isinstance(envelope.get("data"), dict) else {}
    sources = result.get("sources") if isinstance(result.get("sources"), list) else []
    input_payload = result.get("input") if isinstance(result.get("input"), dict) else {}
    answer = _summarize_envelope(envelope)
    return {
        "source_reference": {
            "operation": result.get("operation"),
            "sources": sources,
            "input": input_payload,
            "workspace_id": envelope.get("workspace_id"),
            "connector_artifact_id": result.get("connector_artifact_id"),
        },
        "note": {
            "title": input_payload.get("title") or "Knowledge Workflow Note",
            "content": input_payload.get("content") or answer,
            "operation": result.get("operation"),
        },
        "brief": {
            "query": input_payload.get("query"),
            "answer": answer,
            "summary": data.get("summary"),
            "operation": result.get("operation"),
        },
        "citation_bundle": {
            "citations": data.get("citations") or [],
            "sources": sources,
            "workspace_id": envelope.get("workspace_id"),
        },
    }


def _extract_existing_source_path(user_input: str) -> Optional[Path]:
    for raw in user_input.replace("\n", " ").split(" "):
        candidate = raw.strip().strip("\"'")
        if not candidate or "/" not in candidate:
            continue
        path = Path(candidate).expanduser()
        if path.exists():
            return path
    return None


def _validate_source_path(path: Path) -> None:
    if path.is_symlink():
        raise ValueError(f"Knowledge source path must not be a symlink: {path}")
    resolved = path.resolve()
    roots = _knowledge_allowed_source_roots()
    if roots and not any(resolved == root or root in resolved.parents for root in roots):
        raise ValueError(f"Knowledge source path is outside allowed roots: {resolved}")
    max_bytes = int(os.getenv("HARNESS_KNOWLEDGE_SOURCE_MAX_BYTES", str(10 * 1024 * 1024)))
    if resolved.stat().st_size > max_bytes:
        raise ValueError(f"Knowledge source file exceeds size limit: {resolved}")


def _knowledge_allowed_source_roots() -> list[Path]:
    config = get_data_service_mcp_config()
    raw_roots = config.allowed_source_roots or os.getenv("DATA_SERVICE_ALLOWED_SOURCE_ROOTS") or ""
    return [
        Path(item).expanduser().resolve()
        for item in raw_roots.split(":")
        if item.strip()
    ]


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

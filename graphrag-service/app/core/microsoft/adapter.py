"""Microsoft GraphRAG adapter - bridges API parameters to Microsoft GraphRAG."""

from __future__ import annotations

import asyncio
import json
import shutil
import subprocess
from pathlib import Path
from typing import Any

from app.config import settings
from app.core.base import (
    CommunityInfo,
    EntityInfo,
    GraphData,
    GraphEdge,
    GraphNode,
    GraphRAGCore,
    IndexResult,
    QueryResult,
    SourceChunk,
    SummaryResult,
    BatchIndexResult,
)


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
        self._init_workspace()

    def _init_workspace(self) -> None:
        """初始化 GraphRAG workspace"""
        self.workspace.mkdir(parents=True, exist_ok=True)
        settings_yaml = self.workspace / "settings.yaml"
        if not settings_yaml.exists():
            settings_yaml.write_text(self._default_settings())

    def _default_settings(self) -> str:
        """生成 GraphRAG settings.yaml"""
        return f"""encoding_model: cl100k_base
skip_workflow: false
llm:
  description: DashScope LLM
  configuration:
    type: openai_chat
    api_key: {self.llm_config['api_key']}
    model: {self.llm_config['model']}
    api_base: {self.llm_config['base_url']}
"""

    def _get_namespace_dir(self, namespace: str) -> Path:
        """获取 namespace 对应的输入目录"""
        namespace_dir = self.workspace / "input" / namespace
        namespace_dir.mkdir(parents=True, exist_ok=True)
        return namespace_dir

    def _run_graphrag_command(self, *args: str) -> asyncio.subprocess.Process:
        """运行 graphrag CLI 命令"""
        cmd = ["graphrag"] + list(args)
        return asyncio.create_subprocess_exec(
            *cmd,
            cwd=str(self.workspace),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

    async def _execute_command(self, *args: str) -> tuple[int, str, str]:
        """执行 graphrag 命令并返回结果"""
        process = await self._run_graphrag_command(*args)
        stdout, stderr = await process.communicate()
        return (
            process.returncode,
            stdout.decode("utf-8") if stdout else "",
            stderr.decode("utf-8") if stderr else "",
        )

    async def index_document(self, doc_path: Path, namespace: str) -> IndexResult:
        """索引单个文档"""
        try:
            # 将文件复制到 namespace 目录
            namespace_dir = self._get_namespace_dir(namespace)
            dest_path = namespace_dir / doc_path.name
            shutil.copy2(doc_path, dest_path)

            # 运行 graphrag index
            returncode, stdout, stderr = await self._execute_command(
                "index",
                "--root",
                str(self.workspace),
            )

            if returncode != 0:
                return IndexResult(
                    document_id=doc_path.name,
                    namespace=namespace,
                    status="failed",
                    error=stderr or stdout,
                )

            # 解析输出获取统计信息
            entity_count = 0
            relationship_count = 0
            community_count = 0

            # 尝试从输出中解析计数
            try:
                if stdout:
                    output_json = json.loads(stdout)
                    entity_count = output_json.get("entity_count", 0)
                    relationship_count = output_json.get("relationship_count", 0)
                    community_count = output_json.get("community_count", 0)
            except json.JSONDecodeError:
                pass

            return IndexResult(
                document_id=doc_path.name,
                namespace=namespace,
                status="completed",
                entity_count=entity_count,
                relationship_count=relationship_count,
                community_count=community_count,
            )
        except Exception as e:
            return IndexResult(
                document_id=doc_path.name,
                namespace=namespace,
                status="failed",
                error=str(e),
            )

    async def index_documents_batch(
        self, doc_paths: list[Path], namespace: str
    ) -> BatchIndexResult:
        """批量索引文档"""
        results: list[IndexResult] = []
        succeeded = 0
        failed = 0

        for doc_path in doc_paths:
            result = await self.index_document(doc_path, namespace)
            results.append(result)
            if result.status == "completed":
                succeeded += 1
            else:
                failed += 1

        return BatchIndexResult(
            total=len(doc_paths),
            succeeded=succeeded,
            failed=failed,
            results=results,
        )

    async def query(
        self,
        query_text: str,
        namespace: str,
        top_k: int = 10,
        context: str | None = None,
    ) -> QueryResult:
        """查询知识图谱"""
        try:
            # 如果提供了 context，拼接在 query 前面
            full_query = query_text
            if context:
                full_query = f"{context}\n\n{query_text}"

            # 运行 graphrag query
            returncode, stdout, stderr = await self._execute_command(
                "query",
                "--root",
                str(self.workspace),
                "--query",
                full_query,
                "--method",
                "local",
            )

            if returncode != 0:
                return QueryResult(
                    query_text=query_text,
                    answer=f"Query failed: {stderr or stdout}",
                    confidence=0.0,
                )

            # 解析输出
            try:
                output = json.loads(stdout) if stdout else {}
                answer = output.get("answer", stdout if stdout else "No result")
                source_chunks = []
                entities = []
                communities = []

                # 尝试解析 source_chunks
                for chunk_data in output.get("source_chunks", []):
                    source_chunks.append(
                        SourceChunk(
                            chunk_id=chunk_data.get("chunk_id", ""),
                            text=chunk_data.get("text", ""),
                            document_id=chunk_data.get("document_id", ""),
                        )
                    )

                # 尝试解析 entities
                for entity_data in output.get("entities", []):
                    entities.append(
                        EntityInfo(
                            entity_id=entity_data.get("id", ""),
                            name=entity_data.get("name", ""),
                            entity_type=entity_data.get("type", ""),
                            description=entity_data.get("description"),
                        )
                    )

                confidence = output.get("confidence", 0.5)

                return QueryResult(
                    query_text=query_text,
                    answer=answer,
                    source_chunks=source_chunks,
                    entities=entities,
                    communities=communities,
                    confidence=confidence,
                )
            except json.JSONDecodeError:
                return QueryResult(
                    query_text=query_text,
                    answer=stdout if stdout else "No result",
                    confidence=0.0,
                )
        except Exception as e:
            return QueryResult(
                query_text=query_text,
                answer=f"Query error: {str(e)}",
                confidence=0.0,
            )

    async def summarize(
        self, namespace: str, query: str | None = None
    ) -> SummaryResult:
        """生成知识图谱摘要"""
        try:
            # 默认的摘要查询
            if not query:
                query = "Provide a comprehensive summary of all entities and relationships in this knowledge graph."

            # 运行 graphrag query --method global
            returncode, stdout, stderr = await self._execute_command(
                "query",
                "--root",
                str(self.workspace),
                "--query",
                query,
                "--method",
                "global",
            )

            if returncode != 0:
                return SummaryResult(
                    summary=f"Summarize failed: {stderr or stdout}",
                    total_entities=0,
                    total_communities=0,
                )

            try:
                output = json.loads(stdout) if stdout else {}
                summary = output.get("summary", stdout if stdout else "No summary")
                community_summaries = []
                total_entities = output.get("total_entities", 0)
                total_communities = output.get("total_communities", 0)

                for comm_data in output.get("community_summaries", []):
                    community_summaries.append(
                        CommunityInfo(
                            community_id=comm_data.get("id", ""),
                            level=comm_data.get("level", 0),
                            title=comm_data.get("title"),
                            summary=comm_data.get("summary"),
                            entity_ids=comm_data.get("entity_ids", []),
                        )
                    )

                return SummaryResult(
                    summary=summary,
                    community_summaries=community_summaries,
                    total_entities=total_entities,
                    total_communities=total_communities,
                )
            except json.JSONDecodeError:
                return SummaryResult(
                    summary=stdout if stdout else "No summary",
                    total_entities=0,
                    total_communities=0,
                )
        except Exception as e:
            return SummaryResult(
                summary=f"Summarize error: {str(e)}",
                total_entities=0,
                total_communities=0,
            )

    async def get_graph_data(
        self, namespace: str, max_nodes: int = 100
    ) -> GraphData:
        """获取图谱数据用于可视化"""
        # 这里应该调用 storage.database.get_graph_data
        # 但目前 storage 还是 placeholder，先返回空数据
        try:
            # 尝试从 workspace 的 output 目录读取图数据
            output_dir = self.workspace / "output"
            if not output_dir.exists():
                return GraphData(nodes=[], edges=[])

            # 查找最新的输出文件
            output_files = list(output_dir.glob("*.json"))
            if not output_files:
                return GraphData(nodes=[], edges=[])

            latest_output = max(output_files, key=lambda p: p.stat().st_mtime)

            with open(latest_output, "r", encoding="utf-8") as f:
                data = json.load(f)

            nodes: list[GraphNode] = []
            edges: list[GraphEdge] = []

            # 解析 nodes
            for node_data in data.get("nodes", [])[:max_nodes]:
                nodes.append(
                    GraphNode(
                        node_id=node_data.get("id", ""),
                        label=node_data.get("label", ""),
                        node_type=node_data.get("type", ""),
                        attributes=node_data.get("attributes", {}),
                    )
                )

            # 解析 edges
            for edge_data in data.get("edges", []):
                edges.append(
                    GraphEdge(
                        edge_id=edge_data.get("id", ""),
                        source_id=edge_data.get("source", ""),
                        target_id=edge_data.get("target", ""),
                        relationship=edge_data.get("relationship", ""),
                        weight=edge_data.get("weight", 1.0),
                        attributes=edge_data.get("attributes", {}),
                    )
                )

            return GraphData(nodes=nodes, edges=edges)
        except Exception:
            return GraphData(nodes=[], edges=[])

    async def delete_document(self, doc_id: str, namespace: str) -> None:
        """删除文档及其关联数据"""
        try:
            # 删除输入目录中的文件
            namespace_dir = self._get_namespace_dir(namespace)
            doc_path = namespace_dir / doc_id
            if doc_path.exists():
                doc_path.unlink()

            # 调用 storage.database.delete_document
            # 由于 storage 是 placeholder，这里先不实现
            # from app.storage.database import database
            # await database.delete_document(doc_id, namespace)
        except Exception:
            # 忽略删除错误
            pass

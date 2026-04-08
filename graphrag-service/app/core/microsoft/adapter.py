"""Microsoft GraphRAG adapter - bridges API parameters to Microsoft GraphRAG."""

from __future__ import annotations

import asyncio
import json
import logging
import shutil
from pathlib import Path

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


logger = logging.getLogger(__name__)


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
        """生成 GraphRAG settings.yaml

        完整的配置参考 Microsoft GraphRAG 文档:
        https://github.com/microsoft/graphrag/tree/main/examples
        """
        return f"""encoding_model: cl100k_base
skip_workflow: false

# LLM 配置
llm:
  description: DashScope LLM
  configuration:
    type: openai_chat
    api_key: {self.llm_config['api_key']}
    model: {self.llm_config['model']}
    api_base: {self.llm_config['base_url']}

# 嵌入模型配置 (用于向量化和检索)
embeddings:
  description: DashScope Embeddings
  configuration:
    type: openai_text
    api_key: {self.llm_config['api_key']}
    model: text-embedding-v3
    api_base: {self.llm_config['base_url']}

# 存储配置
storage:
  type: file
  path: ./output

# 报告配置
reporting:
  type: file
  path: ./output/reports

# 搜索配置
search:
  type: local
  local:
    mode: local
    vectorizer: embed
    max_tokens: 7500
    temperature: 0.0
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
            await asyncio.to_thread(shutil.copy2, doc_path, dest_path)

            # 运行 graphrag index
            #
            # 注意: graphrag CLI 的 index 命令处理的是整个 workspace/input 目录，
            # 无法指定只处理特定 namespace 下的文件。这会导致:
            # 1. 如果多个 namespace 同时索引，会相互影响
            # 2. 已索引的文件重新索引时会累积数据
            # 解决方案: 可以考虑为每个 namespace 创建独立的 workspace，
            # 或在运行 index 前清空 output 目录并只保留目标 namespace 的文件
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
        results: list[IndexResult] = await asyncio.gather(*[
            self.index_document(doc_path, namespace)
            for doc_path in doc_paths
        ])

        succeeded = sum(1 for r in results if r.status == "completed")
        failed = len(results) - succeeded

        return BatchIndexResult(
            total=len(doc_paths),
            succeeded=succeeded,
            failed=failed,
            results=list(results),
        )

    async def query(
        self,
        query_text: str,
        namespace: str,
        top_k: int = 10,
        context: Optional[str] = None,
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

                # 尝试解析 entities 并应用 top_k 限制
                # 注意: graphrag CLI 没有直接的 top_k 参数，
                # 所以我们在返回结果前进行后过滤
                all_entities = output.get("entities", [])
                for entity_data in all_entities[:top_k]:
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
        self, namespace: str, query: Optional[str] = None
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
        # namespace isolation is not yet implemented in graphrag
        raise NotImplementedError(
            "Namespace isolation in get_graph_data is not yet implemented. "
            "All namespaces share the same output directory."
        )

    async def delete_document(self, doc_id: str, namespace: str) -> None:
        """删除文档及其关联数据

        注意: 当前实现仅删除 source 文件 (输入目录中的文件)，
        不删除 graphrag 已经索引的数据。这是因为:
        1. graphrag index 命令会处理整个 input 目录并生成全局索引
        2. 已生成的索引数据 (output 目录) 是累积的，无法单独删除特定文件的索引
        3. 要彻底清理，需要删除整个 output 目录并重新索引

        如需完全删除，建议:
        - 删除 source 文件后，手动清理 output 目录
        - 或为每个 namespace 使用独立的 workspace
        """
        try:
            # 删除输入目录中的文件
            namespace_dir = self._get_namespace_dir(namespace)
            doc_path = namespace_dir / doc_id
            if doc_path.exists():
                doc_path.unlink()

            # graphrag 索引数据无法单独删除，需要整体清理
        except Exception as e:
            logger.warning(f"Failed to delete document {doc_id}: {e}")

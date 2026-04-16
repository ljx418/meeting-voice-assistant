"""Microsoft GraphRAG adapter - bridges API parameters to Microsoft GraphRAG."""

from __future__ import annotations

import asyncio
import json
import logging
import os
import shutil
import uuid
from pathlib import Path
from typing import Optional, Literal, AsyncGenerator

import httpx
import numpy as np
import pandas as pd

# Monkey-patch httpx to disable trust_env (macOS system proxy issue)
# See: https://github.com/encode/httpx/issues/2524
_original_httpx_client = httpx.Client
_original_httpx_async_client = httpx.AsyncClient

class _FixedClient(_original_httpx_client):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('trust_env', False)
        super().__init__(*args, **kwargs)

class _FixedAsyncClient(_original_httpx_async_client):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('trust_env', False)
        super().__init__(*args, **kwargs)

httpx.Client = _FixedClient
httpx.AsyncClient = _FixedAsyncClient

from ...config import settings
from ..base import (
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
from ..language_detector import detect_language


logger = logging.getLogger(__name__)


class MicrosoftGraphRAGAdapter(GraphRAGCore):
    """微软 GraphRAG 实现 + 参数适配"""

    def __init__(self):
        self.workspace = settings.GRAPHRAG_WORKSPACE.resolve()  # Use absolute path
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
        """生成 GraphRAG settings.yaml（不包含明文密钥，使用环境变量）

        完整的配置参考 Microsoft GraphRAG 文档:
        https://github.com/microsoft/graphrag/tree/main/examples

        注意：API Key 通过环境变量 $GRAPHRAG_LLM_API_KEY 传入，不写入文件
        """
        return f"""encoding_model: cl100k_base
skip_workflow: false

# LLM 配置
llm:
  description: DashScope LLM
  configuration:
    type: openai_chat
    api_key: ${{GRAPHRAG_LLM_API_KEY}}
    model: {self.llm_config['model']}
    api_base: {self.llm_config['base_url']}

# 嵌入模型配置 (用于向量化和检索)
embeddings:
  description: DashScope Embeddings
  configuration:
    type: openai_text
    api_key: ${{GRAPHRAG_LLM_API_KEY}}
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

    def _get_input_dir(self) -> Path:
        """获取输入目录（环境隔离，无需 namespace 子目录）"""
        input_dir = self.workspace / "input"
        input_dir.mkdir(parents=True, exist_ok=True)
        return input_dir

    def _run_graphrag_command(self, *args: str) -> asyncio.subprocess.Process:
        """运行 graphrag CLI 命令"""
        cmd = ["graphrag"] + list(args)
        # 设置环境变量禁用 httpx trust_env，避免 macOS 系统代理干扰
        # 同时注入 LLM API Key（settings.yaml 使用 $GRAPHRAG_LLM_API_KEY 占位符）
        env = {
            **os.environ,
            "HTTPX_TRUST_ENV": "false",
            "GRAPHRAG_LLM_API_KEY": self.llm_config.get("api_key", ""),
        }
        return asyncio.create_subprocess_exec(
            *cmd,
            cwd=str(self.workspace),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            env=env,
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

    async def _stream_graphrag_index(
        self
    ) -> AsyncGenerator[dict, None]:
        """流式执行 graphrag index 命令，yield 进度事件

        Yields:
            dict: 包含 stage, progress, message
        """
        cmd = ["graphrag", "index", "--root", str(self.workspace)]
        # 注入 LLM API Key（settings.yaml 使用 $GRAPHRAG_LLM_API_KEY 占位符）
        env = {**os.environ, "HTTPX_TRUST_ENV": "false", "GRAPHRAG_LLM_API_KEY": self.llm_config.get("api_key", "")}

        process = await asyncio.create_subprocess_exec(
            *cmd,
            cwd=str(self.workspace),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            env=env,
        )

        stderr_buffer = ""
        stdout_data = b""
        process_done = False

        stage_progress_map = {
            "load_input_documents": 20,
            "create_base_text_units": 30,
            "create_final_documents": 40,
            "extract_graph": 55,
            "finalize_graph": 65,
            "extract_covariates": 70,
            "create_communities": 75,
            "create_final_text_units": 80,
            "create_community_reports": 85,
            "generate_text_embeddings": 90,
            "Pipeline complete": 95,
        }

        async def read_stdout():
            nonlocal stdout_data, process_done
            while True:
                chunk = await process.stdout.read(4096)
                if not chunk:
                    break
                stdout_data += chunk
            process_done = True

        # 并行读取 stdout 和监听 stderr 进度
        stdout_task = asyncio.create_task(read_stdout())

        try:
            while not process_done or not process.stderr.at_eof():
                # 读取 stderr
                chunk = await process.stderr.read(4096)
                if chunk:
                    line = chunk.decode("utf-8", errors="replace")
                    stderr_buffer += line

                    # 解析进度
                    for stage, prog in stage_progress_map.items():
                        if stage in stderr_buffer:
                            yield {
                                "stage": "indexing",
                                "progress": prog,
                                "message": f"索引阶段: {stage.replace('_', ' ')}",
                                "details": {}
                            }
                            stderr_buffer = ""
                            break
                else:
                    # 没有数据，短暂等待
                    await asyncio.sleep(0.1)

        finally:
            await stdout_task
            await process.wait()

        # 清理剩余的 stderr
        if stderr_buffer.strip():
            yield {
                "stage": "indexing",
                "progress": 95,
                "message": stderr_buffer.strip()[:100],
                "details": {}
            }

    async def index_document(self, doc_path: Path, namespace: str) -> IndexResult:
        """索引单个文档

        环境隔离说明:
        - 每个环境使用独立的 GRAPHRAG_WORKSPACE 目录
        - 文件直接存放在 input/ 目录（不再按 namespace 分子目录）
        - graphrag CLI 处理整个 input/ 目录

        注意: namespace 参数保留用于数据库记录，但不再用于目录组织
        """
        doc_id = doc_path.stem  # Use filename without extension as doc_id
        try:
            # 检测文件语言类型（用于日志记录）
            file_text = ""
            try:
                file_text = doc_path.read_text(encoding='utf-8', errors='ignore')[:1000]
            except Exception:
                pass
            language = detect_language(file_text)
            logger.info(f"Detected language for {doc_path.name}: {language}")

            # 文件已在 input/ 目录中（由 API 层保存），无需额外复制
            # graphrag index 会处理 input/ 目录下的所有文件

            # 运行 graphrag index
            returncode, stdout, stderr = await self._execute_command(
                "index",
                "--root",
                str(self.workspace),
            )

            # 从 parquet 文件中解析并保存实体、关系、社区数据
            entity_count = 0
            relationship_count = 0
            community_count = 0

            output_dir = self.workspace / "output"
            if output_dir.exists():
                entity_count, relationship_count, community_count = await self._parse_and_save_graphrag_output(
                    output_dir, namespace, doc_id
                )

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

    async def index_document_stream(
        self, doc_path: Path, namespace: str
    ) -> AsyncGenerator[dict, None]:
        """流式索引单个文档，yield 进度事件

        Yields:
            dict: 包含 stage, progress (0-100), message, details
        """
        doc_id = doc_path.stem

        # Stage 1: 检测语言
        yield {
            "stage": "detecting_language",
            "progress": 5,
            "message": "检测文档语言...",
            "details": {"filename": doc_path.name}
        }

        try:
            file_text = ""
            try:
                file_text = doc_path.read_text(encoding='utf-8', errors='ignore')[:1000]
            except Exception:
                pass
            language = detect_language(file_text)

            yield {
                "stage": "language_detected",
                "progress": 10,
                "message": f"语言检测完成: {language}",
                "details": {"language": language}
            }

            # Stage 2: 执行 graphrag index（流式）
            yield {
                "stage": "indexing",
                "progress": 15,
                "message": "开始索引文档...",
                "details": {"filename": doc_path.name}
            }

            # 迭代流式索引事件
            async for event in self._stream_graphrag_index():
                yield event

            yield {
                "stage": "parsing",
                "progress": 95,
                "message": "解析索引结果...",
                "details": {}
            }

            # Stage 3: 解析 parquet 文件
            entity_count = 0
            relationship_count = 0
            community_count = 0

            output_dir = self.workspace / "output"
            if output_dir.exists():
                entity_count, relationship_count, community_count = await self._parse_and_save_graphrag_output(
                    output_dir, namespace, doc_id
                )

            # Stage 4: 完成
            yield {
                "stage": "complete",
                "progress": 100,
                "message": f"索引完成: {entity_count} 实体, {relationship_count} 关系",
                "details": {
                    "document_id": doc_id,
                    "entity_count": entity_count,
                    "relationship_count": relationship_count,
                    "community_count": community_count,
                    "status": "completed"
                }
            }

        except Exception as e:
            yield {
                "stage": "error",
                "progress": 0,
                "message": f"索引失败: {str(e)}",
                "details": {}
            }

    async def _parse_and_save_graphrag_output(
        self, output_dir: Path, namespace: str, doc_id: str
    ) -> tuple[int, int, int]:
        """解析 GraphRAG 输出的 parquet 文件并保存到数据库

        Args:
            output_dir: GraphRAG output 目录 (包含 parquet 文件)
            namespace: 命名空间
            doc_id: 文档 ID

        Returns:
            (entity_count, relationship_count, community_count)
        """
        # Lazy import to avoid circular dependency
        from ...storage.database import save_entity, save_relationship, save_community, update_entity_community_id

        entity_count = 0
        relationship_count = 0
        community_count = 0

        # 解析 entities parquet (first pass - no community_id yet)
        # 同时建立 name->id 映射表用于后续 relationship 解析
        entities_file = output_dir / "entities.parquet"
        name_to_id_map: dict[str, str] = {}  # name -> entity_id
        if entities_file.exists():
            try:
                df_entities = await asyncio.to_thread(pd.read_parquet, entities_file)
                for _, row in df_entities.iterrows():
                    entity_id_str = str(row.get("id", uuid.uuid4()))
                    entity_name = str(row.get("title", ""))
                    name_to_id_map[entity_name] = entity_id_str

                    await save_entity(
                        entity_id=entity_id_str,
                        namespace=namespace,
                        name=entity_name,
                        doc_id=doc_id,
                        entity_type=str(row.get("type", "")) if pd.notna(row.get("type")) else None,
                        description=str(row.get("description", "")) if pd.notna(row.get("description")) else None,
                        community_id=None,  # Will be updated after communities are saved
                    )
                    entity_count += 1
            except Exception as e:
                logger.warning(f"Failed to parse entities parquet: {e}")

        # 解析 relationships parquet (使用 name->id 映射转换 source/target)
        relationships_file = output_dir / "relationships.parquet"
        if relationships_file.exists():
            try:
                df_rels = await asyncio.to_thread(pd.read_parquet, relationships_file)
                for _, row in df_rels.iterrows():
                    source_name = str(row.get("source", ""))
                    target_name = str(row.get("target", ""))
                    # 通过名称查找对应的 entity_id
                    source_entity_id = name_to_id_map.get(source_name, source_name)
                    target_entity_id = name_to_id_map.get(target_name, target_name)

                    await save_relationship(
                        rel_id=str(row.get("id", uuid.uuid4())),
                        source_entity_id=source_entity_id,
                        target_entity_id=target_entity_id,
                        namespace=namespace,
                        relation_type=str(row.get("type", "")) if pd.notna(row.get("type")) else None,
                        description=str(row.get("description", "")) if pd.notna(row.get("description")) else None,
                        weight=float(row.get("weight", 1.0)) if pd.notna(row.get("weight")) else 1.0,
                    )
                    relationship_count += 1
            except Exception as e:
                logger.warning(f"Failed to parse relationships parquet: {e}")

        # 解析 communities parquet
        communities_file = output_dir / "communities.parquet"
        if communities_file.exists():
            try:
                df_comm = await asyncio.to_thread(pd.read_parquet, communities_file)
                for _, row in df_comm.iterrows():
                    community_id = str(row.get("id", uuid.uuid4()))
                    await save_community(
                        community_id=community_id,
                        namespace=namespace,
                        level=int(row.get("level", 0)) if pd.notna(row.get("level")) else None,
                        summary=str(row.get("summary", "")) if pd.notna(row.get("summary")) else None,
                        parent_id=str(row.get("parent")) if pd.notna(row.get("parent")) else None,
                    )
                    community_count += 1

                    # Update entity community_ids based on entity_ids list
                    entity_ids_raw = row.get("entity_ids")
                    # entity_ids_raw could be a numpy array which has ambiguous truth value
                    try:
                        is_empty = isinstance(entity_ids_raw, np.ndarray) and entity_ids_raw.size == 0
                    except (ValueError, TypeError):
                        is_empty = False
                    if entity_ids_raw is not None and not is_empty:
                        # entity_ids may be a list, numpy array, or string representation
                        if isinstance(entity_ids_raw, (list, tuple)):
                            entity_ids = entity_ids_raw
                        elif hasattr(entity_ids_raw, 'tolist'):  # numpy array
                            entity_ids = entity_ids_raw.tolist()
                        else:
                            # Try parsing string representation
                            try:
                                entity_ids = json.loads(str(entity_ids_raw))
                            except (json.JSONDecodeError, TypeError):
                                entity_ids = []
                        for entity_id in entity_ids:
                            await update_entity_community_id(str(entity_id), community_id)
            except Exception as e:
                logger.warning(f"Failed to parse communities parquet: {e}")

        return entity_count, relationship_count, community_count

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
        self, max_nodes: int = 100
    ) -> GraphData:
        """获取图谱数据用于可视化

        Note: Environment isolation is handled via separate GRAPHRAG_WORKSPACE directories.
        """
        from ...storage.database import get_graph_data as storage_get_graph_data
        return await storage_get_graph_data(max_nodes=max_nodes)

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
            # 删除输入目录中的文件（文件直接在 input/ 目录下）
            input_dir = self._get_input_dir()
            # 尝试多种可能的文件名模式
            for ext in ['', '.txt', '.md', '.pdf', '.docx']:
                doc_path = input_dir / f"{doc_id}{ext}"
                if doc_path.exists():
                    doc_path.unlink()
                    break
            # 也尝试原始文件名（如果记录在数据库中）
            doc_path = input_dir / doc_id
            if doc_path.exists():
                doc_path.unlink()

            # graphrag 索引数据无法单独删除，需要整体清理
        except Exception as e:
            logger.warning(f"Failed to delete document {doc_id}: {e}")

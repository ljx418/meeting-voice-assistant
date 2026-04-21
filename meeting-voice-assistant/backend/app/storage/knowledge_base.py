"""
全局知识库模块

提供 L2 全局知识库功能，支持 namespace 管理和实体合并。
namespace 结构: meeting_{id} (单会议命名空间) / global (全局知识库)
"""

import json
import logging
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any, Tuple

from sqlalchemy import select, delete, func, or_, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.graphrag.storage.database import async_session
from app.graphrag.storage.models import Entity, Relationship, Document, Community

logger = logging.getLogger("knowledge_base")


# ============================================================================
# Namespace 常量
# ============================================================================

NAMESPACE_GLOBAL = "global"  # 全局知识库命名空间
NAMESPACE_PREFIX_MEETING = "meeting_"  # 单会议命名空间前缀


def is_meeting_namespace(namespace: str) -> bool:
    """判断是否为会议命名空间"""
    return namespace.startswith(NAMESPACE_PREFIX_MEETING)


def make_meeting_namespace(meeting_id: str) -> str:
    """创建会议命名空间"""
    return f"{NAMESPACE_PREFIX_MEETING}{meeting_id}"


def extract_meeting_id(namespace: str) -> Optional[str]:
    """从命名空间提取会议 ID"""
    if is_meeting_namespace(namespace):
        return namespace[len(NAMESPACE_PREFIX_MEETING):]
    return None


# ============================================================================
# 跨会议实体升级 Prompt
# ============================================================================

CROSS_MEETING_ENTITY_UPGRADE_PROMPT = """# 角色与任务
你是一个知识图谱融合助手。你的任务是基于多个会议的实体和关系，构建全局知识库。

# 输入说明
你将获得：
1. 全局知识库中已存在的实体列表（global）
2. 新会议中提取的实体列表（meeting_{id}）

# 任务目标
将新会议的实体融合到全局知识库中，识别：
1. **同义词合并**: 同一实体在不同会议中有不同名称，如"张总"和"张三"可能是同一人
2. **实体升级**: 在新会议中出现的重要实体是否应提升到全局知识库
3. **关系扩展**: 全局知识库中已有实体的关系是否需要扩展

# 实体类型（6大类型）
- PERSON: 人物
- ORGANIZATION: 组织
- PROJECT: 项目
- PRODUCT: 产品
- TECHNOLOGY: 技术
- CONCEPT: 概念

# 输出格式
请严格按以下 JSON 格式输出：

```json
{{
  "entity_merges": [
    {{
      "meeting_entity": "新会议中的实体名称",
      "global_entity": "全局知识库中对应的实体名称（如果存在）",
      "merge_action": "MERGE|UPDATE|CREATE",
      "reason": "合并/更新/创建的原因"
    }}
  ],
  "entities_to_promote": [
    {{
      "name": "应提升到全局的实体名称",
      "type": "实体类型",
      "reason": "提升原因",
      "confidence": 0.85
    }}
  ],
  "relationship_extensions": [
    {{
      "source_entity": "源实体",
      "target_entity": "目标实体",
      "new_relation_type": "新增的关系类型",
      "source_meeting_id": "来源会议ID"
    }}
  ]
}}
```

# 重要提示
1. 只有高置信度（>0.8）的同义词匹配才执行合并
2. 新会议中的核心人物和关键决策应考虑提升到全局
3. 不要过度合并，保持实体独立性


# 全局知识库实体

{global_entities}

# 新会议实体

{meeting_entities}
"""


# ============================================================================
# Synonym 同义词管理
# ============================================================================

class SynonymRegistry:
    """
    同义词注册表

    管理实体名称的同义词关系，用于实体匹配和合并。
    """

    def __init__(self):
        # 同义词组: canonical_name -> set of synonyms
        self._synonym_groups: Dict[str, set] = {}
        # 反向索引: synonym -> canonical name
        self._synonym_to_canonical: Dict[str, str] = {}

    def add_synonym_group(self, canonical: str, synonyms: List[str]) -> None:
        """添加同义词组"""
        canonical_lower = canonical.lower().strip()
        synonym_set = {canonical_lower}
        for syn in synonyms:
            synonym_set.add(syn.lower().strip())

        self._synonym_groups[canonical_lower] = synonym_set
        for s in synonym_set:
            self._synonym_to_canonical[s] = canonical_lower

    def get_canonical(self, name: str) -> Optional[str]:
        """获取名称的规范形式"""
        name_lower = name.lower().strip()
        return self._synonym_to_canonical.get(name_lower)

    def are_synonyms(self, name1: str, name2: str) -> bool:
        """判断两个名称是否为同义词"""
        c1 = self.get_canonical(name1)
        c2 = self.get_canonical(name2)
        if c1 and c2:
            return c1 == c2
        return False

    def to_dict(self) -> Dict[str, List[str]]:
        """导出同义词组"""
        return {
            k: list(v) for k, v in self._synonym_groups.items()
        }


# ============================================================================
# Embedding 相似度计算（简化版）
# ============================================================================

class EmbeddingSimilarity:
    """
    基于 Embedding 的相似度计算

    实际生产中应使用专门的 embedding 服务（如 Ollama、OpenAI）
    这里提供基于关键词重叠的简化实现作为 fallback。
    """

    # 停用词
    STOPWORDS = {"的", "了", "是", "在", "和", "与", "或", "以及", "等", "于", "对", "为", "了", "这", "那"}

    def __init__(self):
        self._embedding_cache: Dict[str, List[float]] = {}

    def _tokenize(self, text: str) -> set:
        """简单分词"""
        chars = list(text.lower().strip())
        # 简单按字符 n-gram 处理
        tokens = set()
        for n in [1, 2, 3]:
            for i in range(len(chars) - n + 1):
                tokens.add("".join(chars[i:i+n]))
        # 过滤停用词
        return tokens - self.STOPWORDS

    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """计算余弦相似度"""
        dot = sum(a * b for a, b in zip(vec1, vec2))
        norm1 = sum(a * a for a in vec1) ** 0.5
        norm2 = sum(b * b for b in vec2) ** 0.5
        if norm1 * norm2 == 0:
            return 0.0
        return dot / (norm1 * norm2)

    def compute_similarity(self, text1: str, text2: str) -> float:
        """
        计算两个文本的相似度

        Args:
            text1: 文本1
            text2: 文本2

        Returns:
            float: 相似度 0.0 - 1.0
        """
        tokens1 = self._tokenize(text1)
        tokens2 = self._tokenize(text2)

        if not tokens1 or not tokens2:
            return 0.0

        # Jaccard 相似度作为基础
        intersection = tokens1 & tokens2
        union = tokens1 | tokens2
        jaccard = len(intersection) / len(union) if union else 0.0

        # 结合字符级相似度
        char_sim = self._cosine_similarity(
            [1.0] * 100,
            [1.0] * 100
        )

        return jaccard

    async def compute_entity_similarity(
        self,
        entity1: Dict[str, Any],
        entity2: Dict[str, Any],
        synonym_registry: Optional[SynonymRegistry] = None
    ) -> float:
        """
        计算两个实体的相似度

        Args:
            entity1: 实体1 (dict with name, type, description)
            entity2: 实体2
            synonym_registry: 同义词注册表

        Returns:
            float: 相似度 0.0 - 1.0
        """
        # 名称完全匹配
        if entity1.get("name") == entity2.get("name"):
            return 1.0

        # 检查同义词
        if synonym_registry and synonym_registry.are_synonyms(
            entity1.get("name", ""),
            entity2.get("name", "")
        ):
            return 0.95

        # 类型不同，惩罚
        if entity1.get("type") != entity2.get("type"):
            return 0.0

        # 基于描述的相似度
        desc1 = entity1.get("description", "") or ""
        desc2 = entity2.get("description", "") or ""

        if not desc1 or not desc2:
            # 无描述，使用名称相似度
            return self.compute_similarity(entity1.get("name", ""), entity2.get("name", ""))

        # 描述相似度 + 名称相似度加权
        name_sim = self.compute_similarity(entity1.get("name", ""), entity2.get("name", ""))
        desc_sim = self.compute_similarity(desc1, desc2)

        return 0.4 * name_sim + 0.6 * desc_sim


# ============================================================================
# Namespace 管理
# ============================================================================

class NamespaceManager:
    """
    Namespace 命名空间管理器

    namespace 结构:
    - meeting_{id}: 单会议命名空间
    - global: 全局知识库命名空间
    """

    def __init__(self):
        self._cache: Dict[str, datetime] = {}
        self._cache_ttl = 300  # 5 分钟缓存

    async def create_namespace(self, namespace: str) -> bool:
        """
        创建命名空间（如果不存在）

        Args:
            namespace: 命名空间名称

        Returns:
            bool: 是否创建成功
        """
        try:
            async with async_session() as session:
                # 检查是否已存在
                result = await session.execute(
                    select(func.count(Document.id)).where(Document.namespace == namespace)
                )
                count = result.scalar()

                if count is None or count == 0:
                    # 创建一个占位文档用于初始化 namespace
                    placeholder = Document(
                        id=f"__ns_{namespace}_{uuid.uuid4().hex[:8]}__",
                        namespace=namespace,
                        filename="__namespace_placeholder__",
                        file_path="__namespace_placeholder__",
                    )
                    session.add(placeholder)
                    await session.commit()
                    logger.info(f"[NamespaceManager] Created namespace: {namespace}")
                    return True
                return True

        except Exception as e:
            logger.error(f"[NamespaceManager] Failed to create namespace {namespace}: {e}")
            return False

    async def delete_namespace(self, namespace: str) -> dict:
        """
        删除命名空间及其所有数据

        Args:
            namespace: 命名空间名称

        Returns:
            dict: 删除统计信息
        """
        from app.graphrag.storage.database import clear_all_data
        result = await clear_all_data(namespace)
        logger.info(f"[NamespaceManager] Deleted namespace {namespace}: {result}")
        return result

    async def list_namespaces(self) -> List[str]:
        """
        列出所有命名空间

        Returns:
            List[str]: 命名空间列表
        """
        async with async_session() as session:
            result = await session.execute(
                select(Document.namespace).distinct()
            )
            namespaces = [row[0] for row in result.fetchall()]
            return namespaces

    async def list_meeting_namespaces(self) -> List[str]:
        """列出所有会议命名空间"""
        all_ns = await self.list_namespaces()
        return [ns for ns in all_ns if is_meeting_namespace(ns)]

    async def get_or_create_global_namespace(self) -> str:
        """获取或创建全局命名空间"""
        await self.create_namespace(NAMESPACE_GLOBAL)
        return NAMESPACE_GLOBAL

    async def get_namespace_stats(self, namespace: str) -> Dict[str, int]:
        """
        获取命名空间统计信息

        Args:
            namespace: 命名空间名称

        Returns:
            Dict[str, int]: 统计数据
        """
        async with async_session() as session:
            # 文档数
            doc_result = await session.execute(
                select(func.count(Document.id)).where(Document.namespace == namespace)
            )
            doc_count = doc_result.scalar() or 0

            # 实体数
            ent_result = await session.execute(
                select(func.count(Entity.id)).where(Entity.namespace == namespace)
            )
            ent_count = ent_result.scalar() or 0

            # 关系数
            rel_result = await session.execute(
                select(func.count(Relationship.id)).where(Relationship.namespace == namespace)
            )
            rel_count = rel_result.scalar() or 0

            # 社区数
            comm_result = await session.execute(
                select(func.count(Community.id)).where(Community.namespace == namespace)
            )
            comm_count = comm_result.scalar() or 0

            return {
                "namespace": namespace,
                "documents": doc_count,
                "entities": ent_count,
                "relationships": rel_count,
                "communities": comm_count,
            }

    async def migrate_meeting_to_global(
        self,
        meeting_id: str,
        merge_threshold: float = 0.85
    ) -> dict:
        """
        将会议命名空间的实体迁移到全局知识库

        Args:
            meeting_id: 会议ID
            merge_threshold: 合并阈值

        Returns:
            dict: 迁移结果
        """
        meeting_ns = make_meeting_namespace(meeting_id)
        await self.get_or_create_global_namespace()

        # 获取会议实体
        async with async_session() as session:
            meeting_ents = await session.execute(
                select(Entity).where(Entity.namespace == meeting_ns)
            )
            meeting_entities = [
                {
                    "id": e.id,
                    "name": e.name,
                    "type": e.type,
                    "description": e.description,
                }
                for e in meeting_ents.scalars().all()
            ]

            global_ents = await session.execute(
                select(Entity).where(Entity.namespace == NAMESPACE_GLOBAL)
            )
            global_entities = [
                {
                    "id": e.id,
                    "name": e.name,
                    "type": e.type,
                    "description": e.description,
                }
                for e in global_ents.scalars().all()
            ]

        return {
            "meeting_namespace": meeting_ns,
            "meeting_entity_count": len(meeting_entities),
            "global_entity_count": len(global_entities),
            "merge_threshold": merge_threshold,
            "status": "ready_for_merge",
        }


# ============================================================================
# 实体合并
# ============================================================================

class EntityMerger:
    """
    实体合并器

    用于合并相似实体，支持同义词匹配和 embedding 相似度。
    """

    # 实体类型优先级（用于决定合并后保留的类型）
    TYPE_PRIORITY = {
        "PERSON": 1,
        "ORGANIZATION": 2,
        "PRODUCT": 3,
        "PROJECT": 4,
        "TECHNOLOGY": 5,
        "CONCEPT": 6,
    }

    def __init__(self):
        self._merge_history: List[Dict[str, str]] = []
        self._synonym_registry = SynonymRegistry()
        self._similarity_engine = EmbeddingSimilarity()

        # 预定义同义词组
        self._init_common_synonyms()

    def _init_common_synonyms(self):
        """初始化常见同义词组"""
        common_synonyms = [
            ("张总", ["张三", "张总", "Zhang San"]),
            ("李总", ["李四", "李总", "Li Si"]),
            ("王总", ["王五", "王总", "Wang Wu"]),
            ("GraphRAG", ["graphrag", "Graph RAG", "GraphRAG"]),
            ("微服务", ["微服务架构", "Microservice", "microservices"]),
        ]
        for canonical, synonyms in common_synonyms:
            self._synonym_registry.add_synonym_group(canonical, synonyms)

    async def find_similar_entities(
        self,
        namespace: str,
        threshold: float = 0.8
    ) -> List[Tuple[str, str, float]]:
        """
        查找需要合并的相似实体对

        Args:
            namespace: 命名空间
            threshold: 相似度阈值，默认 0.8

        Returns:
            List[Tuple[实体ID1, 实体ID2, 相似度]]: 相似实体对列表
        """
        async with async_session() as session:
            result = await session.execute(
                select(Entity).where(Entity.namespace == namespace)
            )
            entities = result.scalars().all()

        similar_pairs = []
        entity_dicts = [
            {
                "id": e.id,
                "name": e.name,
                "type": e.type,
                "description": e.description,
            }
            for e in entities
        ]

        for i, e1 in enumerate(entity_dicts):
            for e2 in entity_dicts[i + 1:]:
                similarity = await self._similarity_engine.compute_entity_similarity(
                    e1, e2, self._synonym_registry
                )
                if similarity >= threshold:
                    similar_pairs.append((e1["id"], e2["id"], similarity))

        return similar_pairs

    async def merge_entities(
        self,
        namespace: str,
        source_id: str,
        target_id: str,
        update_relationships: bool = True
    ) -> bool:
        """
        合并两个实体

        保留 target_id，删除 source_id，将其关系转移给 target_id。

        Args:
            namespace: 命名空间
            source_id: 被合并的实体 ID（将删除）
            target_id: 目标实体 ID（将保留）
            update_relationships: 是否更新关系指向

        Returns:
            bool: 是否合并成功
        """
        try:
            async with async_session() as session:
                # 获取两个实体
                source_result = await session.execute(
                    select(Entity).where(
                        and_(Entity.id == source_id, Entity.namespace == namespace)
                    )
                )
                source_entity = source_result.scalar_one_or_none()

                target_result = await session.execute(
                    select(Entity).where(
                        and_(Entity.id == target_id, Entity.namespace == namespace)
                    )
                )
                target_entity = target_result.scalar_one_or_none()

                if not source_entity or not target_entity:
                    logger.warning(f"[EntityMerger] Entity not found: source={source_id}, target={target_id}")
                    return False

                # 合并描述（取更长的）
                if source_entity.description and target_entity.description:
                    if len(source_entity.description) > len(target_entity.description):
                        target_entity.description = source_entity.description
                elif source_entity.description:
                    target_entity.description = source_entity.description

                # 更新关系（如果启用）
                if update_relationships:
                    # 将所有指向 source 的关系改为指向 target
                    rel_result = await session.execute(
                        select(Relationship).where(
                            and_(
                                Relationship.source_entity_id == source_id,
                                Relationship.namespace == namespace
                            )
                        )
                    )
                    for rel in rel_result.scalars():
                        rel.source_entity_id = target_id

                    # 将所有从 source 出发的关系改为从 target 出发
                    rel_result = await session.execute(
                        select(Relationship).where(
                            and_(
                                Relationship.target_entity_id == source_id,
                                Relationship.namespace == namespace
                            )
                        )
                    )
                    for rel in rel_result.scalars():
                        rel.target_entity_id = target_id

                # 删除源实体
                await session.delete(source_entity)
                await session.commit()

                # 记录合并历史
                self._merge_history.append({
                    "source_id": source_id,
                    "target_id": target_id,
                    "timestamp": datetime.now().isoformat(),
                    "merged_name": target_entity.name,
                })

                logger.info(
                    f"[EntityMerger] Merged entity {source_id} -> {target_id} (name: {target_entity.name})"
                )
                return True

        except Exception as e:
            logger.error(f"[EntityMerger] Failed to merge entities: {e}")
            return False

    async def auto_merge_namespace(
        self,
        namespace: str,
        threshold: float = 0.85
    ) -> Dict[str, Any]:
        """
        自动合并命名空间内的相似实体

        Args:
            namespace: 命名空间
            threshold: 相似度阈值

        Returns:
            Dict[str, Any]: 合并结果统计
        """
        logger.info(f"[EntityMerger] Starting auto-merge for namespace: {namespace}")

        # 查找相似实体对
        similar_pairs = await self.find_similar_entities(namespace, threshold)

        merged_count = 0
        skipped_count = 0

        for source_id, target_id, similarity in similar_pairs:
            # 检查是否已经被合并
            async with async_session() as session:
                check_result = await session.execute(
                    select(Entity.id).where(Entity.id == source_id)
                )
                if check_result.scalar_one_or_none() is None:
                    skipped_count += 1
                    continue

            success = await self.merge_entities(namespace, source_id, target_id)
            if success:
                merged_count += 1
            else:
                skipped_count += 1

        result = {
            "namespace": namespace,
            "threshold": threshold,
            "similar_pairs_found": len(similar_pairs),
            "merged_count": merged_count,
            "skipped_count": skipped_count,
            "merge_history": self._merge_history[-10:],
        }

        logger.info(f"[EntityMerger] Auto-merge completed: {result}")
        return result

    def get_merge_history(self, limit: int = 10) -> List[Dict[str, str]]:
        """获取合并历史"""
        return self._merge_history[-limit:]

    def add_synonym(self, canonical: str, synonym: str) -> None:
        """添加同义词"""
        self._synonym_registry.add_synonym_group(canonical, [synonym])


# ============================================================================
# 全局知识库
# ============================================================================

class GlobalKnowledgeBase:
    """
    全局知识库

    整合 namespace 管理和实体合并功能，提供统一的接口。
    namespace 结构:
    - meeting_{id}: 单会议命名空间
    - global: 全局知识库命名空间
    """

    def __init__(self):
        self.namespace_manager = NamespaceManager()
        self.entity_merger = EntityMerger()
        self.synonym_registry = SynonymRegistry()

    async def initialize(self) -> None:
        """初始化知识库"""
        logger.info("[GlobalKnowledgeBase] Initializing...")
        await self.namespace_manager.get_or_create_global_namespace()

    async def create_namespace_if_not_exists(self, namespace: str) -> bool:
        """创建命名空间（如果不存在）"""
        return await self.namespace_manager.create_namespace(namespace)

    async def get_knowledge_graph(
        self,
        namespace: str,
        max_entities: int = 100,
        max_relationships: int = 200
    ) -> Dict[str, Any]:
        """
        获取知识图谱数据

        Args:
            namespace: 命名空间
            max_entities: 最大实体数
            max_relationships: 最大关系数

        Returns:
            Dict containing nodes and edges
        """
        async with async_session() as session:
            # 获取实体
            ent_result = await session.execute(
                select(Entity)
                .where(Entity.namespace == namespace)
                .limit(max_entities)
            )
            entities = ent_result.scalars().all()

            nodes = []
            entity_ids = []
            for entity in entities:
                nodes.append({
                    "id": entity.id,
                    "name": entity.name,
                    "type": entity.type or "unknown",
                    "description": entity.description,
                    "community_id": entity.community_id,
                })
                entity_ids.append(entity.id)

            # 获取关系
            edges = []
            if entity_ids:
                rel_result = await session.execute(
                    select(Relationship)
                    .where(
                        and_(
                            Relationship.namespace == namespace,
                            or_(
                                Relationship.source_entity_id.in_(entity_ids),
                                Relationship.target_entity_id.in_(entity_ids)
                            )
                        )
                    )
                    .limit(max_relationships)
                )
                relationships = rel_result.scalars().all()

                for rel in relationships:
                    edges.append({
                        "id": rel.id,
                        "source": rel.source_entity_id,
                        "target": rel.target_entity_id,
                        "type": rel.relation_type or "related",
                        "description": rel.description,
                        "weight": rel.weight,
                    })

            return {
                "namespace": namespace,
                "nodes": nodes,
                "edges": edges,
                "stats": await self.namespace_manager.get_namespace_stats(namespace),
            }

    async def search_entities(
        self,
        namespace: str,
        query: str,
        entity_type: Optional[str] = None,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        搜索实体

        Args:
            namespace: 命名空间
            query: 搜索关键词
            entity_type: 实体类型过滤
            limit: 返回数量限制

        Returns:
            List[Dict]: 匹配的实体列表
        """
        async with async_session() as session:
            stmt = select(Entity).where(Entity.namespace == namespace)

            if entity_type:
                stmt = stmt.where(Entity.type == entity_type)

            result = await session.execute(stmt.limit(limit * 2))
            entities = result.scalars().all()

        # 简单的关键词匹配
        query_lower = query.lower()
        matched = []
        for entity in entities:
            if query_lower in entity.name.lower():
                matched.append({
                    "id": entity.id,
                    "name": entity.name,
                    "type": entity.type,
                    "description": entity.description,
                })
                if len(matched) >= limit:
                    break

        return matched

    async def get_entity_relationships(
        self,
        namespace: str,
        entity_id: str
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        获取实体的所有关系

        Args:
            namespace: 命名空间
            entity_id: 实体 ID

        Returns:
            Dict with 'incoming' and 'outgoing' relationship lists
        """
        async with async_session() as session:
            # 获取作为源实体的关系（ outgoing ）
            outgoing_result = await session.execute(
                select(Relationship, Entity)
                .join(Entity, Relationship.target_entity_id == Entity.id)
                .where(
                    and_(
                        Relationship.source_entity_id == entity_id,
                        Relationship.namespace == namespace
                    )
                )
            )
            outgoing = []
            for rel, target in outgoing_result.all():
                outgoing.append({
                    "relationship_id": rel.id,
                    "target_entity": {
                        "id": target.id,
                        "name": target.name,
                        "type": target.type,
                    },
                    "relation_type": rel.relation_type,
                    "description": rel.description,
                    "weight": rel.weight,
                })

            # 获取作为目标实体的关系（ incoming ）
            incoming_result = await session.execute(
                select(Relationship, Entity)
                .join(Entity, Relationship.source_entity_id == Entity.id)
                .where(
                    and_(
                        Relationship.target_entity_id == entity_id,
                        Relationship.namespace == namespace
                    )
                )
            )
            incoming = []
            for rel, source in incoming_result.all():
                incoming.append({
                    "relationship_id": rel.id,
                    "source_entity": {
                        "id": source.id,
                        "name": source.name,
                        "type": source.type,
                    },
                    "relation_type": rel.relation_type,
                    "description": rel.description,
                    "weight": rel.weight,
                })

        return {
            "entity_id": entity_id,
            "outgoing": outgoing,
            "incoming": incoming,
        }

    async def export_knowledge_base(self, namespace: str) -> Dict[str, Any]:
        """
        导出知识库数据

        Args:
            namespace: 命名空间

        Returns:
            Dict: 完整的知识库数据
        """
        async with async_session() as session:
            # 获取所有文档
            docs_result = await session.execute(
                select(Document).where(Document.namespace == namespace)
            )
            documents = []
            for doc in docs_result.scalars().all():
                if not doc.filename.startswith("__"):
                    documents.append({
                        "id": doc.id,
                        "filename": doc.filename,
                        "file_path": doc.file_path,
                        "indexed_at": doc.indexed_at.isoformat() if doc.indexed_at else None,
                        "chunk_count": doc.chunk_count,
                        "entity_count": doc.entity_count,
                    })

            # 获取所有实体
            ents_result = await session.execute(
                select(Entity).where(Entity.namespace == namespace)
            )
            entities = []
            for ent in ents_result.scalars().all():
                entities.append({
                    "id": ent.id,
                    "name": ent.name,
                    "type": ent.type,
                    "description": ent.description,
                    "community_id": ent.community_id,
                    "doc_id": ent.doc_id,
                })

            # 获取所有关系
            rels_result = await session.execute(
                select(Relationship).where(Relationship.namespace == namespace)
            )
            relationships = []
            for rel in rels_result.scalars().all():
                relationships.append({
                    "id": rel.id,
                    "source_entity_id": rel.source_entity_id,
                    "target_entity_id": rel.target_entity_id,
                    "relation_type": rel.relation_type,
                    "description": rel.description,
                    "weight": rel.weight,
                })

            # 获取所有社区
            comms_result = await session.execute(
                select(Community).where(Community.namespace == namespace)
            )
            communities = []
            for comm in comms_result.scalars().all():
                communities.append({
                    "id": comm.id,
                    "level": comm.level,
                    "summary": comm.summary,
                    "parent_id": comm.parent_id,
                })

        return {
            "namespace": namespace,
            "exported_at": datetime.now().isoformat(),
            "statistics": await self.namespace_manager.get_namespace_stats(namespace),
            "documents": documents,
            "entities": entities,
            "relationships": relationships,
            "communities": communities,
        }

    async def merge_meeting_to_global(
        self,
        meeting_id: str,
        merge_threshold: float = 0.85
    ) -> Dict[str, Any]:
        """
        将会议命名空间合并到全局知识库

        Args:
            meeting_id: 会议ID
            merge_threshold: 合并阈值

        Returns:
            dict: 合并结果
        """
        meeting_ns = make_meeting_namespace(meeting_id)
        await self.namespace_manager.get_or_create_global_namespace()

        # 自动合并会议内相似实体
        meeting_result = await self.entity_merger.auto_merge_namespace(meeting_ns, merge_threshold)

        # 自动合并全局内相似实体
        global_result = await self.entity_merger.auto_merge_namespace(NAMESPACE_GLOBAL, merge_threshold)

        return {
            "meeting_id": meeting_id,
            "meeting_merge": meeting_result,
            "global_merge": global_result,
            "status": "completed",
        }


# ============================================================================
# 全局实例
# ============================================================================

_global_kb: Optional[GlobalKnowledgeBase] = None


def get_knowledge_base() -> GlobalKnowledgeBase:
    """获取全局知识库实例"""
    global _global_kb
    if _global_kb is None:
        _global_kb = GlobalKnowledgeBase()
    return _global_kb

"""Compatibility graph state materializer for data_service workspaces."""

from __future__ import annotations

import re
import sqlite3
from collections import defaultdict
from pathlib import Path
from typing import Dict, Iterable, List, Tuple


class GraphCompatMaterializer:
    """Materialize one compatibility graph DB from distilled contract payloads."""

    STAGING_DB_NAME = "graphrag.db"
    ENTITY_STOPWORDS = {
        "废弃于", "学习", "使用", "注意事项", "注意", "事项", "流程图", "根据", "现在", "需要",
        "建库", "指南", "说明", "记录", "问题", "内容", "方案", "某个", "以及", "相关", "安装",
        "技术咨询", "学习废弃于", "技术咨询废弃于", "步骤", "方法", "分析", "解析",
        "认证", "已安装", "选项验证", "含义", "配置微信飞书", "国内", "免费", "介绍", "app", "user",
    }
    THEME_STOPWORDS = ENTITY_STOPWORDS | {"安装", "如何", "怎么", "什么", "为什么"}
    ENTITY_REJECT_SUBSTRINGS = {
        "现在需要", "根据此", "某个", "流程图", "建库", "方案中的", "试验流程", "注意事项", "错误解决",
    }
    GENERIC_CN_SHORT_TOKENS = {
        "分析", "解析", "指南", "内容", "说明", "记录", "问题", "方案", "步骤", "方法",
        "工作", "政策", "主题", "总结", "情况", "结果", "原因", "过程", "计划",
    }
    THEME_SUFFIX_PATTERNS = [
        re.compile(r"(涨跌逻辑分析|逻辑分析|搭建指南|安装指南|使用指南|配置说明|说明|指南|解析|分析|闪退解决|错误解决|解决方案|问题排查|使用限制|信息查询|信息获取建议|核实及信息获取建议|计算税前工资)$"),
    ]

    @classmethod
    def write_compat_state_from_contract(
        cls,
        workspace: Path,
        contract_payload: Dict[str, object],
        *,
        execution_owner: str = "app.graphrag",
    ) -> Dict[str, object]:
        from data_service.models import (
            ArtifactLayout,
            AuthorityLevel,
            DistilledUnit,
            DistilledUnitKind,
            EngineTarget,
            GraphExecutionOwner,
            IngestPlan,
            SourceEnvelope,
        )

        workspace = Path(workspace).resolve()
        layout = ArtifactLayout.from_workspace(workspace)
        layout.ensure_directories()
        owner = GraphExecutionOwner(execution_owner)
        sources = []
        for source in contract_payload.get("sources", []):
            meta = dict(source.get("meta", {}) or {})
            sources.append(
                SourceEnvelope(
                    path=str(source.get("path", "")),
                    source_id=str(source.get("source_id", "")),
                    authority_hint=AuthorityLevel(str(source.get("authority", AuthorityLevel.PRIMARY_DOC.value))),
                    meta={key: str(value) for key, value in meta.items()},
                )
            )
        plan = IngestPlan(
            workspace=workspace,
            layout=layout,
            sources=sources,
            targets=[EngineTarget.GRAPHRAG],
            stages=[],
            graphrag_execution_owner=owner,
        )
        units: List[DistilledUnit] = []
        for item in contract_payload.get("units", []):
            units.append(
                DistilledUnit(
                    unit_id=str(item["unit_id"]),
                    source_id=str(item["source_id"]),
                    kind=DistilledUnitKind(str(item["kind"])),
                    authority=AuthorityLevel(str(item["authority"])),
                    text=str(item["text"]),
                    normalized_text=str(item.get("normalized_text", item["text"])),
                    importance=float(item.get("importance", 0.0)),
                    confidence=float(item.get("confidence", 0.0)),
                    source_weight=float(item.get("source_weight", 1.0)),
                    source_density_score=float(item.get("source_density_score", 1.0)),
                    is_title_derived=bool(item.get("is_title_derived", False)),
                    is_llm_enriched=bool(item.get("is_llm_enriched", False)),
                    tags=list(item.get("tags", []) or []),
                    entities=list(item.get("entities", []) or []),
                    relations=list(item.get("relations", []) or []),
                    provenance=dict(item.get("provenance", {}) or {}),
                )
            )
        db_path = layout.graphrag_state_dir / cls.STAGING_DB_NAME
        stats = cls.write_index(db_path, plan, units)
        return {
            "state_db": str(db_path),
            **stats,
        }

    @classmethod
    def write_index(cls, db_path: Path, plan, units) -> Dict[str, int]:
        conn = sqlite3.connect(db_path)
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS documents (
                    id TEXT PRIMARY KEY,
                    filename TEXT NOT NULL,
                    file_path TEXT NOT NULL,
                    authority TEXT,
                    distilled_unit_count INTEGER NOT NULL DEFAULT 0,
                    source_weight REAL NOT NULL DEFAULT 1.0,
                    density_score REAL NOT NULL DEFAULT 1.0,
                    primary_theme TEXT
                )
                """
            )
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS distilled_units (
                    unit_id TEXT PRIMARY KEY,
                    source_id TEXT NOT NULL,
                    kind TEXT NOT NULL,
                    authority TEXT NOT NULL,
                    text TEXT NOT NULL,
                    importance REAL NOT NULL DEFAULT 0,
                    confidence REAL NOT NULL DEFAULT 0,
                    source_weight REAL NOT NULL DEFAULT 1.0,
                    source_density_score REAL NOT NULL DEFAULT 1.0,
                    is_title_derived INTEGER NOT NULL DEFAULT 0,
                    is_llm_enriched INTEGER NOT NULL DEFAULT 0
                )
                """
            )
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS entities (
                    entity_id TEXT PRIMARY KEY,
                    normalized_name TEXT NOT NULL UNIQUE,
                    name TEXT NOT NULL,
                    occurrence_count INTEGER NOT NULL DEFAULT 0,
                    weighted_occurrence_count REAL NOT NULL DEFAULT 0,
                    document_count INTEGER NOT NULL DEFAULT 0
                )
                """
            )
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS themes (
                    theme_id TEXT PRIMARY KEY,
                    normalized_label TEXT NOT NULL UNIQUE,
                    label TEXT NOT NULL,
                    weighted_score REAL NOT NULL DEFAULT 0,
                    source_count INTEGER NOT NULL DEFAULT 0
                )
                """
            )
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS document_entities (
                    doc_id TEXT NOT NULL,
                    entity_id TEXT NOT NULL,
                    occurrence_count INTEGER NOT NULL DEFAULT 0,
                    weighted_occurrence_count REAL NOT NULL DEFAULT 0,
                    PRIMARY KEY (doc_id, entity_id)
                )
                """
            )
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS relationships (
                    relationship_id TEXT PRIMARY KEY,
                    source_node_id TEXT NOT NULL,
                    target_node_id TEXT NOT NULL,
                    source_node_kind TEXT NOT NULL,
                    target_node_kind TEXT NOT NULL,
                    relation_type TEXT NOT NULL,
                    weight REAL NOT NULL DEFAULT 1.0,
                    source_id TEXT,
                    unit_id TEXT
                )
                """
            )

            for table in ["documents", "distilled_units", "entities", "themes", "document_entities", "relationships"]:
                cursor.execute(f"DELETE FROM {table}")
            cursor.execute("DROP TABLE IF EXISTS entity_fts")
            cursor.execute("DROP TABLE IF EXISTS theme_fts")
            cursor.execute("DROP TABLE IF EXISTS unit_fts")
            cursor.execute("CREATE VIRTUAL TABLE entity_fts USING fts5(entity_id UNINDEXED, name, normalized_name)")
            cursor.execute("CREATE VIRTUAL TABLE theme_fts USING fts5(theme_id UNINDEXED, label, normalized_label)")
            cursor.execute("CREATE VIRTUAL TABLE unit_fts USING fts5(unit_id UNINDEXED, source_id UNINDEXED, text)")

            unit_counts: Dict[str, int] = defaultdict(int)
            source_authority: Dict[str, str] = {}
            source_weights: Dict[str, float] = defaultdict(lambda: 1.0)
            source_density: Dict[str, float] = defaultdict(lambda: 1.0)
            source_primary_theme: Dict[str, str] = {}

            entity_occurrences: Dict[str, int] = defaultdict(int)
            entity_weighted_occurrences: Dict[str, float] = defaultdict(float)
            entity_names: Dict[str, str] = {}
            document_entities: Dict[str, Dict[str, Dict[str, float]]] = defaultdict(lambda: defaultdict(lambda: {"count": 0, "weight": 0.0}))

            theme_scores: Dict[str, float] = defaultdict(float)
            theme_labels: Dict[str, str] = {}
            theme_sources: Dict[str, set] = defaultdict(set)
            relationships: Dict[Tuple[str, str, str], float] = defaultdict(float)

            for unit in units:
                unit_counts[unit.source_id] += 1
                source_authority[unit.source_id] = unit.authority.value if hasattr(unit.authority, "value") else str(unit.authority)
                source_weights[unit.source_id] = max(source_weights[unit.source_id], float(unit.source_weight or 1.0))
                source_density[unit.source_id] = max(source_density[unit.source_id], float(unit.source_density_score or 1.0))

                cursor.execute(
                    """
                    INSERT INTO distilled_units (
                        unit_id, source_id, kind, authority, text, importance, confidence,
                        source_weight, source_density_score, is_title_derived, is_llm_enriched
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        unit.unit_id,
                        unit.source_id,
                        unit.kind.value if hasattr(unit.kind, "value") else str(unit.kind),
                        unit.authority.value if hasattr(unit.authority, "value") else str(unit.authority),
                        unit.text,
                        unit.importance,
                        unit.confidence,
                        unit.source_weight,
                        unit.source_density_score,
                        int(bool(unit.is_title_derived)),
                        int(bool(unit.is_llm_enriched)),
                    ),
                )
                cursor.execute("INSERT INTO unit_fts (unit_id, source_id, text) VALUES (?, ?, ?)", (unit.unit_id, unit.source_id, unit.text))

                unit_entities = cls._unit_entities(unit)
                unit_themes = cls._unit_themes(unit)
                unit_weight = max(0.25, float(unit.importance or 0.0) * float(unit.source_weight or 1.0))

                for normalized_name, display_name in unit_entities:
                    entity_occurrences[normalized_name] += 1
                    entity_weighted_occurrences[normalized_name] += unit_weight
                    entity_names.setdefault(normalized_name, display_name)
                    document_entities[unit.source_id][normalized_name]["count"] += 1
                    document_entities[unit.source_id][normalized_name]["weight"] += unit_weight

                if unit_themes and unit.source_id not in source_primary_theme:
                    source_primary_theme[unit.source_id] = unit_themes[0][1]

                for normalized_label, display_label in unit_themes:
                    theme_scores[normalized_label] += unit_weight
                    theme_labels.setdefault(normalized_label, display_label)
                    theme_sources[normalized_label].add(unit.source_id)
                    for normalized_name, _display_name in unit_entities:
                        relationships[(f"entity:{normalized_name}", f"theme:{normalized_label}", "about")] += unit_weight

                for source_name, target_name in cls._pairwise(unit_entities):
                    if source_name == target_name:
                        continue
                    left, right = sorted([source_name, target_name], key=lambda item: item[0])
                    relationships[(f"entity:{left[0]}", f"entity:{right[0]}", "co_occurs")] += unit_weight

            for source in plan.sources:
                source_id = source.source_id or Path(source.path).stem
                cursor.execute(
                    """
                    INSERT INTO documents (
                        id, filename, file_path, authority, distilled_unit_count, source_weight, density_score, primary_theme
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        source_id,
                        Path(source.path).name,
                        source.path,
                        source_authority.get(source_id, ""),
                        unit_counts.get(source_id, 0),
                        source_weights.get(source_id, 1.0),
                        source_density.get(source_id, 1.0),
                        source_primary_theme.get(source_id),
                    ),
                )

            entity_ids: Dict[str, str] = {}
            for normalized_name, display_name in entity_names.items():
                entity_id = f"entity:{normalized_name}"
                entity_ids[normalized_name] = entity_id
                doc_count = sum(1 for per_doc in document_entities.values() if normalized_name in per_doc)
                cursor.execute(
                    """
                    INSERT INTO entities (
                        entity_id, normalized_name, name, occurrence_count, weighted_occurrence_count, document_count
                    ) VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (
                        entity_id,
                        normalized_name,
                        display_name,
                        entity_occurrences[normalized_name],
                        round(entity_weighted_occurrences[normalized_name], 4),
                        doc_count,
                    ),
                )
                cursor.execute("INSERT INTO entity_fts (entity_id, name, normalized_name) VALUES (?, ?, ?)", (entity_id, display_name, normalized_name))

            theme_ids: Dict[str, str] = {}
            for normalized_label, display_label in theme_labels.items():
                theme_id = f"theme:{normalized_label}"
                theme_ids[normalized_label] = theme_id
                cursor.execute(
                    """
                    INSERT INTO themes (
                        theme_id, normalized_label, label, weighted_score, source_count
                    ) VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        theme_id,
                        normalized_label,
                        display_label,
                        round(theme_scores[normalized_label], 4),
                        len(theme_sources[normalized_label]),
                    ),
                )
                cursor.execute("INSERT INTO theme_fts (theme_id, label, normalized_label) VALUES (?, ?, ?)", (theme_id, display_label, normalized_label))

            for doc_id, per_doc in document_entities.items():
                for normalized_name, stats in per_doc.items():
                    cursor.execute(
                        """
                        INSERT INTO document_entities (
                            doc_id, entity_id, occurrence_count, weighted_occurrence_count
                        ) VALUES (?, ?, ?, ?)
                        """,
                        (
                            doc_id,
                            entity_ids[normalized_name],
                            int(stats["count"]),
                            round(stats["weight"], 4),
                        ),
                    )

            rel_index = 0
            for (source_node_id, target_node_id, relation_type), weight in relationships.items():
                rel_index += 1
                source_kind = "theme" if source_node_id.startswith("theme:") else "entity"
                target_kind = "theme" if target_node_id.startswith("theme:") else "entity"
                cursor.execute(
                    """
                    INSERT INTO relationships (
                        relationship_id, source_node_id, target_node_id, source_node_kind, target_node_kind, relation_type, weight
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        f"rel:{rel_index}",
                        source_node_id,
                        target_node_id,
                        source_kind,
                        target_kind,
                        relation_type,
                        round(weight, 4),
                    ),
                )

            conn.commit()
            return {
                "entity_count": len(entity_ids),
                "theme_count": len(theme_ids),
                "relationship_count": rel_index,
            }
        finally:
            conn.close()

    @classmethod
    def _unit_entities(cls, unit) -> List[Tuple[str, str]]:
        candidates = list(unit.entities or [])
        pairs: List[Tuple[str, str]] = []
        seen = set()
        for raw in candidates:
            display_name = str(raw).strip()
            normalized_name = cls._normalize_entity_name(display_name)
            if not normalized_name or normalized_name in seen:
                continue
            if not cls._is_meaningful_entity(display_name):
                continue
            seen.add(normalized_name)
            pairs.append((normalized_name, display_name))
        return pairs

    @classmethod
    def _unit_themes(cls, unit) -> List[Tuple[str, str]]:
        from data_service.models import DistilledUnitKind

        candidates: List[str] = []
        kind = unit.kind.value if hasattr(unit.kind, "value") else str(unit.kind)
        if kind == DistilledUnitKind.TOPIC_CANDIDATE.value:
            candidates.append(unit.text)
        pairs: List[Tuple[str, str]] = []
        seen = set()
        for raw in candidates:
            display_label = str(raw).strip()
            normalized_label = cls._normalize_entity_name(display_label)
            if not normalized_label or normalized_label in seen:
                continue
            if not cls._is_meaningful_theme(display_label):
                continue
            seen.add(normalized_label)
            pairs.append((normalized_label, display_label))
        return pairs

    @staticmethod
    def _normalize_entity_name(value: str) -> str:
        normalized = re.sub(r"\s+", " ", value).strip().lower()
        normalized = re.sub(r"[^0-9a-z\u4e00-\u9fff ._+-]", "", normalized)
        return normalized.strip(" ._+-")

    @classmethod
    def _is_meaningful_entity(cls, value: str) -> bool:
        normalized = cls._normalize_entity_name(value)
        if not normalized or normalized in cls.ENTITY_STOPWORDS:
            return False
        if any(fragment in normalized for fragment in cls.ENTITY_REJECT_SUBSTRINGS):
            return False
        if cls._looks_like_noise_phrase(normalized):
            return False
        if normalized.startswith("废弃于") or normalized.endswith("废弃于"):
            return False
        if re.fullmatch(r"[0-9.]+", normalized):
            return False
        if re.fullmatch(r"\d+[\u4e00-\u9fff]{1,4}", normalized):
            return False
        if re.fullmatch(r"[\u4e00-\u9fff]+", normalized) and len(normalized) > 8:
            return False
        if re.fullmatch(r"[\u4e00-\u9fff]{2,3}", normalized) and normalized in cls.GENERIC_CN_SHORT_TOKENS:
            return False
        return len(normalized) >= 2

    @classmethod
    def _is_meaningful_theme(cls, value: str) -> bool:
        normalized = cls._normalize_entity_name(cls._clean_theme_candidate(value))
        if not normalized or normalized in cls.THEME_STOPWORDS:
            return False
        if cls._looks_like_noise_phrase(normalized):
            return False
        if normalized.startswith("废弃于") or normalized.endswith("废弃于"):
            return False
        if normalized.startswith("表") and re.search(r"\d", normalized):
            return False
        if "试验流程" in normalized or "流程表" in normalized or "建库" in normalized:
            return False
        if re.fullmatch(r"\d+[\u4e00-\u9fff]{1,6}", normalized):
            return False
        if re.fullmatch(r"\d+岁[\u4e00-\u9fff]{0,8}", normalized):
            return False
        if re.fullmatch(r"[\u4e00-\u9fff]{2,3}", normalized) and normalized in cls.GENERIC_CN_SHORT_TOKENS:
            return False
        if re.fullmatch(r"[\u4e00-\u9fff]{9,}", normalized) and not any(ch in normalized for ch in ("ai", "llm", "mcp", "etf")):
            return False
        return len(normalized) >= 2

    @classmethod
    def _looks_like_noise_phrase(cls, token: str) -> bool:
        if not token:
            return True
        if any(fragment in token for fragment in cls.ENTITY_REJECT_SUBSTRINGS):
            return True
        if token.startswith(("第", "这", "该")) and len(token) <= 4:
            return True
        if token.endswith(("中的", "里的", "相关", "情况")) and len(token) <= 6:
            return True
        if re.fullmatch(r"岁工作[\u4e00-\u9fff]{0,4}", token):
            return True
        if re.fullmatch(r"(公里续航发展|元以上人数|岁被裁退休金计算|万贷款)", token):
            return True
        if re.fullmatch(r"点分析[\u4e00-\u9fff]{0,4}", token):
            return True
        if re.fullmatch(r"表\d+[\u4e00-\u9fff]{0,12}", token):
            return True
        if re.fullmatch(r"[a-z]+(?:\s+[a-z]+){2,}", token):
            return True
        if re.fullmatch(r"[\u4e00-\u9fff]{2,4}", token) and token.endswith(("分析", "解析", "工作", "内容", "说明")):
            return True
        return False

    @classmethod
    def _clean_theme_candidate(cls, value: str) -> str:
        text = str(value or "").strip()
        text = re.sub(r"^表\d+[\u4e00-\u9fffA-Za-z0-9]{0,8}", "", text)
        text = re.sub(r"^[0-9]+岁", "", text)
        text = re.sub(r"\d+岁被裁退休金计算$", "", text)
        text = re.sub(r"([\u4e00-\u9fffA-Za-z]+)\d+公里续航发展(?:分析)?$", r"\1", text)
        text = re.sub(r"([\u4e00-\u9fffA-Za-z]+)\d+元以上人数(?:分析)?$", r"\1", text)
        text = re.sub(r"([\u4e00-\u9fffA-Za-z]+)\d+岁被裁退休金计算$", r"\1", text)
        text = re.sub(r"^\d+万贷款(?:\d+年等额本息月供计算)?$", "贷款", text)
        text = re.sub(r"^税后\d+万计算税前工资$", "税前工资", text)
        for pattern in cls.THEME_SUFFIX_PATTERNS:
            text = pattern.sub("", text).strip()
        mixed_prefix = re.match(r"^([A-Za-z][A-Za-z0-9.+_-]{1,}|[A-Z]{2,}[A-Za-z0-9.+_-]*|\d*[A-Z][A-Za-z0-9.+_-]*)(?:[\u4e00-\u9fff].*)$", text)
        if mixed_prefix:
            text = mixed_prefix.group(1)
        text = re.sub(r"^([A-Za-z][A-Za-z0-9.+_-]{1,}|[A-Z]{2,}[A-Za-z0-9.+_-]*)(?:中的.+)$", r"\1", text)
        text = re.sub(r"\s+", " ", text).strip(" -_")
        return text

    @staticmethod
    def _pairwise(items: Iterable[Tuple[str, str]]) -> List[Tuple[Tuple[str, str], Tuple[str, str]]]:
        items = list(items)
        pairs: List[Tuple[Tuple[str, str], Tuple[str, str]]] = []
        for index, current in enumerate(items):
            for other in items[index + 1:]:
                pairs.append((current, other))
        return pairs

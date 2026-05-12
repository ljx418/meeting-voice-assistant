"""Session relation extraction primitives for GraphRAG service boundaries."""

from __future__ import annotations

import hashlib
import re
from typing import Any

from .session_graph_service import stable_slug


class SessionRelationExtractor:
    """Extract session units, actors, and relations from structured source records."""

    def extract(
        self,
        *,
        session_id: str,
        sources: list[dict[str, Any]],
    ) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, dict[str, Any]], dict[str, dict[str, Any]]]:
        units = []
        relations = []
        actors: dict[str, dict[str, Any]] = {}
        source_nodes: dict[str, dict[str, Any]] = {}
        for item in sources:
            source = dict(item.get("source") or {})
            source_id = str(source.get("source_id") or "")
            if not source_id:
                continue
            source_nodes[source_id] = source
            for record in item.get("records", []) or []:
                text = str((record or {}).get("text") or "").strip()
                if not text:
                    continue
                actor_id = record.get("actor_id")
                if actor_id:
                    actors[str(actor_id)] = {
                        "actor_id": str(actor_id),
                        "label": str(record.get("actor_label") or actor_id),
                        "role": str(record.get("role") or ""),
                    }
                unit_type = self.classify_unit(text)
                record_id = str(record.get("record_id") or "")
                unit_id = f"unit_{hashlib.sha256((source_id + record_id + text).encode('utf-8')).hexdigest()[:16]}"
                topics = self.extract_topics(text)
                entities = self.extract_entities(text, actors)
                source_refs = [
                    {
                        "source_id": source_id,
                        "record_id": record.get("record_id"),
                        "start_time": record.get("start_time"),
                        "end_time": record.get("end_time"),
                    }
                ]
                unit = {
                    "unit_id": unit_id,
                    "session_id": session_id,
                    "unit_type": unit_type,
                    "text": text,
                    "actors": ([{"actor_id": str(actor_id), "role": self.actor_relation_role(unit_type)}] if actor_id else []),
                    "source_refs": source_refs,
                    "topics": topics,
                    "entities": entities,
                    "confidence": self.unit_confidence(unit_type),
                    "metadata": {"record_id": record.get("record_id"), "source_type": source.get("source_type")},
                }
                units.append(unit)
                if actor_id:
                    relations.append(self.relation_for_actor(unit_type, str(actor_id), unit_id, source_refs))
                relations.append(
                    {
                        "source": f"unit:{unit_id}",
                        "target": f"source:{source_id}",
                        "type": "unit_related_to_source",
                        "weight": 1.0,
                        "source_refs": source_refs,
                    }
                )
                for topic in topics:
                    relations.append(
                        {
                            "source": f"unit:{unit_id}",
                            "target": f"topic:{stable_slug(topic, fallback='topic')}",
                            "type": "unit_about_topic",
                            "weight": 0.8,
                            "source_refs": source_refs,
                            "label": topic,
                        }
                    )
                for entity in entities:
                    relations.append(
                        {
                            "source": f"unit:{unit_id}",
                            "target": f"entity:{stable_slug(entity, fallback='entity')}",
                            "type": "unit_mentions_entity",
                            "weight": 0.72,
                            "source_refs": source_refs,
                            "label": entity,
                        }
                    )
                for left, right in self.pairwise(entities):
                    relations.append(
                        {
                            "source": f"entity:{stable_slug(left, fallback='entity')}",
                            "target": f"entity:{stable_slug(right, fallback='entity')}",
                            "type": "entity_co_occurs",
                            "weight": 0.45,
                            "source_refs": source_refs,
                        }
                    )
            for related_source_id in source.get("related_source_ids", []) or []:
                relations.append(
                    {
                        "source": f"source:{source_id}",
                        "target": f"source:{related_source_id}",
                        "type": "source_related_to_source",
                        "weight": 0.6,
                        "source_refs": [{"source_id": source_id}],
                    }
                )
        return units, relations, actors, source_nodes

    @staticmethod
    def classify_unit(text: str) -> str:
        lowered = text.lower()
        if "?" in text or "？" in text or any(token in text for token in ["吗", "如何", "怎么", "是否"]):
            return "question"
        if any(token in text for token in ["决定", "确认", "定为", "通过", "验收"]):
            return "decision"
        if any(token in text for token in ["负责", "完成", "跟进", "推进", "提交", "整理"]):
            return "task"
        if any(token in text for token in ["风险", "担心", "阻塞", "延期", "问题", "失败"]):
            return "risk"
        if any(token in lowered for token in ["must", "require", "requirement"]) or any(token in text for token in ["必须", "需要"]):
            return "requirement"
        if re.search(r"\d{4}|\d+月|\d+日|下周|今天|明天|昨天", text):
            return "fact"
        return "statement"

    @staticmethod
    def actor_relation_role(unit_type: str) -> str:
        return {
            "decision": "proposer",
            "task": "assignee",
            "risk": "raiser",
            "question": "asker",
        }.get(unit_type, "speaker")

    @staticmethod
    def unit_confidence(unit_type: str) -> float:
        return 0.82 if unit_type in {"question", "decision", "task", "risk"} else 0.68

    @staticmethod
    def relation_for_actor(unit_type: str, actor_id: str, unit_id: str, source_refs: list[dict[str, Any]]) -> dict[str, Any]:
        relation_type = {
            "question": "actor_asked_question",
            "decision": "actor_proposed_decision",
            "task": "actor_accepted_task",
            "risk": "actor_raised_risk",
        }.get(unit_type, "actor_made_statement")
        return {
            "source": f"actor:{actor_id}",
            "target": f"unit:{unit_id}",
            "type": relation_type,
            "weight": 0.91,
            "source_refs": source_refs,
        }

    @staticmethod
    def extract_topics(text: str) -> list[str]:
        candidates = []
        for token in ["发布计划", "最终验收", "验收", "测试", "风险", "任务", "需求", "预算", "客户", "排期"]:
            if token in text:
                candidates.append(token)
        if not candidates:
            cn = re.findall(r"[\u4e00-\u9fff]{2,6}", text)
            candidates.extend(cn[:2])
        return list(dict.fromkeys(candidates))[:5]

    @staticmethod
    def extract_entities(text: str, actors: dict[str, dict[str, Any]]) -> list[str]:
        entities = []
        for actor in actors.values():
            label = str(actor.get("label") or "")
            if label and label in text:
                entities.append(label)
        for token in re.findall(r"[A-Za-z][A-Za-z0-9_.+-]{1,}|[\u4e00-\u9fff]{2,8}", text):
            if token not in {"我们", "这个", "下周一", "今天", "明天"}:
                entities.append(token)
        return list(dict.fromkeys(entities))[:8]

    @staticmethod
    def pairwise(items: list[str]) -> list[tuple[str, str]]:
        pairs = []
        for index, left in enumerate(items):
            for right in items[index + 1:]:
                if left != right:
                    pairs.append((left, right))
        return pairs

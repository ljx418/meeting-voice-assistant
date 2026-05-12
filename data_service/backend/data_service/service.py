"""Current implementation carrier for the local knowledge governance service."""

import json
import math
import re
import shutil
import uuid
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Set, Union

from .adapters import AdapterResult, GraphRAGAdapter, LLMWikiAdapter
from .default_adapters import GraphRAGWorkspaceAdapter, LLMWikiEngineAdapter
from .models import (
    ArtifactLayout,
    AuthorityLevel,
    DistilledUnit,
    DistilledUnitKind,
    EngineTarget,
    GraphExecutionOwner,
    IngestPlan,
    QueryHit,
    QueryMode,
    QueryResponse,
    SourceEnvelope,
)
from app.llmwiki.config import LLMWikiConfig
from app.llmwiki.engine import WikiEngine
from app.llmwiki.dotenv_support import load_llmwiki_dotenv
from app.llmwiki.llm_client import LLMClientError, build_llm_client


class DataService:
    """Knowledge Governance Service implementation boundary.

    This service exposes the local data-governance boundary used by MCP, CLI,
    and HTTP. It does not own meeting, learning, interview, code-assistant, or
    other upstream application workflows.

    This layer does not reimplement llmwiki or graphrag internals.
    It owns:
    - workspace artifact layout
    - source ingest planning
    - distill-layer policy
    - retrieval/query aggregation
    - quality governance artifacts
    - operator-facing workspace summaries
    """

    DEFAULT_STAGES = [
        "row",
        "extract",
        "normalize",
        "distill",
        "llmwiki_compile",
        "graphrag_index",
        "summary",
    ]
    SUPPORTED_SOURCE_SUFFIXES = {
        ".md", ".markdown", ".txt", ".text",
        ".csv", ".json",
        ".pdf", ".pptx", ".ppt",
        ".html", ".htm", ".docx", ".yaml", ".yml",
    }
    TITLE_MARKER_PATTERNS = [
        (re.compile(r"[-_\s]*(废弃于\d{4,}|废弃于|已废弃|归档|临时版?|tmp)\b", re.IGNORECASE), "status_marker"),
        (re.compile(r"[-_\s]*(v?\d{6,}|20\d{6,})\b", re.IGNORECASE), "date_marker"),
    ]
    ENTITY_STOPWORDS = {
        "废弃于", "学习", "使用", "注意事项", "注意", "事项", "流程图", "根据", "现在", "需要",
        "建库", "指南", "说明", "记录", "问题", "内容", "方案", "某个", "以及", "相关", "安装",
        "技术咨询", "学习废弃于", "技术咨询废弃于", "conversation", "source", "general",
        "question", "conclusion", "note", "topic", "步骤", "方法", "分析", "解析", "研究",
        "认证", "已安装", "选项验证", "含义", "配置微信飞书", "国内", "免费", "介绍", "app", "user",
        "背景介绍", "复态",
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
    LOW_SIGNAL_SENTENCE_PATTERNS = [
        re.compile(r"^(你好|您好|谢谢|好的|嗯|哦|哈喽|hi|hello)[!！。.\s]*$", re.IGNORECASE),
        re.compile(r"^(可以|行|没问题|收到|明白了)[!！。.\s]*$", re.IGNORECASE),
        re.compile(r"^(请继续|继续|展开说说|详细说说)[!！。.\s]*$", re.IGNORECASE),
    ]
    TITLE_QUESTION_HINTS = (
        "区别", "用途", "建议", "选择", "原因", "时间", "数据", "进展", "来源", "概念",
        "特点", "解析", "对比", "说明", "方法", "流程", "含义", "作用", "岗位", "名称来源",
        "推荐", "年限", "宜居", "确保", "充足", "案例", "注意事项", "评价", "专利", "应用",
        "clarification", "term",
    )
    TITLE_ENTITY_SPLIT_PATTERN = re.compile(r"[与和、/&]|及(?![并其])")
    TITLE_ENTITY_SUFFIX_PATTERNS = [
        re.compile(r"(应用)?创新点(?:与专利技术点)?$"),
        re.compile(r"(?:app|应用)?跨端协作技术专利方案$", re.IGNORECASE),
        re.compile(r"(?:专利技术点|专利方案|专利技术|技术专利|技术点)$"),
        re.compile(r"(?:跨端协作技术)$"),
        re.compile(r"(?:玻璃)?防晒性能$"),
        re.compile(r"(?:上市|小组赛)$"),
        re.compile(r"(?:选项验证|自动化测试代码示例|自动化测试|测试代码示例|代码示例)$"),
        re.compile(r"(?:股权结构及背景介绍|股权结构|背景介绍)$"),
        re.compile(r"(?:实践移植案例|移植案例|案例)$"),
        re.compile(r"(?:看望老人注意事项|注意事项)$"),
        re.compile(r"(?:相关)$"),
        re.compile(r"(?:专利)$"),
        re.compile(r"(?:及其在.+中的应用)$"),
    ]
    TITLE_NORMALIZATION_NOISE_FRAGMENTS = [
        "已安装",
        "选项验证",
        "自动化测试代码示例",
        "测试代码示例",
        "代码示例",
        "自动化测试",
        "股权结构",
        "背景介绍",
        "玻璃防晒性能",
        "中的多态与复态",
        "解析",
    ]
    HIGH_DENSITY_THRESHOLD = 2.2
    DISTILL_SCHEMA_VERSION = "1.2"
    TYPED_DISTILL_UNIT_SCHEMA_VERSION = "typed-distill-unit-1.2"
    ENGINE_INPUT_CONTRACT_VERSION = "1.0"
    GRAPH_QUERY_MODEL_VERSION = "1.0"
    DEFAULT_GRAPH_EXECUTION_OWNER = GraphExecutionOwner.APP_GRAPHRAG
    LLMWIKI_ALLOWED_UNIT_KINDS = {
        DistilledUnitKind.TOPIC_CANDIDATE,
        DistilledUnitKind.QUESTION,
        DistilledUnitKind.CONCLUSION,
        DistilledUnitKind.STEP,
        DistilledUnitKind.NOTE,
        DistilledUnitKind.RISK,
        DistilledUnitKind.EXAMPLE,
    }
    GRAPHRAG_ALLOWED_UNIT_KINDS = {
        DistilledUnitKind.TOPIC_CANDIDATE,
        DistilledUnitKind.ENTITY_CANDIDATE,
        DistilledUnitKind.CONCLUSION,
        DistilledUnitKind.NOTE,
        DistilledUnitKind.QUESTION,
        DistilledUnitKind.STEP,
        DistilledUnitKind.RELATION_CANDIDATE,
        DistilledUnitKind.FACT_CANDIDATE,
        DistilledUnitKind.RISK,
        DistilledUnitKind.EXAMPLE,
    }
    LEGACY_KIND_TO_TYPED_UNIT_TYPE = {
        DistilledUnitKind.TOPIC_CANDIDATE.value: "concept",
        DistilledUnitKind.QUESTION.value: "question",
        DistilledUnitKind.CONCLUSION.value: "claim",
        DistilledUnitKind.STEP.value: "workflow",
        DistilledUnitKind.EXAMPLE.value: "example",
        DistilledUnitKind.NOTE.value: "meeting_summary",
        DistilledUnitKind.RISK.value: "risk",
        DistilledUnitKind.FACT_CANDIDATE.value: "fact",
        DistilledUnitKind.ENTITY_CANDIDATE.value: "entity_evidence",
        DistilledUnitKind.RELATION_CANDIDATE.value: "relation_evidence",
    }
    EXTRA_TYPED_UNIT_TYPES = {
        "architecture_note",
        "code_symbol",
        "code_dependency",
        "code_call_edge",
    }

    def __init__(self, workspace: Path):
        self.workspace = Path(workspace).resolve()
        self.layout = ArtifactLayout.from_workspace(self.workspace)
        load_llmwiki_dotenv()

    def ensure_layout(self) -> ArtifactLayout:
        self.layout.ensure_directories()
        return self.layout

    def build_ingest_plan(
        self,
        paths: Iterable[str],
        *,
        include_llmwiki: bool = True,
        include_graphrag: bool = True,
        graphrag_execution_owner: Union[GraphExecutionOwner, str] = DEFAULT_GRAPH_EXECUTION_OWNER,
    ) -> IngestPlan:
        """Create a single-write, dual-engine ingest plan."""
        expanded_paths = self._expand_source_paths(paths)
        sources = [SourceEnvelope(path=str(path)) for path in expanded_paths]
        targets: List[EngineTarget] = []
        if include_llmwiki:
            targets.append(EngineTarget.LLMWIKI)
        if include_graphrag:
            targets.append(EngineTarget.GRAPHRAG)
        execution_owner = GraphExecutionOwner(graphrag_execution_owner)

        notes = [
            "Users write data once; internal processing fans out after normalize/distill.",
            "LLMWiki consumes readable and distilled material for compilation and provenance.",
            "GraphRAG consumes distilled, high-information units rather than raw fulltext by default.",
            f"GraphRAG execution owner: {execution_owner.value}.",
        ]
        policy = {
            "raw_ingest_mode": "single_write",
            "shared_extract_normalize": True,
            "graphrag_prefers_distill": True,
            "llmwiki_prefers_readable_and_distill": True,
            "secondary_chat_enters_unverified": True,
        }

        return IngestPlan(
            workspace=self.workspace,
            layout=self.layout,
            sources=sources,
            targets=targets,
            stages=list(self.DEFAULT_STAGES),
            graphrag_execution_owner=execution_owner,
            distill_policy=policy,
            notes=notes,
        )

    def reset_workspace(self, confirmation: str) -> Dict[str, Any]:
        """Delete only data_service-managed artifacts inside the workspace."""
        if confirmation != "Delete":
            raise ValueError("Confirmation token mismatch. Type 'Delete' to reset the workspace.")

        self.ensure_layout()
        removed: List[str] = []
        managed_paths = [
            self.layout.distill_dir,
            self.layout.llmwiki_dir,
            self.layout.graphrag_dir,
            self.layout.summary_dir,
            self.layout.quality_dir,
            self.layout.row_manifest,
            self.workspace / "llmwiki.db",
            self.workspace / "llmwiki_markdown",
            self.workspace / "llmwiki_vault",
            self.workspace / "summary.md",
            self.workspace / "summary.json",
        ]

        for path in managed_paths:
            resolved = path.resolve()
            try:
                resolved.relative_to(self.workspace)
            except ValueError:
                continue
            if not resolved.exists():
                continue
            if resolved.is_dir():
                shutil.rmtree(resolved)
            else:
                resolved.unlink()
            removed.append(str(resolved))

        self.ensure_layout()
        self.write_summary_files(self.build_ingest_plan([]))
        return {
            "workspace": str(self.workspace),
            "removed": removed,
            "row_preserved": True,
        }

    def render_architecture_markdown(self, plan: Optional[IngestPlan] = None) -> str:
        """Render a human-readable summary for operators."""
        plan = plan or self.build_ingest_plan([])
        targets = ", ".join(target.value for target in plan.targets) or "none"
        stage_lines = "\n".join(f"- {stage}" for stage in plan.stages)
        note_lines = "\n".join(f"- {note}" for note in plan.notes)
        return "\n".join(
            [
                "# Data Service Summary",
                "",
                "## Positioning",
                "",
                "- `data_service` is the upstream orchestration layer above `llmwiki` and `graphrag`.",
                "- `llmwiki` focuses on compilation, readability, provenance, and local browsing.",
                "- `graphrag` focuses on entity/relation indexing and graph-based reasoning.",
                "",
                "## Ingest Policy",
                "",
                "- Single user write: yes",
                "- Shared extract/normalize: yes",
                "- Distill before GraphRAG: yes",
                f"- Targets: {targets}",
                "",
                "## Stages",
                "",
                stage_lines or "- none",
                "",
                "## Artifact Layout",
                "",
                f"- row manifest: `{plan.layout.row_manifest}`",
                f"- raw: `{plan.layout.raw_dir}`",
                f"- readable: `{plan.layout.readable_dir}`",
                f"- normalized: `{plan.layout.normalized_dir}`",
                f"- distill: `{plan.layout.distill_dir}`",
                f"- distill sources: `{plan.layout.distill_sources_dir}`",
                f"- distill units: `{plan.layout.distill_units_dir}`",
                f"- distill manifest: `{plan.layout.distill_manifest}`",
                f"- distill schema: `{plan.layout.distill_schema}`",
                f"- llmwiki pages: `{plan.layout.llmwiki_pages_dir}`",
                f"- graphrag input: `{plan.layout.graphrag_input_dir}`",
                f"- graphrag state: `{plan.layout.graphrag_state_dir}`",
                f"- graphrag execution owner: `{plan.graphrag_execution_owner.value}`",
                f"- summary dir: `{plan.layout.summary_dir}`",
                f"- summary.md: `{plan.layout.summary_md}`",
                f"- summary.json: `{plan.layout.summary_json}`",
                f"- quality feedback: `{plan.layout.quality_feedback_jsonl}`",
                f"- correction rules: `{plan.layout.quality_correction_rules_json}`",
                f"- correction plan: `{plan.layout.quality_correction_plan_json}`",
                "",
                "## Notes",
                "",
                note_lines or "- none",
                "",
            ]
        )

    def write_summary_files(self, plan: Optional[IngestPlan] = None) -> None:
        """Persist operator-facing summary files."""
        plan = plan or self.build_ingest_plan([])
        self.ensure_layout()
        self.layout.summary_md.write_text(self.render_architecture_markdown(plan), encoding="utf-8")
        quality = self._build_quality_summary()
        summary_payload = {
            "workspace": str(plan.workspace),
            "targets": [target.value for target in plan.targets],
            "stages": plan.stages,
            "distill_policy": plan.distill_policy,
            "distill_schema_version": self.DISTILL_SCHEMA_VERSION,
            "sources": [source.path for source in plan.sources],
            "quality": quality,
            "layout": {
                "row_manifest": str(plan.layout.row_manifest),
                "raw": str(plan.layout.raw_dir),
                "readable": str(plan.layout.readable_dir),
                "normalized": str(plan.layout.normalized_dir),
                "distill": str(plan.layout.distill_dir),
                "distill_sources": str(plan.layout.distill_sources_dir),
                "distill_units": str(plan.layout.distill_units_dir),
                "distill_manifest": str(plan.layout.distill_manifest),
                "distill_schema": str(plan.layout.distill_schema),
                "llmwiki_pages": str(plan.layout.llmwiki_pages_dir),
                "graphrag_input": str(plan.layout.graphrag_input_dir),
                "graphrag_state": str(plan.layout.graphrag_state_dir),
                "summary_dir": str(plan.layout.summary_dir),
                "summary_md": str(plan.layout.summary_md),
                "summary_json": str(plan.layout.summary_json),
                "quality_dir": str(plan.layout.quality_dir),
                "quality_feedback": str(plan.layout.quality_feedback_jsonl),
                "quality_correction_rules": str(plan.layout.quality_correction_rules_json),
                "quality_correction_plan": str(plan.layout.quality_correction_plan_json),
            },
            "notes": plan.notes,
        }
        self.layout.summary_json.write_text(json.dumps(summary_payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    def read_summary_bundle(self) -> Dict[str, Any]:
        """Return frontend-friendly workspace summary data."""
        if not self.layout.summary_md.exists() or not self.layout.summary_json.exists():
            plan = self.build_ingest_plan([])
            self.write_summary_files(plan)
        summary_markdown = self.layout.summary_md.read_text(encoding="utf-8") if self.layout.summary_md.exists() else ""
        summary_json = {}
        if self.layout.summary_json.exists():
            try:
                summary_json = json.loads(self.layout.summary_json.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                summary_json = {}

        llmwiki_pages = []
        if self.layout.llmwiki_pages_dir.exists():
            for page_path in sorted(self.layout.llmwiki_pages_dir.glob("*.md"), key=lambda item: item.stat().st_mtime, reverse=True)[:12]:
                llmwiki_pages.append(
                    {
                        "slug": page_path.stem,
                        "title": self._extract_markdown_title(page_path),
                        "path": str(page_path),
                        "updated_at": page_path.stat().st_mtime,
                    }
                )

        graph_snapshot = self.get_graph_snapshot(max_nodes=80)
        return {
            "workspace": str(self.workspace),
            "summary_markdown": summary_markdown,
            "summary_json": summary_json,
            "quality": summary_json.get("quality", {}),
            "llmwiki_pages": llmwiki_pages,
            "graph_stats": graph_snapshot["stats"],
            "graph_preview": {
                "communities": graph_snapshot["communities"][:8],
                "nodes": graph_snapshot["nodes"][:20],
                "edges": graph_snapshot["edges"][:20],
            },
            "quality_feedback": self.read_quality_feedback(limit=20)["items"],
            "quality_correction_rules": self.read_quality_correction_rules(limit=20)["items"],
            "quality_correction_plan": self.read_quality_correction_plan(build_if_missing=False),
        }

    def record_quality_feedback(
        self,
        *,
        target_type: str,
        target_id: str,
        action: str,
        label: str = "",
        suggested_value: str = "",
        reason: str = "",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Persist an operator quality signal without mutating source data."""
        self.ensure_layout()
        target_type = str(target_type).strip()
        target_id = str(target_id).strip()
        action = str(action).strip()
        label = str(label or "").strip()
        suggested_value = str(suggested_value or "").strip()
        reason = str(reason or "").strip()
        if not target_type:
            raise ValueError("target_type is required")
        if not target_id:
            raise ValueError("target_id is required")
        if not action:
            raise ValueError("action is required")

        now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        record = {
            "feedback_id": uuid.uuid4().hex[:12],
            "created_at": now,
            "workspace": str(self.workspace),
            "target_type": target_type,
            "target_id": target_id,
            "action": action,
            "label": label,
            "suggested_value": suggested_value,
            "reason": reason,
            "metadata": dict(metadata or {}),
        }
        with self.layout.quality_feedback_jsonl.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")
        self.build_quality_correction_rules()
        return record

    def build_quality_correction_rules(self) -> Dict[str, Any]:
        """Build draft correction rules from manual feedback signals."""
        self.ensure_layout()
        feedback_records = self._read_jsonl_all(self.layout.quality_feedback_jsonl)
        existing_payload = self._read_json_file(self.layout.quality_correction_rules_json)
        existing_rules = {
            str(rule.get("source_feedback_id", "")).strip(): rule
            for rule in list(existing_payload.get("rules", []) or [])
            if str(rule.get("source_feedback_id", "")).strip()
        }
        rules: List[Dict[str, Any]] = []
        for record in feedback_records:
            rule = self._feedback_to_correction_rule(record)
            if not rule:
                continue
            existing_rule = existing_rules.get(str(rule.get("source_feedback_id", "")).strip())
            if existing_rule:
                for key in ("status", "reviewed_at", "reviewer", "review_note"):
                    if existing_rule.get(key):
                        rule[key] = existing_rule[key]
            rules.append(rule)
        payload = {
            "schema_version": "1.0",
            "workspace": str(self.workspace),
            "generated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "source_feedback_count": len(feedback_records),
            "rules": rules,
            "summary": self._build_correction_rules_summary(rules),
        }
        self._write_quality_correction_rules_payload(payload)
        self.write_summary_files(self.build_ingest_plan([]))
        return payload

    def read_quality_correction_rules(self, *, limit: int = 100, status: Optional[str] = None) -> Dict[str, Any]:
        """Return draft correction rules derived from manual feedback."""
        self.ensure_layout()
        limit = max(1, min(int(limit), 500))
        payload = self._read_json_file(self.layout.quality_correction_rules_json)
        if not payload:
            payload = self.build_quality_correction_rules()
        status_filter = str(status).strip() if status else ""
        rules = list(payload.get("rules", []) or [])
        filtered = [rule for rule in rules if not status_filter or rule.get("status") == status_filter]
        return {
            "workspace": str(self.workspace),
            "rules_path": str(self.layout.quality_correction_rules_json),
            "items": filtered[:limit],
            "total_count": len(rules),
            "filtered_count": len(filtered),
            "summary": self._build_correction_rules_summary(rules),
            "generated_at": payload.get("generated_at", ""),
            "schema_version": payload.get("schema_version", "1.0"),
        }

    def review_quality_correction_rule(
        self,
        *,
        rule_id: str,
        status: str,
        reviewer: str = "",
        note: str = "",
    ) -> Dict[str, Any]:
        """Update the review status of one correction rule without applying it."""
        self.ensure_layout()
        rule_id = str(rule_id).strip()
        status = str(status).strip()
        reviewer = str(reviewer or "").strip()
        note = str(note or "").strip()
        allowed_statuses = {"draft", "approved", "rejected", "archived", "revoked"}
        if not rule_id:
            raise ValueError("rule_id is required")
        if status not in allowed_statuses:
            raise ValueError(f"Unsupported status: {status}")

        payload = self._read_json_file(self.layout.quality_correction_rules_json)
        if not payload:
            payload = self.build_quality_correction_rules()
        rules = list(payload.get("rules", []) or [])
        matched_rule = None
        now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        for rule in rules:
            if str(rule.get("rule_id", "")).strip() != rule_id:
                continue
            rule["status"] = status
            rule["reviewed_at"] = now
            rule["reviewer"] = reviewer
            rule["review_note"] = note
            matched_rule = rule
            break
        if matched_rule is None:
            raise ValueError(f"Unknown correction rule: {rule_id}")

        payload["generated_at"] = payload.get("generated_at") or now
        payload["updated_at"] = now
        payload["rules"] = rules
        payload["summary"] = self._build_correction_rules_summary(rules)
        self._write_quality_correction_rules_payload(payload)
        correction_plan = self.build_quality_correction_plan()
        return {
            "workspace": str(self.workspace),
            "rules_path": str(self.layout.quality_correction_rules_json),
            "rule": matched_rule,
            "summary": payload["summary"],
            "correction_plan": {
                "summary": correction_plan.get("summary", {}),
                "source_rule_count": correction_plan.get("source_rule_count", 0),
            },
        }

    def build_quality_correction_plan(self) -> Dict[str, Any]:
        """Convert approved correction rules into an engine consumption plan."""
        self.ensure_layout()
        rules_payload = self._read_json_file(self.layout.quality_correction_rules_json)
        if not rules_payload:
            rules_payload = self.build_quality_correction_rules()
        approved_rules = [
            rule for rule in list(rules_payload.get("rules", []) or [])
            if rule.get("status") == "approved"
        ]
        actions = [self._correction_rule_to_plan_action(rule) for rule in approved_rules]
        actions = [action for action in actions if action]
        actions = self._attach_correction_plan_impacts(actions)
        payload = {
            "schema_version": "1.0",
            "workspace": str(self.workspace),
            "generated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "source_rule_count": len(approved_rules),
            "actions": actions,
            "summary": self._build_correction_plan_summary(actions),
            "notes": [
                "Only approved rules are included.",
                "The plan is a non-destructive governance layer; raw row data and engine artifacts are not rewritten.",
                "Graph snapshots apply presentation suppress/rename/merge actions at read time.",
            ],
        }
        self.layout.quality_correction_plan_json.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        self.write_summary_files(self.build_ingest_plan([]))
        return payload

    def read_quality_correction_plan(self, *, build_if_missing: bool = True) -> Dict[str, Any]:
        """Return the latest approved-rule consumption plan."""
        self.ensure_layout()
        payload = self._read_json_file(self.layout.quality_correction_plan_json)
        if not payload and build_if_missing:
            payload = self.build_quality_correction_plan()
        return payload or {
            "schema_version": "1.0",
            "workspace": str(self.workspace),
            "generated_at": "",
            "source_rule_count": 0,
            "actions": [],
            "summary": self._build_correction_plan_summary([]),
            "notes": ["No approved correction plan has been generated yet."],
        }

    def apply_quality_plan_to_llmwiki_markdown_files(self) -> Dict[str, Any]:
        """Apply approved correction plan display rules to generated LLMWiki markdown files."""
        self.ensure_layout()
        policy = self._build_quality_plan_policy("llmwiki")
        if not policy["applied_actions"] or not self.layout.llmwiki_pages_dir.exists():
            return {
                "workspace": str(self.workspace),
                "status": "skipped",
                "reason": "no_llmwiki_quality_actions",
                "updated_pages": [],
                "updated_count": 0,
            }

        updated_pages: List[Dict[str, Any]] = []
        page_paths = sorted(self.layout.llmwiki_pages_dir.glob("*.md"))
        page_titles: Dict[Path, str] = {page_path: self._extract_markdown_title(page_path) for page_path in page_paths}
        for page_path in page_paths:
            try:
                original_body = page_path.read_text(encoding="utf-8")
            except OSError:
                continue
            title = page_titles.get(page_path, page_path.stem)
            suppressed = self._quality_policy_matches(policy, page_path.stem, title, original_body)
            rewritten_body = self._apply_quality_policy_to_text(original_body, policy)
            if suppressed and "<!-- quality_suppressed: true -->" not in rewritten_body:
                rewritten_body = "<!-- quality_suppressed: true -->\n" + rewritten_body
            merge_target = self._quality_policy_merge_replacement(policy, page_path.stem, title)
            canonical_path = self._find_llmwiki_canonical_page_path(
                page_paths,
                page_titles,
                merge_target,
                exclude_path=page_path,
            )
            if merge_target and canonical_path:
                rewritten_body = self._build_merged_llmwiki_page_body(rewritten_body, merge_target)
                self._append_llmwiki_merged_topic_signal(canonical_path, title, page_path.stem, original_body)
            if rewritten_body == original_body:
                continue
            page_path.write_text(rewritten_body, encoding="utf-8")
            updated_pages.append(
                {
                    "slug": page_path.stem,
                    "title": self._apply_quality_policy_to_text(title, policy),
                    "path": str(page_path),
                    "quality_suppressed": suppressed,
                    "quality_merged_into": merge_target if canonical_path else "",
                }
            )

        return {
            "workspace": str(self.workspace),
            "status": "applied",
            "updated_pages": updated_pages,
            "updated_count": len(updated_pages),
            "applied_action_count": len(policy["applied_actions"]),
        }

    def _find_llmwiki_canonical_page_path(
        self,
        page_paths: List[Path],
        page_titles: Dict[Path, str],
        title: str,
        *,
        exclude_path: Path,
    ) -> Optional[Path]:
        title = str(title or "").strip()
        if not title:
            return None
        canonical_slug = self._simple_slug(title)
        for page_path in page_paths:
            if page_path == exclude_path:
                continue
            page_title = str(page_titles.get(page_path, "")).strip()
            if page_title == title or page_path.stem == canonical_slug:
                return page_path
        return None

    @classmethod
    def _build_merged_llmwiki_page_body(cls, body: str, merge_target: str) -> str:
        marker = f"<!-- quality_merged_into: {merge_target} -->"
        if marker in body:
            return body
        notice = "\n".join(
            [
                marker,
                f"> This page has been merged into [[{merge_target}]] by an approved quality rule.",
                "",
            ]
        )
        return notice + body

    def _append_llmwiki_merged_topic_signal(self, canonical_path: Path, source_title: str, source_slug: str, source_body: str) -> None:
        try:
            canonical_body = canonical_path.read_text(encoding="utf-8")
        except OSError:
            return
        marker = f"<!-- quality_merge_source: {source_slug} -->"
        if marker in canonical_body:
            return
        excerpt = self._summarize_markdown_for_merge(source_body)
        section = "\n".join(
            [
                "",
                "## Merged Topic Signals",
                "",
                marker,
                f"- From [[{source_slug}|{source_title}]]: {excerpt}",
                "",
            ]
        )
        canonical_path.write_text(canonical_body.rstrip() + "\n\n" + section, encoding="utf-8")

    @staticmethod
    def _summarize_markdown_for_merge(body: str) -> str:
        for line in str(body or "").splitlines():
            stripped = line.strip()
            if not stripped or stripped.startswith("#") or stripped.startswith("<!--"):
                continue
            return stripped[:240]
        return "Merged by approved quality rule."

    @staticmethod
    def _simple_slug(text: str) -> str:
        slug = str(text or "").strip().lower().replace(" ", "-")
        return "".join(char for char in slug if char.isalnum() or char in "-_")[:80]

    def read_quality_feedback(
        self,
        *,
        limit: int = 100,
        target_type: Optional[str] = None,
        target_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Return recent operator feedback records and aggregate counts."""
        self.ensure_layout()
        limit = max(1, min(int(limit), 500))
        target_type_filter = str(target_type).strip() if target_type else ""
        target_id_filter = str(target_id).strip() if target_id else ""
        records = self._read_jsonl_all(self.layout.quality_feedback_jsonl)
        filtered = [
            record for record in records
            if (not target_type_filter or record.get("target_type") == target_type_filter)
            and (not target_id_filter or record.get("target_id") == target_id_filter)
        ]
        recent = list(reversed(filtered))[:limit]
        summary = self._build_manual_feedback_summary(records)
        return {
            "workspace": str(self.workspace),
            "feedback_path": str(self.layout.quality_feedback_jsonl),
            "items": recent,
            "total_count": len(records),
            "filtered_count": len(filtered),
            "summary": summary,
        }

    def read_distill_bundle(
        self,
        *,
        source_id: Optional[str] = None,
        limit: int = 20,
        kind: Optional[str] = None,
        typed_unit_type: Optional[str] = None,
        min_importance: float = 0.0,
        llm_enriched_only: bool = False,
        authority: Optional[str] = None,
        min_source_weight: float = 0.0,
        min_source_density: float = 0.0,
    ) -> Dict[str, Any]:
        """Return frontend/CLI-friendly distill preview data."""
        self.ensure_layout()
        limit = max(1, min(int(limit), 200))
        kind = str(kind).strip() if kind else None
        typed_unit_type = str(typed_unit_type).strip() if typed_unit_type else None
        authority = str(authority).strip() if authority else None
        min_importance = max(0.0, float(min_importance))
        min_source_weight = max(0.0, float(min_source_weight))
        min_source_density = max(0.0, float(min_source_density))
        manifest = self._read_json_file(self.layout.distill_manifest) or {}
        schema = self._read_json_file(self.layout.distill_schema) or {}

        sources = manifest.get("sources", []) or []
        if not sources and self.layout.distill_sources_dir.exists():
            recovered_sources: List[Dict[str, Any]] = []
            for source_path in sorted(self.layout.distill_sources_dir.glob("*.json")):
                source_record = self._read_json_file(source_path) or {}
                if not source_record:
                    continue
                recovered_sources.append(
                    {
                        "source_id": source_record.get("source_id", source_path.stem),
                        "path": source_record.get("path", ""),
                        "source_format": source_record.get("source_format", ""),
                        "extractor_name": source_record.get("extractor_name", ""),
                        "extractor_available": bool(source_record.get("extractor_available", False)),
                        "authority": source_record.get("authority", ""),
                        "unit_count": len(source_record.get("units", []) or []),
                        "source_weight": source_record.get("source_weight", 1.0),
                        "source_density_score": source_record.get("source_density_score", 1.0),
                        "title": source_record.get("title", source_path.stem),
                        "title_flags": source_record.get("title_flags", []),
                        "llm_enriched": bool(source_record.get("llm_enriched", False)),
                        "distill_path": str(source_path),
                        "profile": source_record.get("profile", {}),
                        "unit_kind_counts": source_record.get("unit_kind_counts", {}),
                        "typed_unit_type_counts": source_record.get("typed_unit_type_counts", {}),
                    }
                )
            sources = recovered_sources
            if not manifest:
                manifest = {
                    "schema_version": schema.get("schema_version", self.DISTILL_SCHEMA_VERSION),
                    "workspace": str(self.workspace),
                    "source_count": len(sources),
                    "distilled_unit_count": sum(int(source.get("unit_count", 0)) for source in sources),
                    "sources": sources,
                    "units_path": str(self.layout.distill_units_dir / "distilled_units.jsonl"),
                    "recovered_from_sources_dir": True,
                }
        source_payload = None
        units: List[Dict[str, Any]] = []

        if source_id:
            source_payload = next((source for source in sources if source.get("source_id") == source_id), None)
            if source_payload:
                source_distill_path = self.layout.distill_sources_dir / f"{source_id}.json"
                source_record = self._read_json_file(source_distill_path) or {}
                source_payload = {
                    **source_payload,
                    "record": source_record,
                    "profile_debug": source_record.get("profile_debug", {}),
                    "provenance_summary": self._build_provenance_summary(source_record.get("units", [])),
                    "units_by_kind": self._group_units_by_kind(source_record.get("units", [])),
                    "top_units": self._select_top_units(source_record.get("units", []), limit=min(8, limit)),
                }
                units = self._filter_distill_units(
                    list(source_record.get("units", [])),
                    kind=kind,
                    typed_unit_type=typed_unit_type,
                    min_importance=min_importance,
                    llm_enriched_only=llm_enriched_only,
                    authority=authority,
                    min_source_weight=min_source_weight,
                    min_source_density=min_source_density,
                    limit=limit,
                )
        else:
            units = self._filter_distill_units(
                self._read_jsonl_preview(self.layout.distill_units_dir / "distilled_units.jsonl", limit=max(limit * 8, limit)),
                kind=kind,
                typed_unit_type=typed_unit_type,
                min_importance=min_importance,
                llm_enriched_only=llm_enriched_only,
                authority=authority,
                min_source_weight=min_source_weight,
                min_source_density=min_source_density,
                limit=limit,
            )

        return {
            "workspace": str(self.workspace),
            "schema_version": manifest.get("schema_version", self.DISTILL_SCHEMA_VERSION),
            "manifest": manifest,
            "schema": schema,
            "sources": sources[:limit],
            "source_profiles": self._build_source_profiles_preview(sources, limit=min(limit, 12)),
            "source": source_payload,
            "units": units,
            "available_source_count": len(sources),
            "provenance_overview": self._build_provenance_overview(sources, units),
            "filters": {
                "kind": kind,
                "typed_unit_type": typed_unit_type,
                "min_importance": min_importance,
                "llm_enriched_only": llm_enriched_only,
                "authority": authority,
                "min_source_weight": min_source_weight,
                "min_source_density": min_source_density,
            },
        }

    def _build_source_profiles_preview(self, sources: List[Dict[str, Any]], *, limit: int) -> List[Dict[str, Any]]:
        preview: List[Dict[str, Any]] = []
        for source in sources[:limit]:
            source_id = str(source.get("source_id", "")).strip()
            source_record = self._read_json_file(self.layout.distill_sources_dir / f"{source_id}.json") or {}
            preview.append(
                {
                    "source_id": source_id,
                    "title": source.get("title", source_id),
                    "source_format": source.get("source_format", ""),
                    "extractor_name": source.get("extractor_name", ""),
                    "extractor_available": bool(source.get("extractor_available", False)),
                    "authority": source.get("authority"),
                    "source_weight": source.get("source_weight", 1.0),
                    "source_density_score": source.get("source_density_score", 1.0),
                    "title_flags": list(source.get("title_flags", []) or []),
                    "unit_count": int(source.get("unit_count", 0)),
                    "unit_kind_counts": dict(source.get("unit_kind_counts", {}) or {}),
                    "typed_unit_type_counts": dict(source.get("typed_unit_type_counts", {}) or {}),
                    "profile": dict(source.get("profile", {}) or {}),
                    "low_signal": dict(source.get("low_signal", {}) or source_record.get("profile", {}).get("low_signal", {}) or {}),
                    "profile_debug": dict(source_record.get("profile_debug", {}) or {}),
                    "distill_path": source.get("distill_path"),
                }
            )
        return preview

    @classmethod
    def _build_low_signal_diagnostics(
        cls,
        *,
        title: str,
        title_only_excerpt: bool,
        source_profile: Dict[str, Any],
        source_units: List[DistilledUnit],
        entity_candidates: List[str],
        theme_labels: List[str],
        title_fallbacks: Dict[str, bool],
    ) -> Dict[str, Any]:
        unit_count = len(source_units)
        reasons: List[str] = []
        if unit_count == 0:
            if not entity_candidates:
                reasons.append("no_entity_candidates")
            if not theme_labels:
                reasons.append("no_theme_labels")
            if title_only_excerpt:
                reasons.append("title_only_without_semantic_fallback")
            if not any(title_fallbacks.values()):
                reasons.append("no_safe_title_fallback")
            if int(source_profile.get("sentence_count", 0) or 0) <= 1:
                reasons.append("no_content_sentences")
            if float(source_profile.get("density_score", 0.0) or 0.0) < 0.6:
                reasons.append("low_density_source")
        elif title_only_excerpt:
            reasons.append("title_only_conservatively_covered")

        return {
            "zero_unit": unit_count == 0,
            "unit_count": unit_count,
            "title": title,
            "title_only_excerpt": bool(title_only_excerpt),
            "sentence_count": int(source_profile.get("sentence_count", 0) or 0),
            "density_score": float(source_profile.get("density_score", 0.0) or 0.0),
            "source_weight": float(source_profile.get("source_weight", 0.0) or 0.0),
            "entity_candidate_count": len(entity_candidates),
            "theme_label_count": len(theme_labels),
            "title_fallbacks": dict(title_fallbacks),
            "reasons": reasons,
        }

    @classmethod
    def _build_distill_manifest_quality(cls, sources: List[Dict[str, Any]]) -> Dict[str, Any]:
        zero_unit_sources: List[Dict[str, Any]] = []
        reason_counts: Dict[str, int] = defaultdict(int)
        title_fallback_source_counts: Dict[str, int] = defaultdict(int)
        title_only_covered_count = 0
        format_counts: Dict[str, int] = defaultdict(int)
        extractor_counts: Dict[str, int] = defaultdict(int)
        format_issue_sources: List[Dict[str, Any]] = []
        for source in sources:
            source_format = str(source.get("source_format") or "").strip() or "unknown"
            extractor_name = str(source.get("extractor_name") or "").strip() or "unknown"
            format_counts[source_format] += 1
            extractor_counts[extractor_name] += 1
            if not bool(source.get("extractor_available", False)):
                format_issue_sources.append(
                    {
                        "source_id": source.get("source_id"),
                        "title": source.get("title"),
                        "source_format": source_format,
                        "issue": "extractor_unavailable",
                    }
                )
            low_signal = dict(source.get("low_signal", {}) or {})
            if low_signal.get("zero_unit"):
                zero_unit_sources.append(
                    {
                        "source_id": source.get("source_id"),
                        "title": source.get("title"),
                        "reasons": list(low_signal.get("reasons", []) or []),
                    }
                )
            for reason in low_signal.get("reasons", []) or []:
                reason_counts[str(reason)] += 1
            fallbacks = dict(low_signal.get("title_fallbacks", {}) or {})
            if any(fallbacks.values()):
                title_only_covered_count += 1
            for key, enabled in fallbacks.items():
                if enabled:
                    title_fallback_source_counts[str(key)] += 1
        typed_unit_type_counts: Dict[str, int] = defaultdict(int)
        for source in sources:
            for unit_type, count in (source.get("typed_unit_type_counts", {}) or {}).items():
                typed_unit_type_counts[str(unit_type)] += int(count)
        return {
            "zero_unit_count": len(zero_unit_sources),
            "zero_unit_sources": zero_unit_sources[:20],
            "low_signal_reason_counts": dict(sorted(reason_counts.items())),
            "title_fallback_source_count": title_only_covered_count,
            "title_fallback_source_counts": dict(sorted(title_fallback_source_counts.items())),
            "typed_unit_type_counts": dict(sorted(typed_unit_type_counts.items())),
            "format_counts": dict(sorted(format_counts.items())),
            "extractor_counts": dict(sorted(extractor_counts.items())),
            "format_issue_sources": format_issue_sources[:20],
        }

    @classmethod
    def _build_provenance_summary(cls, units: List[Dict[str, Any]]) -> Dict[str, Any]:
        path_counts: Dict[str, int] = defaultdict(int)
        title_flag_counts: Dict[str, int] = defaultdict(int)
        authority_counts: Dict[str, int] = defaultdict(int)
        kind_counts: Dict[str, int] = defaultdict(int)
        typed_unit_type_counts: Dict[str, int] = defaultdict(int)
        llm_enriched_count = 0
        title_derived_count = 0
        sample_provenance: List[Dict[str, Any]] = []

        for unit in units:
            kind = str(unit.get("kind", "")).strip()
            authority = str(unit.get("authority", "")).strip()
            provenance = dict(unit.get("provenance", {}) or {})
            path = str(provenance.get("path", "")).strip()
            if path:
                path_counts[path] += 1
            for flag in provenance.get("title_flags", []) or []:
                title_flag_counts[str(flag)] += 1
            if authority:
                authority_counts[authority] += 1
            if kind:
                kind_counts[kind] += 1
            typed_unit = dict(unit.get("typed_unit", {}) or {})
            typed_unit_type = str(typed_unit.get("type", "")).strip()
            if typed_unit_type:
                typed_unit_type_counts[typed_unit_type] += 1
            if bool(unit.get("is_llm_enriched", False)):
                llm_enriched_count += 1
            if bool(unit.get("is_title_derived", False)):
                title_derived_count += 1
            if provenance and len(sample_provenance) < 6:
                sample_provenance.append(
                    {
                        "unit_id": unit.get("unit_id"),
                        "kind": kind,
                        "path": path,
                        "title_flags": list(provenance.get("title_flags", []) or []),
                    }
                )

        return {
            "path_count": len(path_counts),
            "paths": dict(sorted(path_counts.items())),
            "title_flag_counts": dict(sorted(title_flag_counts.items())),
            "authority_counts": dict(sorted(authority_counts.items())),
            "unit_kind_counts": dict(sorted(kind_counts.items())),
            "typed_unit_type_counts": dict(sorted(typed_unit_type_counts.items())),
            "llm_enriched_unit_count": llm_enriched_count,
            "title_derived_unit_count": title_derived_count,
            "sample_provenance": sample_provenance,
        }

    @classmethod
    def _group_units_by_kind(cls, units: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        grouped: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        for unit in sorted(units, key=lambda item: (-float(item.get("importance", 0.0)), str(item.get("kind", "")))):
            kind = str(unit.get("kind", "unknown"))
            if len(grouped[kind]) >= 4:
                continue
            grouped[kind].append(
                {
                    "unit_id": unit.get("unit_id"),
                    "text": unit.get("text"),
                    "importance": unit.get("importance", 0.0),
                    "typed_unit": dict(unit.get("typed_unit", {}) or {}),
                    "entities": list(unit.get("entities", []) or []),
                }
            )
        return dict(grouped)

    @classmethod
    def _select_top_units(cls, units: List[Dict[str, Any]], *, limit: int) -> List[Dict[str, Any]]:
        selected = sorted(
            units,
            key=lambda item: (
                -float(item.get("importance", 0.0)),
                -float(item.get("source_weight", 0.0)),
                str(item.get("kind", "")),
            ),
        )[:limit]
        return [
            {
                "unit_id": unit.get("unit_id"),
                "kind": unit.get("kind"),
                "typed_unit": dict(unit.get("typed_unit", {}) or {}),
                "text": unit.get("text"),
                "importance": unit.get("importance", 0.0),
                "source_weight": unit.get("source_weight", 1.0),
                "source_density_score": unit.get("source_density_score", 1.0),
                "entities": list(unit.get("entities", []) or []),
                "provenance": dict(unit.get("provenance", {}) or {}),
            }
            for unit in selected
        ]

    @classmethod
    def _build_provenance_overview(cls, sources: List[Dict[str, Any]], units: List[Dict[str, Any]]) -> Dict[str, Any]:
        title_flag_counts: Dict[str, int] = defaultdict(int)
        authority_counts: Dict[str, int] = defaultdict(int)
        typed_unit_type_counts: Dict[str, int] = defaultdict(int)
        llm_enriched_source_count = 0
        for source in sources:
            if bool(source.get("llm_enriched", False)):
                llm_enriched_source_count += 1
            authority = str(source.get("authority", "")).strip()
            if authority:
                authority_counts[authority] += 1
            for flag in source.get("title_flags", []) or []:
                title_flag_counts[str(flag)] += 1
        for unit in units:
            typed_unit_type = str(dict(unit.get("typed_unit", {}) or {}).get("type", "")).strip()
            if typed_unit_type:
                typed_unit_type_counts[typed_unit_type] += 1
        return {
            "available_source_count": len(sources),
            "preview_unit_count": len(units),
            "authority_counts": dict(sorted(authority_counts.items())),
            "title_flag_counts": dict(sorted(title_flag_counts.items())),
            "typed_unit_type_counts": dict(sorted(typed_unit_type_counts.items())),
            "llm_enriched_source_count": llm_enriched_source_count,
        }

    def read_boundary_audit(self) -> Dict[str, Any]:
        """Inspect current capability split between data_service and app.graphrag."""
        backend_root = Path(__file__).resolve().parent.parent
        graphrag_root = backend_root / "app" / "graphrag"
        api_dir = graphrag_root / "api" / "v1"
        core_dir = graphrag_root / "core"
        storage_dir = graphrag_root / "storage"
        service_dir = graphrag_root / "service"

        def module_names(path: Path) -> List[str]:
            if not path.exists():
                return []
            names = []
            for file_path in sorted(path.glob("*.py")):
                if file_path.name in {"__init__.py", "router.py"}:
                    continue
                names.append(file_path.stem)
            return names

        api_modules = module_names(api_dir)
        if not api_modules and service_dir.exists():
            api_modules = ["index", "query"]

        llmwiki_contract_path = self.layout.llmwiki_state_dir / "input_contract.json"
        graphrag_contract_path = self.layout.graphrag_cache_dir / "input_contract.json"
        execution_owner_path = self.layout.graphrag_execution_owner
        execution_request_path = self.layout.graphrag_execution_request
        execution_runtime = self._read_json_file(execution_owner_path) or {
            "execution_owner": self.DEFAULT_GRAPH_EXECUTION_OWNER.value,
            "status": "unknown",
        }
        graph_index_status = (
            "done"
            if execution_runtime.get("execution_owner") == GraphExecutionOwner.APP_GRAPHRAG.value
            else "materializer_moved_to_app_graphrag"
        )
        schema = self._read_json_file(self.layout.distill_schema) or {}
        manifest = self._read_json_file(self.layout.distill_manifest) or {}
        manifest_quality = dict(manifest.get("quality", {}) or {})
        typed_unit_contract = {
            "schema_version": schema.get("typed_unit_schema_version", self.TYPED_DISTILL_UNIT_SCHEMA_VERSION),
            "typed_unit_types": list(schema.get("typed_unit_types", sorted(set(self.LEGACY_KIND_TO_TYPED_UNIT_TYPE.values()))) or []),
            "legacy_kind_to_typed_unit_type": dict(schema.get("legacy_kind_to_typed_unit_type", self.LEGACY_KIND_TO_TYPED_UNIT_TYPE) or {}),
            "typed_unit_type_counts": dict(manifest_quality.get("typed_unit_type_counts", {}) or {}),
            "compatible_consumers": ["llmwiki", "graphrag", "retrieval", "quality"],
        }

        overlap_areas = [
            {
                "area": "indexing",
                "current": ["data_service.default_adapters.GraphRAGWorkspaceAdapter orchestration", "app.graphrag.service.data_service_materializer"],
                "target_owner": "app.graphrag",
            },
            {
                "area": "graph_query",
                "current": ["data_service.get_graph_snapshot/query entry", "app.graphrag.service bridge/query_model"],
                "target_owner": "app.graphrag",
            },
            {
                "area": "orchestration",
                "current": ["data_service.build_ingest_plan", "data_service.run_default_pipeline"],
                "target_owner": "data_service",
            },
        ]
        capability_migration_table = [
            {
                "capability": "workspace_layout",
                "current_owner": "data_service",
                "target_owner": "data_service",
                "status": "keep",
                "action": "keep_in_data_service",
                "impact_scope": ["backend/data_service", "docs/architecture"],
            },
            {
                "capability": "distill_contract",
                "current_owner": "data_service",
                "target_owner": "data_service",
                "status": "keep",
                "action": "keep_in_data_service",
                "impact_scope": ["backend/data_service", "llmwiki_adapter", "graphrag_adapter"],
            },
            {
                "capability": "graph_index_execution",
                "current_owner": execution_runtime.get("execution_owner", self.DEFAULT_GRAPH_EXECUTION_OWNER.value),
                "target_owner": "app.graphrag",
                "status": graph_index_status,
                "action": "keep_data_service_orchestration_while_app_graphrag_owns_materialization",
                "impact_scope": ["backend/data_service/default_adapters.py", "backend/app/graphrag/service"],
            },
            {
                "capability": "graph_query_model",
                "current_owner": "app.graphrag.service",
                "target_owner": "app.graphrag",
                "status": "done",
                "action": "keep_data_service_entry_calling_app_graphrag_bridge",
                "impact_scope": ["backend/app/graphrag/service/data_service_query_model.py", "frontend/src/api/dataService.ts"],
            },
            {
                "capability": "community_snapshot_assembly",
                "current_owner": "app.graphrag.service",
                "target_owner": "app.graphrag",
                "status": "done",
                "action": "source_snapshot_from_app_graphrag_query_layer",
                "impact_scope": ["backend/app/graphrag/service/data_service_query_model.py", "frontend/src/pages/KnowledgePage.vue"],
            },
            {
                "capability": "knowledge_query_entry",
                "current_owner": "data_service",
                "target_owner": "data_service",
                "status": "keep",
                "action": "keep_unified_query_entry_in_data_service",
                "impact_scope": ["backend/data_service", "backend/app/api/v1/data_service.py", "MCP"],
            },
        ]

        return {
            "workspace": str(self.workspace),
            "contracts": {
                "contract_version": self.ENGINE_INPUT_CONTRACT_VERSION,
                "llmwiki_input_contract": {
                    "path": str(llmwiki_contract_path),
                    "exists": llmwiki_contract_path.exists(),
                },
                "graphrag_input_contract": {
                    "path": str(graphrag_contract_path),
                    "exists": graphrag_contract_path.exists(),
                },
                "graphrag_execution_owner": {
                    "path": str(execution_owner_path),
                    "exists": execution_owner_path.exists(),
                },
                "graphrag_execution_request": {
                    "path": str(execution_request_path),
                    "exists": execution_request_path.exists(),
                },
                "typed_unit_contract": typed_unit_contract,
            },
            "data_service": {
                "cli_commands": ["ingest", "summary", "distill", "boundary", "graphrag-execute", "query"],
                "http_endpoints": ["ingest", "summary", "distill", "boundary", "graphrag/execute", "query", "graph", "page", "reset"],
                "owns_now": [
                    "workspace_layout",
                    "distill_contract",
                    "summary_generation",
                    "unified_query_entry",
                    "graph_ingest_orchestration",
                ],
                "target_owns": [
                    "workspace_layout",
                    "distill_contract",
                    "summary_generation",
                    "unified_query_entry",
                    "mcp/http/cli_boundary",
                ],
            },
            "graphrag_codebase": {
                "root": str(graphrag_root),
                "api_modules": api_modules,
                "core_modules": module_names(core_dir),
                "storage_modules": module_names(storage_dir),
            },
            "overlap_areas": overlap_areas,
            "capability_migration_table": capability_migration_table,
            "graph_execution_runtime": execution_runtime,
            "migration_priorities": [
                "inventory_data_service_vs_app_graphrag_graph_capabilities",
                "decide_graph_index_execution_owner",
                "unify_graph_query_model",
                "keep_data_service_as_upstream_orchestration_boundary",
            ],
        }

    def run_graphrag_execution_request(self) -> Dict[str, Any]:
        """Run one delegated app.graphrag execution request for this workspace."""
        request_path = self.layout.graphrag_execution_request
        if not request_path.exists():
            return {
                "workspace": str(self.workspace),
                "status": "missing_request",
                "request_path": str(request_path),
            }
        from app.graphrag.service import run_data_service_execution_request

        result = run_data_service_execution_request(request_path)
        if result.get("status") == "completed":
            owner_payload = self._read_json_file(self.layout.graphrag_execution_owner) or {}
            owner_payload.update(
                {
                    "execution_owner": GraphExecutionOwner.APP_GRAPHRAG.value,
                    "status": "indexed_via_app_graphrag",
                    "state_db": result.get("compat_state", {}).get("state_db"),
                }
            )
            self.layout.graphrag_execution_owner.write_text(
                json.dumps(owner_payload, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
        return result

    def build_llmwiki_handoff(self, plan: IngestPlan, units: List[DistilledUnit]) -> Dict[str, Any]:
        """Build the explicit distill -> llmwiki input contract."""
        allowed_kinds = {kind.value for kind in self.LLMWIKI_ALLOWED_UNIT_KINDS}
        source_index = {source.source_id: source for source in plan.sources if source.source_id}
        filtered_units = [unit for unit in units if (unit.kind.value if hasattr(unit.kind, "value") else str(unit.kind)) in allowed_kinds]
        return {
            "contract_version": self.ENGINE_INPUT_CONTRACT_VERSION,
            "engine": "llmwiki",
            "workspace": str(plan.workspace),
            "allowed_unit_kinds": sorted(allowed_kinds),
            "typed_unit_schema_version": self.TYPED_DISTILL_UNIT_SCHEMA_VERSION,
            "typed_unit_type_counts": self._count_typed_unit_types(filtered_units),
            "source_fields": [
                "source_id",
                "path",
                "authority_hint",
                "meta.title_flags",
                "meta.source_weight",
                "meta.source_density_score",
            ],
            "unit_fields": [
                "unit_id",
                "source_id",
                "kind",
                "typed_unit",
                "authority",
                "text",
                "importance",
                "confidence",
                "source_weight",
                "source_density_score",
                "is_title_derived",
                "is_llm_enriched",
                "tags",
                "entities",
                "provenance",
            ],
            "sources": [
                {
                    "source_id": source.source_id,
                    "path": source.path,
                    "authority_hint": source.authority_hint.value if getattr(source, "authority_hint", None) else None,
                    "meta": {
                        "title_flags": source.meta.get("title_flags", ""),
                        "source_weight": source.meta.get("source_weight", "1.0"),
                        "source_density_score": source.meta.get("source_density_score", "1.0"),
                    },
                }
                for source in plan.sources
            ],
            "units": [self._serialize_handoff_unit(unit, include_relations=False) for unit in filtered_units],
            "source_unit_counts": self._count_units_by_source(filtered_units, source_index),
        }

    def build_graphrag_handoff(self, plan: IngestPlan, units: List[DistilledUnit]) -> Dict[str, Any]:
        """Build the explicit distill -> graphrag input contract."""
        allowed_kinds = {kind.value for kind in self.GRAPHRAG_ALLOWED_UNIT_KINDS}
        source_index = {source.source_id: source for source in plan.sources if source.source_id}
        filtered_units = [unit for unit in units if (unit.kind.value if hasattr(unit.kind, "value") else str(unit.kind)) in allowed_kinds]
        return {
            "contract_version": self.ENGINE_INPUT_CONTRACT_VERSION,
            "engine": "graphrag",
            "workspace": str(plan.workspace),
            "allowed_unit_kinds": sorted(allowed_kinds),
            "typed_unit_schema_version": self.TYPED_DISTILL_UNIT_SCHEMA_VERSION,
            "typed_unit_type_counts": self._count_typed_unit_types(filtered_units),
            "source_fields": [
                "source_id",
                "path",
                "authority_hint",
                "meta.title_flags",
                "meta.source_weight",
                "meta.source_density_score",
            ],
            "unit_fields": [
                "unit_id",
                "source_id",
                "kind",
                "typed_unit",
                "authority",
                "text",
                "normalized_text",
                "importance",
                "confidence",
                "source_weight",
                "source_density_score",
                "is_title_derived",
                "is_llm_enriched",
                "tags",
                "entities",
                "relations",
                "provenance",
            ],
            "sources": [
                {
                    "source_id": source.source_id,
                    "path": source.path,
                    "authority_hint": source.authority_hint.value if getattr(source, "authority_hint", None) else None,
                    "meta": {
                        "title_flags": source.meta.get("title_flags", ""),
                        "source_weight": source.meta.get("source_weight", "1.0"),
                        "source_density_score": source.meta.get("source_density_score", "1.0"),
                    },
                }
                for source in plan.sources
            ],
            "units": [self._serialize_handoff_unit(unit, include_relations=True) for unit in filtered_units],
            "source_unit_counts": self._count_units_by_source(filtered_units, source_index),
        }

    def _build_quality_summary(self) -> Dict[str, Any]:
        quality: Dict[str, Any] = {
            "distill": {
                "schema_version": self.DISTILL_SCHEMA_VERSION,
                "typed_unit_schema_version": self.TYPED_DISTILL_UNIT_SCHEMA_VERSION,
                "source_count": 0,
                "distilled_unit_count": 0,
                "llm_enriched_source_count": 0,
                "title_flag_counts": {},
                "typed_unit_type_counts": {},
            },
            "llmwiki": {
                "page_count": 0,
            },
            "graphrag": {
                "execution_owner": self.DEFAULT_GRAPH_EXECUTION_OWNER.value,
                "entity_count": 0,
                "theme_count": 0,
                "relationship_count": 0,
                "community_count": 0,
                "top_communities": [],
            },
            "manual_feedback": self._build_manual_feedback_summary(
                self._read_jsonl_all(self.layout.quality_feedback_jsonl)
            ),
            "correction_rules": self._build_correction_rules_summary(
                list((self._read_json_file(self.layout.quality_correction_rules_json) or {}).get("rules", []) or [])
            ),
            "correction_plan": self._build_correction_plan_summary(
                list((self._read_json_file(self.layout.quality_correction_plan_json) or {}).get("actions", []) or [])
            ),
        }

        if self.layout.distill_manifest.exists():
            try:
                manifest = json.loads(self.layout.distill_manifest.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                manifest = {}
            sources = manifest.get("sources", []) or []
            title_flag_counts: Dict[str, int] = defaultdict(int)
            llm_enriched_source_count = 0
            unit_kind_counts: Dict[str, int] = defaultdict(int)
            typed_unit_type_counts: Dict[str, int] = defaultdict(int)
            format_counts: Dict[str, int] = defaultdict(int)
            extractor_counts: Dict[str, int] = defaultdict(int)
            manifest_quality = dict(manifest.get("quality", {}) or {})
            for source in sources:
                if source.get("llm_enriched"):
                    llm_enriched_source_count += 1
                source_format = str(source.get("source_format") or "").strip()
                extractor_name = str(source.get("extractor_name") or "").strip()
                if source_format:
                    format_counts[source_format] += 1
                if extractor_name:
                    extractor_counts[extractor_name] += 1
                for flag in source.get("title_flags", []) or []:
                    title_flag_counts[str(flag)] += 1
                for kind, count in (source.get("unit_kind_counts", {}) or {}).items():
                    unit_kind_counts[str(kind)] += int(count)
                for unit_type, count in (source.get("typed_unit_type_counts", {}) or {}).items():
                    typed_unit_type_counts[str(unit_type)] += int(count)
            quality["distill"] = {
                "schema_version": manifest.get("schema_version", self.DISTILL_SCHEMA_VERSION),
                "typed_unit_schema_version": manifest.get("typed_unit_schema_version", self.TYPED_DISTILL_UNIT_SCHEMA_VERSION),
                "source_count": int(manifest.get("source_count", 0)),
                "distilled_unit_count": int(manifest.get("distilled_unit_count", 0)),
                "llm_enriched_source_count": llm_enriched_source_count,
                "title_flag_counts": dict(sorted(title_flag_counts.items())),
                "unit_kind_counts": dict(sorted(unit_kind_counts.items())),
                "typed_unit_type_counts": dict(sorted(typed_unit_type_counts.items())),
                "format_counts": dict(sorted(format_counts.items())),
                "extractor_counts": dict(sorted(extractor_counts.items())),
                "format_issue_sources": list(manifest_quality.get("format_issue_sources", []) or []),
                "zero_unit_count": int(manifest_quality.get("zero_unit_count", 0) or 0),
                "zero_unit_sources": list(manifest_quality.get("zero_unit_sources", []) or []),
                "low_signal_reason_counts": dict(manifest_quality.get("low_signal_reason_counts", {}) or {}),
                "title_fallback_source_count": int(manifest_quality.get("title_fallback_source_count", 0) or 0),
                "title_fallback_source_counts": dict(manifest_quality.get("title_fallback_source_counts", {}) or {}),
            }

        if self.layout.llmwiki_pages_dir.exists():
            quality["llmwiki"]["page_count"] = len(list(self.layout.llmwiki_pages_dir.glob("*.md")))

        graph_snapshot = self.get_graph_snapshot(max_nodes=80)
        graph_stats = graph_snapshot.get("stats", {})
        execution_runtime = self._read_json_file(self.layout.graphrag_execution_owner) or {}
        quality["graphrag"] = {
            "execution_owner": execution_runtime.get("execution_owner", self.DEFAULT_GRAPH_EXECUTION_OWNER.value),
            "entity_count": int(graph_stats.get("entity_count", 0)),
            "theme_count": int(graph_stats.get("theme_count", 0)),
            "relationship_count": int(graph_stats.get("relationship_count", 0)),
            "community_count": int(graph_stats.get("community_count", 0)),
            "top_communities": [
                {
                    "title": community.get("title"),
                    "score": community.get("score"),
                    "entity_count": community.get("entity_count"),
                    "relationship_count": community.get("relationship_count"),
                }
                for community in graph_snapshot.get("communities", [])[:8]
            ],
        }
        quality["manual_feedback"] = self._build_manual_feedback_summary(
            self._read_jsonl_all(self.layout.quality_feedback_jsonl)
        )
        quality["correction_rules"] = self._build_correction_rules_summary(
            list((self._read_json_file(self.layout.quality_correction_rules_json) or {}).get("rules", []) or [])
        )
        quality["correction_plan"] = self._build_correction_plan_summary(
            list((self._read_json_file(self.layout.quality_correction_plan_json) or {}).get("actions", []) or [])
        )
        return quality

    @classmethod
    def _build_manual_feedback_summary(cls, records: List[Dict[str, Any]]) -> Dict[str, Any]:
        action_counts: Dict[str, int] = defaultdict(int)
        target_type_counts: Dict[str, int] = defaultdict(int)
        latest_at = ""
        for record in records:
            action = str(record.get("action", "")).strip() or "unknown"
            target_type = str(record.get("target_type", "")).strip() or "unknown"
            action_counts[action] += 1
            target_type_counts[target_type] += 1
            created_at = str(record.get("created_at", "")).strip()
            if created_at > latest_at:
                latest_at = created_at
        return {
            "feedback_count": len(records),
            "action_counts": dict(sorted(action_counts.items())),
            "target_type_counts": dict(sorted(target_type_counts.items())),
            "latest_at": latest_at,
        }

    @classmethod
    def _build_correction_rules_summary(cls, rules: List[Dict[str, Any]]) -> Dict[str, Any]:
        status_counts: Dict[str, int] = defaultdict(int)
        rule_type_counts: Dict[str, int] = defaultdict(int)
        target_type_counts: Dict[str, int] = defaultdict(int)
        for rule in rules:
            status_counts[str(rule.get("status", "unknown"))] += 1
            rule_type_counts[str(rule.get("rule_type", "unknown"))] += 1
            target_type_counts[str(rule.get("target_type", "unknown"))] += 1
        return {
            "rule_count": len(rules),
            "status_counts": dict(sorted(status_counts.items())),
            "rule_type_counts": dict(sorted(rule_type_counts.items())),
            "target_type_counts": dict(sorted(target_type_counts.items())),
        }

    @classmethod
    def _build_correction_plan_summary(cls, actions: List[Dict[str, Any]]) -> Dict[str, Any]:
        action_counts: Dict[str, int] = defaultdict(int)
        target_engine_counts: Dict[str, int] = defaultdict(int)
        target_type_counts: Dict[str, int] = defaultdict(int)
        graph_node_count = 0
        graph_edge_count = 0
        llmwiki_page_count = 0
        impacted_action_count = 0
        for action in actions:
            action_counts[str(action.get("action", "unknown"))] += 1
            target_type_counts[str(action.get("target_type", "unknown"))] += 1
            for engine in list(action.get("target_engines", []) or []):
                target_engine_counts[str(engine)] += 1
            impact = dict(action.get("impact", {}) or {})
            graph_nodes = list(impact.get("graph_nodes", []) or [])
            graph_edges = list(impact.get("graph_edges", []) or [])
            llmwiki_pages = list(impact.get("llmwiki_pages", []) or [])
            graph_node_count += len(graph_nodes)
            graph_edge_count += len(graph_edges)
            llmwiki_page_count += len(llmwiki_pages)
            if graph_nodes or graph_edges or llmwiki_pages:
                impacted_action_count += 1
        return {
            "action_count": len(actions),
            "action_counts": dict(sorted(action_counts.items())),
            "target_engine_counts": dict(sorted(target_engine_counts.items())),
            "target_type_counts": dict(sorted(target_type_counts.items())),
            "impacted_action_count": impacted_action_count,
            "impact_counts": {
                "graph_nodes": graph_node_count,
                "graph_edges": graph_edge_count,
                "llmwiki_pages": llmwiki_page_count,
            },
        }

    @classmethod
    def _correction_rule_to_plan_action(cls, rule: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        rule_type = str(rule.get("rule_type", "")).strip()
        target_type = str(rule.get("target_type", "")).strip() or "unknown"
        target_id = str(rule.get("target_id", "")).strip()
        proposed_value = str(rule.get("proposed_value", "")).strip()
        if not rule_type or not target_id:
            return None
        action_by_rule_type = {
            "rename": "rename_target",
            "merge": "merge_target",
            "suppress": "suppress_target",
            "review": "flag_reviewed_target",
        }
        action = action_by_rule_type.get(rule_type)
        if not action:
            return None
        if rule_type in {"rename", "merge"} and not proposed_value:
            return None
        target_engines = ["llmwiki", "graphrag"]
        if target_type in {"entity", "community"}:
            target_engines = ["graphrag", "llmwiki"]
        elif target_type in {"page", "source", "distill_unit"}:
            target_engines = ["llmwiki", "graphrag"]
        return {
            "action_id": f"action_{rule.get('rule_id', '')}",
            "source_rule_id": rule.get("rule_id", ""),
            "source_feedback_id": rule.get("source_feedback_id", ""),
            "action": action,
            "target_type": target_type,
            "target_id": target_id,
            "current_label": str(rule.get("current_label", "")).strip(),
            "proposed_value": proposed_value,
            "target_engines": target_engines,
            "reason": str(rule.get("reason", "")).strip(),
            "metadata": dict(rule.get("metadata", {}) or {}),
        }

    def _attach_correction_plan_impacts(self, actions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        graph_nodes: List[Dict[str, Any]] = []
        graph_edges: List[Dict[str, Any]] = []
        try:
            from app.graphrag.service import read_workspace_graph_snapshot

            snapshot = read_workspace_graph_snapshot(self.workspace, max_nodes=500)
            graph_nodes = list(snapshot.get("nodes", []) or [])
            graph_edges = list(snapshot.get("edges", []) or [])
        except Exception:
            graph_nodes = []
            graph_edges = []

        llmwiki_pages = self._read_llmwiki_page_impacts_source()
        enriched: List[Dict[str, Any]] = []
        for action in actions:
            action = dict(action)
            keys = self._correction_action_match_keys(action)
            impacted_node_ids: Set[str] = set()
            matched_nodes: List[Dict[str, Any]] = []
            for node in graph_nodes:
                node_id = str(node.get("id", "")).strip()
                node_name = str(node.get("name") or node.get("label") or "").strip()
                if self._correction_keys_match(keys, node_id, node_name):
                    impacted_node_ids.add(node_id)
                    matched_nodes.append(
                        {
                            "id": node_id,
                            "name": node_name or node_id,
                            "type": node.get("type") or node.get("node_type") or "",
                        }
                    )

            matched_edges = [
                {
                    "source": edge.get("source", ""),
                    "target": edge.get("target", ""),
                    "label": edge.get("label", edge.get("description", "")),
                }
                for edge in graph_edges
                if str(edge.get("source", "")).strip() in impacted_node_ids
                or str(edge.get("target", "")).strip() in impacted_node_ids
            ]
            matched_pages: List[Dict[str, Any]] = []
            for page in llmwiki_pages:
                if self._correction_keys_match(keys, page.get("slug", ""), page.get("title", ""), page.get("body_md", "")):
                    matched_pages.append(
                        {
                            "slug": page.get("slug", ""),
                            "title": page.get("title", ""),
                            "path": page.get("path", ""),
                        }
                    )

            action["impact"] = {
                "graph_nodes": matched_nodes[:20],
                "graph_edges": matched_edges[:20],
                "llmwiki_pages": matched_pages[:20],
                "query_hits": [],
                "query_hit_note": "Query impact is applied at read time and depends on the operator query.",
            }
            action["impact"]["summary"] = {
                "total_matches": len(matched_nodes) + len(matched_edges) + len(matched_pages),
                "graph_node_count": len(matched_nodes),
                "graph_edge_count": len(matched_edges),
                "llmwiki_page_count": len(matched_pages),
            }
            enriched.append(action)
        return enriched

    def _read_llmwiki_page_impacts_source(self) -> List[Dict[str, Any]]:
        pages: List[Dict[str, Any]] = []
        if not self.layout.llmwiki_pages_dir.exists():
            return pages
        for path in sorted(self.layout.llmwiki_pages_dir.glob("*.md")):
            try:
                body = path.read_text(encoding="utf-8")
            except OSError:
                body = ""
            pages.append(
                {
                    "slug": path.stem,
                    "title": self._extract_markdown_title(path),
                    "path": str(path),
                    "body_md": body,
                }
            )
        return pages

    @classmethod
    def _correction_action_match_keys(cls, action: Dict[str, Any]) -> Set[str]:
        return {
            value
            for value in (
                str(action.get("target_id", "")).strip(),
                str(action.get("current_label", "")).strip(),
            )
            if value
        }

    @classmethod
    def _correction_keys_match(cls, keys: Set[str], *values: str) -> bool:
        for value in values:
            text = str(value or "").strip()
            if not text:
                continue
            if text in keys:
                return True
            if any(key and key in text for key in keys):
                return True
        return False

    def _write_quality_correction_rules_payload(self, payload: Dict[str, Any]) -> None:
        self.layout.quality_correction_rules_json.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )

    @classmethod
    def _feedback_to_correction_rule(cls, record: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        action = str(record.get("action", "")).strip()
        target_id = str(record.get("target_id", "")).strip()
        if not action or not target_id:
            return None
        rule_type_by_action = {
            "rename_suggest": "rename",
            "merge_suggest": "merge",
            "mark_noise": "suppress",
            "needs_review": "review",
        }
        rule_type = rule_type_by_action.get(action)
        if not rule_type:
            return None
        suggested_value = str(record.get("suggested_value", "")).strip()
        if rule_type in {"rename", "merge"} and not suggested_value:
            suggested_value = str(record.get("label", "")).strip()
        if rule_type in {"rename", "merge"} and not suggested_value:
            return None
        feedback_id = str(record.get("feedback_id", "")).strip() or uuid.uuid4().hex[:12]
        return {
            "rule_id": f"rule_{feedback_id}",
            "rule_type": rule_type,
            "status": "draft",
            "target_type": str(record.get("target_type", "")).strip() or "unknown",
            "target_id": target_id,
            "current_label": str(record.get("label", "")).strip(),
            "proposed_value": suggested_value,
            "reason": str(record.get("reason", "")).strip(),
            "source_feedback_id": feedback_id,
            "created_at": str(record.get("created_at", "")).strip(),
            "metadata": dict(record.get("metadata", {}) or {}),
        }

    def _serialize_handoff_unit(self, unit: DistilledUnit, *, include_relations: bool) -> Dict[str, Any]:
        payload = {
            "unit_id": unit.unit_id,
            "source_id": unit.source_id,
            "kind": unit.kind.value if hasattr(unit.kind, "value") else str(unit.kind),
            "typed_unit": self._typed_unit_contract(unit),
            "authority": unit.authority.value if hasattr(unit.authority, "value") else str(unit.authority),
            "text": unit.text,
            "importance": unit.importance,
            "confidence": unit.confidence,
            "source_weight": unit.source_weight,
            "source_density_score": unit.source_density_score,
            "is_title_derived": bool(unit.is_title_derived),
            "is_llm_enriched": bool(unit.is_llm_enriched),
            "tags": list(unit.tags or []),
            "entities": list(unit.entities or []),
            "provenance": dict(unit.provenance or {}),
        }
        if include_relations:
            payload["normalized_text"] = unit.normalized_text
            payload["relations"] = list(unit.relations or [])
        return payload

    @classmethod
    def _typed_unit_contract(cls, unit: DistilledUnit) -> Dict[str, Any]:
        legacy_kind = unit.kind.value if hasattr(unit.kind, "value") else str(unit.kind)
        provenance = dict(unit.provenance or {})
        typed_unit_type = str(provenance.get("typed_unit_type") or "").strip() or cls.LEGACY_KIND_TO_TYPED_UNIT_TYPE.get(legacy_kind, "note")
        if typed_unit_type in {"code_symbol", "code_dependency", "code_call_edge", "architecture_note"}:
            evidence_role = "structure"
        elif legacy_kind in {DistilledUnitKind.TOPIC_CANDIDATE.value, DistilledUnitKind.ENTITY_CANDIDATE.value}:
            evidence_role = "index"
        elif legacy_kind in {DistilledUnitKind.FACT_CANDIDATE.value, DistilledUnitKind.RELATION_CANDIDATE.value}:
            evidence_role = "evidence"
        else:
            evidence_role = "semantic"
        return {
            "schema_version": cls.TYPED_DISTILL_UNIT_SCHEMA_VERSION,
            "type": typed_unit_type,
            "legacy_kind": legacy_kind,
            "evidence_role": evidence_role,
            "confidence": unit.confidence,
            "compatible_consumers": ["llmwiki", "graphrag", "retrieval", "quality"],
        }

    @classmethod
    def _count_typed_unit_types(cls, units: List[DistilledUnit]) -> Dict[str, int]:
        counts: Dict[str, int] = defaultdict(int)
        for unit in units:
            counts[cls._typed_unit_contract(unit)["type"]] += 1
        return dict(sorted(counts.items()))

    def _count_units_by_source(self, units: List[DistilledUnit], source_index: Dict[str, Any]) -> List[Dict[str, Any]]:
        counts: Dict[str, int] = defaultdict(int)
        for unit in units:
            counts[unit.source_id] += 1
        return [
            {
                "source_id": source_id,
                "path": source_index[source_id].path if source_id in source_index else "",
                "unit_count": unit_count,
            }
            for source_id, unit_count in sorted(counts.items())
        ]

    def _build_code_analysis_units(
        self,
        *,
        path: Path,
        source_id: str,
        authority: AuthorityLevel,
        source_weight: float,
        source_density_score: float,
        tags: List[str],
        title_flags: List[str],
    ) -> List[DistilledUnit]:
        if path.suffix.lower() != ".json":
            return []
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError, UnicodeDecodeError):
            return []
        if not isinstance(payload, dict) or not self._looks_like_code_analysis_payload(payload):
            return []

        units: List[DistilledUnit] = []
        base_provenance = {
            "path": str(path),
            "title_flags": title_flags,
            "structured_payload": "code_analysis",
        }

        for index, text in enumerate(self._extract_code_architecture_notes(payload)[:3]):
            units.append(
                DistilledUnit(
                    unit_id=f"{source_id}:architecture_note:{index + 1}",
                    source_id=source_id,
                    kind=DistilledUnitKind.NOTE,
                    authority=authority,
                    text=text,
                    normalized_text=text,
                    importance=0.78 + min(0.12, source_weight * 0.04),
                    confidence=0.7,
                    source_weight=source_weight,
                    source_density_score=source_density_score,
                    tags=tags,
                    provenance={**base_provenance, "typed_unit_type": "architecture_note"},
                )
            )

        for index, symbol in enumerate(self._extract_code_symbols(payload)[:12]):
            units.append(
                DistilledUnit(
                    unit_id=f"{source_id}:code_symbol:{index + 1}",
                    source_id=source_id,
                    kind=DistilledUnitKind.ENTITY_CANDIDATE,
                    authority=authority,
                    text=symbol,
                    normalized_text=symbol,
                    importance=0.76 + min(0.12, source_weight * 0.04),
                    confidence=0.72,
                    source_weight=source_weight,
                    source_density_score=source_density_score,
                    tags=tags,
                    entities=[symbol],
                    provenance={**base_provenance, "typed_unit_type": "code_symbol"},
                )
            )

        for index, relation in enumerate(self._extract_code_relations(payload, keys=("dependencies", "imports"))[:12]):
            text = f"{relation[0]} depends on {relation[1]}"
            units.append(
                DistilledUnit(
                    unit_id=f"{source_id}:code_dependency:{index + 1}",
                    source_id=source_id,
                    kind=DistilledUnitKind.RELATION_CANDIDATE,
                    authority=authority,
                    text=text,
                    normalized_text=text,
                    importance=0.74 + min(0.1, source_weight * 0.03),
                    confidence=0.7,
                    source_weight=source_weight,
                    source_density_score=source_density_score,
                    tags=tags,
                    entities=[relation[0], relation[1]],
                    relations=[{"source": relation[0], "target": relation[1], "relation": "depends_on"}],
                    provenance={**base_provenance, "typed_unit_type": "code_dependency"},
                )
            )

        for index, relation in enumerate(self._extract_code_relations(payload, keys=("calls", "call_edges", "call_graph"))[:12]):
            text = f"{relation[0]} calls {relation[1]}"
            units.append(
                DistilledUnit(
                    unit_id=f"{source_id}:code_call_edge:{index + 1}",
                    source_id=source_id,
                    kind=DistilledUnitKind.RELATION_CANDIDATE,
                    authority=authority,
                    text=text,
                    normalized_text=text,
                    importance=0.72 + min(0.1, source_weight * 0.03),
                    confidence=0.68,
                    source_weight=source_weight,
                    source_density_score=source_density_score,
                    tags=tags,
                    entities=[relation[0], relation[1]],
                    relations=[{"source": relation[0], "target": relation[1], "relation": "calls"}],
                    provenance={**base_provenance, "typed_unit_type": "code_call_edge"},
                )
            )
        return units

    @classmethod
    def _looks_like_code_analysis_payload(cls, payload: Dict[str, Any]) -> bool:
        keys = {str(key).lower() for key in payload.keys()}
        return bool(keys.intersection({"symbols", "dependencies", "imports", "calls", "call_edges", "call_graph", "architecture_notes", "modules"}))

    @classmethod
    def _extract_code_architecture_notes(cls, payload: Dict[str, Any]) -> List[str]:
        values: List[str] = []
        for key in ("architecture_notes", "architecture", "summary", "notes"):
            item = payload.get(key)
            if isinstance(item, str):
                values.append(item)
            elif isinstance(item, list):
                values.extend(str(value) for value in item if str(value).strip())
        return cls._dedupe_preserve(values, validator=lambda value: len(str(value).strip()) >= 8)

    @classmethod
    def _extract_code_symbols(cls, payload: Dict[str, Any]) -> List[str]:
        symbols: List[str] = []
        for item in payload.get("symbols", []) or []:
            if isinstance(item, str):
                symbols.append(item)
            elif isinstance(item, dict):
                name = str(item.get("name") or item.get("symbol") or item.get("id") or "").strip()
                kind = str(item.get("kind") or item.get("type") or "").strip()
                if name and kind:
                    symbols.append(f"{kind}:{name}")
                elif name:
                    symbols.append(name)
        for module in payload.get("modules", []) or []:
            if isinstance(module, str):
                symbols.append(module)
            elif isinstance(module, dict):
                name = str(module.get("name") or module.get("path") or "").strip()
                if name:
                    symbols.append(f"module:{name}")
        return cls._dedupe_preserve(symbols, validator=lambda value: len(str(value).strip()) >= 2)

    @classmethod
    def _extract_code_relations(cls, payload: Dict[str, Any], *, keys: tuple[str, ...]) -> List[tuple[str, str]]:
        relations: List[tuple[str, str]] = []
        for key in keys:
            for item in payload.get(key, []) or []:
                if isinstance(item, dict):
                    source = str(item.get("source") or item.get("from") or item.get("caller") or item.get("module") or "").strip()
                    target = str(item.get("target") or item.get("to") or item.get("callee") or item.get("depends_on") or item.get("import") or "").strip()
                    if source and target:
                        relations.append((source, target))
                elif isinstance(item, (list, tuple)) and len(item) >= 2:
                    source = str(item[0]).strip()
                    target = str(item[1]).strip()
                    if source and target:
                        relations.append((source, target))
        deduped: List[tuple[str, str]] = []
        seen: set[tuple[str, str]] = set()
        for relation in relations:
            if relation not in seen:
                seen.add(relation)
                deduped.append(relation)
        return deduped

    def _read_json_file(self, path: Path) -> Dict[str, Any]:
        if not path.exists():
            return {}
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return {}

    def _read_jsonl_preview(self, path: Path, *, limit: int) -> List[Dict[str, Any]]:
        if not path.exists():
            return []
        rows: List[Dict[str, Any]] = []
        try:
            with path.open("r", encoding="utf-8") as handle:
                for line in handle:
                    if len(rows) >= limit:
                        break
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        rows.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue
        except OSError:
            return []
        return rows

    def _read_jsonl_all(self, path: Path) -> List[Dict[str, Any]]:
        return self._read_jsonl_preview(path, limit=10000)

    @staticmethod
    def _filter_distill_units(
        units: List[Dict[str, Any]],
        *,
        kind: Optional[str],
        typed_unit_type: Optional[str],
        min_importance: float,
        llm_enriched_only: bool,
        authority: Optional[str],
        min_source_weight: float,
        min_source_density: float,
        limit: int,
    ) -> List[Dict[str, Any]]:
        filtered: List[Dict[str, Any]] = []
        for unit in units:
            if kind and str(unit.get("kind", "")).strip() != kind:
                continue
            if typed_unit_type and str(dict(unit.get("typed_unit", {}) or {}).get("type", "")).strip() != typed_unit_type:
                continue
            if float(unit.get("importance", 0.0) or 0.0) < min_importance:
                continue
            if llm_enriched_only and not bool(unit.get("is_llm_enriched", False)):
                continue
            if authority and str(unit.get("authority", "")).strip() != authority:
                continue
            if float(unit.get("source_weight", 0.0) or 0.0) < min_source_weight:
                continue
            if float(unit.get("source_density_score", 0.0) or 0.0) < min_source_density:
                continue
            filtered.append(unit)
            if len(filtered) >= limit:
                break
        return filtered

    def build_distilled_units(self, plan: IngestPlan) -> List[DistilledUnit]:
        """Generate a small, high-signal distilled layer for downstream engines.

        This is intentionally heuristic. It creates stable graph/wiki handoff
        units without forcing GraphRAG to consume raw fulltext.
        """
        self.ensure_layout()
        units: List[DistilledUnit] = []
        source_payloads: List[Dict[str, Any]] = []
        for source in plan.sources:
            path = Path(source.path)
            source_id = source.source_id or path.stem
            authority = self._infer_authority(path)
            title, title_flags = self._resolve_source_title(path)
            full_text = self._read_source_excerpt(path, limit=16000)
            format_profile = self._source_format_profile(path)
            source_profile = self._build_source_profile(path, title, full_text)
            source_weight = source_profile["source_weight"]
            source_density_score = source_profile["density_score"]
            excerpt = source_profile["excerpt"]
            tags = self._extract_tags(title, excerpt)
            entity_candidates = self._extract_entity_candidates(title, excerpt, title_flags)
            title_only_excerpt = source_profile["sentence_count"] <= 1 and excerpt.strip() == title.strip()
            theme_labels = self._extract_theme_labels(
                title,
                excerpt,
                entity_candidates,
                title_only_excerpt=title_only_excerpt,
            )
            llm_enrichment = self._llm_enrich_source(
                title=title,
                excerpt=excerpt,
                source_weight=source_weight,
                source_density_score=source_density_score,
            )
            if llm_enrichment:
                for label in llm_enrichment.get("theme_labels", []):
                    if self._is_meaningful_theme(label):
                        theme_labels.append(label)
                for entity in llm_enrichment.get("entities", []):
                    if self._is_meaningful_entity(entity):
                        entity_candidates.append(entity)
            theme_labels = self._compact_theme_labels(self._dedupe_preserve(theme_labels, validator=self._is_meaningful_theme))[:4]
            entity_candidates = self._compact_entity_candidates(self._dedupe_preserve(entity_candidates, validator=self._is_meaningful_entity))[:10]
            tags = self._dedupe_preserve(tags + theme_labels + entity_candidates, validator=self._is_meaningful_tag)[:10]
            source.source_id = source_id
            source.meta["title_flags"] = ",".join(title_flags)
            source.meta["source_weight"] = f"{source_weight:.3f}"
            source.meta["source_density_score"] = f"{source_density_score:.3f}"
            if llm_enrichment:
                source.meta["llm_enriched"] = "true"

            topic_labels = theme_labels or self._extract_theme_labels(title, excerpt, entity_candidates, title_only_excerpt=title_only_excerpt)
            source_units_start = len(units)
            for index, label in enumerate(topic_labels[: max(1, math.ceil(source_weight))]):
                units.append(
                    DistilledUnit(
                        unit_id=f"{source_id}:topic:{index + 1}",
                        source_id=source_id,
                        kind=DistilledUnitKind.TOPIC_CANDIDATE,
                        authority=authority,
                        text=label,
                        normalized_text=label,
                        importance=0.82 + min(0.14, source_weight * 0.05),
                        confidence=0.68 + min(0.18, source_density_score * 0.04),
                        source_weight=source_weight,
                        source_density_score=source_density_score,
                        is_title_derived=(index == 0 and label == title),
                        is_llm_enriched=bool(llm_enrichment and label in llm_enrichment.get("theme_labels", [])),
                        tags=tags,
                        entities=entity_candidates[:6],
                        provenance={"path": str(path), "title_flags": title_flags},
                    )
                )

            if excerpt and not title_only_excerpt:
                note_chunks = self._chunk_sentences(
                    source_profile["note_sentences"],
                    chunk_size=3,
                    max_chunks=max(1, min(2, math.ceil(source_weight))),
                )
                for index, chunk in enumerate(note_chunks):
                    units.append(
                        DistilledUnit(
                            unit_id=f"{source_id}:note:{index + 1}",
                            source_id=source_id,
                            kind=DistilledUnitKind.NOTE,
                            authority=authority,
                            text=chunk,
                            normalized_text=chunk,
                            importance=0.58 + min(0.18, source_weight * 0.06),
                            confidence=0.56,
                            source_weight=source_weight,
                            source_density_score=source_density_score,
                            tags=tags,
                            entities=entity_candidates[:6],
                            provenance={"path": str(path), "title_flags": title_flags},
                        )
                    )

                conclusion_candidates = self._dedupe_preserve(
                    source_profile["conclusions"] + ([self._first_sentence(excerpt)] if self._first_sentence(excerpt) else []),
                    validator=lambda value: len(value.strip()) >= 12,
                )
                for index, sentence in enumerate(conclusion_candidates[: max(1, min(3, math.ceil(source_weight)))]):
                    units.append(
                        DistilledUnit(
                            unit_id=f"{source_id}:conclusion:{index + 1}",
                            source_id=source_id,
                            kind=DistilledUnitKind.CONCLUSION,
                            authority=authority,
                            text=sentence,
                            normalized_text=sentence,
                            importance=0.72 + min(0.2, source_weight * 0.07),
                            confidence=0.62,
                            source_weight=source_weight,
                            source_density_score=source_density_score,
                            tags=tags,
                            entities=entity_candidates[:6],
                            provenance={"path": str(path), "title_flags": title_flags},
                        )
                    )

                for index, sentence in enumerate(source_profile["questions"][: max(1, min(2, math.ceil(source_weight - 0.3)))]):
                    units.append(
                        DistilledUnit(
                            unit_id=f"{source_id}:question:{index + 1}",
                            source_id=source_id,
                            kind=DistilledUnitKind.QUESTION,
                            authority=authority,
                            text=sentence,
                            normalized_text=sentence,
                            importance=0.62 + min(0.15, source_weight * 0.05),
                            confidence=0.58,
                            source_weight=source_weight,
                            source_density_score=source_density_score,
                            tags=tags,
                            entities=entity_candidates[:6],
                            provenance={"path": str(path), "title_flags": title_flags},
                        )
                    )

                for index, sentence in enumerate(source_profile["steps"][: max(1, min(3, math.ceil(source_weight)))]):
                    units.append(
                        DistilledUnit(
                            unit_id=f"{source_id}:step:{index + 1}",
                            source_id=source_id,
                            kind=DistilledUnitKind.STEP,
                            authority=authority,
                            text=sentence,
                            normalized_text=sentence,
                            importance=0.66 + min(0.18, source_weight * 0.06),
                            confidence=0.61,
                            source_weight=source_weight,
                            source_density_score=source_density_score,
                            tags=tags,
                            entities=entity_candidates[:6],
                            provenance={"path": str(path), "title_flags": title_flags},
                        )
                    )

                for index, sentence in enumerate(source_profile["risks"][: max(1, min(2, math.ceil(source_weight - 0.2)))]):
                    units.append(
                        DistilledUnit(
                            unit_id=f"{source_id}:risk:{index + 1}",
                            source_id=source_id,
                            kind=DistilledUnitKind.RISK,
                            authority=authority,
                            text=sentence,
                            normalized_text=sentence,
                            importance=0.68 + min(0.16, source_weight * 0.05),
                            confidence=0.59,
                            source_weight=source_weight,
                            source_density_score=source_density_score,
                            tags=tags,
                            entities=entity_candidates[:6],
                            provenance={"path": str(path), "title_flags": title_flags},
                        )
                    )

                for index, sentence in enumerate(source_profile["examples"][: max(1, min(2, math.ceil(source_weight - 0.1)))]):
                    units.append(
                        DistilledUnit(
                            unit_id=f"{source_id}:example:{index + 1}",
                            source_id=source_id,
                            kind=DistilledUnitKind.EXAMPLE,
                            authority=authority,
                            text=sentence,
                            normalized_text=sentence,
                            importance=0.56 + min(0.14, source_weight * 0.04),
                            confidence=0.57,
                            source_weight=source_weight,
                            source_density_score=source_density_score,
                            tags=tags,
                            entities=entity_candidates[:6],
                            provenance={"path": str(path), "title_flags": title_flags},
                        )
                    )

                for index, sentence in enumerate(source_profile["facts"][: max(1, min(2, math.ceil(source_weight - 0.2)))]):
                    units.append(
                        DistilledUnit(
                            unit_id=f"{source_id}:fact:{index + 1}",
                            source_id=source_id,
                            kind=DistilledUnitKind.FACT_CANDIDATE,
                            authority=authority,
                            text=sentence,
                            normalized_text=sentence,
                            importance=0.7 + min(0.16, source_weight * 0.05),
                            confidence=0.6,
                            source_weight=source_weight,
                            source_density_score=source_density_score,
                            tags=tags,
                            entities=entity_candidates[:6],
                            provenance={"path": str(path), "title_flags": title_flags},
                        )
                    )

            for index, entity in enumerate(entity_candidates[: max(2, min(8, math.ceil(source_weight * 2)))]):
                units.append(
                    DistilledUnit(
                        unit_id=f"{source_id}:entity:{index + 1}",
                        source_id=source_id,
                        kind=DistilledUnitKind.ENTITY_CANDIDATE,
                        authority=authority,
                        text=entity,
                        normalized_text=entity,
                        importance=0.7 + min(0.18, source_weight * 0.05),
                        confidence=0.6,
                        source_weight=source_weight,
                        source_density_score=source_density_score,
                        is_llm_enriched=bool(llm_enrichment and entity in llm_enrichment.get("entities", [])),
                        tags=tags,
                        entities=[entity],
                        provenance={"path": str(path), "title_flags": title_flags},
                    )
                )

            units.extend(
                self._build_code_analysis_units(
                    path=path,
                    source_id=source_id,
                    authority=authority,
                    source_weight=source_weight,
                    source_density_score=source_density_score,
                    tags=tags,
                    title_flags=title_flags,
                )
            )

            source_units = [unit for unit in units[source_units_start:] if unit.source_id == source_id]
            non_index_kinds = {
                DistilledUnitKind.NOTE,
                DistilledUnitKind.CONCLUSION,
                DistilledUnitKind.QUESTION,
                DistilledUnitKind.STEP,
                DistilledUnitKind.RISK,
                DistilledUnitKind.EXAMPLE,
                DistilledUnitKind.FACT_CANDIDATE,
            }
            has_content_units = any(
                unit.kind in non_index_kinds
                and (unit.text or "").strip() != title.strip()
                for unit in source_units
            )
            title_fallback_question = self._derive_title_fallback_question(title)
            if title_fallback_question and (title_only_excerpt or not has_content_units):
                units.append(
                    DistilledUnit(
                        unit_id=f"{source_id}:question:title",
                        source_id=source_id,
                        kind=DistilledUnitKind.QUESTION,
                        authority=authority,
                        text=title_fallback_question,
                        normalized_text=title_fallback_question,
                        importance=0.64 + min(0.12, source_weight * 0.04),
                        confidence=0.52,
                        source_weight=source_weight,
                        source_density_score=source_density_score,
                        is_title_derived=True,
                        tags=tags,
                        entities=entity_candidates[:6],
                        provenance={"path": str(path), "title_flags": title_flags, "fallback_from_title": True},
                    )
                )
            title_fallback_note = self._derive_title_fallback_note(title, entity_candidates[:6])
            if title_fallback_note and (title_only_excerpt or not has_content_units):
                units.append(
                    DistilledUnit(
                        unit_id=f"{source_id}:note:title",
                        source_id=source_id,
                        kind=DistilledUnitKind.NOTE,
                        authority=authority,
                        text=title_fallback_note,
                        normalized_text=title_fallback_note,
                        importance=0.57 + min(0.1, source_weight * 0.03),
                        confidence=0.49,
                        source_weight=source_weight,
                        source_density_score=source_density_score,
                        is_title_derived=True,
                        tags=tags,
                        entities=entity_candidates[:6],
                        provenance={"path": str(path), "title_flags": title_flags, "fallback_from_title": True},
                    )
                )
            title_fallback_fact = self._derive_title_fallback_fact(title, entity_candidates[:6])
            if title_fallback_fact and (title_only_excerpt or not has_content_units):
                units.append(
                    DistilledUnit(
                        unit_id=f"{source_id}:fact:title",
                        source_id=source_id,
                        kind=DistilledUnitKind.FACT_CANDIDATE,
                        authority=authority,
                        text=title_fallback_fact,
                        normalized_text=title_fallback_fact,
                        importance=0.61 + min(0.1, source_weight * 0.03),
                        confidence=0.5,
                        source_weight=source_weight,
                        source_density_score=source_density_score,
                        is_title_derived=True,
                        tags=tags,
                        entities=entity_candidates[:6],
                        provenance={"path": str(path), "title_flags": title_flags, "fallback_from_title": True},
                    )
                )
            title_fallback_risk = self._derive_title_fallback_risk(title, entity_candidates[:6])
            if title_fallback_risk and (title_only_excerpt or not has_content_units):
                units.append(
                    DistilledUnit(
                        unit_id=f"{source_id}:risk:title",
                        source_id=source_id,
                        kind=DistilledUnitKind.RISK,
                        authority=authority,
                        text=title_fallback_risk,
                        normalized_text=title_fallback_risk,
                        importance=0.63 + min(0.1, source_weight * 0.03),
                        confidence=0.51,
                        source_weight=source_weight,
                        source_density_score=source_density_score,
                        is_title_derived=True,
                        tags=tags,
                        entities=entity_candidates[:6],
                        provenance={"path": str(path), "title_flags": title_flags, "fallback_from_title": True},
                    )
                )

            source_units_final = [unit for unit in units if unit.source_id == source_id]
            title_fallbacks = {
                "question": bool(title_fallback_question),
                "note": bool(title_fallback_note),
                "fact_candidate": bool(title_fallback_fact),
                "risk": bool(title_fallback_risk),
            }
            low_signal_diagnostics = self._build_low_signal_diagnostics(
                title=title,
                title_only_excerpt=title_only_excerpt,
                source_profile=source_profile,
                source_units=source_units_final,
                entity_candidates=entity_candidates,
                theme_labels=theme_labels,
                title_fallbacks=title_fallbacks,
            )
            source_distill_path = plan.layout.distill_sources_dir / f"{source_id}.json"
            source_distill_payload = {
                "schema_version": self.DISTILL_SCHEMA_VERSION,
                "source_id": source_id,
                "path": str(path),
                "source_format": format_profile["source_format"],
                "extractor_name": format_profile["extractor_name"],
                "extractor_available": format_profile["extractor_available"],
                "authority": authority.value,
                "title": title,
                "title_flags": title_flags,
                "source_weight": source_weight,
                "source_density_score": source_density_score,
                "llm_enriched": bool(llm_enrichment),
                "tags": tags,
                "profile": {
                    "sentence_count": source_profile["sentence_count"],
                    "question_count": len(source_profile["questions"]),
                    "step_count": len(source_profile["steps"]),
                    "risk_count": len(source_profile["risks"]),
                    "example_count": len(source_profile["examples"]),
                    "fact_count": len(source_profile["facts"]),
                    "zero_unit": low_signal_diagnostics["zero_unit"],
                    "low_signal": low_signal_diagnostics,
                },
                "profile_debug": {
                    "excerpt_preview": source_profile["excerpt"][:600],
                    "format_profile": format_profile,
                    "title_only_excerpt": title_only_excerpt,
                    "entity_candidates": entity_candidates[:10],
                    "theme_labels": theme_labels[:6],
                    "title_normalization": self._build_title_normalization_debug(
                        title,
                        title_only_excerpt=title_only_excerpt,
                        entity_candidates=entity_candidates,
                        theme_labels=theme_labels,
                    ),
                    "summary_sentences": source_profile["summary_sentences"][:4],
                    "questions": source_profile["questions"][:3],
                    "steps": source_profile["steps"][:4],
                    "risks": source_profile["risks"][:3],
                    "examples": source_profile["examples"][:3],
                    "facts": source_profile["facts"][:3],
                    "note_sentences": source_profile["note_sentences"][:4],
                    "conclusions": source_profile["conclusions"][:4],
                    "title_fallback_question": title_fallback_question,
                    "title_fallback_note": title_fallback_note,
                    "title_fallback_fact": title_fallback_fact,
                    "title_fallback_risk": title_fallback_risk,
                    "low_signal": low_signal_diagnostics,
                },
                "unit_kind_counts": self._count_unit_kinds(source_units_final),
                "typed_unit_type_counts": self._count_typed_unit_types(source_units_final),
                "units": [
                    {
                        "unit_id": unit.unit_id,
                        "kind": unit.kind.value,
                        "typed_unit": self._typed_unit_contract(unit),
                        "text": unit.text,
                        "importance": unit.importance,
                        "confidence": unit.confidence,
                        "source_weight": unit.source_weight,
                        "source_density_score": unit.source_density_score,
                        "is_title_derived": unit.is_title_derived,
                        "is_llm_enriched": unit.is_llm_enriched,
                        "tags": unit.tags,
                        "entities": unit.entities,
                        "provenance": unit.provenance,
                    }
                    for unit in units
                    if unit.source_id == source_id
                ],
            }
            source_distill_path.write_text(
                json.dumps(source_distill_payload, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
            source_payloads.append(
                {
                    "source_id": source_id,
                    "path": str(path),
                    "source_format": format_profile["source_format"],
                    "extractor_name": format_profile["extractor_name"],
                    "extractor_available": format_profile["extractor_available"],
                    "authority": authority.value,
                    "unit_count": len(source_distill_payload["units"]),
                    "source_weight": source_weight,
                    "source_density_score": source_density_score,
                    "title": title,
                    "title_flags": title_flags,
                    "llm_enriched": bool(llm_enrichment),
                    "profile": source_distill_payload["profile"],
                    "unit_kind_counts": source_distill_payload["unit_kind_counts"],
                    "typed_unit_type_counts": source_distill_payload["typed_unit_type_counts"],
                    "low_signal": low_signal_diagnostics,
                    "distill_path": str(source_distill_path),
                }
            )

        units_payload_path = plan.layout.distill_units_dir / "distilled_units.jsonl"
        units_payload_lines = [
            json.dumps(
                {
                    "schema_version": self.DISTILL_SCHEMA_VERSION,
                    "unit_id": unit.unit_id,
                    "source_id": unit.source_id,
                    "kind": unit.kind.value,
                    "typed_unit": self._typed_unit_contract(unit),
                    "authority": unit.authority.value,
                    "text": unit.text,
                    "normalized_text": unit.normalized_text,
                    "importance": unit.importance,
                    "confidence": unit.confidence,
                    "source_weight": unit.source_weight,
                    "source_density_score": unit.source_density_score,
                    "is_title_derived": unit.is_title_derived,
                    "is_llm_enriched": unit.is_llm_enriched,
                    "tags": unit.tags,
                    "entities": unit.entities,
                    "relations": unit.relations,
                    "provenance": unit.provenance,
                },
                ensure_ascii=False,
            )
            for unit in units
        ]
        units_payload_path.write_text(
            "\n".join(units_payload_lines) + ("\n" if units_payload_lines else ""),
            encoding="utf-8",
        )
        manifest_payload = {
            "schema_version": self.DISTILL_SCHEMA_VERSION,
            "typed_unit_schema_version": self.TYPED_DISTILL_UNIT_SCHEMA_VERSION,
            "workspace": str(plan.workspace),
            "source_count": len(plan.sources),
            "distilled_unit_count": len(units),
            "sources": source_payloads,
            "quality": self._build_distill_manifest_quality(source_payloads),
            "units_path": str(units_payload_path),
        }
        plan.layout.distill_manifest.write_text(
            json.dumps(manifest_payload, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        schema_payload = {
            "schema_version": self.DISTILL_SCHEMA_VERSION,
            "typed_unit_schema_version": self.TYPED_DISTILL_UNIT_SCHEMA_VERSION,
            "typed_unit_types": sorted(set(self.LEGACY_KIND_TO_TYPED_UNIT_TYPE.values()) | self.EXTRA_TYPED_UNIT_TYPES),
            "legacy_kind_to_typed_unit_type": dict(sorted(self.LEGACY_KIND_TO_TYPED_UNIT_TYPE.items())),
            "source_record_fields": [
                "source_id",
                "path",
                "authority",
                "title",
                "title_flags",
                "source_format",
                "extractor_name",
                "extractor_available",
                "source_weight",
                "source_density_score",
                "llm_enriched",
                "tags",
                "profile",
                "profile_debug",
                "unit_kind_counts",
                "typed_unit_type_counts",
                "low_signal",
                "units",
            ],
            "unit_fields": [
                "unit_id",
                "source_id",
                "kind",
                "typed_unit",
                "authority",
                "text",
                "normalized_text",
                "importance",
                "confidence",
                "source_weight",
                "source_density_score",
                "is_title_derived",
                "is_llm_enriched",
                "tags",
                "entities",
                "relations",
                "provenance",
            ],
        }
        plan.layout.distill_schema.write_text(
            json.dumps(schema_payload, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        return units

    def run_pipeline(
        self,
        plan: IngestPlan,
        *,
        distilled_units: Optional[List[DistilledUnit]] = None,
        llmwiki_adapter: Optional[LLMWikiAdapter] = None,
        graphrag_adapter: Optional[GraphRAGAdapter] = None,
    ) -> List[AdapterResult]:
        """Run downstream engine adapters from one ingest plan.

        This method intentionally orchestrates only the handoff contract.
        Extraction, normalization, distillation, llmwiki compilation, and
        graphrag internals remain in their own modules.
        """
        self.ensure_layout()
        units = distilled_units or []
        results: List[AdapterResult] = []

        if EngineTarget.LLMWIKI in plan.targets:
            if llmwiki_adapter is None:
                results.append(
                    AdapterResult(
                        engine="llmwiki",
                        status="skipped",
                        meta={"reason": "no_llmwiki_adapter"},
                    )
                )
            else:
                results.append(llmwiki_adapter.compile(plan, units))

        if EngineTarget.GRAPHRAG in plan.targets:
            if graphrag_adapter is None:
                results.append(
                    AdapterResult(
                        engine="graphrag",
                        status="skipped",
                        meta={"reason": "no_graphrag_adapter"},
                    )
                )
            else:
                results.append(graphrag_adapter.index(plan, units))

        return results

    def run_default_pipeline(
        self,
        plan: IngestPlan,
        *,
        distilled_units: Optional[List[DistilledUnit]] = None,
    ) -> List[AdapterResult]:
        """Run the default local adapters for both engines."""
        units = distilled_units if distilled_units is not None else self.build_distilled_units(plan)
        return self.run_pipeline(
            plan,
            distilled_units=units,
            llmwiki_adapter=LLMWikiEngineAdapter(),
            graphrag_adapter=GraphRAGWorkspaceAdapter(execution_owner=plan.graphrag_execution_owner),
        )

    def run_default_pipeline_and_refresh_summary(
        self,
        plan: IngestPlan,
        *,
        distilled_units: Optional[List[DistilledUnit]] = None,
    ) -> List[AdapterResult]:
        """Run default adapters and persist a post-run summary snapshot."""
        results = self.run_default_pipeline(plan, distilled_units=distilled_units)
        self.write_summary_files(plan)
        return results

    def query(
        self,
        query_text: str,
        *,
        mode: QueryMode = QueryMode.HYBRID,
        top_k: int = 8,
    ) -> QueryResponse:
        if mode == QueryMode.LLMWIKI:
            return self.query_llmwiki(query_text, top_k=top_k)
        if mode == QueryMode.GRAPHRAG:
            return self.query_graphrag(query_text, top_k=top_k)

        llmwiki_result = self.query_llmwiki(query_text, top_k=top_k)
        graphrag_result = self.query_graphrag(query_text, top_k=top_k)
        answer_lines = [
            f"LLMWiki pages: {len(llmwiki_result.hits)} hits",
            f"GraphRAG entities/units: {len(graphrag_result.hits)} hits",
        ]
        if llmwiki_result.hits:
            answer_lines.append(f"Top wiki result: {llmwiki_result.hits[0].title}")
        if graphrag_result.hits:
            answer_lines.append(f"Top graph result: {graphrag_result.hits[0].title}")
        return QueryResponse(
            mode=QueryMode.HYBRID,
            query=query_text,
            answer="\n".join(answer_lines),
            hits=llmwiki_result.hits[:top_k] + graphrag_result.hits[:top_k],
            engine_payloads={
                "llmwiki": llmwiki_result.engine_payloads.get("llmwiki", self._query_response_to_dict(llmwiki_result)),
                "graphrag": graphrag_result.engine_payloads.get("graphrag", self._query_response_to_dict(graphrag_result)),
            },
        )

    def get_graph_snapshot(self, *, max_nodes: int = 120) -> Dict[str, Any]:
        """Return graph nodes, edges, communities, and summary stats."""
        from app.graphrag.service import read_workspace_graph_snapshot

        snapshot = read_workspace_graph_snapshot(self.workspace, max_nodes=max_nodes)
        snapshot = self._apply_quality_plan_to_graph_snapshot(snapshot)
        return self._attach_graph_quality_diagnostics(snapshot)

    def query_llmwiki(self, query_text: str, *, top_k: int = 8, scope: str = "hybrid") -> QueryResponse:
        engine = WikiEngine(self._build_llmwiki_config())
        result = engine.search(query_text, top_k=top_k, scope=scope)
        hits: List[QueryHit] = []
        for page in result.get("pages", [])[:top_k]:
            hits.append(
                QueryHit(
                    title=str(page.get("title") or page.get("result_id") or "page"),
                    snippet=str(page.get("snippet") or page.get("body_md") or "")[:280],
                    source=str(page.get("result_id") or ""),
                    score=float(page.get("score") or 0.0),
                    meta={"kind": "page", "slug": page.get("result_id")},
                )
            )
        for passage in result.get("passages", [])[:top_k]:
            hits.append(
                QueryHit(
                    title=str(passage.get("title") or passage.get("source_id") or "passage"),
                    snippet=str(passage.get("snippet") or passage.get("text") or "")[:280],
                    source=str(passage.get("source_id") or ""),
                    score=float(passage.get("score") or 0.0),
                    meta={"kind": "passage", "passage_id": passage.get("result_id")},
                )
            )
        answer = f"LLMWiki returned {len(result.get('pages', []))} pages and {len(result.get('passages', []))} passages."
        response = QueryResponse(
            mode=QueryMode.LLMWIKI,
            query=query_text,
            answer=answer,
            hits=hits[:top_k],
            engine_payloads={"llmwiki": result},
        )
        return self._apply_quality_plan_to_llmwiki_query_response(response, top_k=top_k)

    def query_graphrag(self, query_text: str, *, top_k: int = 8) -> QueryResponse:
        from app.graphrag.service import query_workspace_graph

        payload = query_workspace_graph(self.workspace, query_text, top_k=top_k)
        payload = self._apply_quality_plan_to_graph_query_payload(payload)
        if payload.get("status") == "missing_db":
            return QueryResponse(
                mode=QueryMode.GRAPHRAG,
                query=query_text,
                answer="GraphRAG index not found.",
                hits=[],
                engine_payloads={"graphrag": payload},
            )

        hits = [
            QueryHit(
                title=item["title"],
                snippet=item["snippet"],
                source=item["source"],
                score=float(item.get("score", 0.0)),
                meta=dict(item.get("meta", {})),
            )
            for item in payload.get("hits", [])[:top_k]
        ]
        answer_parts = [
            f"GraphRAG matched {len(payload.get('nodes', []))} nodes, {len(payload.get('edges', []))} relationships, and {len(payload.get('units', []))} supporting units."
        ]
        if payload.get("nodes"):
            answer_parts.append("Top entities: " + ", ".join(item["name"] for item in payload["nodes"][:5]))
        return QueryResponse(
            mode=QueryMode.GRAPHRAG,
            query=query_text,
            answer=" ".join(answer_parts),
            hits=hits[:top_k],
            engine_payloads={"graphrag": payload},
        )

    def read_llmwiki_page(self, slug: str) -> Dict[str, Any]:
        engine = WikiEngine(self._build_llmwiki_config())
        return self._apply_quality_plan_to_llmwiki_page(engine.read_page(slug))

    def _build_llmwiki_config(self) -> LLMWikiConfig:
        return LLMWikiConfig(
            workspace_path=self.workspace,
            vault_path=self.layout.raw_dir,
            db_path=self.layout.llmwiki_state_dir / "llmwiki.db",
            markdown_output_dir=self.layout.llmwiki_pages_dir,
            normalized_output_dir=self.layout.normalized_dir,
            readable_docs_dir=self.layout.readable_dir,
            summary_path=self.layout.summary_md,
        )

    @classmethod
    def _expand_source_paths(cls, paths: Iterable[str]) -> List[Path]:
        resolved: List[Path] = []
        seen: Set[Path] = set()
        for raw_path in paths:
            candidate = Path(raw_path).expanduser().resolve()
            if candidate.is_dir():
                for nested in sorted(candidate.rglob("*")):
                    resolved_nested = nested.resolve()
                    if not cls._is_relative_to(resolved_nested, candidate):
                        continue
                    if cls._should_include_path(resolved_nested) and resolved_nested not in seen:
                        resolved.append(resolved_nested)
                        seen.add(resolved_nested)
                continue
            if cls._should_include_path(candidate) and candidate not in seen:
                resolved.append(candidate)
                seen.add(candidate)
        return resolved

    @staticmethod
    def _is_relative_to(path: Path, root: Path) -> bool:
        try:
            path.relative_to(root)
            return True
        except ValueError:
            return False

    @classmethod
    def _should_include_path(cls, path: Path) -> bool:
        if not path.exists() or not path.is_file():
            return False
        if any(part.startswith(".") for part in path.parts):
            return False
        return path.suffix.lower() in cls.SUPPORTED_SOURCE_SUFFIXES

    @classmethod
    def _source_format_profile(cls, path: Path) -> Dict[str, Any]:
        suffix = path.suffix.lower()
        source_format = suffix.lstrip(".") or "unknown"
        extractor_name = ""
        extractor_available = False
        try:
            from app.llmwiki.extractors import get_extractor

            extractor = get_extractor(str(path))
        except Exception:
            extractor = None
        if extractor:
            extractor_name = extractor.__class__.__name__
            extractor_available = True
        return {
            "source_format": source_format,
            "suffix": suffix,
            "supported_by_data_service": suffix in cls.SUPPORTED_SOURCE_SUFFIXES,
            "extractor_name": extractor_name,
            "extractor_available": extractor_available,
        }

    @staticmethod
    def _extract_markdown_title(path: Path) -> str:
        try:
            for line in path.read_text(encoding="utf-8").splitlines():
                stripped = line.strip()
                if stripped.startswith("#"):
                    return stripped.lstrip("#").strip()
        except OSError:
            pass
        return path.stem

    @staticmethod
    def _query_response_to_dict(response: QueryResponse) -> dict:
        return {
            "mode": response.mode.value,
            "query": response.query,
            "answer": response.answer,
            "hits": [
                {
                    "title": hit.title,
                    "snippet": hit.snippet,
                    "source": hit.source,
                    "score": hit.score,
                    "meta": hit.meta,
                }
                for hit in response.hits
            ],
            "engine_payloads": response.engine_payloads,
        }

    @staticmethod
    def _is_graph_entity_node(node: Dict[str, Any]) -> bool:
        node_type = str(node.get("node_type") or node.get("type") or "").strip().lower()
        return node_type != "theme"

    def _graph_node_counts(self, nodes: List[Dict[str, Any]]) -> Dict[str, int]:
        entity_count = sum(1 for node in nodes if self._is_graph_entity_node(node))
        theme_count = sum(1 for node in nodes if not self._is_graph_entity_node(node))
        return {"entity_count": entity_count, "theme_count": theme_count}

    @classmethod
    def _attach_graph_quality_diagnostics(cls, snapshot: Dict[str, Any]) -> Dict[str, Any]:
        result = dict(snapshot)
        result["quality_diagnostics"] = cls._build_graph_quality_diagnostics(
            nodes=list(result.get("nodes", []) or []),
            edges=list(result.get("edges", []) or []),
            communities=list(result.get("communities", []) or []),
        )
        return result

    @classmethod
    def _build_graph_quality_diagnostics(
        cls,
        *,
        nodes: List[Dict[str, Any]],
        edges: List[Dict[str, Any]],
        communities: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        degree_by_node: Dict[str, int] = defaultdict(int)
        for edge in edges:
            source = str(edge.get("source", "")).strip()
            target = str(edge.get("target", "")).strip()
            if source:
                degree_by_node[source] += 1
            if target:
                degree_by_node[target] += 1

        top_communities = [
            cls._graph_diagnostic_item(
                kind="community",
                target=community,
                reason="top_community",
                severity="info",
                suggested_action="needs_review",
            )
            for community in sorted(
                communities,
                key=lambda item: (
                    float(item.get("score") or item.get("stats", {}).get("score") or 0.0),
                    int(item.get("entity_count") or item.get("stats", {}).get("entity_count") or 0),
                    int(item.get("relationship_count") or item.get("stats", {}).get("relationship_count") or 0),
                ),
                reverse=True,
            )[:8]
        ]
        weak_communities = [
            cls._graph_diagnostic_item(
                kind="community",
                target=community,
                reason="weak_community",
                severity="warning",
                suggested_action="needs_review",
            )
            for community in communities
            if int(community.get("relationship_count") or community.get("stats", {}).get("relationship_count") or 0) == 0
            or int(community.get("entity_count") or community.get("stats", {}).get("entity_count") or 0) <= 1
        ][:20]
        isolated_nodes = [
            cls._graph_diagnostic_item(
                kind="node",
                target=node,
                reason="isolated_node",
                severity="warning",
                suggested_action="mark_noise",
            )
            for node in nodes
            if degree_by_node.get(str(node.get("id", "")).strip(), 0) == 0
        ][:20]
        low_value_nodes = [
            cls._graph_diagnostic_item(
                kind="node",
                target=node,
                reason="low_value_node",
                severity="info",
                suggested_action="needs_review",
            )
            for node in nodes
            if cls._is_low_value_graph_node(node)
        ][:20]
        return {
            "schema_version": "1.0",
            "top_communities": top_communities,
            "weak_communities": weak_communities,
            "isolated_nodes": isolated_nodes,
            "low_value_nodes": low_value_nodes,
            "summary": {
                "top_community_count": len(top_communities),
                "weak_community_count": len(weak_communities),
                "isolated_node_count": len(isolated_nodes),
                "low_value_node_count": len(low_value_nodes),
            },
        }

    @classmethod
    def _graph_diagnostic_item(
        cls,
        *,
        kind: str,
        target: Dict[str, Any],
        reason: str,
        severity: str,
        suggested_action: str,
    ) -> Dict[str, Any]:
        target_id = str(target.get("id", "")).strip()
        label = str(target.get("title") or target.get("name") or target.get("label") or target_id).strip()
        target_type = "community" if kind == "community" else "entity"
        return {
            "id": target_id,
            "title": label,
            "name": label,
            "reason": reason,
            "severity": severity,
            "target_type": target_type,
            "metrics": {
                "score": target.get("score") or target.get("stats", {}).get("score"),
                "entity_count": target.get("entity_count") or target.get("stats", {}).get("entity_count"),
                "relationship_count": target.get("relationship_count") or target.get("stats", {}).get("relationship_count"),
                "document_count": target.get("document_count"),
                "weighted_count": target.get("weighted_count") or target.get("count"),
            },
            "feedback_target": {
                "target_type": target_type,
                "target_id": target_id,
                "label": label,
                "suggested_action": suggested_action,
                "reason": reason,
            },
        }

    @classmethod
    def _is_low_value_graph_node(cls, node: Dict[str, Any]) -> bool:
        document_count = int(node.get("document_count") or 0)
        weighted_count = float(node.get("weighted_count") or node.get("count") or 0.0)
        return cls._is_graph_entity_node(node) and document_count <= 1 and weighted_count <= 1.0

    def _apply_quality_plan_to_llmwiki_query_response(self, response: QueryResponse, *, top_k: int) -> QueryResponse:
        policy = self._build_quality_plan_policy("llmwiki")
        if not policy["applied_actions"]:
            return response
        hits: List[QueryHit] = []
        suppressed_hits: List[Dict[str, Any]] = []
        rewritten_hits: List[Dict[str, Any]] = []
        for hit in response.hits:
            source = str(hit.source or "").strip()
            title = str(hit.title or "").strip()
            if self._quality_policy_matches(policy, source, title, hit.snippet):
                suppressed_hits.append({"title": title, "source": source, "reason": "suppressed_by_quality_plan"})
                continue
            rewritten_title = self._apply_quality_policy_to_text(hit.title, policy)
            rewritten_snippet = self._apply_quality_policy_to_text(hit.snippet, policy)
            meta = dict(hit.meta or {})
            if rewritten_title != hit.title or rewritten_snippet != hit.snippet:
                meta["quality_rewritten"] = True
                meta["quality_original_title"] = hit.title
                rewritten_hits.append(
                    {
                        "source": source,
                        "original_title": hit.title,
                        "title": rewritten_title,
                        "reason": "rewritten_by_quality_plan",
                    }
                )
            hits.append(
                QueryHit(
                    title=rewritten_title,
                    snippet=rewritten_snippet,
                    source=hit.source,
                    score=hit.score,
                    meta=meta,
                )
            )
        payload = dict(response.engine_payloads.get("llmwiki", {}) or {})
        payload["quality_plan"] = {
            "schema_version": policy["schema_version"],
            "generated_at": policy["generated_at"],
            "applied_action_count": len(policy["applied_actions"]),
            "query_hit_impact": {
                "suppressed_count": len(suppressed_hits),
                "rewritten_count": len(rewritten_hits),
                "suppressed_hits": suppressed_hits[:20],
                "rewritten_hits": rewritten_hits[:20],
            },
            "actions": policy["applied_actions"][:20],
        }
        answer = response.answer
        if suppressed_hits or rewritten_hits:
            answer = f"{answer} Quality plan filtered {len(suppressed_hits)} hits and rewrote {len(rewritten_hits)} hits."
        return QueryResponse(
            mode=response.mode,
            query=response.query,
            answer=answer,
            hits=hits[:top_k],
            engine_payloads={"llmwiki": payload},
        )

    def _apply_quality_plan_to_graph_snapshot(self, snapshot: Dict[str, Any]) -> Dict[str, Any]:
        policy = self._build_quality_plan_policy("graphrag")
        if not policy["applied_actions"]:
            return snapshot

        if not policy["suppress_targets"] and not policy["rename_targets"] and not policy["merge_targets"]:
            return snapshot

        original_nodes = list(snapshot.get("nodes", []) or [])
        canonical_node_by_name = {
            str(node.get("name") or node.get("label") or "").strip(): str(node.get("id", "")).strip()
            for node in original_nodes
            if str(node.get("name") or node.get("label") or "").strip() and str(node.get("id", "")).strip()
        }
        filtered_nodes: List[Dict[str, Any]] = []
        suppressed_node_ids: Set[str] = set()
        merged_node_aliases: Dict[str, str] = {}
        for node in original_nodes:
            node_id = str(node.get("id", "")).strip()
            node_name = str(node.get("name") or node.get("label") or "").strip()
            if self._quality_policy_matches(policy, node_id, node_name):
                suppressed_node_ids.add(node_id)
                continue
            replacement = self._quality_policy_replacement(policy, node_id, node_name)
            if replacement:
                merge_target = self._quality_policy_merge_replacement(policy, node_id, node_name)
                canonical_id = canonical_node_by_name.get(replacement)
                if merge_target and canonical_id and canonical_id != node_id:
                    merged_node_aliases[node_id] = canonical_id
                    continue
                node = dict(node)
                node["name"] = replacement
                node["label"] = replacement
                node["quality_alias_of"] = node_name or node_id
                if merge_target:
                    node["quality_merge_target"] = replacement
            filtered_nodes.append(node)

        filtered_edges: List[Dict[str, Any]] = []
        seen_edges: Set[tuple[str, str, str]] = set()
        for edge in list(snapshot.get("edges", []) or []):
            source = str(edge.get("source", "")).strip()
            target = str(edge.get("target", "")).strip()
            if source in suppressed_node_ids or target in suppressed_node_ids:
                continue
            edge = dict(edge)
            edge["source"] = merged_node_aliases.get(source, source)
            edge["target"] = merged_node_aliases.get(target, target)
            edge_key = (str(edge["source"]), str(edge["target"]), str(edge.get("label") or edge.get("relation") or ""))
            if edge_key in seen_edges:
                continue
            seen_edges.add(edge_key)
            filtered_edges.append(edge)
        filtered_communities: List[Dict[str, Any]] = []
        for community in list(snapshot.get("communities", []) or []):
            community = dict(community)
            community_id = str(community.get("id", "")).strip()
            community_title = str(community.get("title", "")).strip()
            if self._quality_policy_matches(policy, community_id, community_title):
                continue
            replacement = self._quality_policy_replacement(policy, community_id, community_title)
            if replacement:
                community["title"] = replacement
                community["quality_alias_of"] = community_title or community_id
            entity_ids = [
                merged_node_aliases.get(str(entity_id).strip(), str(entity_id).strip())
                for entity_id in list(community.get("entity_ids", []) or [])
                if str(entity_id).strip() not in suppressed_node_ids
            ]
            community["entity_ids"] = list(dict.fromkeys(entity_ids))
            community["node_ids"] = community["entity_ids"]
            community["entity_count"] = len(community["entity_ids"])
            filtered_communities.append(community)

        result = dict(snapshot)
        result["nodes"] = filtered_nodes
        result["edges"] = filtered_edges
        result["communities"] = filtered_communities
        result["quality_plan"] = {
            "schema_version": policy["schema_version"],
            "generated_at": policy["generated_at"],
            "applied_action_count": len(policy["applied_actions"]),
            "suppressed_node_count": len(suppressed_node_ids),
            "merged_node_count": len(merged_node_aliases),
            "actions": policy["applied_actions"][:20],
        }
        node_counts = self._graph_node_counts(filtered_nodes)
        result["stats"] = {
            **dict(result.get("stats", {}) or {}),
            **node_counts,
            "relationship_count": len(filtered_edges),
            "community_count": len(filtered_communities),
        }
        return result

    def _apply_quality_plan_to_graph_query_payload(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        policy = self._build_quality_plan_policy("graphrag")
        if not policy["applied_actions"] or payload.get("status") == "missing_db":
            return payload

        original_nodes = list(payload.get("nodes", []) or [])
        canonical_node_by_name = {
            str(node.get("name") or node.get("label") or "").strip(): str(node.get("id", "")).strip()
            for node in original_nodes
            if str(node.get("name") or node.get("label") or "").strip() and str(node.get("id", "")).strip()
        }
        suppressed_node_ids: Set[str] = set()
        merged_node_aliases: Dict[str, str] = {}
        nodes: List[Dict[str, Any]] = []
        for node in original_nodes:
            node_id = str(node.get("id", "")).strip()
            node_name = str(node.get("name") or node.get("label") or "").strip()
            if self._quality_policy_matches(policy, node_id, node_name):
                suppressed_node_ids.add(node_id)
                continue
            replacement = self._quality_policy_replacement(policy, node_id, node_name)
            if replacement:
                merge_target = self._quality_policy_merge_replacement(policy, node_id, node_name)
                canonical_id = canonical_node_by_name.get(replacement)
                if merge_target and canonical_id and canonical_id != node_id:
                    merged_node_aliases[node_id] = canonical_id
                    continue
                node = dict(node)
                node["name"] = replacement
                node["label"] = replacement
                node["quality_alias_of"] = node_name or node_id
                if merge_target:
                    node["quality_merge_target"] = replacement
            nodes.append(node)

        edges: List[Dict[str, Any]] = []
        seen_edges: Set[tuple[str, str, str]] = set()
        for edge in list(payload.get("edges", []) or []):
            source = str(edge.get("source", "")).strip()
            target = str(edge.get("target", "")).strip()
            if source in suppressed_node_ids or target in suppressed_node_ids:
                continue
            edge = dict(edge)
            edge["source"] = merged_node_aliases.get(source, source)
            edge["target"] = merged_node_aliases.get(target, target)
            edge_key = (str(edge["source"]), str(edge["target"]), str(edge.get("label") or edge.get("relation") or ""))
            if edge_key in seen_edges:
                continue
            seen_edges.add(edge_key)
            edges.append(edge)
        hits: List[Dict[str, Any]] = []
        suppressed_hits: List[Dict[str, Any]] = []
        rewritten_hits: List[Dict[str, Any]] = []
        for hit in list(payload.get("hits", []) or []):
            source = str(hit.get("source", "")).strip()
            title = str(hit.get("title", "")).strip()
            if source in suppressed_node_ids or self._quality_policy_matches(policy, source, title):
                suppressed_hits.append(
                    {
                        "title": title,
                        "source": source,
                        "reason": "suppressed_by_quality_plan",
                    }
                )
                continue
            hit = dict(hit)
            original_title = str(hit.get("title", ""))
            original_snippet = str(hit.get("snippet", ""))
            rewritten_title = self._apply_quality_policy_to_text(original_title, policy)
            rewritten_snippet = self._apply_quality_policy_to_text(original_snippet, policy)
            if rewritten_title != original_title or rewritten_snippet != original_snippet:
                rewritten_hits.append(
                    {
                        "source": source,
                        "original_title": original_title,
                        "title": rewritten_title,
                        "original_snippet": original_snippet,
                        "snippet": rewritten_snippet,
                        "reason": "rewritten_by_quality_plan",
                    }
                )
                hit["quality_rewritten"] = True
                hit["quality_original_title"] = original_title
            hit["title"] = rewritten_title
            hit["snippet"] = rewritten_snippet
            hits.append(hit)

        result = dict(payload)
        result["nodes"] = nodes
        result["edges"] = edges
        result["hits"] = hits
        if "communities" in result:
            communities: List[Dict[str, Any]] = []
            for community in list(result.get("communities", []) or []):
                community = dict(community)
                community_id = str(community.get("id", "")).strip()
                community_title = str(community.get("title", "")).strip()
                if self._quality_policy_matches(policy, community_id, community_title):
                    continue
                replacement = self._quality_policy_replacement(policy, community_id, community_title)
                if replacement:
                    community["title"] = replacement
                    community["quality_alias_of"] = community_title or community_id
                entity_ids = [
                    merged_node_aliases.get(str(entity_id).strip(), str(entity_id).strip())
                    for entity_id in list(community.get("entity_ids", []) or [])
                    if str(entity_id).strip() not in suppressed_node_ids
                ]
                community["entity_ids"] = list(dict.fromkeys(entity_ids))
                community["node_ids"] = community["entity_ids"]
                community["entity_count"] = len(community["entity_ids"])
                communities.append(community)
            result["communities"] = communities
        result["quality_plan"] = {
            "schema_version": policy["schema_version"],
            "generated_at": policy["generated_at"],
            "applied_action_count": len(policy["applied_actions"]),
            "suppressed_node_count": len(suppressed_node_ids),
            "merged_node_count": len(merged_node_aliases),
            "query_hit_impact": {
                "suppressed_count": len(suppressed_hits),
                "rewritten_count": len(rewritten_hits),
                "suppressed_hits": suppressed_hits[:20],
                "rewritten_hits": rewritten_hits[:20],
            },
            "actions": policy["applied_actions"][:20],
        }
        node_counts = self._graph_node_counts(nodes)
        result["stats"] = {
            **dict(result.get("stats", {}) or {}),
            **node_counts,
            "relationship_count": len(edges),
        }
        return result

    def _apply_quality_plan_to_llmwiki_page(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        policy = self._build_quality_plan_policy("llmwiki")
        if not policy["applied_actions"] or not payload.get("page"):
            return payload

        result = dict(payload)
        page = dict(result.get("page", {}) or {})
        page_slug = str(page.get("slug", "")).strip()
        page_title = str(page.get("title", "")).strip()
        suppressed = self._quality_policy_matches(policy, page_slug, page_title)
        for field in ("title", "summary", "body_md"):
            if field in page and isinstance(page.get(field), str):
                page[field] = self._apply_quality_policy_to_text(page[field], policy)
        if suppressed:
            page["quality_suppressed"] = True
        result["page"] = page

        for collection_name in ("sources", "citations", "backlinks"):
            collection = []
            for item in list(result.get(collection_name, []) or []):
                if not isinstance(item, dict):
                    collection.append(item)
                    continue
                item = dict(item)
                item_id = str(item.get("source_id") or item.get("slug") or item.get("id") or "").strip()
                item_label = str(item.get("title") or item.get("label") or item.get("name") or "").strip()
                if self._quality_policy_matches(policy, item_id, item_label):
                    item["quality_suppressed"] = True
                for field in ("title", "label", "name", "snippet"):
                    if field in item and isinstance(item.get(field), str):
                        item[field] = self._apply_quality_policy_to_text(item[field], policy)
                collection.append(item)
            result[collection_name] = collection

        result["quality_plan"] = {
            "schema_version": policy["schema_version"],
            "generated_at": policy["generated_at"],
            "applied_action_count": len(policy["applied_actions"]),
            "page_suppressed": suppressed,
            "actions": policy["applied_actions"][:20],
        }
        return result

    def _build_quality_plan_policy(self, engine: str) -> Dict[str, Any]:
        plan = self._read_json_file(self.layout.quality_correction_plan_json)
        actions = list(plan.get("actions", []) or []) if plan else []
        suppress_targets: Set[str] = set()
        rename_targets: Dict[str, str] = {}
        merge_targets: Dict[str, str] = {}
        applied_actions: List[Dict[str, Any]] = []
        for action in actions:
            if engine not in set(action.get("target_engines", []) or []):
                continue
            target_id = str(action.get("target_id", "")).strip()
            current_label = str(action.get("current_label", "")).strip()
            proposed_value = str(action.get("proposed_value", "")).strip()
            keys = {item for item in (target_id, current_label) if item}
            if action.get("action") == "suppress_target":
                suppress_targets.update(keys)
            elif action.get("action") == "rename_target" and proposed_value:
                for key in keys:
                    rename_targets[key] = proposed_value
            elif action.get("action") == "merge_target" and proposed_value:
                for key in keys:
                    merge_targets[key] = proposed_value
            applied_actions.append(
                {
                    "action_id": action.get("action_id"),
                    "action": action.get("action"),
                    "target_id": target_id,
                }
            )
        return {
            "schema_version": plan.get("schema_version", "1.0") if plan else "1.0",
            "generated_at": plan.get("generated_at", "") if plan else "",
            "suppress_targets": suppress_targets,
            "rename_targets": rename_targets,
            "merge_targets": merge_targets,
            "applied_actions": applied_actions,
        }

    @classmethod
    def _quality_policy_matches(cls, policy: Dict[str, Any], *values: str) -> bool:
        targets = set(policy.get("suppress_targets", set()) or set())
        return any(str(value or "").strip() in targets for value in values if str(value or "").strip())

    @classmethod
    def _quality_policy_replacement(cls, policy: Dict[str, Any], *values: str) -> str:
        rename_targets = dict(policy.get("rename_targets", {}) or {})
        merge_targets = dict(policy.get("merge_targets", {}) or {})
        for value in values:
            key = str(value or "").strip()
            if key in rename_targets:
                return str(rename_targets[key])
            if key in merge_targets:
                return str(merge_targets[key])
        return ""

    @classmethod
    def _quality_policy_merge_replacement(cls, policy: Dict[str, Any], *values: str) -> str:
        merge_targets = dict(policy.get("merge_targets", {}) or {})
        for value in values:
            key = str(value or "").strip()
            if key in merge_targets:
                return str(merge_targets[key])
        return ""

    @classmethod
    def _apply_quality_policy_to_text(cls, text: str, policy: Dict[str, Any]) -> str:
        result = str(text)
        replacements = {
            **dict(policy.get("rename_targets", {}) or {}),
            **dict(policy.get("merge_targets", {}) or {}),
        }
        for old, new in sorted(replacements.items(), key=lambda item: len(item[0]), reverse=True):
            if old and new:
                result = result.replace(str(old), str(new))
        return result

    @classmethod
    def _clean_title_meta(cls, stem: str) -> tuple[str, List[str]]:
        cleaned = re.sub(
            r"^[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}[-_ ]*",
            "",
            stem,
            flags=re.IGNORECASE,
        )
        flags: List[str] = []
        for pattern, flag in cls.TITLE_MARKER_PATTERNS:
            if pattern.search(cleaned):
                flags.append(flag)
                cleaned = pattern.sub("", cleaned)
        cleaned = cleaned.replace("_", " ").replace("-", " ").strip()
        cleaned = re.sub(r"\s+", " ", cleaned).strip(" -_")
        return (cleaned or stem, flags)

    @classmethod
    def _resolve_source_title(cls, path: Path) -> tuple[str, List[str]]:
        fallback_title, fallback_flags = cls._clean_title_meta(path.stem)
        inner_title = cls._read_inner_title(path)
        if not inner_title:
            return fallback_title, fallback_flags
        cleaned_title, inner_flags = cls._clean_title_meta(inner_title)
        return cleaned_title, cls._dedupe_preserve(fallback_flags + inner_flags)

    @classmethod
    def _read_inner_title(cls, path: Path) -> str:
        try:
            suffix = path.suffix.lower()
            if suffix in {".md", ".markdown", ".txt", ".text"}:
                for line in path.read_text(encoding="utf-8").splitlines():
                    stripped = line.strip()
                    if stripped.startswith("#"):
                        return stripped.lstrip("#").strip()
            if suffix == ".json":
                data = json.loads(path.read_text(encoding="utf-8"))
                if isinstance(data, dict):
                    for key in ("title", "name", "topic", "subject"):
                        value = data.get(key)
                        if isinstance(value, str) and value.strip():
                            return value.strip()
        except (OSError, json.JSONDecodeError):
            return ""
        return ""

    @staticmethod
    def _first_sentence(text: str) -> str:
        match = re.split(r"(?<=[。！？.!?])\s+", text.strip(), maxsplit=1)
        return match[0].strip()[:280] if match and match[0].strip() else ""

    @classmethod
    def _extract_tags(cls, title: str, excerpt: str) -> List[str]:
        title_only_excerpt = excerpt.strip() == title.strip() and bool(title.strip())
        title_entities = cls._extract_title_entities(title)
        if title_only_excerpt:
            if title_entities:
                return cls._dedupe_preserve(title_entities, validator=cls._is_meaningful_tag)[:8]
            cleaned_title = cls._clean_theme_candidate(title)
            if cls._is_meaningful_tag(cleaned_title):
                return [cleaned_title]
            return []
        combined = f"{title} {excerpt}"
        candidates = re.findall(r"[A-Za-z][A-Za-z0-9.+_-]{2,}|[\u4e00-\u9fff]{2,8}", combined)
        seen = set()
        tags: List[str] = []
        for token in title_entities:
            normalized = token.lower()
            if normalized in seen or not cls._is_meaningful_tag(token):
                continue
            seen.add(normalized)
            tags.append(token)
        for token in candidates:
            cleaned = cls._clean_entity_candidate(token.strip())
            normalized = cleaned.lower()
            if normalized in seen or not cls._is_meaningful_tag(cleaned):
                continue
            seen.add(normalized)
            tags.append(cleaned)
            if len(tags) >= 12:
                break
        return tags

    @classmethod
    def _is_meaningful_tag(cls, value: str) -> bool:
        token = cls._normalize_token(value)
        if not token or token in cls.ENTITY_STOPWORDS:
            return False
        if cls._looks_like_noise_phrase(token):
            return False
        if re.fullmatch(r"\d+", token):
            return False
        if len(token) <= 1:
            return False
        return True

    @classmethod
    def _is_meaningful_entity(cls, value: str) -> bool:
        token = cls._normalize_token(value)
        if not token or token in cls.ENTITY_STOPWORDS:
            return False
        if any(fragment in token for fragment in cls.ENTITY_REJECT_SUBSTRINGS):
            return False
        if cls._looks_like_noise_phrase(token):
            return False
        if token.startswith("废弃于") or token.endswith("废弃于"):
            return False
        if token.startswith("中的"):
            return False
        if len(token) < 2:
            return False
        if re.fullmatch(r"[0-9.]+", token):
            return False
        if re.fullmatch(r"\d+[\u4e00-\u9fff]{1,4}", token):
            return False
        if re.fullmatch(r"[\u4e00-\u9fff]+", token) and len(token) > 8:
            return False
        if re.fullmatch(r"[\u4e00-\u9fff]{2,3}", token) and token in cls.GENERIC_CN_SHORT_TOKENS:
            return False
        return True

    @classmethod
    def _is_meaningful_theme(cls, value: str) -> bool:
        token = cls._normalize_token(cls._clean_theme_candidate(value))
        if not token or token in cls.THEME_STOPWORDS:
            return False
        if cls._looks_like_noise_phrase(token):
            return False
        if token.startswith("废弃于") or token.endswith("废弃于"):
            return False
        if token.startswith("表") and re.search(r"\d", token):
            return False
        if "试验流程" in token or "流程表" in token or "建库" in token:
            return False
        if re.fullmatch(r"\d+[\u4e00-\u9fff]{1,6}", token):
            return False
        if re.fullmatch(r"\d+岁[\u4e00-\u9fff]{0,8}", token):
            return False
        if re.fullmatch(r"[\u4e00-\u9fff]{2,3}", token) and token in cls.GENERIC_CN_SHORT_TOKENS:
            return False
        if re.fullmatch(r"[\u4e00-\u9fff]{9,}", token) and not any(ch in token for ch in ("ai", "llm", "mcp", "etf")):
            return False
        return len(token) >= 2

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

    @staticmethod
    def _normalize_token(value: str) -> str:
        normalized = re.sub(r"\s+", " ", str(value or "")).strip().lower()
        normalized = re.sub(r"[^0-9a-z\u4e00-\u9fff ._+-]", "", normalized)
        return normalized.strip(" ._+-")

    @classmethod
    def _dedupe_preserve(cls, values: Iterable[str], validator=None) -> List[str]:
        seen: Set[str] = set()
        items: List[str] = []
        for raw in values:
            text = str(raw or "").strip()
            if not text:
                continue
            normalized = cls._normalize_token(text)
            if not normalized or normalized in seen:
                continue
            if validator and not validator(text):
                continue
            seen.add(normalized)
            items.append(text)
        return items

    @classmethod
    def _extract_entity_candidates(cls, title: str, excerpt: str, title_flags: List[str]) -> List[str]:
        candidates: List[str] = []
        title_only_excerpt = excerpt.strip() == title.strip() and bool(title.strip())
        title_entities = cls._extract_title_entities(title)
        if title_only_excerpt and title_entities:
            candidates.extend(title_entities)
        for token in re.findall(r"[A-Z][A-Za-z0-9.+_-]{2,}|[A-Za-z]{3,}(?:[A-Z][A-Za-z0-9]+)+|[\u4e00-\u9fff]{2,12}", f"{title} {excerpt}"):
            token = cls._clean_title_entity_candidate(token.strip()) if title_only_excerpt else cls._clean_entity_candidate(token.strip())
            if not token:
                continue
            if "status_marker" in title_flags and "废弃于" in token:
                continue
            candidates.append(token)
        return cls._compact_entity_candidates(cls._dedupe_preserve(candidates, validator=cls._is_meaningful_entity))

    @classmethod
    def _extract_title_entities(cls, title: str) -> List[str]:
        english_term = re.search(r"\bclarification on ([A-Za-z][A-Za-z0-9.+_-]{2,}) term\b", title, flags=re.IGNORECASE)
        if english_term:
            term = english_term.group(1).strip()
            if cls._is_meaningful_entity(term):
                return [term]
        special_entities = [
            ("退休资金", "退休资金"),
            ("管培生", "管培生"),
            ("云南菜", "云南菜"),
            ("车企", "车企"),
            ("智能卡片", "智能卡片"),
            ("香农极限", "香农极限"),
            ("端午节", "端午节"),
        ]
        matched_specials = [
            entity for marker, entity in special_entities
            if marker in title and cls._is_meaningful_entity(entity)
        ]
        if matched_specials:
            return cls._dedupe_preserve(matched_specials, validator=cls._is_meaningful_entity)
        cleaned_title = cls._clean_theme_candidate(title)
        if not cleaned_title:
            return []
        prefix = re.split(
            r"(?:的?(?:区别|用途|建议|选择|原因|小组赛时间|并网时间|宜居年限|上市进展|股权结构|背景介绍|代码示例|选项验证|时间|数据|进展|来源|概念|特点|解析|对比|说明|方法|流程|含义|作用|应用|岗位|名称来源|就诊科室|股东情况|年限|推荐|案例|注意事项|评价|专利|确保|充足).*)",
            cleaned_title,
            maxsplit=1,
        )[0].strip()
        if prefix:
            cleaned_title = prefix
        cleaned_title = re.sub(r"(建设及|上市进展及|上市|进展及|小组赛|就诊科室|建设|并网|选择建议|概念及|特点解析|及用途|及特点|宜居|周末小众游)$", "", cleaned_title).strip()
        if not cleaned_title:
            return []
        parts = [part.strip() for part in cls.TITLE_ENTITY_SPLIT_PATTERN.split(cleaned_title) if part.strip()]
        if not parts:
            parts = [cleaned_title]
        entities: List[str] = []
        for part in parts:
            candidate = cls._clean_title_entity_candidate(part)
            if cls._is_meaningful_entity(candidate):
                entities.append(candidate)
        fallback_candidate = cls._clean_title_entity_candidate(cleaned_title)
        if not entities and cls._is_meaningful_entity(fallback_candidate):
            entities.append(fallback_candidate)
        return cls._dedupe_preserve(entities, validator=cls._is_meaningful_entity)

    @classmethod
    def _clean_title_entity_candidate(cls, value: str) -> str:
        text = cls._clean_entity_candidate(value)
        if not text:
            return ""
        text = re.sub(r"^(?:停止工作)?确保退休资金充足$", "退休资金", text)
        text = re.sub(r"^生成两份(.+?)评价$", r"\1", text)
        text = re.sub(r"^跨设备智能卡片交互系统专利$", "智能卡片交互系统", text)
        for pattern in cls.TITLE_ENTITY_SUFFIX_PATTERNS:
            text = pattern.sub("", text).strip()
        text = re.sub(r"^(?:已安装|安装)([A-Za-z][A-Za-z0-9.+_-]{2,})$", r"\1", text, flags=re.IGNORECASE)
        text = re.sub(r"([\u4e00-\u9fff]{2,12})(?:App|APP|app|应用)$", r"\1", text)
        embedded_latin = re.match(r"^[\u4e00-\u9fff]{2,12}([A-Za-z][A-Za-z0-9.+_-]{3,})$", text)
        if embedded_latin and len(re.findall(r"[A-Za-z]", embedded_latin.group(1))) >= 4:
            text = embedded_latin.group(1)
        text = re.sub(r"\s+", " ", text).strip(" -_")
        return text

    @classmethod
    def _build_title_normalization_debug(
        cls,
        title: str,
        *,
        title_only_excerpt: bool,
        entity_candidates: List[str],
        theme_labels: List[str],
    ) -> Dict[str, Any]:
        normalized_entities = cls._dedupe_preserve(entity_candidates, validator=cls._is_meaningful_entity)
        normalized_themes = cls._dedupe_preserve(theme_labels, validator=cls._is_meaningful_theme)
        dropped_fragments = [
            fragment
            for fragment in cls.TITLE_NORMALIZATION_NOISE_FRAGMENTS
            if fragment in title and fragment not in normalized_entities and fragment not in normalized_themes
        ]
        rules: List[str] = []
        if title_only_excerpt:
            rules.append("title_only_source")
        if title.startswith(("已安装", "安装")) and not any(candidate.startswith(("已安装", "安装")) for candidate in normalized_entities):
            rules.append("install_status_removed")
        if any(fragment in dropped_fragments for fragment in ("选项验证", "自动化测试代码示例", "测试代码示例", "代码示例", "自动化测试", "股权结构", "背景介绍", "玻璃防晒性能")):
            rules.append("functional_suffix_removed")
        if re.match(r"^[A-Za-z][A-Za-z0-9.+_-]+中的", title) and any(re.fullmatch(r"[A-Za-z][A-Za-z0-9.+_-]+", candidate) for candidate in normalized_entities):
            rules.append("latin_prefix_kept")
        if any(re.fullmatch(r"[A-Za-z][A-Za-z0-9.+_-]+", candidate) and candidate in title for candidate in normalized_entities):
            rules.append("latin_core_kept")
        if normalized_entities and any(candidate != title for candidate in normalized_entities):
            rules.append("title_contracted_to_core_entity")
        if normalized_themes and set(map(cls._normalize_token, normalized_themes)).issubset(set(map(cls._normalize_token, normalized_entities))):
            rules.append("theme_aligned_to_entity")
        return {
            "raw_title": title,
            "title_only_excerpt": title_only_excerpt,
            "normalized_entities": normalized_entities[:10],
            "normalized_themes": normalized_themes[:10],
            "dropped_fragments": cls._dedupe_preserve(dropped_fragments),
            "rules_applied": cls._dedupe_preserve(rules),
        }

    @classmethod
    def _extract_theme_labels(
        cls,
        title: str,
        excerpt: str,
        entity_candidates: List[str],
        *,
        title_only_excerpt: bool = False,
    ) -> List[str]:
        labels: List[str] = []
        title_lower = title.lower()
        theme_patterns = [
            ("ai学习", ["ai学习", "人工智能", "机器学习", "llm", "模型", "agent", "claudecode", "openclaw"]),
            ("投资", ["投资", "股票", "基金", "估值", "财报", "股东", "核电", "养老金", "航天公司"]),
            ("宏观政策", ["政策", "医保", "养老金", "宏观", "财政", "就业", "退休"]),
            ("软件开发", ["开发", "代码", "github", "接口", "前端", "后端", "数据库", "mcp"]),
        ]
        if not title_only_excerpt:
            for label, keywords in theme_patterns:
                if any(keyword.lower() in title_lower or keyword.lower() in excerpt.lower() for keyword in keywords):
                    labels.append(label)
        labels.extend(candidate for candidate in entity_candidates[:4] if cls._is_strong_theme_candidate(candidate))
        cleaned_title = cls._clean_theme_candidate(title)
        if cleaned_title and cls._is_meaningful_theme(cleaned_title) and (not title_only_excerpt or not entity_candidates):
            labels.append(cleaned_title)
        return cls._compact_theme_labels(labels)

    @classmethod
    def _is_strong_theme_candidate(cls, value: str) -> bool:
        cleaned = cls._clean_theme_candidate(value)
        token = cls._normalize_token(cleaned)
        if not cls._is_meaningful_theme(cleaned):
            return False
        if re.search(r"[A-Z]", value):
            return True
        if re.search(r"[a-z]", token):
            return True
        if re.fullmatch(r"[\u4e00-\u9fff]{4,10}", token) and token.endswith(("公司", "世界杯")):
            return True
        return len(token) <= 6

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

    @classmethod
    def _clean_entity_candidate(cls, value: str) -> str:
        text = str(value or "").strip()
        cleaned = cls._clean_theme_candidate(text)
        return cleaned or text

    @classmethod
    def _compact_theme_labels(cls, labels: List[str]) -> List[str]:
        items = [label for label in labels if label]
        compacted: List[str] = []
        for label in items:
            normalized = cls._normalize_token(label)
            drop = False
            for other in items:
                if other == label:
                    continue
                other_normalized = cls._normalize_token(other)
                if not normalized or not other_normalized:
                    continue
                if len(normalized) >= 6 and other_normalized.startswith(normalized) and len(other_normalized) > len(normalized) and re.search(r"[A-Z0-9]", other):
                    drop = True
                    break
                if (
                    re.fullmatch(r"[a-z0-9.+_-]{2,6}", normalized)
                    and other_normalized.endswith(normalized)
                    and re.search(r"[\u4e00-\u9fff]", other_normalized)
                ):
                    drop = True
                    break
            if not drop:
                compacted.append(label)
        return compacted

    @classmethod
    def _compact_entity_candidates(cls, entities: List[str]) -> List[str]:
        items = [entity for entity in entities if entity]
        compacted: List[str] = []
        for entity in items:
            normalized = cls._normalize_token(entity)
            if cls._has_generic_theme_suffix(entity) and not re.search(r"[A-Z0-9]", entity):
                continue
            drop = False
            for other in items:
                if other == entity:
                    continue
                other_normalized = cls._normalize_token(other)
                if not normalized or not other_normalized:
                    continue
                if len(normalized) >= 6 and other_normalized.startswith(normalized) and len(other_normalized) > len(normalized) and re.search(r"[A-Z0-9]", other):
                    drop = True
                    break
                if (
                    re.fullmatch(r"[a-z0-9.+_-]{2,6}", normalized)
                    and other_normalized.endswith(normalized)
                    and re.search(r"[\u4e00-\u9fff]", other_normalized)
                ):
                    drop = True
                    break
                if (
                    len(normalized) >= 2
                    and len(normalized) <= 4
                    and re.fullmatch(r"[\u4e00-\u9fff]+", normalized)
                    and other_normalized.startswith(normalized)
                    and len(other_normalized) > len(normalized)
                    and re.search(r"[a-z0-9]", other_normalized)
                ):
                    drop = True
                    break
            if not drop:
                compacted.append(entity)
        return compacted

    @classmethod
    def _has_generic_theme_suffix(cls, value: str) -> bool:
        text = str(value or "").strip()
        return any(pattern.search(text) for pattern in cls.THEME_SUFFIX_PATTERNS)

    @classmethod
    def _build_source_profile(cls, path: Path, title: str, full_text: str) -> Dict[str, Any]:
        sentences = cls._split_sentences(full_text)
        questions = [sentence for sentence in sentences if cls._looks_like_question(sentence)]
        steps = [sentence for sentence in sentences if cls._looks_like_step(sentence)]
        risks = [sentence for sentence in sentences if cls._looks_like_risk(sentence)]
        examples = [sentence for sentence in sentences if cls._looks_like_example(sentence)]
        fact_candidates = [
            sentence
            for sentence in sentences
            if cls._looks_like_fact_candidate(sentence) and not cls._looks_like_step(sentence)
        ]
        scored_sentences = sorted(sentences, key=lambda sentence: (-cls._sentence_score(sentence), len(sentence)))
        summary_sentences = cls._dedupe_preserve(scored_sentences, validator=lambda value: len(value.strip()) >= 12)[:6]
        conclusions = cls._dedupe_preserve(
            [sentence for sentence in summary_sentences if not cls._looks_like_question(sentence)],
            validator=lambda value: len(value.strip()) >= 12,
        )[:4]
        facts = cls._dedupe_preserve(
            fact_candidates + [sentence for sentence in conclusions if cls._looks_like_fact_candidate(sentence)],
            validator=lambda value: len(value.strip()) >= 12,
        )[:3]
        note_sentences = cls._dedupe_preserve(
            [
                sentence
                for sentence in summary_sentences
                if sentence not in conclusions[:2]
                and sentence not in questions[:2]
                and sentence not in steps[:3]
                and sentence not in risks[:2]
            ],
            validator=lambda value: len(value.strip()) >= 12,
        )[:6]
        density_inputs = {
            "text_length": len(full_text),
            "sentence_count": len(sentences),
            "question_count": len(questions),
            "step_count": len(steps),
            "entity_hint_count": len(cls._extract_entity_candidates(title, full_text[:4000], [])),
        }
        density_score = min(
            4.5,
            1.0
            + density_inputs["text_length"] / 2600.0
            + density_inputs["sentence_count"] / 28.0
            + density_inputs["entity_hint_count"] / 10.0
            + density_inputs["question_count"] / 5.0,
        )
        source_weight = min(4.8, 0.9 + density_score * 0.82)
        return {
            "excerpt": full_text[:2400],
            "sentences": sentences,
            "sentence_count": len(sentences),
            "note_sentences": note_sentences,
            "questions": questions,
            "steps": steps,
            "summary_sentences": summary_sentences,
            "conclusions": conclusions,
            "risks": risks,
            "examples": examples,
            "facts": facts,
            "density_score": round(density_score, 4),
            "source_weight": round(source_weight, 4),
        }

    @classmethod
    def _split_sentences(cls, text: str) -> List[str]:
        collapsed = re.sub(r"\s+", " ", text).strip()
        if not collapsed:
            return []
        parts = re.split(r"(?<=[。！？.!?])\s+|(?<=；)\s+", collapsed)
        return [
            part.strip()[:320]
            for part in parts
            if len(part.strip()) >= 8 and not cls._is_low_signal_sentence(part.strip())
        ]

    @staticmethod
    def _looks_like_question(sentence: str) -> bool:
        lowered = sentence.lower()
        return "?" in sentence or "？" in sentence or any(token in lowered for token in ["如何", "怎么", "是否", "what", "why", "how"])

    @classmethod
    def _derive_title_fallback_question(cls, title: str) -> Optional[str]:
        cleaned = str(title or "").strip()
        if not cleaned:
            return None
        if cls._looks_like_question(cleaned):
            return cleaned
        if any(marker in cleaned for marker in cls.TITLE_QUESTION_HINTS):
            return cleaned
        return None

    @classmethod
    def _title_focus_subject(cls, title: str, entities: List[str]) -> str:
        if entities:
            return "、".join(entities[:2])
        cleaned = cls._clean_theme_candidate(title)
        return cleaned or title

    @classmethod
    def _derive_title_fallback_note(cls, title: str, entities: List[str]) -> Optional[str]:
        cleaned = str(title or "").strip()
        if not cleaned:
            return None
        subject = cls._title_focus_subject(cleaned, entities)
        if any(marker in cleaned for marker in ("建议", "推荐", "选择")):
            return f"该 source 主要围绕{subject}相关建议。"
        if any(marker in cleaned for marker in ("解析", "分析", "概念", "特点")):
            return f"该 source 主要围绕{subject}的概念或分析。"
        if any(marker in cleaned for marker in ("确保", "充足")):
            return f"该 source 主要围绕{subject}的规划或充足性判断。"
        if "案例" in cleaned:
            return f"该 source 主要围绕{subject}相关案例。"
        if "评价" in cleaned:
            return f"该 source 主要围绕{subject}相关评价。"
        if any(marker in cleaned for marker in ("专利", "应用")):
            return f"该 source 主要围绕{subject}的技术或应用。"
        if cleaned.endswith("相关") and subject:
            return f"该 source 主要围绕{subject}相关信息。"
        if any(marker in cleaned.lower() for marker in ("clarification", "term")):
            return f"该 source 主要围绕{subject}术语澄清。"
        return None

    @classmethod
    def _derive_title_fallback_fact(cls, title: str, entities: List[str]) -> Optional[str]:
        cleaned = str(title or "").strip()
        if not cleaned:
            return None
        subject = cls._title_focus_subject(cleaned, entities)
        if any(marker in cleaned for marker in ("数据", "进展", "时间", "来源", "含义", "专利", "应用")):
            return f"该 source 关注{subject}的数据或进展信息。"
        return None

    @classmethod
    def _derive_title_fallback_risk(cls, title: str, entities: List[str]) -> Optional[str]:
        cleaned = str(title or "").strip()
        if not cleaned:
            return None
        subject = cls._title_focus_subject(cleaned, entities)
        if any(marker in cleaned for marker in ("风险", "限制", "报错", "问题", "排查", "注意事项")):
            return f"该 source 涉及{subject}的风险、限制或问题排查。"
        return None

    @staticmethod
    def _looks_like_step(sentence: str) -> bool:
        lowered = sentence.lower()
        return bool(
            re.match(r"^\d+[.)、]", sentence)
            or lowered.startswith(("先", "然后", "最后", "step", "步骤", "第一", "第二", "接着", "随后"))
        )

    @classmethod
    def _looks_like_risk(cls, sentence: str) -> bool:
        lowered = sentence.lower()
        markers = ["风险", "注意", "不要", "避免", "否则", "失败", "报错", "限制", "问题", "警惕"]
        return any(marker in sentence for marker in markers) or any(marker in lowered for marker in ["error", "fail", "risk", "warning", "avoid"])

    @classmethod
    def _looks_like_example(cls, sentence: str) -> bool:
        lowered = sentence.lower()
        markers = ["例如", "比如", "举例", "案例", "像", "包括"]
        return any(marker in sentence for marker in markers) or "for example" in lowered

    @classmethod
    def _looks_like_fact_candidate(cls, sentence: str) -> bool:
        lowered = sentence.lower()
        if cls._looks_like_question(sentence):
            return False
        markers = ["是", "需要", "必须", "可以", "用于", "意味着", "支持", "包含"]
        en_markers = ["requires", "supports", "means", "includes", "works with", "is "]
        return any(marker in sentence for marker in markers) or any(marker in lowered for marker in en_markers)

    @staticmethod
    def _sentence_score(sentence: str) -> float:
        score = len(sentence) / 80.0
        if "。" in sentence or "." in sentence:
            score += 0.2
        if any(token in sentence.lower() for token in ["需要", "建议", "应该", "requires", "install", "配置"]):
            score += 0.35
        if "?" in sentence or "？" in sentence:
            score -= 0.2
        return score

    @classmethod
    def _is_low_signal_sentence(cls, sentence: str) -> bool:
        text = re.sub(r"\s+", " ", sentence).strip()
        if not text:
            return True
        if len(text) < 8:
            return True
        if all(ch in ".,!?;:，。！？；：-_()[]{} " for ch in text):
            return True
        if any(pattern.match(text) for pattern in cls.LOW_SIGNAL_SENTENCE_PATTERNS):
            return True
        return False

    @staticmethod
    def _chunk_sentences(sentences: List[str], *, chunk_size: int, max_chunks: int) -> List[str]:
        chunks: List[str] = []
        for index in range(0, min(len(sentences), chunk_size * max_chunks), chunk_size):
            chunk = " ".join(sentences[index:index + chunk_size]).strip()
            if chunk:
                chunks.append(chunk[:720])
        return chunks

    @classmethod
    def _count_unit_kinds(cls, units: List[DistilledUnit]) -> Dict[str, int]:
        counts: Dict[str, int] = defaultdict(int)
        for unit in units:
            counts[unit.kind.value if hasattr(unit.kind, "value") else str(unit.kind)] += 1
        return dict(sorted(counts.items()))

    def _llm_enrich_source(
        self,
        *,
        title: str,
        excerpt: str,
        source_weight: float,
        source_density_score: float,
    ) -> Optional[Dict[str, List[str]]]:
        if source_density_score < self.HIGH_DENSITY_THRESHOLD or not excerpt.strip():
            return None
        client = build_llm_client(LLMWikiConfig.from_env())
        if not client.is_enabled():
            return None

        system_prompt = (
            "You extract only high-value theme labels and entity names from source text. "
            "Ignore status markers, dates, generic words, UI labels, and fragments. "
            "Return JSON with keys theme_labels and entities."
        )
        user_prompt = json.dumps(
            {
                "title": title,
                "excerpt": excerpt[:5000],
                "source_weight": source_weight,
                "source_density_score": source_density_score,
            },
            ensure_ascii=False,
        )
        try:
            response = client.complete_json(system_prompt, user_prompt)
            payload = json.loads(response.text)
        except (LLMClientError, json.JSONDecodeError, TypeError, ValueError):
            return None

        return {
            "theme_labels": self._dedupe_preserve(payload.get("theme_labels", []), validator=self._is_meaningful_theme),
            "entities": self._dedupe_preserve(payload.get("entities", []), validator=self._is_meaningful_entity),
        }

    @staticmethod
    def _infer_authority(path: Path) -> AuthorityLevel:
        suffix = path.suffix.lower()
        if suffix == ".json":
            return AuthorityLevel.SECONDARY_CHAT
        return AuthorityLevel.PRIMARY_DOC

    @staticmethod
    def _read_source_excerpt(path: Path, limit: int = 1200) -> str:
        if path.suffix.lower() in {".docx", ".yaml", ".yml"}:
            text = DataService._extract_source_text_via_llmwiki(path)
            if text:
                return re.sub(r"\s+", " ", text).strip()[:limit]

        try:
            raw = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            raw = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            return ""

        if path.suffix.lower() == ".json":
            try:
                payload = json.loads(raw)
            except json.JSONDecodeError:
                payload = None
            text = DataService._extract_json_text(payload) if payload is not None else raw
        else:
            text = raw

        text = re.sub(r"\s+", " ", text).strip()
        return text[:limit]

    @staticmethod
    def _extract_source_text_via_llmwiki(path: Path) -> str:
        try:
            from app.llmwiki.extractors import get_extractor
        except Exception:
            return ""

        extractor = get_extractor(str(path))
        if not extractor:
            return ""
        result = extractor.extract(str(path))
        if result.status != "success":
            return ""
        fragments = []
        for section in result.sections:
            title = str(section.title or "").strip()
            text = str(section.text or "").strip()
            if title:
                fragments.append(title)
            if text:
                fragments.append(text)
        return "\n".join(fragments)

    @classmethod
    def _extract_json_text(cls, payload: object) -> str:
        fragments: List[str] = []

        def visit(node: object) -> None:
            if node is None:
                return
            if isinstance(node, str):
                stripped = node.strip()
                if stripped and not cls._is_low_signal_sentence(stripped):
                    fragments.append(stripped)
                return
            if isinstance(node, list):
                for item in node:
                    visit(item)
                return
            if isinstance(node, dict):
                for key in ("title", "question", "answer", "text", "content", "summary"):
                    value = node.get(key)
                    if isinstance(value, str) and value.strip() and not cls._is_low_signal_sentence(value.strip()):
                        fragments.append(value.strip())
                content = node.get("content")
                if isinstance(content, dict):
                    for key in ("text", "content"):
                        value = content.get(key)
                        if isinstance(value, str) and value.strip() and not cls._is_low_signal_sentence(value.strip()):
                            fragments.append(value.strip())
                    parts = content.get("parts")
                    if isinstance(parts, list):
                        visit(parts)
                for key in ("turns", "messages", "items", "fragments", "mapping"):
                    value = node.get(key)
                    if value is not None:
                        visit(value)
                return

        visit(payload)
        joined = " ".join(fragments)
        return re.sub(r"\s+", " ", joined).strip()

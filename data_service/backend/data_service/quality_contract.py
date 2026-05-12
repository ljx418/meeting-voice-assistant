"""Shared quality contract helpers for HTTP and future CLI/MCP entrypoints."""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .service import DataService


LOW_SIGNAL_AUDIT_LIMIT_MIN = 1
LOW_SIGNAL_AUDIT_LIMIT_MAX = 100
LOW_SIGNAL_AUDIT_LIMIT_DEFAULT = 30
_SAFE_TITLE_DERIVED_KINDS = {"question", "note", "fact_candidate", "risk"}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _read_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return default


def normalize_low_signal_audit_limit(value: object, *, default: int = LOW_SIGNAL_AUDIT_LIMIT_DEFAULT) -> int:
    try:
        parsed = int(value if value is not None else default)
    except (TypeError, ValueError) as exc:
        raise ValueError("limit must be an integer") from exc
    if parsed < LOW_SIGNAL_AUDIT_LIMIT_MIN or parsed > LOW_SIGNAL_AUDIT_LIMIT_MAX:
        raise ValueError(f"limit must be between {LOW_SIGNAL_AUDIT_LIMIT_MIN} and {LOW_SIGNAL_AUDIT_LIMIT_MAX}")
    return parsed


def record_quality_feedback_payload(
    service: DataService,
    *,
    target_type: str,
    target_id: str,
    action: str,
    label: str = "",
    suggested_value: str = "",
    reason: str = "",
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    record = service.record_quality_feedback(
        target_type=target_type,
        target_id=target_id,
        action=action,
        label=label,
        suggested_value=suggested_value,
        reason=reason,
        metadata=metadata or {},
    )
    return {
        "workspace": str(service.workspace),
        "feedback": record,
        "summary": service.read_quality_feedback(limit=20)["summary"],
    }


def quality_feedback_list_payload(
    service: DataService,
    *,
    limit: int = 100,
    target_type: str | None = None,
    target_id: str | None = None,
) -> dict[str, Any]:
    return service.read_quality_feedback(
        limit=limit,
        target_type=target_type,
        target_id=target_id,
    )


def quality_correction_rules_payload(
    service: DataService,
    *,
    limit: int = 100,
    status: str | None = None,
) -> dict[str, Any]:
    return service.read_quality_correction_rules(limit=limit, status=status)


def quality_summary_payload(service: DataService) -> dict[str, Any]:
    bundle = service.read_summary_bundle()
    return {
        "workspace": str(service.workspace),
        "quality": bundle.get("quality", {}),
        "quality_feedback": bundle.get("quality_feedback", []),
        "quality_correction_rules": bundle.get("quality_correction_rules", []),
        "quality_correction_plan": bundle.get("quality_correction_plan", {}),
    }


def quality_correction_plan_preview_payload(service: DataService, *, rebuild: bool = False) -> dict[str, Any]:
    if rebuild:
        return service.build_quality_correction_plan()
    return service.read_quality_correction_plan(build_if_missing=False)


def quality_correction_rules_build_payload(service: DataService) -> dict[str, Any]:
    return service.build_quality_correction_rules()


def quality_correction_rule_review_payload(
    service: DataService,
    *,
    rule_id: str,
    status: str,
    reviewer: str = "",
    note: str = "",
) -> dict[str, Any]:
    return service.review_quality_correction_rule(
        rule_id=rule_id,
        status=status,
        reviewer=reviewer,
        note=note,
    )


def quality_correction_plan_payload(service: DataService) -> dict[str, Any]:
    return service.build_quality_correction_plan()


def _markdown_title(path: Path) -> str:
    try:
        for line in path.read_text(encoding="utf-8").splitlines():
            stripped = line.strip()
            if stripped.startswith("#"):
                return stripped.lstrip("#").strip()
    except OSError:
        pass
    return path.stem


def _source_low_signal(source: dict[str, Any]) -> dict[str, Any]:
    return dict(source.get("profile", {}).get("low_signal") or source.get("low_signal") or {})


def _title_like_terms(title: str) -> set[str]:
    text = str(title or "").strip()
    if not text:
        return set()
    terms = {text}
    stem = Path(text).stem
    if stem:
        terms.add(stem)
    without_uuid = re.sub(r"^[0-9a-fA-F-]{12,}[-_\\s]+", "", stem).strip()
    if without_uuid and len(without_uuid) >= 8:
        terms.add(without_uuid)
    return {term for term in terms if len(term) >= 8}


def low_signal_audit_payload(service: DataService, *, limit: object = LOW_SIGNAL_AUDIT_LIMIT_DEFAULT) -> dict[str, Any]:
    normalized_limit = normalize_low_signal_audit_limit(limit)
    service.ensure_layout()
    summary_bundle = service.read_summary_bundle()
    distill_bundle = service.read_distill_bundle(limit=200)
    distill_quality = dict(summary_bundle.get("quality", {}).get("distill", {}) or {})
    sources = list(distill_bundle.get("sources", []) or [])
    low_signal_sources = [source for source in sources if _source_low_signal(source)]
    low_signal_terms: dict[str, set[str]] = {
        str(source.get("source_id") or ""): _title_like_terms(str(source.get("title") or ""))
        for source in low_signal_sources
    }

    title_derived_conclusion_count = 0
    disallowed_title_derived_count = 0
    title_derived_kind_counts: dict[str, int] = {}
    title_derived_samples: list[dict[str, Any]] = []
    disallowed_samples: list[dict[str, Any]] = []
    scanned_source_count = 0

    if service.layout.distill_sources_dir.exists():
        for source_path in sorted(service.layout.distill_sources_dir.glob("*.json")):
            source_record = _read_json(source_path, {})
            if not source_record:
                continue
            scanned_source_count += 1
            for unit in source_record.get("units", []) or []:
                if not bool(unit.get("is_title_derived", False)):
                    continue
                kind = str(unit.get("kind") or "unknown")
                title_derived_kind_counts[kind] = title_derived_kind_counts.get(kind, 0) + 1
                sample = {
                    "source_id": source_record.get("source_id") or source_path.stem,
                    "source_title": source_record.get("title") or source_path.stem,
                    "unit_id": unit.get("unit_id"),
                    "kind": kind,
                    "text": str(unit.get("text") or unit.get("normalized_text") or "")[:220],
                }
                if len(title_derived_samples) < normalized_limit:
                    title_derived_samples.append(sample)
                if kind == "conclusion":
                    title_derived_conclusion_count += 1
                if kind not in _SAFE_TITLE_DERIVED_KINDS:
                    disallowed_title_derived_count += 1
                    if len(disallowed_samples) < normalized_limit:
                        disallowed_samples.append(sample)

    llmwiki_title_leaks: list[dict[str, Any]] = []
    if service.layout.llmwiki_pages_dir.exists() and low_signal_terms:
        for page_path in sorted(service.layout.llmwiki_pages_dir.glob("*.md")):
            page_title = _markdown_title(page_path)
            haystack = f"{page_path.stem}\n{page_title}"
            for source_id, terms in low_signal_terms.items():
                matched = next((term for term in terms if len(term) >= 18 and term in haystack), "")
                if matched:
                    source = next((item for item in low_signal_sources if str(item.get("source_id") or "") == source_id), {})
                    llmwiki_title_leaks.append(
                        {
                            "source_id": source_id,
                            "source_title": source.get("title"),
                            "page_slug": page_path.stem,
                            "page_title": page_title,
                            "matched_term": matched,
                        }
                    )
                    break
            if len(llmwiki_title_leaks) >= normalized_limit:
                break

    graph_snapshot = service.get_graph_snapshot(max_nodes=160)
    graph_quality = dict(graph_snapshot.get("quality_diagnostics", {}) or {})
    top_communities = list(graph_quality.get("top_communities", []) or graph_snapshot.get("communities", []) or [])
    graph_title_leaks: list[dict[str, Any]] = []
    for community in top_communities[:50]:
        label = str(community.get("title") or community.get("label") or community.get("name") or community.get("id") or "")
        if len(label) >= 36:
            graph_title_leaks.append({"community_id": community.get("id") or community.get("target_id"), "title": label, "reason": "long_community_title"})
            continue
        for source_id, terms in low_signal_terms.items():
            matched = next((term for term in terms if len(term) >= 18 and term in label), "")
            if matched:
                graph_title_leaks.append(
                    {
                        "community_id": community.get("id") or community.get("target_id"),
                        "title": label,
                        "source_id": source_id,
                        "matched_term": matched,
                        "reason": "low_signal_title_leak",
                    }
                )
                break
        if len(graph_title_leaks) >= normalized_limit:
            break

    checks = [
        {
            "check_id": "zero_unit_count",
            "label": "zero unit source",
            "status": "passed" if int(distill_quality.get("zero_unit_count", 0) or 0) == 0 else "failed",
            "actual": int(distill_quality.get("zero_unit_count", 0) or 0),
            "expected": 0,
        },
        {
            "check_id": "title_derived_conclusion_count",
            "label": "标题派生 conclusion",
            "status": "passed" if title_derived_conclusion_count == 0 else "failed",
            "actual": title_derived_conclusion_count,
            "expected": 0,
        },
        {
            "check_id": "disallowed_title_derived_kind_count",
            "label": "标题派生强语义 unit",
            "status": "passed" if disallowed_title_derived_count == 0 else "failed",
            "actual": disallowed_title_derived_count,
            "expected": 0,
            "allowed_kinds": sorted(_SAFE_TITLE_DERIVED_KINDS),
        },
        {
            "check_id": "llmwiki_low_signal_title_leak_count",
            "label": "LLMWiki 长标题泄漏",
            "status": "passed" if not llmwiki_title_leaks else "warning",
            "actual": len(llmwiki_title_leaks),
            "expected": 0,
        },
        {
            "check_id": "graphrag_low_signal_title_leak_count",
            "label": "GraphRAG 头部社区长标题泄漏",
            "status": "passed" if not graph_title_leaks else "warning",
            "actual": len(graph_title_leaks),
            "expected": 0,
        },
    ]
    failed_count = sum(1 for check in checks if check["status"] == "failed")
    warning_count = sum(1 for check in checks if check["status"] == "warning")
    overall_status = "failed" if failed_count else ("warning" if warning_count else "passed")
    recommendations = []
    if title_derived_conclusion_count or disallowed_title_derived_count:
        recommendations.append("收紧 title fallback：标题派生内容只允许 question / note / fact_candidate / risk。")
    if llmwiki_title_leaks:
        recommendations.append("抽查 LLMWiki 页面标题，将低信号 source 的原始长标题保留到 source trace，不作为 topic 标题。")
    if graph_title_leaks:
        recommendations.append("抽查 GraphRAG top communities，把长标题或功能尾缀主题降权、合并或标记为噪音。")
    if not recommendations:
        recommendations.append("当前低信号 source 审计未发现阻塞项，继续用真实知识库定期回归。")

    return {
        "workspace": str(service.workspace),
        "audited_at": _now(),
        "overall_status": overall_status,
        "checks": checks,
        "metrics": {
            "source_count": len(sources),
            "scanned_source_count": scanned_source_count,
            "low_signal_source_count": len(low_signal_sources),
            "zero_unit_count": int(distill_quality.get("zero_unit_count", 0) or 0),
            "title_fallback_source_count": int(distill_quality.get("title_fallback_source_count", 0) or 0),
            "title_fallback_source_counts": dict(distill_quality.get("title_fallback_source_counts", {}) or {}),
            "title_derived_unit_count": sum(title_derived_kind_counts.values()),
            "title_derived_kind_counts": dict(sorted(title_derived_kind_counts.items())),
            "title_derived_conclusion_count": title_derived_conclusion_count,
            "disallowed_title_derived_count": disallowed_title_derived_count,
            "llmwiki_title_leak_count": len(llmwiki_title_leaks),
            "graphrag_title_leak_count": len(graph_title_leaks),
        },
        "samples": {
            "title_derived": title_derived_samples,
            "disallowed_title_derived": disallowed_samples,
            "llmwiki_title_leaks": llmwiki_title_leaks,
            "graphrag_title_leaks": graph_title_leaks,
        },
        "recommendations": recommendations,
    }

"""V2.8 architecture context pack builder."""

from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from typing import Any


ALLOWED_MODES = {"project_brief", "task_context"}
SECTION_TITLES = [
    "Project Architecture Brief",
    "Relevant Views and Diagrams",
    "Ranked Architecture Signals",
    "Relevant Code Fact Chains",
    "Design Intent Evidence",
    "Drift, Risks, and Review Queue",
    "Suggested Tests",
    "Implementation Guidance",
    "Omitted Items",
    "Evidence Appendix",
]


def build_architecture_context_pack_v2(
    *,
    workspace_id: str,
    codebase_id: str,
    snapshot_id: str | None,
    mode: str,
    task: str | None,
    max_tokens: int,
    dashboard: dict[str, Any],
    graph: dict[str, Any],
    ranking: dict[str, Any],
    code_fact_chains: dict[str, Any],
    intent_evidence: dict[str, Any],
    artifact_refs: list[dict[str, str]],
) -> dict[str, Any]:
    normalized_mode = mode if mode in ALLOWED_MODES else "project_brief"
    pack_id = _stable_id("architecture-context-pack-v2", codebase_id, str(snapshot_id or ""), normalized_mode, str(task or ""), str(max_tokens))
    items = _items_from_sources(dashboard, graph, ranking, code_fact_chains, intent_evidence, task=task)
    sections = _sections(items)
    pack = {
        "schema_version": "v2.8",
        "workspace_id": workspace_id,
        "codebase_id": codebase_id,
        "snapshot_id": snapshot_id,
        "pack_id": pack_id,
        "mode": normalized_mode,
        "task": task if normalized_mode == "task_context" else None,
        "sections": sections,
        "items": items,
        "token_estimate": _estimate_tokens({"sections": sections, "items": items}),
        "max_tokens": max_tokens,
        "omitted_items": [],
        "source_artifact_refs": artifact_refs,
        "evidence_refs": _evidence_refs(items),
        "warnings": [],
        "unresolved": _unresolved(items),
        "confidence": _confidence(items),
        "created_at": _now(),
    }
    pack = _apply_budget(pack)
    pack["content"] = render_architecture_context_markdown(pack)
    pack["token_estimate"] = _estimate_tokens(pack["content"])
    return pack


def public_architecture_context_pack_v2_payload(pack: dict[str, Any]) -> dict[str, Any]:
    return dict(pack)


def render_architecture_context_markdown(pack: dict[str, Any]) -> str:
    lines = ["# Architecture Context Pack", ""]
    sections_by_title = {section["title"]: section for section in pack.get("sections", [])}
    for index, title in enumerate(SECTION_TITLES, start=1):
        lines.append(f"## {index}. {title}")
        section = sections_by_title.get(title, {"items": []})
        if title == "Omitted Items":
            for item in pack.get("omitted_items", []):
                lines.append(f"- {item.get('title')}: {item.get('reason')}")
        elif title == "Evidence Appendix":
            for ref in pack.get("evidence_refs", [])[:60]:
                lines.append(f"- {_safe(ref)}")
        else:
            for item in section.get("items", [])[:20]:
                review = " needs_review" if item.get("needs_review") else ""
                lines.append(f"- [{item.get('priority')}] {item.get('title')}{review}: {item.get('summary')}")
        lines.append("")
    return "\n".join(lines).strip() + "\n"


def _items_from_sources(
    dashboard: dict[str, Any],
    graph: dict[str, Any],
    ranking: dict[str, Any],
    code_fact_chains: dict[str, Any],
    intent_evidence: dict[str, Any],
    *,
    task: str | None,
) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    summary = dashboard.get("summary", {})
    items.append(
        _item(
            "project_brief",
            "Project architecture brief",
            f"{summary.get('target_node_count', 0)} target nodes, {summary.get('current_node_count', 0)} current nodes, {summary.get('diff_node_count', 0)} diff nodes.",
            "p0",
            dashboard.get("artifact_refs") or dashboard.get("source_artifact_refs") or [],
            dashboard.get("artifact_refs") or [],
            "Use the reading dashboard as the first human-facing architecture summary.",
            [],
        )
    )
    graph_summary = graph.get("summary", {})
    for view_id in graph_summary.get("view_ids", [])[:6]:
        items.append(
            _item(
                "graph_view",
                f"Graph view: {view_id}",
                f"Use {view_id} to inspect clustered architecture relationships.",
                "p1",
                graph.get("artifact_refs") or [],
                graph.get("artifact_refs") or [],
                "Open this view before manually traversing raw graph nodes.",
                [],
            )
        )
    ranking_items = ranking.get("ranking", {}).get("items", [])
    for rank in ranking_items[:40]:
        items.append(
            _item(
                "ranked_signal",
                str(rank.get("label") or rank.get("item_type") or "ranked signal"),
                f"Score {rank.get('score')} via {', '.join(rank.get('reason_codes') or [])}.",
                "p0" if rank.get("pinned") else "p1",
                rank.get("source_refs") or [],
                rank.get("evidence_refs") or [],
                "Review this signal before making architecture claims.",
                rank.get("needs_review") or ([] if rank.get("evidence_refs") else [{"code": "RANKING_EVIDENCE_REVIEW", "reason": "Ranked signal lacks direct evidence refs."}]),
            )
        )
    chains = code_fact_chains.get("chains", [])
    task_tokens = {token.lower() for token in str(task or "").replace("_", " ").split() if len(token) > 2}
    for chain in chains[:60]:
        label = str(chain.get("chain_type") or "code fact chain")
        if task_tokens and not any(token in label.lower() or token in str(chain.get("entry_ref") or "").lower() for token in task_tokens):
            priority = "p2"
        else:
            priority = "p1" if chain.get("status") == "accepted" else "p2"
        items.append(
            _item(
                "code_fact_chain",
                label,
                f"Status {chain.get('status')}; confidence {chain.get('confidence')}.",
                priority,
                [{"chain_id": chain.get("chain_id"), "chain_type": chain.get("chain_type")}],
                chain.get("evidence_refs") or [],
                "Use accepted chains as deterministic entry-point evidence; keep reviewable chains out of accepted claims.",
                chain.get("needs_review") or ([] if chain.get("evidence_refs") else [{"code": "CHAIN_EVIDENCE_REVIEW", "reason": "Chain has no direct evidence refs."}]),
            )
        )
    for intent in intent_evidence.get("intents", [])[:80]:
        items.append(
            _item(
                "intent_evidence",
                str(intent.get("label") or intent.get("intent_type") or "intent evidence"),
                f"Intent state {intent.get('intent_type')}; confidence {intent.get('confidence')}.",
                "p1" if intent.get("intent_type") in {"mismatch", "audit_accepted"} else "p2",
                [*intent.get("claim_refs", []), *intent.get("code_refs", []), *intent.get("audit_refs", [])],
                intent.get("evidence_refs") or [],
                "Keep documented intent, code-observed implementation, and mismatch states separate.",
                intent.get("needs_review") or ([] if (intent.get("evidence_refs") or intent.get("claim_refs") or intent.get("code_refs") or intent.get("audit_refs")) else [{"code": "INTENT_REVIEW_REQUIRED", "reason": "Intent has no supporting refs."}]),
            )
        )
    return sorted(items, key=lambda item: (_priority_sort(item["priority"]), item["item_id"]))[:260]


def _item(item_type: str, title: str, summary: str, priority: str, source_refs: list[dict[str, Any]], evidence_refs: list[dict[str, Any]], recommendation: str, needs_review: list[dict[str, Any]]) -> dict[str, Any]:
    if not evidence_refs and not needs_review:
        needs_review = [{"code": "RECOMMENDATION_EVIDENCE_REQUIRED", "reason": "Recommendation has no evidence refs."}]
    item = {
        "item_id": _stable_id("context-item", item_type, title, summary),
        "item_type": item_type,
        "title": title,
        "summary": summary,
        "priority": priority,
        "source_refs": source_refs[:8],
        "evidence_refs": evidence_refs[:8],
        "recommendation": recommendation,
        "needs_review": needs_review,
    }
    item["token_estimate"] = _estimate_tokens(item)
    return item


def _sections(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    sections = []
    section_map = {
        "project_brief": "Project Architecture Brief",
        "graph_view": "Relevant Views and Diagrams",
        "ranked_signal": "Ranked Architecture Signals",
        "code_fact_chain": "Relevant Code Fact Chains",
        "intent_evidence": "Design Intent Evidence",
    }
    for title in SECTION_TITLES[:8]:
        section_items = [item for item in items if section_map.get(item["item_type"]) == title]
        if title == "Drift, Risks, and Review Queue":
            section_items = [item for item in items if item["item_type"] == "ranked_signal" and item["priority"] == "p0"]
        elif title == "Suggested Tests":
            section_items = [
                _item("suggested_test", "Run focused architecture tests", "Run V2.8 focused tests and public surface guard before relying on the pack.", "p1", [], [{"type": "test_command", "command": "pytest backend/tests/test_v2_8_reading_dashboard.py backend/tests/test_public_surface_guard.py -q"}], "Run tests before implementing architecture changes.", [])
            ]
        elif title == "Implementation Guidance":
            section_items = [
                _item("implementation_guidance", "Preserve evidence boundaries", "Do not convert needs_review rows into accepted architecture facts.", "p0", [], [{"type": "policy", "ref": "V2.8 evidence preservation"}], "Treat missing evidence as review work, not implementation proof.", [])
            ]
        sections.append({"section_id": _stable_id("section", title), "title": title, "items": section_items[:30]})
    return sections


def _apply_budget(pack: dict[str, Any]) -> dict[str, Any]:
    max_tokens = int(pack.get("max_tokens") or 12000)
    if max_tokens < 800:
        pack["warnings"].append({"code": "ARCHITECTURE_CONTEXT_BUDGET_TOO_SMALL", "message": "Budget is very small; low-priority items were omitted."})
    items = list(pack.get("items", []))
    kept: list[dict[str, Any]] = []
    omitted: list[dict[str, Any]] = []
    budget_for_items = max(350, max_tokens - 450)
    used = 0
    for item in items:
        estimate = int(item.get("token_estimate") or 0)
        if used + estimate <= budget_for_items or item.get("priority") == "p0":
            if item.get("recommendation") and not item.get("evidence_refs") and not item.get("needs_review"):
                item = dict(item)
                item["needs_review"] = [{"code": "RECOMMENDATION_EVIDENCE_REQUIRED", "reason": "Recommendation retained only as reviewable because evidence is absent."}]
            kept.append(item)
            used += estimate
        else:
            omitted.append({"item_id": item.get("item_id"), "title": item.get("title"), "reason": "omitted_due_to_token_budget", "token_estimate": estimate})
    pack["items"] = kept
    pack["sections"] = _sections(kept)
    pack["omitted_items"] = omitted[:120]
    pack["evidence_refs"] = _evidence_refs(kept)
    pack["unresolved"] = _unresolved(kept)
    pack["confidence"] = _confidence(kept)
    pack["token_estimate"] = _estimate_tokens({"sections": pack["sections"], "items": kept})
    return pack


def _evidence_refs(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    refs: list[dict[str, Any]] = []
    seen: set[str] = set()
    for item in items:
        for ref in item.get("evidence_refs", []):
            key = repr(sorted(ref.items()))
            if key not in seen:
                seen.add(key)
                refs.append(ref)
    return refs[:160]


def _unresolved(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    unresolved = []
    for item in items:
        for review in item.get("needs_review", []):
            unresolved.append({"item_id": item.get("item_id"), "code": review.get("code"), "reason": review.get("reason")})
    return unresolved[:160]


def _confidence(items: list[dict[str, Any]]) -> float:
    if not items:
        return 0.0
    reviewed = sum(1 for item in items if item.get("needs_review"))
    return round(max(0.1, 1.0 - reviewed / max(1, len(items))), 2)


def _estimate_tokens(value: Any) -> int:
    return max(1, len(str(value)) // 4)


def _priority_sort(priority: str) -> int:
    return {"p0": 0, "p1": 1, "p2": 2}.get(priority, 3)


def _safe(value: Any) -> str:
    return str(value).replace("\n", " ")[:240]


def _stable_id(*parts: str) -> str:
    return hashlib.sha256(":".join(parts).encode("utf-8")).hexdigest()[:20]


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()

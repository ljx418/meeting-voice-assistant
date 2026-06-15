"""Diagram-to-claim parser for V2.26 Phase 92."""

from __future__ import annotations

import hashlib
import re
from collections import Counter
from pathlib import Path
from typing import Any

from data_service.mcp_common import now, read_json, write_json

from ..artifacts import read_jsonl, write_jsonl
from .paths import (
    architecture_intent_claim_artifact_refs,
    architecture_intent_diagram_cells_path,
    architecture_intent_diagram_claim_summary_path,
    architecture_intent_diagram_claims_path,
    architecture_intent_diagram_relations_path,
    architecture_intent_source_blocks_path,
)
from .source_model import SCHEMA_VERSION, redact_public_text


RELATION_TYPES = {
    "depends_on",
    "implements",
    "calls_claimed",
    "publishes",
    "consumes",
    "stores",
    "governs",
    "validates",
    "relates_to",
}


def build_diagram_claims(
    *,
    workspace: Path,
    workspace_id: str,
    codebase_id: str,
    snapshot_id: str,
) -> dict[str, Any]:
    created_at = now()
    cells = read_jsonl(architecture_intent_diagram_cells_path(workspace, codebase_id))
    blocks = read_jsonl(architecture_intent_source_blocks_path(workspace, codebase_id))
    claims: list[dict[str, Any]] = []
    relations: list[dict[str, Any]] = []

    cell_claim_by_raw: dict[tuple[str, str, str], str] = {}
    for cell in cells:
        if cell.get("cell_kind") not in {"node", "cell"}:
            continue
        label = redact_public_text(str(cell.get("label") or "")).strip()
        if not label:
            continue
        claim = make_claim(
            workspace_id=workspace_id,
            codebase_id=codebase_id,
            snapshot_id=snapshot_id,
            source_id=str(cell.get("source_id") or ""),
            label=label,
            claim_type=classify_claim(label),
            source_locator={
                "path": cell.get("path"),
                "diagram_page": cell.get("diagram_page"),
                "cell_id": cell.get("raw_cell_id"),
            },
            source_block_type="diagram_node",
            evidence=[{"type": "diagram_cell", "path": cell.get("path"), "diagram_page": cell.get("diagram_page"), "cell_id": cell.get("raw_cell_id"), "extractor": "architecture_intent_diagram_claims"}],
            confidence=min(float(cell.get("confidence") or 0.7), 0.7),
            created_at=created_at,
        )
        claims.append(claim)
        cell_claim_by_raw[(str(cell.get("path") or ""), str(cell.get("diagram_page_id") or ""), str(cell.get("raw_cell_id") or ""))] = claim["claim_id"]

    for cell in cells:
        if cell.get("cell_kind") != "edge":
            continue
        key_base = (str(cell.get("path") or ""), str(cell.get("diagram_page_id") or ""))
        source_claim_id = cell_claim_by_raw.get((*key_base, str(cell.get("raw_source") or "")))
        target_claim_id = cell_claim_by_raw.get((*key_base, str(cell.get("raw_target") or "")))
        label = redact_public_text(str(cell.get("label") or "")).strip()
        relation_type = classify_relation(label)
        needs_review = []
        confidence = 0.65
        if not label:
            needs_review.append({"code": "UNLABELED_DIAGRAM_EDGE", "reason": "Diagram edge has no explicit label; relation semantics require review."})
            confidence = 0.45
        if not source_claim_id or not target_claim_id:
            needs_review.append({"code": "UNRESOLVED_DIAGRAM_EDGE_ENDPOINT", "reason": "Edge source or target does not resolve to a parsed diagram node claim."})
            confidence = min(confidence, 0.4)
        relations.append(
            make_relation(
                workspace_id=workspace_id,
                codebase_id=codebase_id,
                snapshot_id=snapshot_id,
                source_id=str(cell.get("source_id") or ""),
                source_claim_id=source_claim_id,
                target_claim_id=target_claim_id,
                relation_type=relation_type,
                label=label,
                source_locator={"path": cell.get("path"), "diagram_page": cell.get("diagram_page"), "cell_id": cell.get("raw_cell_id")},
                evidence=[{"type": "diagram_edge", "path": cell.get("path"), "diagram_page": cell.get("diagram_page"), "cell_id": cell.get("raw_cell_id"), "extractor": "architecture_intent_diagram_claims"}],
                confidence=confidence,
                needs_review=needs_review,
                created_at=created_at,
            )
        )

    block_claims, block_relations = claims_from_blocks(workspace_id, codebase_id, snapshot_id, blocks, created_at)
    claims.extend(block_claims)
    relations.extend(block_relations)

    claims = sorted(_dedupe(claims, "claim_id"), key=lambda item: (str(item.get("source_locator", {}).get("path") or ""), str(item.get("label") or "")))
    relations = sorted(_dedupe(relations, "relation_id"), key=lambda item: (str(item.get("source_locator", {}).get("path") or ""), str(item.get("relation_type") or "")))
    summary = build_summary(workspace_id, codebase_id, snapshot_id, claims, relations, created_at)

    write_jsonl(architecture_intent_diagram_claims_path(workspace, codebase_id), claims)
    write_jsonl(architecture_intent_diagram_relations_path(workspace, codebase_id), relations)
    write_json(architecture_intent_diagram_claim_summary_path(workspace, codebase_id), summary)
    return {
        "schema_version": SCHEMA_VERSION,
        "workspace_id": workspace_id,
        "codebase_id": codebase_id,
        "snapshot_id": snapshot_id,
        "claims": claims,
        "relations": relations,
        "summary": summary,
        "artifact_refs": architecture_intent_claim_artifact_refs(codebase_id),
    }


def read_diagram_claims(*, workspace: Path, codebase_id: str) -> dict[str, Any]:
    summary = read_json(architecture_intent_diagram_claim_summary_path(workspace, codebase_id), {})
    return {
        "schema_version": summary.get("schema_version", SCHEMA_VERSION),
        "workspace_id": summary.get("workspace_id"),
        "codebase_id": codebase_id,
        "snapshot_id": summary.get("snapshot_id"),
        "claims": read_jsonl(architecture_intent_diagram_claims_path(workspace, codebase_id)),
        "relations": read_jsonl(architecture_intent_diagram_relations_path(workspace, codebase_id)),
        "summary": summary,
        "artifact_refs": architecture_intent_claim_artifact_refs(codebase_id),
    }


def claims_from_blocks(workspace_id: str, codebase_id: str, snapshot_id: str, blocks: list[dict[str, Any]], created_at: str) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    claims: list[dict[str, Any]] = []
    relations: list[dict[str, Any]] = []
    for block in blocks:
        block_type = str(block.get("block_type") or "")
        text = redact_public_text(str(block.get("text") or "")).strip()
        if not text:
            continue
        if block_type in {"mermaid", "plantuml"}:
            block_claims, block_relations = parse_diagram_text(workspace_id, codebase_id, snapshot_id, block, text, created_at)
            claims.extend(block_claims)
            relations.extend(block_relations)
            continue
        if block_type in {"heading", "bullet", "numbered_item", "table_row"} and is_architecture_text(text):
            claim_type = classify_claim(text)
            claims.append(
                make_claim(
                    workspace_id=workspace_id,
                    codebase_id=codebase_id,
                    snapshot_id=snapshot_id,
                    source_id=str(block.get("source_id") or ""),
                    label=text[:300],
                    claim_type=claim_type,
                    source_locator={"path": block.get("path"), "line_range": block.get("line_range")},
                    source_block_type=block_type,
                    evidence=[{"type": "source_block", "path": block.get("path"), "line_range": block.get("line_range"), "extractor": "architecture_intent_diagram_claims"}],
                    confidence=0.75 if claim_type not in {"unknown"} else 0.55,
                    created_at=created_at,
                )
            )
    return claims, relations


def parse_diagram_text(workspace_id: str, codebase_id: str, snapshot_id: str, block: dict[str, Any], text: str, created_at: str) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    claims: dict[str, dict[str, Any]] = {}
    relations: list[dict[str, Any]] = []
    for line in text.splitlines():
        stripped = line.strip().strip(";")
        if not stripped or stripped.lower().startswith(("graph ", "flowchart ", "@start", "@end")):
            continue
        match = re.match(r"(.+?)(-->|->|=>|--|\\.\\.|==>)(.+)", stripped)
        if match:
            left = normalize_diagram_label(match.group(1))
            right = normalize_diagram_label(match.group(3))
            if not left or not right:
                continue
            for label in (left, right):
                claims.setdefault(
                    label,
                    make_claim(
                        workspace_id=workspace_id,
                        codebase_id=codebase_id,
                        snapshot_id=snapshot_id,
                        source_id=str(block.get("source_id") or ""),
                        label=label,
                        claim_type=classify_claim(label),
                        source_locator={"path": block.get("path"), "line_range": block.get("line_range")},
                        source_block_type=str(block.get("block_type") or "diagram_text"),
                        evidence=[{"type": "diagram_text", "path": block.get("path"), "line_range": block.get("line_range"), "extractor": "architecture_intent_diagram_claims"}],
                        confidence=0.65,
                        created_at=created_at,
                    ),
                )
            relations.append(
                make_relation(
                    workspace_id=workspace_id,
                    codebase_id=codebase_id,
                    snapshot_id=snapshot_id,
                    source_id=str(block.get("source_id") or ""),
                    source_claim_id=claims[left]["claim_id"],
                    target_claim_id=claims[right]["claim_id"],
                    relation_type="relates_to",
                    label=stripped[:300],
                    source_locator={"path": block.get("path"), "line_range": block.get("line_range")},
                    evidence=[{"type": "diagram_text_relation", "path": block.get("path"), "line_range": block.get("line_range"), "extractor": "architecture_intent_diagram_claims"}],
                    confidence=0.6,
                    needs_review=[{"code": "DIAGRAM_TEXT_RELATION_SEMANTICS_WEAK", "reason": "Text diagram relation is document-claimed and not a runtime call."}],
                    created_at=created_at,
                )
            )
        elif is_architecture_text(stripped):
            label = normalize_diagram_label(stripped)
            claims.setdefault(
                label,
                make_claim(
                    workspace_id=workspace_id,
                    codebase_id=codebase_id,
                    snapshot_id=snapshot_id,
                    source_id=str(block.get("source_id") or ""),
                    label=label,
                    claim_type=classify_claim(label),
                    source_locator={"path": block.get("path"), "line_range": block.get("line_range")},
                    source_block_type=str(block.get("block_type") or "diagram_text"),
                    evidence=[{"type": "diagram_text", "path": block.get("path"), "line_range": block.get("line_range"), "extractor": "architecture_intent_diagram_claims"}],
                    confidence=0.55,
                    created_at=created_at,
                ),
            )
    return list(claims.values()), relations


def make_claim(
    *,
    workspace_id: str,
    codebase_id: str,
    snapshot_id: str,
    source_id: str,
    label: str,
    claim_type: str,
    source_locator: dict[str, Any],
    source_block_type: str,
    evidence: list[dict[str, Any]],
    confidence: float,
    created_at: str,
) -> dict[str, Any]:
    label = redact_public_text(label)
    needs_review = []
    if claim_type == "unknown":
        needs_review.append({"code": "UNKNOWN_CLAIM_TYPE", "reason": "Architecture claim type is ambiguous."})
    return {
        "schema_version": SCHEMA_VERSION,
        "workspace_id": workspace_id,
        "codebase_id": codebase_id,
        "snapshot_id": snapshot_id,
        "claim_id": stable_id("claim", snapshot_id, source_id, label, claim_type, source_locator),
        "source_id": source_id,
        "claim_type": claim_type,
        "label": label,
        "normalized_label": normalize_label(label),
        "source_locator": source_locator,
        "source_block_type": source_block_type,
        "status_hint": status_hint(label),
        "source_kind": "document_claim",
        "evidence": evidence,
        "confidence": round(confidence, 3),
        "needs_review": needs_review,
        "created_at": created_at,
    }


def make_relation(
    *,
    workspace_id: str,
    codebase_id: str,
    snapshot_id: str,
    source_id: str,
    source_claim_id: str | None,
    target_claim_id: str | None,
    relation_type: str,
    label: str,
    source_locator: dict[str, Any],
    evidence: list[dict[str, Any]],
    confidence: float,
    needs_review: list[dict[str, Any]] | None = None,
    created_at: str,
) -> dict[str, Any]:
    relation_type = relation_type if relation_type in RELATION_TYPES else "relates_to"
    label = redact_public_text(label)
    return {
        "schema_version": SCHEMA_VERSION,
        "workspace_id": workspace_id,
        "codebase_id": codebase_id,
        "snapshot_id": snapshot_id,
        "relation_id": stable_id("relation", snapshot_id, source_id, source_claim_id, target_claim_id, relation_type, label, source_locator),
        "source_id": source_id,
        "source_claim_id": source_claim_id,
        "target_claim_id": target_claim_id,
        "relation_type": relation_type,
        "label": label,
        "source_locator": source_locator,
        "source_kind": "document_claimed_relation",
        "semantic_limit": "not_runtime_call",
        "evidence": evidence,
        "confidence": round(confidence, 3),
        "needs_review": list(needs_review or []),
        "created_at": created_at,
    }


def build_summary(workspace_id: str, codebase_id: str, snapshot_id: str, claims: list[dict[str, Any]], relations: list[dict[str, Any]], created_at: str) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "workspace_id": workspace_id,
        "codebase_id": codebase_id,
        "snapshot_id": snapshot_id,
        "created_at": created_at,
        "claim_count": len(claims),
        "relation_count": len(relations),
        "claim_type_counts": dict(sorted(Counter(str(row.get("claim_type")) for row in claims).items())),
        "relation_type_counts": dict(sorted(Counter(str(row.get("relation_type")) for row in relations).items())),
        "needs_review_count": sum(1 for row in [*claims, *relations] if row.get("needs_review")),
        "artifact_refs": architecture_intent_claim_artifact_refs(codebase_id),
    }


def classify_claim(label: str) -> str:
    low = label.lower()
    if any(token in low for token in ("forbidden", "禁止", "不得", "不能", "不承诺", "out of scope")):
        return "forbidden_claim"
    if any(token in low for token in ("non-goal", "non goal", "非目标")):
        return "non_goal"
    if any(token in low for token in ("api", "mcp", "cli", "http", "surface", "interface", "入口")):
        return "public_interface"
    if any(token in low for token in ("quality", "gate", "acceptance", "验收", "门槛", "ci", "test")):
        return "quality_gate"
    if any(token in low for token in ("workflow", "flow", "工作流", "orchestration", "station", "agent")):
        return "workflow"
    if any(token in low for token in ("runtime", "executor", "运行时")):
        return "runtime"
    if any(token in low for token in ("adapter", "provider", "plugin", "sdk")):
        return "provider" if "provider" in low else "adapter"
    if any(token in low for token in ("storage", "store", "artifact", "asset", "evidence", "持久化")):
        return "storage"
    if any(token in low for token in ("layer", "plane", "层")):
        return "layer"
    if any(token in low for token in ("boundary", "bounded", "边界", "治理")):
        return "boundary"
    if any(token in low for token in ("phase", "milestone", "里程碑", "v2.")):
        return "milestone"
    if any(token in low for token in ("service", "engine", "system", "module", "component", "console", "dashboard", "report")):
        return "component"
    return "unknown"


def classify_relation(label: str) -> str:
    low = label.lower()
    if any(token in low for token in ("implement", "实现")):
        return "implements"
    if any(token in low for token in ("publish", "发布")):
        return "publishes"
    if any(token in low for token in ("consume", "订阅", "消费")):
        return "consumes"
    if any(token in low for token in ("store", "persist", "写入", "存储")):
        return "stores"
    if any(token in low for token in ("govern", "治理", "policy")):
        return "governs"
    if any(token in low for token in ("validate", "verify", "验收", "验证")):
        return "validates"
    if any(token in low for token in ("call", "调用")):
        return "calls_claimed"
    if any(token in low for token in ("depend", "依赖")):
        return "depends_on"
    return "relates_to"


def is_architecture_text(text: str) -> bool:
    low = text.lower()
    return any(
        token in low
        for token in (
            "architecture",
            "target",
            "runtime",
            "workflow",
            "agent",
            "mcp",
            "api",
            "cli",
            "provider",
            "adapter",
            "artifact",
            "governance",
            "quality",
            "boundary",
            "架构",
            "目标",
            "工作流",
            "能力",
            "治理",
            "边界",
            "验收",
            "禁止",
            "不承诺",
        )
    )


def status_hint(label: str) -> str:
    low = label.lower()
    if any(token in low for token in ("target", "目标")):
        return "target"
    if any(token in low for token in ("planned", "计划", "phase")):
        return "planned"
    if any(token in low for token in ("accepted", "pass", "通过", "完成")):
        return "current_or_accepted"
    if any(token in low for token in ("historical", "legacy", "deprecated", "历史")):
        return "historical"
    return "unknown"


def normalize_diagram_label(value: str) -> str:
    value = re.sub(r"\[[^\]]*\]", "", value)
    value = re.sub(r"\([^)]*\)", "", value)
    value = re.sub(r"[^A-Za-z0-9_./\-\u4e00-\u9fff ]+", " ", value)
    return redact_public_text(re.sub(r"\s+", " ", value).strip())


def normalize_label(value: str) -> str:
    value = value.lower()
    value = re.sub(r"[^a-z0-9\u4e00-\u9fff]+", "_", value)
    return value.strip("_")[:120]


def stable_id(prefix: str, *parts: Any) -> str:
    raw = "\\x1f".join(str(part) for part in parts)
    return f"{prefix}_{hashlib.sha256(raw.encode('utf-8')).hexdigest()[:16]}"


def _dedupe(rows: list[dict[str, Any]], key: str) -> list[dict[str, Any]]:
    seen: set[str] = set()
    result: list[dict[str, Any]] = []
    for row in rows:
        value = str(row.get(key) or "")
        if not value or value in seen:
            continue
        seen.add(value)
        result.append(row)
    return result

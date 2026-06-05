"""Service layer for V2.1 code quality governance."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from data_service.mcp_common import read_json

from ..artifacts import (
    agent_context_dir,
    architecture_doc_claims_path,
    architecture_doc_code_alignment_path,
    architecture_doc_quality_findings_path,
    architecture_doc_relations_path,
    architecture_docs_path,
    architecture_code_boundaries_path,
    architecture_code_layers_path,
    architecture_code_roles_path,
    architecture_design_code_drift_path,
    architecture_pattern_candidates_path,
    architecture_reconstructed_model_path,
    devwiki_page_json_path,
    inventory_capabilities_path,
    inventory_surfaces_path,
    symbols_path,
    read_jsonl,
)
from ..context.persistence import read_context_pack
from ..devwiki.persistence import read_index as read_devwiki_index, read_page as read_devwiki_page
from ..graph.persistence import read_edges as read_graph_edges, read_graph, read_nodes as read_graph_nodes
from ..registry import CodebaseRegistry
from ..snapshot import CodebaseSnapshotService
from .feedback import make_feedback
from .model import QUALITY_SCHEMA_VERSION, validate_review_status, validate_rule_type, validate_target_type
from .persistence import (
    quality_artifact_refs,
    read_feedback,
    read_plan,
    read_reviews,
    read_rules,
    read_summary,
    write_feedback,
    write_plan,
    write_reviews,
    write_rules,
    write_summary,
)
from .plan import build_plan
from .review import apply_review
from .rules import build_rules_from_feedback


class CodeQualityService:
    def __init__(self, workspace: Path, *, workspace_id: str) -> None:
        self.workspace = Path(workspace)
        self.workspace_id = workspace_id
        self.registry = CodebaseRegistry(workspace, workspace_id=workspace_id)
        self.snapshots = CodebaseSnapshotService(workspace, workspace_id=workspace_id)

    def record_feedback(
        self,
        codebase_id: str,
        *,
        target_type: str,
        target_id: str,
        action: str,
        rule_type: str,
        severity: str = "medium",
        reason: str = "",
        suggested_value: str = "",
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        self.registry.describe(codebase_id)
        normalized_target_type = validate_target_type(target_type)
        normalized_rule_type = validate_rule_type(rule_type)
        if not str(target_id or "").strip():
            raise ValueError("INVALID_TARGET_ID")
        if not str(action or "").strip():
            raise ValueError("INVALID_ACTION")
        resolved_target = self.resolve_target(codebase_id, normalized_target_type, str(target_id).strip())
        rows = read_feedback(self.workspace, codebase_id)
        feedback = make_feedback(
            workspace_id=self.workspace_id,
            codebase_id=codebase_id,
            target_type=normalized_target_type,
            target_id=str(target_id).strip(),
            action=str(action).strip(),
            rule_type=normalized_rule_type,
            severity=str(severity or "medium").strip(),
            reason=str(reason or ""),
            suggested_value=str(suggested_value or ""),
            metadata=metadata,
            resolved_target=resolved_target,
        )
        rows = [row for row in rows if row.get("feedback_id") != feedback["feedback_id"]] + [feedback]
        write_feedback(self.workspace, codebase_id, sorted(rows, key=lambda row: row["feedback_id"]))
        summary = self._write_summary(codebase_id)
        return {"feedback": feedback, "summary": summary, "artifact_refs": quality_artifact_refs(codebase_id)}

    def build_rules(self, codebase_id: str) -> dict[str, Any]:
        self.registry.describe(codebase_id)
        feedback = read_feedback(self.workspace, codebase_id)
        if not feedback:
            raise FileNotFoundError("QUALITY_FEEDBACK_NOT_FOUND")
        rules = build_rules_from_feedback(
            workspace_id=self.workspace_id,
            codebase_id=codebase_id,
            feedback=feedback,
            existing_rules=read_rules(self.workspace, codebase_id),
        )
        write_rules(self.workspace, codebase_id, rules)
        summary = self._write_summary(codebase_id)
        return {"rules": rules, "summary": summary, "artifact_refs": quality_artifact_refs(codebase_id)}

    def review_rule(self, codebase_id: str, rule_id: str, *, status: str, reviewer: str = "", note: str = "") -> dict[str, Any]:
        self.registry.describe(codebase_id)
        normalized_status = validate_review_status(status)
        rules = read_rules(self.workspace, codebase_id)
        updated, rule, review = apply_review(
            workspace_id=self.workspace_id,
            codebase_id=codebase_id,
            rules=rules,
            rule_id=rule_id,
            status=normalized_status,
            reviewer=reviewer,
            note=note,
        )
        write_rules(self.workspace, codebase_id, updated)
        reviews = read_reviews(self.workspace, codebase_id)
        write_reviews(self.workspace, codebase_id, [*reviews, review])
        summary = self._write_summary(codebase_id)
        return {"rule": rule, "review": review, "summary": summary, "artifact_refs": quality_artifact_refs(codebase_id)}

    def build_plan(self, codebase_id: str) -> dict[str, Any]:
        self.registry.describe(codebase_id)
        rules = read_rules(self.workspace, codebase_id)
        plan = build_plan(workspace_id=self.workspace_id, codebase_id=codebase_id, rules=rules)
        write_plan(self.workspace, codebase_id, plan)
        summary = self._write_summary(codebase_id)
        return {"plan": plan, "summary": summary, "artifact_refs": quality_artifact_refs(codebase_id)}

    def summary(self, codebase_id: str) -> dict[str, Any]:
        self.registry.describe(codebase_id)
        summary = read_summary(self.workspace, codebase_id)
        if not summary:
            summary = self._write_summary(codebase_id)
        plan = read_plan(self.workspace, codebase_id)
        return {"summary": summary, "plan": plan or None, "artifact_refs": quality_artifact_refs(codebase_id)}

    def resolve_target(self, codebase_id: str, target_type: str, target_id: str) -> dict[str, Any]:
        if target_type == "codebase":
            asset = self.registry.describe(codebase_id)
            if target_id not in {codebase_id, asset.codebase_id}:
                raise FileNotFoundError("QUALITY_TARGET_NOT_FOUND")
            return {"target_type": target_type, "target_id": target_id}
        if target_type == "repo_snapshot":
            self.snapshots.read_snapshot(codebase_id, target_id)
            return {"target_type": target_type, "target_id": target_id}
        latest = self._latest_snapshot_id(codebase_id)
        if target_type == "code_file":
            for row in self._snapshot_files(codebase_id, latest):
                if row.get("path") == target_id:
                    return {"target_type": target_type, "target_id": target_id, "source_file": target_id}
        if target_type in {"public_surface", "code_route", "code_mcp_tool", "code_cli_command"}:
            for row in read_jsonl(inventory_surfaces_path(self.workspace, codebase_id, latest)):
                if row.get("surface_id") == target_id:
                    return {"target_type": target_type, "target_id": target_id, "surface_type": row.get("surface_type")}
        if target_type == "capability":
            for row in read_jsonl(inventory_capabilities_path(self.workspace, codebase_id, latest)):
                if row.get("capability_id") == target_id:
                    return {"target_type": target_type, "target_id": target_id}
        if target_type == "code_symbol":
            for row in read_jsonl(symbols_path(self.workspace, codebase_id, latest)):
                if row.get("symbol_id") == target_id:
                    return {"target_type": target_type, "target_id": target_id, "source_file": row.get("path")}
        if target_type == "devwiki_page":
            page = self._resolve_devwiki_page(codebase_id, target_id)
            return {"target_type": target_type, "target_id": target_id, "page_id": page.get("page_id"), "slug": page.get("slug")}
        if target_type == "devwiki_section":
            section = self._resolve_devwiki_section(codebase_id, target_id)
            return {"target_type": target_type, "target_id": target_id, **section}
        if target_type == "code_graph_node":
            for row in read_graph_nodes(self.workspace, codebase_id):
                if row.get("node_id") == target_id:
                    return {"target_type": target_type, "target_id": target_id, "node_type": row.get("node_type")}
        if target_type == "code_graph_edge":
            for row in read_graph_edges(self.workspace, codebase_id):
                if row.get("edge_id") == target_id:
                    return {"target_type": target_type, "target_id": target_id, "relation": row.get("relation")}
        if target_type == "agent_context_pack":
            pack = read_context_pack(self.workspace, codebase_id, target_id)
            return {"target_type": target_type, "target_id": target_id, "pack_id": pack.get("pack_id")}
        if target_type == "agent_context_item":
            item = self._resolve_context_item(codebase_id, target_id)
            return {"target_type": target_type, "target_id": target_id, **item}
        if target_type == "architecture_role":
            return self._resolve_architecture_jsonl_target(codebase_id, target_id, architecture_code_roles_path(self.workspace, codebase_id), "role_id", "role_type")
        if target_type == "architecture_layer":
            return self._resolve_architecture_jsonl_target(codebase_id, target_id, architecture_code_layers_path(self.workspace, codebase_id), "layer_id", "layer_type")
        if target_type == "architecture_boundary":
            return self._resolve_architecture_jsonl_target(codebase_id, target_id, architecture_code_boundaries_path(self.workspace, codebase_id), "boundary_id", "boundary_type")
        if target_type == "architecture_pattern":
            return self._resolve_architecture_jsonl_target(codebase_id, target_id, architecture_pattern_candidates_path(self.workspace, codebase_id), "pattern_id", "pattern_type")
        if target_type == "architecture_drift_finding":
            return self._resolve_architecture_jsonl_target(codebase_id, target_id, architecture_design_code_drift_path(self.workspace, codebase_id), "finding_id", "finding_type")
        if target_type == "architecture_doc":
            return self._resolve_architecture_jsonl_target(codebase_id, target_id, architecture_docs_path(self.workspace, codebase_id), "doc_id", "doc_type")
        if target_type == "architecture_doc_claim":
            return self._resolve_architecture_jsonl_target(codebase_id, target_id, architecture_doc_claims_path(self.workspace, codebase_id), "claim_id", "claim_type")
        if target_type == "architecture_doc_relation":
            return self._resolve_architecture_jsonl_target(codebase_id, target_id, architecture_doc_relations_path(self.workspace, codebase_id), "relation_id", "relation_type")
        if target_type == "architecture_doc_quality_finding":
            return self._resolve_architecture_jsonl_target(codebase_id, target_id, architecture_doc_quality_findings_path(self.workspace, codebase_id), "finding_id", "finding_type")
        if target_type == "architecture_doc_code_alignment":
            return self._resolve_architecture_jsonl_target(codebase_id, target_id, architecture_doc_code_alignment_path(self.workspace, codebase_id), "alignment_id", "status")
        if target_type == "architecture_reconstructed_node":
            return self._resolve_reconstructed_node(codebase_id, target_id)
        if target_type == "architecture_reconstructed_edge":
            return self._resolve_reconstructed_edge(codebase_id, target_id)
        raise FileNotFoundError("QUALITY_TARGET_NOT_FOUND")

    def _write_summary(self, codebase_id: str) -> dict[str, Any]:
        feedback = read_feedback(self.workspace, codebase_id)
        rules = read_rules(self.workspace, codebase_id)
        reviews = read_reviews(self.workspace, codebase_id)
        plan = read_plan(self.workspace, codebase_id)
        status_counts: dict[str, int] = {}
        for rule in rules:
            status_counts[str(rule.get("status") or "unknown")] = status_counts.get(str(rule.get("status") or "unknown"), 0) + 1
        summary = {
            "schema_version": QUALITY_SCHEMA_VERSION,
            "workspace_id": self.workspace_id,
            "codebase_id": codebase_id,
            "feedback_count": len(feedback),
            "rule_count": len(rules),
            "draft_rule_count": status_counts.get("draft", 0),
            "approved_rule_count": status_counts.get("approved", 0),
            "rejected_rule_count": status_counts.get("rejected", 0),
            "revoked_rule_count": status_counts.get("revoked", 0),
            "review_count": len(reviews),
            "unresolved_target_count": 0,
            "active_approved_rule_ids": [rule["rule_id"] for rule in rules if rule.get("status") == "approved"],
            "plan_id": plan.get("plan_id") if plan else None,
            "artifact_refs": quality_artifact_refs(codebase_id),
        }
        write_summary(self.workspace, codebase_id, summary)
        return summary

    def _latest_snapshot_id(self, codebase_id: str) -> str:
        snapshots = self.snapshots.list_snapshots(codebase_id, limit=1)
        if not snapshots:
            raise FileNotFoundError("SNAPSHOT_NOT_FOUND")
        return str(snapshots[0]["snapshot_id"])

    def _snapshot_files(self, codebase_id: str, snapshot_id: str) -> list[dict[str, Any]]:
        from ..artifacts import snapshot_files_path

        return read_jsonl(snapshot_files_path(self.workspace, codebase_id, snapshot_id))

    def _resolve_devwiki_page(self, codebase_id: str, target_id: str) -> dict[str, Any]:
        index = read_devwiki_index(self.workspace, codebase_id)
        for row in index.get("pages", []):
            if target_id in {row.get("page_id"), row.get("slug")}:
                return read_devwiki_page(self.workspace, codebase_id, str(row["slug"]))
        if devwiki_page_json_path(self.workspace, codebase_id, target_id).exists():
            return read_devwiki_page(self.workspace, codebase_id, target_id)
        raise FileNotFoundError("QUALITY_TARGET_NOT_FOUND")

    def _resolve_devwiki_section(self, codebase_id: str, target_id: str) -> dict[str, Any]:
        slug_hint = None
        section_hint = target_id
        if "#" in target_id:
            slug_hint, section_hint = target_id.split("#", 1)
        pages = []
        if slug_hint:
            pages = [read_devwiki_page(self.workspace, codebase_id, slug_hint)]
        else:
            index = read_devwiki_index(self.workspace, codebase_id)
            pages = [read_devwiki_page(self.workspace, codebase_id, str(row["slug"])) for row in index.get("pages", [])]
        for page in pages:
            for section in page.get("sections", []):
                if section_hint in {section.get("section_id"), section.get("title")}:
                    return {"page_id": page.get("page_id"), "slug": page.get("slug"), "section_id": section.get("section_id")}
        raise FileNotFoundError("QUALITY_TARGET_NOT_FOUND")

    def _resolve_context_item(self, codebase_id: str, target_id: str) -> dict[str, Any]:
        pack_hint = None
        item_hint = target_id
        if "#" in target_id:
            pack_hint, item_hint = target_id.split("#", 1)
        packs = []
        if pack_hint:
            packs = [read_context_pack(self.workspace, codebase_id, pack_hint)]
        else:
            for path in agent_context_dir(self.workspace, codebase_id).glob("*.json"):
                payload = read_json(path, None)
                if payload:
                    packs.append(payload)
        for pack in packs:
            for section in [
                "relevant_capabilities",
                "relevant_public_surface",
                "relevant_files",
                "relevant_symbols",
                "implementation_guidance",
                "risks",
                "suggested_tests",
                "recommended_next_steps",
                "evidence",
            ]:
                for index, item in enumerate(pack.get(section, []) or []):
                    item_id = str(item.get("item_id") or item.get("claim_id") or item.get("surface_id") or item.get("symbol_id") or item.get("capability_id") or f"{section}:{index}")
                    if item_hint == item_id or item_hint == f"{section}:{index}":
                        return {"pack_id": pack.get("pack_id"), "section": section, "item_id": item_id}
        raise FileNotFoundError("QUALITY_TARGET_NOT_FOUND")

    def _resolve_architecture_jsonl_target(self, codebase_id: str, target_id: str, path: Path, id_key: str, type_key: str) -> dict[str, Any]:
        for row in read_jsonl(path):
            if row.get(id_key) == target_id:
                return {
                    "target_type": id_key.removesuffix("_id"),
                    "target_id": target_id,
                    id_key: row.get(id_key),
                    type_key: row.get(type_key),
                    "snapshot_id": row.get("snapshot_id"),
                    "evidence_count": len(row.get("evidence") or []),
                }
        raise FileNotFoundError("QUALITY_TARGET_NOT_FOUND")

    def _resolve_reconstructed_node(self, codebase_id: str, target_id: str) -> dict[str, Any]:
        model = read_json(architecture_reconstructed_model_path(self.workspace, codebase_id), None)
        if not model:
            raise FileNotFoundError("QUALITY_TARGET_NOT_FOUND")
        for collection_name in ("target_nodes", "current_nodes", "diff_nodes"):
            for row in model.get(collection_name, []) or []:
                if row.get("node_id") == target_id:
                    return {"target_type": "architecture_reconstructed_node", "target_id": target_id, "node_type": row.get("node_type"), "section": row.get("section")}
        raise FileNotFoundError("QUALITY_TARGET_NOT_FOUND")

    def _resolve_reconstructed_edge(self, codebase_id: str, target_id: str) -> dict[str, Any]:
        model = read_json(architecture_reconstructed_model_path(self.workspace, codebase_id), None)
        if not model:
            raise FileNotFoundError("QUALITY_TARGET_NOT_FOUND")
        for row in model.get("edges", []) or []:
            if row.get("edge_id") == target_id:
                return {"target_type": "architecture_reconstructed_edge", "target_id": target_id, "edge_type": row.get("edge_type")}
        raise FileNotFoundError("QUALITY_TARGET_NOT_FOUND")


def public_quality_payload(payload: dict[str, Any]) -> dict[str, Any]:
    return dict(payload)

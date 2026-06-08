"""V2.11 Coding Agent actionability service.

This module intentionally builds deterministic edit-planning evidence only. It
does not execute code, infer runtime calls, or mutate repository files.
"""

from __future__ import annotations

import ast
import html
import hashlib
import os
import re
import shlex
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

from data_service.mcp_common import now, read_json

from ..artifacts import inventory_surfaces_path, read_jsonl, snapshot_files_path, symbols_path
from ..registry import CodebaseRegistry
from ..snapshot import CodebaseSnapshotService
from .persistence import (
    actionability_artifact_refs,
    context_export_path,
    fingerprint_index_path,
    patch_plan_artifact_ref,
    patch_plan_path,
    patch_plans_dir,
    read_actionability_bundle,
    read_context_export,
    read_drift_timeline,
    read_fingerprint_index,
    read_impact,
    read_patch_plan,
    read_runtime_registry,
    read_runtime_run,
    read_snapshot_diff,
    read_task_plan,
    read_workbench,
    runtime_log_path,
    runtime_registry_artifact_ref,
    runtime_run_artifact_ref,
    runtime_runs_dir,
    snapshot_diff_artifact_ref,
    snapshot_diff_path,
    snapshot_diffs_dir,
    workbench_artifact_refs,
    workbench_html_path,
    workbench_mermaid_path,
    write_actionability_bundle,
    write_context_export,
    write_fingerprint_index,
    write_impact,
    write_patch_plan,
    write_runtime_registry,
    write_runtime_run,
    write_snapshot_diff,
    write_task_plan,
    write_workbench,
)
from ..coding_agent_v2_16.provider_registry import (
    ProviderCapabilityRegistryService,
    public_provider_registry_payload,
)
from ..coding_agent_v2_16.persistence import (
    read_large_project_advisor,
    read_patch_preview,
    read_semantic_index,
    read_runtime_profile_run,
    read_runtime_profiles,
    read_workbench_v2,
    write_large_project_advisor,
    write_patch_preview,
    write_runtime_profile_run,
    write_runtime_profiles,
    write_semantic_index,
    write_workbench_v2,
)
from ..coding_agent_v2_16.large_project_advisor import (
    build_large_project_advisor_payload,
    public_large_project_advisor_payload,
)
from ..coding_agent_v2_16.patch_sandbox import (
    blocked_patch_apply,
    build_patch_preview_payload,
    public_patch_preview_payload,
)
from ..coding_agent_v2_16.runtime_profiles import (
    blocked_profile_run,
    build_runtime_profiles_payload,
    profile_run_from_runtime,
    public_runtime_profile_run_payload,
    public_runtime_profiles_payload,
)
from ..coding_agent_v2_16.semantic_orchestrator import (
    build_semantic_payload,
    public_semantic_payload,
)
from ..coding_agent_v2_16.workbench_v2 import (
    build_workbench_v2_payload,
    public_workbench_v2_payload,
    render_workbench_v2_html,
    render_workbench_v2_mermaid,
)


SCHEMA_VERSION = "v2.11"
PATCH_PLAN_SCHEMA_VERSION = "v2.12"
RUNTIME_SCHEMA_VERSION = "v2.13"
INCREMENTAL_SCHEMA_VERSION = "v2.14"
WORKBENCH_SCHEMA_VERSION = "v2.15"
PROVIDER_REGISTRY_SCHEMA_VERSION = "v2.16"
FORBIDDEN_RELATION_TYPES = {"runtime_call", "runtime_calls", "data_flow", "control_flow", "type_inferred", "type_inferred_dependency"}


class CodingAgentActionabilityService:
    def __init__(self, workspace: Path, *, workspace_id: str) -> None:
        self.workspace = Path(workspace)
        self.workspace_id = workspace_id
        self.registry = CodebaseRegistry(workspace, workspace_id=workspace_id)
        self.snapshots = CodebaseSnapshotService(workspace, workspace_id=workspace_id)

    def build_provider_registry(self, codebase_id: str, *, snapshot_id: str | None = None) -> dict[str, Any]:
        return ProviderCapabilityRegistryService(self.workspace, workspace_id=self.workspace_id).build_registry(codebase_id, snapshot_id=snapshot_id)

    def read_provider_registry(self, codebase_id: str) -> dict[str, Any]:
        return ProviderCapabilityRegistryService(self.workspace, workspace_id=self.workspace_id).read_registry(codebase_id)

    def build_semantic_provider_index(self, codebase_id: str, *, snapshot_id: str | None = None) -> dict[str, Any]:
        resolved_snapshot_id = snapshot_id or self._latest_snapshot_id(codebase_id)
        try:
            provider_registry = self.read_provider_registry(codebase_id)
        except FileNotFoundError:
            provider_registry = self.build_provider_registry(codebase_id, snapshot_id=resolved_snapshot_id)
        try:
            actionability = self.read_actionability(codebase_id)
            if actionability.get("index", {}).get("snapshot_id") != resolved_snapshot_id:
                actionability = self.build_actionability(codebase_id, snapshot_id=resolved_snapshot_id)
        except FileNotFoundError:
            actionability = self.build_actionability(codebase_id, snapshot_id=resolved_snapshot_id)
        index, facts, conflicts = build_semantic_payload(
            workspace_id=self.workspace_id,
            codebase_id=codebase_id,
            snapshot_id=resolved_snapshot_id,
            actionability=actionability,
            provider_registry=provider_registry,
        )
        write_semantic_index(self.workspace, codebase_id, index, facts, conflicts)
        return {"index": index, "provider_facts": facts, "provider_conflicts": conflicts, "artifact_refs": index.get("artifact_refs", [])}

    def read_semantic_provider_index(self, codebase_id: str) -> dict[str, Any]:
        self.registry.describe(codebase_id)
        return read_semantic_index(self.workspace, codebase_id)

    def build_runtime_profiles(self, codebase_id: str, *, snapshot_id: str | None = None, patch_plan_id: str | None = None) -> dict[str, Any]:
        runtime_registry = self.build_runtime_registry(codebase_id, snapshot_id=snapshot_id, patch_plan_id=patch_plan_id)
        payload = build_runtime_profiles_payload(
            workspace_id=self.workspace_id,
            codebase_id=codebase_id,
            snapshot_id=str(runtime_registry.get("snapshot_id") or snapshot_id or ""),
            runtime_registry=runtime_registry,
        )
        write_runtime_profiles(self.workspace, codebase_id, payload)
        return payload

    def read_runtime_profiles_v2_16(self, codebase_id: str) -> dict[str, Any]:
        self.registry.describe(codebase_id)
        return read_runtime_profiles(self.workspace, codebase_id)

    def run_runtime_profile(self, codebase_id: str, *, profile_id: str, patch_plan_id: str | None = None, snapshot_id: str | None = None) -> dict[str, Any]:
        try:
            profiles = self.read_runtime_profiles_v2_16(codebase_id)
        except FileNotFoundError:
            profiles = self.build_runtime_profiles(codebase_id, snapshot_id=snapshot_id, patch_plan_id=patch_plan_id)
        profile = next((item for item in profiles.get("profiles", []) if item.get("profile_id") == profile_id), None)
        if not profile:
            payload = blocked_profile_run(
                workspace_id=self.workspace_id,
                codebase_id=codebase_id,
                snapshot_id=profiles.get("snapshot_id") or snapshot_id,
                profile_id=profile_id,
            )
            return payload
        runtime_run = self.run_runtime_command(codebase_id, command_id=str(profile.get("command_id") or ""), patch_plan_id=patch_plan_id, snapshot_id=profiles.get("snapshot_id") or snapshot_id)
        payload = profile_run_from_runtime(workspace_id=self.workspace_id, codebase_id=codebase_id, profile=profile, runtime_run=runtime_run)
        write_runtime_profile_run(self.workspace, codebase_id, payload)
        return payload

    def read_runtime_profile_run(self, codebase_id: str, profile_run_id: str) -> dict[str, Any]:
        self.registry.describe(codebase_id)
        return read_runtime_profile_run(self.workspace, codebase_id, profile_run_id)

    def build_workbench_v2(self, codebase_id: str, *, snapshot_id: str | None = None) -> dict[str, Any]:
        resolved_snapshot_id = snapshot_id or self._latest_snapshot_id(codebase_id)
        try:
            provider_registry = self.read_provider_registry(codebase_id)
        except FileNotFoundError:
            provider_registry = self.build_provider_registry(codebase_id, snapshot_id=resolved_snapshot_id)
        try:
            semantic_index = self.read_semantic_provider_index(codebase_id)
        except FileNotFoundError:
            semantic_index = self.build_semantic_provider_index(codebase_id, snapshot_id=resolved_snapshot_id)
        try:
            runtime_profiles = self.read_runtime_profiles_v2_16(codebase_id)
        except FileNotFoundError:
            runtime_profiles = self.build_runtime_profiles(codebase_id, snapshot_id=resolved_snapshot_id)
        try:
            workbench = self.read_workbench(codebase_id)
        except FileNotFoundError:
            workbench = self.build_workbench(codebase_id, snapshot_id=resolved_snapshot_id)
        payload = build_workbench_v2_payload(
            workspace_id=self.workspace_id,
            codebase_id=codebase_id,
            snapshot_id=resolved_snapshot_id,
            provider_registry=provider_registry,
            semantic_index=semantic_index,
            runtime_profiles=runtime_profiles,
            workbench=workbench,
        )
        write_workbench_v2(self.workspace, codebase_id, payload, render_workbench_v2_html(payload), render_workbench_v2_mermaid(payload))
        return payload

    def read_workbench_v2(self, codebase_id: str) -> dict[str, Any]:
        self.registry.describe(codebase_id)
        return read_workbench_v2(self.workspace, codebase_id)

    def read_workbench_v2_view(self, codebase_id: str, view_id: str) -> dict[str, Any]:
        from ..coding_agent_v2_16.persistence import workbench_v2_artifact_refs, workbench_v2_html_path, workbench_v2_mermaid_path

        self.registry.describe(codebase_id)
        if view_id in {"html", "review_workbench_v2.html"}:
            path = workbench_v2_html_path(self.workspace, codebase_id)
            content_type = "text/html"
        elif view_id in {"mermaid", "review_workbench_v2.mmd"}:
            path = workbench_v2_mermaid_path(self.workspace, codebase_id)
            content_type = "text/vnd.mermaid"
        else:
            raise FileNotFoundError("WORKBENCH_V2_VIEW_NOT_FOUND")
        if not path.exists():
            raise FileNotFoundError("WORKBENCH_V2_VIEW_NOT_FOUND")
        return {
            "schema_version": PROVIDER_REGISTRY_SCHEMA_VERSION,
            "workspace_id": self.workspace_id,
            "codebase_id": codebase_id,
            "view_id": view_id,
            "content_type": content_type,
            "content": path.read_text(encoding="utf-8"),
            "artifact_refs": workbench_v2_artifact_refs(codebase_id),
        }

    def build_large_project_advisor(self, codebase_id: str, *, snapshot_id: str | None = None) -> dict[str, Any]:
        resolved_snapshot_id = snapshot_id or self._latest_snapshot_id(codebase_id)
        self.snapshots.read_snapshot(codebase_id, resolved_snapshot_id)
        files = read_jsonl(snapshot_files_path(self.workspace, codebase_id, resolved_snapshot_id))
        try:
            semantic_index = self.read_semantic_provider_index(codebase_id)
        except FileNotFoundError:
            semantic_index = self.build_semantic_provider_index(codebase_id, snapshot_id=resolved_snapshot_id)
        try:
            workbench_v2 = self.read_workbench_v2(codebase_id)
        except FileNotFoundError:
            workbench_v2 = self.build_workbench_v2(codebase_id, snapshot_id=resolved_snapshot_id)
        payload, adapters, blockers = build_large_project_advisor_payload(
            workspace_id=self.workspace_id,
            codebase_id=codebase_id,
            snapshot_id=resolved_snapshot_id,
            files=files,
            semantic_index=semantic_index,
            workbench_v2=workbench_v2,
        )
        write_large_project_advisor(self.workspace, codebase_id, payload, adapters, blockers)
        return payload

    def read_large_project_advisor(self, codebase_id: str) -> dict[str, Any]:
        self.registry.describe(codebase_id)
        return read_large_project_advisor(self.workspace, codebase_id)

    def create_patch_preview(self, codebase_id: str, *, task: str, patch_plan_id: str | None = None, snapshot_id: str | None = None) -> dict[str, Any]:
        asset = self.registry.describe(codebase_id)
        if patch_plan_id:
            patch_plan = self.read_patch_plan(codebase_id, patch_plan_id)
        else:
            patch_plan = self.create_patch_plan(codebase_id, task=task, snapshot_id=snapshot_id)
        payload, diff_text = build_patch_preview_payload(
            workspace_id=self.workspace_id,
            codebase_id=codebase_id,
            snapshot_id=patch_plan.get("snapshot_id") or snapshot_id,
            patch_plan=patch_plan,
            repo_root=Path(asset.root_path).expanduser().resolve(),
        )
        write_patch_preview(self.workspace, codebase_id, payload, diff_text)
        return payload

    def read_patch_preview(self, codebase_id: str, preview_id: str) -> dict[str, Any]:
        self.registry.describe(codebase_id)
        return read_patch_preview(self.workspace, codebase_id, preview_id)

    def apply_patch_preview(self, codebase_id: str, preview_id: str) -> dict[str, Any]:
        self.registry.describe(codebase_id)
        return blocked_patch_apply(workspace_id=self.workspace_id, codebase_id=codebase_id, preview_id=preview_id)

    def build_actionability(self, codebase_id: str, *, snapshot_id: str | None = None) -> dict[str, Any]:
        asset = self.registry.describe(codebase_id)
        if asset.status != "active":
            raise ValueError("CODEBASE_NOT_ACTIVE")
        resolved_snapshot_id = snapshot_id or self._latest_snapshot_id(codebase_id)
        self.snapshots.read_snapshot(codebase_id, resolved_snapshot_id)
        root = Path(asset.root_path).expanduser().resolve()
        files = read_jsonl(snapshot_files_path(self.workspace, codebase_id, resolved_snapshot_id))
        symbols = read_jsonl(symbols_path(self.workspace, codebase_id, resolved_snapshot_id))
        surfaces = read_jsonl(inventory_surfaces_path(self.workspace, codebase_id, resolved_snapshot_id))
        if not files:
            raise FileNotFoundError("SNAPSHOT_FILES_NOT_FOUND")

        definitions, references, warnings = _build_ast_facts(
            workspace_id=self.workspace_id,
            codebase_id=codebase_id,
            snapshot_id=resolved_snapshot_id,
            root=root,
            files=files,
            symbols=symbols,
            surfaces=surfaces,
        )
        test_mapping = _build_test_mapping(self.workspace_id, codebase_id, resolved_snapshot_id, definitions, files)
        provider_status = [
            {"provider": "python_ast", "kind": "ast", "mandatory": True, "status": "available", "reason": None},
            {"provider": "tree_sitter", "kind": "tree_sitter", "mandatory": False, "status": "unavailable", "reason": "optional provider not configured"},
            {"provider": "lsp", "kind": "lsp", "mandatory": False, "status": "unavailable", "reason": "optional provider not configured"},
        ]
        relation_types = sorted({row["relation_type"] for row in references})
        index = {
            "schema_version": SCHEMA_VERSION,
            "workspace_id": self.workspace_id,
            "codebase_id": codebase_id,
            "snapshot_id": resolved_snapshot_id,
            "created_at": now(),
            "provider_status": provider_status,
            "summary": {
                "definition_count": len(definitions),
                "reference_count": len(references),
                "test_mapping_count": len(test_mapping),
                "accepted_test_mapping_count": sum(1 for row in test_mapping if row["status"] == "accepted"),
                "needs_review_count": sum(1 for row in test_mapping if row["status"] != "accepted"),
                "forbidden_relation_count": sum(1 for row in references if row.get("relation_type") in FORBIDDEN_RELATION_TYPES),
                "relation_types": relation_types,
                "warning_count": len(warnings),
            },
            "warnings": warnings,
            "artifact_refs": actionability_artifact_refs(codebase_id),
            "source_artifact_refs": [
                {"type": "snapshot_files", "artifact_ref": f"snapshot-files://{codebase_id}/{resolved_snapshot_id}"},
                {"type": "symbols", "artifact_ref": f"symbols://{codebase_id}/{resolved_snapshot_id}"},
                {"type": "inventory_surfaces", "artifact_ref": f"inventory-surfaces://{codebase_id}/{resolved_snapshot_id}"},
            ],
        }
        write_actionability_bundle(self.workspace, codebase_id, index, definitions, references, test_mapping)
        return {"index": index, "definitions": definitions, "references": references, "test_mapping": test_mapping, "artifact_refs": actionability_artifact_refs(codebase_id)}

    def read_actionability(self, codebase_id: str) -> dict[str, Any]:
        self.registry.describe(codebase_id)
        return read_actionability_bundle(self.workspace, codebase_id)

    def analyze_impact(self, codebase_id: str, *, task: str, focus_paths: list[str] | None = None, snapshot_id: str | None = None) -> dict[str, Any]:
        bundle = _ensure_actionability(self, codebase_id, snapshot_id=snapshot_id)
        index = bundle["index"]
        terms = _task_terms(task)
        focus_paths = [str(path) for path in (focus_paths or []) if str(path).strip()]
        definitions = bundle["definitions"]
        references = bundle["references"]
        tests = bundle["test_mapping"]
        refs_by_definition: dict[str, list[dict[str, Any]]] = {}
        for ref in references:
            refs_by_definition.setdefault(str(ref.get("from_definition_id") or ""), []).append(ref)
        tests_by_definition: dict[str, list[dict[str, Any]]] = {}
        for row in tests:
            tests_by_definition.setdefault(str(row.get("definition_id") or ""), []).append(row)
        candidates: list[dict[str, Any]] = []
        for definition in definitions:
            score, reason_codes = _score_definition(definition, terms, focus_paths)
            if score <= 0:
                continue
            definition_id = str(definition.get("definition_id") or "")
            related_refs = refs_by_definition.get(definition_id, [])[:8]
            mapped_tests = tests_by_definition.get(definition_id, [])[:8]
            status = "accepted" if definition.get("evidence_refs") and score >= 0.55 else "needs_review"
            candidates.append(
                {
                    "target_id": definition["definition_id"],
                    "target_type": definition["kind"],
                    "path": definition["path"],
                    "line_range": definition["line_range"],
                    "qualified_name": definition["qualified_name"],
                    "score": round(score, 3),
                    "status": status,
                    "reason_codes": reason_codes,
                    "evidence_refs": list(definition.get("evidence_refs") or []),
                    "related_reference_ids": [ref["reference_id"] for ref in related_refs],
                    "mapped_tests": mapped_tests,
                    "needs_review": [] if status == "accepted" else ["impact confidence below accepted threshold"],
                }
            )
        candidates.sort(key=lambda item: (-float(item["score"]), item["path"], item["qualified_name"]))
        if not candidates:
            candidates = [_blocker_row(task, focus_paths)]
        impact_id = _stable_id("impact", index["codebase_id"], index["snapshot_id"], task, focus_paths)
        payload = {
            "schema_version": SCHEMA_VERSION,
            "workspace_id": self.workspace_id,
            "codebase_id": codebase_id,
            "snapshot_id": index["snapshot_id"],
            "impact_id": impact_id,
            "task": task,
            "focus_paths": focus_paths,
            "provider_status": index.get("provider_status", []),
            "summary": {
                "candidate_count": len(candidates),
                "accepted_count": sum(1 for item in candidates if item["status"] == "accepted"),
                "needs_review_count": sum(1 for item in candidates if item["status"] != "accepted"),
                "forbidden_claims": [],
            },
            "impacted_targets": candidates[:50],
            "artifact_refs": actionability_artifact_refs(codebase_id) + [{"type": "impact", "artifact_ref": f"coding-agent://{codebase_id}/impact/{impact_id}.json"}],
        }
        write_impact(self.workspace, codebase_id, payload)
        return payload

    def read_impact(self, codebase_id: str, impact_id: str) -> dict[str, Any]:
        self.registry.describe(codebase_id)
        return read_impact(self.workspace, codebase_id, impact_id)

    def create_task_plan(self, codebase_id: str, *, task: str, focus_paths: list[str] | None = None, max_items: int = 12, snapshot_id: str | None = None) -> dict[str, Any]:
        impact = self.analyze_impact(codebase_id, task=task, focus_paths=focus_paths, snapshot_id=snapshot_id)
        recommendations = []
        for target in impact["impacted_targets"][: max(1, min(int(max_items or 12), 50))]:
            evidence = list(target.get("evidence_refs") or [])
            needs_review = list(target.get("needs_review") or [])
            if not evidence:
                needs_review.append("recommendation has no accepted line-level evidence")
            recommendations.append(
                {
                    "recommendation_id": _stable_id("edit", target.get("target_id"), task),
                    "action": "inspect_or_modify",
                    "path": target.get("path"),
                    "line_range": target.get("line_range"),
                    "qualified_name": target.get("qualified_name"),
                    "reason_codes": target.get("reason_codes", []),
                    "evidence_refs": evidence,
                    "needs_review": sorted(set(needs_review)),
                    "mapped_tests": target.get("mapped_tests", []),
                }
            )
        plan_id = _stable_id("plan", codebase_id, impact["snapshot_id"], task, [item["recommendation_id"] for item in recommendations])
        payload = {
            "schema_version": SCHEMA_VERSION,
            "workspace_id": self.workspace_id,
            "codebase_id": codebase_id,
            "snapshot_id": impact["snapshot_id"],
            "plan_id": plan_id,
            "impact_id": impact["impact_id"],
            "task": task,
            "summary": {
                "recommendation_count": len(recommendations),
                "evidence_backed_count": sum(1 for item in recommendations if item.get("evidence_refs")),
                "needs_review_count": sum(1 for item in recommendations if item.get("needs_review")),
                "mutates_code": False,
                "executes_runtime": False,
            },
            "recommended_edits": recommendations,
            "omitted_items": [],
            "stop_conditions": ["does_not_mutate_code", "does_not_execute_runtime_commands", "no_full_call_graph_claim"],
            "artifact_refs": impact["artifact_refs"] + [{"type": "task_to_edit_plan", "artifact_ref": f"coding-agent://{codebase_id}/actionability/task_to_edit_plan_{plan_id}.json"}],
        }
        write_task_plan(self.workspace, codebase_id, payload)
        return payload

    def read_task_plan(self, codebase_id: str, plan_id: str) -> dict[str, Any]:
        self.registry.describe(codebase_id)
        return read_task_plan(self.workspace, codebase_id, plan_id)

    def create_patch_plan(
        self,
        codebase_id: str,
        *,
        task: str,
        focus_paths: list[str] | None = None,
        max_options: int = 3,
        snapshot_id: str | None = None,
        task_plan_id: str | None = None,
    ) -> dict[str, Any]:
        if task_plan_id:
            task_plan = self.read_task_plan(codebase_id, task_plan_id)
        else:
            task_plan = self.create_task_plan(codebase_id, task=task, focus_paths=focus_paths, max_items=12, snapshot_id=snapshot_id)
        resolved_task = str(task or task_plan.get("task") or "")
        candidates, unresolved = _patch_edit_candidates(codebase_id, str(task_plan.get("snapshot_id") or ""), resolved_task, task_plan.get("recommended_edits", []))
        validation_plan, validation_unresolved = _patch_validation_plan(codebase_id, str(task_plan.get("snapshot_id") or ""), candidates)
        rollback_plan, rollback_unresolved = _patch_rollback_plan(candidates)
        unresolved.extend(validation_unresolved)
        unresolved.extend(rollback_unresolved)
        patch_options = _patch_options(resolved_task, candidates, validation_plan, rollback_plan, max_options=max_options)
        needs_review = sorted(set(_collect_patch_needs_review(candidates, patch_options, validation_plan, rollback_plan, unresolved)))
        readiness = _patch_readiness(candidates, patch_options, validation_plan, rollback_plan, unresolved, needs_review)
        patch_plan_id = _stable_id("patchplan", codebase_id, task_plan.get("snapshot_id"), resolved_task, [item.get("candidate_id") for item in candidates], [item.get("code") for item in unresolved])
        refs = list(task_plan.get("artifact_refs") or []) + [patch_plan_artifact_ref(codebase_id, patch_plan_id)]
        evidence = sorted({ref for candidate in candidates for ref in candidate.get("evidence_refs", [])})
        payload = {
            "schema_version": PATCH_PLAN_SCHEMA_VERSION,
            "workspace_id": self.workspace_id,
            "codebase_id": codebase_id,
            "snapshot_id": task_plan.get("snapshot_id"),
            "patch_plan_id": patch_plan_id,
            "task": resolved_task,
            "status": readiness["status"],
            "readiness": readiness,
            "mutates_code": False,
            "executes_runtime": False,
            "source_refs": [
                {"type": "task_to_edit_plan", "id": task_plan.get("plan_id"), "artifact_ref": f"coding-agent://{codebase_id}/actionability/task_to_edit_plan_{task_plan.get('plan_id')}.json"},
                {"type": "impact", "id": task_plan.get("impact_id"), "artifact_ref": f"coding-agent://{codebase_id}/impact/{task_plan.get('impact_id')}.json"},
            ],
            "edit_candidates": candidates,
            "patch_options": patch_options,
            "validation_plan": validation_plan,
            "rollback_plan": rollback_plan,
            "evidence": evidence,
            "needs_review": needs_review,
            "warnings": [],
            "unresolved": unresolved,
            "artifact_refs": refs,
            "user_sections": _patch_user_sections(candidates, patch_options, validation_plan, rollback_plan, readiness, unresolved),
            "stop_conditions": ["does_not_mutate_code", "does_not_execute_runtime_commands", "not_a_patch_application", "human_review_required"],
            "created_at": now(),
        }
        write_patch_plan(self.workspace, codebase_id, payload)
        return payload

    def read_patch_plan(self, codebase_id: str, patch_plan_id: str) -> dict[str, Any]:
        self.registry.describe(codebase_id)
        return read_patch_plan(self.workspace, codebase_id, patch_plan_id)

    def build_runtime_registry(self, codebase_id: str, *, snapshot_id: str | None = None, patch_plan_id: str | None = None) -> dict[str, Any]:
        asset = self.registry.describe(codebase_id)
        resolved_snapshot_id = snapshot_id or self._latest_snapshot_id(codebase_id)
        self.snapshots.read_snapshot(codebase_id, resolved_snapshot_id)
        files = read_jsonl(snapshot_files_path(self.workspace, codebase_id, resolved_snapshot_id))
        commands = _runtime_allowlist(codebase_id, resolved_snapshot_id, files)
        patch_plan_ref = patch_plan_artifact_ref(codebase_id, patch_plan_id) if patch_plan_id else None
        payload = {
            "schema_version": RUNTIME_SCHEMA_VERSION,
            "workspace_id": self.workspace_id,
            "codebase_id": codebase_id,
            "snapshot_id": resolved_snapshot_id,
            "root_path_hash": hashlib.sha256(str(Path(asset.root_path).expanduser().resolve()).encode("utf-8")).hexdigest(),
            "policy": {
                "default": "deny",
                "requires_allowlisted_command_id": True,
                "timeout_seconds": 20,
                "mutates_code": False,
                "network": "disabled_by_policy",
            },
            "allowlisted_commands": commands,
            "blocked_commands": [
                {"pattern": "unregistered_command", "reason": "Only command_id values persisted in allowlisted_commands may be executed."},
                {"pattern": "shell_control_operators", "reason": "Commands are executed without shell=True and cannot use shell control syntax."},
            ],
            "linked_patch_plan_id": patch_plan_id,
            "source_refs": [ref for ref in [patch_plan_ref] if ref],
            "summary": {
                "allowlisted_command_count": len(commands),
                "test_command_count": sum(1 for item in commands if item["command_type"] == "pytest"),
                "syntax_check_command_count": sum(1 for item in commands if item["command_type"] == "python_ast_check"),
            },
            "warnings": [] if commands else [{"code": "NO_SAFE_RUNTIME_COMMANDS", "message": "No pytest or Python compile command could be allowlisted."}],
            "unresolved": [],
            "artifact_refs": [runtime_registry_artifact_ref(codebase_id)],
            "created_at": now(),
        }
        write_runtime_registry(self.workspace, codebase_id, payload)
        return payload

    def read_runtime_registry(self, codebase_id: str) -> dict[str, Any]:
        self.registry.describe(codebase_id)
        return read_runtime_registry(self.workspace, codebase_id)

    def run_runtime_command(self, codebase_id: str, *, command_id: str, patch_plan_id: str | None = None, snapshot_id: str | None = None) -> dict[str, Any]:
        asset = self.registry.describe(codebase_id)
        try:
            registry = self.read_runtime_registry(codebase_id)
        except FileNotFoundError:
            registry = self.build_runtime_registry(codebase_id, snapshot_id=snapshot_id, patch_plan_id=patch_plan_id)
        command = next((item for item in registry.get("allowlisted_commands", []) if item.get("command_id") == command_id), None)
        if not command:
            return _blocked_runtime_run(
                workspace_id=self.workspace_id,
                codebase_id=codebase_id,
                snapshot_id=str(registry.get("snapshot_id") or snapshot_id or ""),
                command_id=command_id,
                patch_plan_id=patch_plan_id,
                reason="RUNTIME_COMMAND_NOT_ALLOWLISTED",
            )
        root = Path(asset.root_path).expanduser().resolve()
        command_text = str(command.get("command") or "")
        run_id = _stable_id("run", codebase_id, registry.get("snapshot_id"), command_id, patch_plan_id, time.time_ns())
        started = time.monotonic()
        stdout = ""
        stderr = ""
        exit_code: int | None = None
        status = "failed"
        error: dict[str, Any] | None = None
        try:
            completed = subprocess.run(
                shlex.split(command_text),
                cwd=root,
                env=_runtime_env(root),
                text=True,
                capture_output=True,
                timeout=int(registry.get("policy", {}).get("timeout_seconds") or 20),
                check=False,
            )
            stdout = completed.stdout or ""
            stderr = completed.stderr or ""
            exit_code = completed.returncode
            status = "passed" if completed.returncode == 0 else "failed"
        except subprocess.TimeoutExpired as exc:
            stdout = exc.stdout.decode("utf-8", errors="replace") if isinstance(exc.stdout, bytes) else str(exc.stdout or "")
            stderr = exc.stderr.decode("utf-8", errors="replace") if isinstance(exc.stderr, bytes) else str(exc.stderr or "")
            status = "timeout"
            error = {"code": "RUNTIME_COMMAND_TIMEOUT", "message": "Runtime command exceeded the configured timeout.", "retryable": True}
        except OSError as exc:
            status = "failed"
            error = {"code": "RUNTIME_COMMAND_EXECUTION_FAILED", "message": str(exc), "retryable": False}
        duration_ms = int((time.monotonic() - started) * 1000)
        redacted_stdout = _redact_runtime_text(stdout, root)
        redacted_stderr = _redact_runtime_text(stderr, root)
        payload = {
            "schema_version": RUNTIME_SCHEMA_VERSION,
            "workspace_id": self.workspace_id,
            "codebase_id": codebase_id,
            "snapshot_id": registry.get("snapshot_id"),
            "run_id": run_id,
            "command_id": command_id,
            "command_label": command.get("label"),
            "command_type": command.get("command_type"),
            "status": status,
            "exit_code": exit_code,
            "duration_ms": duration_ms,
            "linked_patch_plan_id": patch_plan_id,
            "linked_static_evidence": list(command.get("evidence_refs") or []),
            "logs": {
                "stdout_ref": f"coding-agent://{codebase_id}/runtime/logs/{run_id}.stdout.redacted.txt",
                "stderr_ref": f"coding-agent://{codebase_id}/runtime/logs/{run_id}.stderr.redacted.txt",
                "stdout_preview": redacted_stdout[:2000],
                "stderr_preview": redacted_stderr[:2000],
                "redacted": True,
            },
            "error": error,
            "warnings": [],
            "unresolved": [] if status == "passed" else [{"code": "RUNTIME_VALIDATION_NOT_PASSED", "message": f"Command finished with status {status}.", "retryable": status == "timeout"}],
            "artifact_refs": [runtime_run_artifact_ref(codebase_id, run_id)],
            "created_at": now(),
        }
        write_runtime_run(self.workspace, codebase_id, payload, redacted_stdout, redacted_stderr)
        return payload

    def read_runtime_run(self, codebase_id: str, run_id: str) -> dict[str, Any]:
        self.registry.describe(codebase_id)
        return read_runtime_run(self.workspace, codebase_id, run_id)

    def build_incremental_diff(self, codebase_id: str, *, from_snapshot_id: str, to_snapshot_id: str, task: str | None = None) -> dict[str, Any]:
        self.registry.describe(codebase_id)
        self.snapshots.read_snapshot(codebase_id, from_snapshot_id)
        self.snapshots.read_snapshot(codebase_id, to_snapshot_id)
        from_files = read_jsonl(snapshot_files_path(self.workspace, codebase_id, from_snapshot_id))
        to_files = read_jsonl(snapshot_files_path(self.workspace, codebase_id, to_snapshot_id))
        from_index = _fingerprint_index(self.workspace_id, codebase_id, from_snapshot_id, from_files)
        to_index = _fingerprint_index(self.workspace_id, codebase_id, to_snapshot_id, to_files)
        write_fingerprint_index(self.workspace, codebase_id, from_snapshot_id, from_index)
        write_fingerprint_index(self.workspace, codebase_id, to_snapshot_id, to_index)
        changed_files = _snapshot_changed_files(from_index, to_index)
        changed_symbols = _changed_symbol_hints(codebase_id, to_snapshot_id, changed_files)
        diff_id = _stable_id("diff", codebase_id, from_snapshot_id, to_snapshot_id, [row["path"] for row in changed_files])
        task_memory = []
        if task:
            task_memory.append(
                {
                    "schema_version": INCREMENTAL_SCHEMA_VERSION,
                    "workspace_id": self.workspace_id,
                    "codebase_id": codebase_id,
                    "diff_id": diff_id,
                    "task": task,
                    "changed_file_count": len(changed_files),
                    "created_at": now(),
                }
            )
        drift_events = [
            {
                "schema_version": INCREMENTAL_SCHEMA_VERSION,
                "workspace_id": self.workspace_id,
                "codebase_id": codebase_id,
                "diff_id": diff_id,
                "snapshot_id": to_snapshot_id,
                "event_type": f"file_{row['change_type']}",
                "path": row["path"],
                "evidence_refs": row.get("evidence_refs", []),
                "created_at": now(),
            }
            for row in changed_files[:200]
        ]
        payload = {
            "schema_version": INCREMENTAL_SCHEMA_VERSION,
            "workspace_id": self.workspace_id,
            "codebase_id": codebase_id,
            "from_snapshot_id": from_snapshot_id,
            "to_snapshot_id": to_snapshot_id,
            "diff_id": diff_id,
            "summary": {
                "changed_file_count": len(changed_files),
                "added_count": sum(1 for row in changed_files if row["change_type"] == "added"),
                "modified_count": sum(1 for row in changed_files if row["change_type"] == "modified"),
                "deleted_count": sum(1 for row in changed_files if row["change_type"] == "deleted"),
                "changed_symbol_hint_count": len(changed_symbols),
            },
            "changed_files": changed_files,
            "changed_symbols": changed_symbols,
            "changed_surfaces": [row for row in changed_symbols if row["symbol_type"] == "public_surface_hint"],
            "changed_documents": [row for row in changed_files if row["path"].lower().endswith((".md", ".drawio", ".mmd"))],
            "identity_inputs": {
                "from_snapshot_id": from_snapshot_id,
                "to_snapshot_id": to_snapshot_id,
                "changed_file_fingerprints": [row["fingerprint"] for row in changed_files],
            },
            "task_memory_written": bool(task_memory),
            "drift_event_count": len(drift_events),
            "warnings": [],
            "unresolved": [],
            "artifact_refs": [snapshot_diff_artifact_ref(codebase_id, diff_id)],
            "created_at": now(),
        }
        write_snapshot_diff(self.workspace, codebase_id, payload, task_memory, drift_events)
        return payload

    def read_incremental_diff(self, codebase_id: str, diff_id: str) -> dict[str, Any]:
        self.registry.describe(codebase_id)
        return read_snapshot_diff(self.workspace, codebase_id, diff_id)

    def read_incremental_timeline(self, codebase_id: str) -> dict[str, Any]:
        self.registry.describe(codebase_id)
        events = read_drift_timeline(self.workspace, codebase_id)
        return {
            "schema_version": INCREMENTAL_SCHEMA_VERSION,
            "workspace_id": self.workspace_id,
            "codebase_id": codebase_id,
            "event_count": len(events),
            "events": events[-500:],
            "artifact_refs": [{"type": "drift_timeline", "artifact_ref": f"coding-agent://{codebase_id}/incremental/drift_timeline.jsonl"}],
        }

    def build_workbench(self, codebase_id: str, *, snapshot_id: str | None = None) -> dict[str, Any]:
        resolved_snapshot_id = snapshot_id or self._latest_snapshot_id(codebase_id)
        try:
            actionability = self.read_actionability(codebase_id)
        except FileNotFoundError:
            actionability = self.build_actionability(codebase_id, snapshot_id=resolved_snapshot_id)
        patch_plans = _read_json_files(patch_plans_dir(self.workspace, codebase_id))
        runtime_runs = _read_json_files(runtime_runs_dir(self.workspace, codebase_id))
        diffs = _read_json_files(snapshot_diffs_dir(self.workspace, codebase_id))
        nodes, edges = _workbench_graph(actionability, patch_plans, runtime_runs, diffs)
        risk_lanes = _workbench_risk_lanes(patch_plans, runtime_runs, diffs)
        blockers = _workbench_blockers(patch_plans, runtime_runs, diffs)
        payload = {
            "schema_version": WORKBENCH_SCHEMA_VERSION,
            "workspace_id": self.workspace_id,
            "codebase_id": codebase_id,
            "snapshot_id": resolved_snapshot_id,
            "workbench_id": _stable_id("workbench", codebase_id, resolved_snapshot_id, len(nodes), len(edges), len(blockers)),
            "summary": {
                "definition_count": actionability.get("index", {}).get("summary", {}).get("definition_count", 0),
                "patch_plan_count": len(patch_plans),
                "runtime_run_count": len(runtime_runs),
                "incremental_diff_count": len(diffs),
                "blocker_count": len(blockers),
            },
            "sections": [
                {"section_id": "architecture_map", "title": "Architecture Map", "item_count": len(nodes), "visible": True},
                {"section_id": "patch_readiness", "title": "Patch Readiness", "item_count": len(patch_plans), "visible": True},
                {"section_id": "runtime_evidence", "title": "Runtime Evidence", "item_count": len(runtime_runs), "visible": True},
                {"section_id": "incremental_drift", "title": "Incremental Drift", "item_count": len(diffs), "visible": True},
                {"section_id": "blockers", "title": "Blockers and Needs Review", "item_count": len(blockers), "visible": True},
            ],
            "capability_graph": {"nodes": nodes, "edges": edges},
            "risk_lanes": risk_lanes,
            "blockers": blockers,
            "artifact_refs": workbench_artifact_refs(codebase_id),
            "warnings": [],
            "unresolved": blockers,
            "created_at": now(),
        }
        write_workbench(self.workspace, codebase_id, payload, _render_workbench_html(payload), _render_workbench_mermaid(payload))
        return payload

    def read_workbench(self, codebase_id: str) -> dict[str, Any]:
        self.registry.describe(codebase_id)
        return read_workbench(self.workspace, codebase_id)

    def read_workbench_view(self, codebase_id: str, view_id: str) -> dict[str, Any]:
        self.registry.describe(codebase_id)
        if view_id in {"html", "review_workbench.html"}:
            path = workbench_html_path(self.workspace, codebase_id)
            content_type = "text/html"
        elif view_id in {"mermaid", "capability_graph.mmd"}:
            path = workbench_mermaid_path(self.workspace, codebase_id)
            content_type = "text/vnd.mermaid"
        else:
            raise FileNotFoundError("WORKBENCH_VIEW_NOT_FOUND")
        if not path.exists():
            raise FileNotFoundError("WORKBENCH_VIEW_NOT_FOUND")
        return {
            "schema_version": WORKBENCH_SCHEMA_VERSION,
            "workspace_id": self.workspace_id,
            "codebase_id": codebase_id,
            "view_id": view_id,
            "content_type": content_type,
            "content": path.read_text(encoding="utf-8"),
            "artifact_refs": workbench_artifact_refs(codebase_id),
        }

    def create_workbench_context_export(self, codebase_id: str, *, mode: str = "coding_agent", max_items: int = 25) -> dict[str, Any]:
        try:
            workbench = self.read_workbench(codebase_id)
        except FileNotFoundError:
            workbench = self.build_workbench(codebase_id)
        max_items = max(1, min(int(max_items or 25), 100))
        recommendations = []
        for item in workbench.get("risk_lanes", [])[:max_items]:
            evidence = list(item.get("evidence_refs") or [])
            needs_review = list(item.get("needs_review") or [])
            if not evidence and not needs_review:
                needs_review.append("context item has no evidence and requires review")
            recommendations.append(
                {
                    "recommendation_id": _stable_id("ctxrec", item.get("lane_id"), mode),
                    "title": item.get("title"),
                    "priority": item.get("priority"),
                    "evidence_refs": evidence,
                    "needs_review": needs_review,
                }
            )
        export_id = _stable_id("ctxexport", codebase_id, workbench.get("workbench_id"), mode, [item["recommendation_id"] for item in recommendations])
        graph = workbench.get("capability_graph", {})
        payload = {
            "schema_version": WORKBENCH_SCHEMA_VERSION,
            "workspace_id": self.workspace_id,
            "codebase_id": codebase_id,
            "snapshot_id": workbench.get("snapshot_id"),
            "export_id": export_id,
            "mode": mode,
            "source_workbench_id": workbench.get("workbench_id"),
            "summary": {
                "node_count": len(graph.get("nodes", [])),
                "edge_count": len(graph.get("edges", [])),
                "recommendation_count": len(recommendations),
                "omitted_count": max(0, len(workbench.get("risk_lanes", [])) - len(recommendations)),
            },
            "recommendations": recommendations,
            "omitted_items": workbench.get("risk_lanes", [])[max_items:],
            "source_phase_refs": ["V2.11", "V2.12", "V2.13", "V2.14", "V2.15"],
            "artifact_refs": workbench.get("artifact_refs", []) + [{"type": "workbench_context_export", "artifact_ref": f"coding-agent://{codebase_id}/workbench/context_exports/{export_id}.json"}],
            "warnings": [],
            "unresolved": workbench.get("unresolved", []),
            "created_at": now(),
        }
        write_context_export(self.workspace, codebase_id, payload)
        return payload

    def read_workbench_context_export(self, codebase_id: str, export_id: str) -> dict[str, Any]:
        self.registry.describe(codebase_id)
        return read_context_export(self.workspace, codebase_id, export_id)

    def _latest_snapshot_id(self, codebase_id: str) -> str:
        snapshots = self.snapshots.list_snapshots(codebase_id, limit=1)
        if not snapshots:
            raise FileNotFoundError("SNAPSHOT_NOT_FOUND")
        return str(snapshots[0]["snapshot_id"])


def public_actionability_payload(payload: dict[str, Any]) -> dict[str, Any]:
    definitions = []
    for item in payload["definitions"][:500]:
        row = dict(item)
        row["source_file"] = row.pop("path", row.get("source_file", ""))
        definitions.append(row)
    references = []
    for item in payload["references"][:1000]:
        row = dict(item)
        row["source_file"] = row.pop("path", row.get("source_file", ""))
        references.append(row)
    return {
        "schema_version": SCHEMA_VERSION,
        "index": payload["index"],
        "definitions": definitions,
        "references": references,
        "test_mapping": payload["test_mapping"][:500],
        "artifact_refs": payload.get("artifact_refs", []),
    }


def public_impact_payload(payload: dict[str, Any]) -> dict[str, Any]:
    result = dict(payload)
    result["impacted_targets"] = [_with_source_file(item) for item in payload.get("impacted_targets", [])]
    return result


def public_task_plan_payload(payload: dict[str, Any]) -> dict[str, Any]:
    result = dict(payload)
    result["recommended_edits"] = [_with_source_file(item) for item in payload.get("recommended_edits", [])]
    return result


def public_patch_plan_payload(payload: dict[str, Any]) -> dict[str, Any]:
    result = dict(payload)
    result["edit_candidates"] = [_with_source_file(item) for item in payload.get("edit_candidates", [])]
    result["patch_options"] = [dict(item) for item in payload.get("patch_options", [])]
    result["validation_plan"] = [dict(item) for item in payload.get("validation_plan", [])]
    result["rollback_plan"] = [_with_source_file(item) for item in payload.get("rollback_plan", [])]
    return result


def public_runtime_registry_payload(payload: dict[str, Any]) -> dict[str, Any]:
    return dict(payload)


def public_runtime_run_payload(payload: dict[str, Any]) -> dict[str, Any]:
    return dict(payload)


def public_incremental_diff_payload(payload: dict[str, Any]) -> dict[str, Any]:
    result = dict(payload)
    result["changed_files"] = [_with_source_file(item) for item in payload.get("changed_files", [])]
    result["changed_symbols"] = [_with_source_file(item) for item in payload.get("changed_symbols", [])]
    result["changed_surfaces"] = [_with_source_file(item) for item in payload.get("changed_surfaces", [])]
    result["changed_documents"] = [_with_source_file(item) for item in payload.get("changed_documents", [])]
    return result


def public_incremental_timeline_payload(payload: dict[str, Any]) -> dict[str, Any]:
    return dict(payload)


def public_workbench_payload(payload: dict[str, Any]) -> dict[str, Any]:
    return dict(payload)


def public_workbench_view_payload(payload: dict[str, Any]) -> dict[str, Any]:
    return dict(payload)


def public_workbench_context_export_payload(payload: dict[str, Any]) -> dict[str, Any]:
    return dict(payload)


def _with_source_file(item: dict[str, Any]) -> dict[str, Any]:
    row = dict(item)
    if "path" in row:
        row["source_file"] = row.pop("path")
    return row


def _runtime_allowlist(codebase_id: str, snapshot_id: str, files: list[dict[str, Any]]) -> list[dict[str, Any]]:
    commands: list[dict[str, Any]] = []
    test_paths = [str(row.get("path") or "") for row in files if row.get("included") and _is_test_path(str(row.get("path") or "")) and str(row.get("path") or "").endswith(".py")]
    for test_path in sorted(test_paths)[:8]:
        command = f"{shlex.quote(sys.executable)} -m pytest {shlex.quote(test_path)} -q"
        commands.append(
            {
                "command_id": _stable_id("runcmd", codebase_id, snapshot_id, "pytest", test_path),
                "label": f"Run pytest for {test_path}",
                "command_type": "pytest",
                "command": command,
                "status": "allowlisted",
                "evidence_refs": [f"code://{codebase_id}/{snapshot_id}/{test_path}"],
                "needs_review": [],
            }
        )
    py_paths = [str(row.get("path") or "") for row in files if row.get("included") and str(row.get("path") or "").endswith(".py")]
    for py_path in sorted(py_paths)[:5]:
        checker = "import ast,pathlib,sys; ast.parse(pathlib.Path(sys.argv[1]).read_text(encoding='utf-8'))"
        command = f"{shlex.quote(sys.executable)} -c {shlex.quote(checker)} {shlex.quote(py_path)}"
        commands.append(
            {
                "command_id": _stable_id("runcmd", codebase_id, snapshot_id, "python_ast_check", py_path),
                "label": f"AST syntax-check {py_path}",
                "command_type": "python_ast_check",
                "command": command,
                "status": "allowlisted",
                "evidence_refs": [f"code://{codebase_id}/{snapshot_id}/{py_path}"],
                "needs_review": [],
            }
        )
        if len(commands) >= 12:
            break
    return commands


def _runtime_env(root: Path) -> dict[str, str]:
    env = dict(os.environ)
    current = env.get("PYTHONPATH", "")
    additions = [str(root / "backend"), str(root)]
    env["PYTHONPATH"] = os.pathsep.join([*additions, current]) if current else os.pathsep.join(additions)
    env.setdefault("PYTHONDONTWRITEBYTECODE", "1")
    return env


def _redact_runtime_text(text: str, root: Path) -> str:
    redacted = str(text or "")
    replacements = [str(root), str(root.parent), str(Path.home())]
    for value in sorted({item for item in replacements if item}, key=len, reverse=True):
        redacted = redacted.replace(value, "<redacted-path>")
    redacted = re.sub(r"(?i)(api[_-]?key|token|secret|authorization)(['\"=: ]+)[^\s'\",]+", r"\1\2<redacted-secret>", redacted)
    return redacted


def _blocked_runtime_run(*, workspace_id: str, codebase_id: str, snapshot_id: str, command_id: str, patch_plan_id: str | None, reason: str) -> dict[str, Any]:
    run_id = _stable_id("runblocked", codebase_id, snapshot_id, command_id, patch_plan_id)
    return {
        "schema_version": RUNTIME_SCHEMA_VERSION,
        "workspace_id": workspace_id,
        "codebase_id": codebase_id,
        "snapshot_id": snapshot_id,
        "run_id": run_id,
        "command_id": command_id,
        "status": "blocked",
        "exit_code": None,
        "duration_ms": 0,
        "linked_patch_plan_id": patch_plan_id,
        "linked_static_evidence": [],
        "logs": {"stdout_preview": "", "stderr_preview": "", "redacted": True},
        "error": {"code": reason, "message": "Runtime command was not executed because it is not allowlisted.", "retryable": False},
        "warnings": [reason],
        "unresolved": [{"code": reason, "message": "Runtime command was not executed.", "retryable": False}],
        "artifact_refs": [],
        "created_at": now(),
    }


def _fingerprint_index(workspace_id: str, codebase_id: str, snapshot_id: str, files: list[dict[str, Any]]) -> dict[str, Any]:
    rows = []
    for record in files:
        path = str(record.get("path") or "")
        if not path:
            continue
        fingerprint = _file_record_fingerprint(record)
        rows.append(
            {
                "path": path,
                "fingerprint": fingerprint,
                "included": bool(record.get("included")),
                "language": record.get("language"),
                "size_bytes": record.get("size_bytes"),
                "sha256": record.get("sha256"),
                "evidence_refs": [f"code://{codebase_id}/{snapshot_id}/{path}"] if record.get("included") else [],
            }
        )
    return {
        "schema_version": INCREMENTAL_SCHEMA_VERSION,
        "workspace_id": workspace_id,
        "codebase_id": codebase_id,
        "snapshot_id": snapshot_id,
        "file_count": len(rows),
        "files": rows,
        "artifact_refs": [{"type": "fingerprint_index", "artifact_ref": f"coding-agent://{codebase_id}/incremental/fingerprint_index/{snapshot_id}.json"}],
        "created_at": now(),
    }


def _file_record_fingerprint(record: dict[str, Any]) -> str:
    stable = {
        "path": record.get("path"),
        "included": record.get("included"),
        "skip_reason": record.get("skip_reason"),
        "language": record.get("language"),
        "loc": record.get("loc") or record.get("line_count"),
        "size_bytes": record.get("size_bytes"),
        "sha256": record.get("sha256"),
    }
    return hashlib.sha256(repr(sorted(stable.items())).encode("utf-8")).hexdigest()


def _snapshot_changed_files(from_index: dict[str, Any], to_index: dict[str, Any]) -> list[dict[str, Any]]:
    before = {row["path"]: row for row in from_index.get("files", [])}
    after = {row["path"]: row for row in to_index.get("files", [])}
    rows = []
    for path in sorted(set(before) | set(after)):
        old = before.get(path)
        new = after.get(path)
        if old and new and old.get("fingerprint") == new.get("fingerprint"):
            continue
        if old and not new:
            change_type = "deleted"
            fingerprint = str(old.get("fingerprint") or "")
            evidence_refs = list(old.get("evidence_refs") or [])
        elif new and not old:
            change_type = "added"
            fingerprint = str(new.get("fingerprint") or "")
            evidence_refs = list(new.get("evidence_refs") or [])
        else:
            change_type = "modified"
            fingerprint = str(new.get("fingerprint") or "")
            evidence_refs = list(new.get("evidence_refs") or [])
        rows.append(
            {
                "change_id": _stable_id("change", path, change_type, fingerprint),
                "path": path,
                "change_type": change_type,
                "fingerprint": fingerprint,
                "language": (new or old or {}).get("language"),
                "evidence_refs": evidence_refs,
                "needs_review": [] if evidence_refs else ["changed file has no source evidence ref"],
            }
        )
    return rows


def _changed_symbol_hints(codebase_id: str, snapshot_id: str, changed_files: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows = []
    for item in changed_files:
        path = str(item.get("path") or "")
        if not path.endswith((".py", ".ts", ".tsx", ".vue", ".js")):
            continue
        lowered = path.lower()
        symbol_type = "public_surface_hint" if any(part in lowered for part in ("api", "router", "mcp", "cli")) else "module_hint"
        rows.append(
            {
                "symbol_hint_id": _stable_id("symhint", path, item.get("change_type"), snapshot_id),
                "symbol_type": symbol_type,
                "path": path,
                "change_type": item.get("change_type"),
                "confidence": 0.72 if symbol_type == "public_surface_hint" else 0.55,
                "evidence_refs": item.get("evidence_refs", []),
                "needs_review": ["symbol-level diff requires rebuilding symbol index"],
            }
        )
    return rows


def _read_json_files(directory: Path) -> list[dict[str, Any]]:
    if not directory.exists():
        return []
    rows = []
    for path in sorted(directory.glob("*.json")):
        payload = read_json(path, None)
        if isinstance(payload, dict):
            rows.append(payload)
    return rows


def _workbench_graph(actionability: dict[str, Any], patch_plans: list[dict[str, Any]], runtime_runs: list[dict[str, Any]], diffs: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    nodes: list[dict[str, Any]] = []
    edges: list[dict[str, Any]] = []
    index = actionability.get("index", {})
    nodes.append({"node_id": "actionability", "node_type": "artifact", "label": "Actionability", "artifact_ref": actionability_artifact_refs(str(index.get("codebase_id") or ""))[0]["artifact_ref"]})
    for plan in patch_plans[:20]:
        node_id = f"patch:{plan.get('patch_plan_id')}"
        nodes.append({"node_id": node_id, "node_type": "patch_plan", "label": f"Patch {plan.get('status')}", "artifact_ref": patch_plan_artifact_ref(str(plan.get("codebase_id") or ""), str(plan.get("patch_plan_id") or ""))["artifact_ref"]})
        edges.append({"edge_id": _stable_id("edge", "actionability", node_id), "from": "actionability", "to": node_id, "relation_type": "informs"})
    for run in runtime_runs[:20]:
        node_id = f"runtime:{run.get('run_id')}"
        nodes.append({"node_id": node_id, "node_type": "runtime_run", "label": f"Runtime {run.get('status')}", "artifact_ref": runtime_run_artifact_ref(str(run.get("codebase_id") or ""), str(run.get("run_id") or ""))["artifact_ref"]})
        if run.get("linked_patch_plan_id"):
            edges.append({"edge_id": _stable_id("edge", f"patch:{run.get('linked_patch_plan_id')}", node_id), "from": f"patch:{run.get('linked_patch_plan_id')}", "to": node_id, "relation_type": "validated_by"})
    for diff in diffs[:20]:
        node_id = f"diff:{diff.get('diff_id')}"
        nodes.append({"node_id": node_id, "node_type": "incremental_diff", "label": f"Diff {diff.get('summary', {}).get('changed_file_count', 0)} files", "artifact_ref": snapshot_diff_artifact_ref(str(diff.get("codebase_id") or ""), str(diff.get("diff_id") or ""))["artifact_ref"]})
        edges.append({"edge_id": _stable_id("edge", "actionability", node_id), "from": "actionability", "to": node_id, "relation_type": "changed_by"})
    return _dedupe(nodes, "node_id"), _dedupe(edges, "edge_id")


def _workbench_risk_lanes(patch_plans: list[dict[str, Any]], runtime_runs: list[dict[str, Any]], diffs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for plan in patch_plans:
        rows.append(
            {
                "lane_id": _stable_id("lane", "patch", plan.get("patch_plan_id")),
                "title": f"Patch plan {plan.get('status')}",
                "priority": "high" if plan.get("status") == "blocked" else "medium" if plan.get("status") == "needs_review" else "low",
                "evidence_refs": list(plan.get("evidence") or []),
                "needs_review": list(plan.get("needs_review") or []),
            }
        )
    for run in runtime_runs:
        if run.get("status") != "passed":
            rows.append(
                {
                    "lane_id": _stable_id("lane", "runtime", run.get("run_id")),
                    "title": f"Runtime validation {run.get('status')}",
                    "priority": "high",
                    "evidence_refs": list(run.get("linked_static_evidence") or []),
                    "needs_review": [item.get("message") for item in run.get("unresolved", []) if item.get("message")],
                }
            )
    for diff in diffs:
        if diff.get("summary", {}).get("changed_file_count", 0):
            rows.append(
                {
                    "lane_id": _stable_id("lane", "diff", diff.get("diff_id")),
                    "title": f"{diff.get('summary', {}).get('changed_file_count', 0)} changed files since previous snapshot",
                    "priority": "medium",
                    "evidence_refs": sorted({ref for row in diff.get("changed_files", []) for ref in row.get("evidence_refs", [])}),
                    "needs_review": [],
                }
            )
    return rows


def _workbench_blockers(patch_plans: list[dict[str, Any]], runtime_runs: list[dict[str, Any]], diffs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    blockers = []
    for plan in patch_plans:
        for item in plan.get("unresolved", []):
            blockers.append({"source": "patch_plan", "code": item.get("code"), "message": item.get("message"), "artifact_id": plan.get("patch_plan_id")})
    for run in runtime_runs:
        if run.get("status") in {"blocked", "failed", "timeout"}:
            error = run.get("error") or {}
            blockers.append({"source": "runtime", "code": error.get("code") or run.get("status"), "message": error.get("message") or run.get("status"), "artifact_id": run.get("run_id")})
    for diff in diffs:
        for item in diff.get("unresolved", []):
            blockers.append({"source": "incremental", "code": item.get("code"), "message": item.get("message"), "artifact_id": diff.get("diff_id")})
    return blockers


def _render_workbench_html(payload: dict[str, Any]) -> str:
    esc = html.escape
    sections = "\n".join(
        f"<li><strong>{esc(str(section['title']))}</strong>: {int(section.get('item_count') or 0)} items</li>"
        for section in payload.get("sections", [])
    )
    nodes = "\n".join(
        f"<tr><td>{esc(str(node.get('node_type')))}</td><td>{esc(str(node.get('label')))}</td><td>{esc(str(node.get('artifact_ref')))}</td></tr>"
        for node in payload.get("capability_graph", {}).get("nodes", [])[:80]
    )
    risks = "\n".join(
        f"<tr><td>{esc(str(row.get('priority')))}</td><td>{esc(str(row.get('title')))}</td><td>{len(row.get('evidence_refs') or [])}</td><td>{len(row.get('needs_review') or [])}</td></tr>"
        for row in payload.get("risk_lanes", [])[:80]
    )
    blockers = "\n".join(
        f"<li>{esc(str(item.get('source')))} / {esc(str(item.get('code')))}: {esc(str(item.get('message')))}</li>"
        for item in payload.get("blockers", [])[:80]
    )
    return f"""<!doctype html>
<html lang=\"zh-CN\">
<head><meta charset=\"utf-8\"><title>Coding Agent Review Workbench</title>
<style>body{{font-family:-apple-system,BlinkMacSystemFont,Segoe UI,sans-serif;margin:24px;line-height:1.5}}table{{border-collapse:collapse;width:100%;margin:12px 0}}td,th{{border:1px solid #ddd;padding:6px}}th{{background:#f5f5f5;text-align:left}}.grid{{display:grid;grid-template-columns:1fr 1fr;gap:16px}}</style></head>
<body>
<h1>Coding Agent Review Workbench</h1>
<p>Codebase: {esc(str(payload.get('codebase_id')))} | Snapshot: {esc(str(payload.get('snapshot_id')))}</p>
<div class=\"grid\"><section><h2>Sections</h2><ul>{sections}</ul></section><section><h2>Blockers</h2><ul>{blockers or '<li>None</li>'}</ul></section></div>
<h2>Capability Graph Nodes</h2><table><thead><tr><th>Type</th><th>Label</th><th>Artifact</th></tr></thead><tbody>{nodes}</tbody></table>
<h2>Risk Lanes</h2><table><thead><tr><th>Priority</th><th>Title</th><th>Evidence</th><th>Needs Review</th></tr></thead><tbody>{risks}</tbody></table>
</body></html>"""


def _render_workbench_mermaid(payload: dict[str, Any]) -> str:
    lines = ["flowchart TD"]
    node_ids = set()
    for node in payload.get("capability_graph", {}).get("nodes", [])[:60]:
        node_id = _mermaid_id(str(node.get("node_id") or "node"))
        node_ids.add(str(node.get("node_id") or ""))
        label = html.escape(str(node.get("label") or node.get("node_id") or "node")).replace('"', "'")
        lines.append(f"  {node_id}[\"{label}\"]")
    for edge in payload.get("capability_graph", {}).get("edges", [])[:80]:
        if str(edge.get("from")) not in node_ids or str(edge.get("to")) not in node_ids:
            continue
        lines.append(f"  {_mermaid_id(str(edge.get('from')))} -->|{html.escape(str(edge.get('relation_type') or 'related')).replace(chr(34), chr(39))}| {_mermaid_id(str(edge.get('to')))}")
    return "\n".join(lines) + "\n"


def _mermaid_id(value: str) -> str:
    return "n_" + re.sub(r"[^A-Za-z0-9_]", "_", value)


def _patch_edit_candidates(codebase_id: str, snapshot_id: str, task: str, recommendations: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    candidates: list[dict[str, Any]] = []
    unresolved: list[dict[str, Any]] = []
    for item in recommendations:
        path = item.get("path")
        line_range = item.get("line_range")
        if not path or not line_range:
            continue
        if _is_weak_patch_candidate(item):
            continue
        evidence_refs = list(item.get("evidence_refs") or [])
        needs_review = sorted(set(item.get("needs_review") or []))
        if not evidence_refs:
            needs_review.append("edit candidate has no accepted evidence and requires review")
        candidate_id = _stable_id("patchcand", item.get("recommendation_id"), path, line_range, task)
        candidates.append(
            {
                "candidate_id": candidate_id,
                "source_recommendation_id": item.get("recommendation_id"),
                "path": path,
                "line_range": line_range,
                "qualified_name": item.get("qualified_name"),
                "change_intent": _change_intent(task),
                "confidence": 0.86 if evidence_refs and not needs_review else 0.55,
                "reason_codes": sorted(set(item.get("reason_codes") or [])),
                "evidence_refs": evidence_refs,
                "needs_review": sorted(set(needs_review)),
                "mapped_tests": list(item.get("mapped_tests") or []),
            }
        )
    if not candidates:
        unresolved.append(
            {
                "code": "NO_EDIT_CANDIDATES",
                "message": "No deterministic line-backed edit candidates were available for this task.",
                "retryable": False,
                "next_actions": ["narrow the task", "provide focus_paths", "build V2.11 actionability artifacts"],
            }
        )
    return candidates[:50], unresolved


def _patch_validation_plan(codebase_id: str, snapshot_id: str, candidates: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    rows: list[dict[str, Any]] = []
    unresolved: list[dict[str, Any]] = []
    seen: set[str] = set()
    for candidate in candidates:
        for mapping in candidate.get("mapped_tests", []):
            test_path = mapping.get("test_path")
            if not test_path:
                continue
            command = f"pytest {test_path}"
            key = f"{command}:{candidate['candidate_id']}"
            if key in seen:
                continue
            seen.add(key)
            status = "accepted" if mapping.get("status") == "accepted" else "needs_review"
            rows.append(
                {
                    "command_id": _stable_id("valcmd", codebase_id, snapshot_id, command, candidate["candidate_id"]),
                    "label": f"Plan pytest for {test_path}",
                    "command": command,
                    "execution_policy": "plan_only",
                    "status": status,
                    "source": "v2_11_test_mapping",
                    "covers_candidate_ids": [candidate["candidate_id"]],
                    "evidence_refs": list(mapping.get("evidence_refs") or candidate.get("evidence_refs") or []),
                    "needs_review": [] if status == "accepted" else ["test mapping is weak and must be confirmed before execution"],
                }
            )
            if len(rows) >= 20:
                break
        if len(rows) >= 20:
            break
    if not rows and candidates:
        rows.append(
            {
                "command_id": _stable_id("valcmd", codebase_id, snapshot_id, "manual_validation", [item["candidate_id"] for item in candidates]),
                "label": "Manual validation selection required",
                "command": "",
                "execution_policy": "plan_only",
                "status": "needs_review",
                "source": "no_deterministic_test_mapping",
                "covers_candidate_ids": [item["candidate_id"] for item in candidates[:10]],
                "evidence_refs": sorted({ref for item in candidates for ref in item.get("evidence_refs", [])}),
                "needs_review": ["No deterministic validation command was mapped; reviewer must choose tests before editing"],
            }
        )
        unresolved.append(
            {
                "code": "VALIDATION_TEST_NOT_FOUND",
                "message": "No deterministic validation command was mapped for the proposed edit candidates.",
                "retryable": False,
                "next_actions": ["inspect mapped tests", "add focus_paths", "select validation manually"],
            }
        )
    return rows, unresolved


def _patch_rollback_plan(candidates: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    by_path: dict[str, list[dict[str, Any]]] = {}
    unresolved: list[dict[str, Any]] = []
    for candidate in candidates:
        path = str(candidate.get("path") or "")
        if not path:
            unresolved.append(
                {
                    "code": "ROLLBACK_SCOPE_INCOMPLETE",
                    "message": f"Candidate {candidate.get('candidate_id')} has no file path and cannot be covered by rollback.",
                    "retryable": False,
                    "next_actions": ["review candidate source path"],
                }
            )
            continue
        by_path.setdefault(path, []).append(candidate)
    rows = []
    for path, path_candidates in sorted(by_path.items()):
        rows.append(
            {
                "rollback_step_id": _stable_id("rollback", path, [item["candidate_id"] for item in path_candidates]),
                "path": path,
                "strategy": "restore_original",
                "execution_policy": "manual_review_only",
                "covers_candidate_ids": [item["candidate_id"] for item in path_candidates],
                "manual_action": "If edits are later applied by another tool, restore this file to its pre-edit version or revert the corresponding hunk.",
                "evidence_refs": sorted({ref for item in path_candidates for ref in item.get("evidence_refs", [])}),
                "needs_review": [],
            }
        )
    if candidates and sum(len(row["covers_candidate_ids"]) for row in rows) < len(candidates):
        unresolved.append(
            {
                "code": "ROLLBACK_SCOPE_INCOMPLETE",
                "message": "Rollback scope does not cover all edit candidates.",
                "retryable": False,
                "next_actions": ["remove uncovered candidates", "resolve candidate paths"],
            }
        )
    return rows, unresolved


def _patch_options(task: str, candidates: list[dict[str, Any]], validation_plan: list[dict[str, Any]], rollback_plan: list[dict[str, Any]], *, max_options: int) -> list[dict[str, Any]]:
    max_options = max(1, min(int(max_options or 3), 5))
    validation_ids = [row["command_id"] for row in validation_plan]
    rollback_ids = [row["rollback_step_id"] for row in rollback_plan]
    options: list[dict[str, Any]] = []
    if not candidates:
        return options
    option_specs = [("minimal", candidates[:3]), ("broader", candidates[:8])]
    doc_or_test = [item for item in candidates if any(part in str(item.get("path") or "").lower() for part in ("doc", "test", "readme"))]
    if doc_or_test:
        option_specs.append(("docs_or_tests_first", doc_or_test[:5]))
    for option_type, option_candidates in option_specs:
        if len(options) >= max_options or not option_candidates:
            continue
        evidence_refs = sorted({ref for item in option_candidates for ref in item.get("evidence_refs", [])})
        needs_review = sorted({review for item in option_candidates for review in item.get("needs_review", [])})
        options.append(
            {
                "option_id": _stable_id("patchopt", option_type, task, [item["candidate_id"] for item in option_candidates]),
                "option_type": option_type,
                "summary": _patch_option_summary(option_type, option_candidates),
                "risk_level": "medium" if needs_review else "low",
                "candidate_ids": [item["candidate_id"] for item in option_candidates],
                "validation_command_ids": validation_ids,
                "rollback_step_ids": rollback_ids,
                "evidence_refs": evidence_refs,
                "needs_review": needs_review,
            }
        )
    return options


def _patch_readiness(candidates: list[dict[str, Any]], patch_options: list[dict[str, Any]], validation_plan: list[dict[str, Any]], rollback_plan: list[dict[str, Any]], unresolved: list[dict[str, Any]], needs_review: list[str]) -> dict[str, Any]:
    reason_codes: list[str] = []
    if not candidates:
        return {"score": 0.0, "status": "blocked", "reason_codes": ["no_edit_candidates"]}
    evidence_ratio = sum(1 for item in candidates if item.get("evidence_refs")) / max(1, len(candidates))
    validation_ready = bool(validation_plan) and all(row.get("execution_policy") == "plan_only" for row in validation_plan)
    rollback_coverage = _rollback_covers_all(candidates, rollback_plan)
    score = 0.35 + evidence_ratio * 0.35 + (0.15 if patch_options else 0.0) + (0.1 if validation_ready else 0.0) + (0.05 if rollback_coverage else 0.0)
    if evidence_ratio < 1:
        reason_codes.append("some_candidates_need_review")
    if not validation_ready:
        reason_codes.append("validation_plan_missing")
    if not rollback_coverage:
        reason_codes.append("rollback_scope_incomplete")
    if unresolved:
        reason_codes.extend(str(item.get("code") or "unresolved").lower() for item in unresolved)
    if any(item.get("code") in {"NO_EDIT_CANDIDATES", "ROLLBACK_SCOPE_INCOMPLETE"} for item in unresolved):
        status = "blocked"
        score = min(score, 0.45)
    elif needs_review or unresolved or score < 0.8:
        status = "needs_review"
    else:
        status = "ready_for_review"
    if not reason_codes:
        reason_codes.append("evidence_validation_and_rollback_present")
    return {"score": round(min(score, 1.0), 3), "status": status, "reason_codes": sorted(set(reason_codes))}


def _collect_patch_needs_review(candidates: list[dict[str, Any]], patch_options: list[dict[str, Any]], validation_plan: list[dict[str, Any]], rollback_plan: list[dict[str, Any]], unresolved: list[dict[str, Any]]) -> list[str]:
    rows: list[str] = []
    for collection in (candidates, patch_options, validation_plan, rollback_plan):
        for item in collection:
            rows.extend(str(value) for value in item.get("needs_review", []) if value)
    rows.extend(str(item.get("message") or item.get("code")) for item in unresolved if item)
    return rows


def _patch_user_sections(candidates: list[dict[str, Any]], patch_options: list[dict[str, Any]], validation_plan: list[dict[str, Any]], rollback_plan: list[dict[str, Any]], readiness: dict[str, Any], unresolved: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {"section_id": "proposed_files", "title": "Proposed Files and Symbols", "item_count": len({item.get("path") for item in candidates if item.get("path")}), "summary": "Review candidate files, symbols, and line ranges before editing."},
        {"section_id": "patch_options", "title": "Patch Options", "item_count": len(patch_options), "summary": "Choose a minimal, broader, or docs/tests-first option when available."},
        {"section_id": "evidence_and_needs_review", "title": "Evidence and Needs Review", "item_count": sum(1 for item in candidates if item.get("evidence_refs") or item.get("needs_review")), "summary": "Every candidate is evidence-backed or explicitly marked for review."},
        {"section_id": "validation_plan", "title": "Validation Plan", "item_count": len(validation_plan), "summary": "Validation commands are descriptors only and are not executed by V2.12."},
        {"section_id": "rollback_plan", "title": "Rollback Plan", "item_count": len(rollback_plan), "summary": "Rollback scope covers proposed files when candidate paths are known."},
        {"section_id": "readiness_and_blockers", "title": "Readiness and Blockers", "item_count": len(unresolved), "summary": f"Readiness is {readiness.get('status')} with score {readiness.get('score')}."},
    ]


def _patch_option_summary(option_type: str, candidates: list[dict[str, Any]]) -> str:
    paths = sorted({str(item.get("path") or "") for item in candidates if item.get("path")})
    prefix = {"minimal": "Smallest reviewable edit set", "broader": "Broader implementation sweep", "docs_or_tests_first": "Documentation or test-first option"}.get(option_type, "Patch option")
    return f"{prefix}: {', '.join(paths[:5])}"


def _is_weak_patch_candidate(item: dict[str, Any]) -> bool:
    reason_codes = set(str(code) for code in item.get("reason_codes", []) if code)
    if not reason_codes:
        return True
    strong = {"focus_path_match", "api_surface_hint", "agent_interface_hint"}
    if reason_codes & strong:
        return False
    if any(code.startswith("task_term:") for code in reason_codes):
        return False
    return reason_codes <= {"public_or_core_file"}


def _rollback_covers_all(candidates: list[dict[str, Any]], rollback_plan: list[dict[str, Any]]) -> bool:
    candidate_ids = {str(item.get("candidate_id")) for item in candidates if item.get("candidate_id")}
    covered = {str(candidate_id) for row in rollback_plan for candidate_id in row.get("covers_candidate_ids", [])}
    return bool(candidate_ids) and candidate_ids <= covered


def _change_intent(task: str) -> str:
    lowered = (task or "").lower()
    if any(term in lowered for term in ("delete", "remove", "archive")):
        return "remove_or_archive"
    if any(term in lowered for term in ("rename", "move")):
        return "rename_or_move"
    if any(term in lowered for term in ("add", "create", "新增", "新建")):
        return "add_or_extend"
    return "modify_or_review"


def _ensure_actionability(service: CodingAgentActionabilityService, codebase_id: str, *, snapshot_id: str | None) -> dict[str, Any]:
    try:
        return service.read_actionability(codebase_id)
    except FileNotFoundError:
        return service.build_actionability(codebase_id, snapshot_id=snapshot_id)


def _build_ast_facts(*, workspace_id: str, codebase_id: str, snapshot_id: str, root: Path, files: list[dict[str, Any]], symbols: list[dict[str, Any]], surfaces: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    definitions: list[dict[str, Any]] = []
    references: list[dict[str, Any]] = []
    warnings: list[dict[str, Any]] = []
    symbol_by_path = {str(item.get("path") or item.get("source_file") or ""): item for item in symbols if item.get("kind") == "module"}
    surfaces_by_path: dict[str, list[dict[str, Any]]] = {}
    for surface in surfaces:
        path = str(surface.get("source_file") or surface.get("path") or "")
        if path:
            surfaces_by_path.setdefault(path, []).append(surface)
    for record in files:
        rel = str(record.get("path") or "")
        if not record.get("included") or not rel.endswith(".py"):
            continue
        text = _read_text(root / rel)
        if text is None:
            warnings.append({"path": rel, "code": "READ_FAILED"})
            continue
        try:
            tree = ast.parse(text)
        except SyntaxError as exc:
            warnings.append({"path": rel, "code": "SYNTAX_ERROR", "line": exc.lineno})
            continue
        module = _module_name(rel)
        module_def = _definition(workspace_id, codebase_id, snapshot_id, rel, module, "module", module, [1, max(1, len(text.splitlines()))])
        definitions.append(module_def)
        for surface in surfaces_by_path.get(rel, []):
            references.append(
                _reference(
                    workspace_id,
                    codebase_id,
                    snapshot_id,
                    rel,
                    "exposes_surface",
                    module_def["definition_id"],
                    str(surface.get("surface_id") or surface.get("name") or ""),
                    [int((surface.get("line_range") or [1, 1])[0]), int((surface.get("line_range") or [1, 1])[-1])],
                    "deterministic_public_surface_inventory",
                )
            )
        for node in ast.walk(tree):
            if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
                qn = f"{module}.{node.name}"
                kind = "class" if isinstance(node, ast.ClassDef) else "function"
                line_range = [int(getattr(node, "lineno", 1) or 1), int(getattr(node, "end_lineno", getattr(node, "lineno", 1)) or 1)]
                definition = _definition(workspace_id, codebase_id, snapshot_id, rel, node.name, kind, qn, line_range)
                definitions.append(definition)
                references.append(_reference(workspace_id, codebase_id, snapshot_id, rel, "defines", module_def["definition_id"], definition["definition_id"], line_range, "python_ast"))
                local_ref_count = 0
                for child in ast.walk(node):
                    if isinstance(child, ast.Import):
                        for alias in child.names:
                            references.append(_reference(workspace_id, codebase_id, snapshot_id, rel, "imports", definition["definition_id"], alias.name, [child.lineno, child.lineno], "python_ast_import"))
                    elif isinstance(child, ast.ImportFrom) and child.module:
                        references.append(_reference(workspace_id, codebase_id, snapshot_id, rel, "imports", definition["definition_id"], child.module, [child.lineno, child.lineno], "python_ast_import"))
                    elif isinstance(child, ast.Call) and local_ref_count < 25:
                        target = _call_target_name(child)
                        if target:
                            local_ref_count += 1
                            references.append(_reference(workspace_id, codebase_id, snapshot_id, rel, "references", definition["definition_id"], target, [getattr(child, "lineno", line_range[0]), getattr(child, "lineno", line_range[0])], "python_ast_call_reference"))
    if symbol_by_path and not definitions:
        warnings.append({"code": "NO_AST_DEFINITIONS", "message": "No AST definitions extracted"})
    return _dedupe(definitions, "definition_id"), _dedupe(references, "reference_id"), warnings


def _build_test_mapping(workspace_id: str, codebase_id: str, snapshot_id: str, definitions: list[dict[str, Any]], files: list[dict[str, Any]]) -> list[dict[str, Any]]:
    test_paths = [str(row.get("path") or "") for row in files if row.get("included") and _is_test_path(str(row.get("path") or ""))]
    rows: list[dict[str, Any]] = []
    for definition in definitions:
        if definition["kind"] == "module":
            continue
        candidates = []
        base = Path(definition["path"]).stem
        name = str(definition["name"]).lower()
        for test_path in test_paths:
            lower = test_path.lower()
            if base.lower() in lower or name in lower:
                candidates.append(test_path)
        if not candidates:
            if _looks_public_or_core(definition):
                rows.append(_test_mapping_row(workspace_id, codebase_id, snapshot_id, definition, None, "needs_review", 0.35, "no likely test path found"))
            continue
        for test_path in candidates[:5]:
            status = "accepted" if base.lower() in test_path.lower() else "needs_review"
            confidence = 0.86 if status == "accepted" else 0.55
            rows.append(_test_mapping_row(workspace_id, codebase_id, snapshot_id, definition, test_path, status, confidence, "path/name heuristic"))
    return rows


def _test_mapping_row(workspace_id: str, codebase_id: str, snapshot_id: str, definition: dict[str, Any], test_path: str | None, status: str, confidence: float, reason: str) -> dict[str, Any]:
    return {
        "mapping_id": _stable_id("testmap", definition["definition_id"], test_path or "missing"),
        "schema_version": SCHEMA_VERSION,
        "workspace_id": workspace_id,
        "codebase_id": codebase_id,
        "snapshot_id": snapshot_id,
        "definition_id": definition["definition_id"],
        "qualified_name": definition["qualified_name"],
        "source_path": definition["path"],
        "test_path": test_path,
        "status": status,
        "confidence": confidence,
        "reason": reason,
        "evidence_refs": list(definition.get("evidence_refs") or []),
        "needs_review": [] if status == "accepted" else ["test mapping is weak or missing"],
    }


def _definition(workspace_id: str, codebase_id: str, snapshot_id: str, path: str, name: str, kind: str, qualified_name: str, line_range: list[int]) -> dict[str, Any]:
    definition_id = _stable_id("def", path, qualified_name, kind)
    return {
        "definition_id": definition_id,
        "schema_version": SCHEMA_VERSION,
        "workspace_id": workspace_id,
        "codebase_id": codebase_id,
        "snapshot_id": snapshot_id,
        "kind": kind,
        "name": name,
        "qualified_name": qualified_name,
        "path": path,
        "line_range": line_range,
        "confidence": 1.0,
        "provider": "python_ast",
        "evidence_refs": [f"code://{codebase_id}/{snapshot_id}/{path}#L{line_range[0]}-L{line_range[1]}"],
    }


def _reference(workspace_id: str, codebase_id: str, snapshot_id: str, path: str, relation_type: str, source_id: str, target: str, line_range: list[int], extractor: str) -> dict[str, Any]:
    return {
        "reference_id": _stable_id("ref", path, relation_type, source_id, target, line_range),
        "schema_version": SCHEMA_VERSION,
        "workspace_id": workspace_id,
        "codebase_id": codebase_id,
        "snapshot_id": snapshot_id,
        "relation_type": relation_type,
        "semantic_claim": "dependency_evidence" if relation_type in {"imports", "references"} else "implementation_hint",
        "from_definition_id": source_id,
        "to_target": target,
        "path": path,
        "line_range": line_range,
        "confidence": 0.95 if relation_type != "references" else 0.7,
        "extractor": extractor,
        "evidence_refs": [f"code://{codebase_id}/{snapshot_id}/{path}#L{line_range[0]}-L{line_range[1]}"],
    }


def _score_definition(definition: dict[str, Any], terms: set[str], focus_paths: list[str]) -> tuple[float, list[str]]:
    haystack = " ".join([str(definition.get("path") or ""), str(definition.get("qualified_name") or ""), str(definition.get("name") or "")]).lower()
    score = 0.0
    reason_codes: list[str] = []
    for term in terms:
        if term and term in haystack:
            score += 0.2
            reason_codes.append(f"task_term:{term}")
    for focus in focus_paths:
        if focus and focus in str(definition.get("path") or ""):
            score += 0.5
            reason_codes.append("focus_path_match")
    if any(word in haystack for word in {"api", "router", "route"} & terms):
        score += 0.2
        reason_codes.append("api_surface_hint")
    if any(word in haystack for word in {"mcp", "cli"} & terms):
        score += 0.2
        reason_codes.append("agent_interface_hint")
    if _looks_public_or_core(definition):
        score += 0.1
        reason_codes.append("public_or_core_file")
    return min(score, 1.0), sorted(set(reason_codes))


def _task_terms(task: str) -> set[str]:
    aliases = {
        "api": {"api", "route", "router", "http"},
        "http": {"api", "route", "router", "http"},
        "mcp": {"mcp", "tool", "dispatcher"},
        "cli": {"cli", "command", "parser"},
        "test": {"test", "tests", "pytest"},
        "quality": {"quality", "governance"},
        "codebase": {"codebase", "code_assets"},
        "actionability": {"actionability", "coding_agent"},
    }
    terms = {part.lower() for part in re.split(r"[^A-Za-z0-9_]+", task or "") if len(part) >= 3}
    expanded = set(terms)
    for term in terms:
        expanded |= aliases.get(term, set())
    return expanded


def _blocker_row(task: str, focus_paths: list[str]) -> dict[str, Any]:
    return {
        "target_id": _stable_id("blocker", task, focus_paths),
        "target_type": "blocker",
        "path": None,
        "line_range": None,
        "qualified_name": None,
        "score": 0.0,
        "status": "needs_review",
        "reason_codes": ["no_deterministic_match"],
        "evidence_refs": [],
        "related_reference_ids": [],
        "mapped_tests": [],
        "needs_review": ["No deterministic AST-backed impact target matched this task"],
    }


def _looks_public_or_core(definition: dict[str, Any]) -> bool:
    path = str(definition.get("path") or "")
    return any(part in path for part in ("api/", "mcp_", "cli_", "code_assets", "tests/"))


def _is_test_path(path: str) -> bool:
    normalized = path.lower()
    return "/tests/" in f"/{normalized}" or normalized.startswith("tests/") or Path(path).name.startswith("test_")


def _call_target_name(node: ast.Call) -> str | None:
    func = node.func
    if isinstance(func, ast.Name):
        return func.id
    if isinstance(func, ast.Attribute):
        parts = [func.attr]
        value = func.value
        while isinstance(value, ast.Attribute):
            parts.append(value.attr)
            value = value.value
        if isinstance(value, ast.Name):
            parts.append(value.id)
        return ".".join(reversed(parts[-3:]))
    return None


def _read_text(path: Path) -> str | None:
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return None


def _module_name(path: str) -> str:
    return str(Path(path).with_suffix("")).replace("/", ".")


def _stable_id(prefix: str, *parts: Any) -> str:
    raw = repr(parts)
    digest = hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]
    return f"{prefix}_{digest}"


def _dedupe(rows: list[dict[str, Any]], key: str) -> list[dict[str, Any]]:
    seen = set()
    result = []
    for row in rows:
        value = row.get(key)
        if value in seen:
            continue
        seen.add(value)
        result.append(row)
    return result

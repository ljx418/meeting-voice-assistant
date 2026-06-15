"""Public service facade for V2.25-V2.30 architecture intent artifacts."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from ..artifacts import snapshot_files_path, read_jsonl
from ..registry import CodebaseRegistry
from ..snapshot import CodebaseSnapshotService
from .context_pack import build_architecture_context_pack_v4, read_architecture_context_pack_v4
from .diagram_claims import build_diagram_claims, read_diagram_claims
from .diagram_verification import build_diagram_code_verification, read_diagram_code_verification
from .governance import confirm_architecture_target, read_architecture_governance, revoke_architecture_confirmation
from .intent_inference import build_intent_inference, read_intent_inference
from .proof_graph import build_code_proof_graph, read_code_proof_graph
from .report import build_architecture_intent_report, read_architecture_intent_report
from .source_model import build_architecture_source_model, read_architecture_source_model


class ArchitectureIntentService:
    def __init__(self, workspace: Path, *, workspace_id: str) -> None:
        self.workspace = Path(workspace)
        self.workspace_id = workspace_id
        self.registry = CodebaseRegistry(workspace, workspace_id=workspace_id)
        self.snapshots = CodebaseSnapshotService(workspace, workspace_id=workspace_id)

    def build_pipeline(self, codebase_id: str, *, snapshot_id: str | None = None, mode: str = "architecture_review") -> dict[str, Any]:
        asset = self.registry.describe(codebase_id)
        if asset.status != "active":
            raise ValueError("CODEBASE_NOT_ACTIVE")
        resolved_snapshot_id = snapshot_id or self._latest_snapshot_id(codebase_id)
        self.snapshots.read_snapshot(codebase_id, resolved_snapshot_id)
        files = read_jsonl(snapshot_files_path(self.workspace, codebase_id, resolved_snapshot_id))
        if not files:
            raise FileNotFoundError("SNAPSHOT_FILES_NOT_FOUND")
        root = Path(asset.root_path).expanduser().resolve()
        source_model = build_architecture_source_model(
            workspace=self.workspace,
            workspace_id=self.workspace_id,
            codebase_id=codebase_id,
            snapshot_id=resolved_snapshot_id,
            root=root,
            files=files,
        )
        claims = build_diagram_claims(workspace=self.workspace, workspace_id=self.workspace_id, codebase_id=codebase_id, snapshot_id=resolved_snapshot_id)
        proof_graph = build_code_proof_graph(workspace=self.workspace, workspace_id=self.workspace_id, codebase_id=codebase_id, snapshot_id=resolved_snapshot_id)
        intent = build_intent_inference(workspace=self.workspace, workspace_id=self.workspace_id, codebase_id=codebase_id, snapshot_id=resolved_snapshot_id)
        verification = build_diagram_code_verification(workspace=self.workspace, workspace_id=self.workspace_id, codebase_id=codebase_id, snapshot_id=resolved_snapshot_id)
        context_pack = build_architecture_context_pack_v4(
            workspace=self.workspace,
            workspace_id=self.workspace_id,
            codebase_id=codebase_id,
            snapshot_id=resolved_snapshot_id,
            mode=mode,
        )
        report = build_architecture_intent_report(workspace=self.workspace, workspace_id=self.workspace_id, codebase_id=codebase_id, snapshot_id=resolved_snapshot_id)
        return {
            "schema_version": source_model.get("schema_version", "v2.25"),
            "workspace_id": self.workspace_id,
            "codebase_id": codebase_id,
            "snapshot_id": resolved_snapshot_id,
            "source_model": public_source_model_payload(source_model),
            "diagram_claims": public_diagram_claim_payload(claims),
            "proof_graph": public_proof_graph_payload(proof_graph),
            "intent_inference": public_intent_inference_payload(intent),
            "diagram_verification": public_diagram_verification_payload(verification),
            "context_pack": public_context_pack_v4_payload(context_pack),
            "report": public_report_payload(report),
            "artifact_refs": _all_artifact_refs(source_model, claims, proof_graph, intent, verification, context_pack, report),
            "warnings": [],
            "next_actions": [
                "knowledge_architecture_intent_report",
                "knowledge_diagram_code_verification",
                "knowledge_architecture_context_pack_v4",
            ],
        }

    def read_report(self, codebase_id: str) -> dict[str, Any]:
        self.registry.describe(codebase_id)
        return public_report_payload(read_architecture_intent_report(workspace=self.workspace, codebase_id=codebase_id))

    def read_context_pack(self, codebase_id: str) -> dict[str, Any]:
        self.registry.describe(codebase_id)
        return public_context_pack_v4_payload(read_architecture_context_pack_v4(workspace=self.workspace, codebase_id=codebase_id))

    def read_verification(self, codebase_id: str) -> dict[str, Any]:
        self.registry.describe(codebase_id)
        return public_diagram_verification_payload(read_diagram_code_verification(workspace=self.workspace, codebase_id=codebase_id))

    def read_proof_graph(self, codebase_id: str) -> dict[str, Any]:
        self.registry.describe(codebase_id)
        return public_proof_graph_payload(read_code_proof_graph(workspace=self.workspace, codebase_id=codebase_id))

    def read_governance(self, codebase_id: str) -> dict[str, Any]:
        self.registry.describe(codebase_id)
        return public_governance_payload(read_architecture_governance(workspace=self.workspace, codebase_id=codebase_id))

    def confirm(
        self,
        codebase_id: str,
        *,
        snapshot_id: str | None = None,
        target_type: str,
        target_id: str,
        note: str = "",
        reviewer: str = "local",
    ) -> dict[str, Any]:
        self.registry.describe(codebase_id)
        resolved_snapshot_id = snapshot_id or self._snapshot_id_from_readback(codebase_id)
        payload = confirm_architecture_target(
            workspace=self.workspace,
            workspace_id=self.workspace_id,
            codebase_id=codebase_id,
            snapshot_id=resolved_snapshot_id,
            target_type=target_type,
            target_id=target_id,
            note=note,
            reviewer=reviewer,
        )
        return public_governance_payload(payload)

    def revoke(
        self,
        codebase_id: str,
        *,
        snapshot_id: str | None = None,
        target_type: str,
        target_id: str,
        note: str = "",
        reviewer: str = "local",
    ) -> dict[str, Any]:
        self.registry.describe(codebase_id)
        resolved_snapshot_id = snapshot_id or self._snapshot_id_from_readback(codebase_id)
        payload = revoke_architecture_confirmation(
            workspace=self.workspace,
            workspace_id=self.workspace_id,
            codebase_id=codebase_id,
            snapshot_id=resolved_snapshot_id,
            target_type=target_type,
            target_id=target_id,
            note=note,
            reviewer=reviewer,
        )
        return public_governance_payload(payload)

    def _latest_snapshot_id(self, codebase_id: str) -> str:
        snapshots = self.snapshots.list_snapshots(codebase_id, limit=1)
        if not snapshots:
            raise FileNotFoundError("SNAPSHOT_NOT_FOUND")
        return str(snapshots[0].get("snapshot_id") or "")

    def _snapshot_id_from_readback(self, codebase_id: str) -> str:
        for reader in (
            lambda: read_architecture_intent_report(workspace=self.workspace, codebase_id=codebase_id),
            lambda: read_diagram_code_verification(workspace=self.workspace, codebase_id=codebase_id),
            lambda: read_intent_inference(workspace=self.workspace, codebase_id=codebase_id),
        ):
            payload = reader()
            snapshot_id = payload.get("snapshot_id")
            if snapshot_id:
                return str(snapshot_id)
        return self._latest_snapshot_id(codebase_id)


def public_source_model_payload(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": payload.get("schema_version"),
        "workspace_id": payload.get("workspace_id"),
        "codebase_id": payload.get("codebase_id"),
        "snapshot_id": payload.get("snapshot_id"),
        "summary": payload.get("summary", {}),
        "source_count": len(payload.get("sources") or []),
        "source_block_count": len(payload.get("source_blocks") or []),
        "diagram_cell_count": len(payload.get("diagram_cells") or []),
        "artifact_refs": payload.get("artifact_refs", []),
    }


def public_diagram_claim_payload(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": payload.get("schema_version"),
        "workspace_id": payload.get("workspace_id"),
        "codebase_id": payload.get("codebase_id"),
        "snapshot_id": payload.get("snapshot_id"),
        "summary": payload.get("summary", {}),
        "claim_count": len(payload.get("claims") or []),
        "relation_count": len(payload.get("relations") or []),
        "claims": list(payload.get("claims") or [])[:50],
        "artifact_refs": payload.get("artifact_refs", []),
    }


def public_proof_graph_payload(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": payload.get("schema_version"),
        "workspace_id": payload.get("workspace_id"),
        "codebase_id": payload.get("codebase_id"),
        "snapshot_id": payload.get("snapshot_id"),
        "summary": payload.get("summary", {}),
        "node_count": len(payload.get("nodes") or []),
        "edge_count": len(payload.get("edges") or []),
        "evidence_bundle_count": len(payload.get("evidence_bundles") or []),
        "nodes": list(payload.get("nodes") or [])[:50],
        "edges": list(payload.get("edges") or [])[:50],
        "artifact_refs": payload.get("artifact_refs", []),
    }


def public_intent_inference_payload(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": payload.get("schema_version"),
        "workspace_id": payload.get("workspace_id"),
        "codebase_id": payload.get("codebase_id"),
        "snapshot_id": payload.get("snapshot_id"),
        "summary": payload.get("summary", {}),
        "intent_candidates": list(payload.get("intent_candidates") or [])[:50],
        "counter_evidence": list(payload.get("counter_evidence") or [])[:50],
        "artifact_refs": payload.get("artifact_refs", []),
    }


def public_diagram_verification_payload(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": payload.get("schema_version"),
        "workspace_id": payload.get("workspace_id"),
        "codebase_id": payload.get("codebase_id"),
        "snapshot_id": payload.get("snapshot_id"),
        "summary": payload.get("summary", {}),
        "alignments": list(payload.get("alignments") or [])[:100],
        "undocumented_code_facts": list(payload.get("undocumented_code_facts") or [])[:100],
        "architecture_diff": payload.get("architecture_diff", {}),
        "artifact_refs": payload.get("artifact_refs", []),
    }


def public_context_pack_v4_payload(payload: dict[str, Any]) -> dict[str, Any]:
    pack = dict(payload.get("context_pack") or {})
    return {
        "schema_version": payload.get("schema_version") or pack.get("schema_version"),
        "workspace_id": payload.get("workspace_id") or pack.get("workspace_id"),
        "codebase_id": payload.get("codebase_id") or pack.get("codebase_id"),
        "snapshot_id": payload.get("snapshot_id") or pack.get("snapshot_id"),
        "context_pack": pack,
        "markdown": payload.get("markdown", ""),
        "artifact_refs": payload.get("artifact_refs", []),
    }


def public_report_payload(payload: dict[str, Any]) -> dict[str, Any]:
    report = dict(payload.get("report") or {})
    return {
        "schema_version": payload.get("schema_version") or report.get("schema_version"),
        "workspace_id": payload.get("workspace_id") or report.get("workspace_id"),
        "codebase_id": payload.get("codebase_id") or report.get("codebase_id"),
        "snapshot_id": payload.get("snapshot_id") or report.get("snapshot_id"),
        "report": report,
        "html": payload.get("html", ""),
        "mermaid": payload.get("mermaid", ""),
        "artifact_refs": payload.get("artifact_refs", []),
    }


def public_governance_payload(payload: dict[str, Any]) -> dict[str, Any]:
    summary = dict(payload.get("summary") or {})
    return {
        "schema_version": payload.get("schema_version") or summary.get("schema_version"),
        "workspace_id": payload.get("workspace_id") or summary.get("workspace_id"),
        "codebase_id": payload.get("codebase_id") or summary.get("codebase_id"),
        "snapshot_id": payload.get("snapshot_id") or summary.get("snapshot_id"),
        "event": payload.get("event"),
        "confirmed_facts": payload.get("confirmed_facts", []),
        "governance_events": payload.get("governance_events", []),
        "summary": summary,
        "artifact_refs": payload.get("artifact_refs", []),
    }


def _all_artifact_refs(*payloads: dict[str, Any]) -> list[dict[str, Any]]:
    refs: list[dict[str, Any]] = []
    seen: set[str] = set()
    for payload in payloads:
        for ref in payload.get("artifact_refs", []):
            key = str(ref.get("artifact_ref") or ref)
            if key in seen:
                continue
            seen.add(key)
            refs.append(ref)
    return refs

"""V2.19 artifact contract registry and validator."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from data_service.mcp_common import now

from ..artifacts import codebase_dir
from ..registry import CodebaseRegistry
from .persistence import (
    contract_artifact_refs,
    read_contract_registry,
    read_validation_report,
    write_contracts,
)


ARTIFACT_CONTRACT_SCHEMA_VERSION = "v2.19"


class ArtifactContractService:
    def __init__(self, workspace: Path, *, workspace_id: str) -> None:
        self.workspace = workspace
        self.workspace_id = workspace_id
        self.registry = CodebaseRegistry(workspace, workspace_id=workspace_id)

    def build_contracts(self, codebase_id: str) -> dict[str, Any]:
        self.registry.describe(codebase_id)
        root = codebase_dir(self.workspace, codebase_id)
        contracts = []
        findings = []
        if not root.exists():
            raise FileNotFoundError("CODEBASE_ARTIFACT_ROOT_NOT_FOUND")
        artifact_paths = sorted(
            path for path in root.rglob("*") if path.is_file() and path.suffix in {".json", ".jsonl"} and not _is_self_contract_output(root, path)
        )
        for path in artifact_paths:
            contract, path_findings = self._validate_path(root, path)
            contracts.append(contract)
            findings.extend(path_findings)
        summary = {
            "checked_count": len(contracts),
            "passed_count": sum(1 for item in contracts if item["status"] == "passed"),
            "warning_count": sum(1 for item in contracts if item["status"] == "warning"),
            "failed_count": sum(1 for item in contracts if item["status"] == "failed"),
            "finding_count": len(findings),
        }
        refs = contract_artifact_refs(codebase_id)
        registry = {
            "schema_version": ARTIFACT_CONTRACT_SCHEMA_VERSION,
            "artifact_type": "artifact_contract_registry",
            "workspace_id": self.workspace_id,
            "codebase_id": codebase_id,
            "generated_at": now(),
            "contracts": contracts,
            "validation_summary": summary,
            "artifact_refs": refs,
        }
        report = {
            "schema_version": ARTIFACT_CONTRACT_SCHEMA_VERSION,
            "artifact_type": "artifact_validation_report",
            "workspace_id": self.workspace_id,
            "codebase_id": codebase_id,
            "generated_at": registry["generated_at"],
            "summary": summary,
            "findings": findings,
            "artifact_refs": refs,
        }
        write_contracts(self.workspace, codebase_id, registry, report)
        return {"registry": registry, "validation_report": report, "artifact_refs": refs}

    def read_contracts(self, codebase_id: str) -> dict[str, Any]:
        self.registry.describe(codebase_id)
        registry = read_contract_registry(self.workspace, codebase_id)
        report = read_validation_report(self.workspace, codebase_id)
        return {"registry": registry, "validation_report": report, "artifact_refs": contract_artifact_refs(codebase_id)}

    def _validate_path(self, root: Path, path: Path) -> tuple[dict[str, Any], list[dict[str, Any]]]:
        rel = path.relative_to(root).as_posix()
        artifact_family = _artifact_family(rel)
        fmt = "jsonl" if path.suffix == ".jsonl" else "json"
        findings: list[dict[str, Any]] = []
        schema_version = None
        row_count = None
        artifact_ref_count = 0
        status = "passed"
        if fmt == "json":
            try:
                payload = json.loads(path.read_text(encoding="utf-8"))
                if not isinstance(payload, dict):
                    findings.append(_finding(rel, "invalid_json_shape", "JSON summary artifact must be an object.", "major"))
                    status = "failed"
                else:
                    schema_version = payload.get("schema_version")
                    artifact_refs = payload.get("artifact_refs") or []
                    artifact_ref_count = len(artifact_refs) if isinstance(artifact_refs, list) else 0
                    if not schema_version:
                        findings.append(_finding(rel, "missing_schema_version", "JSON artifact is missing schema_version.", "major" if rel.startswith("platform/") else "minor"))
                        status = "failed" if rel.startswith("platform/") else "warning"
                    if "artifact_refs" in payload and not isinstance(artifact_refs, list):
                        findings.append(_finding(rel, "invalid_artifact_refs", "artifact_refs must be a list when present.", "major"))
                        status = "failed"
            except (OSError, json.JSONDecodeError) as exc:
                findings.append(_finding(rel, "invalid_json", str(exc), "major"))
                status = "failed"
        else:
            row_count = 0
            try:
                with path.open("r", encoding="utf-8") as handle:
                    for line_number, line in enumerate(handle, start=1):
                        if not line.strip():
                            continue
                        row_count += 1
                        try:
                            row = json.loads(line)
                        except json.JSONDecodeError as exc:
                            findings.append(_finding(rel, "invalid_jsonl_row", f"line {line_number}: {exc}", "major"))
                            status = "failed"
                            continue
                        if not isinstance(row, dict):
                            findings.append(_finding(rel, "invalid_jsonl_shape", f"line {line_number}: row must be an object.", "major"))
                            status = "failed"
            except OSError as exc:
                findings.append(_finding(rel, "unreadable_artifact", str(exc), "major"))
                status = "failed"
            if row_count == 0:
                findings.append(_finding(rel, "empty_jsonl", "JSONL artifact has no rows.", "minor"))
                if status == "passed":
                    status = "warning"
        return {
            "artifact_family": artifact_family,
            "artifact_path": rel,
            "format": fmt,
            "row_artifact": fmt == "jsonl",
            "summary_artifact": fmt == "json",
            "schema_version": schema_version,
            "schema_version_present": bool(schema_version) if fmt == "json" else None,
            "row_count": row_count,
            "artifact_ref_count": artifact_ref_count,
            "status": status,
            "validator": "v2_19_artifact_contract_validator",
        }, findings


def public_contract_payload(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": ARTIFACT_CONTRACT_SCHEMA_VERSION,
        "artifact_type": "artifact_contract_bundle",
        "registry": payload.get("registry", {}),
        "validation_report": payload.get("validation_report", {}),
        "artifact_refs": payload.get("artifact_refs", []),
    }


def _artifact_family(rel: str) -> str:
    name = rel.rsplit("/", 1)[-1]
    base = name.rsplit(".", 1)[0]
    return base.replace("-", "_")


def _is_self_contract_output(root: Path, path: Path) -> bool:
    rel = path.relative_to(root).as_posix()
    return rel in {
        "platform/contracts/artifact_contract_registry.json",
        "platform/contracts/validation_report.json",
    }


def _finding(path: str, code: str, message: str, severity: str) -> dict[str, Any]:
    return {"artifact_path": path, "code": code, "message": message, "severity": severity}

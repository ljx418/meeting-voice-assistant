from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
V9_ROOT = ROOT / "docs" / "design" / "V9.x"

DURABLE_OPERATIONS = {
    "workflow.instance.start",
    "station.rerun",
    "artifact.write",
    "quality.evaluation.create",
}

FORBIDDEN_RAW_TERMS = (
    "raw_prompt",
    "raw prompt",
    "raw_file_content",
    "raw file content",
    "raw_provider_payload",
    "raw_connector_payload",
    "raw_artifact_content",
    "raw_secret",
    "api_key",
    "API key",
    "Bearer",
    "bearer_token",
    "signed URL",
    "signed_url",
    "credential raw secret",
    "credential_raw_secret",
)

FORBIDDEN_CLAIM_PATTERN = re.compile(
    r"production[- ]?ready|full production GA|GA ready|Agent executor ready|controlled executor ready|"
    r"production controlled executor ready|full multi-Agent orchestration ready|distributed multi-Agent runtime ready|"
    r"autonomous coding workflow ready|autonomous workflow editing ready|complete Workflow Studio ready|"
    r"unrestricted terminal worker ready|production terminal automation ready|production browser automation ready|"
    r"production automation ready|生产可用|全面生产可用|生产就绪|可投产|正式发布|生产级可用|"
    r"Agent执行器已完成|Agent Executor 已完成|受控执行器已完成|生产级受控执行器已完成|"
    r"完整多Agent编排已完成|多智能体编排已完成|自主代码工作流已完成|自主工作流编辑已完成|"
    r"完整工作流工作台已完成|无限制终端worker已完成|生产终端自动化已完成|生产浏览器自动化已完成|"
    r"生产自动化已完成",
    re.IGNORECASE,
)

ALLOWED_CLAIM_CONTEXT_MARKERS = (
    "Forbidden Claims",
    "No False Green",
    "Stop Conditions",
    "Stop Condition",
    "Out Of Scope",
    "Audit Questions",
    "Global Acceptance Requirements",
    "Validation Commands",
    "Claim Scan Result",
    "is claimed",
    "Readiness Evidence",
    "P0 Risks To Check",
    "Exit Architecture",
    "Success Criteria",
    "Suggested Scan",
    "Redaction Terms",
    "Global Schema Rules",
    "Forbidden persistence",
    "Rejection Cases",
    "Required Negative Fixtures",
    "Drawio warning boxes",
    "Boundary explanations",
    "Boundary",
    "Baseline",
    "Acceptance Oracle",
    "Final Allowed Claim",
    "Naming And Boundary",
    "Product Goal",
    "Forbidden",
    "Non-Claims",
    "Non-Negotiable",
    "禁止",
    "不得",
    "不能",
    "不允许",
    "不证明",
    "not ",
    "does not prove",
    "blocked",
    "NO-GO",
    "No ",
    "without",
)


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def contains_forbidden_raw_content(value: Any) -> list[str]:
    text = json.dumps(value, ensure_ascii=False) if not isinstance(value, str) else value
    lowered = text.lower()
    return [term for term in FORBIDDEN_RAW_TERMS if term.lower() in lowered]


def has_valid_human_authorization_ref(ref: Any) -> bool:
    return isinstance(ref, str) and bool(ref.strip())


def envelope_has_mutation_authorization(envelope: dict[str, Any]) -> bool:
    if envelope.get("operation") not in DURABLE_OPERATIONS:
        return True
    return envelope.get("user_confirmed") is True or has_valid_human_authorization_ref(envelope.get("human_authorization_ref"))


def envelope_source_agent_denied(envelope: dict[str, Any]) -> bool:
    return envelope.get("source") == "agent" and envelope.get("operation") in DURABLE_OPERATIONS

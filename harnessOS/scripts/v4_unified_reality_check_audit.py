"""Generate the V4 unified experience reality-check audit dashboard.

This script is intentionally audit-only. It reads existing evidence, runs
non-mutating validations, and writes an audit package. It does not create or
repair workflow runtime evidence.
"""

from __future__ import annotations

import html
import json
import re
import subprocess
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = REPO_ROOT / "docs/design/V4.x/evidence/unified-experience/reality-check"
SCREENSHOTS_DIR = OUTPUT_DIR / "screenshots"
LOGS_DIR = OUTPUT_DIR / "logs"
RAW_DIR = OUTPUT_DIR / "raw"

EVIDENCE_ROOTS = [
    REPO_ROOT / "docs/design/V4.x/evidence",
    REPO_ROOT / "docs/design/V4.2/evidence",
    REPO_ROOT / "docs/design/V4.3/evidence",
    REPO_ROOT / "docs/design/V4.4/evidence",
    REPO_ROOT / "docs/design/V4.5/evidence",
    REPO_ROOT / "docs/design/V4.6/evidence",
]

CLAIM_SCAN_ROOTS = [
    REPO_ROOT / "docs/design",
    REPO_ROOT / "apps",
    REPO_ROOT / "core",
    REPO_ROOT / "tests",
    REPO_ROOT / "scripts",
]

FORBIDDEN_CLAIMS = [
    "complete Workflow Studio ready",
    "complete AgentTalkWindow ready",
    "Agent executor ready",
    "controlled executor ready",
    "production-ready external app support",
    "full multi-Agent orchestration ready",
    "autonomous workflow editing ready",
    "autonomous coding workflow ready",
    "production controlled executor ready",
]

SENSITIVE_TERMS = [
    "capability_token",
    "subscription_token",
    "Authorization",
    "Bearer",
    "secret",
    "raw_trace_payload",
    "raw_artifact_content",
    "raw_connector_payload",
    "raw prompt",
    "upstream signed URL",
]

EXECUTION_BUTTON_TERMS = ["Apply", "Publish", "Approve", "Reject", "Execute", "Run"]

GUARD_CONTEXT_MARKERS = [
    "forbidden",
    "Forbidden",
    "禁止",
    "不能声明",
    "不得声明",
    "does not prove",
    "does not claim",
    "not claim",
    "Do not claim",
    "No False Green",
    "still forbidden",
    "仍禁止",
    "不代表",
    "不声明",
    "不是",
    "Non-Goals",
    "Non-goals",
    "不实现",
    "不做",
    "不等于",
    "非目标",
    "Boundary",
    "Safety",
    "FORBIDDEN",
    "虚假验收",
    "过度声明",
]


@dataclass
class UxAudit:
    ux_id: str
    title: str
    status: str
    evidence_scope: str
    runtime_backed: bool
    deterministic_only: bool
    transcript_only: bool
    report_only: bool
    false_green_risk: str
    claim_risk: str
    evidence_refs: list[str] = field(default_factory=list)
    commands_run: list[dict[str, Any]] = field(default_factory=list)
    missing_evidence: list[str] = field(default_factory=list)
    notes: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "ux_id": self.ux_id,
            "title": self.title,
            "status": self.status,
            "evidence_scope": self.evidence_scope,
            "runtime_backed": self.runtime_backed,
            "deterministic_only": self.deterministic_only,
            "transcript_only": self.transcript_only,
            "report_only": self.report_only,
            "false_green_risk": self.false_green_risk,
            "claim_risk": self.claim_risk,
            "evidence_refs": self.evidence_refs,
            "commands_run": self.commands_run,
            "missing_evidence": self.missing_evidence,
            "notes": self.notes,
        }


def main() -> None:
    for directory in [OUTPUT_DIR, SCREENSHOTS_DIR, LOGS_DIR, RAW_DIR]:
        directory.mkdir(parents=True, exist_ok=True)

    inventory = build_evidence_inventory()
    command_results = run_validation_commands()
    claims_audit = build_claims_audit()
    redaction_audit = scan_sensitive_terms()
    global_assertions = build_global_assertions(inventory, claims_audit, redaction_audit)
    ux_cases = build_ux_cases(inventory, command_results, redaction_audit)

    audit_data = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "baseline": "V4.6 complete: governed Agent workflow builder UX ready for dev/local validation.",
        "forbidden_claims": FORBIDDEN_CLAIMS,
        "ux_cases": [case.to_dict() for case in ux_cases],
        "global_assertions": global_assertions,
        "claims_audit": claims_audit,
        "redaction_audit": redaction_audit,
        "command_results": command_results,
        "recommendation": build_recommendation(ux_cases, claims_audit, global_assertions),
    }

    write_json(OUTPUT_DIR / "audit-data.json", audit_data)
    write_json(OUTPUT_DIR / "evidence-inventory.json", inventory)
    (OUTPUT_DIR / "claims-audit.md").write_text(render_claims_audit(claims_audit), encoding="utf-8")
    (OUTPUT_DIR / "result-summary.md").write_text(render_result_summary(audit_data), encoding="utf-8")
    (OUTPUT_DIR / "index.html").write_text(render_dashboard(audit_data), encoding="utf-8")


def repo_rel(path: Path) -> str:
    try:
        return str(path.relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def write_json(path: Path, data: Any) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return ""


def read_json(path: Path) -> Any | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def exists(rel_path: str) -> bool:
    return (REPO_ROOT / rel_path).exists()


def build_evidence_inventory() -> dict[str, Any]:
    files: list[dict[str, Any]] = []
    for root in EVIDENCE_ROOTS:
        if not root.exists():
            continue
        for path in sorted(root.rglob("*")):
            if path.is_file():
                files.append(
                    {
                        "path": repo_rel(path),
                        "suffix": path.suffix,
                        "size_bytes": path.stat().st_size,
                    }
                )
    return {
        "roots": [repo_rel(path) for path in EVIDENCE_ROOTS],
        "file_count": len(files),
        "files": files,
    }


def run_validation_commands() -> dict[str, Any]:
    results: dict[str, Any] = {"drawio": [], "pytest_v4": None}
    drawio_files = sorted(
        path
        for root in EVIDENCE_ROOTS
        if root.exists()
        for path in root.rglob("*.drawio")
    )
    drawio_log_lines: list[str] = []
    for path in drawio_files:
        result = run_command(["xmllint", "--noout", repo_rel(path)], timeout=30)
        entry = {"file": repo_rel(path), **result}
        results["drawio"].append(entry)
        drawio_log_lines.append(f"{entry['file']}: exit={entry['returncode']}")
        if entry["stdout"]:
            drawio_log_lines.append(entry["stdout"])
        if entry["stderr"]:
            drawio_log_lines.append(entry["stderr"])
    (LOGS_DIR / "xmllint.log").write_text("\n".join(drawio_log_lines), encoding="utf-8")

    v4_tests = sorted(repo_rel(path) for path in (REPO_ROOT / "tests").glob("test_v4_*.py"))
    pytest_result = run_command(["./.venv/bin/python", "-m", "pytest", *v4_tests, "-q"], timeout=180)
    results["pytest_v4"] = pytest_result
    (LOGS_DIR / "pytest-v4.log").write_text(
        f"command: {pytest_result['command']}\nexit: {pytest_result['returncode']}\n\nSTDOUT\n{pytest_result['stdout']}\n\nSTDERR\n{pytest_result['stderr']}",
        encoding="utf-8",
    )
    write_json(LOGS_DIR / "commands.json", results)
    return results


def run_command(command: list[str], timeout: int) -> dict[str, Any]:
    try:
        completed = subprocess.run(
            command,
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
        return {
            "command": " ".join(command),
            "returncode": completed.returncode,
            "stdout": completed.stdout[-8000:],
            "stderr": completed.stderr[-8000:],
        }
    except Exception as exc:  # pragma: no cover - defensive audit logging
        return {
            "command": " ".join(command),
            "returncode": -1,
            "stdout": "",
            "stderr": repr(exc),
        }


def build_claims_audit() -> dict[str, Any]:
    guarded: list[dict[str, Any]] = []
    historical: list[dict[str, Any]] = []
    violations: list[dict[str, Any]] = []
    for root in CLAIM_SCAN_ROOTS:
        if not root.exists():
            continue
        for path in sorted(root.rglob("*")):
            if not path.is_file() or path.suffix in {".png", ".jpg", ".jpeg", ".pyc", ".drawio"}:
                continue
            if is_under(path, OUTPUT_DIR):
                continue
            text = read_text(path)
            if not text:
                continue
            lines = text.splitlines()
            for line_number, line in enumerate(lines, start=1):
                for claim in FORBIDDEN_CLAIMS:
                    if claim in line:
                        context = "\n".join(lines[max(0, line_number - 20) : min(len(lines), line_number + 6)])
                        item = {
                            "claim": claim,
                            "path": repo_rel(path),
                            "line": line_number,
                            "context": context.strip(),
                        }
                        if is_historical_design_path(path):
                            historical.append(item)
                        elif any(marker in context for marker in GUARD_CONTEXT_MARKERS):
                            guarded.append(item)
                        else:
                            violations.append(item)
    return {
        "violations": violations,
        "guarded_mentions": guarded,
        "historical_mentions": historical,
        "violation_count": len(violations),
        "guarded_count": len(guarded),
        "historical_count": len(historical),
    }


def is_historical_design_path(path: Path) -> bool:
    rel = repo_rel(path)
    return (
        rel.startswith("docs/design/V3.")
        or rel.startswith("docs/design/V4.0/")
        or rel.startswith("docs/design/V4.1/")
        or rel.startswith("docs/design/V4.2/")
        or rel.startswith("docs/design/V4.3/")
        or rel.startswith("docs/design/V4.4/")
        or rel.startswith("docs/design/V4.5/")
        or rel.startswith("docs/design/V4.6/")
        or rel.startswith("tests/test_v3_")
        or rel.startswith("tests/test_v4_0_")
    )


def scan_sensitive_terms() -> dict[str, Any]:
    occurrences: list[dict[str, Any]] = []
    scanned_roots = EVIDENCE_ROOTS
    for root in scanned_roots:
        if not root.exists():
            continue
        for path in sorted(root.rglob("*")):
            if not path.is_file() or path.suffix in {".png", ".jpg", ".jpeg", ".pyc"}:
                continue
            if is_under(path, OUTPUT_DIR):
                continue
            text = read_text(path)
            for term in SENSITIVE_TERMS:
                if term in text:
                    occurrences.append({"term": term, "path": repo_rel(path)})
    return {
        "sensitive_terms": SENSITIVE_TERMS,
        "occurrences": occurrences,
        "status": "PASS" if not occurrences else "FAIL",
    }


def build_global_assertions(
    inventory: dict[str, Any],
    claims_audit: dict[str, Any],
    redaction_audit: dict[str, Any],
) -> list[dict[str, str]]:
    evidence_text = combined_evidence_text()
    return [
        assertion("source=agent cannot execute mutation", "PASS" if "source=agent" in evidence_text and "不能" in evidence_text else "FAIL"),
        assertion("durable mutation requires user_confirmed=true", "PASS" if "user_confirmed=true" in evidence_text else "FAIL"),
        assertion("EventBridge only triggers refresh", "PASS" if "EventBridge" in evidence_text and "refresh" in evidence_text else "FAIL"),
        assertion("WorkflowSpec cannot mutate runtime truth", "PASS" if "WorkflowSpec" in evidence_text and "runtime truth" in evidence_text else "FAIL"),
        assertion("Drawio is visualization only", "PASS" if "Drawio" in evidence_text and ("visualization" in evidence_text or "可视化" in evidence_text) else "FAIL"),
        assertion("HTML Report is read-only", "PASS" if "HTML Report" in evidence_text and ("read-only" in evidence_text or "只读" in evidence_text) else "FAIL"),
        assertion("Browser does not call /v1/rpc", browser_network_assertion("/v1/rpc")),
        assertion("Browser does not call /v1/events/subscribe", browser_network_assertion("/v1/events/subscribe")),
        assertion("No token/raw payload leakage", redaction_audit["status"]),
        assertion("No false-green claims", "PASS" if claims_audit["violation_count"] == 0 else "FAIL"),
        assertion("Reality-check audit package generated", "PASS"),
    ]


def assertion(name: str, status: str) -> dict[str, str]:
    return {"name": name, "status": status}


def browser_network_assertion(forbidden_path: str) -> str:
    network_logs = [
        REPO_ROOT / "docs/design/V4.1/acceptance-evidence/desktop-folder-summary/network-log.json",
        OUTPUT_DIR / "raw/network-log.json",
    ]
    existing = [path for path in network_logs if path.exists()]
    if not existing:
        return "BLOCKED"
    for path in existing:
        if forbidden_path in read_text(path):
            return "FAIL"
    return "PASS"


def combined_evidence_text() -> str:
    chunks: list[str] = []
    for root in EVIDENCE_ROOTS + [REPO_ROOT / "docs/design/V4.x"]:
        if not root.exists():
            continue
        for path in root.rglob("*"):
            if path.is_file() and path.suffix in {".md", ".txt", ".json", ".html"}:
                if is_under(path, OUTPUT_DIR):
                    continue
                chunks.append(read_text(path))
    return "\n".join(chunks)


def build_ux_cases(
    inventory: dict[str, Any],
    command_results: dict[str, Any],
    redaction_audit: dict[str, Any],
) -> list[UxAudit]:
    files = {item["path"] for item in inventory["files"]}
    drawio_results = {item["file"]: item for item in command_results["drawio"]}

    return [
        audit_ux01(files),
        audit_ux02(files, drawio_results, redaction_audit),
        audit_ux03(files, redaction_audit),
        audit_ux04(files, drawio_results, redaction_audit),
        audit_ux05(files),
        audit_ux06(files),
        audit_ux07(files),
        audit_ux08(files, drawio_results),
        audit_ux09(files, drawio_results),
        audit_ux10(files, drawio_results),
        audit_ux11(files),
        audit_ux12(files),
    ]


def audit_ux01(files: set[str]) -> UxAudit:
    refs = [
        "docs/design/V4.x/evidence/unified-experience/mission_console_transcript.txt",
        "docs/design/V4.2/evidence/headless-interaction/workflow.yaml",
        "docs/design/V4.2/evidence/headless-interaction/workflow.json",
        "docs/design/V4.2/evidence/headless-interaction/workflow.schema.json",
        "docs/design/V4.2/evidence/headless-interaction/result-summary.md",
    ]
    transcript = read_text(REPO_ROOT / refs[0])
    spec_json = read_json(REPO_ROOT / refs[2])
    required_states = ["IntentCaptured", "SpecDrafted", "SchemaValidated", "DiffReady"]
    missing = missing_refs(refs, files)
    missing += [f"state:{state}" for state in required_states if state not in transcript]
    if not spec_json:
        missing.append("valid workflow.json")
    if "user_confirmed=true" not in transcript:
        missing.append("user confirmation evidence")
    status = "PASS" if not missing else "PARTIAL"
    return UxAudit(
        ux_id="UX-01",
        title="自然语言创建工作流",
        status=status,
        evidence_scope="transcript_only",
        runtime_backed=False,
        deterministic_only=False,
        transcript_only=True,
        report_only=False,
        false_green_risk="MEDIUM",
        claim_risk="MEDIUM",
        evidence_refs=existing_refs(refs),
        missing_evidence=missing,
        notes="WorkflowSpec evidence exists, but this path is transcript/spec backed and must not be treated as real runtime mutation.",
    )


def audit_ux02(files: set[str], drawio_results: dict[str, Any], redaction_audit: dict[str, Any]) -> UxAudit:
    refs = [
        "docs/design/V4.2/evidence/headless-interaction/workflow.drawio",
        "docs/design/V4.2/evidence/headless-interaction/workflow_status.drawio",
        "docs/design/V4.2/evidence/headless-interaction/artifact_lineage.drawio",
    ]
    missing = missing_refs(refs, files)
    invalid = [ref for ref in refs if drawio_results.get(ref, {}).get("returncode") not in {0, None}]
    missing += [f"xml valid:{ref}" for ref in invalid]
    workflow_text = read_text(REPO_ROOT / refs[0])
    lineage_text = read_text(REPO_ROOT / refs[2])
    if "folder_scan" not in workflow_text or "artifact_publish" not in workflow_text:
        missing.append("station coverage in workflow.drawio")
    if "Artifact" not in lineage_text and "artifact" not in lineage_text:
        missing.append("artifact lineage in drawio")
    status = "PASS" if not missing and redaction_audit["status"] == "PASS" else "PARTIAL"
    return UxAudit(
        ux_id="UX-02",
        title="Workflow Blueprint 可视化",
        status=status,
        evidence_scope="report_only",
        runtime_backed=False,
        deterministic_only=True,
        transcript_only=False,
        report_only=True,
        false_green_risk="LOW",
        claim_risk="LOW",
        evidence_refs=existing_refs(refs),
        commands_run=[drawio_results.get(ref, {"file": ref, "returncode": None}) for ref in refs],
        missing_evidence=missing,
        notes="Drawio files are visualization only and are not runtime truth.",
    )


def audit_ux03(files: set[str], redaction_audit: dict[str, Any]) -> UxAudit:
    refs = [
        "docs/design/V4.2/evidence/headless-interaction/workflow_board.html",
        "docs/design/V4.2/evidence/headless-interaction/exported-runtime-result.json",
    ]
    missing = missing_refs(refs, files)
    runtime = read_json(REPO_ROOT / refs[1]) or {}
    board_html = read_text(REPO_ROOT / refs[0])
    if not runtime.get("nodes"):
        missing.append("runtime DTO station nodes")
    if "<form" in board_html.lower() or "type=\"hidden\"" in board_html.lower():
        missing.append("HTML report has no hidden mutation form")
    status = "PASS" if not missing and redaction_audit["status"] == "PASS" else "PARTIAL"
    return UxAudit(
        ux_id="UX-03",
        title="Runtime Report 运行观察",
        status=status,
        evidence_scope="deterministic_devlocal",
        runtime_backed=True,
        deterministic_only=True,
        transcript_only=False,
        report_only=False,
        false_green_risk="MEDIUM",
        claim_risk="MEDIUM",
        evidence_refs=existing_refs(refs),
        missing_evidence=missing,
        notes=f"Runtime DTO source={runtime.get('source') or runtime.get('backed_by')}; this is dev/local evidence, not production runtime.",
    )


def audit_ux04(files: set[str], drawio_results: dict[str, Any], redaction_audit: dict[str, Any]) -> UxAudit:
    refs = [
        "docs/design/V4.2/evidence/headless-interaction/artifacts.html",
        "docs/design/V4.2/evidence/headless-interaction/exported-runtime-result.json",
        "docs/design/V4.2/evidence/headless-interaction/artifact_lineage.drawio",
    ]
    missing = missing_refs(refs, files)
    if "docs/design/V4.2/evidence/headless-interaction/artifacts.json" not in files:
        missing.append("artifacts.json")
    runtime = read_json(REPO_ROOT / refs[1]) or {}
    artifacts = runtime.get("artifacts", [])
    if not artifacts:
        missing.append("artifact list")
    if any("producer_station_id" not in item and "lineage_refs" not in item for item in artifacts):
        missing.append("producer_station_id or lineage_refs for every artifact")
    if drawio_results.get(refs[2], {}).get("returncode") not in {0, None}:
        missing.append("artifact_lineage.drawio XML valid")
    return UxAudit(
        ux_id="UX-04",
        title="Artifact 查看与血缘",
        status="PARTIAL" if missing else "PASS",
        evidence_scope="deterministic_devlocal",
        runtime_backed=True,
        deterministic_only=True,
        transcript_only=False,
        report_only=False,
        false_green_risk="MEDIUM",
        claim_risk="MEDIUM",
        evidence_refs=existing_refs(refs),
        commands_run=[drawio_results.get(refs[2], {"file": refs[2], "returncode": None})],
        missing_evidence=missing,
        notes="Artifact list is visible, but strict artifact JSON and producer/lineage refs are required for full PASS.",
    )


def audit_ux05(files: set[str]) -> UxAudit:
    refs = [
        "docs/design/V4.2/evidence/headless-interaction/quality.html",
        "docs/design/V4.2/evidence/headless-interaction/exported-runtime-result.json",
    ]
    missing = missing_refs(refs, files)
    if "docs/design/V4.2/evidence/headless-interaction/quality.json" not in files:
        missing.append("quality.json")
    text = read_text(REPO_ROOT / refs[0])
    if not any(term in text for term in ["passed", "warning", "failed", "通过", "警告", "失败"]):
        missing.append("quality status in report")
    return UxAudit(
        ux_id="UX-05",
        title="Quality 查看",
        status="PARTIAL" if missing else "PASS",
        evidence_scope="deterministic_devlocal",
        runtime_backed=True,
        deterministic_only=True,
        transcript_only=False,
        report_only=False,
        false_green_risk="MEDIUM",
        claim_risk="MEDIUM",
        evidence_refs=existing_refs(refs),
        missing_evidence=missing,
        notes="Quality HTML exists, but full PASS requires machine-readable quality.json linked to station or artifact.",
    )


def audit_ux06(files: set[str]) -> UxAudit:
    refs = [
        "docs/design/V4.2/evidence/controlled-runtime/attempt-history.json",
        "docs/design/V4.2/evidence/controlled-runtime/downstream-stale.json",
        "docs/design/V4.2/evidence/controlled-runtime/station-rerun-result.json",
        "docs/design/V4.2/evidence/controlled-runtime/tui-transcript.txt",
        "docs/design/V4.2/evidence/controlled-runtime/runtime-evidence.json",
    ]
    missing = missing_refs(refs, files)
    attempt = read_json(REPO_ROOT / refs[0]) or {}
    rerun = read_json(REPO_ROOT / refs[2]) or {}
    transcript = read_text(REPO_ROOT / refs[3])
    if "failed" not in json.dumps(attempt, ensure_ascii=False):
        missing.append("failed station evidence")
    if "user_confirmed=true" not in transcript and rerun.get("user_confirmed") is not True:
        missing.append("rerun user_confirmed=true")
    if "source=agent" in transcript and "blocked" not in transcript:
        missing.append("source=agent rerun blocked evidence")
    if "attempt" not in json.dumps(attempt, ensure_ascii=False):
        missing.append("attempt history")
    if not rerun:
        missing.append("new attempt result")
    return UxAudit(
        ux_id="UX-06",
        title="局部失败修复与重跑",
        status="PASS" if not missing else "PARTIAL",
        evidence_scope="deterministic_devlocal",
        runtime_backed=True,
        deterministic_only=True,
        transcript_only=False,
        report_only=False,
        false_green_risk="MEDIUM",
        claim_risk="MEDIUM",
        evidence_refs=existing_refs(refs),
        missing_evidence=missing,
        notes="Rerun evidence is dev/local controlled runtime evidence and must not be overclaimed as controlled executor readiness.",
    )


def audit_ux07(files: set[str]) -> UxAudit:
    refs = [
        "docs/design/V4.2/evidence/headless-interaction/evidence.html",
        "docs/design/V4.2/evidence/headless-interaction/operation-evidence.json",
    ]
    missing = missing_refs(refs, files)
    evidence = read_json(REPO_ROOT / refs[1]) or []
    evidence_text = json.dumps(evidence, ensure_ascii=False)
    for field in [
        "proposal_id",
        "handoff_id",
        "user_confirmed",
        "operation",
        "runtime_result_ref",
        "policy_decision",
        "correlation_id",
        "redaction_status",
    ]:
        if field not in evidence_text:
            missing.append(field)
    html_text = read_text(REPO_ROOT / refs[0])
    buttons = execution_terms_in_html(html_text)
    missing += [f"forbidden evidence action button:{term}" for term in buttons]
    return UxAudit(
        ux_id="UX-07",
        title="Evidence Chain 审查",
        status="PASS" if not missing else "PARTIAL",
        evidence_scope="deterministic_devlocal",
        runtime_backed=True,
        deterministic_only=True,
        transcript_only=False,
        report_only=False,
        false_green_risk="MEDIUM",
        claim_risk="MEDIUM",
        evidence_refs=existing_refs(refs),
        missing_evidence=missing,
        notes="Evidence Chain must remain read-only; detected execution terms are treated as missing/risks.",
    )


def audit_ux08(files: set[str], drawio_results: dict[str, Any]) -> UxAudit:
    u7 = audit_u7_provider_scenario(
        ux_id="UX-08",
        title="串行多 Agent 视频工作流",
        directory="UX-08-serial-video",
        minimum_stations=6,
        required_terms=["writer_agent", "storyboard_agent", "station.rerun"],
        note="U7 evidence shows dev/local provider-backed serial station execution with rerun and downstream stale records. This still does not prove production or unrestricted orchestration.",
    )
    if u7:
        return u7
    refs = [
        "docs/design/V4.3/evidence/serial-video-workflow/video_workflow.yaml",
        "docs/design/V4.3/evidence/serial-video-workflow/video_workflow.drawio",
        "docs/design/V4.3/evidence/serial-video-workflow/video_artifacts.html",
        "docs/design/V4.3/evidence/serial-video-workflow/attempt-history.json",
        "docs/design/V4.3/evidence/serial-video-workflow/downstream-stale.json",
        "docs/design/V4.3/evidence/serial-video-workflow/runtime-result.json",
    ]
    missing = missing_refs(refs, files)
    runtime = read_json(REPO_ROOT / refs[5]) or {}
    nodes = runtime.get("nodes", [])
    artifacts = runtime.get("artifacts", [])
    if len(nodes) < 6:
        missing.append("six video stations")
    if len(artifacts) < 6:
        missing.append("artifact per video station")
    if "failed" not in json.dumps(runtime, ensure_ascii=False):
        missing.append("middle station failure before rerun")
    if drawio_results.get(refs[1], {}).get("returncode") not in {0, None}:
        missing.append("video_workflow.drawio XML valid")
    return UxAudit(
        ux_id="UX-08",
        title="串行多 Agent 视频工作流",
        status="PARTIAL",
        evidence_scope="deterministic_devlocal",
        runtime_backed=True,
        deterministic_only=True,
        transcript_only=False,
        report_only=False,
        false_green_risk="HIGH",
        claim_risk="HIGH",
        evidence_refs=existing_refs(refs),
        commands_run=[drawio_results.get(refs[1], {"file": refs[1], "returncode": None})],
        missing_evidence=missing,
        notes="This is deterministic dev/local serial scenario evidence and does not prove full multi-Agent orchestration.",
    )


def audit_ux09(files: set[str], drawio_results: dict[str, Any]) -> UxAudit:
    u7 = audit_u7_provider_scenario(
        ux_id="UX-09",
        title="并行罗马广场讨论",
        directory="UX-09-parallel-deliberation",
        minimum_stations=6,
        required_terms=["product_persona", "architecture_persona", "synthesis_node", "cross_inspiration_edges"],
        note="U7 evidence shows dev/local provider-backed persona outputs, synthesis, attribution inputs, and contradiction review. This is not production parallel orchestration.",
    )
    if u7:
        return u7
    refs = [
        "docs/design/V4.4/evidence/parallel-deliberation/deliberation_workflow.yaml",
        "docs/design/V4.4/evidence/parallel-deliberation/deliberation_workflow.drawio",
        "docs/design/V4.4/evidence/parallel-deliberation/persona_artifacts.html",
        "docs/design/V4.4/evidence/parallel-deliberation/synthesis.html",
        "docs/design/V4.4/evidence/parallel-deliberation/runtime-result.json",
    ]
    missing = missing_refs(refs, files)
    runtime = read_json(REPO_ROOT / refs[4]) or {}
    text = (
        json.dumps(runtime, ensure_ascii=False)
        + read_text(REPO_ROOT / refs[0])
        + read_text(REPO_ROOT / refs[1])
        + read_text(REPO_ROOT / refs[3])
    )
    required_terms = {
        "persona": ("persona",),
        "Attribution": ("Attribution", "attribution"),
        "cross": ("cross", "inspiration", "cross-inspiration"),
        "contradiction": ("contradiction", "contradictions"),
    }
    for label, candidates in required_terms.items():
        if not any(term.lower() in text.lower() for term in candidates):
            missing.append(label)
    if drawio_results.get(refs[1], {}).get("returncode") not in {0, None}:
        missing.append("deliberation_workflow.drawio XML valid")
    return UxAudit(
        ux_id="UX-09",
        title="并行罗马广场讨论",
        status="PARTIAL",
        evidence_scope="deterministic_devlocal",
        runtime_backed=True,
        deterministic_only=True,
        transcript_only=False,
        report_only=False,
        false_green_risk="HIGH",
        claim_risk="HIGH",
        evidence_refs=existing_refs(refs),
        commands_run=[drawio_results.get(refs[1], {"file": refs[1], "returncode": None})],
        missing_evidence=missing,
        notes="This is deterministic dev/local deliberation evidence and must not be overclaimed as real parallel multi-Agent runtime.",
    )


def audit_ux10(files: set[str], drawio_results: dict[str, Any]) -> UxAudit:
    u7 = audit_u7_provider_scenario(
        ux_id="UX-10",
        title="长时工程任务工作流",
        directory="UX-10-engineering-workflow",
        minimum_stations=11,
        required_terms=["human_confirmation", "code_review", "station.rerun"],
        note="U7 evidence shows dev/local provider-backed engineering stage execution with code review rerun and stale records. This is not autonomous coding or Agent executor readiness.",
    )
    if u7:
        return u7
    refs = [
        "docs/design/V4.5/evidence/engineering-workflow/engineering_workflow.yaml",
        "docs/design/V4.5/evidence/engineering-workflow/durable_task_board.html",
        "docs/design/V4.5/evidence/engineering-workflow/stage_artifacts.html",
        "docs/design/V4.5/evidence/engineering-workflow/quality_gate_report.html",
        "docs/design/V4.5/evidence/engineering-workflow/runtime-result.json",
        "docs/design/V4.5/evidence/engineering-workflow/attempt-history.json",
        "docs/design/V4.5/evidence/engineering-workflow/downstream-stale.json",
        "docs/design/V4.5/evidence/engineering-workflow/engineering_board.drawio",
    ]
    missing = missing_refs(refs, files)
    runtime = read_json(REPO_ROOT / refs[4]) or {}
    text = json.dumps(runtime, ensure_ascii=False)
    required_terms = {
        "human": ("human", "human_confirmation"),
        "manual": ("manual", "human_confirmation", "人工确认"),
        "quality": ("quality", "quality_report"),
        "attempt": ("attempt", "attempts"),
    }
    for label, candidates in required_terms.items():
        if not any(term.lower() in text.lower() for term in candidates):
            missing.append(label)
    if drawio_results.get(refs[7], {}).get("returncode") not in {0, None}:
        missing.append("engineering_board.drawio XML valid")
    return UxAudit(
        ux_id="UX-10",
        title="长时工程任务工作流",
        status="PARTIAL",
        evidence_scope="deterministic_devlocal",
        runtime_backed=True,
        deterministic_only=True,
        transcript_only=False,
        report_only=False,
        false_green_risk="HIGH",
        claim_risk="HIGH",
        evidence_refs=existing_refs(refs),
        commands_run=[drawio_results.get(refs[7], {"file": refs[7], "returncode": None})],
        missing_evidence=missing,
        notes="This evidence is deterministic dev/local and does not prove autonomous coding workflow or Agent executor readiness.",
    )


def audit_u7_provider_scenario(
    *,
    ux_id: str,
    title: str,
    directory: str,
    minimum_stations: int,
    required_terms: list[str],
    note: str,
) -> UxAudit | None:
    base = f"docs/design/V4.x/evidence/real-multi-agent/{directory}"
    refs = [
        f"{base}/runtime-result.json",
        f"{base}/operation-evidence.json",
        f"{base}/attempt-history.json",
        f"{base}/downstream-stale.json",
        f"{base}/runtime-report.html",
        f"{base}/artifacts.html",
        f"{base}/quality.html",
        f"{base}/evidence.html",
        f"{base}/workflow.drawio",
        f"{base}/workflow_status.drawio",
        f"{base}/artifact_lineage.drawio",
        f"{base}/result-summary.md",
    ]
    if not (REPO_ROOT / refs[0]).exists():
        return None
    runtime = read_json(REPO_ROOT / refs[0]) or {}
    operation_evidence = read_json(REPO_ROOT / refs[1]) or []
    attempts = read_json(REPO_ROOT / refs[2]) or {}
    stale = read_json(REPO_ROOT / refs[3]) or []
    combined = json.dumps(runtime, ensure_ascii=False) + json.dumps(operation_evidence, ensure_ascii=False)
    missing = missing_refs(refs, set())
    if runtime.get("status") != "completed":
        missing.append("completed provider-backed runtime result")
    if runtime.get("real_provider_backed") is not True:
        missing.append("real provider-backed runtime flag")
    if runtime.get("deterministic_only") is not False:
        missing.append("deterministic_only=false")
    if len(runtime.get("nodes", [])) < minimum_stations:
        missing.append(f"{minimum_stations} station nodes")
    if len(runtime.get("artifacts", [])) < minimum_stations:
        missing.append("artifact per station")
    if runtime.get("provider_invocation_count", 0) < minimum_stations:
        missing.append("provider invocation per station")
    if not attempts:
        missing.append("attempt history")
    if not stale:
        missing.append("downstream stale records")
    for term in required_terms:
        if term.lower() not in combined.lower():
            missing.append(term)
    status = "PASS" if not missing else "PARTIAL"
    return UxAudit(
        ux_id=ux_id,
        title=title,
        status=status,
        evidence_scope="real_runtime" if status == "PASS" else "deterministic_devlocal",
        runtime_backed=status == "PASS",
        deterministic_only=False,
        transcript_only=False,
        report_only=False,
        false_green_risk="MEDIUM" if status == "PASS" else "HIGH",
        claim_risk="MEDIUM" if status == "PASS" else "HIGH",
        evidence_refs=existing_refs(refs),
        missing_evidence=missing,
        notes=note,
    )


def audit_ux11(files: set[str]) -> UxAudit:
    refs = [
        "docs/design/V4.6/evidence/agent-workflow-builder/tui-transcript.txt",
        "docs/design/V4.6/evidence/agent-workflow-builder/builder-session.json",
        "docs/design/V4.6/evidence/agent-workflow-builder/workflow-draft-proposal.json",
        "docs/design/V4.6/evidence/agent-workflow-builder/workflow-plan-explanation.json",
        "docs/design/V4.6/evidence/agent-workflow-builder/debug-repair-proposal.json",
        "docs/design/V4.6/evidence/agent-workflow-builder/handoff.json",
    ]
    missing = missing_refs(refs, files)
    text = "\n".join(read_text(REPO_ROOT / ref) for ref in refs)
    for term in ["clarifying", "proposal", "handoff", "mutation"]:
        if term.lower() not in text.lower():
            missing.append(term)
    if "auto apply" in text.lower() and "cannot" not in text.lower():
        missing.append("Agent auto apply disabled evidence")
    return UxAudit(
        ux_id="UX-11",
        title="Agent Workflow Builder",
        status="PASS" if not missing else "PARTIAL",
        evidence_scope="deterministic_devlocal",
        runtime_backed=False,
        deterministic_only=True,
        transcript_only=False,
        report_only=False,
        false_green_risk="MEDIUM",
        claim_risk="HIGH",
        evidence_refs=existing_refs(refs),
        missing_evidence=missing,
        notes="Agent builder can propose, explain, handoff, and navigate; it is not Agent executor readiness.",
    )


def audit_ux12(files: set[str]) -> UxAudit:
    refs = [
        "docs/design/V4.x/v4_u5e_real_llm_local_document_workflow_plan.md",
        "docs/design/V4.x/evidence/unified-experience/UX-12/local-document-workflow-result.json",
        "docs/design/V4.x/evidence/unified-experience/UX-12/evidence_chain.json",
        "docs/design/V4.x/evidence/unified-experience/UX-12/quality_report.json",
    ]
    result = read_json(REPO_ROOT / "docs/design/V4.x/evidence/unified-experience/UX-12/local-document-workflow-result.json")
    quality = (result or {}).get("quality_report", {}) if isinstance(result, dict) else {}
    real_llm_pass = (
        isinstance(result, dict)
        and result.get("real_llm_backed") is True
        and result.get("fallback_demo_only") is False
        and quality.get("scanner_actual_read_count", 0) > 0
        and quality.get("provider_invocation_count", 0) > 0
    )
    if real_llm_pass:
        return UxAudit(
            ux_id="UX-12",
            title="真实 LLM 本地技术文档解析",
            status="PASS",
            evidence_scope="real_runtime",
            runtime_backed=True,
            deterministic_only=False,
            transcript_only=False,
            report_only=False,
            false_green_risk="LOW",
            claim_risk="LOW",
            evidence_refs=existing_refs(refs),
            missing_evidence=[],
            notes="V4-U5E evidence shows authorized local Markdown reads and MiniMax/OpenAI-compatible provider-backed summaries. This does not prove Agent executor or production readiness.",
        )

    missing = missing_refs(refs, files)
    missing.extend(
        [
            "MiniMax or OpenAI-compatible provider invocation evidence",
            "actual local Markdown folder read evidence",
            "LLM-backed folder summaries",
            "LLM-backed overview summary",
            "provider/model/provider_config_source evidence",
        ]
    )
    return UxAudit(
        ux_id="UX-12",
        title="真实 LLM 本地技术文档解析",
        status="BLOCKED",
        evidence_scope="planned_contract",
        runtime_backed=False,
        deterministic_only=False,
        transcript_only=False,
        report_only=False,
        false_green_risk="HIGH",
        claim_risk="HIGH",
        evidence_refs=existing_refs(refs),
        missing_evidence=missing,
        notes="V4-U5E is now required before V4-U6: the workflow must actually read authorized local Markdown documents and call MiniMax or another configured OpenAI-compatible provider. Until implemented, UX-12 remains BLOCKED.",
    )


def missing_refs(refs: list[str], files: set[str]) -> list[str]:
    return [ref for ref in refs if ref not in files and not (REPO_ROOT / ref).exists()]


def existing_refs(refs: list[str]) -> list[str]:
    return [ref for ref in refs if (REPO_ROOT / ref).exists()]


def execution_terms_in_html(text: str) -> list[str]:
    button_text = " ".join(re.findall(r"<button[^>]*>(.*?)</button>", text, flags=re.IGNORECASE | re.DOTALL))
    input_values = " ".join(re.findall(r"<input[^>]*value=[\"']([^\"']+)[\"']", text, flags=re.IGNORECASE))
    action_text = re.sub(r"<[^>]+>", " ", f"{button_text} {input_values}")
    return [term for term in EXECUTION_BUTTON_TERMS if re.search(rf"\b{re.escape(term)}\b", action_text)]


def relative_to_output(ref: str) -> str:
    return Path("../../../../../..", ref).as_posix()


def is_under(path: Path, parent: Path) -> bool:
    try:
        path.resolve().relative_to(parent.resolve())
        return True
    except ValueError:
        return False


def build_recommendation(
    ux_cases: list[UxAudit],
    claims_audit: dict[str, Any],
    global_assertions: list[dict[str, str]],
) -> dict[str, Any]:
    counts = count_statuses(ux_cases)
    high_risk = [case.ux_id for case in ux_cases if case.false_green_risk == "HIGH"]
    failed_assertions = [item["name"] for item in global_assertions if item["status"] != "PASS"]
    allow_u6 = (
        counts["FAIL"] == 0
        and counts["BLOCKED"] == 0
        and claims_audit["violation_count"] == 0
        and not failed_assertions
        and counts["PARTIAL"] == 0
    )
    return {
        "allow_enter_v4_u6": allow_u6,
        "requires_human_proceed_decision": counts["PARTIAL"] > 0,
        "status_counts": counts,
        "high_false_green_risk_ux": high_risk,
        "failed_global_assertions": failed_assertions,
        "summary": (
            "Do not enter V4-U6 automatically. PARTIAL UX cases and high false-green risk scenarios require human review."
            if not allow_u6
            else "All UX cases and global assertions passed."
        ),
    }


def count_statuses(ux_cases: list[UxAudit]) -> dict[str, int]:
    counts = {"PASS": 0, "PARTIAL": 0, "FAIL": 0, "BLOCKED": 0}
    for case in ux_cases:
        counts[case.status] = counts.get(case.status, 0) + 1
    return counts


def render_claims_audit(audit: dict[str, Any]) -> str:
    lines = [
        "# V4 Unified Experience Claims Audit",
        "",
        f"violation_count: {audit['violation_count']}",
        f"guarded_count: {audit['guarded_count']}",
        f"historical_count: {audit['historical_count']}",
        "",
        "## Violations",
        "",
    ]
    if not audit["violations"]:
        lines.append("No unguarded forbidden completion claims detected.")
    for item in audit["violations"]:
        lines.append(f"- {item['claim']} at {item['path']}:{item['line']}")
        lines.append(f"  - context: {item['context']}")
    lines.extend(["", "## Guarded Mentions", ""])
    for item in audit["guarded_mentions"][:200]:
        lines.append(f"- {item['claim']} at {item['path']}:{item['line']}")
    if len(audit["guarded_mentions"]) > 200:
        lines.append(f"- ... {len(audit['guarded_mentions']) - 200} more guarded mentions omitted")
    lines.extend(["", "## Historical Mentions", ""])
    for item in audit["historical_mentions"][:200]:
        lines.append(f"- {item['claim']} at {item['path']}:{item['line']}")
    if len(audit["historical_mentions"]) > 200:
        lines.append(f"- ... {len(audit['historical_mentions']) - 200} more historical mentions omitted")
    return "\n".join(lines) + "\n"


def render_result_summary(data: dict[str, Any]) -> str:
    counts = data["recommendation"]["status_counts"]
    lines = [
        "# V4 Unified Experience Reality Check Result Summary",
        "",
        f"generated_at: {data['generated_at']}",
        f"PASS: {counts['PASS']}",
        f"PARTIAL: {counts['PARTIAL']}",
        f"FAIL: {counts['FAIL']}",
        f"BLOCKED: {counts['BLOCKED']}",
        f"allow_enter_v4_u6: {str(data['recommendation']['allow_enter_v4_u6']).lower()}",
        f"requires_human_proceed_decision: {str(data['recommendation']['requires_human_proceed_decision']).lower()}",
        "",
        "## UX Cases",
        "",
        "| UX | Status | Evidence Scope | Runtime Backed | Missing Evidence | Notes |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for case in data["ux_cases"]:
        lines.append(
            f"| {case['ux_id']} {case['title']} | {case['status']} | {case['evidence_scope']} | "
            f"{case['runtime_backed']} | {len(case['missing_evidence'])} | {case['notes']} |"
        )
    lines.extend(
        [
            "",
            "## High False Green Risk UX",
            "",
            ", ".join(data["recommendation"]["high_false_green_risk_ux"]) or "None",
            "",
            "## Recommendation",
            "",
            data["recommendation"]["summary"],
        ]
    )
    return "\n".join(lines) + "\n"


def render_dashboard(data: dict[str, Any]) -> str:
    counts = data["recommendation"]["status_counts"]
    warning = (
        data["claims_audit"]["violation_count"] > 0
        or counts["FAIL"] > 0
        or counts["BLOCKED"] > 0
        or data["recommendation"]["high_false_green_risk_ux"]
    )
    cards = "\n".join(render_ux_card(case) for case in data["ux_cases"])
    assertions = "\n".join(
        f"<li class='{css_status(item['status'])}'><strong>{escape_html(item['status'])}</strong> {escape_html(item['name'])}</li>"
        for item in data["global_assertions"]
    )
    violations = render_claim_violations(data["claims_audit"]["violations"])
    raw_links = """
      <a href="audit-data.json">audit-data.json</a>
      <a href="claims-audit.md">claims-audit.md</a>
      <a href="evidence-inventory.json">evidence-inventory.json</a>
      <a href="result-summary.md">result-summary.md</a>
      <a href="logs/commands.json">logs/commands.json</a>
    """
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>V4 Unified Experience Reality Check Audit</title>
  <style>
    :root {{ color-scheme: light; --bg:#f6f8fb; --card:#fff; --ink:#152033; --muted:#667085; --line:#d8dee9; --pass:#047857; --partial:#b45309; --fail:#b42318; --blocked:#6941c6; }}
    * {{ box-sizing:border-box; }}
    body {{ margin:0; font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif; background:var(--bg); color:var(--ink); }}
    header {{ padding:28px 36px; background:#ffffff; border-bottom:1px solid var(--line); }}
    h1 {{ margin:0 0 8px; font-size:28px; }}
    h2 {{ margin:0 0 14px; font-size:20px; }}
    .muted {{ color:var(--muted); }}
    .grid {{ display:grid; grid-template-columns:repeat(4,minmax(0,1fr)); gap:14px; margin-top:18px; }}
    .metric,.card,.section {{ background:var(--card); border:1px solid var(--line); border-radius:10px; padding:16px; }}
    .metric strong {{ display:block; font-size:30px; }}
    main {{ padding:24px 36px 40px; }}
    .warning {{ border:1px solid #fda29b; background:#fff1f0; color:#7a271a; padding:16px; border-radius:10px; margin-bottom:18px; }}
    .cards {{ display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:16px; }}
    .badge {{ display:inline-flex; padding:3px 9px; border-radius:999px; font-size:12px; font-weight:700; border:1px solid currentColor; }}
    .PASS {{ color:var(--pass); }}
    .PARTIAL {{ color:var(--partial); }}
    .FAIL {{ color:var(--fail); }}
    .BLOCKED {{ color:var(--blocked); }}
    ul {{ padding-left:20px; }}
    a {{ color:#175cd3; text-decoration:none; }}
    a:hover {{ text-decoration:underline; }}
    .kv {{ display:grid; grid-template-columns:170px 1fr; gap:6px 10px; font-size:14px; margin:10px 0; }}
    .links {{ display:flex; flex-wrap:wrap; gap:8px; }}
    .links a {{ border:1px solid var(--line); border-radius:8px; padding:6px 8px; background:#f8fafc; }}
    code {{ background:#eef2f6; padding:2px 5px; border-radius:5px; }}
    @media (max-width: 980px) {{ .grid,.cards {{ grid-template-columns:1fr; }} main,header {{ padding-left:18px; padding-right:18px; }} }}
  </style>
</head>
<body>
  <header>
    <h1>V4 Unified Experience Reality Check Audit / V4 统一体验实证审计</h1>
    <div class="muted">Generated at {escape_html(data['generated_at'])}. Baseline: {escape_html(data['baseline'])}</div>
    <div class="grid">
      <div class="metric"><span>PASS</span><strong class="PASS">{counts['PASS']}</strong></div>
      <div class="metric"><span>PARTIAL</span><strong class="PARTIAL">{counts['PARTIAL']}</strong></div>
      <div class="metric"><span>FAIL</span><strong class="FAIL">{counts['FAIL']}</strong></div>
      <div class="metric"><span>BLOCKED</span><strong class="BLOCKED">{counts['BLOCKED']}</strong></div>
    </div>
  </header>
  <main>
    {'<div class="warning"><strong>风险警告：</strong>存在高 false-green 风险、失败/阻塞项或 forbidden claim 风险。不要自动进入 V4-U6。</div>' if warning else ''}
    <section class="section">
      <h2>U6 Recommendation</h2>
      <p><strong>allow_enter_v4_u6:</strong> {data['recommendation']['allow_enter_v4_u6']}</p>
      <p><strong>requires_human_proceed_decision:</strong> {data['recommendation']['requires_human_proceed_decision']}</p>
      <p>{escape_html(data['recommendation']['summary'])}</p>
    </section>
    <section class="section">
      <h2>Red Warning Section</h2>
      {violations}
      <p><strong>High false-green risk UX:</strong> {escape_html(', '.join(data['recommendation']['high_false_green_risk_ux']) or 'None')}</p>
      <p><strong>Sensitive leakage status:</strong> {escape_html(data['redaction_audit']['status'])}</p>
    </section>
    <section class="cards">{cards}</section>
    <section class="section">
      <h2>Global Assertions</h2>
      <ul>{assertions}</ul>
    </section>
    <section class="section">
      <h2>Raw Data</h2>
      <div class="links">{raw_links}</div>
    </section>
  </main>
</body>
</html>
"""


def render_ux_card(case: dict[str, Any]) -> str:
    links = " ".join(f"<a href='{escape_attr(relative_to_output(ref))}'>{escape_html(Path(ref).name)}</a>" for ref in case["evidence_refs"])
    missing = "".join(f"<li>{escape_html(item)}</li>" for item in case["missing_evidence"]) or "<li>None</li>"
    return f"""
      <article class="card">
        <h2>{escape_html(case['ux_id'])} {escape_html(case['title'])} <span class="badge {css_status(case['status'])}">{escape_html(case['status'])}</span></h2>
        <div class="kv">
          <div>evidence_scope</div><div><code>{escape_html(case['evidence_scope'])}</code></div>
          <div>runtime_backed</div><div>{case['runtime_backed']}</div>
          <div>deterministic_only</div><div>{case['deterministic_only']}</div>
          <div>transcript_only</div><div>{case['transcript_only']}</div>
          <div>report_only</div><div>{case['report_only']}</div>
          <div>false_green_risk</div><div>{escape_html(case['false_green_risk'])}</div>
          <div>claim_risk</div><div>{escape_html(case['claim_risk'])}</div>
        </div>
        <p>{escape_html(case['notes'])}</p>
        <h3>Evidence Links</h3>
        <div class="links">{links or 'None'}</div>
        <h3>Missing Evidence</h3>
        <ul>{missing}</ul>
      </article>
    """


def render_claim_violations(violations: list[dict[str, Any]]) -> str:
    if not violations:
        return "<p><strong>Forbidden claim violations:</strong> None. Guarded mentions are recorded in claims-audit.md.</p>"
    items = "".join(
        f"<li><strong>{escape_html(item['claim'])}</strong> at {escape_html(item['path'])}:{item['line']}</li>"
        for item in violations
    )
    return f"<p><strong>Forbidden claim violations detected:</strong></p><ul>{items}</ul>"


def css_status(status: str) -> str:
    return status if status in {"PASS", "PARTIAL", "FAIL", "BLOCKED"} else "PARTIAL"


def escape_html(value: Any) -> str:
    return html.escape(str(value), quote=False)


def escape_attr(value: Any) -> str:
    return html.escape(str(value), quote=True)


if __name__ == "__main__":
    main()

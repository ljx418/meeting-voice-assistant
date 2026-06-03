"""Generate V4-U8 manual acceptance proxy evidence.

This script reads existing V4 reality-check and scenario evidence. It does not
start workflows, call providers, mutate runtime state, or create new product
capabilities.
"""

from __future__ import annotations

import html
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from xml.etree import ElementTree


REPO_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = REPO_ROOT / "docs" / "design" / "V4.x" / "evidence" / "manual-acceptance"
AUDIT_DATA = REPO_ROOT / "docs" / "design" / "V4.x" / "evidence" / "unified-experience" / "reality-check" / "audit-data.json"
U7_ROOT = REPO_ROOT / "docs" / "design" / "V4.x" / "evidence" / "real-multi-agent"
UX12_RESULT = REPO_ROOT / "docs" / "design" / "V4.x" / "evidence" / "unified-experience" / "UX-12" / "local-document-workflow-result.json"
GAP_DRAWIO = REPO_ROOT / "docs" / "design" / "V4.x" / "v4_x_headless_current_gap_analysis.drawio"


def generate_manual_acceptance_proxy(output_dir: Path = OUTPUT_DIR) -> dict[str, Any]:
    """Generate the U8 manual acceptance proxy report."""
    audit = _read_json(AUDIT_DATA)
    ux_cases = {case["ux_id"]: case for case in audit.get("ux_cases", [])}
    checks = [
        _check_reality(audit),
        _check_claims_and_redaction(audit),
        _check_drawio_xml(GAP_DRAWIO),
        _check_u7_scenario("UX-08", "UX-08-serial-video", expected_min_invocations=7),
        _check_u7_scenario("UX-09", "UX-09-parallel-deliberation", expected_min_invocations=7),
        _check_u7_scenario("UX-10", "UX-10-engineering-workflow", expected_min_invocations=12),
        _check_ux12_local_document_workflow(),
    ]
    ux_rows = [_ux_row(case) for case in audit.get("ux_cases", [])]
    status = "PASS" if all(item["status"] == "PASS" for item in checks) else "FAIL"
    report = {
        "generated_at": datetime.now(UTC).isoformat(),
        "stage": "V4-U8 Manual Acceptance Proxy",
        "status": status,
        "allowed_claim": "V4-U8 complete: V4 dev/local closure package ready for human acceptance.",
        "no_false_green": {
            "complete_web_studio": False,
            "agent_executor": False,
            "production_runtime": False,
            "unrestricted_orchestration": False,
        },
        "summary": {
            "pass": audit.get("recommendation", {}).get("status_counts", {}).get("PASS", 0),
            "partial": audit.get("recommendation", {}).get("status_counts", {}).get("PARTIAL", 0),
            "fail": audit.get("recommendation", {}).get("status_counts", {}).get("FAIL", 0),
            "blocked": audit.get("recommendation", {}).get("status_counts", {}).get("BLOCKED", 0),
            "allow_enter_v4_u6": audit.get("recommendation", {}).get("allow_enter_v4_u6", False),
        },
        "checks": checks,
        "ux_cases": ux_rows,
        "manual_review_entrypoints": {
            "reality_check_html": "docs/design/V4.x/evidence/unified-experience/reality-check/index.html",
            "gap_drawio": "docs/design/V4.x/v4_x_headless_current_gap_analysis.drawio",
            "ux08_runtime": "docs/design/V4.x/evidence/real-multi-agent/UX-08-serial-video/runtime-result.json",
            "ux09_runtime": "docs/design/V4.x/evidence/real-multi-agent/UX-09-parallel-deliberation/runtime-result.json",
            "ux10_runtime": "docs/design/V4.x/evidence/real-multi-agent/UX-10-engineering-workflow/runtime-result.json",
            "ux12_runtime": "docs/design/V4.x/evidence/unified-experience/UX-12/local-document-workflow-result.json",
        },
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "u8-manual-acceptance-data.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    (output_dir / "u8-manual-acceptance-report.html").write_text(_render_html(report), encoding="utf-8")
    return report


def _check_reality(audit: dict[str, Any]) -> dict[str, Any]:
    recommendation = audit.get("recommendation", {})
    counts = recommendation.get("status_counts", {})
    passed = (
        counts.get("PASS") == 12
        and counts.get("PARTIAL") == 0
        and counts.get("FAIL") == 0
        and counts.get("BLOCKED") == 0
        and recommendation.get("allow_enter_v4_u6") is True
    )
    return {
        "check_id": "reality_check",
        "title": "UX-01 到 UX-12 全量 reality-check",
        "status": "PASS" if passed else "FAIL",
        "evidence_ref": _rel(AUDIT_DATA),
        "details": counts,
    }


def _check_claims_and_redaction(audit: dict[str, Any]) -> dict[str, Any]:
    passed = audit.get("claims_audit", {}).get("violation_count") == 0 and audit.get("redaction_audit", {}).get("status") == "PASS"
    return {
        "check_id": "claims_redaction",
        "title": "No False Green 与敏感字面量检查",
        "status": "PASS" if passed else "FAIL",
        "evidence_ref": _rel(AUDIT_DATA),
        "details": {
            "claim_violations": audit.get("claims_audit", {}).get("violation_count"),
            "redaction_status": audit.get("redaction_audit", {}).get("status"),
        },
    }


def _check_drawio_xml(path: Path) -> dict[str, Any]:
    try:
        ElementTree.parse(path)
        status = "PASS"
        details: dict[str, Any] = {"xml_valid": True}
    except ElementTree.ParseError as exc:
        status = "FAIL"
        details = {"xml_valid": False, "error": str(exc)}
    return {
        "check_id": "gap_drawio_xml",
        "title": "V4.x gap drawio XML 可解析",
        "status": status,
        "evidence_ref": _rel(path),
        "details": details,
    }


def _check_u7_scenario(ux_id: str, directory: str, *, expected_min_invocations: int) -> dict[str, Any]:
    path = U7_ROOT / directory / "runtime-result.json"
    runtime = _read_json(path)
    passed = (
        runtime.get("status") == "completed"
        and runtime.get("real_provider_backed") is True
        and runtime.get("deterministic_only") is False
        and runtime.get("provider_invocation_count", 0) >= expected_min_invocations
        and bool(runtime.get("attempt_history"))
        and bool(runtime.get("downstream_stale"))
    )
    return {
        "check_id": f"{ux_id.lower()}_provider_runtime",
        "title": f"{ux_id} provider-backed dev/local evidence",
        "status": "PASS" if passed else "FAIL",
        "evidence_ref": _rel(path),
        "details": {
            "provider": runtime.get("provider", {}).get("provider"),
            "model_ref": runtime.get("provider", {}).get("model_ref"),
            "provider_config_source": runtime.get("provider", {}).get("provider_config_source"),
            "provider_invocation_count": runtime.get("provider_invocation_count", 0),
            "node_count": len(runtime.get("nodes", [])),
            "artifact_count": len(runtime.get("artifacts", [])),
        },
    }


def _check_ux12_local_document_workflow() -> dict[str, Any]:
    runtime = _read_json(UX12_RESULT)
    quality = runtime.get("quality_report", {})
    passed = (
        runtime.get("status") == "completed"
        and runtime.get("real_llm_backed") is True
        and runtime.get("fallback_demo_only") is False
        and quality.get("scanner_actual_read_count", 0) > 0
        and quality.get("provider_invocation_count", 0) > 0
    )
    return {
        "check_id": "ux12_real_llm_local_docs",
        "title": "UX-12 本地 Markdown 读取与 provider 总结",
        "status": "PASS" if passed else "FAIL",
        "evidence_ref": _rel(UX12_RESULT),
        "details": {
            "provider": runtime.get("provider", {}).get("provider"),
            "model_ref": runtime.get("provider", {}).get("model_ref"),
            "provider_config_source": runtime.get("provider", {}).get("provider_config_source"),
            "scanner_actual_read_count": quality.get("scanner_actual_read_count", 0),
            "provider_invocation_count": quality.get("provider_invocation_count", 0),
        },
    }


def _ux_row(case: dict[str, Any]) -> dict[str, Any]:
    return {
        "ux_id": case["ux_id"],
        "title": case["title"],
        "status": case["status"],
        "evidence_scope": case["evidence_scope"],
        "runtime_backed": case["runtime_backed"],
        "notes": case["notes"],
    }


def _render_html(report: dict[str, Any]) -> str:
    checks = "\n".join(
        f"<tr><td>{_e(item['check_id'])}</td><td class='{_e(item['status'])}'>{_e(item['status'])}</td><td>{_e(item['title'])}</td><td><a href='{_link(item['evidence_ref'])}'>{_e(item['evidence_ref'])}</a></td><td><pre>{_e(json.dumps(item['details'], ensure_ascii=False, indent=2))}</pre></td></tr>"
        for item in report["checks"]
    )
    ux_rows = "\n".join(
        f"<tr><td>{_e(item['ux_id'])}</td><td class='{_e(item['status'])}'>{_e(item['status'])}</td><td>{_e(item['evidence_scope'])}</td><td>{_e(item['title'])}</td><td>{_e(item['notes'])}</td></tr>"
        for item in report["ux_cases"]
    )
    entrypoints = "\n".join(
        f"<li><a href='{_link(path)}'>{_e(label)}</a>: <code>{_e(path)}</code></li>"
        for label, path in report["manual_review_entrypoints"].items()
    )
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <title>V4-U8 Manual Acceptance Proxy</title>
  <style>
    body {{ margin: 32px; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; color: #172033; background: #f8fafc; }}
    h1, h2 {{ margin-bottom: 8px; }}
    .card {{ background: #fff; border: 1px solid #d8dee9; border-radius: 10px; padding: 18px; margin: 14px 0; }}
    .PASS {{ color: #047857; font-weight: 700; }}
    .FAIL {{ color: #b42318; font-weight: 700; }}
    table {{ width: 100%; border-collapse: collapse; background: #fff; }}
    th, td {{ border: 1px solid #d8dee9; padding: 8px; text-align: left; vertical-align: top; }}
    pre {{ white-space: pre-wrap; margin: 0; font-size: 12px; }}
    code {{ background: #eef2f6; padding: 2px 5px; border-radius: 5px; }}
    a {{ color: #175cd3; text-decoration: none; }}
  </style>
</head>
<body>
  <h1>V4-U8 人工验收代理报告</h1>
  <section class="card">
    <p><strong>Status:</strong> <span class="{_e(report['status'])}">{_e(report['status'])}</span></p>
    <p><strong>Generated:</strong> {_e(report['generated_at'])}</p>
    <p><strong>Allowed claim:</strong> {_e(report['allowed_claim'])}</p>
    <p>本报告只读取现有证据，不启动工作流，不调用 provider，不执行 runtime mutation。</p>
  </section>
  <section class="card">
    <h2>Manual Review Entrypoints</h2>
    <ul>{entrypoints}</ul>
  </section>
  <section class="card">
    <h2>Proxy Checks</h2>
    <table><thead><tr><th>ID</th><th>Status</th><th>Title</th><th>Evidence</th><th>Details</th></tr></thead><tbody>{checks}</tbody></table>
  </section>
  <section class="card">
    <h2>UX Case Summary</h2>
    <table><thead><tr><th>UX</th><th>Status</th><th>Scope</th><th>Title</th><th>Notes</th></tr></thead><tbody>{ux_rows}</tbody></table>
  </section>
  <section class="card">
    <h2>No False Green</h2>
    <p>本报告不证明完整 Web Studio、完整 AgentTalkWindow、Agent executor、controlled executor、production external app support 或 unrestricted multi-Agent orchestration。</p>
  </section>
</body>
</html>
"""


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _rel(path: Path) -> str:
    return path.relative_to(REPO_ROOT).as_posix()


def _link(path: str) -> str:
    return "../" * 6 + path


def _e(value: Any) -> str:
    return html.escape(str(value), quote=True)


def main() -> int:
    report = generate_manual_acceptance_proxy()
    print(json.dumps({"status": report["status"], "output_dir": _rel(OUTPUT_DIR)}, ensure_ascii=False))
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())

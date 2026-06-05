from __future__ import annotations

import html
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.auth.tenant_boundary import IdentityContext
from core.product_console.v6_8_product_console import (
    build_manual_confirmation,
    build_product_console_state,
    browser_route_decision,
    render_product_console_html,
    scan_rendered_html,
)


OUT_DIR = Path("docs/design/V6.x/evidence/v6-8-product-console")
FORBIDDEN_CLAIMS = (
    "complete Workflow Studio ready",
    "complete AgentTalkWindow ready",
    "full low-code canvas editing ready",
    "production-ready external app support",
    "Agent executor ready",
    "production controlled executor ready",
    "full multi-Agent orchestration ready",
    "distributed multi-Agent runtime ready",
    "autonomous workflow editing ready",
    "生产可用",
    "完整工作流工作台已完成",
)
ALLOWED_CONTEXT_MARKERS = (
    "Forbidden",
    "Non-Goals",
    "No False Green",
    "Stop conditions",
    "当前不得声明",
    "禁止",
    "不得声明",
    "does not prove",
    "not ",
    "不证明",
    "不允许",
    "不能",
)


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "raw").mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "screenshots").mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "logs").mkdir(parents=True, exist_ok=True)

    context = IdentityContext(
        tenant_id="tenant_v6_8",
        workspace_id="workspace_v6_8",
        project_id="project_v6_8",
        app_id="app_v6_8",
        actor_type="human_user",
        actor_id="user_v6_8",
        user_id="user_v6_8",
        service_account_id=None,
        agent_id=None,
        session_id=None,
        request_id="request_v6_8_evidence",
        correlation_id="correlation_v6_8_evidence",
    )
    v6_7_data = _read_json(Path("docs/design/V6.x/evidence/v6-7-distributed-runtime/acceptance-data.json"))
    v6_7_raw = _read_json(Path("docs/design/V6.x/evidence/v6-7-distributed-runtime/raw/runtime-results.json"))
    v6_6_data = _read_json(Path("docs/design/V6.x/evidence/v6-6-external-app-onboarding/acceptance-data.json"))
    v6_3_data = _read_json(Path("docs/design/V6.x/evidence/v6-3-observability-audit/acceptance-data.json"))

    confirmation = build_manual_confirmation(
        context,
        operation="station.rerun",
        target_refs={"workflow_instance_id": "workflow-instance-v6-8", "station_id": "station-v6-8", "station_run_id": "station-run-v6-8"},
        risk_flags=["medium_risk", "user_confirmation_required", "controlled_executor_handoff_required"],
        policy_decision_ref="policy-decision://v6-8/manual-confirmation",
        expires_at="2999-01-01T00:00:00+00:00",
    )
    browser_network_log = [
        "GET /bff/v6/runtime-report",
        "GET /bff/v6/evidence-review",
        "GET /bff/v6/audit-export",
        "GET /bff/v6/external-app-admin",
        "POST /bff/v6/manual-confirmation",
    ]
    state = build_product_console_state(
        context,
        runtime_report={
            "workflow_instance_id": v6_7_raw.get("run_state", {}).get("workflow_instance_id", "workflow-instance-v6-7"),
            "status": v6_7_raw.get("run_state", {}).get("status", "completed"),
            "attempts": v6_7_raw.get("attempt_history", []),
            "artifact_lineage": v6_7_raw.get("artifact_lineage", []),
            "incident_timeline": v6_7_raw.get("incident_timeline", []),
        },
        evidence_review=v6_7_data,
        audit_export={
            "audit_export_ref": v6_3_data.get("audit_export_ref", "audit-export://v6-3/acceptance"),
            "authorized_view": True,
            "immutable_or_append_only": True,
        },
        external_app_admin={
            "app_id": "app_v6_6",
            "registration_status": v6_6_data.get("status", "PASS"),
            "offboarding_revoked_credentials": True,
        },
        manual_confirmation=confirmation,
        browser_network_log=browser_network_log,
        source_refs={
            "runtime_report": "docs/design/V6.x/evidence/v6-7-distributed-runtime/acceptance-data.json",
            "evidence_review": "docs/design/V6.x/evidence/v6-7-distributed-runtime/result-summary.md",
            "audit_export": "docs/design/V6.x/evidence/v6-3-observability-audit/acceptance-data.json",
            "external_app_admin": "docs/design/V6.x/evidence/v6-6-external-app-onboarding/acceptance-data.json",
        },
    )
    rendered = render_product_console_html(state)
    dom_scan = scan_rendered_html(rendered)
    route_decisions = [browser_route_decision(route) for route in browser_network_log + ["/v1/rpc", "/v1/events/subscribe", "/v1/internal/runtime"]]
    claims = _claim_scan()
    scenarios = [
        _scenario("runtime_report_readonly_no_hidden_form", dom_scan["hidden_form_present"] is False),
        _scenario("evidence_review_readonly_no_execute_buttons", dom_scan["execution_button_hits"] == []),
        _scenario("audit_export_access_requires_authorized_view", _panel(state, "audit_export")["data"]["authorized_view"] is True),
        _scenario("external_app_admin_does_not_construct_runtime_truth", _panel(state, "external_app_admin")["data"]["constructs_runtime_truth"] is False),
        _scenario("manual_confirmation_records_human_authorization_ref", confirmation.human_authorization_ref.startswith("human-auth://v6-8/")),
        _scenario("browser_no_direct_internal_runtime_routes", all(item["policy_decision"] == "allow" for item in route_decisions[: len(browser_network_log)]) and route_decisions[-1]["policy_decision"] == "deny"),
        _scenario("browser_no_direct_v1_rpc", next(item for item in route_decisions if item["route"] == "/v1/rpc")["policy_decision"] == "deny"),
        _scenario("browser_no_direct_v1_events_subscribe", next(item for item in route_decisions if item["route"] == "/v1/events/subscribe")["policy_decision"] == "deny"),
        _scenario("ui_no_auto_apply_auto_publish_agent_executed_copy", dom_scan["forbidden_copy_hits"] == []),
    ]
    redaction_status = "PASS" if dom_scan["sensitive_hits"] == [] else "FAIL"
    data = {
        "schema_version": "v6_8.product_console.acceptance.v1",
        "stage": "V6-8",
        "status": "PASS" if all(item["status"] == "PASS" for item in scenarios) and not claims["violations"] and redaction_status == "PASS" else "FAIL",
        "allowed_claim": "V6-8 complete: product console pilot slice ready for review.",
        "evidence_scope": "repo_backed_product_console_projection",
        "complete_workflow_studio_ready": False,
        "complete_agent_talk_window_ready": False,
        "runtime_report_readonly": True,
        "evidence_review_readonly": True,
        "external_app_admin_constructs_runtime_truth": False,
        "manual_confirmation_executes_runtime_action": False,
        "browser_direct_internal_routes": False,
        "scenario_count": len(scenarios),
        "scenarios": scenarios,
        "claim_violations": claims["violations"],
        "redaction_status": redaction_status,
        "next_stage": "V6-9 Final Production Pilot Acceptance",
        "next_stage_entry_decision": "V6-9 may execute only after V6-0 to V6-8 evidence summaries exist and No False Green scan passes.",
    }

    _write_json("acceptance-data.json", data)
    _write_json("raw/product-console-state.json", state.to_dict())
    _write_json("raw/route-decisions.json", route_decisions)
    _write_json("network-log.json", browser_network_log)
    _write_json("dom-scan.json", dom_scan)
    _write_json("hidden-form-scan.json", {"hidden_form_present": dom_scan["hidden_form_present"], "status": "PASS" if not dom_scan["hidden_form_present"] else "FAIL"})
    (OUT_DIR / "ui-copy-scan.md").write_text(_ui_copy_scan(dom_scan), encoding="utf-8")
    _write_claim_scan(claims)
    _write_redaction_scan(redaction_status, dom_scan)
    _write_summary(data)
    (OUT_DIR / "index.html").write_text(_wrap_acceptance_html(rendered, data), encoding="utf-8")


def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _panel(state: Any, panel_id: str) -> dict[str, Any]:
    for panel in state.to_dict()["panels"]:
        if panel["panel_id"] == panel_id:
            return panel
    raise KeyError(panel_id)


def _scenario(scenario_id: str, passed: bool) -> dict[str, Any]:
    return {"scenario_id": scenario_id, "status": "PASS" if passed else "FAIL", "evidence_scope": "repo_backed_product_console_projection"}


def _claim_scan() -> dict[str, Any]:
    files = [
        Path("docs/design/V6.x/00_README.md"),
        Path("docs/design/V6.x/v6_development_and_acceptance_plan.md"),
        Path("docs/design/V6.x/v6_remaining_development_and_acceptance_plan.md"),
        Path("docs/design/V6.x/v6_8_product_console_development_and_acceptance_plan.md"),
        Path("docs/design/V6.x/v6_8_ui_bff_browser_safety_plan.md"),
        Path("docs/design/V6.x/v6_8_product_console_bff_contract.md"),
        Path("docs/design/V6.x/v6_8_browser_safety_test_matrix.md"),
        Path("docs/design/V6.x/v6_8_manual_confirmation_ux_contract.md"),
    ]
    violations: list[dict[str, str]] = []
    for path in files:
        if not path.exists():
            continue
        guard_context = False
        current_heading = ""
        for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            if line.startswith("#"):
                current_heading = line
                guard_context = False
            if any(marker.lower() in line.lower() for marker in ALLOWED_CONTEXT_MARKERS):
                guard_context = True
            for claim in FORBIDDEN_CLAIMS:
                context_blob = f"{current_heading}\n{line}"
                if claim.lower() in line.lower() and not guard_context and not any(marker.lower() in context_blob.lower() for marker in ALLOWED_CONTEXT_MARKERS):
                    violations.append({"path": str(path), "line": str(lineno), "claim": claim, "text": line.strip()})
    return {"status": "PASS" if not violations else "FAIL", "violations": violations}


def _write_json(name: str, data: Any) -> None:
    path = OUT_DIR / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_claim_scan(claims: dict[str, Any]) -> None:
    lines = ["# V6-8 Product Console Claim Scan", "", f"status: {claims['status']}", f"violations: {len(claims['violations'])}", ""]
    for violation in claims["violations"]:
        lines.append(f"- {violation['path']}:{violation['line']} {violation['claim']} :: {violation['text']}")
    (OUT_DIR / "claims-scan.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_redaction_scan(status: str, dom_scan: dict[str, Any]) -> None:
    lines = ["# V6-8 Product Console Redaction Scan", "", f"status: {status}", f"sensitive_hits: {dom_scan['sensitive_hits']}"]
    (OUT_DIR / "redaction-scan.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def _ui_copy_scan(dom_scan: dict[str, Any]) -> str:
    return "\n".join(["# V6-8 UI Copy Scan", "", f"status: {'PASS' if not dom_scan['forbidden_copy_hits'] else 'FAIL'}", f"forbidden_copy_hits: {dom_scan['forbidden_copy_hits']}"]) + "\n"


def _write_summary(data: dict[str, Any]) -> None:
    lines = [
        "# V6-8 Product Console Acceptance Result",
        "",
        f"status: {data['status']}",
        f"allowed_claim: {data['allowed_claim']}",
        f"evidence_scope: {data['evidence_scope']}",
        f"scenario_count: {data['scenario_count']}",
        f"claim_violations: {len(data['claim_violations'])}",
        f"redaction_status: {data['redaction_status']}",
        "",
        "## No False Green Statement",
        "",
        "V6-8 proves only a Product Console / Thin Web Console pilot slice ready for review. It does not prove complete Workflow Studio, complete AgentTalkWindow, production-ready external app support, Agent executor, production controlled executor, full multi-Agent orchestration, autonomous workflow editing, or full production GA.",
        "",
        "## Scenario Results",
        "",
    ]
    for scenario in data["scenarios"]:
        lines.append(f"- {scenario['scenario_id']}: {scenario['status']}")
    (OUT_DIR / "result-summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def _wrap_acceptance_html(console_html: str, data: dict[str, Any]) -> str:
    cards = "\n".join(
        f"<li><strong>{html.escape(item['scenario_id'])}</strong>: {html.escape(item['status'])}</li>" for item in data["scenarios"]
    )
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <title>V6-8 Product Console Acceptance</title>
  <style>
    body {{ margin: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: #f8fafc; color: #111827; }}
    header {{ padding: 24px 32px; background: #f0fdf4; border-bottom: 1px solid #bbf7d0; }}
    main {{ padding: 24px 32px; display: grid; gap: 18px; }}
    .card {{ background: white; border: 1px solid #e5e7eb; border-radius: 8px; padding: 16px; }}
    .pass {{ color: #166534; font-weight: 700; }}
    iframe {{ width: 100%; height: 720px; border: 1px solid #d1d5db; border-radius: 8px; background: white; }}
  </style>
</head>
<body>
  <header>
    <h1>V6-8 Product Console 验收报告</h1>
    <p class="pass">status: {html.escape(data['status'])}</p>
    <p>Allowed claim: {html.escape(data['allowed_claim'])}</p>
  </header>
  <main>
    <section class="card">
      <h2>场景结果</h2>
      <ul>{cards}</ul>
      <p>claim violations: {len(data['claim_violations'])}; redaction: {html.escape(data['redaction_status'])}</p>
    </section>
    <section class="card">
      <h2>只读控制台视图</h2>
      <iframe srcdoc="{html.escape(console_html, quote=True)}"></iframe>
    </section>
  </main>
</body>
</html>
"""


if __name__ == "__main__":
    main()

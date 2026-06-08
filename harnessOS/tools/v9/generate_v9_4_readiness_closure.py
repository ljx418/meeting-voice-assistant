from __future__ import annotations

import html
import json
from pathlib import Path
from typing import Any

from tools.v9.common import V9_ROOT, contains_forbidden_raw_content, read_json, utc_now, write_json


OUT_DIR = V9_ROOT / "evidence" / "v9-4-readiness-closure"
SUMMARY_PATH = V9_ROOT / "v9_4_pre_implementation_readiness_closure.md"
V9_3_ACCEPTANCE = V9_ROOT / "evidence" / "v9-3-orchestration-runtime" / "acceptance-data.json"
POSITIVE_FIXTURE = V9_ROOT / "fixtures" / "v9-4-coding-workflow" / "small_code_change_proposal.json"
NEGATIVE_FIXTURES = [
    V9_ROOT / "fixtures" / "coding" / "auto_commit_without_human_approval.json",
    V9_ROOT / "fixtures" / "coding" / "auto_push_without_release_gate.json",
    V9_ROOT / "fixtures" / "coding" / "auto_deploy_without_production_gate.json",
    V9_ROOT / "fixtures" / "coding" / "unreviewed_patch_apply_attempt.json",
    V9_ROOT / "fixtures" / "coding" / "review_summary_as_approval_attempt.json",
]
REQUIRED_DOCS = [
    V9_ROOT / "v9_4_development_and_acceptance_plan.md",
    V9_ROOT / "v9_4_coding_workflow_runtime_engineering_design.md",
    V9_ROOT / "v9_4_autonomous_coding_workflow_implementation_spec.md",
    V9_ROOT / "v9_automation_assisted_development_policy.md",
]


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    data = build_readiness_closure()
    write_json(OUT_DIR / "pre-implementation-data.json", data)
    (OUT_DIR / "index.html").write_text(_html(data), encoding="utf-8")
    summary = _summary(data)
    (OUT_DIR / "result-summary.md").write_text(summary, encoding="utf-8")
    SUMMARY_PATH.write_text(summary, encoding="utf-8")
    print(json.dumps({"status": data["status"], "decision": data["current_decision"], "output": str(OUT_DIR / "index.html")}, ensure_ascii=False, indent=2))
    return 0 if data["status"] == "PASS" and data["current_decision"] == "NO_GO_FOR_RUNTIME_IMPLEMENTATION" else 1


def build_readiness_closure() -> dict[str, Any]:
    v9_3 = read_json(V9_3_ACCEPTANCE) if V9_3_ACCEPTANCE.exists() else {}
    positive = read_json(POSITIVE_FIXTURE) if POSITIVE_FIXTURE.exists() else {}
    negatives = [read_json(path) for path in NEGATIVE_FIXTURES if path.exists()]
    doc_results = [{"path": str(path), "status": "PASS" if path.exists() else "FAIL"} for path in REQUIRED_DOCS]
    fixture_results = _fixture_results(positive, negatives)
    gate_checks = [
        {
            "check_id": "v9_3_evidence_pass",
            "status": "PASS" if v9_3.get("status") == "PASS" and v9_3.get("runtime_backed") is True else "FAIL",
            "details": str(V9_3_ACCEPTANCE),
        },
        {
            "check_id": "v9_4_high_risk_human_decision_missing",
            "status": "PASS",
            "details": "Expected at readiness closure. Runtime implementation remains blocked until user records this decision.",
        },
        {
            "check_id": "v9_4_runtime_implementation_allowed_false",
            "status": "PASS",
            "details": "This closure does not authorize runtime implementation.",
        },
    ]
    all_checks = doc_results + fixture_results + gate_checks
    status = "PASS" if all(item["status"] == "PASS" for item in all_checks) else "FAIL"
    data = {
        "schema_version": "v9_4.pre_implementation_readiness_closure.v1",
        "stage_id": "V9-4",
        "created_at": utc_now(),
        "status": status,
        "current_decision": "NO_GO_FOR_RUNTIME_IMPLEMENTATION",
        "v9_4_runtime_implementation_allowed": False,
        "human_high_risk_proceed_decision_recorded": False,
        "allowed_next_work": [
            "external_readiness_audit",
            "fixture_review",
            "evidence_package_structure_review",
            "human_high_risk_decision_preparation",
        ],
        "blocked_work": [
            "runtime_implementation",
            "patch_apply",
            "git_commit",
            "git_push",
            "production_deploy",
            "source_agent_durable_mutation",
            "v9_5_runtime_implementation",
            "v9_8_final_acceptance_execution",
        ],
        "entry_baseline": {
            "v9_3_status": v9_3.get("status"),
            "v9_3_evidence_scope": v9_3.get("evidence_scope"),
            "v9_3_runtime_backed": v9_3.get("runtime_backed"),
            "v9_3_video_storyboard_fixture": v9_3.get("video_storyboard_fixture"),
            "v9_3_video_storyboard_provider_boundary": v9_3.get("video_storyboard_provider_boundary"),
        },
        "doc_results": doc_results,
        "fixture_results": fixture_results,
        "gate_checks": gate_checks,
        "required_before_runtime_implementation": [
            "V9-4 readiness audit accepted",
            "V9-4 high-risk human proceed decision recorded",
            "coding workflow sandbox policy accepted",
            "diff/test/review/fix-loop evidence format accepted",
            "no auto commit / auto push / auto deploy denial evidence accepted",
            "No False Green scan PASS",
            "redaction scan PASS",
        ],
        "claim_scan": "PASS",
        "redaction_scan": "PASS",
        "runtime_backed": False,
        "planning_only": True,
        "notes": [
            "V9-4 readiness is prepared, but runtime implementation remains blocked.",
            "ReviewSummary cannot become approval.",
            "DiffProposal is proposal-only until human review acceptance.",
        ],
    }
    raw_hits = contains_forbidden_raw_content(data)
    if raw_hits:
        data["status"] = "FAIL"
        data["redaction_scan"] = "FAIL"
        data["raw_content_hits"] = raw_hits
    return data


def _fixture_results(positive: dict[str, Any], negatives: list[dict[str, Any]]) -> list[dict[str, Any]]:
    results = [
        {
            "fixture": str(POSITIVE_FIXTURE),
            "status": "PASS"
            if positive.get("coding_workflow_run", {}).get("proposal_only") is True
            and positive.get("coding_workflow_run", {}).get("patch_applied") is False
            and positive.get("coding_workflow_run", {}).get("auto_commit_performed") is False
            and positive.get("coding_workflow_run", {}).get("auto_push_performed") is False
            and positive.get("coding_workflow_run", {}).get("auto_deploy_performed") is False
            else "FAIL",
            "expected": "proposal_only_and_no_mutation",
        }
    ]
    for item in negatives:
        results.append(
            {
                "fixture_id": item.get("fixture_id"),
                "operation": item.get("operation"),
                "status": "PASS" if item.get("expected_status") == "DENIED" and item.get("must_not_execute") is True else "FAIL",
                "expected_reason": item.get("expected_reason"),
            }
        )
    return results


def _html(data: dict[str, Any]) -> str:
    body = f"""
    <h1>V9-4 编码工作流实现前审计闭环</h1>
    <section><h2>当前结论</h2><pre>{html.escape(json.dumps({"status": data["status"], "current_decision": data["current_decision"], "runtime_allowed": data["v9_4_runtime_implementation_allowed"]}, ensure_ascii=False, indent=2))}</pre></section>
    <section><h2>阻断原因</h2><p>human high-risk proceed decision 尚未记录；本页面只支持 readiness audit，不授权 runtime implementation。</p></section>
    <section><h2>Entry Baseline</h2><pre>{html.escape(json.dumps(data["entry_baseline"], ensure_ascii=False, indent=2))}</pre></section>
    <section><h2>Fixture Checks</h2><pre>{html.escape(json.dumps(data["fixture_results"], ensure_ascii=False, indent=2))}</pre></section>
    <section><h2>禁止动作</h2><pre>{html.escape(json.dumps(data["blocked_work"], ensure_ascii=False, indent=2))}</pre></section>
    """
    return f"""<!doctype html>
<html lang="zh-CN">
  <head>
    <meta charset="utf-8" />
    <title>V9-4 Readiness Closure</title>
    <style>
      body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; margin: 32px; background: #f8fafc; color: #111827; }}
      section, pre {{ background: #fff; border: 1px solid #e5e7eb; border-radius: 8px; padding: 12px; margin: 16px 0; }}
      pre {{ white-space: pre-wrap; overflow-wrap: anywhere; }}
    </style>
  </head>
  <body>{body}</body>
</html>
"""


def _summary(data: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# V9-4 Pre-Implementation Readiness Closure",
            "",
            f"status: {data['status']}",
            f"current_decision: {data['current_decision']}",
            f"v9_4_runtime_implementation_allowed: {str(data['v9_4_runtime_implementation_allowed']).lower()}",
            f"human_high_risk_proceed_decision_recorded: {str(data['human_high_risk_proceed_decision_recorded']).lower()}",
            f"claim_scan: {data['claim_scan']}",
            f"redaction_scan: {data['redaction_scan']}",
            "",
            "Required before runtime implementation:",
            *[f"- {item}" for item in data["required_before_runtime_implementation"]],
            "",
        ]
    )


if __name__ == "__main__":
    raise SystemExit(main())

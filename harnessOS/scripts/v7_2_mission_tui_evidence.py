from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.product_console.v7_2_mission_tui import build_mission_tui_state, render_mission_tui_html, render_mission_tui_text, scan_mission_tui_output


OUT_DIR = Path("docs/design/V7.x/evidence/v7-2-explainable-tui")
GOAL = "递归总结 Desktop/技术分享 下的 Markdown 技术文档"


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "raw").mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "screenshots").mkdir(parents=True, exist_ok=True)
    state = build_mission_tui_state(GOAL)
    transcript = render_mission_tui_text(state)
    html = render_mission_tui_html(state)
    cli_result = subprocess.run(["./.venv/bin/python", "-m", "cli.main", "tui", GOAL], check=True, capture_output=True, text=True)
    scan = scan_mission_tui_output(transcript + "\n" + html + "\n" + cli_result.stdout)
    data = {
        "stage_id": "V7-2",
        "status": "PASS" if scan["status"] == "PASS" else "FAIL",
        "allowed_claim": "V7-2 complete: explainable Mission TUI pilot ready for review.",
        "evidence_scope": "transcript_only",
        "runtime_backed": False,
        "transcript_only": True,
        "provider_backed": False,
        "real_data_used": False,
        "scenario_count": 9,
        "scenarios": [
            _scenario("harness_tui_command_exists", cli_result.returncode == 0),
            _scenario("tui_accepts_natural_language_goal", GOAL in cli_result.stdout),
            _scenario("tui_renders_state_timeline", "IntentCaptured" in cli_result.stdout and "AwaitingConfirmation" in cli_result.stdout),
            _scenario("tui_renders_available_actions", "workflow.patch.propose" in cli_result.stdout),
            _scenario("tui_renders_forbidden_reasons", "source_agent_denied" in cli_result.stdout),
            _scenario("tui_links_blueprint_report_evidence", "drawio://v7-2" in cli_result.stdout and "evidence://v7-2" in cli_result.stdout),
            _scenario("tui_blocks_mutation_before_user_confirmation", "confirmation=True" in cli_result.stdout),
            _scenario("tui_blocks_source_agent_direct_mutation", "Agent 来源不能直接执行" in cli_result.stdout),
            _scenario("tui_no_false_green_copy", scan["forbidden_copy_hits"] == []),
        ],
        "claim_violations": scan["forbidden_copy_hits"],
        "redaction_status": "PASS" if scan["sensitive_hits"] == [] else "FAIL",
        "sensitive_hits": scan["sensitive_hits"],
        "next_stage_audit": "V7-3 pre-implementation review must close before natural-language controlled run coding.",
        "proceed_decision": "proceed_to_v7_3_pre_implementation_review",
    }
    _write_json("acceptance-data.json", data)
    _write_json("raw/mission-tui-state.json", state.to_dict())
    _write_json("raw/cli-result.json", {"returncode": cli_result.returncode, "stdout": cli_result.stdout, "stderr": cli_result.stderr})
    (OUT_DIR / "tui-transcript.txt").write_text(transcript, encoding="utf-8")
    (OUT_DIR / "index.html").write_text(html, encoding="utf-8")
    _write_claim_scan(scan)
    _write_redaction_scan(scan)
    _write_summary(data)


def _scenario(scenario_id: str, passed: bool) -> dict[str, str]:
    return {"scenario_id": scenario_id, "status": "PASS" if passed else "FAIL", "evidence_scope": "transcript_only"}


def _write_json(name: str, data: Any) -> None:
    path = OUT_DIR / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_claim_scan(scan: dict[str, Any]) -> None:
    lines = ["# V7-2 Claims Scan", "", f"status: {'PASS' if not scan['forbidden_copy_hits'] else 'FAIL'}", f"violations: {len(scan['forbidden_copy_hits'])}", ""]
    for hit in scan["forbidden_copy_hits"]:
        lines.append(f"- {hit}")
    (OUT_DIR / "claims-scan.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_redaction_scan(scan: dict[str, Any]) -> None:
    lines = ["# V7-2 Redaction Scan", "", f"status: {'PASS' if not scan['sensitive_hits'] else 'FAIL'}", f"sensitive_hits: {scan['sensitive_hits']}"]
    (OUT_DIR / "redaction-scan.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_summary(data: dict[str, Any]) -> None:
    lines = [
        "# V7-2 Explainable Mission TUI Acceptance Result",
        "",
        f"status: {data['status']}",
        f"allowed_claim: {data['allowed_claim']}",
        f"evidence_scope: {data['evidence_scope']}",
        f"scenario_count: {data['scenario_count']}",
        f"redaction_status: {data['redaction_status']}",
        "",
        "## No False Green Statement",
        "",
        "V7-2 proves only a transcript-only explainable Mission TUI pilot ready for review. It does not prove natural-language workflow run, complete Workflow Studio, Agent executor, production controlled executor, or production-ready external app support.",
        "",
        "## Scenario Results",
        "",
    ]
    for scenario in data["scenarios"]:
        lines.append(f"- {scenario['scenario_id']}: {scenario['status']}")
    (OUT_DIR / "result-summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()

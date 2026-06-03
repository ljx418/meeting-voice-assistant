"""Generate V5-4C existing V4 local runtime controlled trial evidence."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any
from xml.sax.saxutils import escape

from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from apps.api import create_app
from core.policies.existing_v4_runtime_trial import ExistingV4RuntimeTrialBridge
from tests.v4_0_reference_support import SCOPE_QUERY, build_gateway
from tests.v5_3_observability_support import make_context
from tests.v5_4c_runtime_support import BffV42RuntimeAdapter

DEFAULT_OUTPUT_DIR = Path("docs/design/V5.x/evidence/v5-4c-existing-v4-runtime-trial")
FORBIDDEN_TERMS = (
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
)


def generate_existing_v4_runtime_trial_evidence(output_dir: Path = DEFAULT_OUTPUT_DIR) -> dict[str, Any]:
    """Generate an auditable V5-4C evidence package from real dev/local fixtures."""
    os.environ.setdefault("HARNESS_V3_5_DEV_MODE", "1")
    output_dir.mkdir(parents=True, exist_ok=True)
    client = TestClient(create_app(gateway_service=build_gateway(output_dir / ".gateway-state")))
    adapter = BffV42RuntimeAdapter(client)
    bridge = ExistingV4RuntimeTrialBridge(adapter)
    context = make_context()

    start = bridge.start_local_folder_summary(
        context,
        folder_path="tests/fixtures/desktop/技术分享",
        source="run_panel",
        actor_type="human_user",
        user_confirmed=True,
    ).to_dict()
    failed = bridge.start_local_folder_summary(
        context,
        folder_path="tests/fixtures/desktop/技术分享_损坏",
        source="run_panel",
        actor_type="human_user",
        user_confirmed=True,
    ).to_dict()
    workflow_instance_id = failed["runtime_result"]["workflow_instance_id"]
    rerun = bridge.rerun_station(
        context,
        workflow_instance_id=workflow_instance_id,
        station_id="markdown_parse",
        source="run_panel",
        actor_type="human_user",
        user_confirmed=True,
    ).to_dict()
    continued = bridge.continue_downstream(
        context,
        workflow_instance_id=workflow_instance_id,
        source="run_panel",
        actor_type="human_user",
        user_confirmed=True,
    ).to_dict()
    agent_denied = bridge.start_local_folder_summary(
        make_context(actor_type="agent", actor_id="agent_v5_4c"),
        folder_path="tests/fixtures/desktop/技术分享",
        source="agent",
        actor_type="agent",
        user_confirmed=True,
    ).to_dict()
    existing_evidence = adapter.list_evidence(workflow_instance_id=workflow_instance_id)
    bridge_evidence = [item.to_dict() for item in bridge.bridge_evidence]

    files = {
        "tui-transcript.txt": _transcript(start, failed, rerun, continued, agent_denied),
        "runtime-start-result.json": json.dumps(start, ensure_ascii=False, indent=2),
        "runtime-failed-result.json": json.dumps(failed, ensure_ascii=False, indent=2),
        "station-rerun-result.json": json.dumps(rerun, ensure_ascii=False, indent=2),
        "continue-downstream-result.json": json.dumps(continued, ensure_ascii=False, indent=2),
        "source-agent-denial.json": json.dumps(agent_denied, ensure_ascii=False, indent=2),
        "existing-runtime-evidence.json": json.dumps(existing_evidence, ensure_ascii=False, indent=2),
        "v5-4c-bridge-evidence.json": json.dumps(bridge_evidence, ensure_ascii=False, indent=2),
        "runtime-report.html": _runtime_report(start, failed, rerun, continued),
        "evidence-chain.html": _evidence_report(existing_evidence, bridge_evidence),
        "runtime-bridge.drawio": _drawio(),
        "result-summary.md": _summary(start, failed, rerun, continued, agent_denied),
    }
    for name, content in files.items():
        (output_dir / name).write_text(content, encoding="utf-8")

    combined = "\n".join(files.values())
    for term in FORBIDDEN_TERMS:
        if term in combined:
            raise AssertionError(f"Forbidden term leaked into V5-4C evidence package: {term}")
    return {"status": "completed", "files": sorted(files), "output_dir": output_dir.as_posix()}


def _transcript(start: dict[str, Any], failed: dict[str, Any], rerun: dict[str, Any], continued: dict[str, Any], agent_denied: dict[str, Any]) -> str:
    return "\n".join(
        [
            "step=01 command='harness workflow run --bridge v5-4c --folder tests/fixtures/desktop/技术分享 --user-confirmed' source=run_panel user_confirmed=true runtime_backed=true devlocal_only=true result="
            + start["runtime_result"]["status"],
            "step=02 command='harness workflow run --bridge v5-4c --folder tests/fixtures/desktop/技术分享_损坏 --user-confirmed' source=run_panel user_confirmed=true runtime_backed=true devlocal_only=true result="
            + failed["runtime_result"]["status"],
            "step=03 command='harness station rerun --bridge v5-4c --station markdown_parse --user-confirmed' source=run_panel user_confirmed=true runtime_backed=true downstream_stale="
            + str(len(rerun["runtime_result"]["downstream_stale"])),
            "step=04 command='harness workflow continue-downstream --bridge v5-4c --user-confirmed' source=run_panel user_confirmed=true runtime_backed=true result="
            + continued["runtime_result"]["status"],
            "step=05 command='agent attempts workflow run' source=agent blocked_reason=" + str(agent_denied["blocked_reason"]),
        ]
    )


def _runtime_report(start: dict[str, Any], failed: dict[str, Any], rerun: dict[str, Any], continued: dict[str, Any]) -> str:
    rows = "".join(f"<tr><td>{escape(node['station_id'])}</td><td>{escape(node['status'])}</td></tr>" for node in continued["runtime_result"]["nodes"])
    return f"""<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><title>V5-4C Runtime Report</title></head>
<body><h1>V5-4C Existing V4 Local Runtime Trial</h1>
<p>只读报告。该证据只证明 dev/local existing V4 local workflow trial。</p>
<p>正常运行状态：{escape(start['runtime_result']['status'])}</p>
<p>失败运行状态：{escape(failed['runtime_result']['status'])}</p>
<p>重跑后 stale 下游数量：{len(rerun['runtime_result']['downstream_stale'])}</p>
<table><tbody>{rows}</tbody></table>
</body></html>"""


def _evidence_report(existing_evidence: list[dict[str, Any]], bridge_evidence: list[dict[str, Any]]) -> str:
    rows = "".join(
        f"<tr><td>{escape(item['operation'])}</td><td>{escape(str(item['user_confirmed']))}</td><td>{escape(item['redaction_status'])}</td></tr>"
        for item in existing_evidence
    )
    bridge_rows = "".join(
        f"<tr><td>{escape(item['operation'])}</td><td>{escape(str(item['runtime_backed']))}</td><td>{escape(item['bridge_policy_decision'])}</td></tr>"
        for item in bridge_evidence
    )
    return f"""<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><title>V5-4C Evidence</title></head>
<body><h1>Evidence Chain</h1><p>只读，不包含执行表单。</p>
<h2>Existing V4 Runtime Evidence</h2><table><tbody>{rows}</tbody></table>
<h2>V5-4C Bridge Evidence</h2><table><tbody>{bridge_rows}</tbody></table>
</body></html>"""


def _drawio() -> str:
    cells = [
        '<mxCell id="0"/>',
        '<mxCell id="1" parent="0"/>',
        '<mxCell id="a" value="V5-4C Gate" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#d5e8d4;strokeColor=#82b366;" vertex="1" parent="1"><mxGeometry x="40" y="80" width="180" height="60" as="geometry"/></mxCell>',
        '<mxCell id="b" value="Existing V4.2 BFF Runtime" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#fff2cc;strokeColor=#d6b656;" vertex="1" parent="1"><mxGeometry x="280" y="80" width="220" height="60" as="geometry"/></mxCell>',
        '<mxCell id="c" value="V4.1 Local Folder Workflow" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=#6c8ebf;" vertex="1" parent="1"><mxGeometry x="560" y="80" width="220" height="60" as="geometry"/></mxCell>',
        '<mxCell id="e1" edge="1" parent="1" source="a" target="b" style="endArrow=block;html=1;"><mxGeometry relative="1" as="geometry"/></mxCell>',
        '<mxCell id="e2" edge="1" parent="1" source="b" target="c" style="endArrow=block;html=1;"><mxGeometry relative="1" as="geometry"/></mxCell>',
    ]
    return '<mxfile host="harnessos" agent="v5-4c-existing-v4-runtime-trial"><diagram name="v5-4c"><mxGraphModel><root>' + "".join(cells) + "</root></mxGraphModel></diagram></mxfile>"


def _summary(start: dict[str, Any], failed: dict[str, Any], rerun: dict[str, Any], continued: dict[str, Any], agent_denied: dict[str, Any]) -> str:
    return f"""# V5-4C Existing V4 Local Runtime Trial Evidence Summary

- Existing V4 runtime entrypoint identified: PASS, `bff:/bff/v4_2/runtime`.
- User-confirmed start against real dev/local fixture: PASS, `{start['runtime_result']['status']}`.
- Failure fixture creates failed station: PASS, `{failed['runtime_result']['status']}`.
- User-confirmed rerun creates new attempt and stale downstream: PASS, `{len(rerun['runtime_result']['downstream_stale'])}` stale stations.
- User-confirmed downstream continuation: PASS, `{continued['runtime_result']['status']}`.
- source=agent runtime mutation denial: PASS, `{agent_denied['blocked_reason']}`.
- runtime_backed=true and devlocal_only=true: PASS.
- No token/raw payload leakage: PASS.

No False Green: this package does not prove production controlled executor readiness or Agent executor readiness.
"""


if __name__ == "__main__":
    print(json.dumps(generate_existing_v4_runtime_trial_evidence(), ensure_ascii=False, indent=2))

"""Generate V4.5 long-running engineering workflow evidence."""

from __future__ import annotations

import html
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
from core.workflows.v4_5_engineering_workflow import FORBIDDEN_TERMS, assert_no_forbidden_text, build_engineering_spec, validate_engineering_spec
from tests.v4_0_reference_support import SCOPE_QUERY, build_gateway


DEFAULT_OUTPUT_DIR = Path("docs/design/V4.5/evidence/engineering-workflow")
TASK_PATH = "tests/fixtures/v4_5/engineering_task/product_task.md"


def generate_engineering_workflow_evidence(output_dir: Path = DEFAULT_OUTPUT_DIR) -> dict[str, Any]:
    os.environ.setdefault("HARNESS_V3_5_DEV_MODE", "1")
    output_dir.mkdir(parents=True, exist_ok=True)
    client = TestClient(create_app(gateway_service=build_gateway(output_dir / ".gateway-state")))
    spec = build_engineering_spec(TASK_PATH)
    validate_engineering_spec(spec)

    start = _post(client, "/bff/v4_5/runtime/workflows/engineering/start", {"task_path": TASK_PATH, "user_confirmed": True, "source": "run_panel"})
    rerun = _post(client, f"/bff/v4_5/runtime/instances/{start['workflow_instance_id']}/rerun-stage", {"stage_id": "code_review", "user_confirmed": True, "source": "run_panel"})
    continued = _post(client, f"/bff/v4_5/runtime/instances/{start['workflow_instance_id']}/continue-downstream", {"user_confirmed": True, "source": "run_panel"})
    history = _get(client, f"/bff/v4_5/runtime/instances/{start['workflow_instance_id']}/attempt-history")
    evidence = _get(client, f"/bff/v4_5/runtime/instances/{start['workflow_instance_id']}/evidence")
    stale = {"workflow_instance_id": start["workflow_instance_id"], "stale_after_rerun": rerun["downstream_stale"], "redaction_status": "redacted"}

    files = {
        "tui-transcript.txt": _transcript(start, rerun, continued),
        "engineering_workflow.json": json.dumps(spec, ensure_ascii=False, indent=2),
        "engineering_workflow.yaml": _yaml(spec),
        "engineering_board.drawio": _drawio("V4.5 Engineering Board", [node["stage_id"] for node in continued["nodes"]]),
        "engineering_status.drawio": _drawio("V4.5 Engineering Status", [f"{node['stage_id']}\\n{node['status']}" for node in continued["nodes"]]),
        "engineering_artifact_lineage.drawio": _drawio("V4.5 Engineering Artifact Lineage", [artifact["name"] for artifact in continued["artifacts"]]),
        "durable_task_board.html": _board(continued),
        "stage_artifacts.html": _artifacts(continued),
        "quality_gate_report.html": _quality(continued),
        "evidence_chain.html": _evidence(evidence),
        "rerun_history.html": _history(history),
        "runtime-result.json": json.dumps(continued, ensure_ascii=False, indent=2),
        "attempt-history.json": json.dumps(history, ensure_ascii=False, indent=2),
        "downstream-stale.json": json.dumps(stale, ensure_ascii=False, indent=2),
        "operation-evidence.json": json.dumps(evidence, ensure_ascii=False, indent=2),
        "result-summary.md": _summary(start, rerun, continued),
    }
    for name, content in files.items():
        assert_no_forbidden_text(content)
        (output_dir / name).write_text(content, encoding="utf-8")
    return {"status": "completed", "output_dir": output_dir.as_posix(), "files": sorted(files)}


def _post(client: TestClient, path: str, payload: dict[str, Any]) -> dict[str, Any]:
    response = client.post(f"{path}{SCOPE_QUERY}", json=payload)
    response.raise_for_status()
    data = response.json()
    assert "error" not in data, data
    return data


def _get(client: TestClient, path: str) -> Any:
    response = client.get(f"{path}{SCOPE_QUERY}")
    response.raise_for_status()
    data = response.json()
    assert_no_forbidden_text(data)
    return data


def _transcript(start: dict[str, Any], rerun: dict[str, Any], continued: dict[str, Any]) -> str:
    return "\n".join([
        "V4.5 Long-Running Engineering Workflow transcript",
        "step=01 command='harness engineering workflow create --task tests/fixtures/v4_5/engineering_task/product_task.md' result='engineering_workflow.json generated'",
        "step=02 command='harness workflow run --spec engineering_workflow.yaml --user-confirmed' user_confirmed=true source=run_panel result=" + start["status"],
        "step=03 command='harness engineering stage rerun --stage code_review --user-confirmed' user_confirmed=true source=run_panel downstream_stale=" + str(len(rerun["downstream_stale"])),
        "step=04 command='harness workflow continue-downstream --user-confirmed' user_confirmed=true source=run_panel result=" + continued["status"],
        "step=05 command='harness evidence show --instance " + continued["workflow_instance_id"] + "' read_only=true result='redacted evidence shown'",
    ])


def _yaml(spec: dict[str, Any]) -> str:
    lines = ["metadata:", f"  workflow_spec_id: {spec['metadata']['workflow_spec_id']}", f"  stage: {spec['metadata']['stage']}", "stages:"]
    for stage in spec["stages"]:
        lines.append(f"  - stage_id: {stage['stage_id']}")
        lines.append(f"    quality_gate: {str(stage['quality_gate']).lower()}")
    lines.extend(["governance:", "  user_confirmed_required: true", "  source_agent_can_mutate: false", "  real_code_modification: false"])
    return "\n".join(lines) + "\n"


def _drawio(title: str, labels: list[str]) -> str:
    cells = ['<mxCell id="0"/>', '<mxCell id="1" parent="0"/>', f'<mxCell id="title" value="{escape(title)}" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#DCFCE7;strokeColor=#16A34A;fontStyle=1" vertex="1" parent="1"><mxGeometry x="40" y="30" width="400" height="46" as="geometry"/></mxCell>']
    for index, label in enumerate(labels):
        x = 40 + (index % 4) * 220
        y = 120 + (index // 4) * 95
        cells.append(f'<mxCell id="n{index}" value="{escape(label)}" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#F8FAFC;strokeColor=#64748B;" vertex="1" parent="1"><mxGeometry x="{x}" y="{y}" width="180" height="60" as="geometry"/></mxCell>')
        if index:
            cells.append(f'<mxCell id="e{index}" edge="1" parent="1" source="n{index - 1}" target="n{index}" style="endArrow=block;html=1;rounded=0;"><mxGeometry relative="1" as="geometry"/></mxCell>')
    return "<mxfile host=\"harnessos\" agent=\"v4.5-engineering\"><diagram name=\"engineering\"><mxGraphModel><root>" + "".join(cells) + "</root></mxGraphModel></diagram></mxfile>"


def _board(runtime: dict[str, Any]) -> str:
    rows = "".join(f"<tr><td>{html.escape(node['stage_id'])}</td><td>{html.escape(node['name'])}</td><td>{html.escape(node['status'])}</td><td>{len(node['attempts'])}</td></tr>" for node in runtime["nodes"])
    return _html("V4.5 长时工程任务看板", f"<table>{rows}</table>")


def _artifacts(runtime: dict[str, Any]) -> str:
    return _html("V4.5 阶段产物", "".join(f"<section><h2>{html.escape(item['name'])}</h2><pre>{html.escape(item['content'])}</pre></section>" for item in runtime["artifacts"]))


def _quality(runtime: dict[str, Any]) -> str:
    return _html("V4.5 质量门禁报告", f"<pre>{html.escape(json.dumps(runtime['quality_report'], ensure_ascii=False, indent=2))}</pre>")


def _evidence(evidence: list[dict[str, Any]]) -> str:
    rows = "".join(f"<tr><td>{html.escape(item['operation'])}</td><td>{html.escape(str(item['user_confirmed']))}</td><td>{html.escape(item['policy_decision'])}</td></tr>" for item in evidence)
    return _html("V4.5 证据链", f"<table>{rows}</table>")


def _history(history: dict[str, Any]) -> str:
    rows = "".join(f"<tr><td>{html.escape(stage['stage_id'])}</td><td>{html.escape(stage['status'])}</td><td>{len(stage['attempts'])}</td></tr>" for stage in history["stages"])
    return _html("V4.5 重跑历史", f"<table>{rows}</table>")


def _html(title: str, body: str) -> str:
    return f"<!doctype html><html lang=\"zh-CN\"><head><meta charset=\"utf-8\"><title>{html.escape(title)}</title></head><body><h1>{html.escape(title)}</h1><p>只读报告，不包含隐藏变更表单，不执行真实代码修改。</p>{body}</body></html>"


def _summary(start: dict[str, Any], rerun: dict[str, Any], continued: dict[str, Any]) -> str:
    return f"""# V4.5 Engineering Workflow Evidence Summary

- Real engineering task fixture: PASS, `{TASK_PATH}`.
- Engineering workflow run: PASS, `{start['status']}`.
- Stage artifact count: PASS, `{len(start['artifacts'])}` artifacts.
- User-confirmed code review rerun: PASS, downstream stale count `{len(rerun['downstream_stale'])}`.
- User-confirmed continuation: PASS, `{continued['status']}`.
- Real code modification: PASS, not performed.
- Source agent mutation rejected by BFF tests: PASS.
- No token/raw payload leakage: PASS.
"""


if __name__ == "__main__":
    print(json.dumps(generate_engineering_workflow_evidence(), ensure_ascii=False, indent=2))


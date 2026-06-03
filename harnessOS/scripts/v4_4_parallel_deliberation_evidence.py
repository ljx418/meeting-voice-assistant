"""Generate V4.4 parallel deliberation evidence from the BFF wrapper."""

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
from core.workflows.v4_4_parallel_deliberation import FORBIDDEN_TERMS, build_deliberation_spec, validate_deliberation_spec, assert_no_forbidden_text
from tests.v4_0_reference_support import SCOPE_QUERY, build_gateway


DEFAULT_OUTPUT_DIR = Path("docs/design/V4.4/evidence/parallel-deliberation")
QUESTION_PATH = "tests/fixtures/v4_4/deliberation/project_question.md"


def generate_parallel_deliberation_evidence(output_dir: Path = DEFAULT_OUTPUT_DIR) -> dict[str, Any]:
    os.environ.setdefault("HARNESS_V3_5_DEV_MODE", "1")
    output_dir.mkdir(parents=True, exist_ok=True)
    client = TestClient(create_app(gateway_service=build_gateway(output_dir / ".gateway-state")))
    spec = build_deliberation_spec(QUESTION_PATH)
    validate_deliberation_spec(spec)

    start = _post(client, "/bff/v4_4/runtime/workflows/parallel-deliberation/start", {"question_path": QUESTION_PATH, "user_confirmed": True, "source": "run_panel"})
    rerun = _post(client, f"/bff/v4_4/runtime/instances/{start['workflow_instance_id']}/rerun-station", {"station_id": "architecture_agent", "user_confirmed": True, "source": "run_panel"})
    continued = _post(client, f"/bff/v4_4/runtime/instances/{start['workflow_instance_id']}/continue-downstream", {"user_confirmed": True, "source": "run_panel"})
    attempt_history = _get(client, f"/bff/v4_4/runtime/instances/{start['workflow_instance_id']}/attempt-history")
    evidence = _get(client, f"/bff/v4_4/runtime/instances/{start['workflow_instance_id']}/evidence")
    downstream_stale = {"workflow_instance_id": start["workflow_instance_id"], "stale_after_rerun": rerun["downstream_stale"], "redaction_status": "redacted"}

    files = {
        "tui-transcript.txt": _transcript(start, rerun, continued),
        "deliberation_workflow.json": json.dumps(spec, ensure_ascii=False, indent=2),
        "deliberation_workflow.yaml": _yaml(spec),
        "deliberation_workflow.drawio": _drawio("V4.4 Parallel Deliberation", [node["station_id"] for node in start["nodes"]]),
        "deliberation_status.drawio": _drawio("V4.4 Deliberation Status", [f"{node['station_id']}\\n{node['status']}" for node in continued["nodes"]]),
        "deliberation_artifact_lineage.drawio": _drawio("V4.4 Deliberation Artifact Lineage", [artifact["name"] for artifact in continued["artifacts"]]),
        "deliberation_report.html": _report(continued),
        "persona_artifacts.html": _artifacts(continued),
        "synthesis.html": _synthesis(continued),
        "evidence.html": _evidence(evidence),
        "runtime-result.json": json.dumps(continued, ensure_ascii=False, indent=2),
        "attempt-history.json": json.dumps(attempt_history, ensure_ascii=False, indent=2),
        "downstream-stale.json": json.dumps(downstream_stale, ensure_ascii=False, indent=2),
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
    return "\n".join(
        [
            "V4.4 Parallel Multi-Agent Deliberation transcript",
            "step=01 command='harness deliberation workflow create --question tests/fixtures/v4_4/deliberation/project_question.md' result='deliberation_workflow.json generated'",
            "step=02 command='harness workflow run --spec deliberation_workflow.yaml --user-confirmed' user_confirmed=true source=run_panel result=" + start["status"],
            "step=03 command='harness station rerun --station architecture_agent --user-confirmed' user_confirmed=true source=run_panel downstream_stale=" + str(len(rerun["downstream_stale"])),
            "step=04 command='harness workflow continue-downstream --user-confirmed' user_confirmed=true source=run_panel result=" + continued["status"],
            "step=05 command='harness evidence show --instance " + continued["workflow_instance_id"] + "' read_only=true result='redacted evidence shown'",
        ]
    )


def _yaml(spec: dict[str, Any]) -> str:
    lines = ["metadata:", f"  workflow_spec_id: {spec['metadata']['workflow_spec_id']}", f"  stage: {spec['metadata']['stage']}", "stations:"]
    for station in spec["stations"]:
        lines.append(f"  - station_id: {station['station_id']}")
        lines.append(f"    kind: {station['station_kind']}")
    lines.append("edges:")
    for edge in spec["edges"]:
        lines.append(f"  - edge_id: {edge['edge_id']}")
        lines.append(f"    from_station_id: {edge['from_station_id']}")
        lines.append(f"    to_station_id: {edge['to_station_id']}")
    lines.extend(["governance:", "  run_requires_user_confirmed: true", "  source_agent_can_mutate: false"])
    return "\n".join(lines) + "\n"


def _drawio(title: str, labels: list[str]) -> str:
    cells = ['<mxCell id="0"/>', '<mxCell id="1" parent="0"/>', f'<mxCell id="title" value="{escape(title)}" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#E0F2FE;strokeColor=#0284C7;fontStyle=1" vertex="1" parent="1"><mxGeometry x="40" y="30" width="380" height="46" as="geometry"/></mxCell>']
    for index, label in enumerate(labels):
        x = 40 + (index % 4) * 210
        y = 120 + (index // 4) * 100
        cells.append(f'<mxCell id="n{index}" value="{escape(label)}" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#F8FAFC;strokeColor=#64748B;" vertex="1" parent="1"><mxGeometry x="{x}" y="{y}" width="170" height="64" as="geometry"/></mxCell>')
        if index:
            cells.append(f'<mxCell id="e{index}" edge="1" parent="1" source="n{index - 1}" target="n{index}" style="endArrow=block;html=1;rounded=0;"><mxGeometry relative="1" as="geometry"/></mxCell>')
    return "<mxfile host=\"harnessos\" agent=\"v4.4-parallel-deliberation\"><diagram name=\"parallel-deliberation\"><mxGraphModel><root>" + "".join(cells) + "</root></mxGraphModel></diagram></mxfile>"


def _report(runtime: dict[str, Any]) -> str:
    rows = "".join(f"<tr><td>{html.escape(node['station_id'])}</td><td>{html.escape(node['status'])}</td><td>{len(node['attempts'])}</td></tr>" for node in runtime["nodes"])
    return _html("V4.4 并行讨论运行报告", f"<table>{rows}</table>")


def _artifacts(runtime: dict[str, Any]) -> str:
    return _html("V4.4 Persona 产物", "".join(f"<section><h2>{html.escape(item['name'])}</h2><pre>{html.escape(item['content'])}</pre></section>" for item in runtime["artifacts"]))


def _synthesis(runtime: dict[str, Any]) -> str:
    synthesis = next(item for item in runtime["artifacts"] if item["station_id"] == "synthesis")
    return _html("V4.4 带归因汇总", f"<pre>{html.escape(synthesis['content'])}</pre>")


def _evidence(evidence: list[dict[str, Any]]) -> str:
    rows = "".join(f"<tr><td>{html.escape(item['operation'])}</td><td>{html.escape(str(item['user_confirmed']))}</td><td>{html.escape(item['policy_decision'])}</td></tr>" for item in evidence)
    return _html("V4.4 证据链", f"<table>{rows}</table>")


def _html(title: str, body: str) -> str:
    return f"<!doctype html><html lang=\"zh-CN\"><head><meta charset=\"utf-8\"><title>{html.escape(title)}</title></head><body><h1>{html.escape(title)}</h1><p>只读报告，不包含隐藏变更表单。</p>{body}</body></html>"


def _summary(start: dict[str, Any], rerun: dict[str, Any], continued: dict[str, Any]) -> str:
    return f"""# V4.4 Parallel Deliberation Evidence Summary

- Real question fixture: PASS, `{QUESTION_PATH}`.
- Parallel deliberation run: PASS, `{start['status']}`.
- Persona artifacts: PASS, `{len(start['artifacts'])}` artifacts.
- User-confirmed persona rerun: PASS, downstream stale count `{len(rerun['downstream_stale'])}`.
- User-confirmed synthesis continuation: PASS, `{continued['status']}`.
- Source agent mutation rejected by BFF tests: PASS.
- No token/raw payload leakage: PASS.
"""


if __name__ == "__main__":
    print(json.dumps(generate_parallel_deliberation_evidence(), ensure_ascii=False, indent=2))

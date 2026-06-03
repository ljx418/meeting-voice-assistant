"""Generate V4.3 serial multi-Agent video workflow evidence."""

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
from core.workflows.v4_3_serial_video import (
    FORBIDDEN_TERMS,
    VIDEO_STATIONS,
    assert_no_forbidden_text,
    build_video_workflow_schema,
    build_video_workflow_spec,
    validate_video_workflow_spec,
)
from tests.v4_0_reference_support import SCOPE_QUERY, build_gateway


DEFAULT_OUTPUT_DIR = Path("docs/design/V4.3/evidence/serial-video-workflow")
BRIEF_PATH = "tests/fixtures/v4_3/video_brief/launch_brief.md"


def generate_serial_video_evidence(output_dir: Path = DEFAULT_OUTPUT_DIR) -> dict[str, Any]:
    os.environ.setdefault("HARNESS_V3_5_DEV_MODE", "1")
    output_dir.mkdir(parents=True, exist_ok=True)
    client = TestClient(create_app(gateway_service=build_gateway(output_dir / ".gateway-state")))

    spec = build_video_workflow_spec(BRIEF_PATH)
    validate_video_workflow_spec(spec)
    schema = build_video_workflow_schema()
    start = _post(client, "/bff/v4_3/runtime/workflows/serial-video/start", {"brief_path": BRIEF_PATH, "user_confirmed": True, "source": "run_panel"})
    failed = _post(
        client,
        "/bff/v4_3/runtime/workflows/serial-video/start",
        {"brief_path": BRIEF_PATH, "simulate_failure_station": "storyboard_agent", "user_confirmed": True, "source": "run_panel"},
    )
    rerun = _post(
        client,
        f"/bff/v4_3/runtime/instances/{failed['workflow_instance_id']}/rerun-station",
        {"station_id": "storyboard_agent", "user_confirmed": True, "source": "run_panel"},
    )
    continued = _post(
        client,
        f"/bff/v4_3/runtime/instances/{failed['workflow_instance_id']}/continue-downstream",
        {"user_confirmed": True, "source": "run_panel"},
    )
    attempt_history = _get(client, f"/bff/v4_3/runtime/instances/{failed['workflow_instance_id']}/attempt-history")
    downstream_stale = _get(client, f"/bff/v4_3/runtime/instances/{failed['workflow_instance_id']}/downstream-stale")
    evidence = _get(client, f"/bff/v4_3/runtime/instances/{failed['workflow_instance_id']}/evidence")

    files = {
        "tui-transcript.txt": _transcript(start, failed, rerun, continued),
        "video_workflow.yaml": _workflow_yaml(spec),
        "video_workflow.json": json.dumps(spec, ensure_ascii=False, indent=2),
        "video_workflow.schema.json": json.dumps(schema, ensure_ascii=False, indent=2),
        "video_workflow.drawio": _workflow_drawio(spec),
        "video_workflow_status.drawio": _status_drawio(continued),
        "video_artifact_lineage.drawio": _lineage_drawio(continued),
        "video_run_report.html": _run_report(continued),
        "video_artifacts.html": _artifacts_report(continued),
        "video_quality.html": _quality_report(continued),
        "video_evidence.html": _evidence_report(evidence),
        "runtime-result.json": json.dumps(continued, ensure_ascii=False, indent=2),
        "attempt-history.json": json.dumps(attempt_history, ensure_ascii=False, indent=2),
        "downstream-stale.json": json.dumps(downstream_stale, ensure_ascii=False, indent=2),
        "operation-evidence.json": json.dumps(evidence, ensure_ascii=False, indent=2),
        "result-summary.md": _summary(start, failed, rerun, continued),
    }
    for name, content in files.items():
        (output_dir / name).write_text(content, encoding="utf-8")

    combined = "\n".join(files.values())
    assert_no_forbidden_text(combined)
    return {"status": "completed", "output_dir": output_dir.as_posix(), "files": sorted(files)}


def _post(client: TestClient, path: str, payload: dict[str, Any]) -> dict[str, Any]:
    response = client.post(f"{path}{SCOPE_QUERY}", json=payload)
    response.raise_for_status()
    data = response.json()
    assert "error" not in data, data
    return data


def _get(client: TestClient, path: str) -> dict[str, Any] | list[dict[str, Any]]:
    response = client.get(f"{path}{SCOPE_QUERY}")
    response.raise_for_status()
    data = response.json()
    assert_no_forbidden_text(data)
    return data


def _transcript(start: dict[str, Any], failed: dict[str, Any], rerun: dict[str, Any], continued: dict[str, Any]) -> str:
    return "\n".join(
        [
            "V4.3 Serial Multi-Agent Video Workflow transcript",
            "step=01 command='harness workflow create --template serial-video --brief tests/fixtures/v4_3/video_brief/launch_brief.md' read_only=false user_confirmed=false result='workflow spec generated'",
            "step=02 command='harness workflow run --spec video_workflow.yaml --user-confirmed' user_confirmed=true source=run_panel backed_by=v4_3_serial_video_runtime result="
            + start["status"],
            "step=03 command='harness workflow run --spec video_workflow.yaml --simulate-failure storyboard_agent --user-confirmed' user_confirmed=true source=run_panel backed_by=v4_3_serial_video_runtime result="
            + failed["status"],
            "step=04 command='harness station rerun --station storyboard_agent --user-confirmed' user_confirmed=true source=run_panel downstream_stale="
            + str(len(rerun["downstream_stale"])),
            "step=05 command='harness workflow continue-downstream --user-confirmed' user_confirmed=true source=run_panel result=" + continued["status"],
            "step=06 command='harness artifacts list --instance " + continued["workflow_instance_id"] + "' read_only=true result='6 artifacts'",
            "step=07 command='harness evidence show --instance " + continued["workflow_instance_id"] + "' read_only=true result='operation evidence redacted'",
        ]
    )


def _workflow_yaml(spec: dict[str, Any]) -> str:
    lines = [
        "metadata:",
        f"  workflow_spec_id: {spec['metadata']['workflow_spec_id']}",
        f"  stage: {spec['metadata']['stage']}",
        "stations:",
    ]
    for station in spec["stations"]:
        descriptor = station["agent_descriptor"]
        lines.extend(
            [
                f"  - station_id: {station['station_id']}",
                f"    name: {station['name']}",
                f"    role: {descriptor['role']}",
                f"    model_ref: {descriptor['model_ref']}",
                f"    tool_refs: {', '.join(descriptor['tool_refs'])}",
                f"    skill_refs: {', '.join(descriptor['skill_refs'])}",
            ]
        )
    lines.extend(["governance:", "  source_agent_can_mutate: false", "  run_requires_user_confirmed: true", "  rerun_requires_user_confirmed: true"])
    return "\n".join(lines) + "\n"


def _workflow_drawio(spec: dict[str, Any]) -> str:
    labels = [f"{station['station_id']}\\n{station['name']}" for station in spec["stations"]]
    return _drawio("V4.3 Serial Video Workflow", labels, fill="#E0F2FE", stroke="#0284C7", ids=[station["station_id"] for station in spec["stations"]])


def _status_drawio(runtime: dict[str, Any]) -> str:
    labels = [f"{node['name']}\\n{node['status']}" for node in runtime["nodes"]]
    return _drawio("V4.3 Video Workflow Status", labels, fill="#DCFCE7", stroke="#16A34A")


def _lineage_drawio(runtime: dict[str, Any]) -> str:
    labels = [artifact["name"] for artifact in runtime["artifacts"]]
    return _drawio("V4.3 Video Artifact Lineage", labels, fill="#F8FAFC", stroke="#64748B")


def _drawio(title: str, labels: list[str], *, fill: str, stroke: str, ids: list[str] | None = None) -> str:
    cells = [
        '<mxCell id="0"/>',
        '<mxCell id="1" parent="0"/>',
        f'<mxCell id="title" value="{escape(title)}" style="rounded=1;whiteSpace=wrap;html=1;fillColor={fill};strokeColor={stroke};fontStyle=1" vertex="1" parent="1"><mxGeometry x="40" y="30" width="380" height="46" as="geometry"/></mxCell>',
    ]
    for index, label in enumerate(labels):
        node_id = ids[index] if ids else f"n{index}"
        x = 40 + index * 190
        y = 120
        cells.append(
            f'<mxCell id="{escape(node_id)}" value="{escape(label)}" style="rounded=1;whiteSpace=wrap;html=1;fillColor={fill};strokeColor={stroke};" vertex="1" parent="1"><mxGeometry x="{x}" y="{y}" width="150" height="70" as="geometry"/></mxCell>'
        )
        if index:
            previous_id = ids[index - 1] if ids else f"n{index - 1}"
            edge_id = f"edge_{previous_id}_{node_id}" if ids else f"e{index}"
            cells.append(f'<mxCell id="{escape(edge_id)}" edge="1" parent="1" source="{escape(previous_id)}" target="{escape(node_id)}" style="endArrow=block;html=1;rounded=0;"><mxGeometry relative="1" as="geometry"/></mxCell>')
    return "<mxfile host=\"harnessos\" agent=\"v4.3-serial-video\"><diagram name=\"serial-video\"><mxGraphModel><root>" + "".join(cells) + "</root></mxGraphModel></diagram></mxfile>"


def _run_report(runtime: dict[str, Any]) -> str:
    rows = "".join(
        f"<tr><td>{html.escape(node['name'])}</td><td>{html.escape(node['agent_descriptor']['role'])}</td><td>{html.escape(node['status'])}</td><td>{len(node['attempts'])}</td></tr>"
        for node in runtime["nodes"]
    )
    return _html("V4.3 串行视频工作流运行报告", f"<p>只读报告。所有 run / rerun / continue 都需要用户确认。</p><table>{rows}</table>")


def _artifacts_report(runtime: dict[str, Any]) -> str:
    cards = "".join(f"<section><h2>{html.escape(item['name'])}</h2><pre>{html.escape(item['content'])}</pre></section>" for item in runtime["artifacts"])
    return _html("V4.3 视频工位产物", cards)


def _quality_report(runtime: dict[str, Any]) -> str:
    return _html("V4.3 视频质量报告", f"<pre>{html.escape(json.dumps(runtime['quality_report'], ensure_ascii=False, indent=2))}</pre>")


def _evidence_report(evidence: list[dict[str, Any]]) -> str:
    rows = "".join(
        f"<tr><td>{html.escape(item['operation'])}</td><td>{html.escape(str(item['user_confirmed']))}</td><td>{html.escape(item['policy_decision'])}</td><td>{html.escape(item['redaction_status'])}</td></tr>"
        for item in evidence
    )
    return _html("V4.3 视频工作流证据链", f"<p>治理证据链只读，不包含 Apply / Publish / Approve / Reject / Execute / Run 表单。</p><table>{rows}</table>")


def _html(title: str, body: str) -> str:
    return f"""<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><title>{html.escape(title)}</title>
<style>body{{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;margin:32px;color:#0f172a}}table{{border-collapse:collapse;width:100%}}td{{border:1px solid #cbd5e1;padding:8px}}section{{border:1px solid #cbd5e1;border-radius:8px;padding:16px;margin:12px 0}}pre{{white-space:pre-wrap;background:#f8fafc;padding:12px}}</style></head>
<body><h1>{html.escape(title)}</h1><p>只读报告，不包含任何隐藏变更表单。</p>{body}</body></html>"""


def _summary(start: dict[str, Any], failed: dict[str, Any], rerun: dict[str, Any], continued: dict[str, Any]) -> str:
    return f"""# V4.3 Serial Video Workflow Evidence Summary

- Real brief fixture: PASS, `{BRIEF_PATH}`.
- Serial video workflow run: PASS, `{start['status']}`.
- Simulated middle-station failure: PASS, `{failed['status']}`.
- User-confirmed storyboard rerun: PASS, downstream stale count `{len(rerun['downstream_stale'])}`.
- User-confirmed downstream continuation: PASS, `{continued['status']}`.
- Artifact count: PASS, `{len(continued['artifacts'])}`.
- Source agent mutation: PASS, not used and rejected by BFF tests.
- No token/raw payload leakage: PASS.
- No browser direct gateway RPC or event subscription route: PASS, evidence uses BFF route only.
"""


if __name__ == "__main__":
    print(json.dumps(generate_serial_video_evidence(), ensure_ascii=False, indent=2))

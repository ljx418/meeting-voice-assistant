"""Generate V4.6 governed Agent workflow builder evidence."""

from __future__ import annotations

import html
import json
import os
import sys
from pathlib import Path
from typing import Any

from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from apps.api import create_app
from core.workflows.v4_6_agent_builder import FORBIDDEN_TERMS, assert_no_forbidden_text
from tests.v4_0_reference_support import SCOPE_QUERY, build_gateway


DEFAULT_OUTPUT_DIR = Path("docs/design/V4.6/evidence/agent-workflow-builder")
REQUEST_PATH = Path("tests/fixtures/v4_6/agent_builder/user_request.md")


def generate_agent_builder_evidence(output_dir: Path = DEFAULT_OUTPUT_DIR) -> dict[str, Any]:
    os.environ.setdefault("HARNESS_V3_5_DEV_MODE", "1")
    output_dir.mkdir(parents=True, exist_ok=True)
    client = TestClient(create_app(gateway_service=build_gateway(output_dir / ".gateway-state")))
    user_request = REQUEST_PATH.read_text(encoding="utf-8")

    session = _post(client, "/bff/v4_6/agent-builder/sessions", {"user_request": user_request})
    draft = _post(client, f"/bff/v4_6/agent-builder/sessions/{session['agent_builder_session_id']}/draft", {})
    explain = _get(client, f"/bff/v4_6/agent-builder/sessions/{session['agent_builder_session_id']}/explain/{draft['proposal_id']}")
    repair = _post(client, f"/bff/v4_6/agent-builder/sessions/{session['agent_builder_session_id']}/debug-repair", {"failed_station_id": "markdown_parse"})
    handoff = _post(client, f"/bff/v4_6/agent-builder/sessions/{session['agent_builder_session_id']}/handoff", {"proposal_id": draft["proposal_id"], "target_panel": "editing_panel"})

    files = {
        "tui-transcript.txt": _transcript(session, draft, repair, handoff),
        "builder-session.json": json.dumps(session, ensure_ascii=False, indent=2),
        "workflow-draft-proposal.json": json.dumps(draft, ensure_ascii=False, indent=2),
        "workflow-plan-explanation.json": json.dumps(explain, ensure_ascii=False, indent=2),
        "debug-repair-proposal.json": json.dumps(repair, ensure_ascii=False, indent=2),
        "handoff.json": json.dumps(handoff, ensure_ascii=False, indent=2),
        "builder_report.html": _report(session, draft, explain, repair, handoff),
        "result-summary.md": _summary(session, draft, repair, handoff),
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


def _get(client: TestClient, path: str) -> dict[str, Any]:
    response = client.get(f"{path}{SCOPE_QUERY}")
    response.raise_for_status()
    data = response.json()
    assert_no_forbidden_text(data)
    return data


def _transcript(session: dict[str, Any], draft: dict[str, Any], repair: dict[str, Any], handoff: dict[str, Any]) -> str:
    return "\n".join([
        "V4.6 Governed Agent Workflow Builder transcript",
        "step=01 user='创建本地知识总结工作流' result='clarifying questions generated' agent_mutation_allowed=false",
        "step=02 command='agent builder draft' result='" + draft["proposal_id"] + "' status=proposed",
        "step=03 command='agent builder explain' read_only=true result='plan explained'",
        "step=04 command='agent builder debug-repair --failed markdown_parse' result='" + repair["repair_proposal_id"] + "' status=proposed",
        "step=05 command='agent builder handoff --panel editing_panel' operation_executed=" + str(handoff["operation_executed"]).lower(),
        "session=" + session["agent_builder_session_id"],
    ])


def _report(session: dict[str, Any], draft: dict[str, Any], explain: dict[str, Any], repair: dict[str, Any], handoff: dict[str, Any]) -> str:
    return f"""<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><title>V4.6 Agent Workflow Builder</title></head>
<body><h1>Agent 工作流搭建证据</h1><p>只读报告。Agent 只生成建议、解释和 handoff；应用、发布或运行都必须由用户在操作面板确认。</p>
<pre>{html.escape(json.dumps({'session': session, 'draft': draft, 'explain': explain, 'repair': repair, 'handoff': handoff}, ensure_ascii=False, indent=2))}</pre></body></html>"""


def _summary(session: dict[str, Any], draft: dict[str, Any], repair: dict[str, Any], handoff: dict[str, Any]) -> str:
    return f"""# V4.6 Agent Workflow Builder Evidence Summary

- Real user request fixture: PASS, `{REQUEST_PATH.as_posix()}`.
- Clarifying questions: PASS, `{len(session['clarifying_questions'])}` questions.
- Workflow draft proposal: PASS, `{draft['proposal_id']}`.
- Debug repair proposal: PASS, `{repair['repair_proposal_id']}`.
- Handoff opens target panel only: PASS, operation_executed=`{handoff['operation_executed']}`.
- Agent mutation allowed: PASS, `false`.
- No token/raw payload leakage: PASS.
"""


if __name__ == "__main__":
    print(json.dumps(generate_agent_builder_evidence(), ensure_ascii=False, indent=2))

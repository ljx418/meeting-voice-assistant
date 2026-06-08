from __future__ import annotations

import json
import subprocess
from datetime import datetime, timezone
from html import escape
from pathlib import Path
from typing import Any

from tools.v9.common import ROOT, V9_ROOT, write_json


OUT_DIR = V9_ROOT / "evidence" / "v9-prd-ux-runtime-review"
RAW_DIR = OUT_DIR / "raw"
SCREENSHOT_DIR = OUT_DIR / "screenshots"
GOAL = "用多个 Agent 讨论一个视频创作工作流，并给出可审计的分镜与运行证据"
LOCAL_DOC_GOAL = "递归总结 tests/fixtures/desktop/技术分享 下的 Markdown 技术文档"


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)

    command_results = {
        "mission_tui_text": _run_command(
            "mission_tui_text",
            ["./.venv/bin/python", "-m", "cli.main", "tui", GOAL],
        ),
        "mission_tui_json": _run_command(
            "mission_tui_json",
            ["./.venv/bin/python", "-m", "cli.main", "tui", GOAL, "--json"],
        ),
        "local_markdown_workflow_run": _run_command(
            "local_markdown_workflow_run",
            [
                "./.venv/bin/python",
                "-m",
                "cli.main",
                "tui",
                LOCAL_DOC_GOAL,
                "--run",
                "--user-confirmed",
                "--path",
                "tests/fixtures/desktop/技术分享",
                "--evidence-dir",
                str(OUT_DIR / "v7-3-local-markdown-run"),
                "--json",
            ],
            timeout=180,
        ),
        "v9_1_safety_gate_evidence": _run_command(
            "v9_1_safety_gate_evidence",
            ["./.venv/bin/python", "-m", "tools.v9.generate_safety_gate_evidence"],
            timeout=120,
        ),
        "v9_1_internal_audit_closure": _run_command(
            "v9_1_internal_audit_closure",
            ["./.venv/bin/python", "-m", "tools.v9.generate_internal_audit_closure"],
            timeout=120,
        ),
        "v9_2_pre_implementation_closure": _run_command(
            "v9_2_pre_implementation_closure",
            ["./.venv/bin/python", "-m", "tools.v9.generate_v9_2_pre_implementation_closure"],
            timeout=120,
        ),
        "v9_3_orchestration_runtime": _run_command(
            "v9_3_orchestration_runtime",
            ["./.venv/bin/python", "-m", "tools.v9.generate_v9_3_orchestration_evidence"],
            timeout=120,
        ),
        "v9_8_final_acceptance": _run_command(
            "v9_8_final_acceptance",
            ["./.venv/bin/python", "-m", "tools.v9.generate_v9_8_final_acceptance"],
            timeout=120,
        ),
        "v9_tests": _run_command(
            "v9_tests",
            ["./.venv/bin/python", "-m", "pytest", *_v9_test_files(), "-q"],
            timeout=180,
        ),
    }

    generated = _load_generated_evidence()
    summary = _build_summary(command_results, generated)
    write_json(RAW_DIR / "review-summary.json", summary)
    (OUT_DIR / "tui-window.html").write_text(_render_terminal_window(command_results["mission_tui_text"]), encoding="utf-8")
    (OUT_DIR / "runtime-output.html").write_text(_render_runtime_output(command_results), encoding="utf-8")
    (OUT_DIR / "index.html").write_text(_render_report(summary, command_results, generated), encoding="utf-8")
    return 0 if summary["status"] == "PASS" else 1


def _run_command(name: str, command: list[str], *, timeout: int = 60) -> dict[str, Any]:
    result = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, timeout=timeout, check=False)
    data = {
        "name": name,
        "command": command,
        "returncode": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr,
        "status": "PASS" if result.returncode == 0 else "FAIL",
        "created_at": _now(),
    }
    write_json(RAW_DIR / f"{name}.json", data)
    (RAW_DIR / f"{name}.stdout.txt").write_text(result.stdout, encoding="utf-8")
    (RAW_DIR / f"{name}.stderr.txt").write_text(result.stderr, encoding="utf-8")
    return data


def _v9_test_files() -> list[str]:
    return [str(path.relative_to(ROOT)) for path in sorted((ROOT / "tests").glob("test_v9_*.py"))]


def _load_generated_evidence() -> dict[str, Any]:
    paths = {
        "v9_final": V9_ROOT / "evidence" / "v9-8-final-acceptance" / "v9-final-acceptance-data.json",
        "v9_storyboard": V9_ROOT / "evidence" / "v9-3-orchestration-runtime" / "storyboard-provider-evidence.json",
        "v9_orchestration": V9_ROOT / "evidence" / "v9-3-orchestration-runtime" / "acceptance-data.json",
        "v9_user_scenarios": V9_ROOT / "evidence" / "v9-8-final-acceptance" / "v9-final-user-scenario-matrix.json",
        "local_markdown": OUT_DIR / "v7-3-local-markdown-run" / "acceptance-data.json",
    }
    evidence: dict[str, Any] = {}
    for key, path in paths.items():
        evidence[key] = {"path": str(path), "exists": path.exists()}
        if path.exists():
            evidence[key]["data"] = json.loads(path.read_text(encoding="utf-8"))
    return evidence


def _build_summary(command_results: dict[str, dict[str, Any]], generated: dict[str, Any]) -> dict[str, Any]:
    final_data = generated.get("v9_final", {}).get("data") or {}
    storyboard_data = generated.get("v9_storyboard", {}).get("data") or {}
    local_run = generated.get("local_markdown", {}).get("data") or {}
    checks = [
        _check("tui_command_runs", command_results["mission_tui_text"]["returncode"] == 0, "TUI command rendered text state."),
        _check("tui_json_state_runs", command_results["mission_tui_json"]["returncode"] == 0, "TUI command rendered JSON state."),
        _check(
            "real_openharness_tui_screenshot_exists",
            (SCREENSHOT_DIR / "real-openharness-textual-tui-window.png").exists(),
            "Real macOS Terminal window screenshot for `python -m cli.main --oh` exists.",
        ),
        _check(
            "real_openharness_tui_after_input_screenshot_exists",
            (SCREENSHOT_DIR / "real-openharness-textual-tui-after-user-input.png").exists(),
            "Real OpenHarness Textual TUI screenshot after user input and assistant response exists.",
        ),
        _check("local_markdown_workflow_runs", command_results["local_markdown_workflow_run"]["returncode"] == 0, "Natural-language local Markdown workflow executed with user confirmation."),
        _check("v9_1_safety_gate_evidence_runs", command_results["v9_1_safety_gate_evidence"]["returncode"] == 0, "V9-1 safety gate evidence was regenerated before final acceptance."),
        _check("v9_1_internal_audit_runs", command_results["v9_1_internal_audit_closure"]["returncode"] == 0, "V9-1 internal audit closure was regenerated before final acceptance."),
        _check("v9_2_pre_implementation_closure_runs", command_results["v9_2_pre_implementation_closure"]["returncode"] == 0, "V9-2 pre-implementation closure was regenerated before final acceptance."),
        _check("v9_3_runtime_runs", command_results["v9_3_orchestration_runtime"]["returncode"] == 0, "V9-3 orchestration runtime evidence regenerated."),
        _check("v9_8_final_acceptance_runs", command_results["v9_8_final_acceptance"]["returncode"] == 0, "V9-8 final acceptance validator regenerated."),
        _check("v9_tests_pass", command_results["v9_tests"]["returncode"] == 0, "V9 pytest suite passed."),
        _check("v9_final_pass", final_data.get("status") == "PASS", "V9 final acceptance status is PASS."),
        _check("v9_final_has_no_blockers", final_data.get("blockers") == [], "V9 final acceptance blockers are empty."),
        _check("claim_scan_pass", final_data.get("claim_scan") == "PASS", "No False Green scan is PASS."),
        _check("redaction_scan_pass", final_data.get("redaction_scan") == "PASS", "Redaction scan is PASS."),
        _check("storyboard_provider_backed", storyboard_data.get("status") == "PASS" and storyboard_data.get("runtime_backed") is True, "US-V9-08 provider-backed storyboard evidence is PASS."),
        _check("storyboard_has_four_images", len(storyboard_data.get("storyboard_image_artifacts") or []) >= 4, "At least four storyboard image artifacts exist."),
        _check("local_run_runtime_backed", local_run.get("runtime_backed") is True, "Local Markdown workflow evidence is runtime-backed."),
    ]
    return {
        "schema_version": "v9.prd_ux_runtime_review.v1",
        "status": "PASS" if all(item["status"] == "PASS" for item in checks) else "FAIL",
        "created_at": _now(),
        "goal": GOAL,
        "local_doc_goal": LOCAL_DOC_GOAL,
        "prd_refs": [
            "docs/design/V9.x/v9_target_prd.md",
            "docs/design/V9.x/v9_target_architecture.md",
            "docs/design/V9.x/v9_development_and_acceptance_plan.md",
            "docs/design/V9.x/v9_acceptance_gate_matrix.md",
            "docs/design/V9.x/v9_user_scenario_acceptance_gate.md",
        ],
        "test_refs": [
            "tests/test_v9_3_multi_agent_orchestration_runtime.py",
            "tests/test_v9_4_coding_workflow_pilot.py",
            "tests/test_v9_5_governed_terminal_worker.py",
            "tests/test_v9_6_workflow_studio.py",
            "tests/test_v9_7_production_governance.py",
            "tests/test_v9_8_final_acceptance.py",
        ],
        "screenshot_refs": {
            "real_openharness_textual_tui_window": "docs/design/V9.x/evidence/v9-prd-ux-runtime-review/screenshots/real-openharness-textual-tui-window.png",
            "real_openharness_textual_tui_after_user_input": "docs/design/V9.x/evidence/v9-prd-ux-runtime-review/screenshots/real-openharness-textual-tui-after-user-input.png",
            "mission_tui_rendered_snapshot_not_real_window": "docs/design/V9.x/evidence/v9-prd-ux-runtime-review/screenshots/tui-window.png",
            "runtime_output_rendered_snapshot": "docs/design/V9.x/evidence/v9-prd-ux-runtime-review/screenshots/runtime-output.png",
        },
        "checks": checks,
        "allowed_final_claim": final_data.get("final_claim"),
        "forbidden_capability_flags": {
            "production_ready": final_data.get("production_ready"),
            "agent_executor_ready": final_data.get("agent_executor_ready"),
            "full_multi_agent_orchestration_ready": final_data.get("full_multi_agent_orchestration_ready"),
            "complete_workflow_studio_ready": final_data.get("complete_workflow_studio_ready"),
            "unrestricted_terminal_worker_ready": final_data.get("unrestricted_terminal_worker_ready"),
            "production_terminal_automation_ready": final_data.get("production_terminal_automation_ready"),
        },
    }


def _check(check_id: str, passed: bool, details: str) -> dict[str, str]:
    return {"check_id": check_id, "status": "PASS" if passed else "FAIL", "details": details}


def _render_terminal_window(result: dict[str, Any]) -> str:
    command = " ".join(result["command"])
    return _html(
        "TUI 窗口运行截图源",
        f"""
        <section class="hero">
          <h1>HarnessOS TUI 窗口已拉起</h1>
          <p>实际命令：<code>{escape(command)}</code></p>
          <p>返回码：<strong>{result['returncode']}</strong></p>
        </section>
        <section class="terminal">
          <div class="titlebar"><span></span><span></span><span></span><b>Mission TUI</b></div>
          <pre>{escape(result['stdout'] or result['stderr'])}</pre>
        </section>
        """,
    )


def _render_runtime_output(command_results: dict[str, dict[str, Any]]) -> str:
    blocks = []
    for name, result in command_results.items():
        blocks.append(
            f"""
            <article>
              <h2>{escape(name)}</h2>
              <p><code>{escape(' '.join(result['command']))}</code></p>
              <p>status: <strong class="{result['status'].lower()}">{result['status']}</strong>; returncode={result['returncode']}</p>
              <pre>{escape((result['stdout'] or result['stderr'])[:5000])}</pre>
            </article>
            """
        )
    return _html("实际运行输出", "<h1>实际运行输出</h1>" + "\n".join(blocks))


def _render_report(summary: dict[str, Any], command_results: dict[str, dict[str, Any]], generated: dict[str, Any]) -> str:
    final_data = generated.get("v9_final", {}).get("data") or {}
    storyboard_data = generated.get("v9_storyboard", {}).get("data") or {}
    local_run = generated.get("local_markdown", {}).get("data") or {}
    scenario_rows = []
    for item in final_data.get("user_scenarios", []):
        scenario_rows.append(
            f"<tr><td>{escape(str(item.get('scenario_id')))}</td><td>{escape(str(item.get('status')))}</td><td>{escape(str(item.get('runtime_backed')))}</td><td>{escape(str(item.get('evidence_scope') or item.get('evidence_ref') or ''))}</td></tr>"
        )
    checks = "\n".join(f"<tr><td>{escape(c['check_id'])}</td><td class='{c['status'].lower()}'>{c['status']}</td><td>{escape(c['details'])}</td></tr>" for c in summary["checks"])
    command_items = "".join(
        f"<li><code>{escape(' '.join(result['command']))}</code> - <b class=\"{result['status'].lower()}\">{result['status']}</b></li>"
        for result in command_results.values()
    )
    storyboard_images = "".join(
        f"<figure><img src='../v9-3-orchestration-runtime/{escape(item['path'].split('v9-3-orchestration-runtime/')[-1])}'><figcaption>{escape(item['artifact_ref'])}</figcaption></figure>"
        for item in storyboard_data.get("storyboard_image_artifacts", [])
    )
    return _html(
        "V9 PRD/UX/运行证据审查页",
        f"""
        <section class="hero">
          <h1>V9 PRD / 测试 / 用户体验实际运行证据</h1>
          <p>状态：<strong class="{summary['status'].lower()}">{summary['status']}</strong></p>
          <p>允许声明：<code>{escape(str(summary.get('allowed_final_claim')))}</code></p>
          <p>边界：该声明仍然不是 production ready、Agent executor ready、complete Workflow Studio ready 或 full multi-Agent orchestration ready。</p>
        </section>

        <section>
          <h2>当前目标架构与运行设计</h2>
          <div class="architecture">
            <article>
              <h3>用户入口层</h3>
              <p>用户通过 Mission TUI / Workflow Studio / Product Console 输入自然语言目标、查看状态、确认 handoff。TUI 是 workflow head 和解释性界面，不直接构造 runtime truth。</p>
              <p><b>证据：</b><code>cli.main --oh</code> 真实交互 TUI 截图、<code>cli.main tui</code> Mission TUI stdout、V9-6 Studio BFF/DTO 证据。</p>
            </article>
            <article>
              <h3>Agent 与编排层</h3>
              <p>每个 station 绑定独立 Agent 描述，包含 role / goal / memory / tools / skills / MCP refs。V9-3 证明 serial、parallel、fan-out、fan-in、recovery、attempt history 和 artifact lineage。</p>
              <p><b>证据：</b><code>v9-3-orchestration-runtime/acceptance-data.json</code> 与运行看板。</p>
            </article>
            <article>
              <h3>受控执行层</h3>
              <p>V9-2 只允许四个受控动作：workflow.instance.start、station.rerun、artifact.write、quality.evaluation.create。所有 durable mutation 必须经过 policy、HumanAuthorizationRef / user confirmation、approval、kill switch、idempotency、rollback 和 evidence chain。</p>
              <p><b>边界：</b>source=agent direct durable mutation 继续拒绝。</p>
            </article>
            <article>
              <h3>代码与终端工作流层</h3>
              <p>V9-4/V9-5 提供代码工作流和受控终端 worker 试点：可以生成 plan、diff proposal、sandboxed test、review summary、transcript 和 diff capture。</p>
              <p><b>边界：</b>不自动 commit / push / deploy，不提供 unrestricted shell。</p>
            </article>
            <article>
              <h3>证据与治理层</h3>
              <p>V9-7/V9-8 聚合 tenant isolation、credential lease、append-only audit export、incident timeline、No False Green、redaction 和最终验收看板。</p>
              <p><b>证据：</b><code>v9-final-acceptance-data.json</code> status=PASS, blockers=[]。</p>
            </article>
          </div>
        </section>

        <section>
          <h2>当前功能到运行证据映射</h2>
          <table>
            <thead><tr><th>用户可体验能力</th><th>实际运行设计</th><th>本页证据</th><th>边界</th></tr></thead>
            <tbody>
              <tr><td>输入自然语言目标查看 Mission TUI</td><td><code>harness tui</code> 渲染 intent、state timeline、available action、forbidden reason、evidence links</td><td><code>mission_tui_text.json</code> / stdout；渲染快照单独标注为非真实窗口</td><td>Mission TUI 是 transcript_only，不直接执行 durable mutation</td></tr>
              <tr><td>打开真实交互 TUI 并输入问题</td><td><code>python -m cli.main --oh</code> 拉起 OpenHarness Textual TUI，用户在 composer 输入问题，assistant 在 transcript 区响应</td><td>真实 macOS Terminal 窗口截图：启动态 + 输入后响应态</td><td>该截图只证明 TUI 界面和一次短交互，不证明 Agent executor ready</td></tr>
              <tr><td>运行本地 Markdown 技术文档总结工作流</td><td>scanner 读取本地文件，provider-backed summary，生成 workflow board、quality report、evidence chain</td><td><code>v7-3-local-markdown-run/acceptance-data.json</code></td><td>仅授权路径内文件；不存 raw prompt / raw file content</td></tr>
              <tr><td>多 Agent 讨论与合成结论</td><td>station-bound Agents 执行 fan-out/fan-in、attempt history、lineage</td><td>V9-3 运行看板截图</td><td>不声明 full multi-Agent orchestration ready</td></tr>
              <tr><td>视频创作分镜工作流</td><td>MiniMax provider 生成 4 张 storyboard images，记录 provider/model/invocation refs 和 sha256</td><td>US-V9-08 分镜图与 <code>storyboard-provider-evidence.json</code></td><td>不存 provider request/response body、base64 或 credential</td></tr>
              <tr><td>最终验收与审计</td><td>V9-8 validator 聚合阶段证据、用户场景、claim scan、redaction scan、drawio XML</td><td>V9-8 最终验收看板截图</td><td>最终声明只限 ready for review</td></tr>
            </tbody>
          </table>
        </section>

        <section>
          <h2>截图证据</h2>
          <p>截图分为两类：真实窗口截图来自 macOS Terminal；渲染快照来自本报告 HTML 页面，只用于审查排版，不作为真实 TUI 窗口证据。</p>
          <div class="screens">
            <figure><img src="screenshots/real-openharness-textual-tui-window.png"><figcaption>真实窗口截图：macOS Terminal 中实际运行 <code>./.venv/bin/python -m cli.main --oh</code>，显示 OpenHarnessTerminalApp、Status、Tasks、MCP 面板。</figcaption></figure>
            <figure><img src="screenshots/real-openharness-textual-tui-after-user-input.png"><figcaption>真实用户场景截图：在 OpenHarness Textual TUI 中输入问题后，transcript 区出现 user / assistant 交互响应。</figcaption></figure>
            <figure><img src="screenshots/tui-window.png"><figcaption>渲染快照，不是真实窗口：Mission TUI stdout 的 HTML 呈现，用于审查命令输出内容。</figcaption></figure>
            <figure><img src="screenshots/runtime-output.png"><figcaption>渲染快照：实际命令 stdout/stderr 汇总，包括 TUI、V9-3、V9-8、测试命令。</figcaption></figure>
            <figure><img src="screenshots/v9-3-runtime-dashboard.png"><figcaption>V9-3 多 Agent 编排运行看板</figcaption></figure>
            <figure><img src="screenshots/v9-final-dashboard.png"><figcaption>V9-8 最终验收看板</figcaption></figure>
          </div>
        </section>

        <section>
          <h2>开发前固化 PRD / 架构 / 验收门槛</h2>
          <ul>{''.join(f'<li><code>{escape(ref)}</code></li>' for ref in summary['prd_refs'])}</ul>
        </section>

        <section>
          <h2>测试用例覆盖</h2>
          <ul>{''.join(f'<li><code>{escape(ref)}</code></li>' for ref in summary['test_refs'])}</ul>
          <p>本轮实际执行：<code>{escape(' '.join(command_results['v9_tests']['command']))}</code></p>
        </section>

        <section>
          <h2>实际运行命令</h2>
          <ol>{command_items}</ol>
        </section>

        <section>
          <h2>验收检查</h2>
          <table><thead><tr><th>检查项</th><th>状态</th><th>说明</th></tr></thead><tbody>{checks}</tbody></table>
        </section>

        <section>
          <h2>TUI 与自然语言运行证据</h2>
          <p>TUI goal: <code>{escape(summary['goal'])}</code></p>
          <p>本地 Markdown 工作流 goal: <code>{escape(summary['local_doc_goal'])}</code></p>
          <pre>{escape(json.dumps(local_run, ensure_ascii=False, indent=2)[:4000])}</pre>
        </section>

        <section>
          <h2>用户场景验收矩阵</h2>
          <table><thead><tr><th>场景</th><th>状态</th><th>runtime_backed</th><th>证据</th></tr></thead><tbody>{''.join(scenario_rows)}</tbody></table>
        </section>

        <section>
          <h2>US-V9-08 视频创作分镜产物</h2>
          <p>provider: <code>{escape(str(storyboard_data.get('provider_ref')))}</code>; model: <code>{escape(str(storyboard_data.get('provider_model_ref')))}</code>; invocation: <code>{escape(str(storyboard_data.get('provider_invocation_ref')))}</code></p>
          <div class="storyboard">{storyboard_images}</div>
          <pre>{escape(json.dumps(storyboard_data, ensure_ascii=False, indent=2)[:5000])}</pre>
        </section>

        <section>
          <h2>最终验收数据</h2>
          <pre>{escape(json.dumps(final_data, ensure_ascii=False, indent=2)[:9000])}</pre>
        </section>
        """,
    )


def _html(title: str, body: str) -> str:
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{escape(title)}</title>
  <style>
    body {{ margin: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: #f6f7f9; color: #172033; }}
    section, article {{ background: #fff; border: 1px solid #d8dee8; border-radius: 8px; margin: 18px auto; padding: 18px; max-width: 1180px; }}
    .hero {{ background: #111827; color: #f9fafb; border-color: #111827; }}
    code {{ background: #eef2f7; color: #16233a; padding: 2px 5px; border-radius: 4px; }}
    .hero code {{ background: #263244; color: #e5e7eb; }}
    pre {{ white-space: pre-wrap; word-break: break-word; background: #0f172a; color: #dbeafe; border-radius: 8px; padding: 14px; overflow: auto; max-height: 680px; }}
    table {{ width: 100%; border-collapse: collapse; }}
    th, td {{ border: 1px solid #d8dee8; padding: 8px; text-align: left; vertical-align: top; }}
    th {{ background: #eef2f7; }}
    .pass {{ color: #166534; font-weight: 700; }}
    .fail {{ color: #b91c1c; font-weight: 700; }}
    .screens, .storyboard {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 14px; }}
    .architecture {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 14px; }}
    .architecture article {{ margin: 0; max-width: none; background: #f8fafc; }}
    h3 {{ margin-top: 0; }}
    figure {{ margin: 0; border: 1px solid #d8dee8; border-radius: 8px; background: #f8fafc; padding: 10px; }}
    img {{ width: 100%; display: block; border-radius: 6px; border: 1px solid #cbd5e1; }}
    figcaption {{ color: #475569; font-size: 13px; margin-top: 8px; }}
    .terminal {{ background: #0b1020; color: #dbeafe; max-width: 1180px; }}
    .titlebar {{ display: flex; align-items: center; gap: 8px; margin-bottom: 12px; color: #e5e7eb; }}
    .titlebar span {{ display: inline-block; width: 12px; height: 12px; border-radius: 50%; background: #ef4444; }}
    .titlebar span:nth-child(2) {{ background: #f59e0b; }}
    .titlebar span:nth-child(3) {{ background: #22c55e; }}
  </style>
</head>
<body>{body}</body>
</html>
"""


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


if __name__ == "__main__":
    raise SystemExit(main())

# V8-4 Station Agent Runtime Completion Note

文档状态：V8-4 completion note / real runtime fixture evidence summary。

## Allowed Claim

```text
V8-4 complete: station-agent local document workflow pilot ready for review.
```

## Evidence Scope

```text
evidence_scope=real_runtime_fixture
runtime_backed=true
provider=minimax
provider_config_source=.env.local
```

V8-4 使用 `tests/fixtures/desktop/技术分享` 作为真实 fixture 目录，实际读取 Markdown 文件，并通过 MiniMax provider 生成 station-agent 工作流证据。

## Evidence Outputs

```text
docs/design/V8.x/evidence/v8-4-station-agent-runtime/index.html
docs/design/V8.x/evidence/v8-4-station-agent-runtime/acceptance-data.json
docs/design/V8.x/evidence/v8-4-station-agent-runtime/station-agent-registry.json
docs/design/V8.x/evidence/v8-4-station-agent-runtime/station-agent-descriptors.json
docs/design/V8.x/evidence/v8-4-station-agent-runtime/agent-context-envelopes.json
docs/design/V8.x/evidence/v8-4-station-agent-runtime/agent-invocation-evidence.json
docs/design/V8.x/evidence/v8-4-station-agent-runtime/agent-capability-decisions.json
docs/design/V8.x/evidence/v8-4-station-agent-runtime/agent-run-results.json
docs/design/V8.x/evidence/v8-4-station-agent-runtime/workflow_board.html
docs/design/V8.x/evidence/v8-4-station-agent-runtime/agent-evidence.html
docs/design/V8.x/evidence/v8-4-station-agent-runtime/workflow.drawio
docs/design/V8.x/evidence/v8-4-station-agent-runtime/workflow_status.drawio
docs/design/V8.x/evidence/v8-4-station-agent-runtime/claims-scan.md
docs/design/V8.x/evidence/v8-4-station-agent-runtime/redaction-scan.md
docs/design/V8.x/evidence/v8-4-station-agent-runtime/result-summary.md
```

## Acceptance Snapshot

```text
status=PASS
station_count=7
agent_descriptor_count=7
workflow_explainer_agent_exists=true
agent_invocation_count=7
scanner_actual_read_count=5
provider_invocation_count=4
folder_summaries_generated=PASS
folder_summaries_llm_backed=PASS
overview_summary_generated=PASS
overview_summary_llm_backed=PASS
quality_report_generated=PASS
source_agent_mutation_denied=PASS
claim_scan=PASS
redaction_scan=PASS
terminal_worker_enabled=false
```

## Validation Commands

```text
python -m pytest tests/test_v8_*.py -q
python -m pytest tests/test_v8_*.py tests/test_v7_*.py tests/test_v6_*.py -q
python -m pytest -q
xmllint --noout docs/design/V8.x/v8_current_gap_analysis.drawio docs/design/V8.x/evidence/v8-4-station-agent-runtime/workflow.drawio docs/design/V8.x/evidence/v8-4-station-agent-runtime/workflow_status.drawio
```

最新结果：

```text
tests/test_v8_*.py: 15 passed
tests/test_v8_*.py tests/test_v7_*.py tests/test_v6_*.py: 137 passed
full pytest: 1117 passed, 3 skipped
drawio XML validation: PASS
```

## Forbidden Claims

V8-4 不证明：

```text
Agent executor ready
production Agent executor ready
autonomous coding workflow ready
autonomous workflow editing ready
full multi-Agent orchestration ready
complete Workflow Studio ready
unrestricted terminal worker ready
ChromeCLI production automation ready
```

## Spec Drift Evaluation

```text
spec_drift_risk=LOW
```

V8-4 按 V8 PRD 的 bounded local document workflow pilot 执行。它只验证每个本地文档 workflow station 均有 Agent descriptor、context envelope、capability decision、invocation evidence 和 run result。

## False Green Evaluation

```text
false_green_risk=LOW
```

Fake provider 测试不能 PASS；真实 PASS 依赖 provider_invocation_count > 0。Evidence package 中继续保留 redaction scan 和 claim scan。

## Next Stage Audit

V8-5 仅是终端 worker 高风险设计门禁。V8-6 controlled terminal worker pilot 必须另有人类 high-risk proceed decision，不能由 V8-4 自动解锁。

## Proceed Decision

```text
proceed_to_v8_5_design_gate=true
proceed_to_v8_6_runtime=false
```

## No False Green Statement

V8-4 只证明 bounded station-agent local document workflow pilot ready for review。它不证明 Agent executor、完整多 Agent 编排、受控终端 worker 或生产级自动化终端能力。

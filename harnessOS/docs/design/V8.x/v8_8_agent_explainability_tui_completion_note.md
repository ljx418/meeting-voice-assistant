# V8-8 Agent Explainability TUI Completion Note

文档状态：V8-8 completion note / read-model TUI evidence summary。

## Allowed Claim

```text
V8-8 complete: agent explainability TUI baseline ready for review.
```

## Evidence Scope

```text
evidence_scope=read_model_from_v8_4_v8_6_evidence
runtime_backed=false
readonly=true
```

V8-8 基于 V8-4 station-agent runtime evidence 和 V8-6 controlled terminal worker evidence 生成只读解释视图，不构造 runtime truth，不执行 mutation。

## Evidence Outputs

```text
docs/design/V8.x/evidence/v8-8-agent-explainability-tui/index.html
docs/design/V8.x/evidence/v8-8-agent-explainability-tui/tui-screen.html
docs/design/V8.x/evidence/v8-8-agent-explainability-tui/agent-explainability-state.json
docs/design/V8.x/evidence/v8-8-agent-explainability-tui/acceptance-data.json
docs/design/V8.x/evidence/v8-8-agent-explainability-tui/claims-scan.md
docs/design/V8.x/evidence/v8-8-agent-explainability-tui/redaction-scan.md
docs/design/V8.x/evidence/v8-8-agent-explainability-tui/result-summary.md
```

## Acceptance Snapshot

```text
status=PASS
panel_count=8
tui_shows_agent_for_each_station=PASS
tui_shows_workflow_explainer_agent=PASS
tui_shows_forbidden_action_reason=PASS
tui_links_runtime_report_evidence_blueprint=PASS
tui_shows_terminal_handoff_status=PASS
tui_no_hidden_mutation_form=PASS
tui_no_auto_apply_auto_run_copy=PASS
tui_does_not_construct_runtime_truth=PASS
claim_scan=PASS
redaction_scan=PASS
```

## Validation Commands

```text
python -m pytest tests/test_v8_8_agent_explainability_tui.py -q
python -m pytest tests/test_v8_*.py -q
```

最新结果：

```text
tests/test_v8_8_agent_explainability_tui.py: 3 passed
tests/test_v8_*.py: 29 passed
tests/test_v8_*.py tests/test_v7_*.py tests/test_v6_*.py: 151 passed
full pytest: 1131 passed, 3 skipped
drawio XML validation: PASS
```

## Spec Drift Evaluation

```text
spec_drift_risk=LOW
```

V8-8 符合 V8 PRD 的可解释体验目标，只做 read model projection。

## False Green Evaluation

```text
false_green_risk=LOW
```

Evidence 明确 `runtime_backed=false`，TUI 不构造 runtime truth，不出现自动执行文案。

## Next Stage Audit

V8-9 可以进入最终验收框架更新，但最终 V8 complete 声明仍取决于 V8-7 是否被授权并通过，或是否以 high-risk not-enabled 的方式被人工接受。

## Proceed Decision

```text
proceed_to_v8_9_framework_update=true
proceed_to_v8_final_claim=false
```

## No False Green Statement

V8-8 只证明 Agent explainability TUI baseline ready for review。它不证明 Agent executor、完整多 Agent 编排、Workflow Studio 完整产品化或终端 worker 生产自动化。

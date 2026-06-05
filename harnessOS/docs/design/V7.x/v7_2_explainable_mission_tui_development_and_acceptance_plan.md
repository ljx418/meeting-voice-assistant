# V7-2 Explainable Mission TUI Development And Acceptance Plan

文档状态：V7-2 complete / ready for review。

## Entry Gate

V7-2 不能直接进入 implementation。进入 V7-2 前必须满足：

```text
V7-0 accepted
V7-1 accepted
v7_2_pre_implementation_review.md accepted
harness tui command contract accepted
MissionTuiState schema accepted
MissionInputEvent schema accepted
ExperienceStateTimeline schema accepted
AvailableAction schema accepted
ForbiddenActionReason schema accepted
EvidenceLink schema accepted
BlueprintLink schema accepted
RuntimeReportLink schema accepted
TUI screen layout contract accepted
```

当前 V7-0 / V7-1 与 V7-2 pre-implementation review 均已完成本地审计。V7-2 Explainable Mission TUI implementation 已完成，但不得扩展到 V7-3 natural-language controlled run。

## Runtime Truth Boundary

```text
TUI is workflow head, not runtime truth.
TUI cannot execute durable mutation before user confirmation.
TUI cannot let source=agent directly mutate runtime.
TUI cannot claim complete Workflow Studio.
```

## PR Slices

```text
PR1 Add `harness tui` command contract
PR2 Mission input and transcript panel
PR3 Experience state timeline panel
PR4 Available actions and forbidden reasons panel
PR5 Blueprint / report / evidence link rendering
PR6 TUI acceptance transcript and screenshots
```

## Acceptance Tests

```text
harness_tui_command_exists
tui_accepts_natural_language_goal
tui_renders_state_timeline
tui_renders_available_actions
tui_renders_forbidden_reasons
tui_links_blueprint_report_evidence
tui_blocks_mutation_before_user_confirmation
tui_blocks_source_agent_direct_mutation
tui_no_false_green_copy
```

## Evidence Package

```text
docs/design/V7.x/evidence/v7-2-explainable-tui/
  index.html
  tui-transcript.txt
  screenshots/
  acceptance-data.json
  result-summary.md
  claims-scan.md
  redaction-scan.md
```

## Validation

```text
./.venv/bin/python -m pytest tests/test_v7_2_*.py -q
./.venv/bin/python -m pytest tests/test_cli_*.py -q
```

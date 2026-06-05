# V7-2 Pre-Implementation Review

文档状态：V7-2 pre-implementation review / no runtime coding before this review。

## 1. Current Stage

```text
previous_stage: V7-1 complete / ready for review
current_stage: V7-2 pre-implementation PRD/spec review
implementation_allowed: true_after_this_review_passes
runtime_code_started: false
```

## 2. PRD Spec Review

V7-2 must implement:

```text
first-class `harness tui` command
mission input capture
experience state timeline rendering
available action rendering
forbidden reason rendering
blueprint / runtime report / evidence links
TUI transcript and evidence package
```

V7-2 must not implement:

```text
natural-language workflow run
durable mutation before user confirmation
source=agent direct durable mutation
complete Workflow Studio
Agent executor
production controlled executor
full production GA
```

## 3. Architecture Delta Review

V7-2 adds:

```text
Mission TUI state builder
Mission transcript renderer
AvailableAction resolver projection
ForbiddenActionReason projection
Experience link projection
HTML evidence package renderer
```

V7-2 reads from V7-1 Small Studio evidence and V7-0 schemas. It does not write runtime truth.

## 4. Implementation Slices

```text
PR1 Mission TUI state builder
PR2 CLI `harness tui` command
PR3 text transcript renderer
PR4 HTML evidence package
PR5 focused tests and regression
```

## 5. Acceptance Criteria

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

## 6. Required Evidence

```text
docs/design/V7.x/evidence/v7-2-explainable-tui/index.html
docs/design/V7.x/evidence/v7-2-explainable-tui/tui-transcript.txt
docs/design/V7.x/evidence/v7-2-explainable-tui/acceptance-data.json
docs/design/V7.x/evidence/v7-2-explainable-tui/result-summary.md
docs/design/V7.x/evidence/v7-2-explainable-tui/claims-scan.md
docs/design/V7.x/evidence/v7-2-explainable-tui/redaction-scan.md
docs/design/V7.x/evidence/v7-2-explainable-tui/raw/mission-tui-state.json
```

## 7. Test Plan

```text
./.venv/bin/python -m pytest tests/test_v7_2_mission_tui.py -q
./.venv/bin/python -m pytest tests/test_v7_1_small_studio.py tests/test_v7_0_planning_hardening.py -q
xmllint --noout docs/design/V7.x/v7_current_gap_analysis.drawio
```

## 8. PRD Drift Evaluation

```text
LOW
```

V7-2 stays inside explainable Mission TUI and does not implement natural-language controlled run.

## 9. False Green Evaluation

```text
LOW
```

V7-2 must label evidence as `transcript_only` and must not present transcript-only output as runtime-backed.

## 10. Proceed Decision

```text
proceed_to_v7_2_implementation
```

V7-2 implementation may start after this review because no critical or major PRD drift was found.

# V4.3 Serial Multi-Agent Video Workflow MVP Preimplementation Audit

## 1. Current Baseline

Allowed completed baseline:

```text
V4.2-C complete: controlled runtime MVP ready for dev/local validation.
```

V4.2-C proves dev/local controlled runtime start, user-confirmed station rerun, attempt history, downstream stale marking, runtime evidence, Drawio status output, and HTML reports over the V4.1 local knowledge workflow path.

## 2. V4.3 Stage Position

Stage name:

```text
V4.3 Serial Multi-Agent Video Workflow MVP / 串行多 Agent 视频工作流 MVP
```

Allowed completion claim:

```text
V4.3 complete: serial multi-Agent video workflow MVP ready for dev/local validation.
```

Forbidden claims:

```text
forbidden complete Workflow Studio ready
forbidden complete AgentTalkWindow ready
forbidden Agent executor ready
forbidden controlled executor ready
forbidden autonomous workflow editing ready
forbidden production-ready external app support
forbidden full multi-Agent orchestration ready
```

## 3. Product Scope

V4.3 should validate a serial video creation workflow:

```text
Writer Agent
Storyboard Agent
Copywriting Agent
Editing Plan Agent
Quality Review Agent
Publish Preparation Agent
```

The workflow must expose:

1. Agent descriptor per station.
2. Role, goal, model_ref, tool_refs, and skill_refs per station.
3. Input and output artifact contracts per station.
4. Per-station artifact viewer.
5. User-confirmed middle station rerun.
6. Downstream stale propagation after rerun.
7. Runtime evidence for start, rerun, continuation, and report generation.
8. Drawio workflow visualization.
9. HTML run report.
10. TUI transcript for creation, run, status, artifact, quality, and evidence inspection.

## 4. Non-Goals

V4.3 must not implement:

1. Real video rendering.
2. Real editing software integration.
3. Production model or connector credential handling.
4. Agent autonomous execution.
5. Generic multi-Agent runtime beyond the serial video workflow slice.
6. Parallel deliberation workflow. That belongs to V4.4.
7. Long-running engineering workflow. That belongs to V4.5.
8. Full Web low-code studio.

## 5. PR Slices

### V4.3-PR1 Video Workflow Spec Contract

Add a strict serial video workflow fixture and schema extension for AgentDescriptor fields:

```text
role
goal
model_ref
tool_refs
skill_refs
input_artifact_contract
output_artifact_contract
```

WorkflowSpec remains a headless design artifact and must not replace WorkflowDraft or WorkflowVersion runtime truth.

### V4.3-PR2 Deterministic Video Artifact Runner

Add a deterministic dev/local runner that produces text artifacts for each station:

```text
script_outline.md
storyboard.md
short_copy.md
editing_plan.md
quality_review.json
publish_package.md
```

The runner must not call external model APIs or video editing tools.

### V4.3-PR3 User-Confirmed Rerun and Downstream Stale

Reuse the V4.2-C controlled runtime pattern for a middle station rerun.

Required behavior:

```text
user_confirmed=true required
source=agent rejected
new attempt created
old attempt retained
downstream stations marked stale
continuation requires user confirmation
```

### V4.3-PR4 Drawio and HTML Reports

Generate:

```text
video_workflow.drawio
video_workflow_status.drawio
video_artifact_lineage.drawio
video_run_report.html
video_artifacts.html
video_quality.html
video_evidence.html
```

Reports are read-only and must not include hidden mutation forms.

### V4.3-PR5 TUI Evidence Package

Output evidence under:

```text
docs/design/V4.3/evidence/serial-video-workflow/
```

Required files:

```text
tui-transcript.txt
video_workflow.yaml
video_workflow.json
video_workflow.drawio
video_workflow_status.drawio
video_artifact_lineage.drawio
video_run_report.html
video_artifacts.html
video_quality.html
video_evidence.html
runtime-result.json
attempt-history.json
downstream-stale.json
operation-evidence.json
result-summary.md
```

## 6. Test Plan

Add focused tests:

```text
tests/test_v4_3_video_workflow_spec.py
tests/test_v4_3_video_runtime_runner.py
tests/test_v4_3_video_rerun_stale.py
tests/test_v4_3_video_reports.py
tests/test_v4_3_video_evidence_package.py
tests/test_v4_3_video_false_green.py
```

Required assertions:

1. Video workflow spec validates strictly.
2. Unknown fields rejected.
3. Token and raw payload fields rejected.
4. All six video stations exist in serial order.
5. Every station has role, goal, model_ref, tool_refs, skill_refs, input artifact contract, and output artifact contract.
6. Runner produces the expected artifacts.
7. Rerun requires user confirmation.
8. `source=agent` cannot rerun or continue.
9. Middle station rerun creates a new attempt and keeps old attempt.
10. Downstream stale is visible.
11. HTML reports are read-only.
12. Drawio files are valid XML.
13. Evidence package is complete.
14. No false-green claims appear.

Regression commands:

```text
./.venv/bin/python -m pytest tests/test_v4_3_*.py -q
./.venv/bin/python -m pytest tests/test_v4_2_*.py -q
./.venv/bin/python -m pytest tests/test_v4_1_*.py -q
./.venv/bin/python -m pytest tests/test_v4_0_*.py -q
./.venv/bin/python -m pytest -q
cd apps/workflow-console && npm test -- --runInBand
cd apps/workflow-console && npm run build
cd apps/workflow-console && npm run test:e2e
xmllint --noout docs/design/V4.x/v4_x_headless_current_gap_analysis.drawio
```

## 7. Risk Review

Spec Drift Risk: MEDIUM

Reason: V4.3 introduces AgentDescriptor semantics and multi-station video workflow artifacts. The implementation must stay deterministic and dev/local, otherwise it can drift into a generic Agent executor or production connector system.

False Green Risk: MEDIUM

Reason: A deterministic text artifact runner can look like multi-Agent execution even when no real model or tool agents are used. Completion notes must state this is a serial multi-Agent workflow MVP fixture, not full multi-Agent orchestration.

Proceed Decision:

```text
proceed_with_caution_after_user_or_planning_review
```

Development must stop if V4.3 requires:

```text
requires Agent autonomous mutation
requires production connector credentials
requires real video generation
requires full Web Studio editing
requires parallel Agent orchestration
requires production-ready external app support
```

## 8. Acceptance Evidence Format

The V4.3 completion note must include:

1. Allowed claim.
2. Forbidden claims.
3. Actual files changed.
4. Tests added.
5. Evidence package path.
6. TUI transcript result.
7. Drawio validation result.
8. HTML report validation result.
9. Runtime result and attempt history result.
10. Spec Drift Evaluation.
11. False Green Evaluation.
12. Next Stage Audit.
13. Proceed Decision.
14. No False Green Statement.

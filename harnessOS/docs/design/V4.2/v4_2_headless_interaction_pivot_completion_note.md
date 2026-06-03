# V4.2-A Headless Interaction Pivot Completion Note

Status: complete.

## 1. Allowed Claim

```text
V4.2-A complete: headless interaction baseline ready for local workflow validation.
```

## 2. Forbidden Claims

```text
forbidden complete Workflow Studio ready
forbidden Agent executor ready
forbidden controlled executor ready
forbidden production-ready external app support
forbidden full multi-Agent orchestration ready
```

## 3. Implementation Evidence

BFF/runtime source:

```text
apps/api/routers/bff_v41.py
tests/fixtures/desktop/技术分享/
```

Headless generator:

```text
scripts/v4_2_headless_evidence.py
```

Evidence outputs:

```text
docs/design/V4.2/evidence/headless-interaction/tui-transcript.txt
docs/design/V4.2/evidence/headless-interaction/workflow.yaml
docs/design/V4.2/evidence/headless-interaction/workflow.json
docs/design/V4.2/evidence/headless-interaction/workflow.schema.json
docs/design/V4.2/evidence/headless-interaction/workflow.drawio
docs/design/V4.2/evidence/headless-interaction/workflow_status.drawio
docs/design/V4.2/evidence/headless-interaction/artifact_lineage.drawio
docs/design/V4.2/evidence/headless-interaction/thin_web_console.html
docs/design/V4.2/evidence/headless-interaction/workflow_board.html
docs/design/V4.2/evidence/headless-interaction/artifacts.html
docs/design/V4.2/evidence/headless-interaction/quality.html
docs/design/V4.2/evidence/headless-interaction/evidence.html
docs/design/V4.2/evidence/headless-interaction/exported-runtime-result.json
docs/design/V4.2/evidence/headless-interaction/operation-evidence.json
docs/design/V4.2/evidence/headless-interaction/result-summary.md
```

Tests added:

```text
tests/test_v4_2_workflow_spec_schema.py
tests/test_v4_2_tui_transcript_contract.py
tests/test_v4_2_drawio_renderer.py
tests/test_v4_2_html_report_generator.py
tests/test_v4_2_headless_evidence_package.py
tests/test_v4_2_thin_web_console.py
tests/test_v4_2_headless_false_green.py
```

Docs updated:

```text
docs/design/V4.1/v4_1_stage_gate_development_plan.md
docs/design/V4.2/00_README.md
docs/design/V4.x/v4_x_headless_current_gap_analysis.md
docs/design/V4.x/v4_x_headless_current_gap_analysis.drawio
docs/design/V4.0/v4_0_current_gap_analysis.md
```

Frontend compatibility fixes:

```text
apps/workflow-console/src/components/ConsoleShell.tsx
apps/workflow-console/src/ui/base/BaseComponents.stories.tsx
apps/workflow-console/src/ui/panels/RightPanels.tsx
```

## 4. Verified Behavior

1. WorkflowSpec includes strict sections: metadata, stations, edges, artifact_contracts, quality_rules, approval_points, context_refs, evidence_refs.
2. Unknown top-level spec fields are rejected.
3. token, Authorization, raw payload, raw prompt, signed URL, and direct `/v1/*` strings are blocked from generated evidence.
4. TUI read commands are marked read-only.
5. Apply, publish, and run transcript steps are backed by `v4_1_local_workflow_path`.
6. Station rerun is marked `transcript_only=true` because generic station rerun is V4.2-B/C scope.
7. Drawio files are valid XML and read-only visualization outputs.
8. HTML reports are read-only and include no hidden mutation form.
9. Thin Web Console is an observation entry only.
10. Evidence package is generated from real V4.1 BFF/local workflow operations and does not fabricate generic runtime evidence.

## 5. Validation Commands

```text
./.venv/bin/python scripts/v4_2_headless_evidence.py
Result: PASS

./.venv/bin/python -m pytest tests/test_v4_2_*.py -q
Result: PASS, 22 passed

./.venv/bin/python -m pytest tests/test_v4_1_*.py -q
Result: PASS, 7 passed

./.venv/bin/python -m pytest tests/test_v4_0_*.py -q
Result: PASS, 215 passed

./.venv/bin/python -m pytest -q
Result: PASS, 685 passed, 3 skipped

npm test -- --runInBand
Working directory: apps/workflow-console
Result: PASS, 76 passed

npm run build
Working directory: apps/workflow-console
Result: PASS

npm run test:e2e
Working directory: apps/workflow-console
Result: PASS, 23 passed

xmllint --noout docs/design/V4.x/v4_x_headless_current_gap_analysis.drawio
Result: PASS

xmllint --noout docs/design/V4.2/evidence/headless-interaction/workflow.drawio docs/design/V4.2/evidence/headless-interaction/workflow_status.drawio docs/design/V4.2/evidence/headless-interaction/artifact_lineage.drawio
Result: PASS
```

## 6. Spec Drift Evaluation

Risk: LOW

Evidence:

```text
V4.2-A outputs are Headless wrappers around the verified V4.1 local recursive Markdown workflow path.
WorkflowSpec, Drawio, HTML reports, and Thin Web Console are explicitly read-only or evidence/report artifacts.
Generic start/rerun/runtime behavior remains deferred to V4.2-B/C.
```

Out-of-scope items detected:

```text
None in V4.2-A implementation.
```

Decision:

```text
Proceed to V4.2-B/C audit planning only. Do not start implementation without a separate controlled runtime acceptance plan.
```

## 7. False Green Evaluation

Risk: LOW

Evidence:

```text
The TUI transcript marks mutating commands as V4.1-backed or transcript-only.
operation-evidence.json only contains workflow.folder_summary.* operations from the V4.1 local workflow path.
No generic controlled runtime evidence is fabricated.
Claim guards pass.
```

Unverified items:

```text
generic workflow start
generic station rerun
StationRun attempt history beyond V4.1 local slice
downstream stale propagation
controlled execution runtime
Agent executor
does not prove production-ready external app support
```

Decision:

```text
V4.2-A can be closed. V4.2-B/C must not inherit V4.2-A evidence as runtime proof.
```

## 8. Next Stage Audit

Next stage:

```text
V4.2-B/C Controlled Execution Runtime / 受控执行运行时
```

Required audit before implementation:

```text
source=agent cannot execute mutation
user confirmation required
high-risk action approval-gated
EventBridge refresh-only
executor reads only redacted or approved inputs
generic workflow start acceptance
generic station rerun acceptance
attempt history and downstream stale acceptance
timeout and kill switch acceptance
runtime evidence acceptance
```

Proceed decision:

```text
proceed_to_next_stage_audit
```

## 9. No False Green Statement

V4.2-A only proves the Headless Interaction Pivot baseline for local workflow validation.

It does not prove:

```text
does not prove controlled executor
does not prove Agent executor
does not prove complete Workflow Studio
does not prove complete AgentTalkWindow
does not prove full multi-Agent orchestration
does not prove generic station rerun
does not prove generic controlled runtime
does not prove production-ready external app support
```

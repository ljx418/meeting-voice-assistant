# V4.2-C Controlled Runtime MVP Completion Note

Status: complete.

## 1. Allowed Claim

```text
V4.2-C complete: controlled runtime MVP ready for dev/local validation.
```

## 2. Forbidden Claims

```text
forbidden controlled executor ready
forbidden Agent executor ready
forbidden autonomous workflow editing ready
forbidden production-ready external app support
forbidden full multi-Agent orchestration ready
forbidden complete Workflow Studio ready
```

## 3. Implementation Evidence

Added:

```text
apps/api/routers/bff_v42.py
tests/test_v4_2_controlled_runtime_bff.py
tests/test_v4_2_controlled_runtime_evidence.py
scripts/v4_2_controlled_runtime_evidence.py
apps/workflow-console/src/__tests__/controlledRuntimeMVP.test.tsx
docs/design/V4.2/v4_2_c_controlled_runtime_mvp_plan.md
docs/design/V4.2/v4_2_c_controlled_runtime_mvp_acceptance.md
docs/design/V4.2/v4_2_c_controlled_runtime_mvp_audit.md
docs/design/V4.2/v4_2_c_controlled_runtime_mvp_completion_note.md
docs/design/V4.2/evidence/controlled-runtime/
```

Updated:

```text
apps/api/__init__.py
apps/workflow-console/src/api/types.ts
apps/workflow-console/src/api/workflowConsoleClient.ts
docs/design/V4.2/00_README.md
docs/design/V4.x/v4_x_headless_current_gap_analysis.md
docs/design/V4.x/v4_x_headless_first_roadmap.md
```

## 4. Verified Behavior

1. Controlled runtime start requires `user_confirmed=true`.
2. Controlled runtime rerun requires `user_confirmed=true`.
3. `source=agent` is rejected.
4. Failed Markdown parse preserves the old failed attempt.
5. Rerun creates a new completed attempt.
6. Downstream stations are marked stale.
7. Downstream continuation requires user confirmation.
8. Runtime evidence includes real runtime refs.
9. Timeout and kill switch baseline are visible in evidence.
10. Reports are generated from runtime result.
11. Browser client uses `/bff/v4_2/runtime/*`.

## 5. Validation Commands

```text
./.venv/bin/python -m pytest tests/test_v4_2_controlled_runtime_*.py -q
Result: PASS, 15 passed, 5 warnings

./.venv/bin/python -m pytest tests/test_v4_2_*.py -q
Result: PASS, 37 passed, 5 warnings

cd apps/workflow-console && npm test -- --runInBand
Result: PASS, 77 passed

xmllint --noout docs/design/V4.2/evidence/controlled-runtime/workflow_status.drawio
Result: PASS

xmllint --noout docs/design/V4.2/evidence/controlled-runtime/rerun_history.drawio
Result: PASS

./.venv/bin/python -m pytest tests/test_v4_1_*.py -q
Result: PASS, 7 passed, 5 warnings

./.venv/bin/python -m pytest tests/test_v4_0_*.py -q
Result: PASS, 215 passed, 5 warnings

./.venv/bin/python -m pytest -q
Result: PASS, 700 passed, 3 skipped, 6 warnings

cd apps/workflow-console && npm run build
Result: PASS

cd apps/workflow-console && npm run test:e2e
Result: PASS, 23 passed

xmllint --noout docs/design/V4.x/v4_x_headless_current_gap_analysis.drawio
Result: PASS
```

## 6. Spec Drift Evaluation

Risk: LOW

Evidence: V4.2-C implements only dev/local controlled runtime MVP over the local knowledge workflow fixture and does not add Agent executor or production controls.

## 7. False Green Evaluation

Risk: LOW

Evidence: The evidence package records real scenario A/B results and keeps unsupported capabilities in forbidden claim context.

## 8. Next Stage Audit

Next stage:

```text
V4.3 Serial Multi-Agent Video Workflow MVP / 串行多 Agent 视频工作流 MVP
```

Preimplementation audit:

```text
docs/design/V4.3/v4_3_serial_multi_agent_video_workflow_preimplementation_audit.md
```

Spec drift risk:

```text
MEDIUM
```

False green risk:

```text
MEDIUM
```

Proceed decision:

```text
proceed_with_caution_after_user_or_planning_review
```

## 9. No False Green Statement

V4.2-C proves only a dev/local controlled runtime MVP for start, station rerun, attempt history, downstream stale, evidence, and report regeneration. It does not prove Agent executor, controlled executor, autonomous workflow editing, production-ready external app support, full multi-Agent orchestration, or complete Workflow Studio.

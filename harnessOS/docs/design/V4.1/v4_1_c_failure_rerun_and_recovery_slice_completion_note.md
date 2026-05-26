# V4.1-C Failure Rerun And Recovery Slice / 失败重跑与刷新恢复切片 Completion Note

Status: completed for local folder summary workflow validation.

## Allowed Claim

V4.1-C complete: failure rerun and recovery slice ready for local folder summary workflow validation.

## Forbidden Claims

- controlled executor ready
- Agent executor ready
- generic station.rerun ready
- complete Workflow Studio ready
- production-ready external app support
- full multi-Agent orchestration ready

## Actual Files Changed

- `apps/api/routers/bff_v41.py`
- `apps/workflow-console/src/api/types.ts`
- `apps/workflow-console/src/api/workflowConsoleClient.ts`
- `apps/workflow-console/src/hooks/useWorkflowConsoleData.ts`
- `apps/workflow-console/src/components/ConsoleShell.tsx`
- `apps/workflow-console/src/App.tsx`
- `tests/test_v4_1_folder_summary_bff.py`
- `tests/fixtures/desktop/技术分享_损坏/损坏/坏文件.md`

## Verified Behavior

- Broken Markdown fixture creates a deterministic `markdown_parse` failure.
- Rerun requires `user_confirmed=true`.
- Rerun source must be `run_panel`; `source=agent` is rejected.
- Rerun creates a new attempt.
- Old failed attempt and old error remain visible.
- Refresh recovery restores the V4.1 folder summary run, node status, artifacts, quality report, and governance state through BFF readback.
- No generic `station.rerun` executor route was added.

## Validation Commands

```bash
./.venv/bin/python -m pytest tests/test_v4_1_folder_summary_bff.py -q
```

Result: passed, 7 tests.

```bash
cd apps/workflow-console && CI=1 npx playwright test e2e/workflow-folder-summary-acceptance.spec.ts --project=chromium
```

Result: passed, Case 7 and Case 8 marked PASS.

## Spec Drift Evaluation / 规格漂移评估

- risk_level: LOW
- evidence: Rerun is scoped to `/bff/v4_1/folder-summary/instances/{workflow_instance_id}/rerun-node` and only supports `markdown_parse` for this local workflow slice.
- decision: proceed

## False Green Evaluation / 虚假验收评估

- risk_level: LOW
- evidence: Backend tests prove source guard and attempt history. Browser evidence proves visible error, rerun, and attempt history.
- decision: proceed

## Next Stage Audit / 下一阶段审计

- next_stage_name: V4.1-D Governance Evidence Chain Slice / 治理证据链切片
- prerequisites_met: Apply, publish, run, rerun operations are user-confirmed and observable.
- blocked_items: none
- plan_revision_required: no
- proceed_decision: proceed

## No False Green

V4.1-C proves only V4.1 local Markdown workflow failure rerun and refresh recovery. It does not prove controlled executor or generic rerun runtime.

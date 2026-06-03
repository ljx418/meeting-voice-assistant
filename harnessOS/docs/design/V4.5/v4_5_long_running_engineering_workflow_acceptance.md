# V4.5 Long-Running Engineering Workflow MVP Acceptance

Required evidence:

```text
docs/design/V4.5/evidence/engineering-workflow/
```

Required outputs:

```text
tui-transcript.txt
engineering_workflow.json
engineering_workflow.yaml
engineering_board.drawio
engineering_status.drawio
engineering_artifact_lineage.drawio
durable_task_board.html
stage_artifacts.html
quality_gate_report.html
evidence_chain.html
rerun_history.html
runtime-result.json
attempt-history.json
downstream-stale.json
operation-evidence.json
result-summary.md
```

Acceptance:

1. 11 engineering stages exist in required order.
2. Every stage has an artifact.
3. Quality gate report is generated.
4. Code review rerun requires user confirmation.
5. Rerun marks E2E acceptance and human confirmation stale.
6. Downstream continuation requires user confirmation.
7. Reports are read-only.
8. No real code modification is performed.
9. `source=agent` cannot mutate.


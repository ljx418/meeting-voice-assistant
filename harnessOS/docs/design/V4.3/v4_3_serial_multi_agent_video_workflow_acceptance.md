# V4.3 Serial Multi-Agent Video Workflow MVP Acceptance

## Required Evidence Path

```text
docs/design/V4.3/evidence/serial-video-workflow/
```

Required outputs:

```text
tui-transcript.txt
video_workflow.yaml
video_workflow.json
video_workflow.schema.json
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

## Acceptance Cases

1. Create serial video WorkflowSpec.
2. Validate six stations in order:
   - writer_agent
   - storyboard_agent
   - copywriting_agent
   - editing_plan_agent
   - quality_review_agent
   - publish_preparation_agent
3. Validate every station has AgentDescriptor metadata.
4. Start workflow with `user_confirmed=true`.
5. Reject start or rerun when `source=agent`.
6. Generate six station artifacts.
7. Simulate middle station failure at `storyboard_agent`.
8. Rerun `storyboard_agent` with user confirmation.
9. Preserve old failed attempt and add a completed attempt.
10. Mark downstream stations stale.
11. Continue downstream with user confirmation.
12. Regenerate read-only HTML reports.
13. Validate Drawio XML.
14. Validate no token, secret, raw payload, or false-green claim leaks.

## Required Commands

```text
./.venv/bin/python scripts/v4_3_serial_video_evidence.py
./.venv/bin/python -m pytest tests/test_v4_3_*.py -q
xmllint --noout docs/design/V4.3/evidence/serial-video-workflow/video_workflow.drawio
xmllint --noout docs/design/V4.3/evidence/serial-video-workflow/video_workflow_status.drawio
xmllint --noout docs/design/V4.3/evidence/serial-video-workflow/video_artifact_lineage.drawio
```

## No False Green

V4.3 acceptance does not prove Agent executor, complete Workflow Studio, controlled executor, production external app support, or full multi-Agent orchestration.


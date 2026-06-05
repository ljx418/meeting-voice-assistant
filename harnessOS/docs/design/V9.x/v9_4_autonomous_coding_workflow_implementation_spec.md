# V9-4 Autonomous Coding Workflow Pilot Implementation Spec

文档状态：V9-4 implementation-readiness spec / planned only。

## 1. Boundary

V9-4 targets an autonomous coding workflow pilot with human-reviewed outputs. It does not allow auto commit, auto push, auto deploy, unreviewed patch apply, or unrestricted terminal worker behavior.

Allowed claim:

```text
V9-4 complete: autonomous coding workflow pilot ready for review.
```

Forbidden interpretations:

```text
autonomous coding workflow ready
Agent executor ready
unrestricted terminal worker ready
production terminal automation ready
```

## 2. Workflow Stages

```text
IntentCapture
SpecDraft
PlanDraft
CodeDiffProposal
TestPlanProposal
SandboxedTestRun
ReviewSummary
FixLoopProposal
HumanReviewHandoff
EvidenceRecorded
```

## 3. Hard Boundaries

```text
No auto commit.
No auto push.
No auto deploy.
No unreviewed patch apply.
No production credential read.
No workspace escape.
source=agent direct durable mutation denied.
```

## 4. Evidence Artifact Format

Required evidence:

```text
coding_workflow_run_id
goal_ref
plan_ref
diff_proposal_ref
test_plan_ref
test_result_ref
review_summary_ref
fix_loop_ref
human_review_handoff_ref
workspace_scope_ref
redaction_status
claim_scan_status
correlation_id
request_id
audit_ref
```

## 5. Acceptance Tests

```text
coding_workflow_generates_diff_proposal
coding_workflow_generates_test_plan
coding_workflow_runs_sandboxed_tests
coding_workflow_records_review_summary
coding_workflow_fix_loop_records_new_diff_proposal
coding_workflow_no_auto_commit
coding_workflow_no_auto_push
coding_workflow_no_auto_deploy
coding_workflow_unreviewed_patch_apply_denied
coding_workflow_workspace_escape_denied
coding_workflow_secret_read_denied
```

## 6. Stop Conditions

```text
commit is created without human approval.
push is executed without release gate.
deploy is executed without production gate.
patch is applied without review handoff.
raw secret / raw prompt / raw file content appears in evidence.
```

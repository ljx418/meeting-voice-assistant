# V9-4 Coding Workflow Runtime Engineering Design

文档状态：V9-4 engineering design / planned only。

## 1. Runtime Boundary

V9-4 creates a coding workflow pilot that generates plans, diff proposals, tests, review summaries and fix-loop proposals. It must not auto commit, auto push, auto deploy or apply unreviewed patches.

## 2. Workflow Runtime

```text
IntentCapture
SpecDraft
PlanDraft
DiffProposal
TestPlanProposal
SandboxedTestRun
ReviewSummary
FixLoopProposal
HumanReviewHandoff
EvidenceRecorded
```

## 3. Git Operation Deny Policy

Denied by default:

```text
git commit
git push
git tag
production deploy
release publish
```

Allowed only as proposal:

```text
commit_message_proposal
patch_diff_proposal
release_note_proposal
deploy_plan_proposal
```

## 4. Sandbox Rules

```text
tests run in workspace-scoped sandbox.
secret reads denied.
workspace escape denied.
raw file content not copied into evidence.
diff proposal is separate from patch apply.
fix-loop creates a new diff proposal.
review summary cannot become approval.
```

## 5. Evidence Package

```text
coding_workflow_run_id
intent_ref
spec_ref
plan_ref
diff_proposal_ref
test_plan_ref
test_result_ref
review_summary_ref
fix_loop_ref
human_review_handoff_ref
git_operation_deny_report_ref
redaction_status
claim_scan_status
```

## 6. Acceptance Tests

```text
coding_workflow_diff_proposal_created
coding_workflow_test_plan_created
coding_workflow_sandboxed_tests_run
coding_workflow_review_summary_created
coding_workflow_fix_loop_creates_new_diff
coding_workflow_no_auto_commit
coding_workflow_no_auto_push
coding_workflow_no_auto_deploy
coding_workflow_unreviewed_patch_apply_denied
coding_workflow_secret_read_denied
```

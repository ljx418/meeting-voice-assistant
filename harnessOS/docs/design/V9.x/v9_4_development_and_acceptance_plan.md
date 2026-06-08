# V9-4 Development And Acceptance Plan

文档状态：V9-4 detailed development and acceptance plan / implementation complete for review.

This document now records the V9-4 stage plan and the completed bounded runtime evidence package. It does not authorize V9-5 runtime implementation or any over-readiness claim.

## 1. Entry Baseline

V9-4 entered implementation after:

```text
V9-3 orchestration runtime evidence PASS.
V9-3 user scenarios US-V9-02 / US-V9-07 / US-V9-08 have PASS or accepted PARTIAL.
V9-4 coding workflow runtime engineering design accepted.
No False Green scan PASS.
Redaction scan PASS.
human high-risk proceed decision recorded for autonomous coding workflow pilot.
```

V9-4 completion evidence:

```text
docs/design/V9.x/evidence/v9-4-coding-workflow-runtime/acceptance-data.json
docs/design/V9.x/evidence/v9-4-coding-workflow-runtime/index.html
docs/design/V9.x/evidence/v9-4-coding-workflow-runtime/result-summary.md
```

## 2. Scope

V9-4 implements a bounded coding workflow pilot:

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

V9-4 must not:

```text
apply patches without review.
commit, push or deploy automatically.
turn review summary into approval.
allow source=agent direct durable mutation.
claim autonomous coding workflow completion beyond pilot ready for review.
```

## 3. Implementation Slices

| Slice | Output | Acceptance |
| --- | --- | --- |
| V9-4A Coding workflow run model | coding_workflow_run record | goal, plan, diff, test, review and handoff refs exist |
| V9-4B Diff proposal path | diff_proposal artifact | proposal_only=true and applied=false |
| V9-4C Sandboxed test runner | sandboxed_test_result record | command refs, exit status and redacted log refs recorded |
| V9-4D Review and fix loop | review_summary and fix_loop records | review is not approval; fix loop creates a new proposal |
| V9-4E Git and deployment deny policy | deny evidence records | auto commit / push / deploy attempts denied |
| V9-4F Evidence dashboard | HTML and acceptance data | user can inspect plan, diff, test, review and denial evidence |

## 4. Required Fixtures

Positive fixture:

```text
fixtures/v9-4-coding-workflow/small_code_change_proposal.json
```

Negative fixtures:

```text
fixtures/coding/auto_commit_without_human_approval.json
fixtures/coding/auto_push_without_release_gate.json
fixtures/coding/auto_deploy_without_production_gate.json
fixtures/coding/unreviewed_patch_apply_attempt.json
fixtures/coding/review_summary_as_approval_attempt.json
```

## 5. Acceptance Tests

```text
v9_4_coding_workflow_creates_plan_diff_test_review_and_handoff
v9_4_diff_proposal_is_not_patch_apply
v9_4_sandboxed_test_result_records_exit_status_and_log_ref
v9_4_review_summary_is_not_approval
v9_4_fix_loop_creates_new_diff_proposal
v9_4_auto_commit_denied
v9_4_auto_push_denied
v9_4_auto_deploy_denied
v9_4_source_agent_direct_mutation_denied
v9_4_claim_scan_pass
v9_4_redaction_scan_pass
```

## 6. Evidence Package

V9-4 completion evidence must include:

```text
acceptance-data.json
index.html
result-summary.md
coding_workflow_run_ref
diff_proposal_ref
sandboxed_test_result_ref
review_summary_ref
fix_loop_ref
human_review_handoff_ref
git_operation_deny_report_ref
claim_scan_result
redaction_scan_result
```

## 7. Stop Conditions

```text
Patch is applied before review.
Commit, push or deploy happens automatically.
Review summary is counted as approval.
Fix loop silently edits previous artifacts.
Source=agent directly mutates durable runtime truth.
Evidence stores sensitive content instead of redacted refs.
Stage is claimed complete without runnable coding workflow evidence.
V9-4 evidence is reused to claim autonomous coding workflow ready.
V9-4 evidence alone is reused to authorize V9-5 runtime implementation without a separate V9-5 high-risk decision.
```

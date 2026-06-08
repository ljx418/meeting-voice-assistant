# V9 Development And Acceptance Plan

文档状态：V9 development and acceptance control plan / V9-8 final acceptance evidence-aligned baseline。

## 0. Current V9 Control Baseline

```text
V9-0 complete: high-risk execution planning gate ready for review.
V9-1 complete: Agent Executor Safety Gate implementation ready for review.
V9-2 complete: limited controlled Agent executor runtime slice ready for review.
V9-3 complete: multi-Agent orchestration runtime slice ready for review.
V9-4 complete: autonomous coding workflow pilot ready for review.
V9-5 complete: governed terminal worker expansion ready for review.
V9-6 complete: Workflow Studio productization slice ready for review.
V9-7 complete: production governance and terminal automation gate ready for review.
V9 complete: high-risk Agent execution and workflow productization baseline ready for review.
```

当前允许的 V9-2 证据解释：

```text
evidence_scope=real_runtime_fixture
runtime_backed=true
allowed_operations=[workflow.instance.start, station.rerun, artifact.write, quality.evaluation.create]
source=agent durable mutation denied
runtime_executor_route_created=false
runtime_worker_created=false
```

当前下一门禁候选：

```text
V9-8 Final Acceptance PASS evidence review
```

V9-3 已产出 bounded real_runtime_fixture evidence。V9-4 已产出 bounded coding workflow real_runtime_fixture evidence。V9-5 已产出 governed terminal worker real_runtime_fixture evidence。V9-6 已产出 Workflow Studio productization real_runtime_fixture evidence。V9-7 已产出 production governance / evidence hardening real_runtime_fixture evidence。V9-8 final acceptance validator 已实现并生成 PASS 看板；US-V9-08 provider-backed storyboard image evidence 已补齐，最终声明允许为 ready for review 范围。

V9-8 final acceptance 还必须通过用户场景验收门槛：

```text
docs/design/V9.x/v9_user_scenario_acceptance_gate.md
```

## 1. Stage Status Table

| Stage | Purpose | Current Status | Allowed Claim | Boundary |
| --- | --- | --- | --- | --- |
| V9-0 | Planning And High-Risk Boundary Gate | complete_for_review | V9-0 complete: high-risk execution planning gate ready for review. | documentation only |
| V9-1 | Agent Executor Safety Gate | complete_for_review | V9-1 complete: Agent Executor Safety Gate implementation ready for review. | validator / safety gate only |
| V9-2 | Controlled Agent Executor Runtime | complete_for_review | V9-2 complete: limited controlled Agent executor runtime slice ready for review. | four-operation runtime fixture only |
| V9-3 | Multi-Agent Orchestration Runtime | complete_for_review | V9-3 complete: multi-Agent orchestration runtime slice ready for review. | not full orchestration GA |
| V9-4 | Autonomous Coding Workflow Pilot | complete_for_review | V9-4 complete: autonomous coding workflow pilot ready for review. | no auto commit / auto push / auto deploy |
| V9-5 | Governed Terminal Worker Expansion | complete_for_review | V9-5 complete: governed terminal worker expansion ready for review. | not unrestricted shell |
| V9-6 | Workflow Studio Productization | complete_for_review | V9-6 complete: Workflow Studio productization slice ready for review. | not complete Studio GA |
| V9-7 | Production Governance / Evidence Hardening and Terminal Automation Gate | complete_for_review | V9-7 complete: production governance and terminal automation gate ready for review. | not production automation ready |
| V9-8 | Final Acceptance | complete_for_review | V9 complete: high-risk Agent execution and workflow productization baseline ready for review. | not production ready / not Agent executor ready / not full orchestration ready |

## 2. Development Order

```text
V9-0 -> V9-1 -> V9-2 -> V9-3 -> V9-4 -> V9-5 -> V9-6 -> V9-7 -> V9-8
```

V9-1、V9-2、V9-3、V9-4、V9-5、V9-6、V9-7 已完成受限证据闭环。V9-8 validator 已实现且 PASS；US-V9-08 真实 provider-backed 图像证据已补齐。当前下一动作是外部审计 V9 final evidence package，不作生产能力声明。

## 2.1 Next Development Order After V9-2

```text
V9-3 orchestration runtime evidence package PASS
 -> V9-3 user scenario acceptance package PASS with provider-backed storyboard image generation evidence
 -> V9-3 PRD/spec review PASS
 -> V9-4 readiness audit PASS
 -> V9-4 coding workflow runtime evidence PASS
 -> V9-5 governed terminal worker evidence PASS
 -> V9-6 Workflow Studio evidence PASS
 -> V9-7 production governance evidence PASS
 -> V9-8 final acceptance validator PASS with US-V9-08 provider-backed image evidence
```

V9-3 必须产生真实 runtime fixture，覆盖：

```text
serial station dependency
parallel branch independent state
fan-out dispatch
fan-in join / synthesis
lost worker recovery
failure retry without overwriting old attempt
artifact lineage with producer_agent_id and producer_attempt_id
incident / evidence chain refs
user-facing orchestration dashboard / report
Roman Forum debate user scenario with role-specific Agents and attributed synthesis
video storyboard workflow user scenario with storyboard artifacts and provider evidence boundary
natural-language workflow optimization user scenario with WorkflowDiff proposal before mutation
```

V9-3 已产出证据：

```text
docs/design/V9.x/evidence/v9-3-orchestration-runtime/acceptance-data.json
docs/design/V9.x/evidence/v9-3-orchestration-runtime/index.html
docs/design/V9.x/evidence/v9-3-orchestration-runtime/result-summary.md
```

V9-3 implementation package 已补齐：

```text
docs/design/V9.x/v9_3_development_and_acceptance_plan.md
docs/design/V9.x/schemas/v9_3_*.schema.json
docs/design/V9.x/fixtures/v9-3-orchestration/
```

V9-4..V9-8 detailed development and acceptance plans are now available as stage audit inputs:

```text
docs/design/V9.x/v9_4_development_and_acceptance_plan.md
docs/design/V9.x/v9_5_development_and_acceptance_plan.md
docs/design/V9.x/v9_6_development_and_acceptance_plan.md
docs/design/V9.x/v9_7_development_and_acceptance_plan.md
docs/design/V9.x/v9_8_development_and_acceptance_plan.md
```

V9-4 readiness closure evidence:

```text
docs/design/V9.x/evidence/v9-4-readiness-closure/pre-implementation-data.json
docs/design/V9.x/evidence/v9-4-readiness-closure/index.html
docs/design/V9.x/evidence/v9-4-readiness-closure/result-summary.md
```

V9-4 runtime evidence:

```text
docs/design/V9.x/evidence/v9-4-coding-workflow-runtime/acceptance-data.json
docs/design/V9.x/evidence/v9-4-coding-workflow-runtime/index.html
docs/design/V9.x/evidence/v9-4-coding-workflow-runtime/result-summary.md
```

These documents support stage-by-stage implementation planning and stage audit only. They do not authorize skipping V9-3 PASS, high-risk human decisions, runtime evidence packages or V9-8 final acceptance gates.

V9-5 completion evidence:

```text
docs/design/V9.x/evidence/v9-5-terminal-worker/acceptance-data.json
docs/design/V9.x/evidence/v9-5-terminal-worker/index.html
docs/design/V9.x/evidence/v9-5-terminal-worker/result-summary.md
```

V9-5 does not authorize broad terminal runtime, unrestricted shell, production deploy, git push, browser account automation or unscoped write actions.

V9-6 completion evidence:

```text
docs/design/V9.x/evidence/v9-6-workflow-studio/acceptance-data.json
docs/design/V9.x/evidence/v9-6-workflow-studio/index.html
docs/design/V9.x/evidence/v9-6-workflow-studio/result-summary.md
```

V9-6 does not authorize complete Workflow Studio readiness, direct runtime truth writes, hidden mutation forms, direct browser internal runtime calls or automatic Agent execution.

V9-7 completion evidence:

```text
docs/design/V9.x/evidence/v9-7-production-governance/acceptance-data.json
docs/design/V9.x/evidence/v9-7-production-governance/index.html
docs/design/V9.x/evidence/v9-7-production-governance/result-summary.md
```

V9-7 does not authorize production automation ready, production terminal automation ready, production browser automation ready, raw credential access, mutable audit export or unrestricted terminal/browser automation.

V9-8 final acceptance evidence:

```text
docs/design/V9.x/evidence/v9-8-final-acceptance/v9-final-acceptance-dashboard.html
docs/design/V9.x/evidence/v9-8-final-acceptance/v9-final-acceptance-data.json
docs/design/V9.x/evidence/v9-8-final-acceptance/v9-final-result-summary.md
docs/design/V9.x/evidence/v9-3-orchestration-runtime/storyboard-provider-evidence.json
```

Provider-backed storyboard image generation was completed through MiniMax. The evidence records four storyboard image artifacts, provider/model/invocation refs, artifact hashes and redaction flags. It does not store raw credentials, raw prompts, raw provider payloads, raw provider responses or base64 images.

## 3. Implementation Readiness Requirements

Before V9-1:

```text
V9-0 accepted.
AgentExecutionPolicy contract accepted.
AgentExecutionEnvelope contract accepted.
CapabilityResolver safety matrix accepted.
Approval / kill switch / timeout / rollback contract accepted.
No False Green guard accepted.
P0 schema files parse.
P0 negative fixtures parse.
V9 front-stage readiness audit accepted.
```

Before V9-2:

```text
V9-1 accepted.
Controlled executor action allowlist accepted.
Durable mutation user confirmation policy accepted.
Durable mutation invariant accepted: user_confirmed=true OR valid human_authorization_ref.
HumanAuthorizationRef contract accepted.
source=agent default durable mutation denial accepted.
Execution evidence schema accepted.
Redaction and secret boundary accepted.
V9-1 runtime evidence PASS.
```

Before V9-3:

```text
V9-2 evidence PASS and remains bounded to limited controlled runtime slice.
Agent message protocol accepted.
Attempt history and artifact lineage contracts accepted.
Serial, parallel, fan-in and fan-out contracts accepted.
Failure recovery and lost worker recovery matrix accepted.
producer_agent_id and producer_attempt_id lineage requirements accepted.
V9-2 runtime evidence PASS.
No False Green scan PASS.
V9-3 E2E fixture design accepted.
```

Before V9-4:

```text
V9-2 and V9-3 evidence PASS.
Coding workflow sandbox contract accepted.
Diff / test / review / fix loop accepted.
No auto commit / push / deploy policy accepted.
No unreviewed patch apply policy accepted.
V9-2 and V9-3 runtime evidence packages accepted.
V9-4 high-risk human proceed decision recorded.
```

## 3.1 Front-Stage PR Slices

```text
V9-1A schema and contract validator
V9-1B CapabilityResolver deny-by-default validator
V9-1C HumanAuthorizationRef validation hook
V9-1D negative fixture runner and evidence package
V9-2A controlled executor action allowlist
V9-2B idempotency / timeout / rollback chain
V9-2C append-only execution evidence
V9-3A orchestration message protocol
V9-3B branch state and fan-in/fan-out coordinator
V9-3C attempt history and artifact lineage
V9-4A coding workflow sandbox and git deny policy
V9-4B diff / test / review / fix-loop evidence
```

Before V9-5:

```text
V8-6 / V8-7 evidence accepted.
Workspace write sandbox accepted.
Command tier allowlist accepted.
File write policy accepted.
Terminal transcript / diff capture accepted.
```

Before V9-6:

```text
Studio PRD accepted.
BFF route allowlist accepted.
Browser denylist accepted.
Runtime truth boundary accepted.
UI false-green copy scan accepted.
```

Before V9-7:

```text
Tenant / credential / approval / audit / incident / evidence hardening contracts accepted.
Production governance / terminal automation scope accepted.
Browser account automation separate PRD accepted if enabled.
```

## 4. Test Matrix

```text
user_scenario_v9_2_controlled_runtime_review_pass
user_scenario_v9_3_orchestration_review_requires_runtime_evidence
user_scenario_v9_4_coding_workflow_review_blocks_without_diff_test_review
user_scenario_v9_5_terminal_worker_review_blocks_without_sandbox_evidence
user_scenario_v9_6_studio_review_blocks_without_bff_browser_evidence
user_scenario_v9_8_final_review_blocks_if_any_required_scenario_missing
agent_execution_requires_policy_decision
durable_mutation_requires_user_confirmation
durable_mutation_allows_human_authorization_ref
source_agent_direct_mutation_denied_by_default
agent_execution_evidence_redacted
kill_switch_checked_before_action
timeout_marks_attempt_failed
rollback_descriptor_required_for_mutation
multi_agent_parallel_branch_states_independent
multi_agent_fan_in_fan_out_evidence_exists
lost_agent_recovery_retains_old_attempt
artifact_lineage_preserves_producer_agent_and_attempt
roman_forum_debate_preserves_agent_roles_and_attribution
video_storyboard_workflow_records_provider_backed_or_blocked_image_evidence
natural_language_workflow_optimization_requires_diff_and_confirmation
coding_workflow_diff_requires_review
coding_workflow_no_auto_commit
coding_workflow_no_auto_push
coding_workflow_no_auto_deploy
terminal_worker_workspace_escape_denied
terminal_worker_secret_read_denied
studio_browser_no_direct_runtime_truth
studio_hidden_mutation_form_absent
production_terminal_automation_requires_high_risk_gate
v9_no_false_green_scan_pass
v9_redaction_scan_pass
```

## 5. Validation Commands

```text
xmllint --noout docs/design/V9.x/v9_current_gap_analysis.drawio
rg -in "production[- ]?ready|full production GA|GA ready|Agent executor ready|controlled executor ready|production controlled executor ready|full multi-Agent orchestration ready|distributed multi-Agent runtime ready|autonomous coding workflow ready|autonomous workflow editing ready|complete Workflow Studio ready|unrestricted terminal worker ready|production terminal automation ready|production browser automation ready|production automation ready|生产可用|全面生产可用|生产就绪|可投产|正式发布|生产级可用|Agent执行器已完成|Agent Executor 已完成|受控执行器已完成|生产级受控执行器已完成|完整多Agent编排已完成|多智能体编排已完成|自主代码工作流已完成|自主工作流编辑已完成|完整工作流工作台已完成|无限制终端worker已完成|生产终端自动化已完成|生产浏览器自动化已完成|生产自动化已完成" docs/design/V9.x
```

The claim scan may find forbidden terms only inside explicit forbidden/no-false-green contexts.

## 6. Stop Conditions

```text
V9 docs retroactively upgrade V8 to production ready.
Any V9 document claims Agent executor ready outside forbidden/no-false-green context.
Any stage allows source=agent default durable mutation.
Terminal worker is designed as unrestricted arbitrary shell.
Studio directly writes runtime truth.
Credential raw secret appears in evidence.
V9-8 final claim emitted before V9-0..V9-7 evidence exists.
```

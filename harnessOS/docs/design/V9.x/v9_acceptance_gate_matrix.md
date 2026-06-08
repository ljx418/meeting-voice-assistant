# V9 Acceptance Gate Matrix

文档状态：V9 acceptance control matrix / V9-8 final acceptance evidence-aligned baseline。

| Stage | Entry Gate | Acceptance Gate | Stop Condition |
| --- | --- | --- | --- |
| V9-0 | V8 final baseline accepted as bounded | PRD, architecture, gap, drawio, plan and claim guard accepted; status complete_for_review | V9-0 claims runtime complete |
| V9-1 | V9-0 accepted | Safety gate validators, negative fixtures, No False Green scan and redaction scan PASS; status complete_for_review | Agent executor ready is claimed |
| V9-2 | V9-1 PASS and human high-risk decision recorded | four allowlisted runtime operations prove policy decision, approval evidence, durable mutation invariant, idempotency, redacted execution evidence and source=agent denial; status complete_for_review | source=agent mutates by default or durable mutation runs without user_confirmed=true OR valid human_authorization_ref |
| V9-3 | V9-2 PASS and V9-3 readiness audit accepted | serial, parallel, fan-in, fan-out, failure recovery, lost worker recovery, attempt history, artifact lineage, producer_agent_id and producer_attempt_id evidence exist; status complete_for_review | full multi-Agent orchestration is claimed without complete evidence |
| V9-4 | V9-2 / V9-3 PASS and V9-4 high-risk human decision recorded | coding workflow produces diff, test, review, fix-loop and evidence with sandbox boundary | auto commit / auto push / auto deploy occurs without approval; automated tooling applies patches, commits, pushes, deploys, or marks review as approval |
| V9-5 | V8-6/V8-7 evidence, V9-4 PASS and new human decision | terminal worker command tiers, transcript, diff capture and denial evidence exist; status complete_for_review | unrestricted shell is allowed |
| V9-6 | Studio PRD and BFF boundary accepted | Studio UI operates through DTO/BFF, passes browser denylist, records WorkflowDiff proposal and manual confirmation evidence; status complete_for_review | Studio directly writes runtime truth |
| V9-7 | production governance / evidence hardening spec and human decision | governance, evidence hardening and terminal automation gate evidence exists; status complete_for_review | browser/terminal automation runs without credential, approval, evidence and incident boundary |
| V9-8 | V9-0..V9-7 evidence exists and user scenario acceptance gate reviewed | final dashboard, user scenario dashboard, claim scan, redaction scan and drawio XML pass | final claim emitted while any stage or user scenario is BLOCKED |

## Current Evidence Status

| Stage | Evidence Path | Status | Scope |
| --- | --- | --- | --- |
| V9-1 | `docs/design/V9.x/evidence/v9-1-safety-gate-implementation/acceptance-data.json` | PASS | real_code_policy_validation; runtime_backed=false |
| V9-2 | `docs/design/V9.x/evidence/v9-2-controlled-executor-runtime/acceptance-data.json` | PASS | real_runtime_fixture; runtime_backed=true; four operations only |
| V9-3 | `docs/design/V9.x/evidence/v9-3-orchestration-runtime/acceptance-data.json` | PASS | real_runtime_fixture; runtime_backed=true; bounded orchestration only |
| V9-4 | `docs/design/V9.x/evidence/v9-4-coding-workflow-runtime/acceptance-data.json` | PASS | real_runtime_fixture; runtime_backed=true; proposal-only coding workflow with sandboxed test and denial evidence |
| V9-5 | `docs/design/V9.x/evidence/v9-5-terminal-worker/acceptance-data.json` | PASS | real_runtime_fixture; runtime_backed=true; workspace-scoped command tiers, transcript, diff capture and denial evidence |
| V9-6 | `docs/design/V9.x/evidence/v9-6-workflow-studio/acceptance-data.json` | PASS | real_runtime_fixture; runtime_backed=true; BFF/DTO read models, browser denylist, read-only panels, WorkflowDiff proposal and manual confirmation |
| V9-7 | `docs/design/V9.x/evidence/v9-7-production-governance/acceptance-data.json` | PASS | real_runtime_fixture; runtime_backed=true; tenant isolation, credential lease, audit export, incident timeline, evidence hardening and automation denial |
| V9-8 | `docs/design/V9.x/evidence/v9-8-final-acceptance/v9-final-acceptance-data.json` | PASS | final validator PASS; US-V9-08 provider-backed storyboard image evidence recorded with four image artifacts |

## Global Acceptance Requirements

```text
No production ready claim.
No full production GA claim.
No Agent executor ready claim in V9, including final acceptance, unless a separate future readiness gate exists.
No full multi-Agent orchestration ready claim in V9, including final acceptance, unless a separate future readiness gate exists.
No autonomous coding workflow ready claim without sandbox, review and rollback evidence.
No complete Workflow Studio ready claim without separate Studio acceptance.
No unrestricted terminal worker.
No raw secret / raw prompt / raw artifact content leakage.
Durable mutation denied unless user_confirmed=true OR valid human_authorization_ref is present.
source=agent default durable mutation always denied.
```

## User Scenario Acceptance Gate

V9 final acceptance must include a user-facing scenario gate in addition to technical gates.

| Scenario | Owner Stage | User-Facing Acceptance |
| --- | --- | --- |
| US-V9-01 | V9-2 | 技术负责人打开 V9-2 controlled runtime dashboard，核对四类 allowed operations、excluded operations、source=agent denial 和 evidence chain。 |
| US-V9-02 | V9-3 | 用户输入“让多个 Agent 评审本地技术方案并合成结论”，看见 3 个 station-bound Agents、fan-out/fan-in、recovery、attempt history 和 artifact lineage。 |
| US-V9-03 | V9-4 | 开发者输入“小型代码修改任务”，看见 plan、diff proposal、sandboxed test、review summary、fix-loop proposal，并验证 no auto commit/push/deploy/unreviewed patch apply。 |
| US-V9-04 | V9-5 | 审计者要求 Agent 运行 workspace-scoped 检查命令，看见 command tier、transcript、diff capture、workspace escape denial 和 secret-read denial。 |
| US-V9-05 | V9-6 | 产品使用者在 Studio 查看 workflow graph、station Agent profile、runtime status、artifact lineage、Runtime Report 和 Evidence Chain。 |
| US-V9-06 | V9-8 | 最终验收人打开 V9 final dashboard，确认每阶段和每个用户场景的 status、claim scan、redaction scan 和 drawio XML result。 |
| US-V9-07 | V9-3 | 用户发起“罗马广场”哲学讨论，看见哲学家、工程师、历史学家、伦理学家等 role-specific Agents 多轮发言、互相引用和 attribution-preserving synthesis。 |
| US-V9-08 | V9-3 / V9-6 | 创作者输入视频点子，看见创作 workflow、brief、script、shot list、storyboard prompts、分镜图 artifact refs、provider/model refs 和 evidence chain。 |
| US-V9-09 | V9-6 | 用户用自然语言优化已有工作流，看见 WorkflowDiff proposal、station/Agent 变化、risk_delta，并确认用户确认前没有 durable mutation。 |

User scenario PASS requires:

```text
dashboard_or_report_ref exists.
evidence_refs exist.
evidence_scope is explicit.
runtime_backed scenarios have real_runtime_fixture or real_runtime evidence.
planning docs / transcript-only / report-only evidence does not satisfy runtime-backed user scenario PASS.
Creative workflow scenes must distinguish real provider-backed artifacts from fallback_demo_only or placeholder outputs.
Natural-language optimization must produce proposal / diff / handoff before mutation.
```

V9-8 would be BLOCKED if any required user scenario is FAIL, BLOCKED or missing without a documented human proceed decision; current generated V9-8 data is PASS.

## Front-Stage Audit Vs Runtime Gates

| Stage | Audit PASS Means | Runtime PASS Requires |
| --- | --- | --- |
| V9-1 | Contract, schema and fixture package accepted | Safety gate validator implemented, negative fixtures exercised, evidence package recorded |
| V9-2 | Controlled executor design accepted | Runtime allowlisted actions execute through policy / authorization / approval / evidence chain |
| V9-3 | Orchestration design accepted | Serial / parallel / fan-in / fan-out runtime evidence with recovery and lineage |
| V9-4 | Coding workflow design accepted | Real sandboxed diff / test / review / fix-loop evidence and no auto commit / push / deploy |

## High-Risk Human Decisions

```text
V9-1 safety gate acceptance
V9-2 controlled Agent executor runtime
V9-4 autonomous coding workflow pilot
V9-5 terminal worker write sandbox
V9-7 production governance / evidence hardening and terminal automation gate
```

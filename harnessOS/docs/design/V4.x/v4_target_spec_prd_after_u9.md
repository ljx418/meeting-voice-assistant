# V4 Target Spec PRD After U9

文档状态：V4-U9 后的 V4 目标规格 PRD 冻结版。本文用于人工验收和外部审计，不新增 V4 功能范围。

## 1. Product Positioning

V4 的产品定位是：

```text
Headless Workflow Core
+ Mission Console
+ Workflow Blueprint
+ Runtime Report
+ Review Console
+ Evidence Chain
```

V4 不是完整 Web 低代码 Studio，也不是生产级 Agent 执行平台。

当前允许声明：

```text
V4-U9 complete: V4 dev/local final human acceptance and V5 handoff package ready for review.
```

## 2. Target User Journey

V4 目标用户路径：

```text
用户说目标
 -> Mission Console 捕获意图
 -> 生成 WorkflowSpec / Diff
 -> Workflow Blueprint 理解结构
 -> 用户确认
 -> Runtime Report 观察运行
 -> Review Console 做局部重跑 / 修复 / 确认
 -> Evidence Chain 审计复盘
```

## 3. UX-01 To UX-12 Target Spec

| UX | Target Experience | Required Evidence |
| --- | --- | --- |
| UX-01 | 自然语言创建工作流 | transcript, WorkflowSpec, Diff, no mutation before confirmation |
| UX-02 | Workflow Blueprint 可视化 | drawio files, XML valid, read-only |
| UX-03 | Runtime Report 运行观察 | workflow board HTML, runtime DTO source |
| UX-04 | Artifact 查看与血缘 | artifact list, producer refs, lineage report |
| UX-05 | Quality 查看 | quality report with station / artifact refs |
| UX-06 | 局部失败修复与重跑 | user_confirmed rerun, attempt history, downstream stale |
| UX-07 | Evidence Chain 审查 | read-only evidence report, no execution buttons |
| UX-08 | 串行多 Agent 视频工作流 | dev/local provider-backed station artifacts |
| UX-09 | 并行罗马广场讨论 | dev/local provider-backed persona artifacts and synthesis |
| UX-10 | 长时工程任务工作流 | dev/local provider-backed staged artifacts and confirmation |
| UX-11 | Agent Workflow Builder | propose / explain / handoff / navigate only |
| UX-12 | 真实 LLM 本地技术文档解析 | authorized local Markdown read, provider-backed summaries |

Every UX case must preserve:

```text
status
evidence_scope
evidence_refs
runtime_backed
false_green_risk
claim_risk
```

## 4. Product Rules

1. WorkflowSpec cannot replace WorkflowDraft / WorkflowVersion runtime truth.
2. Mission Console can propose and handoff, but cannot execute durable mutation as agent.
3. Blueprint / Drawio is visualization only.
4. Runtime Report and HTML Report are read-only.
5. Review Console can initiate user-confirmed handoff only.
6. Evidence Chain is read-only.
7. Durable mutation requires `user_confirmed=true`.
8. EventBridge only triggers refresh.
9. Provider-backed dev/local evidence must not be described as production or distributed runtime.
10. V5 planning cannot retroactively upgrade V4 claims.

## 5. Non-Goals And Forbidden Claims

No False Green：以下完成声明仍然禁止：

```text
complete Workflow Studio ready
complete AgentTalkWindow ready
Agent executor ready
controlled executor ready
production-ready external app support
full multi-Agent orchestration ready
autonomous workflow editing ready
```

V4-U9 does not include:

```text
production auth
production tenant isolation
production credential lifecycle
production observability / audit export
production external app onboarding
distributed multi-agent runtime
full Web Studio productization
```

## 6. PRD Acceptance

The PRD is accepted only if:

```text
UX-01 to UX-12 all have evidence summary
U9 final acceptance data parses
U9 final acceptance report opens
false-green audit is PASS
redaction is PASS
forbidden claims appear only in safe context
V4-R0 to V4-R3 remain closure-only
```

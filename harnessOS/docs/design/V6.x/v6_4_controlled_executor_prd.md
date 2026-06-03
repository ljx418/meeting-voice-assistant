# V6-4 Controlled Executor PRD

文档状态：V6-4 high-risk design contract / pre-implementation audit input。本文定义 V6-4 生产试点受控执行体验，不授权进入实现。

## 1. Current Baseline

```text
V6-1 complete: production identity and tenant boundary pilot slice ready for review.
V6-2 complete: production credential and provider lifecycle pilot slice ready for review.
V6-3 complete: production observability and audit export pilot slice ready for review.
V6-4 complete: limited production controlled executor pilot slice ready for review.
```

## 2. Product Goal

V6-4 目标是把 V5-7B 的 staging controlled executor semantics 推进为 V6 production pilot slice，使用户可以在严格治理边界内执行有限 runtime mutation：

```text
用户或 approved API 发起受控动作
 -> V6-1 identity / tenant / scope guard
 -> V6-2 credential decision ref check
 -> V6-4 policy / action allowlist / approval / kill switch / idempotency
 -> V6-4 pilot runtime state mutation
 -> V6-3 audit event / incident timeline / evidence export refs
 -> Runtime Report / Review Console / Evidence Chain 只读展示
```

## 3. Allowed Claim

```text
V6-4 complete: limited production controlled executor pilot slice ready for review.
```

## 4. Forbidden Claims

```text
production controlled executor ready
controlled executor ready
Agent executor ready
autonomous workflow editing ready
production-ready external app support
complete Workflow Studio ready
```

## 5. In Scope

V6-4 只覆盖四个初始 action：

```text
workflow.instance.start
station.rerun
artifact.write
quality.evaluation.create
```

V6-4 必须支持：

```text
human_user from product_console
service_account_with_human_authorization from approved_api
user_confirmed=true or human_authorization_ref
tenant / workspace / project / app scope guard
action allowlist
approval gate for medium-risk actions
kill switch checked before runtime mutation
idempotency duplicate returns prior execution reference
append-only artifact and quality writes
old attempt retained and downstream stale recorded for station.rerun
V6-3 audit event and incident timeline refs
```

## 6. Out Of Scope

```text
source=agent durable mutation
unrestricted connector.call
unrestricted external_llm.call
business.event.emit
context.update
workflow.template.publish
approval.respond
production runtime worker fleet
production executor route exposed to browser
production secret store access
direct WorkflowDraft / WorkflowVersion / WorkflowStore write
```

## 7. UX Acceptance

用户可体验到：

```text
Review Console 显示一个失败 station。
用户确认 rerun。
系统在 V6-4 pilot runtime state 中保留 old attempt，创建 new attempt，并标记 downstream stale。
Runtime Report 展示新的状态。
Evidence Chain 展示 execution evidence、policy decision、approval gate、kill switch、idempotency、incident timeline refs。
```

用户不能体验到：

```text
Agent 自动 run / rerun / publish / approve。
Evidence Chain 或 Runtime Report 中出现执行按钮。
无确认的 approved API 直接执行。
connector.call 或 external_llm.call 被生产执行器直接调用。
```

## 8. Success Criteria

```text
all four initial actions have PASS evidence
all excluded actions are denied
source=agent durable mutation denied
approved_api cannot bypass human_authorization_ref
service_account_with_human_authorization is not Agent executor
artifact.write and quality.evaluation.create are append-only
kill switch denial happens before runtime mutation
idempotency duplicate returns prior execution reference
V6-3 audit event coverage exists for allow and deny paths
no raw secret / raw prompt / raw artifact content leakage
No False Green claim scan passes
```

## 9. No False Green Stop Conditions

停止并回到规划审计：

```text
human high-risk proceed decision is missing
source=agent receives durable mutation authority
approved_api bypasses human_authorization_ref
service account is treated as Agent executor or admin override
artifact.write overwrites prior version silently
quality.evaluation.create overwrites previous score silently
kill switch is checked after mutation
Evidence Chain becomes execution panel
forbidden claim production controlled executor ready is claimed outside No False Green context
```

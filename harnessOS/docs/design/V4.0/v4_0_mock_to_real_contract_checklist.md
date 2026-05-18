# V4.0 Mock-to-Real Contract Checklist

文档状态：V4.0-0 checklist baseline。每个 V4.0 UI mock 字段都必须落入本表结构，不允许把 mock schema 直接提升为 runtime contract。

## Required Table Shape

| UI 区域 | UI 字段 | 来源 | 对应 API | 是否可持久化 | 是否可写回 runtime | 是否包含敏感信息 | 是否需要 redaction | mock 到期阶段 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Workflow Canvas | workflow title | V3.6 API | `workflow.template.get` | yes | yes, via patch/draft | no | no | V4.0-B |
| Workflow Canvas | selected node | UI-only transient | none | no | no | no | no | never persisted |
| Workflow Canvas | node x/y | UI-only transient | none | local UI only | no | no | no | never persisted |
| Workflow Canvas | canvas zoom | UI-only transient | none | local UI only | no | no | no | never persisted |
| Workflow Canvas | current station status | V3.6 API | `workflow.board.get` | server-owned | no | no | yes, if trace summary included | V4.0-A |
| Inspector | node config | V3.6 API | `workflow.patch.diff/apply` | yes | yes, through patch only | possible | yes | V4.0-B |
| Quality Panel | score | V3.6 API | `quality.evaluation.get/list` | server-owned | no | no | no | V4.0-D |
| Approval Panel | decision | V3.6 API | `approval.respond` | server-owned | yes, action API | possible reason text | yes | V4.0-D |
| Context Panel | business context value | V3.6 API | `workflow.context.get/update` | yes | yes, only `context.business` | possible | yes | V4.0-D |
| Side Panel | panel collapsed | UI-only transient | none | local UI only | no | no | no | never persisted |
| Side Panel | side panel width | UI-only transient | none | local UI only | no | no | no | never persisted |
| Tabs | active tab | UI-only transient | none | local UI only | no | no | no | never persisted |
| Filters | filter keyword | UI-only transient | none | local UI only | no | no | no | never persisted |

## Source Values

Allowed source values:

```text
V3.6 API
V3.5 adaptation
UI-only transient
future
```

## Rules

- `canvas x/y/zoom/selection/panel collapsed/side panel width/active tab/filter keyword` are UI-only transient state.
- UI-only transient state must not be written back to V3.6 runtime contracts.
- Any field containing trace summary, approval reason, context payload, patch diff, or user-provided metadata must be redaction-aware.
- Future fields must include a target phase before implementation.

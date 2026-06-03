# V5-6 UI Acceptance Matrix

文档状态：V5-6 implementation planning。

## Required UI Checks

```text
tenant/workspace/app context visible
Runtime Report opens read-only
Evidence Chain opens read-only
Audit Export requires confirmation
External App admin respects scope
manual confirmation dialog records user_confirmed=true
no false execution buttons in read-only panels
```

## Browser Global Assertions

```text
no direct /v1/rpc
no direct /v1/events/subscribe
no token / secret / raw payload in DOM
no 自动应用 / 自动发布 / Agent 已执行 / Agent 已发布
```


# V4.0-T Production Token Lifecycle Follow-up Design Plan

阶段定位：V4.0-T 只做 production token lifecycle follow-up design，不实现 token rotate/revoke/refresh/introspect route，不实现 OAuth、SSO、tenant control plane、production onboarding 或 executor。

允许完成声明：

```text
V4.0-T complete: production token lifecycle follow-up design ready for review.
```

禁止完成声明：

```text
production-ready external app support
enterprise auth ready
multi-tenant control plane ready
OAuth ready
SSO ready
token lifecycle production-ready
controlled executor ready
Agent executor ready
autonomous workflow editing ready
complete Workflow Studio ready
complete AgentTalkWindow ready
full low-code canvas editing ready
```

## PR Slices

1. 新增机器可读 token lifecycle matrix，覆盖 issuance、expiration、rotation、revocation、origin binding、audience binding、scope binding、emergency revoke 和 token audit。
2. 新增 forbidden route scan，确保没有 `/token/rotate`、`/token/revoke`、`/token/refresh`、`/token/introspect` 或 auth/tenant production route。
3. 固化 capability token 边界：token claims 不能绕过用户确认，`executor.*` 继续 inactive，`source=agent` 不能执行 mutation。
4. 固化 EventBridge truth 边界：事件只触发 refresh，不构造 token truth。
5. 同步 V4.0 gap、audit、UI/event/mock/target architecture 文档。

## Test Plan

新增 `tests/test_v4_0_production_token_lifecycle_design.py` 覆盖合同存在、生命周期字段、forbidden route scan、agent/executor boundary、event truth 和 No False Green。

## Risk Controls

T 阶段不实现任何 token lifecycle production route。所有 token lifecycle 项仍是 blocking production gaps。

## Completion Evidence Format

Completion note 必须记录 allowed claim、forbidden claims、actual files changed、tests added、docs updated、token lifecycle matrix result、route scan result、claim guard result、validation command results 和 No False Green statement。

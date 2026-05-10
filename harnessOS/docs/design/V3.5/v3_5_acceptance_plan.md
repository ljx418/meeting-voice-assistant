# V3.5 Acceptance Plan

文档状态：V3.5 acceptance planning artifact。

## 1. Baseline

V3.5 启动基线：

- Application Adaptation Layer 以 dev/local-first 方式启动。
- 当前默认回归基线必须保持绿灯。
- 本阶段不把历史业务 E2E 重新作为 V3.5 完成条件。

## 2. Phase Acceptance

| 阶段 | 验收项 |
| --- | --- |
| V3.5-0 | contract inventory 完整；legacy/debug blacklist 明确；目录规划完整。 |
| V3.5-A | method/event/error schema registry；`approval.respond`；`events.subscribe`；result/error 互斥测试。 |
| V3.5-B | local capability token；scope/capability/origin 校验；dev mode 显式开启。 |
| V3.5-C | native EventSource / fetch stream；scope/token 校验；cursor replay；channel filter。 |
| V3.5-D | Python SDK MVP 方法全覆盖；scope 透传；error 映射；legacy method excluded。 |
| V3.5-E1 | TS SDK core client；schema default surface；native EventSource / fetch stream client；legacy/debug excluded。 |
| V3.5-E2 | React hooks；browser demo；EventSource reconnect；不得先于 V3.5-C 和 V3.5-E1。 |
| V3.5-F | BFF template；RPC/EventSource proxy；CORS/token/scope；denylist。 |
| V3.5-G | dummy pack / connector template；no-Core-change discovery。 |
| V3.5-H | EmbedDefinition；event union；approval/job/artifact states。 |
| V3.5-I | reference app E2E；approval.respond；scope isolation。 |

## 3. Exit Standard

V3.5 完成必须满足：

- 至少一个平台中立 reference app 能不改 Core 接入。
- SDK/BFF/hooks/event bridge 均通过 contract tests。
- Auth/capability token 明确区分 dev-only 和 local production mode。
- Pack/Connector template 可生成可被 registry 发现的最小样例。
- Embed contract 能支撑 AgentTalkWindow 前置集成。
- 默认全量回归保持绿灯。

## 4. Required New Acceptance Tests

- native EventSource browser auth test：原生 `EventSource` 不设置 Authorization header，使用 same-origin BFF cookie 或 signed subscription URL 通过认证。
- approval.respond idempotency tests：覆盖 repeated same decision、conflicting decision、scope mismatch、approval not found、retry consumed。
- SDK default surface legacy/debug exclusion test：SDK 不能默认暴露 legacy/debug/admin bypass methods。
- reference app neutrality test：reference app 不依赖 Meeting/Knowledge pack 或 legacy RPC。
- BFF cannot proxy forbidden methods test：BFF 对 legacy/debug/admin bypass method 返回稳定 forbidden error。
- REST scope compatibility test：`/v1/runs` 与 `/v1/runs/stream` 如保留，必须校验 app_id/project_id/workspace_id 和 token scope。

## 5. No False Green Rule

- 未实现 auth token 时，不得声明 production-ready external app support。
- 未实现 native EventSource browser auth 和 fetch stream bearer auth 时，不得声明 browser event bridge 完成。
- 未实现 protocol schema registry 时，不得声明 generated/typed SDK 完成。
- 未通过平台中立 reference app 时，不得声明 V3.5 出门。

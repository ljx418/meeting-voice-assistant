# V2.16 Phase 82 验收计划：Closure Acceptance

## 1. 必测断言

- Phase 76-81 验收报告存在。
- 每份报告包含 `Fatal findings：0` 和 `Major findings：0`。
- coverage matrix 中 Phase 76-81 in-scope 行为 `accepted`。
- 非目标仍为 `out_of_scope`。
- focused suite 全部通过。
- 真实 data_service 仓至少执行 provider、semantic、runtime profile、workbench v2、large-project advisor、patch preview E2E。

## 2. 假验收拒绝

- 任何 Phase 缺少验收报告。
- coverage matrix 仍有 Phase 76-81 pending。
- patch preview 修改源码。
- optional provider fake accepted。
- HTML 视图没有底层 payload。
- public payload 泄露绝对路径或 secret。

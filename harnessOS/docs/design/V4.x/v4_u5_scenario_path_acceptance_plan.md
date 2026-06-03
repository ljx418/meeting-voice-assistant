# V4-U5 Scenario Path Acceptance Package Plan

文档状态：已执行验收包计划。V4-U5 可以形成 U6 输入包，但不得自动进入 U6。

允许完成声明：

```text
V4-U5 complete: unified scenario path acceptance package ready for V4-U6 gate review.
```

## 1. 目标

重新验收 UX-01 到 UX-12，形成 V4-U6 输入包，并把 UX-08 / UX-09 / UX-10 的 PARTIAL 风险显式记录为 U6 前置人工决策点。

## 2. 实现范围

```text
重新运行 reality-check。
更新 UX-01 到 UX-12 result-summary。
更新 Runtime Capability Matrix。
更新 WorkflowSpec Registry。
更新 unified result-summary。
记录 PARTIAL proceed decision 或 blocked-from-U6 decision。
```

当前执行策略：

```text
UX-12 已具备 real_runtime / real_llm evidence。
UX-08 / UX-09 / UX-10 仍是 deterministic_devlocal PARTIAL。
本轮完成 V4-U5 验收包，但不进入 V4-U6。
```

## 3. 验收

```text
UX-01 到 UX-12 全部有 evidence summary。
无 FAIL / BLOCKED。
PARTIAL 均有人工确认或保持 blocked from U6。
No False Green claim scan 通过。
reality-check HTML 可打开。
drawio gap XML valid。
UX-08 / UX-09 / UX-10 如果还是 deterministic_devlocal，不得写成 full multi-Agent orchestration。
UX-12 必须 real_llm 或明确 BLOCKED，不得假验收。
```

当前验收结果：

```text
PASS: 9
PARTIAL: 3
FAIL: 0
BLOCKED: 0
allow_enter_v4_u6: false
requires_human_proceed_decision: true
```

## 4. 停止条件

```text
任一 UX case FAIL / BLOCKED。
PARTIAL 未记录 proceed decision 或 blocked-from-U6 decision。
active forbidden claim violation > 0。
UX-08 / UX-09 / UX-10 被写成 full multi-Agent orchestration。
```

## 5. U6 前置决策

```text
UX-08 / UX-09 / UX-10 的证据仍是 deterministic_devlocal。
这些证据可作为 V4-U5 验收包输入，但不能自动放行 V4-U6。
V4-U6 只能在用户人工接受 PARTIAL 风险，或后续把 UX-08 / UX-09 / UX-10 补成真实运行证据后启动。
```

# V3.5 Reference App Example Plan

文档状态：V3.5-I planning artifact。

## 1. Goal

新增一个平台中立 reference app example，证明业务 App 可以通过 SDK + BFF + hooks 接入 harnessOS Core，而不修改 Core/Gateway 业务逻辑。

Reference app 不依赖 Meeting Pack、Knowledge Pack 或任何 legacy RPC。它必须使用 dummy pack / dummy connector 或 generic workflow，证明 V3.5 Application Adaptation Layer 本身可用。

## 2. Target Directory

```text
examples/reference_app/
  README.md
  bff/
  frontend/
  pack/
  connector/
  tests/
```

## 3. Required Flow

Reference app 必须完成：

- 创建 session
- 发起 turn
- 订阅 events
- 展示 artifacts
- 展示 jobs
- 展示 approvals
- 展示 traces
- 处理 `approval.respond`
- 验证 scope isolation
- 使用 dummy pack / dummy connector 或 generic workflow 产生平台中立 job/artifact/trace。

## 4. Constraints

- 不使用业务 legacy RPC。
- 不使用 `meeting.*` / `knowledge.*` 业务方法。
- 不依赖 Meeting Pack 或 Knowledge Pack。
- 不使用业务 reference lifecycle 作为 shortcut。
- 不直接读写 Core store。
- 不绕过 BFF token/scope。

## 5. Acceptance

- reference app 使用 SDK + BFF + hooks。
- pack/connector 使用 V3.5 templates。
- reference app neutrality test 证明无 Meeting/Knowledge/legacy dependency。
- 两个不同 app/project/workspace 的数据互不可见。
- 默认回归仍绿。

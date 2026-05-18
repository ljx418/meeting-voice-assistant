# V4.0 Frontend Stack Decision

文档状态：V4.0-0 baseline decision。本文冻结 V4.0 Workflow Console / Workflow Studio 前端技术栈选择，不代表前端实现已完成。

## Decision

V4.0 Workflow Console 主实现采用：

```text
React + Vite + TypeScript
```

默认新建应用路径：

```text
apps/workflow-console/
```

现有 `apps/web` 继续作为 Vue 3 + Vite surface 保留，不作为 V4.0 Workflow Console 主实现。

## Rationale

- V3.5 已完成 TypeScript SDK core client 与 React hooks。
- Stitch 原型更适合快速落到 React component / hooks / state model。
- V4.0-0 目标是冻结 UI contract，不改造现有 Vue surface。
- 如果未来要让 `apps/web` 承载同等功能，必须新增 Vue composables 计划，不能直接复用 React hooks。

## Production and Dev Paths

Production recommended path：

```text
Business UI / Workflow Console
  -> BFF / SDK / hooks / EventBridge proxy
  -> harnessOS
```

Dev direct path：

```text
Workflow Console dev build
  -> TypeScript SDK direct transport
  -> harnessOS /v1/rpc
```

Dev direct 只允许在显式 dev mode 与受限 capability token 下使用。生产默认路径不得让浏览器长期持有广权限 token。

## No False Green

本决策完成后不能声明：

```text
Workflow Console ready
Workflow Studio ready
AgentTalkWindow ready
V4.0 complete
```

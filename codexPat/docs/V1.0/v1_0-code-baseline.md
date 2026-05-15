# V1.0 Code Baseline

## 固化对象

V1.0 固化当前 macOS-first MVP 代码能力，不再把 Phase 1-7 继续拆分为活跃开发阶段。

固化范围：

- `apps/desktop` Tauri 2 desktop app。
- `packages/pet-protocol`。
- `packages/petctl`。
- macOS-first transparent pet window。
- CatStateMachine 和占位动画。
- Rust Local Event Bridge。
- PetEvent JSON Schema 校验。
- token、白名单、rate limit、Ingress Queue。
- diagnostics accepted/rejected summaries。
- Safe Sound service。
- `petctl notify` 参数模式和 JSON stdin。

## 固化声明

V1.0 代码基线可声明：

```text
macOS-first MVP ready: local desktop agent status pet with HTTP + petctl integration and safe sound feedback.
```

V1.0 代码基线不可声明：

```text
cross-platform ready
Windows ready
MCP/Skill ready
USB ready
production signed release ready
```

## 后续变更规则

- V1.0 后续修复可以修改当前代码，但不得降低 V1.0 验收标准。
- 新功能必须进入 V1.1 或后续阶段计划，不直接混入 V1.0 归档。
- Windows、MCP、USB、Skill、3D、照片自定义和签名发布均不属于 V1.0。
- 后续文档若更新当前实现，应同时维护 `docs/active/current-vs-target-gap.md` 和 drawio；V1.0 归档只在发现归档错误时修正。

# V3.2 Development Plan

文档状态：active draft；Agent Integration Readiness。

## Baseline

V3.2 从 V3.1 final acceptance passed 开始。

允许继承声明：

```text
V3.1 ready: multi-instance Codex pet workflow stabilized with user onboarding, manager polish, repeatable runtime smoke, and migration guidance.
```

V3.2 不能扩大 V3.1 的验收范围。所有新集成必须独立留下 smoke 和 evidence。

## Product Goal

V3.2 的目标是把外部 agent 接入能力收敛成可审计、可复跑、无 false-green 的集成层。三方 agent、MCP adapter、Claude Code hook 都只能写入结构化 `PetEvent`，不能直接控制 UI、窗口、资源、声音路径或内部状态机。

## Phase Plan

### Phase 1：Scope Freeze & Integration Claim Matrix

状态：passed。

目标：

- 固化 V3.2 允许声明和禁止声明。
- 明确 MCP、Claude Code hook、third-party contract 都以 localhost HTTP/Event Bridge 为唯一入口。
- 建立 V3.2 evidence index 和 claim matrix。

产物：

- `docs/V3.2/v3_2-claim-matrix.md`
- `docs/V3.2/v3_2-evidence-index.md`

允许声明：

```text
V3.2 Phase 1 complete: integration scope and claim matrix frozen.
```

### Phase 2：MCP Adapter Minimal Implementation

状态：deferred for V3.2 closure。

目标：

- 新增 `packages/pet-mcp` 最小 MCP adapter。
- 工具通过 localhost HTTP/Event Bridge 调用现有 API。
- 保持 PetEvent schema、token、白名单、rate limit、diagnostics 边界。

最小工具：

- `pet_notify`
- `pet_list_instances`
- `pet_get_capabilities`
- `pet_get_state`

边界：

- 工具必须支持 `instanceId`。
- 不直接控制 UI。
- 不读取或输出本地路径。
- 不打印 token 或 Authorization header。
- 不声明 `MCP ready`，除非后续真实 Codex/Claude MCP smoke 通过。

产物：

- `packages/pet-mcp`
- `scripts/v3_2_mcp_adapter_smoke.mjs`
- `docs/V3.2/evidence/mcp-adapter-smoke-2026-05-23.md`

允许声明：

```text
V3.2 MCP adapter minimal smoke passed for localhost bridge routing.
```

### Phase 3：Claude Code Hook Real Verification

状态：passed。

目标：

- 用真实 Claude Code hook lifecycle 验证最小路径。
- 最低目标：`Notification -> need_input`。
- diagnostics 或 evidence 中必须出现 `sourceId=claude-code.local` 或等价可审计字段。

不接受：

- curl mock。
- 普通 shell `petctl` smoke 冒充 hook。
- 只有模板文档，没有真实 hook lifecycle evidence。

允许声明：

```text
V3.2 Claude Code hook Notification -> need_input smoke passed.
```

不允许声明：

```text
Claude Code integration verified
```

### Phase 4：Third-party Agent Contract v3 Refresh

状态：passed。

目标：

- 将 `docs/reference/third-party-agent-contract.md` 从 V2.1 `/api/events` 语境升级到 V3 multi-instance。
- 保留 curl / Node / Python contract smoke。
- 明确如果没有真实第三方产品，不得声明 third-party product integration verified。

必须覆盖：

- `/api/events` legacy default。
- `/api/instances/:instanceId/events`。
- `petctl attach`。
- `petctl notify --instance`。
- `instance_not_found`。
- `instance_id_invalid`。
- `instance_limit_reached`。
- hard limit。
- redaction。

允许声明：

```text
V3.2 third-party contract v3 smoke passed.
```

### Phase 5：Security & Regression Final Acceptance

状态：planned。

目标：

- 复跑 V3.1 runtime smoke，确认 V3.2 新集成不破坏多实例 Codex 主线。
- 复跑协议、CLI、desktop、Tauri build checks。
- 收口 V3.2 final acceptance report。

必须执行：

```bash
node scripts/v3_1_runtime_smoke.mjs
pnpm run doctor
pnpm --filter @agent-desktop-pet/pet-protocol check
pnpm --filter @agent-desktop-pet/pet-protocol test
pnpm --filter @agent-desktop-pet/petctl check
pnpm --filter @agent-desktop-pet/petctl test
pnpm --filter desktop check
cargo check --manifest-path apps/desktop/src-tauri/Cargo.toml
pnpm --filter desktop build
pnpm --filter desktop tauri build -b app
```

V3.2 还应执行：

```bash
pnpm --filter @agent-desktop-pet/pet-mcp check
pnpm --filter @agent-desktop-pet/pet-mcp test
```

## Explicit Non-goals

V3.2 不做：

- 无条件 `MCP ready`。
- 无条件 `Claude Code integration verified`。
- 无条件 `Third-party agent integration verified`。
- Windows ready / cross-platform ready。
- USB。
- production signed release / notarization / auto update。
- all Codex workflows verified。
- OS-level Codex window binding。
- per-instance queue。

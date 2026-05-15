# Monorepo 结构

推荐目录结构。当前已落地 `apps/desktop`、`packages/pet-protocol` 和 `packages/petctl`；`pet-mcp`、skills、cat-packs 和 hardware-protocol 仍是后续阶段。

```text
agent-desktop-pet/
  apps/
    desktop/
      src-tauri/
      src/
      public/
      package.json
      vite.config.ts
      tauri.conf.json

  packages/
    pet-protocol/
      src/
      schemas/
      package.json

    petctl/
      src/
      package.json

    # Post-MVP
    pet-mcp/
      src/
      package.json

    # Post-MVP
    cat-packs/
      default-cat/
        manifest.json
        sprites/
        sounds/
      sample-photo-cat/
        manifest.json
        sprites/
        sounds/

    # Post-MVP
    hardware-protocol/
      src/
      examples/

  skills/
    codex-agent-pet/
      SKILL.md

    claude-agent-pet/
      SKILL.md

  docs/
    00-overview.md
    01-tech-stack.md
    02-monorepo-structure.md
    03-pet-event-protocol.md
    04-cat-state-machine.md
    05-desktop-window.md
    06-cat-pack.md
    07-integrations.md
    08-hardware-light.md
    development-plan.md
    acceptance-plan.md
    target-architecture.md
    current-vs-target-gap.md
    post-mvp-roadmap.md
    10-risks-and-decisions.md

  scripts/
    dev-desktop.*
    build-desktop.*

  package.json
  pnpm-workspace.yaml
  README.md
```

## 目录职责

- `apps/desktop`：Tauri 桌面 App，负责窗口、托盘、动画、设置、本地 HTTP、事件消费、diagnostics 和 Phase 6 safe sound feedback。
- `packages/pet-protocol`：协议唯一来源，已包含 JSON Schema、TypeScript 类型、白名单常量、capabilities 和 fixtures。
- `packages/petctl`：CLI client，通过 HTTP 写入桌宠状态，复用 `pet-protocol` 本地校验。
- `packages/pet-mcp`：Post-MVP adapter，暴露桌宠状态 tools。
- `packages/cat-packs`：Post-MVP 资产包系统。
- `packages/hardware-protocol`：Post-MVP 串口协议和灯效常量；MVP 不实现 mock 或真实硬件。
- `skills/codex-agent-pet`：Post-MVP Codex instruction layer。
- `skills/claude-agent-pet`：Post-MVP Claude Code instruction layer。
- `docs`：设计、协议、计划和风险文档。
- `scripts`：开发、构建和验证脚本。

## 依赖方向

```text
apps/desktop -> packages/pet-protocol
packages/petctl -> packages/pet-protocol
packages/pet-mcp -> packages/pet-protocol       # Post-MVP
skills/* -> packages/petctl or HTTP API         # Post-MVP
```

禁止反向依赖：

- `pet-protocol` 不依赖 desktop、CLI 或 MCP。
- `cat-packs` 不依赖 desktop。
- Skill 文档不包含 UI 控制逻辑。

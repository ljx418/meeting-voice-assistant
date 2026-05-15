# Post-MVP Roadmap

文档状态：Post-MVP reference。  
说明：真正 MVP 开发计划以 `docs/active/development-plan.md` 为准。本文只记录 MVP 之后的扩展方向，不能作为第一版实现范围。

## MVP 之后的阶段边界

MVP 已经收敛为：

- Tauri 桌面壳。
- 占位猫。
- 低打扰状态机。
- 本地 HTTP API。
- PetEvent JSON Schema 校验。
- Rust Ingress Queue / TypeScript Behavior Queue。
- 事件日志。
- `petctl` CLI client。
- 声音白名单。
- 基础设置页。

以下能力全部是 Post-MVP：

- MCP server。
- Codex / Claude Code Skill 完整包。
- Cat Pack 系统。
- 用户照片自定义猫咪。
- Rive / Live2D / Spine。
- Three.js + GLTF / GLB。
- USB 真实或 mock 硬件。
- 团队协作状态提示。
- 自动更新和正式签名发布。

## Phase 2：Agent Integration Adapters

目标：

- 在 MVP HTTP + petctl 稳定之后，为更多 Agent 接入提供 adapter。

包含：

- `packages/pet-mcp`。
- MCP tools：`pet_notify`、`pet_get_capabilities`、`pet_get_state`。
- Codex Skill 文档包。
- Claude Code Skill 文档包。
- 自定义 agent SDK 探索。

边界：

- MCP 和 skills 都不能直接控制 UI。
- MCP 和 skills 最终仍通过同一 HTTP/Event Bridge 写入结构化事件。
- 不绕过 PetEvent JSON Schema 和白名单。

## Phase 2：Cat Asset Evolution

目标：

- 在占位猫 MVP 成立后，提高猫咪表现力。

包含：

- Cat Pack manifest。
- 默认 sprite pack。
- Rive / Live2D / Spine renderer 探索。
- 用户照片模板化自定义：提取主色、眼睛色、花纹参考并套用模板。

边界：

- 不做照片一键生成完整动态猫。
- 不让 Agent 传入任意资源路径或 URL。
- 资产包必须经过 manifest 校验。

## Phase 3：3D And Hardware

目标：

- 在状态反馈链路稳定之后，扩展到 3D 和物理空间反馈。

包含：

- Three.js + GLTF / GLB。
- 3D animation clip。
- USB 氛围灯真实串口实现。
- Rust `serialport`。
- JSON Lines 硬件协议。

边界：

- 硬件必须手动启用。
- 无硬件时桌宠正常工作。
- USB mock 和真实硬件都不进入 MVP。
- 设备和硬件 effect 必须白名单。

## Phase 3：Team Status Layer

目标：

- 探索团队协作状态的低打扰提示。

可能场景：

- PR 等待 Review。
- CI 失败。
- 线上告警。
- 团队 Agent 批量任务。

边界：

- 不替代 Slack、飞书、GitHub、Jira。
- 不做团队监控平台。
- 仍然只做低打扰状态提示层。

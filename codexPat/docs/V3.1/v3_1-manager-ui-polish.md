# V3.1 Phase 3：Manager UI Usability Polish

文档状态：active phase design and acceptance。

## 目标

把多猫管理从“功能能用”打磨成“普通用户看得懂、点得明白、误操作风险低”。

本阶段只改 Multi-pet Manager 的文案、反馈、布局和安全复制体验，不扩展运行时能力。

## 已实现范围

- 设置页标题统一为“多猫管理”。
- default pet 标注为“默认猫 / 旧路由”。
- extra pet 标注为“Codex 实例猫 / 实例路由”。
- `currentState` 在 Manager 中显示为中文状态：
  - `idle`：空闲
  - `thinking`：思考中
  - `running`：执行中
  - `success`：完成
  - `warning`：注意
  - `error`：失败
  - `need_input`：需要确认
  - `sleeping`：休息中
- 实例字段中文化：实例 ID、窗口标签、当前状态、外观、路由、最近事件。
- 重命名改为 inline input + 卡片内反馈，不使用系统 prompt。
- 移除改为“移除 / 确认移除”二次点击，不使用系统 confirm。
- 显示、隐藏、重置位置、复制命令都有卡片内反馈。
- default pet 的移除按钮禁用并显示“默认猫不可移除”。
- 复制按钮只复制安全模板文本，不执行命令，不复制 token 或本地路径。
- 设置页卡片与命令文本支持换行，降低窄窗口溢出风险。

## 安全边界

本阶段没有修改：

- PetEvent schema。
- Rust bridge routing 语义。
- CatStateMachine。
- `petctl` 参数。
- safe sound policy。
- MCP / USB / Windows / 3D / 照片自定义相关能力。

Manager UI 仍然不允许：

- 执行 shell、`petctl`、`curl`、`node`、`osascript` 或任何系统命令。
- 显示 token、raw payload、metadata 全量、完整 workspace path。
- 提供通知中心式 UI。

## 验收重点

- 中文文案可理解。
- 重命名成功后卡片和猫窗口名字即时更新，不需要 reload。
- 显示 / 隐藏 / 重置位置 / 移除都有明确反馈。
- 复制文本不包含 token、本地 config 路径、workspace path 或 payload。
- 设置页可滚动，长 instanceId / windowLabel 不撑破容器。
- 主猫窗口透明、拖拽、动画不回归。

## 证据

- `docs/V3.1/evidence/manager-ui-polish-2026-05-20.md`

# Codex Real Integration Verification

文档状态：V2.1-B passed；Codex local workflow integration verified for tested local Codex CLI smoke scenarios。

## Goal

验证真实 Codex CLI 工作流能按 `skills/codex-agent-pet/SKILL.md` 写入 agent-desktop-pet，并在 diagnostics 中留下 `sourceId=codex.local`。

## Preconditions

- 桌宠 `.app` 已启动。
- `petctl` 可用，或可以使用 `node packages/petctl/dist/cli.js notify`。
- 本地 token 可由 `petctl` 读取，或设置 `AGENT_DESKTOP_PET_TOKEN`。
- Codex 任务明确加载或引用 `skills/codex-agent-pet/SKILL.md`。

## Required Smoke Scenarios

| Scenario | Expected PetEvent | Required evidence |
| --- | --- | --- |
| Planning | `level=thinking` | diagnostics accepted event: `sourceId=codex.local`。 |
| Running | `level=running` | 猫进入 running 或低打扰忙碌状态。 |
| Success | `level=success`, `sound=success_chime` | 猫进入 success，diagnostics 有 accepted summary。 |
| Error | `level=error`, `sound=error_chime` | 猫进入 error，diagnostics 有 accepted summary。 |
| Need input | `level=need_input`, `sound=need_input_chime` | 猫进入 need_input，且声音受 mute/cooldown 控制。 |

## Verification Rules

- 只在状态阶段变化时发送事件。
- 不对每个文件、日志行、tool call 或小步骤发送事件。
- 不传本地路径、相对路径、绝对路径或 URL 作为 `sound`。
- 不直接控制桌宠 UI。
- 不执行桌宠内部脚本。

## Pass Criteria

只有同时满足以下条件，才允许声明 `Codex local workflow integration verified.`：

- 真实 Codex CLI 任务完成全部 required smoke scenarios。
- diagnostics 出现 `sourceId=codex.local` 的 accepted summaries。
- 人工确认猫状态变化。
- 没有高频刷事件、非法 sound、UI 直接控制或脚本执行。
- `docs/V2.1/evidence/codex-smoke-template.md` 被填写并标记 status=`passed`。

如果只是复制模板命令或在普通终端手动运行 `petctl`，只能声明 `Codex local workflow template ready`。

## 2026-05-19 Smoke Result

真实 `codex exec` 已完成三组 smoke：

- Smoke A：读取 README / V2.1 文档，运行 `pnpm --filter @agent-desktop-pet/petctl test`，发送 `thinking`、`running`、`success`。
- Smoke B：执行安全失败命令 `false`，发送 `running`、`error`。
- Smoke C：在提交/推送前请求确认，发送 `need_input`。

diagnostics 已出现 `sourceId=codex.local` 的 accepted summaries，覆盖 `thinking`、`running`、`success`、`error`、`need_input`。

operator 已确认人工视觉验收通过。V2.1-B 当前可声明：

```text
V2.1-B complete: Codex local workflow integration smoke passed.
Codex local workflow integration verified for tested local Codex CLI smoke scenarios.
```

证据文件：

- `docs/V2.1/evidence/codex-smoke-2026-05-19.md`

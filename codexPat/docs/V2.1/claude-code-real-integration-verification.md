# Claude Code Real Integration Verification

文档状态：V2.1 smoke plan。

## Goal

验证真实 Claude Code skill 和 hook 流程能按 `skills/claude-agent-pet/SKILL.md` 写入 agent-desktop-pet，并在 diagnostics 中留下 `sourceId=claude-code.local`。

## Preconditions

- 桌宠 `.app` 已启动。
- `petctl` 可用，或设置了等价 CLI wrapper。
- 本地 token 可由 `petctl` 读取，或设置 `AGENT_DESKTOP_PET_TOKEN`。
- Claude Code 任务明确加载 `skills/claude-agent-pet/SKILL.md`。
- hook 验证使用 `skills/claude-agent-pet/settings-hooks.example.json` 作为示例，不自动覆盖用户配置。

## Skill Smoke Scenarios

| Scenario | Expected PetEvent | Required evidence |
| --- | --- | --- |
| Analysis | `level=thinking` | diagnostics accepted event: `sourceId=claude-code.local`。 |
| Running | `level=running` | 猫进入 running。 |
| Success | `level=success`, `sound=success_chime` | 猫进入 success。 |
| Error | `level=error`, `sound=error_chime` | 猫进入 error。 |
| Need input | `level=need_input`, `sound=need_input_chime` | 猫进入 need_input。 |

## Hook Smoke Scenarios

- 使用 hook 示例发送 `running`。
- 使用 hook 示例发送 `success`。
- 使用 hook 示例发送 `error` 或 `need_input`。
- hook 不打印完整 token。
- hook 失败不得阻塞 Claude Code 主任务。

## Pass Criteria

只有同时满足以下条件，才允许声明 `Claude Code local workflow integration verified.`：

- 真实 Claude Code skill smoke 通过。
- 真实 Claude Code hook smoke 通过。
- diagnostics 出现 `sourceId=claude-code.local` accepted summaries。
- 人工确认猫状态变化。
- 没有高频刷事件、非法 sound、UI 直接控制或脚本执行。
- `docs/V2.1/evidence/claude-code-smoke-template.md` 被填写并标记 status=`passed`。

如果只完成 instruction template 或 hook example 文档，仍只能声明 `Claude Code local workflow template ready`。


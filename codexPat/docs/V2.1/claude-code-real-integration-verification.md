# Claude Code Real Integration Verification

文档状态：deferred to V3.0；C1 runtime smoke 已产生 accepted diagnostics evidence，operator 视觉确认和 C2 Notification 真实触发迁移到 V3.0。

## Goal

记录真实 Claude Code skill 和 hook 流程的当前证据、未完成项和 V3.0 验收边界。当前文档不再作为 V2.1-B Codex 适配声明的阻塞项。

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

## 2026-05-19 Execution Result

证据文件：`docs/V2.1/evidence/claude-code-smoke-2026-05-19.md`。

### C1 Skill Runtime Smoke

真实 Claude Code CLI 任务已通过 `petctl` / localhost HTTP 写入 `sourceId=claude-code.local` 的 accepted events：

| Scenario | Diagnostics evidence | Runtime result | Visual result |
| --- | --- | --- | --- |
| Smoke A success path | `evt_1779161559496_9` thinking；`evt_1779161598847_10` success | pass | pending operator confirmation |
| Smoke B failure path | `evt_1779161673291_11` running；`evt_1779161691052_12` error | pass | pending operator confirmation |
| Smoke C need_input | `evt_1779161749592_13` need_input | pass | pending operator confirmation |

当前只能说明 Claude Code skill runtime smoke 已产生 accepted diagnostics evidence；在 operator 视觉确认前，不声明 `Claude Code skill workflow verified`。

### C2 Hook Smoke

当前 `skills/claude-agent-pet/settings-hooks.example.json` 已改为默认只覆盖 `Notification -> need_input`。`UserPromptSubmit`、`PreToolUse` 和 `Stop` 不作为默认验收 hook：

- `UserPromptSubmit -> thinking` 容易高频触发，后续如启用必须节流。
- `PreToolUse -> running` 不应无过滤启用，后续如启用只针对安全命令模式并节流。
- `Stop -> success` 不等同任务成功，不作为默认 hook。

本轮真实 Claude Code CLI 使用 `--settings skills/claude-agent-pet/settings-hooks.example.json --include-hook-events --output-format stream-json --verbose` 进行了 hook lifecycle 探测。结果：

- Claude Code 2.1.114 支持 `Notification`、`PostToolUse`、`UserPromptSubmit`、`Stop` 等 hook event。
- 本地文档未发现 `PostToolUseFailure` event；失败 hook 仍 pending。
- 非交互 `claude -p` 的 Bash permission、AskUserQuestion、disallowed Bash 路径均未稳定触发 `Notification` hook event。

C2 当前状态迁移到 V3.0 backlog，不能声明 `Claude Code hook workflow verified`。

## Pass Criteria

V3.0 中只有同时满足以下条件，才允许声明 `Claude Code local workflow integration verified.`：

- 真实 Claude Code skill smoke 通过。
- 真实 Claude Code hook smoke 通过。
- diagnostics 出现 `sourceId=claude-code.local` accepted summaries。
- 人工确认猫状态变化。
- 没有高频刷事件、非法 sound、UI 直接控制或脚本执行。
- `docs/V2.1/evidence/claude-code-smoke-template.md` 被填写并标记 status=`passed`。

如果只完成 instruction template 或 hook example 文档，仍只能声明 `Claude Code local workflow template ready`。

如果 C1 runtime smoke 已通过但 operator 视觉确认未记录，最多只能记录为 runtime evidence captured，不得声明 workflow verified。

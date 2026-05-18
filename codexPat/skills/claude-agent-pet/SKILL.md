# Claude Code Agent Desktop Pet

Use this skill when reporting Claude Code task progress to agent-desktop-pet.

## Purpose

Send low-interruption local workflow status updates while Claude Code analyzes, edits, tests, or builds a project. The desktop pet only receives structured PetEvent status intent.

## Source

Always use:

```text
source.id = claude-code.local
source.kind = claude_code
source.name = Claude Code
```

## Rules

- Only send structured PetEvent updates through `petctl notify` or the localhost HTTP API.
- Never control the pet UI directly.
- Never execute scripts inside the pet.
- Never pass local file paths, relative paths, absolute paths, URLs, or arbitrary resource names as `sound`.
- Use only whitelisted sound IDs: `none`, `success_chime`, `warning_chime`, `error_chime`, `need_input_chime`.
- Send events only when the workflow phase changes; do not send one event per file, log line, command output line, or small step.
- Keep `title` and `message` short.
- Do not claim MCP integration ready.

## State Mapping

```text
thinking   -> reading, analyzing, or planning code changes
running    -> editing, testing, building, or validating
success    -> task completed and verification passed
warning    -> non-blocking issue or residual risk
error      -> failed command, implementation blocker, or unrecoverable problem
need_input -> user decision, approval, credentials, or clarification required
```

## Example Commands

Analysis:

```bash
petctl notify \
  --source-id claude-code.local \
  --source-kind claude_code \
  --source-name "Claude Code" \
  --level thinking \
  --title "Claude Code 正在分析代码"
```

Editing or testing:

```bash
petctl notify \
  --source-id claude-code.local \
  --source-kind claude_code \
  --source-name "Claude Code" \
  --level running \
  --title "Claude Code 正在执行开发任务"
```

Warning:

```bash
petctl notify \
  --source-id claude-code.local \
  --source-kind claude_code \
  --source-name "Claude Code" \
  --level warning \
  --title "Claude Code 发现非阻塞问题" \
  --message "任务可继续，但建议稍后处理" \
  --sound warning_chime
```

Need input:

```bash
petctl notify \
  --source-id claude-code.local \
  --source-kind claude_code \
  --source-name "Claude Code" \
  --level need_input \
  --title "Claude Code 需要用户确认" \
  --message "需要选择实现方向或授权操作" \
  --sound need_input_chime
```

Error:

```bash
petctl notify \
  --source-id claude-code.local \
  --source-kind claude_code \
  --source-name "Claude Code" \
  --level error \
  --title "Claude Code 执行失败" \
  --message "请查看终端输出" \
  --sound error_chime
```

Success:

```bash
petctl notify \
  --source-id claude-code.local \
  --source-kind claude_code \
  --source-name "Claude Code" \
  --level success \
  --title "Claude Code 任务完成" \
  --message "开发任务已完成并验证" \
  --sound success_chime
```

## Not Ready Claims

This skill is an instruction template only. Do not claim Claude Code integration verified, MCP integration ready, Windows ready, cross-platform ready, or production signed release ready.


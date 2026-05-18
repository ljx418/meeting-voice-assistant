# Codex Agent Desktop Pet

Use this skill when reporting Codex task progress to agent-desktop-pet.

## Purpose

Send low-interruption status updates to the local desktop pet while working in a developer workflow. The pet is a feedback layer, not a UI controller.

## Source

Always use:

```text
source.id = codex.local
source.kind = codex
source.name = Codex
```

## Rules

- Only send structured PetEvent updates through `petctl notify` or the localhost HTTP API.
- Never control the pet UI directly.
- Never execute scripts inside the pet.
- Never pass local file paths, relative paths, absolute paths, URLs, or arbitrary resource names as `sound`.
- Use only whitelisted sound IDs: `none`, `success_chime`, `warning_chime`, `error_chime`, `need_input_chime`.
- Send events only when the task phase changes; do not send an event for every file, log line, tool call, or small step.
- Keep `title` and `message` short.
- Prefer silent `thinking` and `running`; only use sound for meaningful `success`, `warning`, `error`, or `need_input`.

## State Mapping

```text
thinking   -> analysis or planning
running    -> executing edits, commands, tests, or builds
success    -> completed and verified
warning    -> non-blocking issue
error      -> failed command or blocker
need_input -> user approval, clarification, or decision needed
```

## Example Commands

Planning:

```bash
petctl notify \
  --source-id codex.local \
  --source-kind codex \
  --source-name Codex \
  --level thinking \
  --title "Codex 正在分析任务"
```

Running:

```bash
petctl notify \
  --source-id codex.local \
  --source-kind codex \
  --source-name Codex \
  --level running \
  --title "Codex 正在执行任务"
```

Need input:

```bash
petctl notify \
  --source-id codex.local \
  --source-kind codex \
  --source-name Codex \
  --level need_input \
  --title "Codex 需要确认" \
  --message "有命令需要授权或实现方向需要确认" \
  --sound need_input_chime
```

Error:

```bash
petctl notify \
  --source-id codex.local \
  --source-kind codex \
  --source-name Codex \
  --level error \
  --title "Codex 遇到阻塞" \
  --message "请查看终端输出" \
  --sound error_chime
```

Success:

```bash
petctl notify \
  --source-id codex.local \
  --source-kind codex \
  --source-name Codex \
  --level success \
  --title "Codex 任务完成" \
  --message "已完成并通过验证" \
  --sound success_chime
```

## Not Ready Claims

This skill is an instruction template only. Do not claim MCP integration ready, Codex integration verified, Windows ready, cross-platform ready, or production signed release ready.


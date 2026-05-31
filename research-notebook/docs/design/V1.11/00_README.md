# ResearchNotebook V1.11 Scoped Repository Sync / Release Handoff

日期：2026-05-31

## 当前状态

`BLOCKED_BY_REMOTE_CONFIRMATION`

V1.11 是 V1.x `PASS_LIMITED` 收口后的仓库同步阶段，不做功能开发。

## 阶段目标

- 确认当前 git remote / branch / repository scope。
- 复跑 V1.x final smoke 与 `npm run check`。
- 验证 `.smoke-artifacts/` 不进入 git。
- 验证 V1.x 文档仍保持 `PASS_LIMITED`，不扩大成 all-source / all-domain ready。
- 在 remote 和提交范围确认后，执行 scoped staging / commit / push。

## 当前阻塞

当前 git 根目录为：

```text
<workspace-root>
```

当前 remote 为：

```text
origin https://github.com/ljx418/meeting-voice-assistant.git
```

该 remote 名称与当前子项目 `research-notebook` 不一致。为避免推错仓库或混入 sibling project，V1.11 必须停在人工确认点。

## 文档索引

| 文档 | 用途 |
| --- | --- |
| `v1_11_scoped_repository_sync_plan.md` | V1.11 scoped sync 开发与验收计划。 |
| `v1_11_plan_audit.md` | V1.11 计划审计、规格漂移和虚假验收风险评估。 |
| `v1_11_scoped_repository_sync_report.md` | V1.11 执行结果和阻塞记录。 |

## 仍不能声明

- all websites URL extraction ready
- all-source-type ready
- OCR ready
- scanned PDF ready
- Audio Overview ready
- PPT generation ready
- Mindmap ready
- Document comparison ready
- cloud sync / collaboration ready

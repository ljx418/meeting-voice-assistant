# ResearchNotebook Git Remote Sync Status

文档状态：RC8 remote sync complete。
日期：2026-05-19。

## 1. Repository Discovery

当前 `research-notebook` 目录仍位于上层 workspace Git 仓库中：

```text
<workspace-root>/research-notebook
```

当前远端：

```text
origin https://github.com/ljx418/meeting-voice-assistant.git
```

当前分支：

```text
main
```

用户已确认当前先以 `research-notebook/` 子目录同步到既有上层远端，后续再处理独立分库。

## 2. RC8 Sync Result

同步范围：

```text
research-notebook/
```

RC8 主提交：

```text
34142eba Finalize ResearchNotebook V1.0 RC7 release handoff
```

推送结果：

```text
origin/main c774626a..34142eba
```

本次同步包含：

- RC7 release handoff 文档；
- RC6 source trace re-smoke 结果；
- V1.0 release checklist；
- gap markdown / drawio 更新到 RC7；
- README / docs index 收口；
- `smoke:release` 命令与 release smoke 脚本；
- `fixtures/real/` 与 `fixtures/adapter/` 语义分层；
- RC2-RC6 alignment / readiness / hygiene 文档；
- source trace 404 的真实记录与 accepted degraded fallback 声明。

未纳入本次同步：

```text
workspace 下其它 sibling 项目的既有改动
```

## 3. Current Release State

V1.0-M0 到 M4 状态：

```text
integration-smoke-ready
```

RC6 real smoke 状态：

```text
complete
```

Source trace integration：

```text
NOT_READY
```

Trace-unavailable fallback：

```text
DEGRADED_ACCEPTED
```

V1.0 当前可声明：

```text
ResearchNotebook V1.0 release candidate repository handoff is complete.
ResearchNotebook V1.0 M0-M4 is integration-smoke-ready.
ResearchNotebook V1.0 source-grounded personal knowledge MVP is release candidate ready with trace-unavailable fallback.
```

仍不能声明：

- source trace integration ready；
- source preview ready；
- precise citation backjump ready；
- multi-format ingestion ready；
- assessment ready；
- quality governance console ready；
- graph editing/governance ready；
- cloud sync/collaboration ready。

## 4. Sync Hygiene

RC8 使用 scoped add：

```bash
git add research-notebook/
```

未使用：

```bash
git add .
```

RC8 entry gate 已确认：

- `npm run check` 通过；
- `research-notebook/src`、`research-notebook/scripts`、`research-notebook/fixtures` 无本地绝对路径、cache path、artifact physical path；
- `research-notebook/` 内无 `.bkp` 文件；
- staged paths 全部位于 `research-notebook/`；
- source trace integration 仍为 `NOT_READY`，没有被伪装为成功。

## 5. Future Split Step

ResearchNotebook 后续仍建议迁移到自己的独立 Git remote。迁移前，本项目只以 `research-notebook/` 子目录形式进入当前远端。

独立分库时可选择：

```bash
git remote add origin <research-notebook-remote-url>
git push -u origin main
```

或修复 GitHub CLI 认证后创建独立仓库。

## 6. Next Product Phase

RC8 后不应继续追加 RC 功能开发。若继续产品开发，应进入：

```text
V1.1 Source Preview / Evidence Navigation
```

V1.1 entry gate 依赖 `data_service` 提供明确 contract：

- `DocumentUnit`；
- `EvidenceSpan`；
- source preview route；
- precise locator model；
- citation backjump semantics；
- capability/version manifest。

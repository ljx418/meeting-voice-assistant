# ResearchNotebook Git Remote Sync Status

文档状态：RC7 release handoff prepared；last remote sync predates RC5-RC7 package updates。
日期：2026-05-19。

## 1. Repository Discovery

当前 `research-notebook` 目录最初位于上层 workspace Git 仓库中：

```text
<workspace-root>
```

上层仓库远端为：

```text
origin https://github.com/ljx418/meeting-voice-assistant.git
```

该远端不属于 ResearchNotebook，因此不得把 ResearchNotebook 作为上层仓库的一部分推送到该远端。

## 2. Intended Project Repository

长期来看，ResearchNotebook 仍应作为独立前端应用仓库维护。

已探测：

```text
https://github.com/ljx418/research-notebook.git
```

结果：

```text
Repository not found
```

GitHub CLI 当前认证状态：

```text
gh auth status -> token invalid for ljx418
```

用户已确认当前先直接全量同步到既有远端，后续再处理分库。

## 3. Sync Preparation

已为独立仓库准备：

- `.gitignore`：排除 `node_modules/`、`dist/`、`.DS_Store`、env、coverage 和测试产物；
- `README.md`：记录项目定位、当前 RC 状态、命令和边界规则；
- V1.0 文档集：记录真实 data_service route alignment、integration readiness 和 gap 状态。

## 4. Current Sync Decision

当前同步目标：

```text
origin https://github.com/ljx418/meeting-voice-assistant.git
```

同步范围：

```text
research-notebook/
```

已同步提交：

```text
8a0f2cdb Add ResearchNotebook V1 RC1 frontend
```

推送结果：

```text
origin/main d580066a..8a0f2cdb
```

当前本地最新提交：

```text
c774626a Document ResearchNotebook remote sync
```

RC5-RC7 release packaging / source trace re-smoke / release handoff 改动仍在本地 working tree，尚未 commit / push。本轮文档和仓库卫生更新包括：

- `npm run smoke:release` 推荐命令与 `smoke:rc1` legacy alias；
- `scripts/release-smoke.mjs`；
- README RC7 release handoff 口径；
- `fixtures/real/` 与 `fixtures/adapter/` 分层；
- `v1_0_release_checklist.md` 三态化；
- `v1_0_rc5_repository_hygiene_summary.md`；
- `v1_0_rc6_source_trace_resmoke_report.md`；
- `v1_0_rc7_release_handoff.md`；
- gap markdown/drawio 更新到 RC6；
- RC6 `smoke:release` 真实结果：source trace still 404，fallback accepted。
- RC7 handoff 口径：repository handoff ready，等待用户确认后 scoped commit / push。

不纳入本次提交：

```text
workspace 下其它 sibling 项目的既有改动
```

## 5. Future Split Step

二选一：

1. 提供 ResearchNotebook 远端仓库 URL，然后执行：

```bash
git remote add origin <remote-url>
git push -u origin main
```

2. 修复 GitHub CLI 认证后创建远端：

```bash
gh auth login -h github.com
gh repo create ljx418/research-notebook --private --source=. --remote=origin --push
```

## 6. Long-term Sync Rule

ResearchNotebook 后续建议迁移到自己的独立 Git remote。迁移前，本项目只以 `research-notebook/` 子目录形式进入当前远端，不混入 `data_service` 或其它 workspace sibling 项目的未审计改动。

RC7 commit / push 建议命令必须保持 scoped add：

```bash
git add research-notebook/
git commit -m "Finalize ResearchNotebook V1.0 RC7 release handoff"
git push
```

禁止使用 `git add .`，避免混入 workspace sibling 项目改动。

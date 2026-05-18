# ResearchNotebook Git Remote Sync Status

文档状态：Git sync complete；ResearchNotebook 当前作为上层仓库子目录同步。
日期：2026-05-18。

## 1. Repository Discovery

当前 `research-notebook` 目录最初位于上层 workspace Git 仓库中：

```text
/Users/Zhuanz/Desktop/workspace
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
- `README.md`：记录项目定位、RC1 状态、命令和边界规则；
- V1.0 RC1 文档集：记录真实 data_service route alignment、integration readiness 和 gap 状态。

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

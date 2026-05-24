# ResearchNotebook V1.1 可视化用户端到端验收报告

文档状态：脚本已落地，等待在已启动的本地前后端服务上执行。
日期：2026-05-24。

## 目标

本报告用于记录 Chrome CLI 可视化端到端验收。该验收会打开真实 Chrome 窗口，并像普通用户一样操作 ResearchNotebook。

## 执行命令

后端需要先运行在：

```text
http://127.0.0.1:8003
```

前端需要先运行在：

```text
http://127.0.0.1:5173
```

执行：

```bash
RN_CHROMIUM_PATH="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
RN_VISIBLE_E2E_KEEP_BROWSER_OPEN=1 \
npm run smoke:v1.1-visible-user-e2e
```

## 覆盖路径

| 路径 | 预期 |
| --- | --- |
| Home | Chrome 打开真实页面，非空白，无 crash overlay |
| Workspace | 创建 workspace 并进入 workspace 页面 |
| Text source | 创建 text source，打开 Source Preview Drawer，选择 DocumentUnit，点击 citation，看到 EvidenceSpan 高亮 |
| Markdown source | 创建 markdown source，验证 preview、unit、workspace citation highlight |
| JSON source | 创建 json source，验证 preview、unit、workspace citation highlight |
| Source Trace | 点击 Trace，看到 source trace/provenance |
| Session | 创建 session，ingest snippet，build session，提交 session query，点击 citation，看到 EvidenceSpan 高亮 |
| Cleanup | 脚本结束时归档 workspace |

## 输出

脚本输出目录：

```text
.smoke-artifacts/v1_1_visible_user_e2e/<timestamp>/
```

脱敏 fixture 目录：

```text
fixtures/real/v1_1/visible-user-e2e/
```

## 当前记录

| 项目 | 结果 |
| --- | --- |
| Chrome path | `/Applications/Google Chrome.app/Contents/MacOS/Google Chrome` |
| frontend URL | `http://127.0.0.1:5173` |
| backend URL | `http://127.0.0.1:8003` |
| latest run | 待执行 |
| latest decision | NOT_RUN |

## 声明边界

该可视化 E2E 通过后，只能声明 V1.1 当前受限路径的可视化用户验收通过。

仍不能声明：

- all-source-type precise backjump ready；
- all-source-type source trace ready；
- native PDF/PPTX/HTML/video/audio ingestion ready；
- Assessment / Mastery ready；
- Quality/Governance console ready；
- Graph editing/governance ready；
- Cloud sync/collaboration ready。

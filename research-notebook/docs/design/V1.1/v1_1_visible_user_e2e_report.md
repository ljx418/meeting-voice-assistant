# ResearchNotebook V1.1 可视化用户端到端验收报告

文档状态：Chrome CLI 可视化用户端到端验收已通过。
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
| latest run | 2026-05-24 |
| latest workspace | `rn-v11-visible-user-1779602822347-workspace` |
| latest session | `ksess_f36af3eb7c0b4ab6` |
| latest decision | PASS |

## 最新执行结果

```text
npm run smoke:v1.1-visible-user-e2e
V1_1_VISIBLE_USER_E2E_DECISION PASS
```

通过项：

- Chrome 真实窗口打开 ResearchNotebook；
- workspace 创建并进入；
- text source preview、DocumentUnit、workspace citation、EvidenceSpan highlight 通过；
- markdown source preview、DocumentUnit、workspace citation、EvidenceSpan highlight 通过；
- json source preview、DocumentUnit、workspace citation、EvidenceSpan highlight 通过；
- Source Trace Drawer 显示 trace/provenance；
- session 创建、ingest、build、query、citation click 和 EvidenceSpan highlight 通过；
- 未观察到 `/api/v1/knowledge/*` 请求；
- 无阻塞 console error / pageerror；
- workspace cleanup 通过。

最新 artifact：

```text
.smoke-artifacts/v1_1_visible_user_e2e/1779602822347/
```

最新脱敏 fixture：

```text
fixtures/real/v1_1/visible-user-e2e/
```

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

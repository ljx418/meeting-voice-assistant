# ResearchNotebook V1.2 Release Readiness Checklist

文档状态：V1.2-C 已通过；V1.2-D 待执行。

| 检查项 | 状态 | 证据 |
| --- | --- | --- |
| V1.1 final baseline | PASS | V1.1 文档和 smoke 作为 V1.2 baseline。 |
| 导入格式选择 UI | PASS | Source import form 使用明确格式 select。 |
| Markdown/JSON browser smoke | PASS | `npm run smoke:v1.2-multiformat-browser` 已通过。 |
| `npm run check` | PASS | 2026-05-24 已通过。 |
| fixtures 脱敏 | PASS | `fixtures/real/v1_2/multiformat/v1_2-multiformat-browser-result.json` 使用 `<research-notebook>` 占位，不含本地绝对路径。 |
| `.smoke-artifacts/` 不提交 | PASS | `git status --short -- .smoke-artifacts` 无输出。 |
| no `/api/v1/knowledge/*` 新功能调用 | PASS | 命中仅为 smoke guard 和文档说明，未新增功能调用。 |
| route shape 只在 dataServiceClient | PASS | `/api/` 命中为 adapter import path，不是 feature route string。 |
| 手工验收报告 | NOT_STARTED | `v1_2_manual_acceptance_report.md` 待填写。 |
| scoped commit / push | NOT_STARTED | V1.2-D 执行。 |

## 仍为 NOT_READY

- PDF/PPTX/HTML/video/audio ingestion。
- all-source-type precise backjump。
- Assessment / Mastery。
- Quality/Governance console。
- Graph editing/governance。
- Cloud sync/collaboration。

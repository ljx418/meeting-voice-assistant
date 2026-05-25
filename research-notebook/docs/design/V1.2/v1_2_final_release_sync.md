# ResearchNotebook V1.2 Final Release Sync

文档状态：V1.2-C 已通过；V1.2-D 手工验收按产品决策跳过；本文件只记录 closeout 和 V1.3 迁移。

## 收尾条件

1. `npm run check` 通过。
2. `npm run smoke:v1.2-multiformat-browser` 通过。已完成。
3. `v1_2_multiformat_browser_smoke_report.md` 更新为 PASS。已完成。
4. `v1_2_manual_acceptance_report.md` 标记为 SKIPPED_BY_PRODUCT_DECISION。
5. fixtures 脱敏。
6. `.smoke-artifacts/` 未进入 git。
7. scoped commit / push 完成。

## Commit Scope

允许提交：

- `src/` 中与中文化和 V1.2 导入格式选择相关的改动。
- `scripts/v1_2_multiformat_browser_smoke.mjs`。
- V1.1/V1.2 相关 smoke 脚本兼容中文 UI 的小修。
- `docs/design/V1.2/`。
- 必要的 V1.1 pointer 文档。
- `fixtures/real/v1_2/multiformat/` 中脱敏 JSON fixture。
- `fixtures/manual/` 中脱敏 Chrome CLI 技术分享导入探索 summary。
- `docs/design/V1.3/` 中 Agent Workflow 规划文档。

禁止提交：

- `.smoke-artifacts/`。
- 未脱敏截图或日志。
- unrelated sibling project 改动。
- data_service 改动，除非另开后端合同阶段。

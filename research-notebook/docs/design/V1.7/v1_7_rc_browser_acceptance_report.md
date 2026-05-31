# ResearchNotebook V1.7-RC Browser Acceptance Report

日期：2026-05-30

## 自动验收

| 命令 | 状态 |
| --- | --- |
| `npm run check` | PASS |
| `npm run smoke:v1.7-ux` | PASS |
| `npm run smoke:v1.5-e-e2e` | PASS |
| `npm run smoke:v1.1-visible-user-e2e` | NOT_RUN_THIS_ROUND |

说明：本轮 V1.7 修改前端 UX、文案、布局和文档，未修改 data_service 合同、AI provider、来源解析、EvidenceSpan 后端路径。已复跑 V1.5 真实数据 ChromeCLI 主路径，覆盖数字人资料导入、Notebook Guide、引用问答、citation 高亮、Studio 四类输出和资料外拒答。V1.1 visible-user 脚本包含非 PRD MVP 的 JSON source 案例，本轮不作为 V1.7 出门条件。

## 人工验收

| 项 | 状态 |
| --- | --- |
| 三列布局 | READY_FOR_HUMAN_REVIEW |
| 来源导入 | READY_FOR_HUMAN_REVIEW |
| Guide-first 问答 | READY_FOR_HUMAN_REVIEW |
| citation 定位 | READY_FOR_HUMAN_REVIEW |
| 输出四类工具 | READY_FOR_HUMAN_REVIEW |
| 中文文案 | READY_FOR_HUMAN_REVIEW |
| 窄屏无重叠 | READY_FOR_HUMAN_REVIEW |

## 当前决策

V1.7_RC_AUTOMATED_CHECK_PASS。

当前可进入人工 UX 验收。人工验收通过前，不声明 V1.7 最终完成。

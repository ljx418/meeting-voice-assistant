# ResearchNotebook V1.10 设计与验收索引

日期：2026-05-31

## 阶段定位

V1.10 是 V1.x 的 Phase 2/3 输出能力与 OCR / 扫描 PDF的最终决策阶段。

本阶段默认不直接实现 Audio Overview、PPT、思维导图、文档对比或 OCR。V1.10 的核心目标是：

1. 明确哪些能力继续保持 disabled / NOT_READY。
2. 明确如果要实现任一能力，需要哪些后端合同、provider、schema、UI、真实数据 smoke 和人工验收。
3. 防止把 disabled shell 或合同发现误写成功能 ready。

## 文档索引

| 文档 | 用途 |
| --- | --- |
| `v1_10_remaining_development_and_acceptance_plan.md` | V1.10 剩余开发及验收总计划。 |
| `v1_10_phase_2_3_output_decision_plan.md` | Phase 2/3 输出能力实现决策计划。 |
| `v1_10_ocr_scanned_pdf_decision_plan.md` | OCR / 扫描 PDF 实现决策计划。 |
| `v1_10_plan_audit.md` | V1.10 自审、规格漂移和虚假验收风险评估。 |
| `v1_10_manual_acceptance_checklist.md` | V1.10 手工验收清单。 |
| `v1_10_rc_disabled_boundary_report.md` | V1.10-RC disabled boundary 自动化验收报告。 |

## 当前建议

V1.10 当前建议为：

- OCR / 扫描 PDF：继续 `NOT_READY`，保留 `CONTRACT_DISCOVERY_READY`。
- Audio Overview：继续 `DISABLED_READY`。
- PPT generation：继续 `DISABLED_READY`。
- Mindmap：继续 `DISABLED_READY`。
- Document comparison：继续 `DISABLED_READY`。

若用户明确要求实现其中任一项，必须单独开独立阶段，不得一次性实现全部。

## 自动化验收入口

```bash
npm run smoke:v1.10-disabled-boundary
```

该命令只验证 disabled boundary 和既有真实 P0 来源 smoke 结果，不声明后续输出功能 ready。

## 仍不能声明

- OCR ready
- scanned PDF ready
- Audio Overview ready
- PPT generation ready
- Mindmap ready
- Document comparison ready
- all-source-type ready
- all websites URL ready
- cloud sync / collaboration ready

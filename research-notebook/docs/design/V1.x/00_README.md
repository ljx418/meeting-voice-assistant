# ResearchNotebook V1.x 总开发与验收索引

日期：2026-05-31

## 用途

本目录用于集中记录 V1.7 之后的 V1.x 剩余开发与验收计划，供外部审计和后续执行使用。

## 当前基线

- V1.7 自动化 UX hardening：PASS。
- V1.5 真实数据 ChromeCLI 主路径：PASS。
- V1.9 final PRD acceptance package：READY_FOR_FINAL_HUMAN_ACCEPTANCE。
- V1.10 Phase 2/3 / OCR disabled boundary：ACCEPTED。
- V1.x final PRD acceptance：V1_X_FINAL_ACCEPTANCE_PASS_LIMITED。
- 云同步 / 协作：已从 V1.x 范围剔除。

## 文档索引

| 文档 | 用途 |
| --- | --- |
| `v1_x_remaining_development_and_acceptance_plan.md` | V1.x 剩余开发阶段、验收标准、风险门禁和审计路径。 |
| `v1_x_final_prd_acceptance_report.md` | V1.x 最终 PRD 验收汇总报告，记录自动化结果和人工验收门禁。 |
| `v1_x_release_handoff.md` | V1.x release handoff 文档，当前基于已认可的交互式浏览器证据包进入 scoped sync。 |
| `v1_x_manual_acceptance_decision.md` | V1.x 交互式浏览器证据包人工认可结论。 |
| `v1_x_scoped_sync_status.md` | V1.x scoped sync 状态，记录当前因远端/仓库范围需要确认而暂停 commit / push。 |

## V1.10 相关文档

- `../V1.10/00_README.md`
- `../V1.10/v1_10_remaining_development_and_acceptance_plan.md`
- `../V1.10/v1_10_phase_2_3_output_decision_plan.md`
- `../V1.10/v1_10_ocr_scanned_pdf_decision_plan.md`
- `../V1.10/v1_10_plan_audit.md`
- `../V1.10/v1_10_manual_acceptance_checklist.md`
- `../V1.10/v1_10_rc_disabled_boundary_report.md`

## 当前命令入口

```bash
npm run smoke:v1.x-rc
```

该命令汇总 V1.9 / V1.10 的自动化证据，并读取已认可的交互式浏览器证据包结论生成 V1.x final PRD acceptance 报告。自动化结果不能替代后续抽样内容质量复核。

当前已结合交互式浏览器证据包人工认可结论，最终状态为 `V1_X_FINAL_ACCEPTANCE_PASS_LIMITED`。该状态仍是受限通过，不代表 all-source / all-domain / OCR / Phase 2/3 ready。

## 统一停止规则

任一后续阶段如果出现以下情况，停止自动推进，回到人工审计：

- PRD 规格漂移风险为 HIGH。
- 虚假验收风险为 HIGH。
- 需要人工质量判断但只有自动 smoke。
- 真实数据验收失败。
- 将未完成能力展示成 ready。
- 输出、fixture、日志泄露本地绝对路径、API key、cache path 或 artifact physical path。

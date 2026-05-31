# ResearchNotebook V1.10 Plan Audit

日期：2026-05-31

## 自审结论

V1.10 可以进入文档化决策阶段，但不建议直接进入 Phase 2/3 或 OCR 真实实现。

修订后执行结论：

- V1.10 disabled-boundary smoke 已新增。
- 该 smoke 不实现新功能，不发起 Phase 2/3 后端生成。
- 当前无新增致命或重大规格偏差。

审计结论：

- V1.10-0 Scope Rebase / PRD Decision Gate：GO。
- V1.10-A OCR / Scanned PDF Decision：GO，保持 NOT_READY。
- V1.10-B Audio Overview Decision：GO，保持 DISABLED_READY。
- V1.10-C PPT Generation Decision：GO，保持 DISABLED_READY。
- V1.10-D Mindmap Decision：GO，保持 DISABLED_READY。
- V1.10-E Document Comparison Decision：GO，保持 DISABLED_READY。
- V1.10-RC Disabled Boundary Acceptance：GO。

## 主要审计意见

| 审计项 | 风险 | 结论 |
| --- | --- | --- |
| OCR 容易被文本 PDF PASS_LIMITED 误扩展 | HIGH | 保持 OCR NOT_READY |
| Audio / PPT / Mindmap / Compare disabled shell 被误写成 ready | HIGH | 文档必须写 DISABLED_READY / NOT_READY |
| 一次性实现全部 Phase 2/3 | HIGH | 禁止，必须逐项独立开阶段 |
| 自动 smoke 替代人工质量验收 | HIGH | 禁止 |
| 云同步 / 协作回流 V1.x | MEDIUM | 保持 OUT_OF_SCOPE |

## 计划修正结果

已在 V1.10 计划中明确：

- 默认不实现 OCR。
- 默认不实现 Audio / PPT / Mindmap / Document comparison。
- 任一能力实现前必须有独立合同、schema、provider、真实 smoke 和人工验收。
- disabled shell 只能声明 `DISABLED_READY`，不能声明 ready。

## 风险评估

| 风险项 | 评级 | 说明 |
| --- | --- | --- |
| 规格漂移 | HIGH | 后置能力容易膨胀进 V1.x |
| 虚假验收 | HIGH | disabled shell 容易被误认成功能可用 |
| 当前执行风险 | LOW | 本轮只落盘计划和验收标准，不实现高风险功能 |

## 修订后审计意见闭环

| 审计意见 | 闭环方式 |
| --- | --- |
| Disabled shell 不等于 ready | V1.10 docs 和 smoke 均使用 NOT_READY / DISABLED_READY |
| 可抽取文本 PDF 不等于 OCR ready | smoke 读取 V1.4 P0 PDF_EXTRACTED，同时保留 OCR CONTRACT_DISCOVERY |
| Phase 2/3 disabled 工具不能发请求 | smoke 检查无 Phase 2/3 route string / artifact mutation |
| 需要记录 RC 环境和 final decision | `v1_10_rc_disabled_boundary_report.md` 自动落盘 |

## 停止规则

出现以下任一情况必须停止：

- 文档把 disabled shell 写成 ready。
- UI 对 disabled 工具发起后端请求。
- 没有 provider / schema / smoke 就实现真实输出。
- OCR 未接 provider 却声明扫描 PDF ready。
- Phase 2/3 任一单项通过后扩大成全部 ready。

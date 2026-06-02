# V2.3 OCR Provider Gate Plan Audit

日期：2026-06-02

## 审计结论

**当前状态**：待审计

## 审计检查表

### 规格漂移风险评估

| 检查项 | 状态 | 说明 |
| --- | --- | --- |
| 不声明 all PDF ready | ✅ | 计划明确限制为 "scanned PDF 受限 MVP" |
| 不声明 all-language OCR ready | ✅ | 计划只做单语言测试 |
| 不声明 all-layout OCR ready | ✅ | 计划只做受限 layout |
| Provider gate 决策正确 | ⏳ | 需要确认 provider 可用性 |
| OCR 结果进入 DocumentUnit 路径 | ⏳ | 需要确认 schema 对齐 |

### 虚假验收风险评估

| 检查项 | 状态 | 说明 |
| --- | --- | --- |
| Provider 可用性测试覆盖 | ⏳ | health probe 是否充分 |
| 扫描 PDF 样本测试 | ⏳ | 需要准备真实扫描 PDF 样本 |
| OCR 质量人工审查计划 | ⏳ | 人工审查标准是否明确 |
| bbox/confidence 可见性 | ⏳ | UI 如何展示置信度 |

### 实现风险评估

| 检查项 | 状态 | 说明 |
| --- | --- | --- |
| OCR provider 可用性 | ⏳ | 需要确认是否有可用 provider |
| OCR schema 与后端对齐 | ⏳ | OCRPage.page_num 等字段需要确认 |
| 前端 OCR UI 实现 | ⏳ | 需要新增 OCR 状态显示 |
| Scanned PDF 检测 | ⏳ | 如何区分扫描 PDF 和文本 PDF |

## 审计结论

**规格漂移风险**：MEDIUM
- OCR provider gate 是关键决策点

**虚假验收风险**：MEDIUM
- 需要准备真实扫描 PDF 样本
- 人工审查标准需要明确

**实现风险**：HIGH
- 无 provider 时保持 NOT_READY 是正确决策
- 但需要确认 provider 决策流程

**是否可以进入实现**：需要确认

### 关键决策点

V2.3 的核心是 provider gate。若无 provider：
- 保持 `OCR_DECISION_RECORDED`
- 不进入 V2.3-A ~ V2.3-D 实现

若有 provider：
- 进入 OCR 实现阶段
- 需要与后端对齐 OCR schema

### 前置确认事项

- [ ] 确认是否有可用的 OCR provider
- [ ] 若有 provider，确认 OCR schema（page_num、text、bbox、confidence）
- [ ] 若有 provider，确认 scanned PDF 测试样本
- [ ] 确认人工质量审查标准

若没有 provider，审计通过但停留在 DECISION_RECORDED。
若有 provider，需要进一步审计实现计划。
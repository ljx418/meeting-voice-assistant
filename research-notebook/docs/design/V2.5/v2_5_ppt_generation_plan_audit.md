# V2.5 PPT Generation Plan Audit

日期：2026-06-02

## 审计结论

**当前状态**：待审计

## 审计检查表

### 规格漂移风险评估

| 检查项 | 状态 | 说明 |
| --- | --- | --- |
| 不伪装 Markdown/JSON 为 PPT | ✅ | 计划明确区分 PPTX 和 SLIDE_OUTLINE_ONLY |
| PPTX / Outline decision 正确 | ⏳ | 需要确认 generator/export 能力 |
| citation binding 覆盖 | ⏳ | Slide.evidence_refs 需要确认 |
| 不声明 all presentation styles | ✅ | 计划限制为受限 MVP |

### 虚假验收风险评估

| 检查项 | 状态 | 说明 |
| --- | --- | --- |
| PPTX 可打开测试 | ⏳ | 需要验证真实 .pptx 文件 |
| Outline download 测试 | ⏳ | 需要验证 Markdown download |
| citation metadata 验证 | ⏳ | 需要验证每个 slide 有 evidence_refs |
| 人工质量审查标准 | ⏳ | 审查标准是否明确 |

### 实现风险评估

| 检查项 | 状态 | 说明 |
| --- | --- | --- |
| PPTX generator 可用性 | ⏳ | 需要确认是否有真实 PPTX 生成能力 |
| Slide artifact schema 与后端对齐 | ⏳ | Slide 结构需要确认 |
| 前端 Slide preview UI 实现 | ⏳ | 需要新增 SlidePreview 组件 |
| PPTX export vs outline 决策 | ⏳ | 需要提前确定方案 |

## 审计结论

**规格漂移风险**：MEDIUM
- PPTX vs SLIDE_OUTLINE_ONLY 决策需要提前确认

**虚假验收风险**：MEDIUM
- 需要验证真实 PPTX 可打开
- outline 方案需要明确标记

**实现风险**：MEDIUM
- 依赖 generator 能力
- 需要提前确定方案

**是否可以进入实现**：需要确认

### 关键决策点

V2.5 的核心是 PPTX vs SLIDE_OUTLINE_ONLY 决策。

若无法生成真实 PPTX：
- 使用 SLIDE_OUTLINE_ONLY 方案
- 提供 Markdown outline download
- 不伪装成 PPT

### 前置确认事项

- [ ] 确认是否有真实 PPTX 生成能力
- [ ] 若有，确认 slide artifact schema（title、bullets、speaker_notes、layout_hint、evidence_refs）
- [ ] 若无，确认 SLIDE_OUTLINE_ONLY 方案是否可接受
- [ ] 确认人工质量审查标准

根据确认结果，决定是进入 PPT_GENERATION_PASS_LIMITED 还是 SLIDE_OUTLINE_ONLY。
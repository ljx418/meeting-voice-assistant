# V2.6 Mindmap Plan Audit

日期：2026-06-02

## 审计结论

**当前状态**：待审计

## 审计检查表

### 规格漂移风险评估

| 检查项 | 状态 | 说明 |
| --- | --- | --- |
| 不把 Graph 伪装成 Mindmap | ✅ | 计划明确区分 Graph 和 Mindmap |
| Mindmap schema 与 PRD 一致 | ⏳ | MindmapNode 结构需要确认 |
| citation binding 覆盖 | ⏳ | node.evidence_refs 需要确认 |
| expand/collapse 语义正确 | ⏳ | UI 状态管理需要确认 |
| 不声明 all mindmap styles | ✅ | 计划限制为受限 MVP |

### 虚假验收风险评估

| 检查项 | 状态 | 说明 |
| --- | --- | --- |
| Mindmap 生成测试 | ⏳ | 需要验证 generator 输出 |
| expand/collapse 功能测试 | ⏳ | 需要验证 UI 状态管理 |
| citation drawer 集成测试 | ⏳ | 需要验证点击 node 打开 SourcePreview |
| 人工质量审查标准 | ⏳ | 审查标准是否明确 |

### 实现风险评估

| 检查项 | 状态 | 说明 |
| --- | --- | --- |
| Mindmap generator 可用性 | ⏳ | 需要确认是否有 generator |
| Mindmap artifact schema 与后端对齐 | ⏳ | MindmapArtifact 结构需要确认 |
| 前端 Mindmap canvas UI 实现 | ⏳ | 需要新增 MindmapCanvas 组件 |
| 与现有 Graph 组件的关系 | ⏳ | 是否复用 GraphPage 组件 |

## 审计结论

**规格漂移风险**：MEDIUM
- 需要明确 Mindmap 和 Graph 的区别

**虚假验收风险**：MEDIUM
- 需要验证 citation drawer 集成

**实现风险**：MEDIUM
- 依赖 mindmap generator 能力
- 需要确认与现有 Graph 的关系

**是否可以进入实现**：需要确认

### 关键决策点

1. Mindmap vs Graph：Mindmap 是用户生成的内容，Graph 是 workspace 的图结构
2. citation drawer 集成：点击 node 需要打开 SourcePreview

### 前置确认事项

- [ ] 确认是否有 mindmap generator
- [ ] 若有，确认 Mindmap artifact schema（node_id、label、parent_id、evidence_refs）
- [ ] 确认 mindmap UI 是否复用 Graph 组件
- [ ] 确认人工质量审查标准

若有 generator，审计通过后进入实现。
若无 generator，保持 NOT_READY。
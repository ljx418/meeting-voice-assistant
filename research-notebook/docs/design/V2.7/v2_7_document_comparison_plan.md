# V2.7 Document Comparison

日期：2026-06-02

## 阶段目标

实现 PRD Phase 3 文档对比受限 MVP。

**约束**：不把 Research report 伪装成 Document comparison，不声明 all document types ready。

## 阶段 Entry Gate

- [ ] V2.6 Mindmap Generation 通过验收
- [ ] 当前分支无未合并的 V2.6 功能变更
- [ ] Comparison generator 能力确认

## 子阶段

### V2.7-A Compare Contract

**目标**：定义 document comparison 数据结构。

**API Contract**：
```typescript
// 创建 Compare artifact
POST /api/workspaces/{workspace_id}/artifacts/compare
Request: {
  source_ids: string[]  // 至少 2 个
}
Response: {
  artifact: CompareArtifact
}

// CompareArtifact 结构
interface CompareArtifact {
  artifact_id: string
  workspace_id: string
  type: "compare"
  status: "generating" | "ready" | "error"
  compare_set: string[]  // source_ids
  result: ComparisonResult
  created_at: string
  error?: {
    code: string
    message: string
  }
}

interface ComparisonResult {
  summary: string  // 总体概述
  source_pairs: SourcePair[]  // 两两对比结果
  all_similarities?: Similarity[]  // 多文档共同点
  all_differences?: Difference[]  // 多文档分歧
}

interface SourcePair {
  source_a: string  // source_id
  source_b: string  // source_id
  source_a_title?: string
  source_b_title?: string
  similarities: Similarity[]
  differences: Difference[]
  conflicts: Conflict[]
}

interface Similarity {
  topic: string
  description: string
  evidence_refs: EvidenceRef[]
}

interface Difference {
  topic: string
  source_a_position: string  // A 的观点
  source_b_position: string  // B 的观点
  evidence_a: EvidenceRef[]
  evidence_b: EvidenceRef[]
}

interface Conflict {
  topic: string
  claim_a: string
  claim_b: string
  evidence_a: EvidenceRef[]
  evidence_b: EvidenceRef[]
  resolution?: string  // 如果有的话
}
```

**Compare 与 Research 的区别**：
| 属性 | Compare | Research |
|------|---------|-----------|
| 输入 | 多个文档 | 问题 + sources |
| 输出 | 文档间异同 | 基于 source 回答 |
| 目的 | 对比分析 | 信息提取 |
| evidence | 两侧证据 | 单侧证据 |

### V2.7-B Pairwise Comparison

**目标**：实现两文档对比。

**Pairwise Contract**：
```typescript
// 两文档对比
POST /api/workspaces/{workspace_id}/artifacts/compare
Request: {
  source_ids: [source_a, source_b]  // exactly 2
}
Response: {
  artifact: CompareArtifact
}
```

**约束**：
- 至少支持 2 个文档对比
- similarities / differences / conflicts 均绑定 evidence_refs

**验收**：
- [ ] 2 个文档对比结果正确
- [ ] 每项差异有 evidence_refs
- [ ] 每个冲突有两侧 evidence_refs

### V2.7-C Multi-document Comparison

**目标**：扩展到多文档对比。

**Multi-document Contract**：
```typescript
// 多文档对比
POST /api/workspaces/{workspace_id}/artifacts/compare
Request: {
  source_ids: string[]  // 3+
}
Response: {
  artifact: CompareArtifact
  // result.all_similarities 包含共同点
  // result.all_differences 包含分歧
}
```

**多文档场景语义**：
- `all_similarities`：所有文档共同持有的观点
- `all_differences`：文档之间的分歧

### V2.7-D Comparison UI

**目标**：展示对比结果并支持 citation 跳转。

**UI 组件**：
```typescript
// ComparePanel 组件
interface ComparePanelProps {
  artifact: CompareArtifact
  onSourceClick?: (source_id: string) => void
  onEvidenceClick?: (evidence: EvidenceRef) => void
}

// 功能
- 显示 summary
- 显示 source pairs（两两对比）
- 或显示 all_similarities/all_differences（多文档）

// SourcePairView 组件
interface SourcePairViewProps {
  pair: SourcePair
  onSourceClick: (source_id: string) => void
  onEvidenceClick: (evidence: EvidenceRef) => void
}

// 功能
- side-by-side 显示两个 source
- highlights 差异部分
- 点击 source 跳转

// ConflictCard 组件
interface ConflictCardProps {
  conflict: Conflict
  onEvidenceClick: (evidence: EvidenceRef) => void
}

// 功能
- 显示 topic
- 显示 claim_a 和 claim_b
- 显示两侧 evidence（可点击跳转）
```

**与 Research 的区分**：
```typescript
// Studio 页面中
{artifact.type === 'compare' && <ComparePanel artifact={artifact} />}
{artifact.type === 'research' && <ResearchReport artifact={artifact} />}

// Compare 入口
<Button onClick={() => startCompare()}>
  对比文档
</Button>

// Research 入口
<Button onClick={() => startResearch()}>
  生成 Research Report
</Button>
```

**验收**：
- [ ] 至少支持 2 个文档对比
- [ ] similarities / differences / conflicts 均绑定 evidence_refs
- [ ] conflict 两侧证据可跳转
- [ ] 不把 Research report 当作 Compare

### V2.7-RC Comparison Quality Review

**目标**：人工确认对比结果质量。

**人工审查检查项**：
- [ ] 支持 2 个文档对比
- [ ] 支持 3+ 文档对比
- [ ] 证据绑定正确
- [ ] 冲突解析逻辑正确
- [ ] 不把 Research report 当作 Compare

**质量标准**：
- similarities/differences/conflicts 有明确区分
- 每个 claim 有 evidence_refs
- evidence_refs 对应的 source 确实包含相关内容

## 风险评估

| 风险 | 等级 | 缓解策略 |
| --- | --- | --- |
| Comparison generator 不可用 | HIGH | Phase 1 先确认 generator |
| 冲突检测质量不达标 | MEDIUM | 人工确认 claim 准确性 |
| 与 Research 混淆 | MEDIUM | UI 上明确区分 |

## 实现顺序

### Phase 1: Comparison Generator 确认（1天）
1. 调用 compare API
2. 确认 generator 可用性
3. 若不可用，记录 NOT_READY，结束

### Phase 2: Compare Schema 对齐（1-2天）
1. 与后端对齐 CompareArtifact schema
2. 确认 SourcePair/Similarity/Difference/Conflict 结构
3. 确认 evidence_refs 绑定

### Phase 3: 前端 Compare UI（2-3天）
1. ComparePanel 组件
2. SourcePairView 组件
3. ConflictCard 组件
4. citation 跳转

### Phase 4: Smoke + Manual Review（1天）
1. 运行 Compare smoke 测试
2. 人工质量审查
3. 更新报告

## 出门状态

- `DOCUMENT_COMPARISON_PASS_LIMITED`

## 仍不声明

- all document types ready
- full production ready

## 下一步

V2.7 通过后进入 V2.8 Final PRD Expanded RC。
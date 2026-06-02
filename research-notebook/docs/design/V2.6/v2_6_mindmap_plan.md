# V2.6 Mindmap Generation

日期：2026-06-02

## 阶段目标

实现 PRD Phase 3 思维导图受限 MVP。

**约束**：不把现有 Graph 伪装成 Mindmap，不声明 all mindmap styles ready。

## 阶段 Entry Gate

- [ ] V2.5 PPT Generation 通过验收
- [ ] 当前分支无未合并的 V2.5 功能变更
- [ ] Mindmap generator 能力确认

## 子阶段

### V2.6-A Mindmap Schema

**目标**：定义 mindmap 数据结构。

**API Contract**：
```typescript
// 创建 Mindmap artifact
POST /api/workspaces/{workspace_id}/artifacts/mindmap
Request: {
  source_ids: string[]
  topic?: string
  max_depth?: number  // 默认 3，最大 5
}
Response: {
  artifact: MindmapArtifact
}

// MindmapArtifact 结构
interface MindmapArtifact {
  artifact_id: string
  workspace_id: string
  type: "mindmap"
  status: "generating" | "ready" | "error"
  root_node: MindmapNode
  created_at: string
  error?: {
    code: string
    message: string
  }
}

interface MindmapNode {
  node_id: string
  label: string
  summary?: string        // 节点摘要，用于 hover
  parent_id?: string     // null for root
  children?: MindmapNode[]  // 递归结构
  evidence_refs?: EvidenceRef[]
  position?: {            // 可选，用于固定布局
    x: number
    y: number
  }
}
```

**Mindmap 与 Graph 的区别**：
| 属性 | Mindmap | Graph |
|------|---------|-------|
| 生成方式 | 用户触发，基于 sources | 自动构建，基于 workspace |
| 结构 | 树形（parent-child） | 网状（任意连接） |
| 内容 | 用户可读的主题 | 实体关系 |
| 用途 | 梳理思路 | 探索关联 |
| 触发 | Studio → 生成 Mindmap | 自动生成 |

### V2.6-B Mindmap Generator

**目标**：基于 sources 生成 mindmap。

**Generation Contract**：
```typescript
// 生成 mindmap
POST /api/workspaces/{workspace_id}/artifacts/mindmap/generate
Request: {
  source_ids: string[]
  topic?: string
  max_depth?: number
}
Response: {
  artifact_id: string
  status: "generating"
}

// 获取生成状态
GET /api/workspaces/{workspace_id}/artifacts/{artifact_id}/status
Response: {
  artifact_id: string
  status: "generating" | "ready" | "error"
  progress?: number
}
```

**约束**：
- 节点绑定 evidence_refs
- 若 sources 不足，拒绝生成：
```typescript
{
  error: {
    code: "INSUFFICIENT_SOURCES",
    message: "资料不足，无法生成 Mindmap。请先添加更多 sources。"
  }
}
```

### V2.6-C Mindmap UI

**目标**：展示 mindmap 并支持 citation drawer。

**UI 组件**：
```typescript
// MindmapCanvas 组件
interface MindmapCanvasProps {
  artifact: MindmapArtifact
  onNodeClick?: (node: MindmapNode) => void
  onNodeExpand?: (node_id: string) => void
  onNodeCollapse?: (node_id: string) => void
}

// 功能
- 可缩放画布（zoom in/out/reset）
- 可拖拽画布（pan）
- 节点展开/收起
- 点击节点 → 打开 SourcePreview

// MindmapNode 组件
interface MindmapNodeProps {
  node: MindmapNode
  isExpanded: boolean
  onExpand: () => void
  onCollapse: () => void
  onClick: () => void
}

// 功能
- 显示 label
- 显示子节点数量（收起时）
- expand/collapse 按钮
- evidence indicator（如果有 evidence_refs）
```

**与 Graph 的区分**：
```typescript
// 在 Studio 页面中
{artifact.type === 'mindmap' && <MindmapCanvas artifact={artifact} />}
{artifact.type === 'graph' && <GraphContextPanel artifact={artifact} />}

// Mindmap 入口
<Button onClick={() => generateMindmap()}>
  生成思维导图
</Button>

// Graph 入口（自动生成，用户无法手动触发）
// GraphContextPanel 仅在 session 中显示
```

**验收**：
- [ ] 节点绑定 evidence_refs
- [ ] 节点可展开 / 收起
- [ ] 点击节点打开 SourcePreview
- [ ] 不与 Graph 混淆

### V2.6-RC Mindmap Review

**目标**：人工确认 mindmap 结构和质量。

**人工审查检查项**：
- [ ] 节点绑定 evidence_refs
- [ ] expand/collapse 正常工作
- [ ] citation drawer 集成正确
- [ ] 不把现有 Graph 当作 Mindmap
- [ ] 树形结构清晰

**质量标准**：
- root_node 有明确的中心主题
- 每个节点有 label
- 节点之间关系清晰
- evidence_refs 对应的 source 确实包含相关内容

## 风险评估

| 风险 | 等级 | 缓解策略 |
| --- | --- | --- |
| Mindmap generator 不可用 | HIGH | Phase 1 先确认 generator |
| 树形结构质量不达标 | MEDIUM | 设置 evidence_refs 覆盖率阈值 |
| 与 Graph 混淆 | MEDIUM | UI 上明确区分 |

## 实现顺序

### Phase 1: Mindmap Generator 确认（1天）
1. 调用 mindmap generate API
2. 确认 generator 可用性
3. 若不可用，记录 NOT_READY，结束

### Phase 2: Mindmap Schema 对齐（1-2天）
1. 与后端对齐 MindmapArtifact schema
2. 确认 MindmapNode 结构
3. 确认 generation API

### Phase 3: 前端 Mindmap UI（2-3天）
1. MindmapCanvas 组件
2. MindmapNode 组件
3. expand/collapse 功能
4. citation drawer 集成

### Phase 4: Smoke + Manual Review（1天）
1. 运行 Mindmap smoke 测试
2. 人工质量审查
3. 更新报告

## 出门状态

- `MINDMAP_PASS_LIMITED`

## 仍不声明

- all mindmap styles ready
- full production ready

## 下一步

V2.6 通过后进入 V2.7 Document Comparison。
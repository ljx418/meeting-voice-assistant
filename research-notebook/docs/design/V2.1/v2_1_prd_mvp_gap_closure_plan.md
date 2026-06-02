# V2.1 PRD MVP Gap Closure 开发计划

日期：2026-06-02

## 1. 背景

V2 已完成 V2-0 ~ V2-RC，当前状态为 `V2_RELEASE_HANDOFF_READY_WITH_LIMITATIONS`。V2.1 目标补齐 Phase 1 中仍未完整产品化的能力。

## 2. 阶段 Entry Gate

本阶段开始前必须确认：

- [ ] V2 final handoff 已通过 `npm run check`
- [ ] V2.x remaining plan 已读过
- [ ] 当前分支无未合并的 V2 功能变更

## 3. 开发任务（更新）

> ⚠️ **范围调整**：根据 Plan Audit 结果，Studio artifact 管理已标记为 `DEFERRED`，将在后续 V2.x 阶段处理。AI 质量闭环依赖现有 `generation_metadata.fallback_mode` 字段，无需新增 API。

### 3.1 Sources 搜索入口

**目标**：用户能按标题、类型、正文片段搜索来源。

**API Contract**（新增）：
```
GET /api/workspaces/{workspace_id}/sources/search?q={query}&type_filter={type}&limit={limit}
Response: {
  sources: SourceSummary[]
  total: number
  query: string
}
```

**前端实现**：
- 在 SourceLibrary 页面添加 SearchBar 组件
- 搜索框支持 debounce (300ms)
- 搜索状态：idle / searching / results / no_results / error
- 搜索结果可点击打开 SourcePreview / DocumentUnit

**边界约束**：
- 搜索失败时不清空来源列表，保持上次有效状态
- 搜索结果可点击打开 SourcePreview / DocumentUnit

**验收**：
- [ ] 搜索框可见且可输入
- [ ] 搜索结果列表正确显示
- [ ] 点击结果打开 SourcePreview
- [ ] 搜索失败保持来源列表不变

### 3.2 Notes 保存与管理

**目标**：用户能把回答或摘录保存为 Note，支持手写 note、编辑、删除、citation 跳转。

**降级决策**：后端 Notes API 不存在，采用 **localStorage 降级方案**，后续迁移到后端。

**API Contract**（localStorage）：
```typescript
// localStorage key: `notes_${workspaceId}`
interface Note {
  note_id: string
  workspace_id: string
  content: string
  evidence_refs: EvidenceRef[]
  created_at: string
  updated_at: string
}

// 操作
notes = JSON.parse(localStorage.getItem(`notes_${workspaceId}`) || '[]')
```

**前端组件**：
- `NoteList`：显示当前 workspace 所有 notes（从 localStorage 读取）
- `NoteEditor`：创建/编辑 note，支持选中文字后保存
- `NoteCard`：单个 note 展示，支持编辑/删除按钮

**功能流程**：
1. 从 QA 回答保存：选中文字 → 右键/按钮 → 保存到 Notes（携带 evidence_refs）
2. 从 SourcePreview 摘录：选中文字 → 保存到 Notes
3. 手写 note：点击"新建 Note" → 进入空白编辑器
4. 编辑/删除：NoteCard 上 hover 显示编辑/删除按钮
5. citation 跳转：点击 note 中的 citation → 打开 EvidenceSpan

**数据持久化**：
- 使用 `localStorage` 存储
- Key: `notes_${workspaceId}`
- JSON 序列化/反序列化

**未来迁移**：
当后端 Notes API 实现后，替换 localStorage 读写为 API 调用。

**验收**：
- [ ] 能从 QA 回答保存 note
- [ ] 能从 SourcePreview 摘录保存 note
- [ ] 能手写创建 note
- [ ] 能编辑已有 note
- [ ] 能删除 note
- [ ] note 保留 evidence_refs
- [ ] citation 跳转正确
- [ ] 刷新页面后 notes 仍存在（localStorage 持久化）

### 3.3 Notebook 删除语义

**目标**：决策归档是否满足 PRD 删除；若不满足，补安全删除。

**当前状态确认**：
V2 已有 `archive` 方法（`workspaceQueries.ts` 中的 `useArchiveWorkspaceMutation`），但需确认：
1. 后端 `DELETE /api/workspaces/{workspace_id}` 的实际行为（软删除 vs 物理删除）
2. 前端是否需要确认弹窗

**API Contract（假设归档）**：
```
POST /api/workspaces/{workspace_id}/archive
Response: { workspace_id: string, archived: boolean }

恢复操作（如需）：
POST /api/workspaces/{workspace_id}/unarchive
```

**决策点**：
| 后端行为 | 前端实现 |
|---|---|
| 软删除（已实现 archive） | 保持现有行为，添加确认弹窗 |
| 物理删除 | 添加确认弹窗 + 级联删除提示 |

**方案 A - 归档（软删除）**：
- `DELETE` → 使用现有 `archive` API
- Notebook 列表过滤 `archived != true`
- 支持恢复（`unarchive`）

**方案 B - 永久删除**：
- `DELETE /api/workspaces/{workspace_id}` → 物理删除
- 显示确认弹窗："此操作不可恢复，确定删除？"
- 级联删除关联的 sources、notes、artifacts

**前端实现**：
- 在 WorkspacePage 添加删除按钮
- 点击后显示确认弹窗
- 删除后重定向到 HomePage

**验收**：
- [ ] 删除按钮存在且可点击
- [ ] 删除前显示确认弹窗
- [ ] 删除后 Notebook 从列表消失
- [ ] 删除的资源（sources、notes、artifacts）有正确处理策略

### 3.4 Studio Artifact 管理

**目标**：输出列表、重命名、删除、重新生成、导出状态可见。

**当前 API（dataServiceClient）**：
```typescript
// 创建 artifact（已有）
studio.createArtifact(workspaceId, { artifact_type })

// 获取 artifact（通过 workspace detail）
workspace.detail → artifact_refs

// 需要新增的 API：
- GET /api/workspaces/{workspace_id}/artifacts → artifact 列表
- PUT /api/workspaces/{workspace_id}/artifacts/{artifact_id} → 重命名
- DELETE /api/workspaces/{workspace_id}/artifacts/{artifact_id} → 删除
- POST /api/workspaces/{workspace_id}/artifacts/{artifact_id}/regenerate → 重新生成
```

**新增 API Contract**：
```
GET /api/workspaces/{workspace_id}/artifacts
Response: {
  artifacts: [{
    artifact_id: string
    artifact_type: 'notes' | 'study_guide' | 'briefing_doc' | 'faq'
    title: string
    created_at: string
    status: 'ready' | 'generating' | 'failed'
  }]
}

PUT /api/workspaces/{workspace_id}/artifacts/{artifact_id}
Body: { title: string }
Response: { artifact: Artifact }

DELETE /api/workspaces/{workspace_id}/artifacts/{artifact_id}
Response: { deleted: boolean }

POST /api/workspaces/{workspace_id}/artifacts/{artifact_id}/regenerate
Response: { artifact_id: string, status: 'generating' }
```

**前端组件**：
- `ArtifactList`：显示当前 workspace 所有 artifacts
- `ArtifactCard`：name, type, created_at, status, actions
- `ArtifactRenameModal`：点击 name → inline edit → 保存

**功能**：
- 列表：显示所有生成的 artifact（按类型分组）
- 重命名：点击 name → inline edit → 保存
- 删除：hover 显示删除按钮 → 确认 → 删除
- 重新生成：点击 regenerate → 重新调用生成 API
- 导出状态：显示 .md / .json export 是否可下载

**验收**：
- [ ] 能看到所有 artifacts 列表
- [ ] 能重命名 artifact
- [ ] 能删除 artifact
- [ ] 能重新生成 artifact
- [ ] 导出状态可见（.md / .json 可下载）
- [ ] 删除/重新生成不丢失 citation

### 3.5 AI Guide / QA / Studio 质量闭环

**目标**：修复 fallback / schema mismatch，从 `REVIEWED_WITH_LIMITATIONS` 推进到 `PASS_LIMITED`。

**问题分类**：

| 问题类型 | 描述 | 根因 |
|---|---|---|
| fallback | AI 返回了未基于 source 的回答 | 后端 fallback 模式触发但前端未识别 |
| schema mismatch | 返回格式不符合前端期望 | 后端响应字段名/结构变化 |
| 拒答错误 | 资料充足时仍拒答 | threshold 设置过高 |
| 幻觉 | 回答包含 source 中不存在的信息 | prompt 质量问题 |

**当前已有**：
- `generation_metadata` 包含 `fallback_mode: boolean`
- `response_schema` 字段存在
- `answerBasis` 包含 'source_supported' | 'source_grounded_refusal' 等

**修复策略**：

1. **fallback 识别**
```typescript
// 在 QA 组件中检查 generation_metadata
if (response.generation_metadata?.fallback_mode) {
  // 显示 "AI 基于有限信息回答" 提示
  // 不显示 "source-grounded" 标志
}
```

2. **schema validation layer**
```typescript
// 添加 schema 验证
function validateQueryResponse(response: unknown): QueryResponse {
  const required = ['answer', 'evidence', 'noEvidence'];
  // 验证存在且类型正确
  // 抛出 DataServiceError 如果失败
}
```

3. **AI 质量评分 API**
```
POST /api/workspaces/{workspace_id}/quality/ai-score
Body: { response_id: string, score: 1-5, comment?: string }
Response: { accepted: boolean }
```

**质量标准**：
- Guide 可用性 >= 4/5（用户评分）
- citation 可定位率 >= 90%
- 拒答正确率 >= 80%
- 高危幻觉 = 0

**验证方法**：
1. 自动化：检查 `generation_metadata.fallback_mode` 出现频率
2. 自动化：检查 evidence 中 `traceAvailable: true` 比例
3. 人工：抽样 20 个 QA 对话，评估可用性

**验收**：
- [ ] fallback 场景正确识别并显示提示
- [ ] schema mismatch 不再导致 UI crash
- [ ] AI 质量人工评分达标
- [ ] citation 可定位率 >= 90%
- [ ] 拒答正确率 >= 80%
- [ ] 高危幻觉 = 0

## 4. 风险评估

| 风险 | 等级 | 缓解策略 |
| --- | --- | --- |
| 后端 API 缺失（Notes/Artifacts） | MEDIUM | 优先对齐 API contract，再实现前端；若后端不支持，先用 localStorage 降级 |
| 搜索性能 | LOW | debounce (300ms) + 懒加载 |
| Note citation 一致性 | MEDIUM | 添加 integration test 验证 evidence_refs 不丢失 |
| AI 质量阈值达标 | MEDIUM | 先修复 fallback 识别，再人工评分验证 |
| Notebook 删除后端行为 | MEDIUM | 先测试 archive API，确认行为再实现 UI |

## 5. 实现顺序

1. **Phase 1：API Contract 对齐**（1-2天）
   - 确认 Notes API 是否存在
   - 确认 Artifacts 列表 API 是否存在
   - 确认 archive vs delete 行为

2. **Phase 2：前端基础功能**（2-3天）
   - Sources 搜索 UI + debounce
   - Notes CRUD UI + evidence_refs
   - Artifact 列表 UI

3. **Phase 3：质量闭环**（1-2天）
   - fallback 识别和显示
   - schema validation
   - 人工评分验证

## 6. 验收标准汇总

| 功能 | 验收条件 | 验证方法 |
| --- | --- | --- |
| Sources 搜索 | 用户能搜索来源并打开 SourcePreview / DocumentUnit | 手动测试 10 个查询 |
| Notes 保存 | 用户能把回答或摘录保存为 Note | 手动测试保存流程 |
| Notes 管理 | Notes 保留 evidence_refs，citation 可跳转 | Integration test |
| Notebook 删除 | 删除语义符合 PRD，有确认弹窗 | 手动测试删除流程 |
| Studio artifact | 可管理且不丢失 citation | 手动测试 CRUD |
| AI 质量 | Guide 可用性 >= 4/5，citation 可定位率 >= 90%，拒答正确率 >= 80%，高危幻觉 = 0 | 人工评分 20 个样本 |

## 7. 出门状态

- `PRD_MVP_GAP_CLOSURE_PASS_LIMITED`

## 8. 下一步

V2.1 通过后进入 V2.2 Sources P1 URL Hardening。
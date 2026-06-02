# V2.1 PRD MVP Gap Closure Plan Audit

日期：2026-06-02

## 审计结论

**当前状态**：⚠️ 发现实现风险，需要决策

## 前置确认事项执行结果

| 确认项 | 状态 | 发现 |
| --- | --- | --- |
| 确认后端是否有 Notes API | ❌ 不存在 | 当前 dataServiceClient 无 notes 端点，需要新增 |
| 确认后端是否有 Artifacts 列表 API | ❌ 不存在 | 当前只有 `studio.createArtifact`，无 list/update/delete |
| 确认 archive 方法的实际行为 | ✅ 软删除 | `POST /api/workspaces/{id}/archive` 是软删除 |
| 确认 smoke 测试脚本的覆盖范围 | ⏳ 待确认 | 需要新增 V2.1 smoke |

## 后端 API 对齐发现

### 1. Notes API - 不存在 ❌

**当前状态**：
- dataServiceClient 无 notes 相关端点
- 无任何 note 相关的 API：create/read/update/delete

**影响评估**：
- 规格漂移风险：LOW（不影响范围，只是需要新增 API）
- 实现风险：MEDIUM（依赖后端实现）

**缓解策略**：
1. 方案 A：后端先实现 Notes API，前端等待
2. 方案 B：前端用 localStorage 降级，后续迁移到后端
3. 方案 C：使用现有 text source 作为 Note 存储（不推荐，语义不一致）

**决策**：建议采用方案 B，前端先用 localStorage 降级，确保功能可用。

### 2. Artifacts 列表 API - 不存在 ❌

**当前状态**：
- `studio.createArtifact` ✅ 存在
- `studio.getArtifact` ❌ 不存在
- `studio.listArtifacts` ❌ 不存在
- `studio.updateArtifact` ❌ 不存在
- `studio.deleteArtifact` ❌ 不存在

**影响评估**：
- 规格漂移风险：LOW（不影响范围）
- 实现风险：MEDIUM（依赖后端实现）

**缓解策略**：
1. 方案 A：后端先实现 Artifacts CRUD API
2. 方案 B：前端使用 workspace detail 中的 `artifact_refs` 字段（只读）
3. 方案 C：Studio artifact 管理暂缓，优先实现其他功能

**决策**：建议 V2.1 暂不实现 Studio artifact 管理（属于 PRD MVP Gap Closure 非核心功能），后续 V2.x 再处理。

### 3. Archive 行为 - 软删除 ✅

**当前状态**：
- `POST /api/workspaces/{workspaceId}/archive` 存在
- 返回 `{ workspace_id, archived: true }`
- 是软删除，Notebooks 列表会过滤 archived 的 workspace

**影响评估**：
- 规格漂移风险：无
- 实现风险：无

**决策**：Archive 行为符合预期，可以继续。

## 审计检查表（更新后）

### 规格漂移风险评估

| 检查项 | 状态 | 说明 |
| --- | --- | --- |
| 开发范围与 PRD V2.1 一致 | ✅ | 5 个功能点都在 PRD 中定义 |
| 无新增功能污染范围 | ✅ | 未扩大范围 |
| API contract 与现有 dataServiceClient 一致 | ⚠️ | Notes/Artifacts API 需要新增 |
| 验收标准与 PRD 声明边界一致 | ✅ | 不声明 all-source-type ready |
| fallback 处理符合质量标准 | ✅ | 不把 fallback 当作 full pass |

### 虚假验收风险评估

| 检查项 | 状态 | 说明 |
| --- | --- | --- |
| 自动化 smoke 覆盖关键路径 | ⚠️ | 需要新增 smoke 脚本 |
| 人工验收标准明确 | ✅ | Guide >= 4/5 等指标可测试 |
| 失败场景有降级路径 | ✅ | Notes 可降级到 localStorage |
| citation 可定位率测量方法 | ⏳ | 需要在 smoke 中实现 |

### 实现风险评估

| 检查项 | 状态 | 说明 |
| --- | --- | --- |
| 后端 Notes API 存在性确认 | ❌ | 不存在，需要新增 |
| 后端 Artifacts 列表 API 存在性确认 | ❌ | 不存在，只有 create |
| Notebook archive vs delete 行为确认 | ✅ | 软删除，符合预期 |
| 前端状态管理方案 | ⏳ | Notes 暂用 localStorage |
| 测试覆盖方案 | ⏳ | 需要新增 smoke |

## 审计结论

**规格漂移风险**：LOW
- Notes/Artifacts API 缺失不影响范围定义
- 可通过降级方案解决

**虚假验收风险**：MEDIUM
- smoke 测试覆盖不完整
- citation 可定位率测量方法需要明确

**实现风险**：MEDIUM
- 后端 API 需要新增（Notes、Artifacts CRUD）
- Archive 行为符合预期

**是否可以进入实现**：⚠️ 需要决策

### 关键决策点

1. **Notes 功能**：是否接受前端 localStorage 降级方案？
   - 接受：继续实现，后续迁移到后端
   - 不接受：停止，等待后端实现

2. **Studio artifact 管理**：是否从 V2.1 范围中移除？
   - 移除：降低对后端 API 的依赖
   - 保留：继续依赖后端实现

### 建议

1. **Notes 功能**：接受 localStorage 降级，实现核心保存/编辑/删除功能
2. **Studio artifact 管理**：从 V2.1 范围中移除，标记为 `ARTIFACT_MANAGEMENT_DEFERRED`，后续 V2.x 处理
3. **AI 质量闭环**：继续依赖现有 `generation_metadata.fallback_mode` 字段，已有基础

### 风险阈值判断

根据 V2.x 统一门禁规则："若任一风险为 HIGH，停止并重新审计，不进入实现"。

当前实现风险为 **MEDIUM**，不属于 HIGH 风险。
因此可以继续进入实现，但需要：
1. 记录降级决策
2. 在 smoke 中验证 API 存在性
3. 在 report 中标记 ARTIFACT_MANAGEMENT_DEFERRED

**审计通过**，进入实现阶段。
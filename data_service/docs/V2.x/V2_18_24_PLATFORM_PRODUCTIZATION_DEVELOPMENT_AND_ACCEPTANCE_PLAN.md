# V2.18-V2.24 开发与验收计划

## 1. 总体原则

每个阶段必须遵循：

1. 先制定 phase-specific development plan、acceptance plan、audit report。
2. 开发前关闭 fatal / major 规格偏差。
3. 使用真实 `data_service` repo 验收。
4. 涉及大项目能力时补 HarnessOS 或同类大 repo E2E。
5. 验收必须检查 artifact 落盘、readback、public contract、MCP/HTTP/CLI parity。
6. 不得用 mock-only 结果标记 accepted。

## 2. Phase 84：V2.18 Product Console & Report UX

### 目标

统一项目智能入口，减少 raw JSON 依赖。

### 开发内容

- Console overview payload。
- Console HTML/read API。
- Evidence / architecture / context / runtime / patch preview 分区。
- accepted / needs_review / blocked 状态视图。
- 下一步操作建议。

### 验收

- data_service 真实 repo 生成 console view。
- 页面不引入后端 artifact 中不存在的事实。
- blocker 和 unresolved 必须展示。
- HTML escaping / link sanitization。
- 前端 build 通过。

## 3. Phase 85：V2.19 Artifact Schema & Public Contract Consolidation

### 目标

统一 artifact schema、public envelope 和 validator。

### 开发内容

- 通用 artifact envelope。
- Artifact schema validator。
- Row artifact / summary artifact 区分。
- Public API envelope parity tests。
- Artifact refs integrity checker。

### 验收

- 主要 V2 artifacts 可通过 validator。
- 无 schema_version 的新 artifact 不允许 accepted。
- `.jsonl` 文件必须是真 row JSONL，summary 用 `.json`。
- HTTP/MCP/CLI 输出 stable fields 一致。

## 4. Phase 86：V2.20 MCP Tool Discovery & Agent Workflow Guide

### 目标

让外部 Agent 能发现工具、理解调用顺序。

### 开发内容

- MCP Tool Catalog artifact。
- Tool group / dependency / next_actions。
- Workflow recommendation API。
- Goal-based call sequences。
- Tool failure remediation guide。

### 验收

- 156 tools 级别的 registry 能生成 catalog。
- 每个 tool 至少有 group、description、input schema、preconditions、outputs、failure modes。
- 给定目标 `coding_task_preparation` 能返回稳定调用链。
- 不推荐 missing / deprecated tool。

## 5. Phase 87：V2.21 Incremental Build & Large Repo Performance

### 目标

降低大项目重复构建成本。

### 开发内容

- Snapshot diff reader。
- Build impact planner。
- Artifact cache invalidation。
- Scan budget report。
- Large repo scan profile。

### 验收

- 修改单个 fixture 文件后只刷新相关 artifact 或说明为何全量刷新。
- 输出 reused / refreshed / invalidated。
- skipped files 和 warnings repo-relative。
- 不静默跳过失败。

## 6. Phase 88：V2.22 Provider Plugin System

### 目标

建立语义 provider 插件化边界。

### 开发内容

- Provider adapter SDK。
- Provider health/config/execution contract。
- Python AST mandatory baseline 保持。
- tree-sitter / Jedi / LSP optional unavailable contract。
- Provider result confidence policy。

### 验收

- AST provider 必须可用。
- 未配置 optional provider 返回 structured unavailable。
- health-known 不得标记 execution accepted。
- provider output 必须带 evidence_refs / confidence / extractor。

## 7. Phase 89：V2.23 Governance Feedback Loop

### 目标

把质量治理从“报告”推进到“反馈-规则-生效-撤销”闭环。

### 开发内容

- Feedback target resolver。
- Correction rule builder。
- Rule review workflow。
- Read-time overlay。
- Revoke semantics。
- Governance impact report。

### 验收

- feedback -> rule -> approve -> read output applied_rules。
- revoke 后 applied_rules 消失。
- source artifact hash 不变。
- missing target feedback 被拒绝。

## 8. Phase 90：V2.24 Production Readiness & CI Hardening

### 目标

形成可持续维护的生产化门禁。

### 开发内容

- 测试分层。
- warning budget。
- public contract snapshot tests。
- artifact validation gate。
- security/redaction gate。
- release readiness checklist。

### 验收

- unit / contract / artifact / real repo e2e 分层可运行。
- known warning 分类并设置 budget。
- public payload 不含 absolute path / secret / traceback。
- release readiness report 生成。

## 9. 全局出门条件

V2.18-V2.24 完成时必须满足：

- 用户可以通过 console 理解项目状态。
- Agent 可以通过 tool catalog 获取推荐调用链。
- 主要 artifacts 有 validator。
- 增量构建能说明 reused / refreshed / invalidated。
- Provider 插件 contract 清晰。
- Governance feedback loop 跑通。
- CI 和测试门禁可长期维护。

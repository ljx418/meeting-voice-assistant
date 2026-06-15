# V2.18-V2.24 目标架构：平台产品化与生产化

## 1. 架构目标

当前系统已经具备大量项目智能能力。目标架构要解决的问题不是“再加更多孤立工具”，而是：

```text
让工具可发现；
让产物可验证；
让报告可操作；
让构建可增量；
让 provider 可插拔；
让治理可闭环；
让 CI 可生产化防护。
```

## 2. 目标架构总览

```text
┌────────────────────────────────────────────────────────────┐
│                 Project Intelligence Console               │
│  Overview / Evidence / Architecture / Agent / Runtime      │
└───────────────────────────┬────────────────────────────────┘
                            │ reads public contracts
┌───────────────────────────▼────────────────────────────────┐
│               Public API / MCP / CLI Contract Layer         │
│  Tool Catalog / Workflow Guide / V2 Envelope / Errors       │
└───────────────────────────┬────────────────────────────────┘
                            │ validated artifacts
┌───────────────────────────▼────────────────────────────────┐
│                  Artifact Contract & Validator              │
│  schema_version / refs / evidence / warnings / needs_review │
└──────────────┬────────────┬───────────────┬────────────────┘
               │            │               │
┌──────────────▼───┐ ┌──────▼────────┐ ┌────▼─────────────┐
│ Incremental Build│ │ Provider SDK   │ │ Governance Loop  │
│ diff/cache/budget│ │ AST/tree/Jedi  │ │ feedback/rules   │
└──────────────┬───┘ └──────┬────────┘ └────┬─────────────┘
               │            │               │
┌──────────────▼────────────▼───────────────▼────────────────┐
│                  Existing V2.0-V2.17 Capabilities           │
│ snapshot / surface / symbols / architecture / context /     │
│ workbench / patch preview / runtime profile / quality       │
└────────────────────────────────────────────────────────────┘
```

## 3. 组件设计

### 3.1 Project Intelligence Console

职责：

- 汇总项目状态。
- 呈现 architecture / evidence / context / runtime / patch preview。
- 展示 accepted、needs_review、blocked。
- 提供下一步操作建议。

边界：

- 只消费后端 public payload。
- 不在前端计算事实。
- 不隐藏 unresolved / blocker。

### 3.2 Artifact Contract & Validator

职责：

- 统一 artifact envelope。
- 校验 artifact schema。
- 校验 evidence_refs 和 source_artifact_refs 可解析。
- 区分 row artifacts 与 summary artifacts。

建议 envelope：

```json
{
  "schema_version": "v2.18+",
  "artifact_type": "string",
  "workspace_id": "string",
  "codebase_id": "string",
  "snapshot_id": "string",
  "created_at": "string",
  "source_artifact_refs": [],
  "evidence_refs": [],
  "warnings": [],
  "needs_review": []
}
```

### 3.3 MCP Tool Catalog & Workflow Guide

职责：

- 生成工具目录。
- 根据用户目标推荐调用链。
- 说明工具前置条件、输出、失败原因、next actions。

示例目标：

```text
project_overview
architecture_review
coding_task_preparation
patch_preview
runtime_validation
quality_governance
```

### 3.4 Incremental Build Engine

职责：

- 读取 snapshot diff。
- 判断 artifact 是否复用、刷新、失效。
- 记录 scan budget。
- 生成 build impact report。

输出：

```text
reused_artifacts
refreshed_artifacts
invalidated_artifacts
skipped_files
scan_warnings
```

### 3.5 Provider Plugin System

职责：

- 定义 provider adapter SDK。
- 保留 Python AST mandatory baseline。
- tree-sitter、Jedi、LSP 作为 optional providers。
- 统一 health/config/execution/error contract。

规则：

- health-known 不等于 execution-ready。
- optional unavailable 不得 fake accepted。
- provider 输出必须带 confidence、extractor、evidence。

### 3.6 Governance Feedback Loop

职责：

- 对 finding、claim、context item、evidence、tool guidance 提反馈。
- 生成 correction rule。
- 审核 approved / rejected / revoked。
- read-time overlay 生效。

规则：

- 不改写 source artifacts。
- revoke 后 overlay 失效。
- 所有规则有 target resolver。

### 3.7 Production Readiness & CI

职责：

- 测试分层。
- public contract guard。
- warning budget。
- security gate。
- artifact validation gate。

测试层级：

```text
unit
contract
artifact
frontend build
real repo e2e
slow/nightly
```

## 4. 数据流

```text
repo change
  -> snapshot diff
  -> incremental build plan
  -> selected builders
  -> validated artifacts
  -> public contract
  -> console / MCP / CLI
  -> governance feedback
  -> read-time overlay
```

## 5. 存储布局建议

```text
workspace/assets/codebase/{codebase_id}/
  platform/
    console/
    contracts/
    tool_catalog/
    incremental/
    providers/
    governance/
    ci/
```

## 6. 架构门禁

- 不继续扩大 legacy `data_service.py` / `service.py`。
- HTTP/MCP/CLI 层保持薄 wrapper。
- Console 不作为事实源。
- Artifact validator 不自动修正事实。
- Provider unavailable 不算 accepted。
- Governance overlay 不改写原始 artifact。
- Incremental build 不静默跳过失败。

# V2.18-V2.24 Phase 84-90 详细实现包

## 1. 文档目标

本文件把 V2.18-V2.24 的高层路线图拆成可执行的 Phase 84-90 实现包。每个 phase 仍需在正式开发前生成单独的 development plan、acceptance plan、pre-implementation audit 和 acceptance audit。

## 2. Phase 84 / V2.18 Product Console & Report UX

### 输入

- Existing V2.0-V2.17 artifacts。
- Architecture reports。
- Context packs。
- Runtime profile / patch preview artifacts。

### 输出

```text
platform/console/platform_console.json
platform/console/views/platform_console.html
```

### 实现任务

1. Console payload builder。
2. Panel registry。
3. HTML renderer。
4. Status summarizer。
5. Next-action selector。

### 自动验收

- HTML parser pass。
- No unpersisted fact check。
- Blocker visibility check。
- Public redaction check。

## 3. Phase 85 / V2.19 Artifact Schema & Public Contract

### 输入

- Current artifact roots。
- Existing public envelopes。
- Artifact refs。

### 输出

```text
platform/contracts/artifact_contract_registry.json
platform/contracts/validation_report.json
```

### 实现任务

1. Artifact family discovery。
2. Schema registry。
3. Validator runner。
4. Ref integrity checker。
5. HTTP/MCP/CLI parity checker。

### 自动验收

- Invalid schema fixture fails。
- Missing refs become unresolved。
- New artifact without schema_version rejected。

## 4. Phase 86 / V2.20 MCP Tool Discovery & Workflow Guide

### 输入

- `all_tool_specs()`。
- Tool descriptions。
- Existing next_actions。

### 输出

```text
platform/tool_catalog/mcp_tool_catalog.json
platform/tool_catalog/workflow_guides.json
```

### 实现任务

1. Registry scraper。
2. Tool group classifier。
3. Preconditions/output inference from schema。
4. Goal-based workflow guide builder。
5. Missing/deprecated tool guard。

### 自动验收

- Catalog count equals registry count。
- Goal `coding_task_preparation` returns stable chain。
- Missing tool fixture rejected。

## 5. Phase 87 / V2.21 Incremental Build & Large Repo Performance

### 输入

- Snapshot A/B。
- File manifest。
- Existing artifacts。

### 输出

```text
platform/incremental/incremental_build_plan.json
platform/incremental/cache_decisions.jsonl
platform/incremental/scan_profile.json
```

### 实现任务

1. Snapshot diff reader。
2. Artifact dependency registry。
3. Cache invalidation policy。
4. Build impact planner。
5. Scan budget reporter。

### 自动验收

- Changed file detected。
- Related artifact invalidated or full rebuild reason present。
- Unsafe reuse fails。

## 6. Phase 88 / V2.22 Provider Plugin System

### 输入

- Current provider registry。
- AST extractor。
- Optional provider availability。

### 输出

```text
platform/providers/provider_capabilities.json
platform/providers/provider_execution_contract.json
```

### 实现任务

1. Provider adapter base protocol。
2. Health/config/execution separation。
3. AST mandatory adapter。
4. Optional provider unavailable adapters。
5. Provider output validation。

### 自动验收

- AST ready。
- tree-sitter/Jedi/LSP unavailable if not configured。
- health-known without adapter returns unsupported。

## 7. Phase 89 / V2.23 Governance Feedback Loop

### 输入

- Findings。
- Claims。
- Evidence。
- Context items。
- Tool guidance items。

### 输出

```text
platform/governance/feedback.jsonl
platform/governance/rules.jsonl
platform/governance/overlay_report.json
```

### 实现任务

1. Target resolver。
2. Feedback persistence。
3. Rule builder。
4. Review state machine。
5. Read-time overlay applicator。
6. Revoke logic。

### 自动验收

- Missing target rejected。
- Approved rule appears in read output。
- Revoked rule removed。
- Source artifact hash unchanged。

## 8. Phase 90 / V2.24 Production Readiness & CI Hardening

### 输入

- Test suite。
- Contract checks。
- Artifact validators。
- Frontend build。
- Real repo E2E commands。

### 输出

```text
platform/ci/ci_readiness_report.json
platform/ci/release_readiness_report.md
```

### 实现任务

1. Test layer command registry。
2. Warning classifier。
3. Warning budget。
4. Public payload redaction gate。
5. Release readiness report。

### 自动验收

- Layered test commands recorded。
- Skipped not counted as passed。
- Redaction failure blocks readiness。
- Release report references command evidence。

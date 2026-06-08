# V2.16 Phase 76-82 详细实施包

## 1. 文件定位

本文件把 V2.16 PRD、目标架构、开发验收计划进一步细化为可进入实现的工程实施包。

它回答四个问题：

1. 每个 Phase 具体要新增哪些模块和 artifact。
2. 每个 Phase 的 HTTP/MCP/CLI 合同如何收敛。
3. 每个 Phase 用什么真实数据验收。
4. 每个 Phase 哪些情况必须停止，不能假验收。

注意：本文件仍然是实现前计划，不是实现完成证明。每个 Phase 真正开始前，仍需要生成当期 pre-implementation audit，并确认无 fatal / major finding。

## 2. 统一模块边界

V2.16 新能力建议放在 focused modules 中，避免继续扩大旧大文件。

建议模块：

```text
backend/data_service/code_assets/coding_agent_v2_16/
  __init__.py
  models.py
  persistence.py
  provider_registry.py
  provider_decisions.py
  semantic_orchestrator.py
  semantic_merge.py
  runtime_profiles.py
  runtime_runner.py
  workbench_v2.py
  large_project_abstraction.py
  patch_sandbox.py
  redaction.py
  parity.py

backend/app/api/v1/code_assets_coding_agent_v2_16.py
backend/data_service/mcp_coding_agent_v2_16_tools.py
backend/data_service/cli_coding_agent_v2_16.py
```

接口层必须保持薄封装：

- HTTP router 只做 request/response mapping。
- MCP tools 只做参数校验和 service 调用。
- CLI 只做命令解析和 JSON 输出。
- 核心业务逻辑必须在 `coding_agent_v2_16/` 下。

禁止：

- 把 V2.16 核心逻辑塞进 `backend/app/api/v1/data_service.py`。
- 把 V2.16 核心逻辑塞进 `backend/data_service/service.py`。
- 把 provider SDK、runtime 执行、patch sandbox 逻辑塞进 route handler。

## 3. 统一 Artifact 根目录

所有 V2.16 产物写入：

```text
workspace/assets/codebase/{codebase_id}/coding_agent/v2_16/
```

每个 artifact 必须包含：

- `schema_version = "v2.16"`
- `workspace_id`
- `codebase_id`
- `snapshot_id` 或明确说明不依赖 snapshot
- `artifact_refs`
- `evidence_refs` 或 `needs_review`
- `created_at`
- `source_phase`

public payload 不得输出：

- 本机绝对路径。
- API key / token / secret。
- raw traceback。
- raw provider body。
- 未脱敏 runtime log。

## 4. Phase 76：Provider Capability Registry

### 4.1 目标

让用户和 Agent 清楚知道每个 provider 的状态：

- 是否被系统识别。
- 是否已配置。
- 是否有 execution adapter。
- 是否当前可执行。
- 不可用原因是什么。

### 4.2 输入

- 现有 V2.11-V2.15 artifacts。
- 本地 provider 配置。
- 环境变量状态。
- 可选 provider 探测结果。
- 禁止读取或输出 secret 原文。

### 4.3 输出

```text
providers/capability_registry.json
providers/decisions/{decision_id}.json
```

### 4.4 实现动作

1. 定义 `ProviderCapability`、`ProviderDecisionRecord`、`ProviderError` model。
2. 实现 provider 探测器：
   - AST baseline provider。
   - optional semantic providers：tree-sitter、Jedi、LSP 先支持 unavailable / unsupported contract。
   - runtime provider：local profile runner。
   - patch provider：sandbox preview only。
3. 实现 registry builder。
4. 实现 decision record writer。
5. 实现 HTTP/MCP/CLI read contract。
6. 实现 redaction checker。

### 4.5 验收

必须通过：

- `data_service` 真实 repo 生成非空 provider registry。
- known / configured / execution_supported / available 字段可区分。
- known provider without adapter 返回 `PROVIDER_UNSUPPORTED`。
- missing credential 返回 `PROVIDER_MISSING_CREDENTIAL` 或 `provider_unavailable`。
- HTTP/MCP/CLI 输出 stable ids、counts、warnings、error code 一致。
- public payload 不泄露 secret、endpoint、raw provider body。

不得通过：

- health-known 被标记为 execution accepted。
- skipped optional provider 被标记为 accepted。
- unsupported provider 静默 fallback 到其他 provider。

## 5. Phase 77：Semantic Provider Orchestrator

### 5.1 目标

在不承诺 full static analysis 的前提下，增强 symbol/reference/import/test mapping 等语义事实，并保留 provider provenance。

### 5.2 输入

- V2.0 symbols / imports / evidence。
- V2.11 actionability artifacts。
- Phase 76 provider registry。
- snapshot files。

### 5.3 输出

```text
semantic/provider_facts/{provider}/{snapshot_id}.jsonl
semantic/merged_semantic_index.json
semantic/conflicts.jsonl
```

### 5.4 实现动作

1. 定义 `SemanticProviderFact` model。
2. 实现 AST provider adapter，作为 mandatory baseline。
3. 为 tree-sitter / Jedi / LSP 定义 adapter interface。
4. optional provider 未安装时输出 structured unavailable。
5. 实现 semantic fact merge policy。
6. 实现 conflict policy：
   - exact match 合并。
   - conflict 进入 `needs_review`。
   - weak fact 不得 accepted。
7. 将 merged facts 接入 actionability / workbench export。

### 5.5 验收

必须通过：

- AST baseline 在 `data_service` 上真实跑通。
- optional provider unavailable 不阻塞系统。
- 每条 fact 有 provider、extractor、confidence、evidence_refs。
- line range 抽样真实存在。
- conflict artifact 非空或明确 no conflict。

不得通过：

- import/reference 被写成 runtime call。
- 生成 full call graph、data flow、control flow、type inference claim。
- provider fact 没 evidence 但被 accepted。

## 6. Phase 78：Runtime Profile Manager

### 6.1 目标

把 V2.13 的 allowlist-only runtime evidence 升级为 profile-based runtime evidence，让运行行为可解释、可审批、可复现。

### 6.2 输入

- validation plan。
- safe patch plan。
- runtime profile templates。
- provider registry。

### 6.3 输出

```text
runtime_profiles/profiles.json
runtime_profiles/runs/{run_id}.json
runtime_profiles/logs/{run_id}.stdout.redacted.txt
runtime_profiles/logs/{run_id}.stderr.redacted.txt
```

### 6.4 实现动作

1. 定义 `RuntimeProfile`、`RuntimeProfileRun`、`RuntimeProfileError`。
2. 建立默认 profile：
   - `pytest_file`
   - `pytest_focused`
   - `python_compile`
   - `frontend_build_optional`
3. 实现参数校验。
4. 实现 command rendering。
5. 实现 default-deny runner。
6. 实现 timeout、exit code、stdout/stderr redaction。
7. 将 run result 关联 patch plan 和 static evidence。

### 6.5 验收

必须通过：

- non-profile command blocked。
- approved profile 在 `data_service` 真实运行。
- failed / timeout / blocked 分类正确。
- redacted log 落盘。
- HTTP/MCP/CLI 可读取 run result。

不得通过：

- 任意 shell 命令绕过 profile。
- timeout 被包装为 passed。
- log 泄露绝对路径、secret、raw traceback。
- runtime evidence 覆盖 static evidence。

## 7. Phase 79：Workbench v2

### 7.1 目标

把 V2.15 的静态报告升级为更像审查产品的 Workbench v2，让人类能直接理解项目状态、任务风险、provider 状态、runtime 结果和 blocker。

### 7.2 输入

- Phase 76 provider registry。
- Phase 77 semantic index。
- Phase 78 runtime runs。
- V2.11-V2.15 actionability / patch / incremental artifacts。
- V2.7-V2.10 architecture artifacts。

### 7.3 输出

```text
workbench_v2/payload.json
workbench_v2/report.html
workbench_v2/graph.mmd
workbench_v2/exports/{export_id}.json
```

### 7.4 实现动作

1. 定义 Workbench v2 view model。
2. 聚合 provider matrix、impact map、risk lanes、blocker board、runtime results。
3. 生成 HTML report。
4. 生成 Mermaid graph。
5. 生成 reviewer export 和 agent context export。
6. 实现 renderer integrity check。

### 7.5 验收

必须通过：

- HTML/Mermaid 只能来自 `payload.json`。
- 每个 visible node 能解析到 artifact ref。
- blocker 和 `needs_review` 可见。
- 页面包含 provider matrix、risk lanes、runtime、patch readiness。
- 人类不读 raw JSON 也能理解当前状态。

不得通过：

- renderer 生成新事实。
- 隐藏 major/fatal/blocker。
- HTML/Mermaid 泄露绝对路径或 secret。

## 8. Phase 80：Large-Project Abstraction Advisor

### 8.1 目标

增强对大型项目的泛化架构抽象能力，尤其是对 HarnessOS 这类复杂项目输出更精确的 accepted / needs_review / blocked 解释。

### 8.2 输入

- V2.6 scale profile。
- V2.7 document claims。
- V2.8 dashboard / graph / intent。
- V2.9 evidence / relationship / report。
- V2.10 pattern adapters。
- V2.11-V2.16 actionability artifacts。

### 8.3 输出

```text
large_project/abstraction_report.json
large_project/blockers.jsonl
large_project/taxonomy_mapping.json
```

### 8.4 实现动作

1. 建立 generic adapter catalog。
2. 建立 taxonomy mapping。
3. 聚合 document claim、code fact、pattern evidence。
4. 输出 accepted / needs_review / blocked。
5. 归一化 blocker：
   - missing entrypoint evidence
   - missing runtime profile
   - document-only claim
   - weak code evidence
   - unsupported language
   - unsupported framework pattern
6. 输出 next actions。

### 8.5 验收

必须通过：

- `data_service` E2E 通过。
- HarnessOS 或替代大项目 E2E 通过，或 structured blocker 被接受。
- accepted claim 有 code evidence。
- document-only claim 保持 document claim。
- blocker 包含 reason、missing evidence、next actions。

不得通过：

- HarnessOS-only hardcoding。
- document claim 伪装成 code fact。
- blocker 只有“无法识别”。

## 9. Phase 81：Human-Gated Patch Sandbox

### 9.1 目标

在不自动改代码的前提下，基于 safe patch plan 生成 patch preview、diff、rollback 和 validation profile，让用户先审查再决定是否批准 apply。

### 9.2 输入

- V2.12 safe patch plan。
- V2.13/V2.78 runtime validation plan。
- task plan。
- impact analysis。

### 9.3 输出

```text
patch_sandbox/previews/{preview_id}.json
patch_sandbox/diffs/{preview_id}.diff
patch_sandbox/rollback/{preview_id}.json
patch_sandbox/approvals/{approval_id}.json
```

### 9.4 实现动作

1. 定义 `PatchSandboxPreview`、`PatchSandboxDiff`、`RollbackPlan`、`PatchApproval`。
2. 从 safe patch plan 生成 dry-run preview。
3. 生成 unified diff artifact。
4. 生成 rollback artifact。
5. 关联 validation profiles。
6. 实现 approval state machine。
7. 默认阻断 apply。

### 9.5 验收

必须通过：

- preview 不修改 source repo。
- diff artifact 可读。
- rollback 覆盖 previewed files。
- validation profiles 与 preview 关联。
- apply without approval blocked。

不得通过：

- dry-run preview 发生源码变更。
- 未审批 apply。
- 默认 git commit / push / reset / restore。

## 10. Phase 82：最终闭环验收

### 10.1 目标

用真实数据证明 V2.16 所有 in-scope 能力已实现或被明确归类为 structured blocker / provider_unavailable / out_of_scope。

### 10.2 输入

- Phase 76-81 artifacts。
- Phase 76-81 acceptance audit reports。
- real repo E2E results。
- coverage matrix。
- public contract parity results。

### 10.3 输出

```text
V2_16_PHASE_82_CLOSURE_AUDIT_REPORT.md
V2_16_FULL_COVERAGE_MATRIX.md
V2_16_REAL_REPO_E2E_ACCEPTANCE_MATRIX.md
```

### 10.4 验收

必须通过：

- focused tests 全部通过。
- `data_service` E2E 通过。
- HarnessOS 或替代大项目 E2E 通过或 structured blocker accepted。
- HTTP/MCP/CLI parity 通过。
- public redaction 通过。
- artifact disk inspection 通过。
- no open fatal / major finding。
- in-scope coverage row 无 pending。

不得通过：

- 任何 accepted row 没有真实证据。
- planning docs 被当成 implementation closure。
- mock-only 被当成真实 E2E。
- blocker 被隐藏。

## 11. 每个 Phase 的最小测试清单

每个 Phase 至少要有：

```text
backend/tests/test_v2_16_phase_{phase}_*.py
backend/tests/test_v2_16_public_contract_parity.py
backend/tests/test_v2_16_redaction.py
backend/tests/test_v2_16_artifact_integrity.py
```

Phase 81 额外需要：

```text
backend/tests/test_v2_16_patch_sandbox_no_source_mutation.py
```

Phase 82 额外需要：

```text
backend/tests/test_v2_16_closure_matrix.py
```

## 12. 实现前审计结论

本实施包足以指导 Phase 76-82 的代码实现规划，但真正进入某个 Phase 前仍必须生成当期 pre-implementation audit，确认：

- 输入 artifact 可读。
- 真实 repo 路径可用。
- 目标 provider 决策明确。
- 无 fatal / major 规格偏差。
- 高风险动作已标记为人工审批。

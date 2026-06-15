# V2.23 Phase 89 Governance Feedback Loop Development Plan

## 1. 阶段目标

Phase 89 目标是补齐平台产品化层的治理反馈闭环：

```text
feedback -> rule -> review -> read-time overlay -> revoke
```

本阶段治理对象限定为 V2.18-V2.22 平台 artifacts，不改写源 artifact，不替代既有 V2.1 Code Quality Governance。

## 2. 输入

- Product Console panels。
- Artifact contract rows。
- MCP tool catalog entries / workflow guide steps。
- Incremental build cache decisions。
- Provider capabilities。

## 3. 输出

```text
platform/governance/feedback.jsonl
platform/governance/rules.jsonl
platform/governance/overlay_report.json
```

## 4. 实现任务

1. 新增 `backend/data_service/code_assets/platform/governance.py`。
2. 新增 platform target resolver：
   - `platform_panel`
   - `artifact_contract`
   - `tool_guidance`
   - `incremental_decision`
   - `provider_capability`
3. 反馈持久化。
4. 规则生成。
5. 审核状态机：`draft | approved | rejected | revoked`。
6. read-time overlay report。
7. source artifact hash before/after 不变证明。
8. HTTP/MCP/CLI 三端接口。

## 5. Public Contract

HTTP:

```text
POST /api/workspaces/{workspace_id}/codebases/{codebase_id}/platform/governance/feedback
POST /api/workspaces/{workspace_id}/codebases/{codebase_id}/platform/governance/rules/build
POST /api/workspaces/{workspace_id}/codebases/{codebase_id}/platform/governance/rules/{rule_id}/review
GET  /api/workspaces/{workspace_id}/codebases/{codebase_id}/platform/governance/overlay
```

MCP:

```text
knowledge_code_platform_governance_feedback
knowledge_code_platform_governance_rules_build
knowledge_code_platform_governance_rule_review
knowledge_code_platform_governance_overlay
```

CLI:

```text
knowledge code platform governance-feedback
knowledge code platform governance-rules-build
knowledge code platform governance-rule-review
knowledge code platform governance-overlay
```

## 6. Non-goals

- 不自动改写 Console / Tool Catalog / Provider / Incremental artifacts。
- 不自动提交文档或代码修复。
- 不替代 V2.1 code quality governance。
- 不接受不存在 target 的 feedback。

## 7. 架构边界

- 核心逻辑在 `code_assets/platform/governance.py`。
- HTTP/MCP/CLI 只做薄封装。
- read-time overlay 只输出 `applied_rules` 和 `overlay_report`。
- 原始 artifact hash 必须保持不变。

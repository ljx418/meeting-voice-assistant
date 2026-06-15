# V2.30 Phase 96 开发计划：Report、Context、Governance 与 Closure

## 1. 阶段目标

Phase 96 是 V2.25-V2.30 的用户出口和闭环阶段，基于 Phase 91-95 产物生成：

- 人类可读 HTML 架构意图报告。
- Mermaid 关键关系/差异图。
- Architecture Context Pack extension。
- Human confirmation / revoke governance overlay。
- Closure audit 与 coverage matrix 更新。

本阶段不重新抽取 source，不重写 Phase 91-95 原始 artifact，不做运行时调用图、data flow、control flow 或 type inference。

## 2. 新增模块

```text
backend/data_service/code_assets/architecture_intent/report.py
backend/data_service/code_assets/architecture_intent/context_pack.py
backend/data_service/code_assets/architecture_intent/governance.py
```

## 3. 新增 artifact

```text
workspace/assets/codebase/{codebase_id}/architecture/intent/report/
  architecture_intent_report.json
  architecture_intent_report.html
  architecture_intent_diff.mmd

workspace/assets/codebase/{codebase_id}/architecture/intent/context/
  architecture_context_pack_v4.json
  architecture_context_pack_v4.md

workspace/assets/codebase/{codebase_id}/architecture/intent/governance/
  confirmed_facts.jsonl
  governance_events.jsonl
  governance_summary.json
```

## 4. 报告区块

HTML 报告必须包含：

- Target Architecture from Documents。
- Current Architecture from Code Facts。
- Inferred Intent Candidates。
- Human Confirmed Architecture。
- Diagram-to-Code Verification Board。
- Diff / Drift / Missing Evidence。
- Review Queue。
- Recommended Next Actions。

## 5. Context Pack 模式

支持：

- `project_brief`
- `task_context`
- `architecture_review`

每条 recommendation 必须有 evidence refs 或 needs_review。

## 6. Governance 行为

支持：

- confirm target。
- revoke confirmation。
- read-time overlay。

确认和撤销不得修改：

- Phase 91 source model。
- Phase 92 claims。
- Phase 93 proof graph。
- Phase 94 intent。
- Phase 95 verification。

## 7. 公共接口策略

本阶段优先完成 artifact/readback/test closure。公共 HTTP/MCP/CLI 若进入实现，必须使用 focused router/tool/CLI 模块，不得修改 legacy 大文件。

若 Phase 96 closure 未完成公共接口实现，coverage matrix 必须将 public contract 标记为 `not_implemented` 或 `conditionally_accepted`，不得虚假标记 accepted。

## 8. 出门条件

- HTML 非 raw JSON，包含表格、图和解释。
- Mermaid 节点全部来自 persisted report JSON。
- Context Pack recommendations 有 evidence 或 needs_review。
- confirm/revoke 不改原始 artifact hash。
- data_service 与 HarnessOS 真实 E2E 通过。
- Full coverage matrix 无未解释的 planned 行。

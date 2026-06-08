# V2.16 Phase 80 开发计划：Large-Project Abstraction Advisor

## 1. 阶段定位

Phase 80 目标是让系统对大型或复杂项目给出更可读的架构抽象建议，同时保持泛用性。它不针对 HarnessOS 写专用逻辑，而是基于 generic pattern adapter catalog 输出 accepted / needs_review / blocked 结果。

## 2. In Scope

- 生成大型项目抽象 advisor artifact。
- 输出 generic pattern adapter catalog。
- 输出 architecture role / layer / boundary hints。
- 输出 precise blockers：缺少什么证据、为什么无法 accepted、下一步补什么。
- 使用 data_service 和大项目式 fixture/真实仓进行验收。

## 3. Out of Scope

- HarnessOS-only hardcoding。
- 从代码完整恢复设计意图。
- runtime topology、full call graph、data flow、type inference。

## 4. Artifact

```text
workspace/assets/codebase/{codebase_id}/coding_agent/v2_16/large_project_advisor/
  abstraction_advisor.json
  pattern_adapters.json
  blockers.jsonl
```

## 5. 出门条件

- advisor artifact 落盘。
- pattern adapters 非空。
- accepted item 必须有 code evidence。
- blocker 必须有 reason、missing evidence、next actions。
- artifact 不包含项目专用硬编码判断。

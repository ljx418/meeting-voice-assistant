# V2.29 Phase 95 预实施审计：Diagram-to-Code Verification

审计日期：2026-06-10
阶段：V2.29 / Phase 95
结论：通过，可进入实现

## 1. 依赖检查

已完成并验收：

- Phase 91 Architecture Source Model：accepted。
- Phase 92 Diagram-to-Claim Parser：accepted。
- Phase 93 Code Proof Graph：accepted。
- Phase 94 Intent Inference Engine：accepted。

Phase 95 仅消费上述 artifact，不重写原始 source model、claims、proof graph 或 intent inference。

## 2. PRD 对齐

Phase 95 对应 V2.25-V2.30 PRD 中的 Diagram-to-Code Verification：

- 将文档/图声明对齐到代码、配置、测试、runtime descriptor 证据。
- 输出 matched / weak / missing / conflict / stale / undocumented。
- 不做完整静态分析。
- 不把图当成代码事实。

结论：无重大 PRD 偏移。

## 3. 架构边界审计

允许新增 focused module：

```text
backend/data_service/code_assets/architecture_intent/diagram_verification.py
```

禁止：

- 修改 `backend/app/api/v1/data_service.py`。
- 修改 `backend/data_service/service.py`。
- 生成 runtime call graph。
- 生成 data flow / control flow / type inference。
- 让 token overlap only 进入 accepted。

结论：无 fatal / major 架构风险。

## 4. 验收门槛闭环

必须执行：

- focused tests。
- V2.18-V2.24 + Phase 91-95 回归子集。
- data_service + HarnessOS 真实 E2E。
- accepted hard gate 抽样。
- redaction scan。
- false-green review。

## 5. 风险与处理

| 风险 | 级别 | 处理 |
| --- | --- | --- |
| token overlap 被误判为代码落地 | major | 写入自动测试，token-only 永远不能 accepted。 |
| HarnessOS accepted 不足 | major | 允许 structured blocker，但不能伪装 accepted。 |
| undocumented code facts 被忽略 | major | 验收强制 `undocumented_code_fact_count > 0`。 |
| target architecture 被当 current code | major | verification 输出必须保留 document/source_kind 与 code evidence 分离。 |

## 6. 审计结论

Phase 95 可进入实现。当前无 open fatal / major finding。

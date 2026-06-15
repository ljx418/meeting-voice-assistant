# V2.37 Milestones and Exit Gates

## M0：文档开发完成

出门条件：

- PRD、目标架构、开发验收计划、artifact schema、E2E matrix、coverage matrix、gap、drawio、audit 均存在。
- 文档无 fatal/major 不一致。
- drawio 可打开且非空。

## M1：Phase 103 完成

出门条件：

- 三个真实项目 document authority registry 非空。
- stale/historical/current 分类正确。
- 无绝对路径泄露。

## M2：Phase 104 完成

出门条件：

- claims 和 claim relations 非空。
- drawio node/edge 有 cell evidence。
- non-goals/forbidden claims 被抽取。

## M3：Phase 105 完成

出门条件：

- current implementation model 完成。
- V2.0-V2.36 artifacts hash 不被静默改写。
- no-surface 项目以 blocker 降级。

## M4：Phase 106 完成

出门条件：

- verification matrix 完成。
- supported row 均有双边 evidence。
- HarnessOS 至少 10 条 claim 分类。

## M5：Phase 107 完成

出门条件：

- HTML 原位渲染图。
- Mermaid/SVG 节点来自 persisted model。
- Agent brief 保留 evidence floor。

## M6：Phase 108 Closure

出门条件：

- data_service/HarnessOS/codexPat E2E 通过。
- 全量 backend tests 通过。
- 无 open fatal/major。
- Coverage matrix accepted rows 全部有证据。

## 总体出门条件

- 不声称完整设计意图恢复。
- 不声称 full call graph。
- 不出现 HarnessOS-only hardcode。
- 不改写目标项目代码或文档。
- 不隐藏 unsupported/needs_review/contradicted。

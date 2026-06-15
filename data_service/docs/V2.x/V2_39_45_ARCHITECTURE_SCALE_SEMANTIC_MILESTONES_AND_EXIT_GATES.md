# V2.39-V2.45 项目里程碑与出门条件

## 当前 closure 状态

V2.39-V2.45 的 M0-M7 已按阶段完成并验收。本文档仍保留原出门条件，作为后续回归和变更验收时的审计门槛；当前 acceptance 状态以各阶段 acceptance audit、full coverage matrix 和 closure audit 为准。

当前可声明：

```text
V2.39-V2.45 scoped implementation accepted.
```

不可声明：

```text
full call graph accepted
data/control flow accepted
production runtime topology accepted
type inference accepted
complete human design intent recovery accepted
```

## M0：文档基线

出门条件：

- PRD、目标架构、开发验收计划、Gap、drawio 已落盘。
- 文档审计无 fatal / major。
- 阶段开始前明确 V2.39-V2.45 是后续实现目标，不是已完成能力；closure 后必须由 acceptance audit 和 coverage matrix 将对应行更新为 accepted。

## M1：大型项目性能基线

出门条件：

- scale profile 生成。
- scan budget report 生成。
- shard + paginated readback 可用。
- timeout / oversized / generated skip 有 structured blocker。

## M2：多语言 Provider 基线

出门条件：

- Python AST mandatory provider 通过。
- TS/JS fixture 通过基础抽取。
- tree-sitter/LSP 未配置返回 provider_unavailable。
- provider error contract 稳定。

## M3：Workflow / Runtime Candidate 基线

出门条件：

- workflow manifest、runtime adapter、agent registry、CLI/TUI/console entrypoint 至少完成 attempt。
- 成功或 blocker 都有 evidence。
- 不声称 production runtime topology。

## M4：Relationship Chain v3

出门条件：

- data_service 至少 10 条 accepted chain。
- HarnessOS 输出 accepted chain 或 structured blocker。
- forbidden edge type scan 通过。
- Phase 119 acceptance audit 落盘。

## M5：drawio / 文档语义增强

出门条件：

- drawio page/lane/group/edge/gate 可抽取。
- Markdown acceptance/non-goal/stop condition 可抽取。
- document claim 与 code fact 分离。
- Phase 120 acceptance audit 落盘。

## M6：Token / Cache 优化闭环

出门条件：

- Context Pack 输出 token_estimate、cache_hit_ratio、omitted_items。
- 小 budget 下不保留无 evidence recommendation。
- 重复任务能复用缓存或解释无法复用原因。
- Phase 121 acceptance audit 落盘。

## M7：Profile / Taxonomy 与回归矩阵闭环

出门条件：

- profile registry 可读写。
- data_service、HarnessOS、codexPat regression matrix 生成。
- no-hardcode audit 通过。
- PRD coverage matrix accepted row 全部有真实证据。
- Phase 122 closure audit 落盘。

## 总出门条件

- 所有 focused tests 通过。
- public surface guard 通过。
- HTTP/MCP/CLI parity 通过。
- public payload 无绝对路径、secret、raw traceback。
- 无 open fatal / major finding。

当前 closure audit 已记录以上总出门条件通过；后续变更不得只依赖本文件声明通过，必须重新绑定测试命令、真实项目结果、artifact path 和审计报告。

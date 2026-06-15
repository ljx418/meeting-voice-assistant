# V2.39-V2.45 Real Repo E2E Acceptance Matrix

## 1. 目标

V2.39-V2.45 必须使用真实项目验收，不能只用 mock fixture。真实项目包括：

```text
/Users/Zhuanz/Desktop/workspace/data_service
/Users/Zhuanz/Desktop/workspace/harnessOS
/Users/Zhuanz/Desktop/workspace/codexPat
```

如果路径不存在或环境不可用，只能记录 structured unavailable，不能标记 accepted。

## 2. data_service 验收矩阵

| 阶段 | 最低验收 | 不可接受结果 |
| --- | --- | --- |
| V2.39 | 生成 scale profile、budget report、shard readback | 超预算无 blocker |
| V2.40 | Python AST provider 通过，TS/JS fixture 不影响主流程 | provider failed 仍 accepted |
| V2.41 | HTTP/MCP/CLI/console entrypoint candidate 可识别 | 候选误写成 runtime topology |
| V2.42 | 至少 10 条 accepted relationship chain | runtime_call accepted |
| V2.43 | docs/drawio/Markdown claim semantics 可抽取 | drawio claim 变 code fact |
| V2.44 | task context 输出 token/cache/omitted 指标 | 小预算保留无证据建议 |
| V2.45 | profile/taxonomy/regression matrix 生成 | 通用逻辑硬编码项目路径 |

## 3. HarnessOS 验收矩阵

| 阶段 | 最低验收 | 不可接受结果 |
| --- | --- | --- |
| V2.39 | 大项目 scale profile 或 structured unavailable | 扫描失败但标 ready |
| V2.40 | 语言 provider attempt，有 accepted facts 或 provider/blocker 状态 | 只因语言未知就全局失败 |
| V2.41 | workflow/runtime/agent/CLI/TUI extractor attempt | HarnessOS-only hardcode |
| V2.42 | accepted chain 或 structured blocker | blocker 被隐藏 |
| V2.43 | docs/design drawio/Markdown semantic claims 可抽取 | docs 声明和 code fact 混淆 |
| V2.44 | Agent context pack 说明 reading order 和 omitted_items | token 裁剪删除 evidence 后保留建议 |
| V2.45 | HarnessOS profile 存在且通用 extractor 无硬编码 | profile 规则写进通用模块 |

## 4. codexPat 验收矩阵

| 阶段 | 最低验收 | 不可接受结果 |
| --- | --- | --- |
| V2.39 | scale profile 或 structured unavailable | 小项目路径不可用却 accepted |
| V2.40 | 语言 provider attempt | provider unavailable 被 accepted |
| V2.41 | app/package/CLI/desktop candidates attempt | 无 public surface 时硬失败 |
| V2.42 | relationship chain 或 blocker | 空链路标 accepted |
| V2.43 | 文档语义抽取 attempt | 没文档仍标完成 |
| V2.44 | context pack 低预算策略可见 | omitted_items 缺原因 |
| V2.45 | regression matrix 记录项目状态 | 未运行却写 pass |

## 5. 共享 E2E 门槛

- artifact 必须落盘。
- artifact 必须 readback。
- public payload 不得泄露绝对路径。
- HTTP/MCP/CLI parity 必须覆盖 success 和 error。
- 每个 accepted row 必须有 test command、artifact path、真实项目结果。

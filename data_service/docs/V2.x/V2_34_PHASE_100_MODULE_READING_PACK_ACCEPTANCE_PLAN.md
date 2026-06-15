# V2.34 Phase 100 验收计划：Module Reading Pack & Token Ledger

阶段：V2.34 / Phase 100
目标：验证阅读包能减少 Coding Agent 阅读量，并且不会因 token 裁剪丢失证据。

## 1. 自动化验收

新增测试：

```text
backend/tests/test_v2_34_module_reading_pack.py
```

覆盖：

- JSON reading pack build/read。
- Markdown reading pack read。
- token ledger artifact read。
- HTTP/MCP/CLI smoke。
- small token budget behavior。
- no evidence-less high confidence recommendation。
- no absolute path leak。

## 2. data_service 真实任务

使用 5 个真实任务：

1. 新增 MCP tool 并同步 HTTP/CLI。
2. 修改 codebase snapshot。
3. 新增 architecture report 字段。
4. 修改 provider adapter。
5. 调整 quality governance。

每个任务必须：

- `required_reads` 非空。
- `token_ledger.estimated_tokens <= max_tokens` 或 blocker。
- `omitted_items` 有 reason。
- 比 naive all-related refs 更小。

## 3. HarnessOS 真实任务

使用 3 个真实任务：

1. 修改 workflow dispatch。
2. 新增 station/agent descriptor。
3. 审查 mission TUI entrypoint。

允许 blocker，但必须输出 token ledger 和 omitted reason。

## 4. False-Green Rejection

以下情况不得通过：

- Markdown 中出现 JSON artifact 不存在的新事实。
- 保留 recommendation 但删除 evidence 且未降级 needs_review。
- omitted_items 缺 reason。
- token ledger 不包含 included/omitted/evidence floor。
- public payload 泄露绝对路径。

## 5. 出门条件

- Focused tests 通过。
- data_service / HarnessOS 真实 E2E 通过。
- PRD/spec/false-green review 无 fatal/major。
- Phase 100 acceptance audit report 落盘。

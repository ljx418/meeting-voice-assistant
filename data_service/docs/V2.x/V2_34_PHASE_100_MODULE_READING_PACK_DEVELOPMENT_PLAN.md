# V2.34 Phase 100 开发计划：Module Reading Pack & Token Ledger

阶段：V2.34 / Phase 100
前置阶段：Phase 97、98、99 accepted
目标：为 Coding Agent 生成任务级最小阅读包，明确 required/optional/skip reads、reuse patterns、recommended next steps 和 token ledger。

## 1. 阶段目标

输入 task 或 `task_id`，输出：

- required_reads
- optional_reads
- skip_reads
- reuse_patterns
- recommended_next_steps
- token_ledger
- omitted_items
- Markdown 阅读包

Phase 100 不做：

- Agent handoff contract。
- HTML/Mermaid 最终报告。
- 自动修改代码。
- 自动运行测试。

## 2. 输入

```text
task_queries/{task_id}.json
relationships.jsonl / relationship_graph.json
impacts/{task_id}.json
test_selection/{task_id}.json
```

若 Phase 99 artifacts 缺失，允许自动构建 impact/test selection；若上游必需 artifacts 缺失，必须 structured blocker。

## 3. 输出

```text
coding_agent/task_navigation/reading_packs/{pack_id}.json
coding_agent/task_navigation/reading_packs/{pack_id}.md
coding_agent/task_navigation/token_ledgers/{pack_id}.json
```

## 4. 实现设计

新增 focused modules：

```text
backend/data_service/code_assets/coding_agent_navigation/reading_pack.py
backend/data_service/code_assets/coding_agent_navigation/reading_pack_persistence.py
```

最小挂载：

- HTTP：`/coding-agent/reading-pack`
- MCP：`knowledge_code_module_reading_pack`
- CLI：`knowledge code coding-agent reading-pack`

## 5. Token 策略

默认估算：

```text
estimated_tokens = max(1, ceil(char_count / 4))
```

裁剪规则：

1. 优先保留 accepted evidence / high priority item。
2. 合并重复 path/ref。
3. 超预算时移动到 omitted_items。
4. 如果 evidence 被裁剪，对应 recommendation 必须降级为 needs_review 或 omitted。
5. 每个 omitted item 必须有 reason。

## 6. 验收门槛

- data_service 5 个真实任务均生成 reading pack。
- HarnessOS 3 个真实任务生成 reading pack 或 structured blocker。
- `estimated_tokens <= max_tokens`，除非 `TOKEN_BUDGET_TOO_SMALL` blocker。
- `omitted_items` 每项有 reason。
- recommended_next_steps 每项有 evidence_refs 或 needs_review。
- Markdown 与 JSON 主要字段一致。

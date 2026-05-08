# 低信号 Source 观测阶段报告

日期：2026-04-30

## 结论

本轮完成 distill 低信号 source 观测第一版。系统现在不会盲目把弱标题或低密度聊天强行补成结论，而是把每个 source 是否 `zero_unit`、为什么 zero-unit、是否已被 title fallback 保守覆盖写入 source profile、manifest 和 summary。

追加进展：基于真实知识库的 low-signal reasons，本轮已补一组保守标题规则，覆盖退休资金、管培生案例、端午注意事项、云南菜评价、车企相关、智能卡片专利、creample 术语、香农极限应用等标题型 source。真实知识库临时 workspace 验证中，`zero_unit_count` 已从 8 降到 0，且 `title_derived_conclusion_count = 0`。

继续抽查进展：LLMWiki topic grouping 已对齐同一批低信号标题 anchor。真实知识库临时 workspace 复跑后，topic 页收缩为 `退休资金 / 管培生 / 端午节 / 云南菜 / 车企 / 智能卡片 / 香农极限 / creample` 等核心主题；原始长标题仍保留在 source 页，便于追溯。

## 新增能力

- `distill/sources/*.json.profile.zero_unit`
- `distill/sources/*.json.profile.low_signal`
- `distill/sources/*.json.profile_debug.low_signal`
- `distill/manifest.json.quality.zero_unit_count`
- `distill/manifest.json.quality.zero_unit_sources`
- `distill/manifest.json.quality.low_signal_reason_counts`
- `distill/manifest.json.quality.title_fallback_source_counts`
- `summary.json.quality.distill` 同步以上统计
- `/knowledge` Distill Quality 面板展示 Zero Unit、Low Signal Reasons、Title Fallback 覆盖和 Zero Unit Sources
- `/knowledge` Source 级蒸馏详情展示当前 source 的 low-signal reasons 与 title fallback 类型
- LLMWiki topic anchor 同步覆盖上述低信号标题，避免 topic 页继续生成 `岁停止工作确保退休资金充足`、`生成两份云南菜评价`、`跨设备智能卡片交互系统专利` 这类长标题页

## 低信号原因

当前诊断会记录以下原因：

- `no_entity_candidates`
- `no_theme_labels`
- `title_only_without_semantic_fallback`
- `no_safe_title_fallback`
- `no_content_sentences`
- `low_density_source`
- `title_only_conservatively_covered`

## 开发意义

- 对真实知识库剩余 `0 unit` source，可以先看原因分布，再决定补实体规则、主题规则还是 title fallback。
- title-only / low-content source 仍然不产出强 `conclusion`，避免为了降低 zero-unit 数量引入幻觉型结论。
- `/knowledge` 和 MCP 后续可以直接消费 `summary.json.quality.distill.zero_unit_sources` 做质量运营视图。
- 质量运营台已经可以直接查看 zero-unit source 列表并跳转到 source 详情，减少人工排查成本。

## 验收记录

自动化验证：

```bash
python3 -m pytest backend/tests/test_data_service.py backend/tests/test_data_service_api.py backend/tests/test_data_service_mcp.py -q
```

结果：

```text
74 passed, 4 skipped
```

LLMWiki topic anchor 验证：

```bash
python3 -m pytest backend/tests/test_llmwiki.py -q
```

结果：

```text
34 passed
```

真实知识库临时验收：

```text
workspace: /tmp/mva-low-signal-check-20260430b
source_count: 86
distilled_unit_count: 293
zero_unit_count: 0
title_derived_conclusion_count: 0
llmwiki: success
graphrag: indexed
graph compat: 93 entities / 83 themes / 140 relationships
```

补充复跑：

```text
workspace: /tmp/mva-continue-low-signal-20260430c
topic pages: 退休资金 / 管培生 / 端午节 / 云南菜 / 车企 / 智能卡片 / 香农极限 / creample
zero_unit_count: 0
title_fallback_source_count: 50
```

前端验证：

```bash
npx vite build
```

结果：通过。

说明：`npm run build` 当前在 Node 24.14.0 下停在 `vue-tsc` 兼容错误 `Search string not found: "/supportedTSExtensions = .*(?=;)/"`，未进入本轮代码编译；已用 `vite build` 验证模板与生产打包。

## 下一步

- 继续抽查新增 title fallback 的可读性
- 继续保证 `title_derived_conclusion_count = 0`
- 继续观察 GraphRAG top communities 中少量弱主题，例如 `ai学习`

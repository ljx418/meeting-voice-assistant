# Phase 2 阶段验收报告

验收日期：2026-04-29

## 结论

`Phase 2：distill 正式化中间层` 已完成阶段性验收。当前 `distill v1.1` 可以作为独立中间契约层阅读、调试和被下游引擎消费。GraphRAG owner 最终收口与 LLMWiki 页面标题自然度继续放入 Phase 3 / LLMWiki 质量提升。

## 验收命令与结果

自动化回归：

```bash
python3 -m pytest backend/tests/test_data_service.py backend/tests/test_data_service_api.py -q
```

结果：

- `53 passed in 21.32s`
- 仅出现既有 `urllib3` LibreSSL warning

真实知识库端到端：

```bash
cd backend
python3 -m data_service ingest \
  --workspace /tmp/data-service-phase2-acceptance-20260429 \
  /Users/Zhuanz/Desktop/workspace/知识库/row/deepseek_split
```

结果：

- 86 sources
- `llmwiki: success`
- `graphrag: indexed`
- 248 distilled units
- 85 entities
- 76 themes
- 131 relationships

## distill 契约检查

验收 workspace：

```text
/tmp/data-service-phase2-acceptance-20260429
```

已确认生成：

- `distill/schema.json`
- `distill/manifest.json`
- `distill/sources/`
- `distill/units/distilled_units.jsonl`

契约字段：

- `schema_version`: `1.1`
- source record: `source_id / path / authority / title / title_flags / source_weight / source_density_score / llm_enriched / tags / profile / profile_debug / unit_kind_counts / units`
- unit record: `unit_id / source_id / kind / authority / text / normalized_text / importance / confidence / source_weight / source_density_score / is_title_derived / is_llm_enriched / tags / entities / relations / provenance`

unit 类型分布：

- `topic_candidate`: 89
- `entity_candidate`: 90
- `question`: 29
- `fact_candidate`: 7
- `note`: 25
- `conclusion`: 6
- `risk`: 2

质量检查：

- `title_derived_conclusion_count`: 0
- `zero_unit_count`: 8 / 86；未形成大面积退化，保留为后续质量优化观察项

## 样例质量

已稳定收缩到核心实体：

- `小米SU7玻璃防晒性能解析 -> 小米SU7`
- `中国民营航天公司上市进展及股东情况 -> 中国民营航天公司`
- `美加墨世界杯小组赛时间 -> 美加墨世界杯`
- `已安装VSCode选项验证 -> VSCode`
- `TypeScript中的多态与复态解析 -> TypeScript`
- `鸿蒙手机Python自动化测试代码示例 -> Python / 鸿蒙手机`
- `超聚变公司股权结构及背景介绍 -> 超聚变公司`

以下噪音在 distilled units 中未出现：

- 裸 `SU7`
- `已安装VSCode选项验证`
- `中的多态与复态`
- `鸿蒙手机Python自动化测试代码示例`
- `背景介绍`

## 下游消费验证

GraphRAG 查询：

```bash
python3 -m data_service query VSCode \
  --workspace /tmp/data-service-phase2-acceptance-20260429 \
  --mode graphrag \
  --top-k 5
```

结果：

- 命中 `Entity: VSCode`
- 命中 `Theme: VSCode`
- 返回 supporting units
- payload source 为 `app.graphrag.bridge`

Hybrid 查询：

```bash
python3 -m data_service query VSCode \
  --workspace /tmp/data-service-phase2-acceptance-20260429 \
  --mode hybrid \
  --top-k 5
```

结果：

- GraphRAG 命中正常
- hybrid payload 结构稳定

LLMWiki 查询：

```bash
python3 -m data_service query conversation \
  --workspace /tmp/data-service-phase2-acceptance-20260429 \
  --mode llmwiki \
  --top-k 5
```

结果：

- LLMWiki 页面检索链路可用
- 仍存在 `conversation id` 标题残留；该问题属于后续 LLMWiki 质量提升，不阻塞 Phase 2 中间层验收

## 后续事项

- Phase 3 已于 2026-04-29 完成阶段性验收，详见 [PHASE-3-ACCEPTANCE-REPORT.md](./PHASE-3-ACCEPTANCE-REPORT.md)
- LLMWiki：继续提升 topic 聚合和 source/topic 标题自然度
- distill：继续观察 8 个 `0 unit` source，并在不误产强结论的前提下逐步提升低信号 source 覆盖率

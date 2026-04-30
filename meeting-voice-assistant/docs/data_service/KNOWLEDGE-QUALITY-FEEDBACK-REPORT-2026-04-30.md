# Knowledge 质量反馈入口阶段报告

日期：2026-04-30

## 结论

本轮完成 `/knowledge` 质量反馈与人工校正入口的第一版。它不是直接改写知识产物，而是把人工质量信号稳定记录到 workspace 内，供后续 topic 合并、标题修正、噪音实体屏蔽和 Agent 工具消费。

## 新增能力

- workspace 新增 `quality/feedback.jsonl`
- `summary.json` 的 `quality.manual_feedback` 新增反馈总数、action 分布、target type 分布、最新时间
- HTTP API 新增：
  - `POST /api/v1/knowledge/quality/feedback`
  - `POST /api/v1/knowledge/quality/feedback/list`
- `/knowledge` 新增“质量反馈与校正”面板
- 前端可从当前页面、GraphRAG 节点、distill source、当前查询快速带入反馈对象
- 支持 `needs_review / rename_suggest / merge_suggest / mark_noise / confirm_good / note`

## 设计边界

- 不修改 `row` 原始资料
- 不直接覆盖 LLMWiki 页面或 GraphRAG 图谱
- 反馈作为人工信号先进入 `quality/feedback.jsonl`
- 后续再由明确的校正任务消费这些反馈

## 自动化验收

```bash
python3 -m pytest backend/tests/test_data_service.py backend/tests/test_data_service_api.py -q
```

结果：

- `56 passed`

前端打包验证：

```bash
npx vite build
```

结果：

- Vite build passed
- `npm run build` 当前在 `vue-tsc` 启动阶段失败，原因是 Node 24 与当前 `vue-tsc` 的 TypeScript 扩展探测不兼容：`Search string not found: "/supportedTSExtensions = .*(?=;)/"`。该失败发生在项目代码检查前。

## 手工验收标准

打开 `/knowledge`：

- 刷新工作台后可以看到“质量反馈与校正”面板
- 点击 LLMWiki 页面后，反馈对象自动变为 `page + slug`
- 点击 GraphRAG 节点后，反馈对象自动变为 `entity + node.id`
- 点击 distill source 后，反馈对象自动变为 `source + source_id`
- 点击“当前查询”后，反馈对象自动变为 `query + 查询文本`
- 提交反馈后页面提示成功，最近反馈列表出现新记录
- 再刷新 summary 后，`summary.json.quality.manual_feedback.feedback_count` 增加

## 下一步

- 把 `rename_suggest / merge_suggest / mark_noise` 反馈接入可审核的校正规则
- 增加反馈导出或 MCP tool，让 Agent 能读取待处理质量队列
- 在 GraphRAG 和 LLMWiki 质量治理中消费人工反馈

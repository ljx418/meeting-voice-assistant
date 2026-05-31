# V1.8-RC Agent-Led PRD Smoke Plan

日期：2026-05-30

## 目标

使用真实数据跑通 Agent-led PRD MVP 能力路径。

## 完整路径

1. 用户输入任务。
2. Agent 生成 draft。
3. 用户确认授权。
4. Agent 创建 Notebook。
5. Agent 导入 Markdown / TXT / PDF / URL。
6. Agent build/index。
7. Agent 生成 Guide。
8. Agent 提问 Suggested Question。
9. Agent 验证引用问答。
10. Agent 解析 citation。
11. Agent 生成 Notes / Study Guide / Briefing Doc / FAQ。
12. Agent 导出 Markdown / JSON。
13. Agent 提问资料外问题并验证拒答。
14. Agent 生成最终验收报告。
15. 弱前端展示结果。

## 验收标准

- Agent workflow 完整跑通。
- 每一步有 step log。
- 每一步有 input/output summary。
- 失败时有 error_code 和 recovery suggestion。
- fixtures 脱敏。
- 不含本地绝对路径。
- 不含 API key。
- 不调用 `/api/v1/knowledge/*`。
- 不声明强前端体验 ready。
- 不声明 all-source-type ready。
- 不声明 all websites URL ready。
- 不声明 OCR ready。
- 不声明 Phase 2/3 ready。

## 必跑命令

```bash
npm run check
npm run smoke:v1.8-agent-prd
npm run smoke:v1.8-weak-frontend
```

## 完成声明上限

ResearchNotebook V1.8 Agent-led PRD MVP capability validation is smoke-ready for validated PDF / TXT / Markdown and limited URL sources on approved datasets.


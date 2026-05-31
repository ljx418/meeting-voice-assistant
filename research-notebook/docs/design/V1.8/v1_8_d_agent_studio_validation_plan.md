# V1.8-D Agent-Led Studio Output Validation Plan

日期：2026-05-30

## 目标

Agent 验证 Studio 四类轻量输出和导出合同。

## 范围

- Notes
- Study Guide
- Briefing Doc
- FAQ

## 开发内容

1. 生成 Studio artifacts。
2. 验证 artifact schema。
3. 验证 evidence_refs。
4. 验证 citation 可解析。
5. 导出 Markdown。
6. 导出 JSON。
7. 检查导出内容安全。

## 验收标准

- 四类 artifact 均生成成功。
- 每类输出有引用。
- FAQ 每条答案有 citation 或明确未覆盖。
- Markdown export 可打开。
- JSON export 包含 `artifact_id`、`artifact_type`、`sections`、`evidence_refs`、`schema_version`、`exported_at`。
- 导出不含 `/Users`、`file://`、cache path、artifact physical path、API key、stack trace。

## 必跑命令

```bash
npm run check
npm run smoke:v1.5-c-studio
npm run smoke:v1.8-agent-studio
```

## 风险

- 规格漂移：LOW-MEDIUM。
- 虚假验收：MEDIUM。schema pass 不等于质量 pass。


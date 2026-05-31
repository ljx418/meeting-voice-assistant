# V1.8-E Weak Frontend Shell Plan Audit

日期：2026-05-30

## 审计结论

`CONDITIONAL GO`

V1.8-E 可以进入实质开发，但必须保持“弱前端展示壳”定位。主 Notebook 三列体验不应塞入完整 Agent workflow editor；本阶段只生成和校验 Agent-led validation report 的可读展示壳。

## 前置验收

| 前置项 | 状态 | 说明 |
| --- | --- | --- |
| V1.8-B Agent Source Import | PASS_LIMITED | 来源导入 fixtures 可用 |
| V1.8-C Agent Guide / QA / Citation | PASS_LIMITED | Guide / QA / citation fixtures 可用 |
| V1.8-D Agent Studio | PASS_LIMITED | Studio / export fixtures 可用 |
| Main Notebook UX boundary | PASS | 主工作区不注入非 PRD Agent workflow controls |

## 实现策略

为了避免规格漂移，本阶段不实现完整产品级 workflow editor。实现方式为：

1. 新增 `scripts/v1_8_e_weak_frontend_smoke.mjs`。
2. 读取 V1.8-B/C/D 脱敏 fixtures。
3. 生成 `docs/design/V1.8/v1_8_e_weak_frontend_shell_report.html`。
4. HTML 展示 Agent plan、authorization、execution status、source import summary、Guide / QA / Studio validation result、skipped/error state、citation entry。
5. smoke 校验 HTML 关键内容和无敏感路径。

## 验收标准

- 展示 Agent 计划。
- 展示授权确认状态。
- 展示运行状态。
- 展示来源导入汇总。
- 展示 Guide / QA / Studio 验证结果。
- 展示 skipped / failed / degraded 状态说明。
- 展示 citation / evidence entry。
- 页面没有明显重叠风险的固定窄布局。
- 不出现 `/Users`、`file://`、cache path、artifact physical path、API key。
- 不声明普通用户 UX ready。

## 风险评估

| 风险 | 等级 | 是否阻塞 | 收敛措施 |
| --- | --- | --- | --- |
| 规格漂移 | MEDIUM | 否 | 明确这是 validation report shell，不是 workflow editor |
| 虚假验收 | MEDIUM | 否 | 壳展示成功不等于后端能力或人工内容质量通过 |
| UX 债务 | HIGH accepted | 不阻塞 V1.8 | 保留 V1.x Final Human UX Acceptance |

## 审计意见

可以实现 `npm run smoke:v1.8-weak-frontend`。

完成后必须执行：

```bash
npm run check
npm run smoke:v1.7-ux
npm run smoke:v1.8-weak-frontend
```

如果全部通过，V1.8-E 最多进入 `PASS_LIMITED`，下一阶段只能审计 V1.8-RC。

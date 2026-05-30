# ResearchNotebook V1.5-E ChromeCLI / Manual E2E Plan

日期：2026-05-27

## 阶段目标

像普通用户一样完整验证 V1.5 主路径。

## Entry Gate

- V1.5-A provider PASS。
- V1.5-B AI Guide PASS。
- V1.5-C AI Studio PASS。
- V1.5-D QA quality PASS。

## 验收路径

1. 启动 data_service。
2. 启动 ResearchNotebook。
3. 打开 Chrome。
4. 创建 Notebook。
5. 上传数字人 Markdown。
6. 上传数字人 PDF。
7. 等待解析。
8. 查看 AI Guide。
9. 点击 Suggested Question。
10. 查看引用问答。
11. 点击 citation。
12. 生成 Notes。
13. 生成 Study Guide。
14. 生成 Briefing Doc。
15. 生成 FAQ。
16. 点击 Studio citation。
17. 提问资料外问题。
18. 点击添加来源。
19. 归档 Notebook。

## 验收标准

- 页面非空白。
- 无 crash overlay。
- 无 blocking console error。
- Guide 非模板化。
- Chat 带 citation。
- Studio 输出带 citation。
- citation highlight 可见。
- 资料不足拒答正确。
- cleanup 成功。
- `npm run check` PASS。

## Artifacts

- 截图和日志只进入 `.smoke-artifacts/`。
- 提交报告只保存脱敏 summary。
- 不提交 API key、本地绝对路径、cache path。

## 风险评估

- 规格漂移风险：LOW。
- 虚假验收风险：MEDIUM，若仅依赖自动化断言而缺少人工质量判断。


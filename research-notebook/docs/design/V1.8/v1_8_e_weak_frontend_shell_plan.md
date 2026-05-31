# V1.8-E Weak Frontend Shell Plan

日期：2026-05-30

## 目标

弱前端只展示 Agent draft、运行状态、结果摘要和失败原因，不承担完整工作流编辑器职责。

## 开发内容

1. 展示 Agent task draft。
2. 展示授权确认入口。
3. 展示 execution status。
4. 展示 source import summary。
5. 展示 Guide / QA / Studio validation result。
6. 展示 skipped files。
7. 展示 error_code 和 recovery suggestion。
8. 提供 citation drawer 入口。

## 验收标准

- 用户能看到 Agent 计划。
- 用户能确认执行。
- 用户能看到运行状态。
- 用户能看到导入来源和 skipped files。
- 用户能看到 Guide / QA / Studio 验证结果。
- 用户能打开 citation drawer。
- 弱前端不出现明显重叠。
- 不把 disabled 能力展示成 ready。

## 必跑命令

```bash
npm run check
npm run smoke:v1.7-ux
npm run smoke:v1.8-weak-frontend
```

## 风险

- 规格漂移：MEDIUM。弱前端不应演变成完整 workflow designer。
- 虚假验收：MEDIUM。前端展示成功不代表后端真实成功。


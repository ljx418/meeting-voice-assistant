# ResearchNotebook V1.9 剩余开发及验收计划

日期：2026-05-31

## 当前结论

V1.9 剩余工作已从“宽泛 Research 质量补齐”收敛为一个明确阻塞点并完成修复：

- V1.9-A Research quality：`PASS_LIMITED`
- V1.9-B Conflict labeling：`PASS_LIMITED`
- V1.9-C Human UX acceptance package：`READY_FOR_HUMAN_ACCEPTANCE`
- V1.9-RC：`V1_9_READY_FOR_FINAL_HUMAN_ACCEPTANCE`

V1.9 当前自动化阶段已完成到人工验收入口。后续不得把自动化 smoke 写成人工内容质量 PASS。

## 已执行的剩余开发

### V1.9-R1 Conflict Labeling Contract Fix

修复目标：

- Research report 在真实冲突样本下生成 structured `conflicts`。
- 不在前端伪造冲突。
- 不使用互联网搜索或 provider 常识。
- 每个 conflict position 必须携带 evidence refs。

执行结果：

- 后端 Research fallback 已能从 supported conclusions 中识别当前 Alpha 商业化状态冲突。
- focused backend tests 通过。
- `npm run smoke:v1.9-conflict-labeling` 通过。

状态：`PASS_LIMITED`

### V1.9-R2 RC Aggregation Re-Smoke

执行命令：

```bash
npm run smoke:v1.9-research-quality
npm run smoke:v1.9-conflict-labeling
npm run smoke:v1.9-human-ux-package
npm run smoke:v1.9-rc
npm run check
```

结果：

- Research quality：`PASS_LIMITED`
- Conflict labeling：`PASS_LIMITED`
- Human UX package：`READY_FOR_HUMAN_ACCEPTANCE`
- RC decision：`V1_9_READY_FOR_FINAL_HUMAN_ACCEPTANCE`
- `npm run check`：PASS

状态：`PASS`

## 剩余验收工作

### V1.9-H Human Research Quality Acceptance

必须由人工完成，自动化不能替代。

验收内容：

1. 打开 `docs/design/V1.9/v1_9_c_human_ux_acceptance_report.html`。
2. 检查 Research supported conclusions 是否来自来源资料。
3. 检查 conflict topic 是否真实表达了来源分歧。
4. 检查两个 conflict positions 是否分别来自乐观口径和保守口径。
5. 检查 citation 是否能回跳 source / unit / EvidenceSpan。
6. 检查资料外问题是否拒答。
7. 检查报告没有把自动化 smoke 写成人工质量通过。

通过后才允许进入 V1.9 final sync。

## 仍不能声明

- 普通用户 UX fully ready
- all-domain Research ready
- all-source-type ready
- all websites URL ready
- OCR ready
- Audio Overview ready
- PPT generation ready
- Mindmap ready
- Document comparison ready
- cloud sync / collaboration ready

## 风险评估

| 风险项 | 当前评级 | 说明 |
| --- | --- | --- |
| 规格漂移 | MEDIUM | V1.9 只覆盖 approved datasets，不代表 all-domain Research |
| 虚假验收 | MEDIUM | 自动化已通过，但内容质量仍需人工审查 |
| 后端合同风险 | LOW | 当前 conflict smoke 和 focused tests 已覆盖 Alpha 样本 |

## 下一阶段

进入 `V1.9-H Human Research Quality Acceptance`。

如果人工验收通过，再进入 scoped final sync。

如果人工验收失败，回到 V1.9-R1 或 Research quality 修复阶段，不得声明 V1.9 完成。

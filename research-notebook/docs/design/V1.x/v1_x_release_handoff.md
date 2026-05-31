# ResearchNotebook V1.x Release Handoff

日期：2026-05-31

## 当前状态

`V1_X_FINAL_ACCEPTANCE_PASS_LIMITED`

## Handoff Summary

V1.x 已完成自动化收口汇总：

- V1.9 Research quality / conflict labeling 已进入 final human acceptance。
- V1.10 Phase 2/3 / OCR disabled boundary 已通过自动化验收。
- V1.x 最终 PRD 验收报告已生成。

当前交互式浏览器证据包已获用户认可，允许进入 scoped sync。

## 已验证证据

| 证据 | 路径 | 状态 |
| --- | --- | --- |
| V1.9 RC report | `docs/design/V1.9/v1_9_rc_final_prd_acceptance_report.md` | READY_FOR_FINAL_HUMAN_ACCEPTANCE |
| V1.10 disabled boundary report | `docs/design/V1.10/v1_10_rc_disabled_boundary_report.md` | ACCEPTED |
| V1.x final PRD acceptance report | `docs/design/V1.x/v1_x_final_prd_acceptance_report.md` | V1_X_FINAL_ACCEPTANCE_PASS_LIMITED |
| V1.x final acceptance fixture | `fixtures/real/v1_x/final-prd-acceptance/v1_x_final_prd_acceptance_result.json` | GENERATED |
| V1.x manual acceptance decision | `docs/design/V1.x/v1_x_manual_acceptance_decision.md` | ACCEPTED |
| V1.x interactive browser evidence | `.smoke-artifacts/v1_x_interactive_acceptance/1780225853829/result.json` | ACCEPTED |

## Release 前验收结论

本轮已认可交互式浏览器证据包。后续只保留抽样复核建议：

- Guide / QA / Studio / Research 的内容质量。
- Citation 可定位且与文本证据一致。
- Studio Markdown / JSON 导出文件真实可打开。
- V1.10 disabled 工具不会发起后端生成请求。
- 页面没有把 OCR / Audio / PPT / Mindmap / Document comparison 写成 ready。

## Scoped Sync Plan

当前交互式浏览器证据包已获用户认可，可以进行 scoped commit / push。最终声明仍必须保持 PASS_LIMITED，不得扩大为 all-source / all-domain ready。

提交前必须确认：

- `.smoke-artifacts/` 不进入 git。
- fixtures 不含本地绝对路径、cache path、artifact physical path、API key。
- 文档没有把 PASS_LIMITED 扩大成 all-source / all-domain ready。
- staged diff 不混入 unrelated sibling project。

建议提交信息：

```text
Finalize ResearchNotebook V1.x PRD release handoff
```

## 完成声明上限

当前 PASS_LIMITED 验收口径下最多声明：

```text
ResearchNotebook V1.x PRD MVP path is release-candidate-ready for validated PDF / TXT / Markdown and limited URL sources, with source-grounded Guide, QA, lightweight Studio outputs, export, citation navigation, and Research 补源 workflow on approved datasets.
```

## 仍不能声明

- all websites URL extraction ready
- all-source-type ready
- OCR ready
- scanned PDF ready
- Audio Overview ready
- PPT generation ready
- Mindmap ready
- Document comparison ready
- cloud sync / collaboration ready

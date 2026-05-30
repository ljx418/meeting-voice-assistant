# ResearchNotebook V1.6 Final Release Handoff

日期：2026-05-29

## 1. Handoff Summary

```text
V1.6_FINAL_ACCEPTANCE_PASS_SCOPED
```

V1.6 已完成 PRD MVP 受限路径的最终收口：

- validated PDF / TXT / Markdown。
- limited public URL sources。
- source-grounded Notebook Guide。
- source-grounded QA with citation navigation。
- Studio Notes / Study Guide / Briefing Doc / FAQ。
- Markdown / JSON Studio export。
- Research 补源 / 冲突分析合同 smoke。
- Phase 2/3 输出工具 disabled shell。

本阶段不进入 V1.7，不新增功能，只做 V1.6 final handoff 和 scoped repository sync。

## 2. Verified Commands

| 命令 | 状态 | 说明 |
| --- | --- | --- |
| `npm run check` | PASS | boundary checks、lint、128 tests、build 通过。 |
| `npm run smoke:v1.5-e-e2e` | PASS | Guide / QA / Studio / refusal / cleanup 浏览器路径通过。 |
| `npm run smoke:v1.1-visible-user-e2e` | PASS | workspace / source / preview / citation / session 路径通过。 |

## 3. Manual Acceptance Evidence

| 证据 | 路径 | 状态 |
| --- | --- | --- |
| 人工截图报告 | `docs/design/V1.6/v1_6_manual_quality_review_screenshot_report.html` | PASS，用户确认通过验收。 |
| 关键文本记录 | `docs/design/V1.6/v1_6_manual_quality_review_key_texts.md` | PASS，记录 ChromeCLI 路径关键文本和验收关注点。 |
| 前端 PRD 工作流报告 | `docs/design/V1.6/v1_6_frontend_prd_workflow_validation_report.md` | PASS，记录 404、来源导入、问答反馈、布局重叠修复和 ChromeCLI 结果。 |
| 最新 V1.5 E2E 截图 | `.smoke-artifacts/v1_5_e_chromecli_manual_e2e/1780026136870/` | 本地 artifact，不提交。 |
| 最新 visible-user 截图 | `.smoke-artifacts/v1_1_visible_user_e2e/1780026263488/` | 本地 artifact，不提交。 |

## 4. PRD Coverage Decision

| PRD 功能点 | V1.6 决策 |
| --- | --- |
| Notebook 创建 / 列表 / 最近打开 | PASS_LIMITED |
| PDF / TXT / Markdown 导入 | PASS_LIMITED |
| URL 正文抽取 | PASS_LIMITED |
| Notebook Guide | PASS_LIMITED_ACCEPTED |
| 引用问答 | PASS_LIMITED_ACCEPTED |
| 资料不足拒答 | PASS_LIMITED |
| Studio Notes / Study Guide / Briefing Doc / FAQ | PASS_LIMITED_ACCEPTED |
| Studio Markdown / JSON 导出 | PASS_LIMITED_ACCEPTED |
| Research 补源 / 综合输出 | PASS_LIMITED_CONTRACT_SMOKE |
| 冲突标注 | CONTRACT_ONLY |
| OCR / 扫描 PDF | CONTRACT_DISCOVERY_READY |
| Audio / PPT / Mindmap / Document comparison | DISABLED_READY |
| 云同步 / 协作 | OUT_OF_SCOPE |

## 5. Risk Review

| 风险 | 等级 | 结论 |
| --- | --- | --- |
| 规格漂移 | MEDIUM | 已由 scoped wording 收敛，不能扩展到 all-source、OCR、Phase 2/3 或 all-domain。 |
| 虚假验收 | MEDIUM | 已有真实数据、ChromeCLI 和用户人工截图验收；仍不能把 limited pass 写成全量 ready。 |

本阶段没有 HIGH 风险，允许进入 scoped commit / push。

## 6. Final Declaration

可以声明：

```text
ResearchNotebook V1.6 PRD MVP browser path and manual UX / quality screenshot review are accepted for validated PDF / TXT / Markdown and limited URL sources, with source-grounded Guide, QA, Studio exports, and Research contract smoke on approved datasets.
```

仍不能声明：

```text
all websites URL extraction ready
OCR ready
Audio Overview ready
PPT generation ready
Mindmap ready
Document comparison ready
all-domain Research ready
cloud sync / collaboration ready
```

## 7. Scoped Sync Plan

提交前必须确认：

- `.smoke-artifacts/` 不进入 git。
- fixtures 不含 `/Users`、`file://`、cache path、artifact physical path。
- 文档没有把 V1.6 扩大成 all-domain / all-source ready。
- staged diff 不混入 unrelated sibling project。

建议提交信息：

```text
Finalize ResearchNotebook V1.6 PRD acceptance handoff
```

## 8. Recommended Next Phase

V1.7 不应继续堆功能。建议先进入：

```text
V1.7 UX Recomposition / NotebookLM-style Usability Hardening
```

目标：

- 以 PRD 三列 IA 为基础重组信息密度。
- 降低开发调试字段暴露。
- 强化 Sources / Chat / Studio 的普通用户路径。
- 不新增 OCR、Audio、PPT、Mindmap、Compare 的真实能力，除非另开对应合同阶段。

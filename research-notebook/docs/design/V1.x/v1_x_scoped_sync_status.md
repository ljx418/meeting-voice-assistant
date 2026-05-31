# ResearchNotebook V1.x Scoped Sync Status

日期：2026-05-31

## 当前结论

`READY_FOR_SCOPED_SYNC_CONFIRMATION`

V1.x final PRD acceptance 已收口到 `V1_X_FINAL_ACCEPTANCE_PASS_LIMITED`，但本轮不自动 commit / push。

## 已完成验证

| 项 | 结果 |
| --- | --- |
| `npm run smoke:v1.9-rc` | PASS |
| `npm run smoke:v1.x-rc` | PASS，`V1_X_FINAL_ACCEPTANCE_PASS_LIMITED` |
| `npm run check` | PASS |
| `.smoke-artifacts/` git status | clean |
| `.bkp` 文件检查 | clean |
| V1.x fixtures / docs 脱敏检查 | PASS，命中仅限脚本中的 redaction / guard regex |

## 未执行 commit / push 的原因

当前 git 根目录为上层 workspace：

```text
<workspace-root>
```

当前远端为：

```text
origin https://github.com/ljx418/meeting-voice-assistant.git
```

远端名称与当前子项目 `research-notebook` 不一致，且当前工作区包含跨 V1.4 到 V1.x 的大量历史改动。为避免把 unrelated sibling project 或错误远端混入，本轮停止在 scoped sync confirmation。

## 建议人工确认

提交前需要确认：

- 当前 `origin` 是否就是 ResearchNotebook 目标远端。
- 是否允许在上层 workspace 仓库中提交 `research-notebook/` 子目录改动。
- 是否需要拆分 V1.4/V1.5/V1.6/V1.7/V1.8/V1.9/V1.10/V1.x 为多个提交。

## 建议 scoped staging

如果确认当前远端正确，建议仅 staging ResearchNotebook 范围：

```bash
git add research-notebook/package.json \
  research-notebook/scripts/v1_7_ux_smoke.mjs \
  research-notebook/scripts/v1_8_b_agent_source_import_smoke.mjs \
  research-notebook/scripts/v1_8_c_agent_guide_qa_smoke.mjs \
  research-notebook/scripts/v1_8_d_agent_studio_smoke.mjs \
  research-notebook/scripts/v1_8_e_weak_frontend_smoke.mjs \
  research-notebook/scripts/v1_8_rc_agent_prd_smoke.mjs \
  research-notebook/scripts/v1_9_conflict_labeling_smoke.mjs \
  research-notebook/scripts/v1_9_human_ux_acceptance_package.mjs \
  research-notebook/scripts/v1_9_rc_smoke.mjs \
  research-notebook/scripts/v1_9_research_quality_smoke.mjs \
  research-notebook/scripts/v1_10_disabled_boundary_smoke.mjs \
  research-notebook/scripts/v1_x_interactive_acceptance_capture.mjs \
  research-notebook/scripts/v1_x_rc_final_prd_acceptance.mjs \
  research-notebook/docs/design/V1.7 \
  research-notebook/docs/design/V1.8 \
  research-notebook/docs/design/V1.9 \
  research-notebook/docs/design/V1.10 \
  research-notebook/docs/design/V1.x \
  research-notebook/fixtures/real/v1_8 \
  research-notebook/fixtures/real/v1_9 \
  research-notebook/fixtures/real/v1_10 \
  research-notebook/fixtures/real/v1_x \
  research-notebook/fixtures/manual/v1_9
```

禁止使用：

```bash
git add .
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

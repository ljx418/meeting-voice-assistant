# V1.11 Full Code Review / E2E Acceptance Report

日期：2026-05-31

## 当前结论

`PASS_READY_FOR_SCOPED_SYNC`

本轮按“全量代码检视 + 全量端到端验收 + git 上传前检查”执行。Studio fallback 阻塞已修复并通过复验；用户已确认当前 remote 是目标远端，并允许在上层 workspace 仓库中执行 scoped commit / push。

## 阻塞项

### RESOLVED: V1.8 Studio 真实 AI 输出验收失败

修复前命令：

```bash
RN_V18_D_PROVIDER_MAX_ATTEMPTS=10 RN_V18_D_PROVIDER_RETRY_DELAY_MS=10000 npm run smoke:v1.8-agent-studio
```

结果：

```text
V1_8_D_AGENT_STUDIO_DECISION FAIL
```

失败原因：

- `faq used fallback mode`
- 前一次复跑还出现 `study_guide used fallback mode`
- V1.5 Studio 基线复跑也出现 `notes used fallback mode`

修复：

- 后端 Studio prompt 升级到 `v1_5_c_ai_studio_2026_05_31`。
- Studio validator 兼容常见 citation 字段。
- 模型遗漏 citation indexes 时，后端使用已有 evidence_refs 进行 schema normalization，仍保持每个 section 都有 evidence_refs。
- 增加 focused test 覆盖 missing section evidence refs normalization。

复验：

```bash
./.venv/bin/python -m pytest tests/test_target_http_studio_artifacts.py -q
RN_V18_D_PROVIDER_MAX_ATTEMPTS=10 RN_V18_D_PROVIDER_RETRY_DELAY_MS=10000 npm run smoke:v1.8-agent-studio
```

结果：

```text
6 passed
V1_8_D_AGENT_STUDIO_DECISION PASS_LIMITED
```

### RESOLVED: V1.8 RC 端到端汇总失败

命令：

```bash
npm run smoke:v1.8-agent-prd
```

修复后结果：

```text
V1_8_RC_AGENT_PRD_DECISION AGENT_CAPABILITY_SMOKE_READY
```

### RESOLVED: git remote / repository scope 已确认

当前 remote：

```text
origin https://github.com/ljx418/meeting-voice-assistant.git
```

当前项目是 `research-notebook` 子目录，git root 在上层 workspace。用户已确认该 remote 是目标远端，并允许提交 `research-notebook/` 加 data_service 两个 Studio 合同修复文件。提交仍必须 scoped staging，禁止 `git add .`，禁止混入 sibling project。

## 已通过项

| 命令 | 结果 |
| --- | --- |
| `npm run smoke:v1.7-ux` | PASS |
| `npm run smoke:v1.8-agent-source-import` | PASS_LIMITED |
| `RN_V18_C_PROVIDER_MAX_ATTEMPTS=8 RN_V18_C_PROVIDER_RETRY_DELAY_MS=8000 npm run smoke:v1.8-agent-guide-qa` | PASS_LIMITED |
| `RN_V18_D_PROVIDER_MAX_ATTEMPTS=10 RN_V18_D_PROVIDER_RETRY_DELAY_MS=10000 npm run smoke:v1.8-agent-studio` | PASS_LIMITED |
| `npm run smoke:v1.8-agent-prd` | AGENT_CAPABILITY_SMOKE_READY |
| `npm run smoke:v1.8-weak-frontend` | PASS_LIMITED |
| `npm run smoke:v1.9-rc` | PASS |
| `npm run smoke:v1.x-rc` | PASS |
| `npm run check` | PASS |
| `npm run smoke:v1.5-a-provider` | PASS |
| `npm run smoke:v1.5-c-studio` | PASS |
| data_service `tests/test_target_http_studio_artifacts.py` | PASS |

## 代码检视摘要

| 项 | 结果 | 说明 |
| --- | --- | --- |
| `/api/v1/knowledge/*` 新功能调用 | PASS | 命中仅在文档/guard/smoke 检查文本中 |
| feature/components direct `fetch(` | PASS | 未发现 feature/component 直接 HTTP fetch；route string 仍集中在 api adapter 或 smoke 脚本 |
| `dangerouslySetInnerHTML` | PASS | 未发现命中 |
| artifact_ref path parsing | PASS_WITH_REVIEW | 当前 UI 仅作为元数据展示；仍需继续禁止 path 解析 |
| backend id 用户态暴露 | PASS_LIMITED | 主要移动到调试详情中 |
| 测试覆盖变化 | REVIEW_REQUIRED | `WorkspacePage.test.tsx` 删除了 Agent workflow panel 相关测试，符合 V1.7 weak frontend 策略，但应在提交说明中明确 |

## PRD 规格检视

当前仍不能把 V1.8 / V1.x 写成全量 ready。原因：

- V1.8 / V1.x 仍是 approved dataset 上的受限 smoke。
- fallback 输出不能作为 AI quality pass，本轮已修复并复验。
- git remote 已确认，但提交必须保持 scoped。

## 决策

`READY_FOR_SCOPED_SYNC`

## 下一步

1. 执行 scoped staging；禁止 `git add .`。
2. 确认 staged diff 不包含 `.smoke-artifacts/`、sibling project、未脱敏日志或本地绝对路径。
3. commit / push 后记录 commit hash、branch、remote。

## 仍不能声明

- V1.x full release ready
- all-source-type ready
- all websites URL extraction ready
- OCR ready
- Audio / PPT / Mindmap / Document comparison ready

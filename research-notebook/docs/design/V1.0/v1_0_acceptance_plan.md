# ResearchNotebook V1.0 Acceptance Plan

文档状态：V1.0 planning baseline。
配套核心文档：`v1_0_current_gap_analysis.md` 与 `v1_0_current_gap_analysis.drawio`。

## 1. Final Acceptance Statement

V1.0 完成后可以声明：

```text
ResearchNotebook V1.0 source-grounded personal knowledge MVP ready.
```

含义：

- 用户可以创建/进入 workspace；
- 用户可以导入 source；
- 用户可以触发 build；
- 用户可以 ask with source-level evidence；
- 用户可以从 citation 打开 source trace/provenance drawer；
- 用户可以使用 session workbench 做临时研究；
- 用户可以查看 read-only graph context；
- 用户可以提交 lightweight feedback。

## 2. No False Green Rules

V1.0 不能声明：

- JSON/PPT/video/audio full ingestion ready；
- precise page/slide/timestamp/json citation backjump ready；
- interview assessment ready；
- question generation ready；
- attempt scoring ready；
- mastery profile ready；
- rich editor persistence ready；
- cloud sync ready；
- collaboration ready；
- correction apply ready；
- `/knowledge` 已成为 ResearchNotebook 产品 UI。

## 3. Phase Acceptance

| 阶段 | 出门标准 |
| --- | --- |
| M0 | AppShell、design tokens、health/version mismatch shell 可用。 |
| M1 | Workspace Home 真实调用 target routes，不使用 legacy route。 |
| M2 | Source Library、Build、Ask with Evidence、Trace Drawer 可用。 |
| M3 | Session Workbench 可用，并复用 evidence UI。 |
| M4 | Graph read-only context 与 lightweight feedback 可用，Quality 不成为主角。 |
| M5 | Post-MVP only。Source preview 和 precise evidence navigation 只有在 backend contract ready 后推进，不阻塞 V1.0 release。 |
| M6 | Future backend phase。Multi-format support 只由 capability manifest 驱动，不阻塞 V1.0 release。 |
| M7 | Future shell only。Assessment 不能伪装成正式能力，不阻塞 V1.0 release。 |

V1.0 release gate is M0-M4.

## 4. Contract Acceptance

前端必须满足：

- target route only；
- `dataServiceClient.ts` only route-shape layer；
- no raw path；
- stable IDs only；
- `artifact_ref` service-owned；
- operation polling for build/session build；
- normalized error states；
- unsupported/future states visible。
- `api-adapter-contract.md` completed before M2 implementation;
- `answer-evidence-contract.md` completed before M2 implementation;
- `operation-polling-contract.md` completed before M2 implementation;
- `error-state-model.md` completed before M2 implementation。

## 5. Product Acceptance

V1.0 体验必须优先满足：

```text
Home
Workspace Source Library
Source Import
Build Status
Ask with Evidence
Source Trace / Provenance Drawer
Session Workbench
Graph Context
Lightweight Feedback
```

如果 Quality/Governance 工作与 source-grounded ask 冲突，优先交付 source-grounded ask。

# V3.0 Old vs New Plan Comparison

对应图文件：`docs/design/V3.0/v3_old_vs_new_plan_comparison.drawio`

文档状态：COMPARISON / DECISION RECORD。新计划是当前活动计划；旧计划仅作为 V3.x+ 能力蓝图保留。

## 旧 V3.0 草案

文件：`docs/design/V3.0/v3_evolution_direction.md`

重点是通用 Agent 工作流平台方向，包括 Generic Workflow Model、Low-Code Workflow Runtime、DomainPack 2.0、Core Memory、Feedback Optimization Loop 和 Workflow Library。

旧计划价值是长期方向，不是当前执行顺序。Low-Code Workflow、Core Memory、Feedback Optimization Loop、Workflow Library 不进入 V3.0-PhaseA 到 V3.0-PhaseE 验收范围。

## 新 V3.0 计划

文件：`docs/design/V3.0/v3_development_plan_multi_app_core.md`

重点调整为先稳 Core：

- Multi-App Core Readiness
- Pack Assembly + Connector Registry
- Job / Artifact / Governance Hardening
- Meeting reference pack validation
- Knowledge reference pack validation

Interview、Investment、Video Studio 在 Meeting / Knowledge 两个 reference packs 完成平台化验证后再扩展。

## 核心区别

- 旧计划偏平台能力蓝图；新计划偏当前工程落地顺序。
- 旧计划把低代码和 workflow library 放在前景；新计划把多 app scope、Pack、Connector、Job、Artifact、Governance 放在最高优先级。
- 旧计划把视频作为典型案例之一；新计划明确 video_studio 延后到 V3.3。
- 新计划明确 meeting / knowledge 是标准迁移样板与 reference packs，interview / investment / video_studio 在平台边界验证后再扩展。
- 新计划不把样板业务等同于平台内置业务；若新增 app 仍需修改 Core/Gateway 业务逻辑，则说明平台目标尚未达成。
- 当前不得把低代码工作流、Memory System、Feedback Loop 放进 V3.0-PhaseA 到 V3.0-PhaseE 验收范围。

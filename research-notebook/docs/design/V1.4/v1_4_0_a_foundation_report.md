# ResearchNotebook V1.4-0/A Foundation Report

日期：2026-05-26

## 阶段结论

V1.4-0 PRD 重基线和文档重排：PASS。

V1.4-A 三列 Notebook 信息架构：PASS_LIMITED。

本阶段只完成 PRD Phase 1 的信息架构和文档基线，不声明 Notebook Guide、Studio 输出、P0 PDF/TXT/Markdown 导入解析已 ready。

## 已完成内容

- 新增 V1.4 文档目录和 PRD Phase 1 MVP 总计划。
- 将 V1.3 遗留手工验收、summary 质量验收、异常边界验收统一后移到 V1.4-RC。
- 工作区页面调整为 Sources / Chat / Studio 三列布局。
- 中列加入 Notebook Guide 区域和 Suggested Questions 入口。
- Studio 列加入 Notes / Study Guide / Briefing Doc / FAQ 工具入口。
- Agent 文件夹总结工作流保留在 Studio 侧作为扩展入口。
- Guide / Studio 区域明确显示合同待接入，不生成无引用或无来源支撑的伪结果。

## 未完成内容

- Notebook 重命名、删除、最近打开。
- P0 PDF/TXT/Markdown 上传、解析、状态、重试。
- Notebook Guide 后端生成合同。
- Studio Notes / Study Guide / Briefing Doc / FAQ 后端产物合同。
- 资料不足拒答、推断标注、补源引导。
- Chat / Studio citation 的完整产品化定位验收。

## 验收记录

| 验收项 | 结果 | 说明 |
| --- | --- | --- |
| V1.4 文档目录 | PASS | `docs/design/V1.4/` 已存在。 |
| V1.3 验收迁移 | PASS | 已记录后移到 V1.4-RC。 |
| 三列布局 | PASS_LIMITED | UI 骨架已落地，真实 Guide / Studio 后端合同仍未接入。 |
| Guide 壳 | PASS_LIMITED | 显示建议问题入口，但不伪造 Overview / Key Topics。 |
| Studio 壳 | PASS_LIMITED | 显示工具入口，但不生成输出。 |
| Agent 扩展入口 | PASS_LIMITED | 作为 Studio 侧扩展保留，不代表 PRD Studio 输出 ready。 |

## 规格漂移评估

风险等级：LOW。

原因：本阶段严格围绕 PRD 的 3 列布局、Guide-first 和 Studio 入口，没有把 V1.3 Agent 文件夹总结扩展成 PRD 主路径。

收敛措施：文档和 UI 均明确 Guide / Studio 后端合同待接入，后续仍按 V1.4-B 到 V1.4-RC 分阶段推进。

## 虚假验收评估

风险等级：MEDIUM。

原因：Guide / Studio 入口已可见，用户可能误以为生成能力已完成。

收敛措施：UI 使用“合同待接入”“当前不会伪造资料导读”“不生成无引用输出”等文案；文档状态使用 PASS_LIMITED / SHELL_ONLY，不使用 ready。

## 下一阶段审计

下一阶段：V1.4-B Notebook 生命周期补齐。

预期工作：

- 核对 workspace rename / delete / recent-open 的真实 route 和前端 wrapper。
- 若后端仅支持 archive，不得把 archive 冒充 delete。
- 若缺少 rename route，必须进入后端合同修复或保持 NOT_READY。
- 最近打开可以用前端本地状态实现，但必须标注为 local-only，不能声明跨设备同步。

下一阶段风险初评：

- 规格漂移：MEDIUM。
- 虚假验收：MEDIUM。

允许自动进入下一阶段的条件：真实 route / wrapper 可确认，或缺口被明确记录为 NOT_READY；不得用本地 UI 状态伪造后端生命周期能力。

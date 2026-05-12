# Data Service V1.5 冻结基线文档入口

本目录固化 Local Knowledge Governance Service 的 V1.5 accepted baseline。V1.5 已完成 PhaseG31 closure acceptance，后续只允许勘误，不再作为滚动开发文档维护。V1.6 的规划和后续开发文档位于 `../V1.6/`。

- `data-service-v1.5-roadmap.drawio`：V1.5 主路线图（canonical master），固化 V1.0 基线、V1.5 目标架构、详细开发计划和验收里程碑。
- `current-vs-target-gap.md`：V1.5 收口后的 Current vs Target / Gap 冻结文档。
- `current-vs-target-gap.drawio`：V1.5 Current vs Target / Gap 摘要图。
- `interface-convergence-matrix.md`：V1.5 接口收敛矩阵。
- `target-http-routes-contract.md`：V1.5 target HTTP contract，固化当前 3 个 target routes。
- `source-trace-contract.md`、`trace-cli-contract.md`、`quality-contract.md`、`graph-cli-contract.md`、`workspace-cli-contract.md`、`source-cli-contract.md`、`build-cli-contract.md`：V1.5 contract 基线文档。
- `PHASE-A1-MCP-SESSION-HANDLER-REPORT-2026-05-08.md`：V1.5 PhaseA1 Session MCP handler 模块化阶段报告。
- `PHASE-A2-MCP-QUALITY-HANDLER-REPORT-2026-05-08.md`：V1.5 PhaseA2 Quality MCP handler 模块化阶段报告。
- `PHASE-A3-MCP-CORE-HANDLER-REPORT-2026-05-08.md`：V1.5 PhaseA3 Core MCP handler 模块化阶段报告。
- `PHASE-A4-1-MCP-WORKSPACE-HANDLER-REPORT-2026-05-08.md`：V1.5 PhaseA4.1 Workspace MCP handler 模块化阶段报告。
- `PHASE-A4-2-MCP-SOURCE-HANDLER-REPORT-2026-05-08.md`：V1.5 PhaseA4.2 Source MCP handler 模块化阶段报告。
- `PHASE-A4-3-MCP-BUILD-HANDLER-REPORT-2026-05-08.md`：V1.5 PhaseA4.3 Build MCP handler 模块化阶段报告。
- `PHASE-A5-1-MCP-COMMON-HELPERS-REPORT-2026-05-08.md`：V1.5 PhaseA5.1 MCP common helpers 模块化阶段报告。
- `PHASE-A5-2-MCP-WORKSPACE-RUNTIME-REPORT-2026-05-08.md`：V1.5 PhaseA5.2 MCP workspace runtime 模块化阶段报告。
- `PHASE-A5-3-MCP-BUILD-RUNTIME-REPORT-2026-05-08.md`：V1.5 PhaseA5.3 MCP build runtime 模块化阶段报告。
- `PHASE-A5-4-MCP-REGISTRY-DISPATCH-REPORT-2026-05-08.md`：V1.5 PhaseA5.4 MCP registry / dispatch 模块化阶段报告。
- `PHASE-A5-5-MCP-CONTRACT-TESTS-REPORT-2026-05-08.md`：V1.5 PhaseA5.5 MCP contract tests 阶段报告。
- `PHASE-B1-SESSION-GRAPHRAG-SERVICE-BOUNDARY-REPORT-2026-05-09.md`：V1.5 PhaseB1 Session GraphRAG service 边界抽取阶段报告。
- `PHASE-B2-SESSION-RELATION-EXTRACTOR-REPORT-2026-05-09.md`：V1.5 PhaseB2 Session relation extractor 边界抽取阶段报告。
- `PHASE-C1-MCP-EXTERNAL-PAYLOAD-HARDENING-REPORT-2026-05-09.md`：V1.5 PhaseC1 MCP external payload hardening 阶段报告。
- `PHASE-C2-MCP-ERROR-CODE-CONTRACT-REPORT-2026-05-09.md`：V1.5 PhaseC2 MCP error code contract hardening 阶段报告。
- `PHASE-C3-HTTP-ENVELOPE-CONTRACT-REPORT-2026-05-09.md`：V1.5 PhaseC3 HTTP envelope contract convergence 阶段报告。
- `PHASE-D1-TYPED-DISTILL-UNIT-MAPPING-REPORT-2026-05-09.md`：V1.5 PhaseD1 typed distill unit mapping 阶段报告。
- `PHASE-D2-TYPED-UNIT-CONSUMER-HARDENING-REPORT-2026-05-09.md`：V1.5 PhaseD2 typed unit consumer hardening 阶段报告。
- `PHASE-D3-TYPED-FIXTURE-COVERAGE-REPORT-2026-05-09.md`：V1.5 PhaseD3 typed fixture coverage 阶段报告。
- `PHASE-E1-FORMAT-EXPANSION-DOCX-YAML-REPORT-2026-05-09.md`：V1.5 PhaseE1 docx/yaml 格式扩展阶段报告。
- `PHASE-E2-FORMAT-GOVERNANCE-DIAGNOSTICS-REPORT-2026-05-09.md`：V1.5 PhaseE2 格式治理诊断阶段报告。
- `PHASE-F1-CONSOLE-FORMAT-DIAGNOSTICS-REPORT-2026-05-09.md`：V1.5 PhaseF1 控制台格式治理可视化阶段报告。
- `PHASE-F2-CONSOLE-OPS-DRILLDOWN-REPORT-2026-05-09.md`：V1.5 PhaseF2 控制台异常队列 drilldown 阶段报告。
- `PHASE-F3-CONSOLE-MCP-CONTRACT-REPORT-2026-05-10.md`：V1.5 PhaseF3 控制台 MCP contract 可视化阶段报告。
- `PHASE-F4-CONSOLE-MCP-DEBUGGER-PRECHECK-REPORT-2026-05-10.md`：V1.5 PhaseF4 控制台 MCP Debugger payload 预检阶段报告。
- `PHASE-F5-FRONTEND-GRAPH-RECOVERY-REPORT-2026-05-10.md`：V1.5 PhaseF5 前端社区图恢复与 Explore 工作台可读性优化阶段报告。
- `PHASE-F5-FRONTEND-ACCEPTANCE-REPORT-2026-05-10.md`：V1.5 PhaseF5 前端验收阶段报告，包含桌面 / 移动截图验收记录。
- `PHASE-F6-FRONTEND-SOURCE-TRACE-AUDIT-REPORT-2026-05-10.md`：V1.5 PhaseF6 Source Trace 社区 fallback 与前端审计阶段报告。
- `PHASE-F7-FRONTEND-GRAPH-VISIBILITY-FIX-REPORT-2026-05-10.md`：V1.5 PhaseF7 社区图不可见根因修复与图谱可见性兜底阶段报告。
- `PHASE-F8-FRONTEND-GRAPH-POLISH-REPORT-2026-05-10.md`：V1.5 PhaseF8 GraphRAG 页面可读性与移动端遮挡优化阶段报告。
- `PHASE-F9-FRONTEND-REGENERATED-WORKBENCH-REPORT-2026-05-10.md`：V1.5 PhaseF9 前端 Explore 规则网格重生成阶段报告。
- `PHASE-F10-MCP-DEBUGGER-RESPONSE-PREVIEW-REPORT-2026-05-11.md`：V1.5 PhaseF10 MCP Debugger response / error envelope 预览阶段报告。
- `PHASE-G1-INTERFACE-CONVERGENCE-BASELINE-REPORT-2026-05-11.md`：V1.5 PhaseG1 接口语义统一基线与迁移护栏阶段报告。
- `PHASE-G2-QUERY-CONTRACT-SHIM-REPORT-2026-05-11.md`：V1.5 PhaseG2 Query 三入口 shared contract shim 阶段报告。
- `PHASE-G3-DISTILL-CONTRACT-SHIM-REPORT-2026-05-11.md`：V1.5 PhaseG3 Distill HTTP / CLI shared contract shim 阶段报告。
- `PHASE-G4-SOURCE-TRACE-CONTRACT-REPORT-2026-05-11.md`：V1.5 PhaseG4 Source Trace 目标 contract 与漂移测试阶段报告。
- `PHASE-G5-SOURCE-TRACE-SHARED-CONTRACT-REPORT-2026-05-11.md`：V1.5 PhaseG5 Source Trace shared contract helper 阶段报告。
- `PHASE-G6-SOURCE-TRACE-SCHEMA-MIGRATION-REPORT-2026-05-11.md`：V1.5 PhaseG6 Source Trace schema 示例与迁移窗口阶段报告。
- `PHASE-G7-LOW-SIGNAL-AUDIT-CONTRACT-REPORT-2026-05-11.md`：V1.5 PhaseG7 Low Signal Audit shared contract helper 阶段报告。
- `PHASE-G8-QUALITY-SUMMARY-CORRECTION-PLAN-CONTRACT-REPORT-2026-05-11.md`：V1.5 PhaseG8 Quality Summary / Correction Plan contract 阶段报告。
- `PHASE-G9-QUALITY-FEEDBACK-RULES-REVIEW-CONTRACT-REPORT-2026-05-11.md`：V1.5 PhaseG9 Quality Feedback / Rules / Review contract 阶段报告。
- `PHASE-G10-QUALITY-HTTP-SHARED-HELPER-REPORT-2026-05-11.md`：V1.5 PhaseG10 Quality HTTP shared helper 阶段报告。
- `PHASE-G11-QUALITY-CORRECTION-PLAN-HTTP-HELPER-REPORT-2026-05-11.md`：V1.5 PhaseG11 Quality Correction Plan HTTP helper 阶段报告。
- `PHASE-G12-QUALITY-CLI-MIGRATION-WINDOW-REPORT-2026-05-11.md`：V1.5 PhaseG12 Quality CLI planned 迁移窗口阶段报告。
- `PHASE-G13-QUALITY-CLI-READONLY-PREVIEW-REPORT-2026-05-11.md`：V1.5 PhaseG13 Quality CLI 只读 preview 阶段报告。
- `PHASE-G14-QUALITY-CLI-WRITE-COMMANDS-REPORT-2026-05-11.md`：V1.5 PhaseG14 Quality CLI 写入型治理命令阶段报告。
- `PHASE-G15-KNOWLEDGE-QUALITY-ALIAS-REPORT-2026-05-11.md`：V1.5 PhaseG15 knowledge quality entrypoint-ready alias 阶段报告。
- `PHASE-G16-PACKAGING-CONSOLE-SCRIPTS-REPORT-2026-05-11.md`：V1.5 PhaseG16 packaging console scripts 阶段报告。
- `PHASE-G17-KNOWLEDGE-ALIAS-SURFACE-GUARD-REPORT-2026-05-11.md`：V1.5 PhaseG17 knowledge alias 公开面护栏阶段报告。
- `PHASE-G18-KNOWLEDGE-QUERY-ALIAS-REPORT-2026-05-11.md`：V1.5 PhaseG18 knowledge query 最小 alias 阶段报告。
- `PHASE-G19-KNOWLEDGE-WORKSPACE-READONLY-ALIAS-REPORT-2026-05-12.md`：V1.5 PhaseG19 knowledge workspace 只读 alias 阶段报告。
- `PHASE-G20-KNOWLEDGE-SOURCE-READONLY-ALIAS-REPORT-2026-05-12.md`：V1.5 PhaseG20 knowledge source 只读 alias 阶段报告。
- `PHASE-G21-KNOWLEDGE-BUILD-STATUS-ALIAS-REPORT-2026-05-12.md`：V1.5 PhaseG21 knowledge build status 只读 alias 阶段报告。
- `PHASE-G22-KNOWLEDGE-GRAPH-SNAPSHOT-ALIAS-REPORT-2026-05-12.md`：V1.5 PhaseG22 knowledge graph snapshot 只读 alias 阶段报告。
- `PHASE-G23-KNOWLEDGE-TRACE-SOURCE-ALIAS-REPORT-2026-05-12.md`：V1.5 PhaseG23 knowledge trace source 只读 alias 阶段报告。
- `PHASE-G24-GRAPH-ADVANCED-CLI-MIGRATION-WINDOW-REPORT-2026-05-12.md`：V1.5 PhaseG24 graph advanced CLI 迁移窗口阶段报告。
- `PHASE-G25-WORKSPACE-WRITE-CLI-CONTRACT-REPORT-2026-05-12.md`：V1.5 PhaseG25 workspace write CLI contract 阶段报告。
- `PHASE-G26-SOURCE-WRITE-CLI-CONTRACT-REPORT-2026-05-12.md`：V1.5 PhaseG26 source write CLI contract 阶段报告。
- `PHASE-G27-BUILD-WRITE-CLI-CONTRACT-REPORT-2026-05-12.md`：V1.5 PhaseG27 build write CLI contract 阶段报告。
- `PHASE-G28-MCP-DISTILL-PREVIEW-REPORT-2026-05-12.md`：V1.5 PhaseG28 MCP distill preview 阶段报告。
- `PHASE-G29-MCP-SOURCE-TRACE-REPORT-2026-05-12.md`：V1.5 PhaseG29 MCP source trace 阶段报告。
- `PHASE-G30-TARGET-HTTP-ROUTES-REPORT-2026-05-12.md`：V1.5 PhaseG30 target HTTP routes 阶段报告。
- `PHASE-G31-V1.5-CLOSURE-ACCEPTANCE-REPORT-2026-05-12.md`：V1.5 PhaseG31 收口验收报告。
- `PHASE-G24-G31-REMAINING-DEVELOPMENT-PLAN-2026-05-12.md`：V1.5 剩余开发计划，固化目标形态、PhaseG24-G31 阶段拆分和最小闭环版本。

冻结规则：V1.5 文档以 PhaseG31 accepted 状态为准。`data-service-v1.5-roadmap.drawio`、`current-vs-target-gap.drawio` 和 `current-vs-target-gap.md` 必须保持一致；如发现错别字、路径或阶段状态不一致，只做勘误，不新增 V1.6 能力描述。

V1.0 表示当前已完成并冻结的 MCP-first 本地知识治理服务基线。V1.5 的主线是边界收口、MCP handler 模块化、Session GraphRAG 正式化、typed distill units、格式扩展、控制台治理化和接口语义统一。

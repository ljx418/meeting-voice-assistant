# V2 Remaining Development Governance Plan

## Summary

V2 后续开发采用“阶段前计划 -> PRD 规格审计 -> 开发 -> 真实数据端到端验收 -> 阶段审计 -> 决策门禁”的闭环流程。任何阶段只要出现重大规格偏差、虚假验收风险、真实数据验收失败，就停止进入下一阶段，回到开发计划阶段重新评估并修订。

当前进入实质开发前必须先完成 Phase 0 准备与审计闭环。Phase 0 通过后，只允许进入 PR1：Codebase Registry + Artifact Foundation。

## Governance Gates

每个阶段必须单独产出：

- 阶段开发计划：`docs/V2.x/V2_PROJECT_INTELLIGENCE_PHASE_{N}_DEVELOPMENT_PLAN.md`
- 阶段验收计划：`docs/V2.x/V2_PROJECT_INTELLIGENCE_PHASE_{N}_ACCEPTANCE_PLAN.md`
- 阶段审计报告：`docs/V2.x/V2_PROJECT_INTELLIGENCE_PHASE_{N}_AUDIT_REPORT.md`

每个阶段开始前必须完成：

- 对照 `docs/V2.x/V2_PROJECT_INTELLIGENCE_PRD.md` 做 PRD 规格检视。
- 对照 `docs/V2.x/V2_PROJECT_BASELINE.md` 做架构边界检视。
- 对照 V2.0 目标文档做阶段范围检视：
  - `docs/V2.x/V2_0_TARGET_ARCHITECTURE.md`
  - `docs/V2.x/V2_0_TARGET_PRD.md`
  - `docs/V2.x/V2_0_TARGET_ACCEPTANCE_PLAN.md`
  - `docs/V2.x/V2_0_PHASE_2_7_DEVELOPMENT_AND_ACCEPTANCE_PLAN.md`
- 明确本阶段真实数据验收样例、命令、预期产物、失败处理。
- 审计意见分级：`fatal | major | minor | note`。
- `fatal` 或 `major` 未闭环时不得进入实质开发。

每个阶段完成后必须完成：

- 真实数据端到端验收，不允许只用 mock 或单元测试替代。
- PRD 规格回放：确认实现没有偏离用户故事、接口、非功能、安全、证据链要求。
- 虚假验收风险评估：检查是否存在只验证 happy path、只测 fixture、不查 artifact、不查失败路径、不查证据链等问题。
- 若验收失败，打回本阶段开发计划，修订计划后再开发。

## Phase Plan

### Phase 0：准备与审计闭环

目标：确认 V2 进入开发前没有基础阻塞。

工作内容：

- 固化当前三份 V2 文档作为阶段输入：baseline、PRD、development/acceptance plan。
- 检查当前工作区变更，隔离既有 unrelated changes。
- 确认 V2 首发只做 PR1-PR7，PR8-PR10 作为 stretch。
- 明确真实数据验收主样例：当前 `data_service` repo。
- 明确 V2 不进入现有 source registry、不扩大 `data_service.py` 和 `service.py`。

进入下一阶段条件：

- Phase 0 审计报告无未闭环 `fatal` / `major`。
- PR1 开发范围和验收命令明确。
- 当前工作区变更已隔离，或已有明确路径级开发约束。

### Phase 1 / PR1：Codebase Registry + Artifact Foundation

目标：新增独立 codebase asset registry。

接口：

- HTTP:
  - `POST /api/workspaces/{workspace_id}/codebases`
  - `GET /api/workspaces/{workspace_id}/codebases`
  - `GET /api/workspaces/{workspace_id}/codebases/{codebase_id}`
  - `POST /api/workspaces/{workspace_id}/codebases/{codebase_id}/archive`
- MCP:
  - `knowledge_codebase_import`
- CLI:
  - `knowledge code import`

真实数据验收：

- 使用当前 repo 路径导入 codebase。
- 验证生成 `workspace/assets/codebase/{codebase_id}/codebase.json`。
- 重复导入同一路径返回同一 asset。
- archive 后不作为 active asset。
- 非 allowed root 路径返回 `PATH_NOT_ALLOWED`。
- 检查现有 source registry 未变化。

### Phase 2 / PR2：Repo Snapshot + File Manifest

目标：生成稳定 repo snapshot。

真实数据验收：

- 对当前 repo 生成 snapshot。
- 验证 `snapshot.json`, `files.jsonl`, `stats.json`, `warnings.jsonl`。
- 验证当前 repo 能识别 docs、backend、frontend、tests、README、配置文件。
- 验证 `.git`, `.venv`, `node_modules`, `dist`, `build`, `__pycache__` 被跳过。
- 验证同一代码状态下 snapshot_id 稳定。

### Phase 3 / PR3：Public Surface Inventory

目标：抽取 HTTP/MCP/CLI/frontend public surface。

真实数据验收：

- 当前 repo 至少识别 FastAPI app、target/legacy HTTP routes。
- 当前 40 个 MCP tools 可识别。
- `data-service` 和 `knowledge` CLI 可识别。
- Vue console entry/API client 可识别。
- 输出 alignment matrix。
- 每个 surface 有 source file、line range、confidence。

### Phase 4 / PR4：Python Symbol Index

目标：AST 抽取 Python symbols 和 imports。

真实数据验收：

- 当前 backend Python 文件可解析。
- 可搜索 HTTP handler、MCP handler、CLI parser symbols。
- `imports.jsonl` 可输出模块依赖。
- 语法错误 fixture 不导致全局失败。

### Phase 5 / PR5：Surface-to-Symbol Mapping + Evidence Trace

目标：把公开服务追踪到 symbol/file/line。

真实数据验收：

- source import、query、build、quality 能 trace 到 surface、handler、file、line。
- unresolved mapping 明确输出原因。
- evidence path repo-relative。
- 低置信度 mapping 标记 confidence。

### Phase 6 / PR6：MCP / HTTP / CLI Contract Convergence

目标：统一 V2 MVP 三端访问能力。

真实数据验收：

- 使用同一当前 repo，分别通过 HTTP/MCP/CLI 完成 import、snapshot、inventory、symbols、trace。
- 对比三端输出关键字段一致。
- V1 MCP/HTTP/CLI smoke tests 通过。

### Phase 7 / PR7：Project Overview + Agent Context Pack MVP

目标：生成可供 Agent 阅读项目的 Project Overview，并生成 task-aware、证据驱动的 Agent Context Pack。

真实数据验收：

- 对当前 repo 通过 HTTP/MCP/CLI 读取 Project Overview。
- Overview 必须包含项目定位、入口、公开能力、核心模块、存储结构、风险和 evidence。
- Context Pack 支持 `project_brief` 和 `task_context` 两种模式。
- 对当前 repo 输入通用阅读任务：“请阅读并汇总当前项目的定位、入口、公开能力、核心模块和证据”。
- 对当前 repo 输入任务：“新增 codebase import MCP tool，并同步 HTTP API”。
- 输出必须包含相关 MCP registry、dispatcher、existing source/build tool patterns、HTTP router、CLI parser、tests。
- 每个关键建议、风险、测试建议和 recommended next step 有 evidence 或 `needs_review`。
- evidence 不足标记 `needs_review`。
- 设置较小 `max_tokens` 时必须裁剪并输出 omitted reasons。

## V2.1 Expansion Phases

- Phase 8：DevWiki Baseline。仅在 PR1-PR7 验收通过后进入，必须基于 V2 artifacts，不允许纯 LLM 编写。
- Phase 9：Code Graph Baseline。仅在 mapping/evidence 质量稳定后进入，生成确定性 file/module/symbol/surface/capability graph。
- Phase 10：Quality Governance Extension。仅在 Agent Context Pack 和 DevWiki 对象稳定后进入。

V2.0 Agent-callable MVP = Phase 1-7。DevWiki、Code Graph、Code Quality Governance Extension 和最小前端只读页面属于 V2.1 Expansion，除非 PRD 和验收计划再次明确调整。

## Stage Failure Policy

任一阶段满足以下条件必须停止并找用户确认：

- PRD 目标与实现路径出现重大偏差。
- 真实数据验收失败两轮后仍无法闭环。
- 需要修改 V1 核心行为或破坏兼容性。
- 需要继续扩大 `backend/app/api/v1/data_service.py` 或 `backend/data_service/service.py` 才能完成。
- V2 codebase artifact 生成会污染 `lifecycle/sources.json` 或依赖普通 source registry 才能工作。
- Phase 7 需要把 ranking、rendering、token budget、evidence selection 和 persistence 全部堆进单个巨型 context pack 文件。
- 出现 evidence 伪阳性、虚假 line range、mock 冒充真实验收。
- 安全策略需要放宽，例如允许任意路径扫描或返回敏感绝对路径。
- 性能目标明显无法满足 5,000 files / 100k LOC。

## Test And Acceptance Requirements

每阶段至少包含：

- unit tests
- contract tests
- artifact golden tests
- real repo end-to-end test
- failure path tests
- V1 regression smoke test
- audit report

真实数据验收默认使用当前 `data_service` repo。mock 只能用于边界条件，不得替代最终验收。

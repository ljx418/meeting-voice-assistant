# CLAUDE.md

## 项目概述

harnessOS - 项目名称待定

## 🧑‍💻 编码规范（强制执行）
### 通用规则
- **优先尝试自己验证**：在找用户确认修改效果之前，先在本地完成验证，确保修改确实有效。不要在未验证的情况下找用户测试。
- **语言**：所有代码注释、提交信息、变量命名必须使用**英文**；用户界面文案使用**简体中文**。
- **格式化**：使用 Prettier + ESLint（配置见 `.prettierrc` / `.eslintrc`）。
- **类型**：TypeScript 严格模式开启，避免使用 `any`。
- **代码复用**：**优先使用已经存在的 example 内的代码，优先做嫁接工作**。嫁接代码时需要先看懂代码、明确设计之后再执行。

### 命名约定
| 类型 | 规范 | 示例 |
|------|------|------|
| 组件文件 | PascalCase | `UserProfile.tsx` |
| 工具函数 | camelCase | `formatDate.ts` |
| 常量 | UPPER_SNAKE_CASE | `MAX_RETRY_COUNT` |
| 环境变量 | `VITE_` 前缀（前端） | `VITE_API_BASE_URL` |
| Git 分支 | `feature/xxx`, `fix/xxx`, `chore/xxx` | `feature/add-auth` |

### 代码风格
- **函数组件** + 命名导出（除非需要懒加载）。
- **Props 类型**：使用 `interface` 声明，放在组件文件上方。
- **副作用**：优先使用 React Query 管理服务端状态；客户端状态使用 Zustand。
- **错误处理**：异步操作必须包含 try/catch，并记录到日志系统。
- **样式**：使用 Tailwind CSS，避免内联 style。

### 测试要求
- 核心业务逻辑必须有单元测试（Vitest）。
- 组件测试至少覆盖交互行为（React Testing Library）。
- 测试文件与源文件同目录，命名为 `*.test.tsx`。

## 📋 常用命令
| 用途 | 命令 |
|------|------|
| 安装依赖 | `pnpm install` |
| 启动开发服务器 | `pnpm dev` |
| 类型检查 | `pnpm type-check` |
| 运行测试 | `pnpm test` |
| 构建生产版本 | `pnpm build` |
| 代码格式化 | `pnpm format` |
| 代码检查 | `pnpm lint` |

## 🔧 环境配置
- Node.js 版本：20.x（使用 `.nvmrc` 管理）
- 包管理器：pnpm 8.x
- 环境变量文件：`.env.local`（不提交 Git）
- 代理配置：本地开发 API 代理指向 `http://localhost:3001`

## 🗂️ 任务管理（重要）
- 当前进行中的任务记录在 `TASKS.md` 文件（项目根目录）。
- 每个任务条目格式：`- [ ] 任务描述（预估耗时）`
- 完成时标记为 `- [x]`，并更新 `COMPLETION_DATE`。
- Claude Code 在每次会话开始时**必须读取 `TASKS.md`**，并遵守任务优先级。

## 🧠 架构决策记录（ADR）
重要决策请在 `docs/decisions/` 下创建 `ADR-XXX-标题.md`，内容包含：
- **背景**：为什么需要做决策
- **方案**：选择了什么方案
- **权衡**：与其他方案的对比
- **影响**：对代码库/团队的长期影响

## ⚠️ 注意事项
- 不要直接修改 `node_modules` 或 `dist` 目录。
- 涉及数据库迁移时，必须先生成迁移文件再执行。
- 提交前确保所有测试通过、类型检查无错误。
- 禁止在代码中硬编码密钥或敏感信息（使用环境变量）。

## 🔄 会话初始指令
当 Claude Code 启动时，自动执行：
1. 读取 `TASKS.md` 并理解当前进度。
2. 如果存在未完成任务，主动询问是否继续。
3. 若需要了解项目架构，查阅 `CLAUDE.md` 本文件。
4. 遵循编码规范输出代码。

## 📐 项目架构

### 架构设计 v1

**核心思想**：产品边界在自己手里，harness 不直接等于产品。

```
用户入口层 → API Gateway/BFF → Agent Orchestrator + Developer Control Plane
                                        ↓
                           Core Agent Graph Layer
                          (Deep Agents / LangGraph)
                                        ↓
              Knowledge & Memory Plane  +  Artifact & Execution Plane
```

### 框架落位

| 框架 | 负责领域 | 参考代码 |
|------|----------|----------|
| **Deep Agents** | 主 agent 内核：planning、filesystem、execute、sub-agents | `examples/deep-agents/` |
| **OpenHarness** | 开发者控制面：commands、hooks、permissions、plugins | `examples/open-harness/` |
| **DeerFlow** | 工件/执行面：Gateway、workspace、artifacts、sandbox | `examples/deer-flow/` |

### 架构图文件

| 文件 | 描述 |
|------|------|
| `docs/architecture/current-vs-target-gap_v2.drawio` | **当前与目标架构差距图** - 当前六平面目标口径 |
| `docs/architecture/diagrams/01_current_architecture_v2.drawio` | 当前架构图 |
| `docs/architecture/diagrams/02_target_architecture_v2.drawio` | 目标架构图 |
| `docs/history/architecture/reference-frameworks/deerflow-architecture.drawio` | DeerFlow 2.0 历史参考图 |
| `docs/history/architecture/reference-frameworks/deep-agents-architecture.drawio` | Deep Agents 历史参考图 |
| `docs/history/architecture/reference-frameworks/openharness-architecture.drawio` | OpenHarness 历史参考图 |

### API 设计文档

| 文件 | 描述 |
|------|------|
| `docs/api/unified-message-schema_v2.md` | 统一消息模式 (ConversationMessage, StreamEvent, etc.) |
| `docs/api/gateway-endpoints_v2.md` | API Gateway 端点设计 |
| `docs/api/orchestrator-interface_v2.md` | 编排器接口 (IntentRouter, WorkflowDispatcher, etc.) |
| `docs/api/llm-provider-config_v2.md` | LLM Provider 配置 |

### 测试验收计划

| 文件 | 描述 |
|------|------|
| `docs/test-acceptance-plan_v2.md` | 完整测试验收计划 (Phase 0-5) |

### 外部 API 清单

| 接口 | 方法 | 用途 |
|------|------|------|
| `/v1/runs` | POST | 发起 agent run |
| `/v1/runs/{run_id}/stream` | GET (SSE) | 流式事件 |
| `/v1/runs/{run_id}` | GET | 查询 run 状态 |
| `/v1/uploads` | POST | 上传文件 |
| `/v1/artifacts/{artifact_id}` | GET | 获取工件 |
| `/v1/knowledge/ingest` | POST | 文档入库 |
| `/v1/knowledge/search` | POST | 检索知识 |
| `/v1/approvals/{approval_id}/decide` | POST | 审批决策 |
| `/v1/jobs` | POST | 发起长任务 |
| `/v1/sessions/{session_id}` | GET | 查询会话 |

### 核心契约类型

- `SessionContext` - 会话上下文
- `RunRequest` / `RunEvent` - 运行请求与事件
- `AgentOutput` / `CitationRef` - Agent 输出与引用
- `Artifact` - 工件
- `ToolCallRecord` / `ApprovalRecord` - 工具调用与审批记录

### v1 最小工具集 (10个)

`workspace_ls` | `workspace_read_file` | `workspace_write_file` | `artifact_save` | `kb_ingest` | `kb_search` | `transcript_parse` | `score_answer` | `draft_email` | `approval_request`

### v1 最小 Skill 集 (10个)

`global-routing` | `meeting-prep` | `meeting-minutes` | `action-items` | `jd-gap-analysis` | `mock-interview` | `answer-review` | `knowledge-ingest` | `knowledge-synthesis` | `followup-scheduler`

### 仓库结构 v1

```
repo/
  apps/
    web/                   # 用户产品前端
    admin/                 # 管理后台 / 运营台
    api/                   # BFF / Gateway

  core/
    domain/                # 领域模型
    orchestration/         # intent router, workflow dispatcher
    policies/              # 权限、审批、审计规则
    schemas/               # 统一消息 schema

  agents/
    lead_orchestrator/     # 主控代理
    meeting_analyst/        # 会议分析代理
    interview_coach/        # 面试辅导代理
    kb_curator/            # 知识库管理代理
    scheduler_assistant/     # 日程助理
    media_orchestrator/     # 媒体编排代理

  tools/
    productivity/          # email / calendar / docs / task
    knowledge/             # retrieve / ingest / cite
    media/                 # script / storyboard / render
    sandbox/               # fs / shell / browser
    connectors/            # MCP / third-party APIs

  execution/
    workspace/             # per-task workspace manager
    artifacts/             # artifact store + serving
    jobs/                  # async jobs / queue / retry
    sandbox/               # local/docker/k8s adapters

  devplane/
    cli/                   # 开发者 CLI
    tui/                   # 本地调试控制台
    commands/              # slash commands
    hooks/                 # pre/post tool hooks
    plugins/               # plugin SDK
```

## 👥 开发团队

本项目的开发团队信息存储在 `~/.claude/teams/*/config.json` 配置文件中，**不记录于本文件**。

### 团队结构 (5人)

| 角色 | 职责 |
|------|------|
| **产品经理 (product-manager)** | 产品规划、需求分析、PRD编写、优先级管理 |
| **架构师 (architect)** | 系统架构设计、技术规范制定、复杂问题解决 |
| **前端开发 (frontend-dev)** | Vue组件开发、WebSocket通信、UI优化、前端测试 |
| **后端开发 (backend-dev)** | API开发、ASR适配器、LLM模块、后端测试 |
| **测试工程师 (tester)** | 前端测试(组件/交互)、后端测试(API/集成)、质量保证 |

### AgentTeam 使用规范

1. **优先使用原型**：团队成员启动后形成原型（如 `architect`），任务完成后成员进入空闲等待状态
2. **复用而非重建**：再次需要该角色时，**优先使用 `SendMessage` 唤醒原型**，而非用 `Agent` 创建新实例
3. **避免重复创建**：每次用 `Agent` 启动同名成员会生成 `-2`、`-3` 后缀的实例，导致实例堆积
4. **正确流程**：
   - 需要 `architect` → 检查是否已启动 → 已启动则 `SendMessage({to: "architect", ...})`
   - 原型未启动 → 用 `Agent` 启动（会注册为原型）
   - 原型已启动又启动 → 产生 `-2` 冗余实例

---
**最后更新**：2026-04-23
**维护者**：harnessOS-dev 团队

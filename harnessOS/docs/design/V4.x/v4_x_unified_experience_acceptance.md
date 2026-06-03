# V4.x Unified Experience Acceptance

文档状态：V4-U9 后的统一体验验收矩阵。UX-01 到 UX-12 已有可审计证据，最终人工验收报告和 V5 移交 brief 已生成。

## 1. 验收原则

所有验收按用户体验路径组织。每条路径必须标记：

```text
PASS / PARTIAL / FAIL / BLOCKED
```

每条路径必须保存：

```text
transcript
workflow spec or scenario spec
drawio
html report
runtime / evidence json
result summary
```

每个 `result-summary.md` 必须包含以下机器可审计字段：

```text
ux_id
status: PASS / PARTIAL / FAIL / BLOCKED
evidence_scope: real_runtime / deterministic_devlocal / transcript_only / report_only / planned_contract
evidence_refs
runtime_backed: true / false
deterministic_only: true / false
false_green_risk: LOW / MEDIUM / HIGH
notes
```

## 2. 验收路径

| ID | 体验路径 | 入口 | 输出 | PASS 条件 |
| --- | --- | --- | --- | --- |
| UX-01 | 自然语言创建工作流 | Mission Console | WorkflowSpec / Diff | 用户确认前不写 runtime |
| UX-02 | Workflow Blueprint 可视化 | Drawio | workflow.drawio | 只读、可重现、无敏感字段 |
| UX-03 | Runtime Report 运行观察 | HTML Report | workflow_board.html | 状态来自 runtime DTO |
| UX-04 | Artifact 查看 | Runtime Report | artifacts.html | station output 和 lineage 可见 |
| UX-05 | Quality 查看 | Runtime Report | quality.html | failed / warning 可定位 |
| UX-06 | 局部失败修复与重跑 | Review Console | new attempt | rerun 必须 user_confirmed |
| UX-07 | Evidence Chain 审查 | Evidence Report | evidence.html | 只读、不可执行 mutation |
| UX-08 | 串行多 Agent 视频工作流 | V4-U7 scenario | video report | provider-backed station artifacts、rerun、downstream stale 可见 |
| UX-09 | 并行罗马广场讨论 | V4-U7 scenario | persona reports | provider-backed persona artifact、synthesis、attribution 可见 |
| UX-10 | 长时工程任务工作流 | V4-U7 scenario | durable board | provider-backed stage artifact、code_review rerun、人工确认可见 |
| UX-11 | Agent Workflow Builder | V4.6 scenario | draft / repair proposal | Agent 不 auto apply / run |
| UX-12 | 真实 LLM 本地技术文档解析 | V4-U5E scenario | folder summaries / overview | 用户确认后真实读取 Markdown 并调用 LLM |

当前 reality-check 状态：

```text
PASS: 12
PARTIAL: 0
FAIL: 0
BLOCKED: 0
allow_enter_v4_u6: true
requires_human_proceed_decision: false
```

V4-U7 后 UX-08 / UX-09 / UX-10 状态：

```text
UX-08 PASS / real_runtime / provider-backed dev/local。
UX-09 PASS / real_runtime / provider-backed dev/local。
UX-10 PASS / real_runtime / provider-backed dev/local。
```

## 2.1 UX-12 Real LLM Local Technical Document Workflow

PASS 条件：

```text
显式 user_confirmed 本地文件夹读取授权。
实际读取 Desktop/技术分享 或等价 fixture。
递归解析 .md / .markdown 文件。
优先使用 MiniMax provider，或明确配置的 OpenAI-compatible provider。
真实 LLM provider 生成每个子文件夹总结。
真实 LLM provider 生成总览总结。
quality_report.json 记录 unsupported 文件和空文件夹。
Evidence Chain 记录 provider/model/provider_config_source/prompt_template_ref/input_artifact_refs/output_artifact_refs。
DOM、network log、error response、evidence 不泄露 raw prompt 或 raw file content。
```

如果没有可用 LLM provider key：

```text
UX-12 必须标记 BLOCKED 或 fallback_demo_only。
不得把 deterministic/template summary 写成 real_llm PASS。
不得把缺少 MINIMAX_API_KEY 的场景写成 MiniMax-backed PASS。
```

当前 UX-12 状态：

```text
PASS / real_runtime。
当前 evidence 显示真实本地 Markdown 读取、真实 LLM provider invocation、provider/model/provider_config_source 记录、LLM-backed folder summaries 和 overview summary。
```

## 3. U5A Evidence Rules

```text
UX-08 / UX-09 / UX-10 如果只是 deterministic dev/local，不得写成 full multi-Agent orchestration PASS。
如果存在 PARTIAL，必须记录是否允许进入 U6。
如果存在 FAIL / BLOCKED，不能进入 U6。
V4-U5A 只能声明 scenario evidence archive ready for review。
V4-U5 只有在 UX-01 到 UX-12 全部归档且 UX-12 不再 BLOCKED 后才能声明 scenario path acceptance package ready for V4-U6 gate review。
V4-U7 之后无需再为 UX-08 / UX-09 / UX-10 记录 PARTIAL proceed decision，但仍必须保留 dev/local 和 No False Green 边界。
```

V4-U8 后新增人工验收入口：

```text
docs/design/V4.x/evidence/manual-acceptance/u8-manual-acceptance-report.html
docs/design/V4.x/evidence/manual-acceptance/u8-manual-acceptance-data.json
```

V4-U9 后新增最终人工验收与 V5 移交入口：

```text
docs/design/V4.x/evidence/final-human-acceptance/u9-final-acceptance-report.html
docs/design/V4.x/evidence/final-human-acceptance/u9-final-acceptance-data.json
docs/design/V4.x/evidence/final-human-acceptance/u9-prd-spec-review.md
docs/design/V4.x/evidence/final-human-acceptance/u9-false-green-audit.md
docs/design/V5.x/v5_0_production_productization_planning_brief.md
```

## 4. 全局断言

```text
source=agent cannot execute mutation
durable mutation requires user_confirmed=true
EventBridge only triggers refresh
WorkflowSpec cannot mutate runtime truth
Drawio is visualization only
HTML Report is read-only
Browser does not call /v1/rpc
Browser does not call /v1/events/subscribe
No token/raw payload leakage
No false-green claims
```

## 5. Evidence Output

统一验收证据目录：

```text
docs/design/V4.x/evidence/unified-experience/
  UX-01/
  UX-02/
  UX-03/
  UX-04/
  UX-05/
  UX-06/
  UX-07/
  UX-08/
  UX-09/
  UX-10/
  UX-11/
  mission_console_transcript.txt
  result-summary.md
```

# V4-U6 Unified Experience Gate Completion Note

文档状态：V4-U6 统一体验收口门禁完成，带 PARTIAL 风险限定。

## Allowed Claim

```text
V4-U6 complete: V4 unified dev/local experience baseline ready for review.
```

必须附带限定：

```text
Headless workflow core with Mission Console, Workflow Blueprint, Runtime Report, Review Console, and Evidence Chain ready for review.
This does not prove complete Workflow Studio, Agent executor, controlled executor production readiness, production external app support, or full multi-Agent orchestration.
```

## Forbidden Claims

```text
complete Workflow Studio ready
complete AgentTalkWindow ready
Agent executor ready
controlled executor ready
production-ready external app support
full multi-Agent orchestration ready
autonomous workflow editing ready
production-ready external app support
```

## Human Proceed Decision

```text
Decision: accepted PARTIAL UX-08 / UX-09 / UX-10 for V4-U6 gate review.
Decision source: user instruction to continue into U6 after reviewing the U5 manual acceptance report.
Decision meaning: proceed with U6 gate review without converting UX-08 / UX-09 / UX-10 to PASS.
```

Accepted PARTIAL cases:

| UX | Status | Evidence Scope | False Green Risk | U6 Interpretation |
| --- | --- | --- | --- | --- |
| UX-08 串行多 Agent 视频工作流 | PARTIAL | deterministic_devlocal | HIGH | Dev/local scenario evidence only; not full multi-Agent orchestration. |
| UX-09 并行罗马广场讨论 | PARTIAL | deterministic_devlocal | HIGH | Dev/local scenario evidence only; not real parallel multi-Agent runtime. |
| UX-10 长时工程任务工作流 | PARTIAL | deterministic_devlocal | HIGH | Dev/local scenario evidence only; not autonomous coding or Agent executor. |

## Gate Result

```text
PASS: 9
PARTIAL: 3
FAIL: 0
BLOCKED: 0
U6 gate review: complete with accepted PARTIAL risk
automatic U6 entry: not allowed by reality-check
human proceed decision: recorded
```

## PRD Spec Review

V4.x PRD 要求的主体验链路为：

```text
用户说目标
 -> Mission Console 捕获意图
 -> 生成 WorkflowSpec / Diff
 -> Workflow Blueprint 理解结构
 -> 用户确认
 -> Runtime Report 观察运行
 -> Review Console 做局部重跑 / 修复 / 确认
 -> Evidence Chain 审计复盘
```

U6 gate review 证明该链路已经形成 dev/local 统一体验基线，可用于 review。它不证明完整 Web Studio、完整 AgentTalkWindow、Agent executor、production controlled executor、production external app support 或 full multi-Agent orchestration。

## Real Data Evidence

UX-12 已复跑真实数据链路：

```text
provider: minimax
model_ref: MiniMax-M2.1
provider_config_source: .env.local
scanner_actual_read_count: 5
provider_invocation_count: 4
real_llm_backed: true
fallback_demo_only: false
```

## Runtime Truth Boundary

```text
WorkflowSpec Registry 不能替代 WorkflowDraft / WorkflowVersion。
Drawio 不能构造 runtime truth。
HTML Report 不能构造 runtime truth。
EventBridge payload 不能构造 runtime truth。
Report Schema 是 read model。
Interaction Orchestrator 不直接写 runtime。
Experience State Machine 是 UX read model。
source=agent 不能执行 mutation。
durable mutation 仍需 user_confirmed=true。
```

## Validation Commands

```text
./.venv/bin/python scripts/v4_unified_reality_check_audit.py -> PASS
./.venv/bin/python scripts/v4_u5e_real_llm_local_document_workflow.py -> PASS
./.venv/bin/python -m pytest tests/test_v4_*.py -q -> PASS, 377 passed, 5 warnings
xmllint --noout docs/design/V4.x/v4_x_headless_current_gap_analysis.drawio -> PASS
```

## Spec Drift Evaluation

Risk: LOW.

U6 did not add new runtime capabilities. It only records a gate review over existing UX-01 to UX-12 evidence and records the human decision to accept three PARTIAL deterministic dev/local scenarios for review.

## False Green Evaluation

Risk: MEDIUM.

UX-12 is LOW false-green risk after real LLM evidence. Overall risk remains MEDIUM because UX-08 / UX-09 / UX-10 retain HIGH false-green risk if overclaimed. The completion claim is therefore limited to dev/local experience baseline ready for review.

## Proceed Decision

```text
V4-U6 is complete with accepted PARTIAL risk.
Do not proceed to production hardening or V5 as if full multi-Agent orchestration, Agent executor, controlled executor, or production-ready external app support had been proven.
```

## No False Green Statement

V4-U6 proves only a unified dev/local experience baseline ready for review. It does not prove complete Workflow Studio, complete AgentTalkWindow, Agent executor, controlled executor readiness, production-ready external app support, full multi-Agent orchestration, or autonomous workflow editing.

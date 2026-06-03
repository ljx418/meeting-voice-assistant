# V4-U6 Unified Experience Gate Plan

文档状态：已执行。V4-U6 通过人工 proceed decision 进入 gate review；UX-08 / UX-09 / UX-10 仍保持 PARTIAL，不升级为 PASS。

允许完成声明：

```text
V4-U6 complete: V4 unified dev/local experience baseline ready for review.
```

声明必须附带：

```text
This does not prove complete Workflow Studio, Agent executor, controlled executor production readiness, production external app support, or full multi-Agent orchestration.
```

## 1. 目标

判断 V4.x 是否可以作为统一 dev/local Headless AI Workflow OS 体验基线。

已记录人工 proceed decision：

```text
UX-08 串行多 Agent 视频工作流仍是 deterministic_devlocal PARTIAL。
UX-09 并行罗马广场讨论仍是 deterministic_devlocal PARTIAL。
UX-10 长时工程任务工作流仍是 deterministic_devlocal PARTIAL。
三者 false-green risk=HIGH。
用户已明确接受这三个 PARTIAL 风险进入 V4-U6 gate review。
这不是把三者改成 PASS，也不证明 full multi-Agent orchestration。
```

## 2. 通过条件

```text
UX-01 到 UX-12 全部有 evidence summary。
无 FAIL / BLOCKED。
PARTIAL 已人工确认并记录 proceed decision。
Runtime Capability Matrix 存在并区分 supported / partial / planned / unsupported。
WorkflowSpec Registry 声明不替代 runtime truth。
Mission Console / Runtime Report / Review Console / Evidence Chain 使用同一 ExperienceStateProjection。
TUI / Command Palette 渲染 ExperienceStateProjection 状态线。
本地技术文档工作流可以实际启动并解析 Markdown 文件。
真实 LLM-backed 总结有 MiniMax 或 OpenAI-compatible provider/model/provider_config_source evidence；无 LLM key 时不得标记 PASS。
Evidence Chain 只读。
Drawio / HTML Report / WorkflowSpec 不构造 runtime truth。
No False Green claim scan 通过。
回归测试通过。
```

## 3. 验收命令

```text
./.venv/bin/python -m pytest tests/test_v4_*.py -q
./.venv/bin/python scripts/v4_unified_reality_check_audit.py
./.venv/bin/python scripts/v4_u5e_real_llm_local_document_workflow.py
xmllint --noout docs/design/V4.x/v4_x_headless_current_gap_analysis.drawio
```

## 3.1 Gate 结果要求

```text
reality-check 可保持 allow_enter_v4_u6=false，因为它表达自动放行门禁。
U6 completion note 必须记录人工 proceed decision。
UX-08 / UX-09 / UX-10 必须继续显示 PARTIAL。
UX-12 必须继续显示 PASS / real_runtime。
```

## 4. 禁止声明

```text
complete Workflow Studio ready
complete AgentTalkWindow ready
Agent executor ready
controlled executor ready
production-ready external app support
full multi-Agent orchestration ready
autonomous workflow editing ready
```

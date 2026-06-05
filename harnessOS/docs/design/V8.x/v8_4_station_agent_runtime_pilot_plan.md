# V8-4 Station Agent Runtime Pilot Plan

文档状态：V8-4 development and acceptance plan / completed for review。

目标：

```text
用本地 Markdown 技术文档总结工作流验证每个 station 独立 Agent。
```

建议 Agent：

```text
MissionAgent
PlannerAgent
ScannerAgent
FolderSummaryAgent
OverviewAgent
QualityAgent
EvidenceAgent
WorkflowExplainerAgent
```

验收：

```text
每个 station 有 Agent run evidence。
每个 Agent 有独立 LLM invocation evidence。
每个 Agent 产物可追踪。
Runtime Report 展示 Agent 状态。
Evidence Chain 展示 Agent context / capability / output / redaction。
```

当前验收结果：

```text
status=PASS
evidence_scope=real_runtime_fixture
station_count=7
agent_descriptor_count=7
provider_invocation_count=4
scanner_actual_read_count=5
claim_scan=PASS
redaction_scan=PASS
evidence_dir=docs/design/V8.x/evidence/v8-4-station-agent-runtime/
```

禁止：

```text
把固定 workflow function 输出写成 Agent-backed。
把 shared provider adapter 写成每站独立 Agent。
```

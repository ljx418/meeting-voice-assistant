# V7-3 Real Data Acceptance Plan

文档状态：V7-3 real-data acceptance contract / external audit draft。本文定义 V7-3 真实数据验收标准。

## 1. Acceptance Goal

V7-3 必须证明用户可以通过 Mission TUI 体验到：

```text
输入自然语言目标
 -> 生成 WorkflowSpec / Diff
 -> 生成 Workflow Blueprint / Drawio
 -> 用户确认
 -> 真实读取本地 Markdown 技术文档
 -> 调用 MiniMax 或 OpenAI-compatible provider
 -> 生成 folder summaries / overview summary / quality report
 -> 查看 Runtime Report / Evidence Chain
```

## 2. Data Source

首选真实路径：

```text
Desktop/技术分享
```

等价 fixture：

```text
tests/fixtures/desktop/技术分享
```

使用 fixture 时必须记录：

```text
fixture_source=true
evidence_scope=real_runtime_fixture
```

禁止：

```text
root scan
home directory scan
parent escape
unbounded full disk scan
unauthorized local folder read
```

## 3. Provider Requirements

默认 provider：

```text
MiniMax
```

允许：

```text
OpenAI-compatible provider explicitly configured by env/dotenv
```

必须记录：

```text
provider
model_ref
provider_config_source
prompt_template_ref
input_artifact_refs
output_artifact_refs
runtime_result_ref
correlation_id
redaction_status
```

不得记录：

```text
raw prompt
raw file content
raw provider payload
raw connector payload
API key
Bearer token
signed URL
raw artifact content in evidence JSON / HTML / logs
```

## 4. PASS Conditions

V7-3 PASS 必须全部满足：

```text
natural_language_goal_generates_workflow_spec=PASS
workflow_spec_schema_valid=PASS
workflow_diff_ready_before_confirmation=PASS
workflow_drawio_xml_valid=PASS
user_confirmation_required_before_run=PASS
source_agent_direct_mutation_denied=PASS
scanner_actual_read_count > 0
provider_invocation_count > 0
folder_summaries_generated=PASS
overview_summary_generated=PASS
quality_report_generated=PASS
runtime_report_generated=PASS
evidence_chain_generated=PASS
redaction_scan=PASS
claim_scan=PASS
```

V7-3 completion allowed only when:

```text
status=PASS
evidence_scope=real_runtime or real_runtime_fixture
runtime_backed=true
fallback_demo_only=false
transcript_only=false
report_only=false
```

## 5. PARTIAL / BLOCKED / FAIL Rules

BLOCKED:

```text
LLM key missing and V7-3 requires real provider evidence.
Authorized folder does not exist.
Folder authorization missing.
Provider unavailable.
scanner_actual_read_count=0.
```

PARTIAL:

```text
WorkflowSpec / Diff / Blueprint generated, but run is not executed.
Runtime report exists but provider invocation evidence is missing.
Fixture path works but real Desktop path is unavailable; human proceed decision required.
fallback_demo_only exists for debug evidence.
```

FAIL:

```text
source=agent executes durable mutation.
user confirmation is bypassed.
raw prompt, raw file content, token, secret or signed URL leaks.
fallback_demo_only is marked PASS.
transcript_only is marked runtime_backed.
WorkflowSpec / Drawio / Report / Evidence constructs runtime truth.
```

## 6. Manual Acceptance Steps

最小人工验收步骤：

```text
1. 打开 V7-3 evidence index.html。
2. 检查 TUI transcript 中存在自然语言目标。
3. 检查状态线包含 UserConfirmed / RuntimeStarted / RuntimeReported / EvidenceRecorded。
4. 打开 workflow.drawio，确认 XML 可打开且只读可视化。
5. 打开 workflow_board.html / quality.html / evidence.html。
6. 检查 local-document-workflow-result.json 中 scanner_actual_read_count > 0。
7. 检查 provider_invocation_count > 0。
8. 检查 evidence_chain.json 中 provider/model/prompt_template_ref/input/output refs 存在。
9. 检查无 raw prompt / raw file content / token / secret 泄露。
10. 确认 allowed claim 未被改写成 production ready 或 complete Workflow Studio。
```

## 7. Evidence Package

V7-3 必须输出：

```text
docs/design/V7.x/evidence/v7-3-workflow-run/
  index.html
  tui-transcript.txt
  workflow.json
  workflow.yaml
  workflow.drawio
  workflow_status.drawio
  workflow_board.html
  artifacts.html
  quality.html
  evidence.html
  local-document-workflow-result.json
  evidence_chain.json
  quality_report.json
  acceptance-data.json
  claims-scan.md
  redaction-scan.md
  result-summary.md
```

## 8. Validation Commands

```text
./.venv/bin/python -m pytest tests/test_v7_3_*.py -q
./.venv/bin/python -m pytest tests/test_v7_*.py -q
./.venv/bin/python -m pytest tests/test_v6_*.py -q
./.venv/bin/python -m pytest tests/test_v5_*.py -q
./.venv/bin/python -m pytest tests/test_v4_u9_final_acceptance.py -q
xmllint --noout docs/design/V7.x/v7_current_gap_analysis.drawio
xmllint --noout docs/design/V7.x/evidence/v7-3-workflow-run/workflow.drawio
```

## 9. No False Green Statement

```text
V7-3 proves only the supported natural-language local Markdown workflow creation and controlled run experience ready for review.
It does not prove arbitrary workflow building, complete Workflow Studio, Agent executor, production controlled executor, production-ready external app support, full multi-Agent orchestration, autonomous workflow editing, production ready or full production GA.
```

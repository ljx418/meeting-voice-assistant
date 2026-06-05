# V7-3 Schema Manifest And Examples

文档状态：V7-3 schema manifest / external audit draft。本文把 V7-3 的 schema、示例数据和生成物命名规则收口为实现合同。

## 1. Purpose

V7-3 实现不得自行推断输出结构。实现必须按本文生成 schema-backed 或 contract-backed artifacts，并在 evidence package 中保留 `evidence_scope`。

## 2. Schema Manifest

V7-3 implementation must use these schema contracts before runtime implementation:

```text
NaturalLanguageGoal.schema.json
WorkflowSpecDraft.schema.json
WorkflowDiff.schema.json
BlueprintLink.schema.json
UserConfirmedRunHandoff.schema.json
LocalDocumentWorkflowRunResult.schema.json
RuntimeReportLink.schema.json
QualityReportLink.schema.json
EvidenceChainLink.schema.json
V73AcceptanceData.schema.json
```

Minimum strictness:

```text
additionalProperties=false
required fields explicit
unknown workflow_kind rejected
source=agent rejected for durable mutation
raw prompt / raw file content / token / secret fields forbidden
```

Current schema files:

```text
docs/design/V7.x/schemas/NaturalLanguageGoal.schema.json
docs/design/V7.x/schemas/WorkflowSpecDraft.schema.json
docs/design/V7.x/schemas/WorkflowDiff.schema.json
docs/design/V7.x/schemas/BlueprintLink.schema.json
docs/design/V7.x/schemas/UserConfirmedRunHandoff.schema.json
docs/design/V7.x/schemas/LocalDocumentWorkflowRunResult.schema.json
docs/design/V7.x/schemas/RuntimeReportLink.schema.json
docs/design/V7.x/schemas/QualityReportLink.schema.json
docs/design/V7.x/schemas/EvidenceChainLink.schema.json
docs/design/V7.x/schemas/V73AcceptanceData.schema.json
```

Current Go / No-Go:

```text
GO: external implementation-readiness audit, test matrix finalization, evidence package skeleton.
CONDITIONAL GO: V7-3 implementation after external audit acceptance.
NO-GO: V7-4 final acceptance, generic natural-language workflow builder, Agent executor, source=agent durable mutation.
```

## 3. Generated File Contract

V7-3 must write:

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

Optional raw directory:

```text
raw/
  mission-state.json
  workflow-diff.json
  user-confirmed-handoff.json
  provider-redacted-summary.json
```

Raw directory name does not allow raw secrets, raw prompts, raw file content, raw connector payloads or signed URLs.

## 4. PASS Example

`acceptance-data.json` minimal PASS:

```json
{
  "stage_id": "V7-3",
  "status": "PASS",
  "evidence_scope": "real_runtime",
  "runtime_backed": true,
  "transcript_only": false,
  "report_only": false,
  "fallback_demo_only": false,
  "user_confirmed": true,
  "source_agent_denied": true,
  "workflow_spec_schema_valid": true,
  "drawio_xml_valid": true,
  "scanner_actual_read_count": 3,
  "provider_invocation_count": 2,
  "claim_scan": "PASS",
  "redaction_scan": "PASS",
  "missing_evidence": [],
  "evidence_refs": [
    "tui-transcript.txt",
    "workflow.json",
    "workflow.drawio",
    "local-document-workflow-result.json",
    "quality_report.json",
    "evidence_chain.json"
  ]
}
```

## 5. BLOCKED Example

`acceptance-data.json` minimal BLOCKED:

```json
{
  "stage_id": "V7-3",
  "status": "BLOCKED",
  "evidence_scope": "blocked",
  "runtime_backed": false,
  "transcript_only": false,
  "report_only": false,
  "fallback_demo_only": false,
  "user_confirmed": true,
  "source_agent_denied": true,
  "workflow_spec_schema_valid": true,
  "drawio_xml_valid": true,
  "scanner_actual_read_count": 0,
  "provider_invocation_count": 0,
  "claim_scan": "PASS",
  "redaction_scan": "PASS",
  "missing_evidence": [
    "authorized Markdown folder read",
    "provider invocation evidence"
  ],
  "blocked_reason": "llm_key_missing"
}
```

## 6. Fallback Demo Example

Fallback evidence is allowed for debugging but cannot satisfy V7-3 completion:

```json
{
  "stage_id": "V7-3",
  "status": "PARTIAL",
  "evidence_scope": "fallback_demo_only",
  "runtime_backed": false,
  "fallback_demo_only": true,
  "scanner_actual_read_count": 3,
  "provider_invocation_count": 0,
  "claim_scan": "PASS",
  "redaction_scan": "PASS",
  "missing_evidence": [
    "real provider invocation evidence"
  ]
}
```

## 7. File-Level Acceptance

```text
workflow.json must include workflow_kind=local_markdown_technical_document_summary.
workflow.yaml must represent the same spec as workflow.json.
workflow.drawio must pass xmllint and remain visualization only.
local-document-workflow-result.json must not include artifact content.
quality_report.json must include scanner_actual_read_count and provider_invocation_count.
evidence_chain.json must include provider/model refs and no raw prompt or raw content.
index.html must not include hidden mutation forms or execution buttons.
```

## 8. No False Green

```text
fallback_demo_only cannot be V7-3 PASS.
transcript_only cannot be runtime_backed.
report_only cannot prove execution.
provider key absence cannot be marked provider-backed PASS.
ready for review must not be summarized as ready.
```

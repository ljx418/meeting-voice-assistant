# V8 Evidence Package Contract

文档状态：V8-0 P0 evidence contract / final acceptance input。

## 1. Evidence Directory

V8 每个阶段应输出：

```text
docs/design/V8.x/evidence/<stage-id>/
```

V8-9 final acceptance should output:

```text
docs/design/V8.x/evidence/final-acceptance/
```

## 2. Common Files

```text
index.html
acceptance-data.json
result-summary.md
claims-scan.md
redaction-scan.md
raw/
screenshots/
logs/
```

## 3. V8-4 Station Agent Evidence

Required:

```text
station-agent-registry.json
station-agent-descriptors.json
agent-context-envelopes.json
agent-invocation-evidence.json
agent-capability-decisions.json
agent-run-results.json
workflow-board.html
agent-evidence.html
workflow.drawio
workflow_status.drawio
```

## 4. V8-6 Terminal Worker Evidence

Required if V8-6 is enabled:

```text
terminal-worker-descriptors.json
terminal-session-policy.json
terminal-transcript.txt
diff-proposal.patch
human-review-handoff.json
workspace-scope-validation.json
command-allowlist-validation.json
```

## 5. V8-9 Final Acceptance Data

Required fields:

```text
status
stage_count
station_count
agent_descriptor_count
workflow_explainer_agent_exists
agent_invocation_count
skill_binding_count
mcp_binding_count
tool_policy_count
source_agent_mutation_denied
terminal_worker_enabled
terminal_worker_scope_pass
claim_scan
redaction_scan
drawio_xml
forbidden_claims
blockers
allowed_claim
forbidden_claims_summary
```

## 6. PASS Rules

```text
station_count == agent_descriptor_count
workflow_explainer_agent_exists=true
source_agent_mutation_denied=PASS
claim_scan=PASS
redaction_scan=PASS
drawio_xml=PASS
blockers=0
```

If terminal_worker_enabled=true:

```text
human_high_risk_decision_recorded=true
terminal_worker_scope_pass=PASS
terminal_transcript_exists=true
diff_capture_exists=true
human_review_handoff_exists=true
```


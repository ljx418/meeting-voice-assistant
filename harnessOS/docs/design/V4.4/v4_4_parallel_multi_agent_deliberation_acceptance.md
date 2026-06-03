# V4.4 Parallel Multi-Agent Deliberation Workflow MVP Acceptance

Required evidence path:

```text
docs/design/V4.4/evidence/parallel-deliberation/
```

Required outputs:

```text
tui-transcript.txt
deliberation_workflow.json
deliberation_workflow.yaml
deliberation_workflow.drawio
deliberation_status.drawio
deliberation_artifact_lineage.drawio
deliberation_report.html
persona_artifacts.html
synthesis.html
evidence.html
runtime-result.json
attempt-history.json
downstream-stale.json
operation-evidence.json
result-summary.md
```

Focused acceptance:

1. Real question fixture is used.
2. Orchestrator and three persona agents exist.
3. Cross-inspiration edges exist.
4. Persona artifacts are generated.
5. Synthesis includes attribution.
6. Contradiction review records disagreement and unresolved risks.
7. Persona rerun requires user confirmation.
8. Persona rerun marks synthesis and contradiction review stale.
9. Downstream continuation requires user confirmation.
10. `source=agent` cannot mutate.
11. Reports are read-only and redacted.


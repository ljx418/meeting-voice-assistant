# V4.6 Agent Workflow Builder UX Acceptance

Required evidence:

```text
docs/design/V4.6/evidence/agent-workflow-builder/
```

Required outputs:

```text
tui-transcript.txt
builder-session.json
workflow-draft-proposal.json
workflow-plan-explanation.json
debug-repair-proposal.json
handoff.json
builder_report.html
result-summary.md
```

Acceptance:

1. Real user request fixture is used.
2. Agent generates clarifying questions.
3. Agent generates workflow draft proposal only.
4. Agent explanation is read-only.
5. Agent debug repair is proposal-only.
6. Handoff opens target panel only and executes nothing.
7. No apply, publish, run, rerun, approval, context, or event mutation is performed by Agent.
8. Evidence is redacted and read-only.


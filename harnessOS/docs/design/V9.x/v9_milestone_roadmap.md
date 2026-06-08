# V9 Milestone Roadmap

文档状态：V9 milestone roadmap / V9-7 production governance evidence-aligned baseline。

## 1. Milestone Table

| Milestone | Stage | Purpose | Evidence Scope | Exit Claim |
| --- | --- | --- | --- | --- |
| M0 | V9-0 | Planning and high-risk boundary gate | planning_gate / complete_for_review | V9-0 complete: high-risk execution planning gate ready for review. |
| M1 | V9-1 | Agent executor safety gate and contract package | real_code_policy_validation / complete_for_review | V9-1 complete: Agent Executor Safety Gate implementation ready for review. |
| M2 | V9-2 | Controlled Agent executor runtime | real_runtime_fixture / complete_for_review | V9-2 complete: limited controlled Agent executor runtime slice ready for review. |
| M3 | V9-3 | Multi-Agent orchestration runtime | real_runtime_fixture / complete_for_review | V9-3 complete: multi-Agent orchestration runtime slice ready for review. |
| M4 | V9-4 | Autonomous coding workflow pilot | real_runtime_fixture / complete_for_review | V9-4 complete: autonomous coding workflow pilot ready for review. |
| M5 | V9-5 | Governed terminal worker expansion | real_runtime_fixture / complete_for_review | V9-5 complete: governed terminal worker expansion ready for review. |
| M6 | V9-6 | Workflow Studio productization | real_runtime_fixture / complete_for_review | V9-6 complete: Workflow Studio productization slice ready for review. |
| M7 | V9-7 | Production governance / evidence hardening and terminal automation gate | real_runtime_fixture / complete_for_review | V9-7 complete: production governance and terminal automation gate ready for review. |
| M8 | V9-8 | Final acceptance | final_acceptance | V9 complete: high-risk Agent execution and workflow productization baseline ready for review. |

## 2. Priority Recommendation

```text
Done: V9-0, V9-1, V9-2, V9-3, V9-4, V9-5, V9-6 and V9-7 have ready-for-review evidence.
Next: V9-8 final acceptance readiness review, not final claim emission.
Finally: V9-8 may aggregate evidence and claim guard only if every stage package and user scenario gate passes.
```

## 3. Exit Criteria

V9 final exit requires:

```text
V9-0..V9-7 evidence packages exist.
All high-risk stages have human proceed decisions.
AgentExecutionEnvelope evidence exists.
Durable mutation invariant evidence exists.
Controlled executor policy decisions exist.
Multi-Agent attempt history and lineage evidence exists.
fan-in / fan-out and failure recovery evidence exists.
Coding workflow diff / test / review evidence exists.
No auto commit / auto push / auto deploy evidence exists.
Terminal worker sandbox evidence exists if V9-5 is enabled.
Studio BFF / browser denylist evidence exists.
No False Green scan PASS.
Redaction scan PASS.
Drawio XML valid.
```

## 4. Remaining Blockers

```text
V9-8 cannot execute from planning docs alone.
V9-8 remains blocked if any required evidence package, user scenario gate, claim scan, redaction scan or drawio XML validation is missing or failing.
```

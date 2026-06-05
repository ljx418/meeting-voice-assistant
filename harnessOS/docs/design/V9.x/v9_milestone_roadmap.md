# V9 Milestone Roadmap

文档状态：V9 milestone roadmap / planning baseline。

## 1. Milestone Table

| Milestone | Stage | Purpose | Evidence Scope | Exit Claim |
| --- | --- | --- | --- | --- |
| M0 | V9-0 | Planning and high-risk boundary gate | planning_gate | V9-0 complete: high-risk execution planning gate ready for review. |
| M1 | V9-1 | Agent executor safety gate and contract package | design_gate / contract_freeze | V9-1 complete: Agent executor safety gate ready for review. |
| M2 | V9-2 | Controlled Agent executor runtime | controlled_runtime_slice | V9-2 complete: controlled Agent execution runtime slice ready for review. |
| M3 | V9-3 | Multi-Agent orchestration runtime | orchestration_runtime_slice | V9-3 complete: multi-Agent orchestration runtime slice ready for review. |
| M4 | V9-4 | Autonomous coding workflow pilot | coding_workflow_pilot | V9-4 complete: autonomous coding workflow pilot ready for review. |
| M5 | V9-5 | Governed terminal worker expansion | terminal_worker_expansion | V9-5 complete: governed terminal worker expansion ready for review. |
| M6 | V9-6 | Workflow Studio productization | studio_productization_slice | V9-6 complete: Workflow Studio productization slice ready for review. |
| M7 | V9-7 | Production governance / evidence hardening and terminal automation gate | high_risk_design_gate | V9-7 complete: production governance and terminal automation gate ready for review. |
| M8 | V9-8 | Final acceptance | final_acceptance | V9 complete: high-risk Agent execution and workflow productization baseline ready for review. |

## 2. Priority Recommendation

```text
First: V9-0, freeze the high-risk PRD and architecture.
Second: V9-1 and V9-2, build safety and controlled Agent execution before expanding capabilities.
Third: V9-3, add orchestration after controlled execution is proven.
Fourth: V9-4 and V9-5, add coding workflow and terminal worker expansion under sandbox.
Fifth: V9-6, productize Studio after runtime boundaries are stable.
Sixth: V9-7, handle production governance, evidence hardening and terminal automation as one high-risk gate.
Seventh: V9-8, aggregate evidence and claim guard.
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
Studio BFF / browser denylist evidence exists if V9-6 is enabled.
No False Green scan PASS.
Redaction scan PASS.
Drawio XML valid.
```

## 4. Remaining Blockers

```text
All V9 runtime stages are planned only.
V9-1 contract audit requires V9-0 acceptance.
V9-1 runtime implementation remains blocked until V9-1 contract package external audit acceptance.
V9-2 implementation requires V9-1 acceptance.
V9-7 implementation requires separate high-risk human decision and accepted governance/evidence hardening spec.
V9-8 cannot execute from planning docs alone.
```

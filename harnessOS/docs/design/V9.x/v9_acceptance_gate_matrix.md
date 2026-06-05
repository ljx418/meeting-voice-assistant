# V9 Acceptance Gate Matrix

文档状态：V9 acceptance control matrix / planning baseline。

| Stage | Entry Gate | Acceptance Gate | Stop Condition |
| --- | --- | --- | --- |
| V9-0 | V8 final baseline accepted as bounded | PRD, architecture, gap, drawio, plan and claim guard accepted | V9-0 claims runtime complete |
| V9-1 | V9-0 accepted | AgentExecutionPolicy, AgentExecutionEnvelope, CapabilityResolver, approval, kill switch, timeout, rollback and evidence contracts accepted | Agent executor ready is claimed |
| V9-2 | V9-1 contract audit accepted, HumanAuthorizationRef contract accepted and human decision recorded | controlled executor slice proves policy decision, approval evidence, durable mutation invariant and redacted execution evidence | source=agent mutates by default or durable mutation runs without user_confirmed=true OR valid human_authorization_ref |
| V9-3 | V9-2 PASS | serial, parallel, fan-in, fan-out, failure recovery, lost worker recovery, attempt history, artifact lineage, producer_agent_id and producer_attempt_id evidence exist | full multi-Agent orchestration is claimed without complete evidence |
| V9-4 | V9-2 / V9-3 PASS | coding workflow produces diff, test, review, fix-loop and evidence with sandbox boundary | auto commit / auto push / auto deploy occurs without approval; automated tooling applies patches, commits, pushes, deploys, or marks review as approval |
| V9-5 | V8-6/V8-7 evidence and new human decision | terminal worker sandbox evidence exists | unrestricted shell is allowed |
| V9-6 | Studio PRD and BFF boundary accepted | Studio UI operates through DTO/BFF and passes browser denylist | Studio directly writes runtime truth |
| V9-7 | production governance / evidence hardening spec and human decision | governance, evidence hardening and terminal automation gate evidence exists | browser/terminal automation runs without credential, approval, evidence and incident boundary |
| V9-8 | V9-0..V9-7 evidence exists | final dashboard, claim scan, redaction scan and drawio XML pass | final claim emitted while any stage is BLOCKED |

## Global Acceptance Requirements

```text
No production ready claim.
No full production GA claim.
No Agent executor ready claim in V9, including final acceptance, unless a separate future readiness gate exists.
No full multi-Agent orchestration ready claim in V9, including final acceptance, unless a separate future readiness gate exists.
No autonomous coding workflow ready claim without sandbox, review and rollback evidence.
No complete Workflow Studio ready claim without separate Studio acceptance.
No unrestricted terminal worker.
No raw secret / raw prompt / raw artifact content leakage.
Durable mutation denied unless user_confirmed=true OR valid human_authorization_ref is present.
source=agent default durable mutation always denied.
```

## Front-Stage Audit Vs Runtime Gates

| Stage | Audit PASS Means | Runtime PASS Requires |
| --- | --- | --- |
| V9-1 | Contract, schema and fixture package accepted | Safety gate validator implemented, negative fixtures exercised, evidence package recorded |
| V9-2 | Controlled executor design accepted | Runtime allowlisted actions execute through policy / authorization / approval / evidence chain |
| V9-3 | Orchestration design accepted | Serial / parallel / fan-in / fan-out runtime evidence with recovery and lineage |
| V9-4 | Coding workflow design accepted | Real sandboxed diff / test / review / fix-loop evidence and no auto commit / push / deploy |

## High-Risk Human Decisions

```text
V9-1 safety gate acceptance
V9-2 controlled Agent executor runtime
V9-4 autonomous coding workflow pilot
V9-5 terminal worker write sandbox
V9-7 production governance / evidence hardening and terminal automation gate
```

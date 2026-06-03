# V4.2 Design Index

Status: V4.2-C controlled runtime MVP complete for dev/local validation.

## Stage Split

V4.2 is split to avoid false-green runtime claims:

1. `V4.2-A Headless Interaction Pivot / Headless 交互转向`
2. `V4.2-B Controlled Runtime Design Gate / 受控运行时设计门禁`
3. `V4.2-C Controlled Runtime MVP / 受控运行时 MVP`

V4.2-A is complete and does not implement generic controlled execution.

V4.2-B is complete as a design gate only and does not implement generic controlled execution.

V4.2-C is complete as a dev/local controlled runtime MVP over the local knowledge workflow fixtures.

## Documents

| File | Purpose |
| --- | --- |
| `v4_2_headless_interaction_pivot_plan.md` | V4.2-A implementation planning scope and acceptance. |
| `v4_2_headless_interaction_pivot_completion_note.md` | V4.2-A completion evidence and validation results. |
| `evidence/headless-interaction/` | Generated V4.2-A WorkflowSpec, TUI transcript, Drawio, HTML reports, and evidence package. |
| `v4_2_b_controlled_runtime_design_gate_contract.json` | Machine-readable V4.2-B controlled runtime design gate contract. |
| `v4_2_b_controlled_runtime_design_gate_plan.md` | V4.2-B design gate plan. |
| `v4_2_b_controlled_runtime_design_gate_acceptance.md` | V4.2-C acceptance standard defined by the V4.2-B gate. |
| `v4_2_b_controlled_runtime_design_gate_audit.md` | PRD, architecture, real-data, and no-false-green audit. |
| `v4_2_b_controlled_runtime_design_gate_completion_note.md` | V4.2-B completion evidence. |
| `v4_2_c_controlled_runtime_mvp_plan.md` | V4.2-C implementation plan. |
| `v4_2_c_controlled_runtime_mvp_acceptance.md` | V4.2-C real-data acceptance standard. |
| `v4_2_c_controlled_runtime_mvp_audit.md` | V4.2-C PRD and architecture audit. |
| `v4_2_c_controlled_runtime_mvp_completion_note.md` | V4.2-C completion evidence. |
| `evidence/controlled-runtime/` | Generated V4.2-C TUI transcript, runtime JSON, Drawio, HTML reports, and evidence package. |

## V4.2-A Boundary

V4.2-A may produce WorkflowSpec, TUI transcript, Drawio files, HTML reports, Thin Web Console observation, and exported evidence packages.

V4.2-A must not claim generic apply, publish, run, station rerun, controlled executor, Agent executor, full Workflow Studio, or production-ready external app support.

Allowed completion claim:

```text
V4.2-A complete: headless interaction baseline ready for local workflow validation.
```

## V4.2-B Boundary

V4.2-B may define the controlled runtime design gate, acceptance standard, audit, and machine-readable contract.

V4.2-B must not add runtime routes, executor workers, generic run/rerun behavior, connector/model invocation, Agent executor, production auth, or production-ready external app support.

Allowed completion claim:

```text
V4.2-B complete: controlled runtime design gate ready for implementation review.
```

## V4.2-C Boundary

V4.2-C may start and rerun the local knowledge workflow through `/bff/v4_2/runtime/*`, record attempt history and downstream stale state, generate runtime evidence, and regenerate Drawio / HTML reports from runtime result.

V4.2-C must not claim Agent executor, controlled executor, production-ready external app support, full multi-Agent orchestration, or complete Workflow Studio.

Allowed completion claim:

```text
V4.2-C complete: controlled runtime MVP ready for dev/local validation.
```

# V2.11 Implementation Package: Coding Agent Actionability

## 1. Goal

Build the first actionable coding-agent layer on top of accepted V2.0-V2.10 project intelligence.

The output must help a Coding Agent decide:

- which files and symbols matter;
- which capabilities and public surfaces may be affected;
- which tests are likely relevant;
- what edit sequence is recommended;
- what evidence or blockers support the recommendation.

## 2. Development Plan

Implement:

- actionability index builder;
- definition/reference graph v1;
- provider abstraction for AST, optional tree-sitter, optional LSP;
- impact analysis builder;
- test mapping builder;
- task-to-edit planner;
- HTTP/MCP/CLI build and read contracts.

The AST provider is mandatory. Tree-sitter and LSP are optional providers and must be reported as `provider_status=unavailable` if not configured.

## 3. Artifact Outputs

```text
coding_agent/actionability/index.json
coding_agent/actionability/definitions.jsonl
coding_agent/actionability/references.jsonl
coding_agent/actionability/test_mapping.jsonl
coding_agent/impact/{impact_id}.json
coding_agent/actionability/task_to_edit_plan_{plan_id}.json
```

## 4. Public Interface Targets

HTTP:

```text
POST /api/workspaces/{workspace_id}/codebases/{codebase_id}/coding-agent/actionability/build
POST /api/workspaces/{workspace_id}/codebases/{codebase_id}/coding-agent/impact
POST /api/workspaces/{workspace_id}/codebases/{codebase_id}/coding-agent/task-plan
GET  /api/workspaces/{workspace_id}/codebases/{codebase_id}/coding-agent/actionability
```

MCP:

```text
knowledge_code_actionability_build
knowledge_code_impact_analyze
knowledge_code_task_plan
knowledge_code_actionability_read
```

CLI:

```text
knowledge code actionability build
knowledge code impact
knowledge code task-plan
knowledge code actionability read
```

## 5. Acceptance Plan

- Focused unit tests for definition/reference graph and test mapping.
- Contract tests for HTTP/MCP/CLI parity.
- Real data_service E2E with three tasks:
  - API behavior change;
  - MCP/CLI capability change;
  - test mapping investigation.
- Large-project E2E with HarnessOS or structured blocker.
- No edge labeled `runtime_call`, `data_flow`, `control_flow`, or `type_inferred`.
- Every recommendation has evidence or `needs_review`.

## 6. Stop Conditions

Stop if implementation requires:

- automatic code mutation;
- runtime command execution;
- accepting token-only matching as actionability evidence;
- claiming full call graph.

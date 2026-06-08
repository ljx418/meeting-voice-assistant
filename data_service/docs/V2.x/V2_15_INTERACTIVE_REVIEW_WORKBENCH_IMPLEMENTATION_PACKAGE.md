# V2.15 Implementation Package: Interactive Review Workbench

## 1. Goal

Provide a readable workbench for humans and agents to inspect coding-agent evidence, risks, blockers, and context exports.

## 2. Development Plan

Implement:

- backend workbench payload;
- HTML review workbench;
- capability graph Mermaid view;
- evidence click-through IDs;
- risk lanes;
- blocker board;
- context export payload.

## 3. Artifact Outputs

```text
coding_agent/workbench/review_workbench.json
coding_agent/workbench/review_workbench.html
coding_agent/workbench/capability_graph.mmd
coding_agent/workbench/context_exports/{export_id}.json
```

## 4. Public Interface Targets

HTTP:

```text
POST /api/workspaces/{workspace_id}/codebases/{codebase_id}/coding-agent/workbench/build
GET  /api/workspaces/{workspace_id}/codebases/{codebase_id}/coding-agent/workbench
GET  /api/workspaces/{workspace_id}/codebases/{codebase_id}/coding-agent/workbench/views/{view_id}
POST /api/workspaces/{workspace_id}/codebases/{codebase_id}/coding-agent/workbench/context-export
```

MCP:

```text
knowledge_code_workbench_build
knowledge_code_workbench_read
knowledge_code_workbench_view
knowledge_code_workbench_context_export
```

CLI:

```text
knowledge code workbench build
knowledge code workbench read
knowledge code workbench view
knowledge code workbench context-export
```

## 5. Acceptance Plan

- HTML and Mermaid render only from persisted workbench payload.
- Every visible node resolves to an artifact ID.
- `needs_review` and blockers are visible.
- No absolute path, secret, or raw traceback appears in public output.
- data_service and HarnessOS workbench outputs are readable and link to evidence.

## 6. Stop Conditions

Stop if:

- frontend or HTML renderer creates facts not present in backend payload;
- blockers are hidden for visual polish;
- graph labels are not escaped;
- context export drops evidence while keeping recommendations.

# V2 Phase 10 Development Plan: Code Knowledge Quality Governance

> Generated before implementation.
> Phase 10 must consume accepted V2.0, Phase 8 DevWiki, and Phase 9 Code Graph artifacts.
> Business code implementation must not start until the companion acceptance plan and audit report have no fatal or major findings.

## 1. Phase Goal

Add code-specific quality governance for V2.1 project intelligence artifacts.

Phase 10 is not a rewrite of existing workspace quality governance. It adds a codebase-scoped quality layer under the code asset artifact tree and exposes controlled feedback, rules, review, plan, and read-time overlay behavior for DevWiki, Code Graph, and Agent Context Pack consumers.

## 2. Scope

In scope:

- Codebase-scoped quality artifacts under `workspace/assets/codebase/{codebase_id}/quality/`.
- Feedback records for V2.1 target types from `docs/V2.x/V2_1_TARGET_PRD.md`.
- Deterministic draft rule generation from feedback.
- Rule review status changes: approve, reject, revoke.
- Quality plan generation that lists impacted targets.
- Read-time overlay metadata for approved rules.
- HTTP/MCP/CLI access through split Phase 10 modules.
- Tests using the real repository and real V2.0/V2.1 artifacts.

Out of scope:

- Mutating original V2.0 fact artifacts.
- Mutating original DevWiki, Graph, or Agent Context Pack artifacts.
- Auto-applying corrections to source code.
- LLM-only quality decisions without evidence or `needs_review`.
- New quality UI beyond backend/API contracts. Frontend is Phase 11.

## 3. Target Artifact Layout

```text
workspace/assets/codebase/{codebase_id}/quality/
  feedback.jsonl
  rules.jsonl
  reviews.jsonl
  plan.json
  summary.json
```

Each artifact includes `schema_version = "v2.1"`, `workspace_id`, `codebase_id`, timestamps, and repo-relative or artifact-relative target references only.

## 4. Target Data Model

### Feedback

Fields:

- `feedback_id`
- `workspace_id`
- `codebase_id`
- `target_type`
- `target_id`
- `action`
- `rule_type`
- `severity`
- `reason`
- `suggested_value`
- `metadata`
- `status`
- `created_at`
- `artifact_ref`

### Rule

Fields:

- `rule_id`
- `workspace_id`
- `codebase_id`
- `rule_type`
- `target_type`
- `target_id`
- `status`
- `source_feedback_ids`
- `action`
- `suggested_value`
- `confidence`
- `created_at`
- `reviewed_at`
- `reviewer`
- `artifact_ref`

### Plan

Fields:

- `plan_id`
- `workspace_id`
- `codebase_id`
- `generated_at`
- `approved_rule_ids`
- `impacted_targets`
- `read_time_overlays`
- `warnings`
- `artifact_ref`

## 5. Target Types

Phase 10 supports:

- `codebase`
- `repo_snapshot`
- `code_file`
- `code_symbol`
- `code_route`
- `code_mcp_tool`
- `code_cli_command`
- `public_surface`
- `capability`
- `devwiki_page`
- `devwiki_section`
- `agent_context_pack`
- `agent_context_item`
- `code_graph_node`
- `code_graph_edge`

Unsupported target types return `UNSUPPORTED_TARGET_TYPE`.

## 6. Rule Types

Phase 10 supports:

- `wrong_summary`
- `missing_evidence`
- `stale_snapshot`
- `wrong_capability_mapping`
- `wrong_surface_mapping`
- `missing_public_surface`
- `doc_code_mismatch`
- `low_confidence_inference`
- `overbroad_agent_context`
- `unsafe_path_exposure`

## 7. Implementation Modules

New modules:

```text
backend/data_service/code_assets/quality/model.py
backend/data_service/code_assets/quality/feedback.py
backend/data_service/code_assets/quality/rules.py
backend/data_service/code_assets/quality/review.py
backend/data_service/code_assets/quality/plan.py
backend/data_service/code_assets/quality/persistence.py
backend/data_service/code_assets/quality/service.py
backend/app/api/v1/code_assets_quality.py
backend/data_service/mcp_code_quality_tools.py
backend/data_service/cli_code_quality.py
backend/tests/test_v2_code_quality_governance.py
```

Existing modules to modify only for thin registration:

- `backend/app/api/__init__.py`
- `backend/data_service/mcp_code_tools.py`
- `backend/data_service/cli_code.py`
- public surface guard and static console contract tests

Forbidden implementation locations for core logic:

- `backend/app/api/v1/data_service.py`
- `backend/data_service/service.py`
- bulk logic in `backend/data_service/__main__.py`

## 8. HTTP / MCP / CLI Interfaces

HTTP:

```text
POST /api/workspaces/{workspace_id}/codebases/{codebase_id}/quality/feedback
GET  /api/workspaces/{workspace_id}/codebases/{codebase_id}/quality/summary
POST /api/workspaces/{workspace_id}/codebases/{codebase_id}/quality/rules/build
POST /api/workspaces/{workspace_id}/codebases/{codebase_id}/quality/rules/{rule_id}/review
POST /api/workspaces/{workspace_id}/codebases/{codebase_id}/quality/plan
```

MCP:

```text
knowledge_code_quality_feedback
knowledge_code_quality_summary
knowledge_code_quality_rules_build
knowledge_code_quality_rule_review
knowledge_code_quality_plan
```

CLI:

```text
knowledge code quality feedback
knowledge code quality summary
knowledge code quality rules build
knowledge code quality rule review
knowledge code quality plan
```

## 9. Read-Time Overlay Design

Approved rules never rewrite original artifacts. Read outputs may include:

- `governed_by`
- `applied_rules`
- `plan_refs`
- `quality_warnings`

Phase 10 must provide overlay helpers that can be consumed by DevWiki, Graph, and Agent Context Pack read paths. Minimal implementation can expose overlay metadata through quality plan and summary; mutation of original target artifacts is forbidden.

## 10. Development Steps

1. Add quality artifact path helpers.
2. Add quality models and validators.
3. Add persistence for feedback, rules, reviews, plan, and summary.
4. Add target resolver against DevWiki, Graph, inventory, symbols, trace, and context artifacts.
5. Add feedback recording service.
6. Add deterministic rule builder from feedback.
7. Add rule review service with approve/reject/revoke.
8. Add plan builder and read-time overlay payload.
9. Add HTTP router.
10. Add MCP tools and registry.
11. Add CLI subcommands under `knowledge code quality`.
12. Add real repository E2E tests and public surface contract updates.

## 11. Stop Conditions

Stop and request human confirmation if:

- Quality implementation requires mutating original DevWiki, Graph, Context Pack, or V2.0 artifacts.
- Target resolution cannot distinguish real targets from arbitrary IDs.
- Rules suppress evidence or hide `needs_review` without a visible plan impact.
- Implementation needs core logic in `backend/app/api/v1/data_service.py` or `backend/data_service/service.py`.
- Real repository E2E cannot produce V2.0/DevWiki/Graph prerequisites.

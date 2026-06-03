# V2 Phase 10 Acceptance Plan: Code Knowledge Quality Governance

> Acceptance uses real repository data.
> Mock-only validation is not sufficient.
> If any fatal or major gate fails, Phase 10 is not accepted.

## 1. Required Inputs

- Accepted V2.0 artifacts for the real repository.
- Accepted Phase 8 DevWiki artifacts.
- Accepted Phase 9 Code Graph artifacts.
- `docs/V2.x/V2_1_TARGET_PRD.md`
- `docs/V2.x/V2_1_TARGET_ARCHITECTURE.md`
- `docs/V2.x/V2_PROJECT_INTELLIGENCE_PHASE_10_DEVELOPMENT_PLAN.md`

## 2. Real Repository Scenario

The E2E test must:

1. Import the current repository as a codebase asset.
2. Build or read V2.0 snapshot, inventory, symbols, trace, overview, and context artifacts.
3. Build or read Phase 8 DevWiki artifacts.
4. Build or read Phase 9 Code Graph artifacts.
5. Record feedback against at least:
   - a DevWiki page
   - a DevWiki section
   - a public surface
   - a capability
   - a code symbol
   - a code graph edge
   - an Agent Context Pack item
6. Build draft quality rules from feedback.
7. Approve one rule, reject one rule, and revoke one previously approved rule.
8. Generate a quality plan.
9. Read quality summary through HTTP, MCP, and CLI.
10. Confirm all public payloads hide absolute repository and workspace paths.

## 3. Artifact Acceptance

Required files:

```text
workspace/assets/codebase/{codebase_id}/quality/feedback.jsonl
workspace/assets/codebase/{codebase_id}/quality/rules.jsonl
workspace/assets/codebase/{codebase_id}/quality/reviews.jsonl
workspace/assets/codebase/{codebase_id}/quality/plan.json
workspace/assets/codebase/{codebase_id}/quality/summary.json
```

Required assertions:

- Each record has `schema_version = "v2.1"`.
- Each feedback has `feedback_id`, `target_type`, `target_id`, `action`, `rule_type`, `severity`, and `artifact_ref`.
- Each rule has `rule_id`, `status`, `source_feedback_ids`, `confidence`, and `artifact_ref`.
- Plan lists `approved_rule_ids`, `impacted_targets`, and `read_time_overlays`.
- Summary counts feedback, draft rules, approved rules, rejected rules, revoked rules, and unresolved targets.

## 4. Immutability Gates

Hash before and after each Phase 10 operation:

- V2.0 source artifacts:
  - `snapshot.json`
  - `files.jsonl`
  - `surfaces.jsonl`
  - `capabilities.jsonl`
  - `symbols.jsonl`
  - `imports.jsonl`
  - `evidence.jsonl`
  - `overview.json`
  - `agent_context/*.json`
- Phase 8 DevWiki artifacts:
  - `devwiki/index.json`
  - `devwiki/pages/*.json`
  - `devwiki/pages/*.md`
- Phase 9 Graph artifacts:
  - `graph/*/graph.json`
  - `graph/*/nodes.jsonl`
  - `graph/*/edges.jsonl`
  - `graph/*/summary.json`
  - `graph/*/mermaid/*.mmd`

Acceptance requires all hashes unchanged after feedback, rule build, review, revoke, and plan generation.

## 5. Target Resolution Gates

The quality service must verify target IDs against persisted artifacts.

Required positive target resolution:

- `devwiki_page`
- `devwiki_section`
- `public_surface`
- `capability`
- `code_symbol`
- `code_graph_node`
- `code_graph_edge`
- `agent_context_pack`
- `agent_context_item`

Required negative tests:

- Unknown target returns a structured error.
- Unsupported target type returns `UNSUPPORTED_TARGET_TYPE`.
- Unsupported rule type returns `UNSUPPORTED_RULE_TYPE`.
- Revoked rules do not appear in active read-time overlays.

## 6. Read-Time Overlay Gates

Approved rules must be visible as overlay metadata without rewriting source artifacts.

Required assertions:

- Approved rule appears in `plan.json`.
- Approved rule appears in read-time overlay payload.
- Rejected rule does not appear in active overlays.
- Revoked rule is removed from active overlays but remains auditable in `rules.jsonl` and `reviews.jsonl`.
- Overlay payload includes `governed_by` or `applied_rules`.
- Plan impacted targets match real persisted targets.

## 7. HTTP / MCP / CLI Gates

HTTP:

- `POST /api/workspaces/{workspace_id}/codebases/{codebase_id}/quality/feedback`
- `GET /api/workspaces/{workspace_id}/codebases/{codebase_id}/quality/summary`
- `POST /api/workspaces/{workspace_id}/codebases/{codebase_id}/quality/rules/build`
- `POST /api/workspaces/{workspace_id}/codebases/{codebase_id}/quality/rules/{rule_id}/review`
- `POST /api/workspaces/{workspace_id}/codebases/{codebase_id}/quality/plan`

MCP:

- `knowledge_code_quality_feedback`
- `knowledge_code_quality_summary`
- `knowledge_code_quality_rules_build`
- `knowledge_code_quality_rule_review`
- `knowledge_code_quality_plan`

CLI:

- `knowledge code quality feedback`
- `knowledge code quality summary`
- `knowledge code quality rules build`
- `knowledge code quality rule review`
- `knowledge code quality plan`

Required convergence:

- HTTP/MCP/CLI agree on `workspace_id`, `codebase_id`, counts, rule IDs, plan ID, active approved rule IDs, warnings, and unresolved target counts.

## 8. Regression Gates

Required commands:

```bash
python3 -m pytest backend/tests/test_v2_code_quality_governance.py -q
python3 -m pytest backend/tests/test_v2_devwiki_baseline.py backend/tests/test_v2_code_graph_baseline.py backend/tests/test_v2_agent_context_pack.py -q
python3 -m pytest backend/tests/test_public_surface_guard.py backend/tests/test_data_service_mcp.py -q
npm run build --prefix frontend
python3 -m pytest backend/tests -q
git diff --check -- .
```

## 9. False Acceptance Rejection

Reject Phase 10 if:

- Only unit tests pass without a real repository E2E.
- Feedback accepts arbitrary target IDs as valid.
- Rule build produces no rules but reports success.
- Approved rules mutate source artifacts.
- Plan omits impacted targets.
- Revoked rules still affect active overlays.
- HTTP passes but MCP or CLI is not tested.
- Absolute paths appear in public payloads.
- Existing V1/V2.0/Phase 8/Phase 9 tests regress.

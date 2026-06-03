# V2 Phase 11 Acceptance Plan: Minimum Read-only Frontend

> Acceptance uses real backend payloads or deterministic fixtures captured from real backend payloads.
> Frontend-only mock success is not sufficient.

## 1. Required Inputs

- Accepted Phase 8 DevWiki.
- Accepted Phase 9 Code Graph.
- Accepted Phase 10 Code Quality Governance.
- Existing Knowledge Console frontend.

## 2. Functional Acceptance

The frontend must provide a read-only Project Intelligence view that can display:

- selected workspace/codebase identity
- DevWiki page count, stale state, needs-review count, and page detail
- Code Graph node/edge counts, unsupported edge count, stale state, and Mermaid export
- Code Quality feedback/rule/approved/rejected/revoked counts and plan impacted targets
- Agent Context Pack summary/readback if a pack is selected
- backend-provided `evidence`, `needs_review`, `unresolved`, `stale`, `applied_rules`, and `governed_by`

## 3. Non-Authority Gates

Frontend must not:

- calculate authoritative graph node count locally from Mermaid text
- calculate authoritative evidence count from visible snippets
- calculate quality status locally
- calculate page confidence locally
- hide backend `needs_review`, `unresolved`, or `stale`
- mutate artifacts

## 4. Error-State Acceptance

The UI must show useful states for:

- no codebase
- missing DevWiki
- missing Code Graph
- missing Quality summary
- stale DevWiki or Graph
- backend structured errors

## 5. Build and Regression Gates

Required commands:

```bash
npm run build --prefix frontend
python3 -m pytest backend/tests/test_console_governance_evidence_plan.py -q
python3 -m pytest backend/tests/test_public_surface_guard.py backend/tests/test_v2_code_quality_governance.py -q
python3 -m pytest backend/tests -q
git diff --check -- .
```

If visual validation tooling is available, capture a screenshot of `/knowledge` and verify:

- Project Intelligence section is visible.
- Text does not overlap at desktop width.
- `needs_review` / `stale` / `unresolved` signals are visible when present in payload.

## 6. False Acceptance Rejection

Reject Phase 11 if:

- only a static mock panel is added
- backend API integration is absent
- UI hides risk signals
- frontend becomes an editor
- frontend build fails
- public surface or backend regression tests fail
- UI text is unreadable or overlapping

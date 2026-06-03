# V2 Remaining Audit Checklist

> Use this checklist before and after every remaining V2 phase.
> A phase cannot enter implementation while any `fatal` or `major` item remains open.

## 1. Documents To Audit

These documents define the next-stage audit baseline:

- `docs/V2.x/V2_PROJECT_INTELLIGENCE_PRD.md`
- `docs/V2.x/V2_PROJECT_BASELINE.md`
- `docs/V2.x/V2_PROJECT_INTELLIGENCE_REMAINING_DEVELOPMENT_PLAN.md`
- `docs/V2.x/V2_PROJECT_INTELLIGENCE_REMAINING_ACCEPTANCE_PLAN.md`
- `docs/V2.x/V2_PROJECT_INTELLIGENCE_REMAINING_GOVERNANCE_PLAN.md`

For each concrete phase, also audit:

- `docs/V2.x/V2_PROJECT_INTELLIGENCE_PHASE_{N}_DEVELOPMENT_PLAN.md`
- `docs/V2.x/V2_PROJECT_INTELLIGENCE_PHASE_{N}_ACCEPTANCE_PLAN.md`
- `docs/V2.x/V2_PROJECT_INTELLIGENCE_PHASE_{N}_AUDIT_REPORT.md`

## 2. Pre-Implementation Audit

| Check | Severity If Failed | Evidence Required |
|---|---|---|
| Phase goal maps to PRD user stories and FRs. | major | PRD section references |
| Phase has explicit non-goals. | major | development plan |
| Phase uses current repo as real acceptance data. | major | acceptance plan |
| Phase artifacts live under `workspace/assets/codebase/{codebase_id}/`. | major | artifact layout |
| Phase does not mutate source registry schema. | fatal | code/design review |
| Phase does not add V2 core routes to `backend/app/api/v1/data_service.py`. | major | file change plan |
| Phase does not add V2 core logic to `backend/data_service/service.py`. | major | file change plan |
| Phase does not add substantial CLI logic to `backend/data_service/__main__.py`. | major | file change plan |
| Phase 7 context pack is split into focused context modules, not a single giant service. | major | file change plan |
| HTTP/MCP/CLI exposure is defined or explicitly deferred. | major | interface table |
| Failure paths are listed. | major | acceptance plan |
| Path/privacy policy is listed. | fatal | security notes |
| False acceptance risks are listed. | major | audit report |

## 3. Post-Implementation Audit

| Check | Severity If Failed | Evidence Required |
|---|---|---|
| Unit tests pass. | major | command output |
| Real repo E2E passes. | fatal | command output + artifact paths |
| Artifact files exist and were inspected. | major | artifact path list |
| Phase audit report lists all changed files. | major | changed-file list |
| HTTP/MCP/CLI contract tests pass for exposed features. | major | command output |
| V1 regression tests pass. | major | command output |
| Frontend build passes if frontend contract changed. | major | `npm run build --prefix frontend` |
| Public output uses repo-relative paths. | fatal | path leak tests |
| Evidence line ranges are real when claimed. | fatal | sampled file/line proof |
| Unresolved facts are marked unresolved/needs_review. | major | artifact sample |
| `lifecycle/sources.json` is unchanged by V2 codebase artifact generation. | fatal | before/after comparison |
| No unsupported claims such as full call graph or data flow. | major | docs/API output review |

## 4. Architecture Gate Checklist

Treat these as automatic gates in every phase audit:

- Any change to `backend/app/api/v1/data_service.py` is `major` by default and needs explicit human approval, except a narrowly justified router import/bootstrap change.
- Any change to `backend/data_service/service.py` is `major` by default and needs explicit human approval.
- `backend/data_service/__main__.py` should only mount CLI command groups; new V2 behavior belongs in `backend/data_service/cli_code.py` or focused helpers.
- V2 codebase artifacts must not create, mutate, or depend on existing source registry entries in `lifecycle/sources.json`.
- Phase 7 must not concentrate ranking, rendering, token budgeting, evidence selection, and persistence in one large `context_pack.py`; split into focused context modules.

## 5. False Acceptance Risk Checklist

Mark a phase as failed if any of these are true:

- Tests only use mocks and no real `data_service` repo.
- Tests only check status code and do not inspect artifacts.
- Snapshot/inventory/symbol/mapping artifacts are generated but not read back.
- HTTP passes but MCP/CLI are not tested despite being in scope.
- Evidence output has file names but no line ranges where line ranges are claimed.
- Tests accept empty lists as success for required inventory/symbol results.
- LLM-generated summary is accepted without evidence or `needs_review`.
- Absolute paths are allowed in public responses because a test fixture expected them.
- Existing V1 tests are skipped to make V2 green.
- Frontend contract changes are made without a frontend build.

## 6. Human Stop Gates

Stop and ask for human review if:

- A phase requires changing V1 public behavior.
- A phase requires scanning outside allowed roots.
- A phase cannot satisfy real repo acceptance after two implementation attempts.
- Generated evidence cannot be traced to stable source files.
- Performance on the current repo is visibly too slow for the 5,000 file / 100k LOC MVP target.
- The implementation needs new external services or network access not present in the PRD.
- Worktree contains unrelated changes that cannot be cleanly separated for commit/review.

## 7. Suggested Audit Questions

1. Does this phase produce deterministic facts before any LLM synthesis?
2. Can an external agent call the feature without reading local implementation details?
3. Can every important conclusion be traced to source evidence?
4. Is the codebase asset still independent from source registry?
5. Are HTTP/MCP/CLI capabilities aligned or is the gap explicit?
6. Does the phase make future phases easier, or create another high-coupling center?
7. Would this implementation work on a larger repo, or only on this fixture?

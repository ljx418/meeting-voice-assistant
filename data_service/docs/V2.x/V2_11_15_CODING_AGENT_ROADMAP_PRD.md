# V2.11-V2.15 PRD: Coding Agent Actionability Roadmap

## 1. Product Positioning

V2.11-V2.15 extends Project Intelligence from "project understanding and evidence governance" into "coding-agent actionability".

The current accepted baseline can import repositories, build snapshots, extract architecture/document/code evidence, produce reports, and generate context packs. The remaining gap for a code assistant is that it can understand and review a project, but it cannot yet reliably plan edits, reason about change impact, map tests, use runtime evidence, or maintain incremental project memory.

This roadmap keeps the same evidence-first rule:

> Code assistant outputs must be grounded in persisted facts, line-level evidence, structured blockers, or explicit `needs_review`. The service must not silently convert weak inference into accepted implementation guidance.

## 2. Users

- External Coding Agent
- Maintainer
- Code Reviewer
- Architecture Reviewer
- Documentation Agent
- Test Agent

## 3. Scope Summary

| Stage | Name | Product Goal |
| --- | --- | --- |
| V2.11 | Coding Agent Actionability Layer | Turn project intelligence into actionable development planning inputs. |
| V2.12 | Safe Patch Planning | Generate evidence-backed patch plans without directly mutating code. |
| V2.13 | Controlled Runtime Evidence | Add allowlisted runtime/test/log evidence as a separate evidence layer. |
| V2.14 | Incremental Intelligence | Maintain project intelligence incrementally across snapshots and tasks. |
| V2.15 | Interactive Review Workbench | Provide a readable, evidence-linked workbench for humans and agents. |

## 4. V2.11 Coding Agent Actionability

### Goal

Let an external Coding Agent ask "how should I approach this task?" and receive files, symbols, capabilities, likely tests, risks, and evidence.

### In Scope

- LSP/tree-sitter/AST hybrid indexing baseline.
- Definition/reference graph v1.
- Diff-aware impact analysis.
- Task-to-edit planning.
- Test mapping.
- Evidence-backed actionability report.
- HTTP/MCP/CLI read and build contracts.

### Out of Scope

- Automatic code edits.
- Runtime command execution.
- Full call graph.
- Data flow, control flow, type inference.
- All-language semantic parity.

## 5. V2.12 Safe Patch Planning

### Goal

Generate safe, evidence-backed patch plans that a Coding Agent or human can review before editing.

V2.12 turns the accepted V2.11 actionability layer into a reviewable patch planning layer. It must produce concrete candidate edit regions, patch options, validation plans, rollback scopes, readiness signals, and blockers, but it must remain strictly read-only. A V2.12 result is not a patch application, not a commit, and not proof that an edit is safe to apply without review.

### In Scope

- Patch plan schema.
- Candidate edit regions.
- Multi-option edit plans.
- Validation command plan.
- Rollback plan.
- Patch readiness score.
- Evidence and `needs_review` per edit recommendation.
- HTTP/MCP/CLI create and read contracts for persisted patch plans.
- Large-project structured blockers when safe patch planning cannot identify enough line-level evidence.

### Out of Scope

- Applying patches automatically.
- Committing or pushing code.
- Editing files without explicit future authorization.
- Running validation commands. V2.12 plans commands; V2.13 controls execution.
- Treating a patch plan as an accepted code review.

### Minimum Public Contract

- HTTP create: `POST /api/workspaces/{workspace_id}/codebases/{codebase_id}/coding-agent/patch-plans`
- HTTP read: `GET /api/workspaces/{workspace_id}/codebases/{codebase_id}/coding-agent/patch-plans/{patch_plan_id}`
- MCP: `knowledge_code_patch_plan_create`, `knowledge_code_patch_plan_read`
- CLI: `knowledge code patch-plan create`, `knowledge code patch-plan read`

### Completion Definition

V2.12 is complete only when real `data_service` tasks generate persisted patch plans with candidate edits, validation commands, rollback plans, readiness status, evidence or `needs_review` on every recommendation, HTTP/MCP/CLI parity, and a no-source-mutation audit. A large-project run must either generate a usable plan or persist exact blockers.

## 6. V2.13 Controlled Runtime Evidence

### Goal

Safely collect runtime/test/log evidence under allowlisted execution rules.

### In Scope

- Allowlisted command registry.
- Test command discovery.
- Test execution result artifacts.
- Runtime smoke descriptors for HTTP/MCP/CLI.
- Log capture and redaction.
- Runtime evidence alignment to static facts.

### Out of Scope

- Arbitrary command execution.
- Production environment execution.
- Secret-bearing logs in public payloads.
- Treating runtime evidence as a replacement for source evidence.

## 7. V2.14 Incremental Intelligence

### Goal

Move from one-shot project intelligence to sustainable, incremental project knowledge maintenance.

### In Scope

- Incremental snapshot diff.
- Changed file/symbol/surface/doc claim detection.
- Artifact version diff.
- Drift timeline.
- Task memory.
- Historical quality trend.
- Incremental rebuild report.

### Out of Scope

- Perfect semantic incremental build.
- Full Git history mining.
- Cross-repository federation.

## 8. V2.15 Interactive Review Workbench

### Goal

Make architecture and coding-agent evidence easy for humans to inspect, navigate, and export.

### In Scope

- HTML review workbench.
- Capability -> surface -> symbol -> file -> test graph.
- Evidence click-through.
- Risk lane and blocker board.
- Task context export.
- Architecture diff view.
- Review queue actions.

### Out of Scope

- Frontend as a source of truth.
- Free-form graph editing.
- Auto rewriting source documents or code.

## 9. Global Non-Goals

Across V2.11-V2.15 the project must not claim:

- Complete architecture intent recovery from code.
- Full static analysis.
- Full call graph.
- Runtime topology inference.
- Data flow or control flow analysis.
- Type inference.
- Autonomous code modification.
- Autonomous PR creation.

## 10. Completion Definition

The roadmap is complete only when each stage has:

- Stage-specific PRD/spec review.
- Real data_service E2E.
- Real HarnessOS or other large-project E2E where applicable.
- HTTP/MCP/CLI contract parity.
- Artifact inspection.
- False-green audit.
- Closure audit with no open fatal or major findings.

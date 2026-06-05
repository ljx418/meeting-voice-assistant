# V2.10 Target PRD: Generic Architecture Pattern Evidence Adapters

## 1. Positioning

V2.10 extends V2.9's evidence-hardening layer with a generic architecture pattern adapter system for large and framework-diverse projects.

V2.10 is not a HarnessOS-only patch. HarnessOS is one acceptance target because it exposed V2.9's blocker: architecture surfaces were detected, but deterministic line ranges were missing. The product goal is to support similar large projects that expose architecture through workflow registries, CLI/TUI consoles, adapter registries, agents, workers, manifests, or mixed documentation-code conventions.

## 2. Problem

V2.9 can reject false acceptance correctly, but large projects may still produce:

```text
surface candidates found
line_range missing
accepted_evidence = 0
structured blocker = LINE_RANGE_INVALID
```

This happens when public/architecture-facing surfaces are not plain FastAPI routes, MCP tools, or argparse commands. Large projects often expose capability through:

- registry dictionaries and lists;
- decorator-based workflow registration;
- class inheritance conventions;
- console/TUI command tables;
- agent/worker registries;
- external app adapter catalogs;
- YAML/JSON/TOML manifests;
- dynamic imports or factory functions;
- architecture documents that name concepts before code evidence is located.

## 3. Goals

1. Provide a generic Architecture Pattern Adapter Registry.
2. Add Python AST binding for registry assignments, decorators, class inheritance, call expressions, and manifest references.
3. Add optional definition lookup support through local, free, open-source tools.
4. Keep document claims separate from code facts while improving doc-code evidence matching.
5. Support optional project-provided architecture manifests without making them mandatory.
6. Support optional controlled runtime introspection contracts, but do not require running arbitrary projects.
7. Improve accepted line-level evidence for HarnessOS and at least one additional real project or real-project-style fixture.
8. Preserve V2.9 false-green rules: no accepted evidence without true source file and line range.

## 4. Non-Goals

- Do not build a full call graph.
- Do not infer runtime topology from imports.
- Do not do data-flow, control-flow, or type inference.
- Do not make HarnessOS-specific logic the default behavior.
- Do not run untrusted project commands by default.
- Do not mark manifest-only or document-only claims as accepted code evidence.
- Do not require cloud providers.

## 5. User Stories

### US-101: Generic Pattern Adapter Discovery

As an architecture reviewer, I want the service to identify which architecture surface patterns are present in a repo so that evidence extraction is explainable.

Acceptance:

- Reports attempted adapters.
- Reports matched adapters.
- Reports unsupported patterns as structured blockers.
- No project-specific adapter can run unless explicitly selected or matched by generic rules.

### US-102: Registry and Decorator Binding

As a maintainer, I want workflow/adapter/agent registries to be resolved to source code definitions and line ranges.

Acceptance:

- Registry keys, decorator names, class definitions, and handler symbols are linked.
- Accepted evidence has repo-relative path and valid line range.
- Dynamic or unresolved entries remain `needs_review`.

### US-103: Definition Lookup Enhancement

As a coding agent, I want symbol references from registries to resolve across files.

Acceptance:

- Local definition lookup can resolve imported symbols.
- If lookup tooling is unavailable, the system returns `DEFINITION_LOOKUP_UNAVAILABLE`.
- Token/string matching alone never produces accepted evidence.

### US-104: Document Claim to Code Evidence Matching v3

As an architecture reviewer, I want document concepts like "Terminal Worker" or "Workflow Plane" to be matched to code evidence when possible.

Acceptance:

- Document claim remains a document claim.
- Code evidence is accepted only with source file and line range.
- Matched, weak_match, missing_code_evidence, and code_not_documented are distinct statuses.

### US-105: Optional Architecture Manifest

As a project owner, I want to provide a machine-readable architecture manifest to improve extraction.

Acceptance:

- Manifest is schema validated.
- Manifest entries must bind to real code line ranges before accepted.
- Invalid manifest entries produce structured errors, not accepted evidence.

### US-106: Controlled Runtime Introspection

As a project owner, I want to optionally provide safe commands that list workflows, agents, adapters, or consoles.

Acceptance:

- Runtime introspection is off by default.
- Only allowlisted commands run.
- Output is treated as candidate evidence until statically bound to line ranges.

## 6. Success Metrics

- HarnessOS `LINE_RANGE_INVALID` blocker count decreases.
- HarnessOS accepted evidence count becomes greater than zero or produces more precise non-line-range blockers.
- At least three generic adapter types are accepted on real repos or realistic fixtures.
- Accepted evidence truth sampling passes.
- No full-call-graph or runtime-flow claim appears.
- Public report shows adapter attempts, matches, blockers, and confidence.

## 7. Completion Definition

V2.10 is complete when:

1. Pattern adapter registry exists and is configurable.
2. AST binding resolves registry/decorator/class/function patterns to line ranges.
3. Definition lookup is integrated or gracefully unavailable.
4. Manifest and runtime-introspection contracts are documented and safely gated.
5. data_service and HarnessOS run through real E2E.
6. HarnessOS result improves from V2.9 or records more precise blockers.
7. Public HTML/JSON/Context Pack explain adapter results and evidence.
8. Closure audit has no open fatal or major false-acceptance finding.

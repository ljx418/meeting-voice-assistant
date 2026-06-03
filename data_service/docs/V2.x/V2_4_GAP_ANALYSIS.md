# V2.4 Gap Analysis: Code-Derived Architecture Inference

> Scope: gap from current V2.3 architecture abstraction to V2.4 code-derived architecture inference.
> Business code was not modified by this document.

Date: 2026-06-02

## 1. Summary

Current V2.3 can parse architecture sources and align documented design elements to code facts. The remaining gap is that the service cannot yet derive an architecture model from code alone.

This gap explains why a generated project structure graph can differ significantly from a human Drawio architecture diagram: the current graph reflects files, surfaces, symbols, and document-alignment matches, while the human diagram usually contains higher-level product planes, bounded contexts, runtime concepts, governance stages, and intended architecture relationships.

V2.4 closes that gap by adding code-derived roles, layers, boundaries, pattern candidates, and design-code drift findings.

## 2. Current Capabilities

Confirmed current capability areas:

- Codebase registry, snapshot, inventory, symbols, trace, overview, and context pack from V2.0.
- DevWiki, Code Graph, Quality Governance, and read-only project intelligence presentation from V2.1.
- Architecture source scanning and design-side model build from V2.3.
- Drawio and Markdown parsing for architecture sources.
- Design-code alignment using available code graph/code facts.
- HTML/Mermaid architecture view generation.

Representative implementation files:

- `backend/data_service/code_assets/architecture/drawio_parser.py`
- `backend/data_service/code_assets/architecture/markdown_parser.py`
- `backend/data_service/code_assets/architecture/model_builder.py`
- `backend/data_service/code_assets/architecture/aligner.py`
- `backend/data_service/code_assets/architecture/findings.py`
- `backend/data_service/code_assets/architecture/renderer.py`
- `backend/data_service/code_assets/architecture/service.py`

## 3. Gaps

| Gap | Current State | V2.4 Target |
| --- | --- | --- |
| Code-derived architecture roles | Not yet a first-class artifact | `code_roles.jsonl` with role type, signals, evidence, confidence |
| Code-derived layers | Not yet inferred from code | `code_layers.jsonl` grouping interface/application/domain/infrastructure/governance/runtime/artifact/test/docs |
| Architecture boundaries | Existing graph has code relationships but not architecture boundaries | `code_boundaries.jsonl` for package, adapter, storage, governance, and public-surface boundaries |
| Pattern candidates | Not explicitly detected as architecture patterns | `pattern_candidates.jsonl` for FastAPI router, MCP registry, CLI group, artifact store, quality gate, DevWiki, Code Graph, Context Pack |
| Code-derived architecture model | No aggregate model from code alone | `code_derived_model.json` |
| Design-code drift | V2.3 design-code findings exist but do not compare design model to a separate code-derived model | `design_code_drift.jsonl` |
| HarnessOS architecture abstraction | Existing generated HTML can show structure but not enough high-level architecture planes | Code-derived roles/layers plus comparison to V2.3 design-side planes |
| Agent-facing architecture summary | Existing overview/context can mention architecture but lacks architecture inference artifacts | HTTP/MCP/CLI reads for roles, patterns, drift, and views |

## 4. Why Current Graphs Differ from Human Architecture Diagrams

The current generated graph is fact-oriented:

- files
- modules
- symbols
- public surfaces
- explicit graph edges
- documented design nodes when architecture sources exist

Human Drawio architecture diagrams are intent-oriented:

- product planes
- runtime layers
- bounded contexts
- governance concepts
- future-state relationships
- design constraints that may not have direct code symbols

Without V2.4, the service cannot reliably promote file/module facts into architecture roles or compare them to design intent. V2.3 alignment can identify overlaps, but it cannot fully reconstruct the intended architecture from code alone.

## 5. Required V2.4 Additions

### Role Classifier

Input:

- public surfaces
- symbols
- graph nodes/edges
- file paths
- module names
- persistence artifacts

Output:

- role records with signals, evidence, confidence, and `needs_review`.

### Layer Inferer

Input:

- roles
- dependency direction where deterministic
- package/module names
- public-surface ownership

Output:

- architecture layers and members.

### Boundary Inferer

Input:

- package structure
- graph edges
- role clusters
- public-surface ownership

Output:

- boundary records and possible boundary leaks.

### Pattern Detector

Input:

- route/MCP/CLI inventories
- persistence modules
- graph/devwiki/quality/context artifacts

Output:

- architecture pattern candidates.

### Drift Analyzer

Input:

- V2.3 design-side model
- V2.4 code-derived model

Output:

- drift findings with evidence and confidence.

## 6. Risks

| Risk | Severity | Mitigation |
| --- | --- | --- |
| Heuristic role classifier overclaims architecture | high | Require evidence, signals, confidence, and `needs_review`; low confidence cannot be accepted as fact |
| Code-derived model pretends to be human design intent | high | Keep design-side and code-derived model separate |
| HarnessOS validation repeats Drawio labels instead of code facts | high | Build code-derived model without design sources as an explicit E2E gate |
| Generated HTML shows facts absent from artifacts | high | Render only from persisted V2.4 artifacts |
| Pattern detection becomes full static analysis | medium | Forbid full call graph/data flow/control flow/type inference |
| Prior artifacts are mutated | medium | Hash-gate V2.0/V2.1/V2.3 artifacts |

## 7. Open Questions for Human Review

- Should V2.4 closure require HarnessOS seven-plane architecture matching as a hard gate or only as a review sample?
- Should V2.4 expose low-confidence role suggestions to Agent Context Pack immediately?
- What threshold is acceptable for architecture role coverage in multi-language repositories?
- Should pattern taxonomy be user-configurable in V2.4, or fixed until V2.5?

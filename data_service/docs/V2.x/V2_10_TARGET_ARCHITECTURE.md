# V2.10 Target Architecture: Generic Pattern Adapter Layer

## 1. Architecture Summary

V2.10 adds a pattern adapter layer between V2.9 surface candidates and accepted line-level evidence.

```text
V2.0-V2.9 artifacts
  -> Pattern Adapter Registry
  -> Generic AST Binding Engine
  -> Optional Definition Lookup
  -> Optional Manifest Resolver
  -> Optional Runtime Introspection Candidate Importer
  -> Evidence Acceptance Gate
  -> V2.10 Pattern Evidence Report
  -> V2.9 Evidence / Relationship / Report / Context Pack consumers
```

## 2. Core Components

### 2.1 Pattern Adapter Registry

Responsible for registering generic architecture surface patterns:

- `python_registry_assignment`
- `python_decorator_registration`
- `python_class_inheritance`
- `python_factory_call`
- `cli_parser_registration`
- `tui_command_table`
- `workflow_manifest`
- `agent_worker_registry`
- `adapter_catalog`
- `external_app_registry`
- `architecture_manifest`
- `runtime_introspection_candidate`

Each adapter declares:

```text
adapter_id
adapter_type
language
supported_file_globs
match_strategy
accepted_evidence_policy
confidence_policy
unsupported_claims
```

### 2.2 AST Binding Engine

Uses Python AST to locate:

- assignments;
- dictionary/list entries;
- decorators;
- class definitions;
- function definitions;
- call expressions;
- import aliases;
- module-level constants.

It emits candidate bindings:

```text
surface candidate
-> registry/decorator/manifest location
-> symbol reference
-> definition candidate
-> line range
```

### 2.3 Definition Lookup Provider

Local provider abstraction for symbol definition resolution.

Preferred local/free choices:

- AST import resolver as default.
- Jedi as optional Python provider.
- tree-sitter as optional multi-language parser.
- Pyright/BasedPyright output as optional future source.

Provider unavailability is not fatal. It returns:

```text
DEFINITION_LOOKUP_UNAVAILABLE
```

### 2.4 Architecture Manifest Resolver

Reads optional project-provided manifests:

```text
architecture.manifest.json
architecture.yaml
docs/architecture.manifest.json
```

Manifest entries are candidates until bound to code. A manifest cannot independently create accepted code evidence.

### 2.5 Runtime Introspection Candidate Importer

Optional, controlled, off by default.

Projects may declare allowlisted commands such as:

```text
project list-workflows --json
project list-agents --json
```

Runtime output is treated as candidate surface inventory. It must still be statically resolved to source line ranges.

### 2.6 Evidence Acceptance Gate

Accepted evidence requires:

- repo-relative path;
- valid source file;
- valid line range;
- truth check can read source lines;
- accepted adapter policy;
- confidence >= threshold;
- no blocking `needs_review`.

## 3. Artifact Layout

```text
workspace/assets/codebase/{codebase_id}/architecture/v2_10/
  pattern_adapter_registry.json
  adapter_attempts.jsonl
  adapter_matches.jsonl
  definition_lookup_results.jsonl
  manifest_candidates.jsonl
  runtime_introspection_candidates.jsonl
  accepted_pattern_evidence.jsonl
  pattern_blockers.jsonl
  pattern_evidence_summary.json
  views/
    architecture_pattern_evidence_report.html
    architecture_pattern_adapter_map.mmd
  context/
    {pack_id}.json
```

## 4. Public Interfaces

HTTP:

- `POST /api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/v2_10/patterns/build`
- `GET /api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/v2_10/patterns`
- `GET /api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/v2_10/patterns/blockers`
- `GET /api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/v2_10/patterns/views/{view_id}`

MCP:

- `knowledge_code_architecture_patterns_v2_build`
- `knowledge_code_architecture_patterns_v2`
- `knowledge_code_architecture_pattern_blockers`
- `knowledge_code_architecture_pattern_view`

CLI:

- `knowledge code architecture patterns-v2-build`
- `knowledge code architecture patterns-v2`
- `knowledge code architecture pattern-blockers`
- `knowledge code architecture pattern-view`

## 5. Architecture Boundaries

V2.10 must not:

- mutate V2.0-V2.9 source artifacts;
- rewrite target repo source files;
- rely on HarnessOS-only hardcoded paths in generic modules;
- run target project commands unless runtime introspection is explicitly enabled;
- convert document-only or manifest-only data into accepted code evidence;
- claim runtime calls from imports.

## 6. Generality Rule

Project-specific rules must be expressed as configuration or adapter packs:

```text
generic adapter engine
  + optional adapter config
  + optional project manifest
```

HarnessOS may be used as an acceptance target, but generic modules must remain usable for other Python projects with similar registries.

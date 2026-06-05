# V2.10 Phase 69 Adapter Registry Plan

## Objective

Create a generic Architecture Pattern Adapter Registry that records what extraction patterns were attempted, which patterns matched, and why a pattern was unavailable or blocked.

This phase must not implement HarnessOS-specific extraction logic in the generic engine.

## Development Plan

Implement a registry service under the V2.10 architecture package with:

- built-in adapter taxonomy;
- adapter configuration loader;
- adapter enable/disable/unavailable states;
- adapter attempt persistence;
- public read payload for registry and attempts.

Initial adapter taxonomy:

```text
python_registry_assignment
python_decorator_registration
python_class_inheritance
python_factory_call
cli_parser_registration
tui_command_table
workflow_manifest
agent_worker_registry
adapter_catalog
external_app_registry
architecture_manifest
runtime_introspection_candidate
```

Project-specific pattern packs are allowed only as data/config:

```text
architecture.patterns.json
docs/architecture.patterns.json
```

Generic code must not contain project names such as `HarnessOS`, `harnessOS`, or known HarnessOS path fragments.

## Artifact Outputs

```text
architecture/v2_10/pattern_adapter_registry.json
architecture/v2_10/adapter_attempts.jsonl
architecture/v2_10/pattern_evidence_summary.json
```

## Acceptance Plan

Required tests:

- registry contains all built-in adapter definitions;
- each adapter has `adapter_id`, `adapter_type`, `language`, `file_globs`, `match_strategy`, `confidence_policy`;
- `adapter_attempts.jsonl` is written even when no accepted match exists;
- disabled/unavailable adapters are represented explicitly;
- project adapter config is loaded as data and does not mutate built-ins;
- public payload has no absolute paths.

Real repo checks:

- `data_service`: attempts are non-empty.
- `HarnessOS`: attempts are non-empty.
- generic fixture: at least three adapter attempts.

False-green rejection:

- no attempts but registry read claims success;
- HarnessOS name/path hardcoded in generic modules;
- unavailable adapter silently treated as no_match;
- missing adapter config silently ignored without warning.

## Pre-Implementation Audit Gate

Phase 69 may enter implementation only if:

- V2.9 closure report exists;
- V2.10 PRD/architecture are current authority;
- adapter taxonomy has no fatal/major ambiguity;
- no runtime introspection command can run in this phase.

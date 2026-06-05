# V2.10 Phase 70 AST Binding Plan

## Objective

Bind architecture pattern candidates to deterministic Python source locations using AST extraction.

Accepted binding requires real source file, valid line range, and truth-checkable source lines.

## Development Plan

Implement AST binding for:

- dictionary and list registry assignments;
- decorator registration;
- class inheritance conventions;
- factory call expressions;
- direct function/class definitions;
- import aliases;
- module-level constants that name surfaces.

Supported AST node categories:

```text
ast.Assign
ast.AnnAssign
ast.Dict
ast.List
ast.Call
ast.FunctionDef
ast.AsyncFunctionDef
ast.ClassDef
ast.Import
ast.ImportFrom
```

Binding flow:

```text
adapter candidate
-> AST pattern match
-> registry/decorator/manifest source location
-> symbol reference
-> definition candidate
-> source line range truth check
```

## Binding Status Policy

Accepted:

- repo-relative source path exists;
- line range is valid;
- source snippet is readable;
- symbol/definition relation is deterministic;
- confidence >= 0.85.

Needs review:

- dynamic expression;
- unresolved import alias;
- factory call with unknown target;
- registry value is computed;
- class inheritance matched by naming convention only.

Blocked:

- source file missing;
- line range invalid;
- parse error prevents binding;
- candidate relies only on documentation text.

## Artifact Outputs

```text
architecture/v2_10/adapter_matches.jsonl
architecture/v2_10/accepted_pattern_evidence.jsonl
architecture/v2_10/pattern_blockers.jsonl
```

## Acceptance Plan

Fixture must include:

- dict registry mapping string key to class;
- list registry of handler functions;
- decorator that registers a command/workflow;
- class inheritance pattern;
- factory call pattern;
- imported alias resolved to local symbol.

Assertions:

- accepted bindings have `definition_path` and `definition_line_range`;
- truth check reads real source lines;
- dynamic registry emits `needs_review`, not accepted;
- token/string overlap cannot produce accepted binding;
- no full call graph, runtime call, data flow, or type inference claims appear.

Real repo checks:

- `data_service`: accepted binding count > 0.
- `HarnessOS`: accepted binding count improves or blocker reason becomes more precise than generic `LINE_RANGE_INVALID`.

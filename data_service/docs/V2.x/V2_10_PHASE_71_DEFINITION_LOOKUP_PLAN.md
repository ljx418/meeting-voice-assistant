# V2.10 Phase 71 Definition Lookup Plan

## Objective

Resolve cross-file symbol references from AST bindings to source definitions using local, free, open-source mechanisms.

## Provider Strategy

Default provider:

- AST import resolver.

Optional providers:

- Jedi for Python definition lookup if installed.
- tree-sitter for future multi-language parsing if installed.

No optional provider is required for V2.10 closure. Unavailable providers must return structured status.

## Development Plan

Implement provider interface:

```text
provider_id
provider_kind
available
capabilities
lookup(symbol, from_path)
```

Default AST resolver handles:

- same-module definitions;
- `from module import Symbol`;
- `import module as alias`;
- relative imports inside Python package roots;
- fallback unresolved result.

## Artifact Outputs

```text
architecture/v2_10/definition_lookup_results.jsonl
```

## Acceptance Plan

Required scenarios:

- same-file symbol lookup;
- cross-file imported class lookup;
- import alias lookup;
- missing module returns `DEFINITION_NOT_FOUND`;
- optional provider unavailable returns `DEFINITION_LOOKUP_UNAVAILABLE`;
- lookup result with no line range is not accepted.

False-green rejection:

- provider name listed in health but no executable lookup exists;
- token match accepted as definition;
- unresolved symbol silently falls back to source candidate;
- absolute path leaked in public output.

## Public Error Codes

```text
DEFINITION_LOOKUP_UNAVAILABLE
DEFINITION_NOT_FOUND
DEFINITION_LOOKUP_PARSE_FAILED
DEFINITION_LOOKUP_UNSUPPORTED_LANGUAGE
```

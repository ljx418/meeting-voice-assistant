# V2.10 False-Green Guard Matrix

## Guard Rules

| False-green risk | Required rejection |
| --- | --- |
| Accepted evidence has no line range | reject |
| Line range cannot be read from file | reject |
| Document claim copied as code fact | reject |
| Manifest entry accepted without static binding | reject |
| Runtime introspection output accepted without static binding | reject |
| Import dependency called runtime call | reject |
| Token-only match accepted | reject |
| HarnessOS name hardcoded in generic module | reject |
| Optional lookup provider unavailable but reported accepted | reject |
| HTML/Mermaid contains unpersisted facts | reject |
| Public payload leaks absolute path, secret, traceback | reject |
| Accepted evidence comes only from manifest/runtime/document data | reject |
| Relationship/report claims runtime execution path from import evidence | reject |
| Renderer creates a capability/surface id not present in persisted artifacts | reject |
| Genericity proof uses only HarnessOS and data_service | reject |
| V2.9 baseline unavailable but improvement is claimed | reject |

## Automated Test Expectations

Each phase must include at least one negative test for its primary false-green risk.

Phase 69:

- hardcoded project name scan;
- adapter unavailable state does not count as matched.

Phase 70:

- invalid line range cannot be accepted;
- dynamic registry becomes `needs_review`.

Phase 71:

- provider unavailable returns structured error;
- token-only lookup cannot accepted.

Phase 72:

- document-only claim cannot become code evidence.

Phase 73:

- runtime disabled by default;
- non-allowlisted command blocked.

Phase 74:

- report cannot introduce artifact IDs that do not exist.

Phase 75:

- closure matrix row without evidence cannot be accepted.

## Mandatory Negative Test Matrix

| Phase | Negative fixture | Expected outcome |
| --- | --- | --- |
| 69 | adapter config references project-specific hardcoded path | `PATTERN_ADAPTER_CONFIG_INVALID` or warning, no built-in mutation |
| 69 | generic module contains `HarnessOS` / `harnessOS` string | phase blocked |
| 70 | AST candidate has line range outside file length | `LINE_RANGE_INVALID`, not accepted |
| 70 | registry value is dynamic expression | `needs_review`, not accepted |
| 71 | optional provider missing | `DEFINITION_LOOKUP_UNAVAILABLE`, not no-match |
| 71 | imported symbol resolves to multiple definitions | `DEFINITION_LOOKUP_AMBIGUOUS`, not accepted |
| 72 | document claim text equals code token but no line evidence | `weak_match`, not matched |
| 73 | runtime command not allowlisted | `RUNTIME_COMMAND_NOT_ALLOWLISTED` |
| 73 | manifest entry points to missing symbol | `MANIFEST_BINDING_MISSING`, candidate only |
| 74 | HTML renderer tries to add non-persisted node | render blocked |
| 75 | coverage row lacks artifact path/test command | row cannot be accepted |

## Audit Rule

Every phase audit report must list:

```text
false_green_tests_run
false_green_tests_passed
false_green_tests_failed
manual_review_required
```

If any required false-green test is skipped, the phase cannot be marked accepted. It may only be marked `conditionally_accepted` with explicit justification.

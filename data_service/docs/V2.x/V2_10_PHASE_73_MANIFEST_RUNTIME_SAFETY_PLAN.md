# V2.10 Phase 73 Manifest and Runtime Safety Plan

## Objective

Add safe optional inputs for architecture candidates while preserving the evidence gate.

Manifest and runtime introspection can improve discovery, but neither can create accepted code evidence without static source binding.

## Manifest Contract

Supported locations:

```text
architecture.manifest.json
architecture.yaml
docs/architecture.manifest.json
docs/architecture.yaml
```

Manifest entry fields:

```text
surface_id
surface_type
label
declared_symbol
declared_path
capability_id
metadata
```

Manifest statuses:

```text
candidate
schema_invalid
bound
blocked
needs_review
```

## Runtime Introspection Contract

Runtime introspection is disabled by default.

Allowed only with explicit config:

```text
runtime_introspection.enabled = true
allowlisted_commands = [...]
timeout_ms
working_directory
env_allowlist
```

Runtime output rules:

- store normalized candidates only;
- raw output is not public;
- command output is candidate-only until statically bound;
- stderr, traceback, env, token, and absolute path are redacted.

## Artifact Outputs

```text
architecture/v2_10/manifest_candidates.jsonl
architecture/v2_10/runtime_introspection_candidates.jsonl
```

## Acceptance Plan

Manifest:

- valid manifest produces candidates;
- invalid manifest returns `ARCHITECTURE_MANIFEST_SCHEMA_INVALID`;
- manifest candidate without code binding cannot be accepted;
- manifest public payload has no absolute path.

Runtime:

- disabled-by-default path returns `ARCHITECTURE_RUNTIME_INTROSPECTION_DISABLED`;
- non-allowlisted command returns `ARCHITECTURE_RUNTIME_INTROSPECTION_UNSAFE`;
- allowlisted command output is candidate-only;
- timeout returns structured retryable error;
- raw traceback is never public.

Stop condition:

- If implementation requires running a real target project command without explicit allowlist, stop and request human approval.

# V2.5 Phase 41 Development Plan: Artifact Download Contract Closure

> Generated after Phase 39 Minimax TTS acceptance.
> This phase closes descriptor-only vs direct stream semantics.

## 1. Objective

Make the ResearchNotebook artifact download contract explicit and testable. The recommended V2.5 closure path is descriptor-only accepted unless the original PRD/API matrix explicitly requires direct binary streaming.

## 2. Scope

In scope:

- inspect original PRD/API matrix for download stream requirements;
- create a download contract decision record;
- verify descriptor-only behavior for JSON, slides Markdown, audio WAV descriptor, and PPTX descriptor;
- prove descriptor metadata matches stored binaries by MIME, size, sha256, and status;
- define direct stream as `not implemented`, `out of scope`, or implement it if explicitly required.

Out of scope unless explicitly required:

- direct binary streaming route;
- expiring signed URLs;
- range requests.

## 3. Selected Decision

Use descriptor-only as the V2.5 closure contract:

```text
GET /api/workspaces/{workspace_id}/artifacts/{artifact_id}/download
  -> returns safe descriptor or inline JSON/Markdown payload metadata
  -> does not expose filesystem paths
  -> does not stream raw bytes in V2.5
```

Direct binary streaming is `out_of_scope_for_v2_5`. If a later product/API decision requires direct stream, it must be reopened with authorization, expiry, content headers, range behavior, and structured error semantics.

## 4. Implementation Plan

1. Keep `V2_5_PHASE_41_DOWNLOAD_CONTRACT_DECISION.json` as the authoritative descriptor-only decision.
2. Add focused download contract tests.
3. Verify existing audio/PPTX binary descriptors against disk files.
4. Verify missing artifact / unsupported format errors are structured.
5. Run Phase 39, Phase 37, V2.5A, and real-input regressions.

## 5. Stop Conditions

Stop for human review if:

- original PRD/API matrix explicitly requires direct binary streaming;
- descriptor-only cannot satisfy ResearchNotebook client contract;
- implementation would expose local filesystem paths as download URLs.

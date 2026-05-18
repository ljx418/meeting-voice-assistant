# ResearchNotebook V1.0 Source Library Information Architecture

文档状态：P1 implementation contract；V1.0-M2 frozen。
适用阶段：M2。

## 1. Purpose

Source Library is the primary workspace surface for making imported knowledge visible and actionable.

It must not be a passive table only. It must show source state, build readiness, trace availability, and actions that connect to Ask with Evidence.

## 2. Minimum Fields

Each source row/card should support:

- title;
- `source_id`;
- import/build state;
- last updated;
- artifact refs presence;
- trace availability;
- source type if provided by service;
- primary actions.

## 3. Source States

Required UI states:

- `idle`;
- `selecting`;
- `uploading` / `importing`;
- `imported_not_built`;
- `building`;
- `ready`;
- `failed_import`;
- `failed_build`;
- `removed`;
- `unsupported_type`.

## 4. Actions

Minimum actions:

- detail;
- remove;
- build;
- ask;
- trace.

Rules:

- `ask` should be disabled or clearly degraded when source/workspace is not built;
- `trace` should show unavailable state if trace cannot be loaded;
- unsupported source types must be visible before build/query assumptions are made.

## 5. Acceptance

M2 is not complete unless users can distinguish:

- imported but not built;
- building;
- ready for query;
- import failed;
- build failed;
- unsupported type.

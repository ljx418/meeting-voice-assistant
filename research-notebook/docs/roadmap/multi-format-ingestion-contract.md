# Multi-format Ingestion Contract Roadmap

Date: 2026-05-18

## 1. Purpose

This document defines the expected `data_service` contract roadmap for ingesting large technical knowledge sources beyond basic V1.0 source import.

ResearchNotebook must not implement parser, extraction, transcription, indexing, or artifact storage internals. The frontend consumes service contracts, capability metadata, normalized source units, and stable artifact references.

## 2. Version Roadmap

### V1.0: Basic Source Import / Build / Query

Expected service capability:

- workspace source import;
- source list/detail/trace;
- workspace/session build lifecycle;
- workspace/session query;
- stable `source_id` and `artifact_ref` references.

Frontend behavior:

- upload/import basic sources through target routes;
- build and query source-backed knowledge;
- show source-level citations and trace/provenance drawer;
- do not claim JSON/PPT/video/audio full ingestion readiness.

### V1.1: Source Preview And Evidence Navigation

Expected service capability:

- normalized `DocumentUnit` for previewable sources;
- normalized `EvidenceSpan` for answer evidence;
- source-level fallback when precise locators are unavailable;
- preview availability metadata.

Frontend behavior:

- render source preview when service says available;
- support citation navigation to source/unit;
- degrade to source-level trace/provenance drawer when precise evidence is unavailable.

### V1.2: Parser Capability Expansion

Expected service capability:

- capability manifest or equivalent endpoint;
- JSON parser capability with `json_path` locator;
- PPT parser capability with `slide_no` locator;
- video parser/transcription capability with `timestamp` locator;
- audio parser/transcription capability with `timestamp` locator;
- parser status and partial-support metadata.

Frontend behavior:

- adapt upload affordances based on capability manifest;
- render unsupported/partial support states explicitly;
- use normalized units and evidence spans rather than file-type internals;
- never infer parser support from file extensions alone.

## 3. Minimum Contract Concepts

The service contract should expose:

- service version;
- schema version;
- capability manifest;
- accepted source types;
- preview support per source type;
- locator support per source type;
- parser/build operation state;
- stable source and artifact references.

## 4. Frontend Constraints

ResearchNotebook must:

- call `/api/workspaces/...` target routes only;
- keep route shapes in `shared/api/dataServiceClient.ts`;
- avoid raw filesystem paths and artifact physical paths;
- handle unsupported formats as product states;
- keep source evidence navigation grounded in `source_id`, `unit_id`, locator fields, and `artifact_ref`.

## 5. Acceptance Criteria

The multi-format roadmap is ready to implement when:

- `data_service` exposes capability metadata;
- normalized `DocumentUnit` and `EvidenceSpan` contracts exist;
- JSON/PPT/video/audio parser readiness is represented by service contract, not frontend assumptions;
- frontend contract tests cover supported, unsupported, and partial-support source types.

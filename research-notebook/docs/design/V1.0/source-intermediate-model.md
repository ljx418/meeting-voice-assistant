# ResearchNotebook Source Intermediate Model

Date: 2026-05-18

## 1. Purpose

ResearchNotebook must support product experiences for source preview, evidence navigation, citations, graph context, and future assessment without coupling the frontend to raw files or backend storage internals.

This document defines the normalized source/evidence concepts the frontend should consume from `data_service` when the service exposes them.

## 2. Principles

- `data_service` owns parsing, extraction, indexing, and artifact storage.
- ResearchNotebook owns rendering, navigation, and product interaction.
- The frontend stores stable service identifiers, not raw paths.
- Format support is driven by a service capability manifest.
- Missing locator fields degrade gracefully to source-level evidence.

## 3. Core Concepts

### Source

A user-imported logical source.

Expected fields:

- `source_id`;
- `workspace_id`;
- title/name metadata;
- media or document type when provided by service;
- import/build state;
- stable `artifact_ref` or related artifact refs when provided.

Frontend use:

- source list;
- source detail;
- query grounding;
- source preview entry point;
- future assessment source selection.

### DocumentUnit

A normalized unit within a source.

Examples:

- document page;
- slide;
- transcript segment;
- JSON node;
- section;
- chunk.

Expected fields:

- `unit_id`;
- `source_id`;
- display label;
- text or preview metadata when available;
- locator metadata when available;
- stable `artifact_ref` when the unit is backed by a derived artifact.

Frontend use:

- source preview;
- citation backjump;
- local evidence context;
- future question review.

### EvidenceSpan

A bounded evidence range used to support an answer, summary, graph insight, or future assessment question.

Expected fields:

- `source_id`;
- optional `unit_id`;
- optional snippet or rendered text;
- optional confidence or score metadata;
- optional locator fields;
- optional `artifact_ref`.

Frontend use:

- inline citations;
- evidence sidebar;
- answer provenance;
- citation backjump;
- future assessment review sources.

### Artifact Reference

`artifact_ref` is a stable service-owned reference to derived service artifacts.

Frontend rules:

- display only when useful for evidence/debugging;
- pass back to service routes only through documented APIs;
- never resolve to a filesystem path;
- never parse physical storage layout from the string.

## 4. Locator Fields

Supported locator fields may include:

| Field | Meaning | Typical source type |
| --- | --- | --- |
| `source_id` | Logical source identifier | All sources |
| `unit_id` | Normalized document unit identifier | All parsed sources |
| `page_no` | Page number | PDF, document, image-based document |
| `slide_no` | Slide number | PPT or slide deck |
| `timestamp` | Time offset or range | Video/audio/transcript |
| `json_path` | JSON pointer/path | JSON documents |

Rules:

- locator fields are optional;
- frontend must not invent locators;
- absent precise locator means render source-level evidence;
- locator shape is controlled by `data_service` contract and capability manifest.

## 5. Product Mapping

| Product capability | Required model support | V1 status |
| --- | --- | --- |
| Source list/detail | `Source` | V1.0 via existing source routes |
| Source trace/provenance | `Source`, `artifact_ref` | V1.0 via existing trace route |
| Source preview | `DocumentUnit` | Future backend phase |
| Citation backjump | `EvidenceSpan` + locator fields | Future backend phase |
| JSON navigation | `DocumentUnit` + `json_path` | V1.2 direction |
| PPT navigation | `DocumentUnit` + `slide_no` | V1.2 direction |
| Video/audio navigation | `DocumentUnit` + `timestamp` | V1.2 direction |
| Assessment evidence review | `EvidenceSpan` + `evidence_refs` | V2.0 direction |

## 6. Assessment Relationship

Future Assessment Studio must use the same evidence model.

Every generated question should include evidence references that can resolve to:

- source-level evidence at minimum;
- unit-level evidence when available;
- precise page/slide/timestamp/json path when available.

Assessment domain objects are separate from Quality Governance:

- `Question`;
- `Assessment`;
- `Attempt`;
- `MasteryProfile`.

V1.0 must not claim these objects are implemented or route-backed.

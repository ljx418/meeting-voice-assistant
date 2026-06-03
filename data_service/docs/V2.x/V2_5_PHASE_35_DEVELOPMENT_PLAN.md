# V2.5 Phase 35 Development Plan: PPTX Export Real Run

> Generated from repository analysis.
> Business code must only change after this phase audit has no fatal or major open findings.
> Phase 35 must prove real `.pptx` OpenXML binary generation; renamed JSON is a stop condition.

## 1. Phase Objective

Implement local PPTX export from an existing evidence-backed slides artifact.

Target exporter stack:

- Exporter provider: local deterministic OpenXML writer.
- Output format: `.pptx` zip package.
- Artifact owner: ResearchNotebook V2.5 artifact store.

Phase 35 does not implement new slide planning or LLM slide generation. It exports the existing deterministic slides artifact.

## 2. Scope

In scope:

- Add focused PPTX exporter implementation under `backend/data_service/research_notebook/providers/`.
- Reuse binary artifact storage for service-owned `.pptx` binaries.
- Update slides export endpoint to write real PPTX when `PPTX_PROVIDER=local` and `PPTX_EXPORTER_ENABLED=1`.
- Preserve exporter-disabled `SLIDE_OUTLINE_ONLY` fallback.
- Persist PPTX export descriptor with source slides artifact id, slide count, binary descriptor, and evidence lineage.
- Add real slides fixture E2E tests that inspect OpenXML zip structure.

Out of scope:

- Advanced slide themes.
- Full PowerPoint rendering validation.
- External slide generation providers.
- Editing existing PPTX templates.

## 3. Technical Design

### 3.1 Module Layout

```text
backend/data_service/research_notebook/
  providers/
    pptx_exporter.py
```

`backend/data_service/research_notebook_artifacts.py` remains the compatibility facade and calls the focused exporter.

### 3.2 PPTX Artifact Contract

Ready PPTX export artifacts must include:

```json
{
  "artifact_type": "pptx_export",
  "status": "ready",
  "artifact_available": true,
  "source_slides_artifact_id": "art_slides_xxx",
  "slide_count": 3,
  "binary": {
    "ref": "artifact://workspace_id/artifact_id?binary=pptx",
    "mime_type": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    "size_bytes": 12345,
    "sha256": "..."
  },
  "evidence_refs": []
}
```

### 3.3 OpenXML Integrity

Generated `.pptx` must be a zip package containing at least:

```text
[Content_Types].xml
_rels/.rels
ppt/presentation.xml
ppt/_rels/presentation.xml.rels
ppt/slides/slide1.xml ... slideN.xml
ppt/slides/_rels/slide1.xml.rels ... slideN.xml.rels
```

The slide XML file count must equal the source slides artifact slide count.

## 4. Implementation Steps

1. Add local OpenXML PPTX writer.
2. Add PPTX binary descriptor helper using existing binary store pattern.
3. Update `export_slides` to create a `pptx_export` artifact when exporter is enabled.
4. Update `download_descriptor` to return safe PPTX binary descriptor.
5. Add tests:
   - exporter-disabled fallback;
   - real PPTX export from real slides artifact;
   - zip/OpenXML structure;
   - slide XML count equals source outline count;
   - source artifact lineage and evidence refs preserved;
   - no local path exposure;
   - Phase 32-34 and V2.5 regression.
6. Update Phase 35 audit report with commands, evidence, PRD review, and false-acceptance review.

## 5. Architecture Gates

- Do not rename JSON or Markdown as `.pptx`.
- Do not expose binary filesystem paths.
- Do not mark exporter-disabled output ready.
- Do not change slide generation semantics in this phase.
- Do not add PPTX implementation logic to `backend/app/api/v1/data_service.py`.
- Do not mutate V2.0-V2.4 code asset artifacts.

## 6. Stop Conditions

Stop and request human confirmation if:

- generated PPTX cannot pass zip/OpenXML inspection;
- slide count does not match source slides artifact;
- export requires a cloud provider;
- public payload leaks local paths;
- provider-disabled fallback regresses;
- implementation requires broad changes to legacy API/service files.

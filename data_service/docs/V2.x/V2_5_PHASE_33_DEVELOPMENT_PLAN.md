# V2.5 Phase 33 Development Plan: OCR Provider Real Run

> Generated from repository analysis.
> Business code must only change after this phase audit has no fatal or major open findings.
> Phase 33 must prove real OCR execution with real image input; fake OCR success is a stop condition.

## 1. Phase Objective

Implement the first provider-backed OCR path for ResearchNotebook using local, free, open-source tooling on the current MacBook Pro 2020 environment.

Target provider stack:

- OCR provider: local `tesseract` CLI.
- PDF rasterizer: local `pdftoppm` from Poppler.
- Artifact owner: ResearchNotebook V2.5 artifact store.

Phase 33 does not implement real TTS or real PPTX export. Those remain Phase 34 and Phase 35.

## 2. Scope

In scope:

- Add focused OCR provider implementation under `backend/data_service/research_notebook/providers/`.
- Add focused OCR artifact helper under `backend/data_service/research_notebook/artifacts/`.
- Keep `backend/data_service/research_notebook_artifacts.py` as a compatibility facade.
- Update ResearchNotebook source OCR create/status endpoints to execute local OCR when `OCR_PROVIDER=tesseract`.
- Support source file OCR for image sources.
- Preserve provider-disabled `OCR_REQUIRED` fallback.
- Return `PDF_RASTERIZER_UNAVAILABLE` for scanned PDF OCR when rasterizer support is unavailable or rasterization fails.
- Add real fixture E2E tests that run the OCR provider on a real image file.
- Add disk artifact inspection, line/path redaction checks, and no-fake OCR assertions.

Out of scope:

- TTS/audio binary generation.
- PPTX export.
- Cloud OCR provider adapters.
- Full PDF OCR acceptance unless local rasterizer and fixture are available.
- Treating embedded text PDF extraction as scanned-PDF OCR.

## 3. Technical Design

### 3.1 Module Layout

```text
backend/data_service/research_notebook/
  providers/
    ocr_tesseract.py
  artifacts/
    __init__.py
    ocr_artifacts.py
```

`backend/data_service/research_notebook_artifacts.py` remains a facade and should expose:

```text
create_ocr_artifact(workspace, workspace_id, source_id)
ocr_status(workspace, workspace_id, source_id)
```

### 3.2 OCR Provider Contract

The local provider must:

- call the real `tesseract` executable;
- not use expected fixture text as input;
- capture provider output from generated OCR text files or stdout;
- map execution errors to stable provider error codes;
- redact public payloads;
- return provider version when available.

### 3.3 OCR Artifact Schema

The persisted OCR artifact must include:

```json
{
  "schema_version": "research-notebook-artifact-2.5",
  "artifact_type": "ocr",
  "status": "ready",
  "artifact_available": true,
  "workspace_id": "...",
  "source_id": "...",
  "provider": {
    "name": "tesseract",
    "kind": "local",
    "version": "..."
  },
  "pages": [
    {
      "page_index": 0,
      "blocks": [
        {
          "block_id": "p0_b0",
          "text": "...",
          "confidence": 0.75,
          "confidence_band": "medium",
          "locator": {
            "page": 1,
            "block_index": 0
          },
          "evidence_refs": [
            {
              "source_id": "...",
              "locator": "source://...#page=1&block=0"
            }
          ]
        }
      ]
    }
  ],
  "generation_metadata": {
    "provider": "tesseract",
    "rasterizer": "pdftoppm | none",
    "duration_ms": 0
  }
}
```

### 3.4 Image Source Support

ResearchNotebook OCR requires real image input. If target source import currently rewrites image upload suffixes to `.txt`, Phase 33 must extend the target source upload allowlist to preserve:

```text
.png .jpg .jpeg .tif .tiff .bmp .pbm .pgm .ppm
```

This is only for source registration and OCR. Source preview may still return `source_type_not_supported` for images.

### 3.5 PDF Rasterizer Behavior

For PDF sources:

- If `pdftoppm` is available, rasterize pages to temporary images and OCR those page images.
- If `pdftoppm` is unavailable or rasterization fails, return a structured unavailable payload with `PDF_RASTERIZER_UNAVAILABLE`.
- Do not claim scanned PDF OCR success by reading embedded PDF text.

## 4. Implementation Steps

1. Install/check local OCR tools: `tesseract` and `pdftoppm`.
2. Add provider preflight/version detection in `ocr_tesseract.py`.
3. Add real OCR execution for image sources.
4. Add optional PDF rasterization path.
5. Add OCR artifact persistence and public redaction.
6. Update ResearchNotebook OCR create/status HTTP routes.
7. Add tests:
   - provider disabled fallback;
   - real image OCR E2E;
   - disk artifact inspection;
   - PDF rasterizer unavailable contract;
   - public payload redaction;
   - no fake/preloaded OCR text.
8. Run focused and regression suites.
9. Update the Phase 33 audit report with commands, evidence, PRD review, and false-acceptance review.

## 5. Architecture Gates

- Do not put OCR implementation logic in `backend/app/api/v1/data_service.py`.
- Do not make `backend/app/api/v1/research_notebook.py` a provider implementation module.
- Do not grow `backend/data_service/research_notebook_artifacts.py` into a large OCR module.
- Do not mutate V2.0-V2.4 `assets/codebase` artifacts.
- Do not expose local absolute paths in public payloads.
- Do not claim real OCR unless provider-enabled real fixture tests pass.

## 6. Stop Conditions

Stop and request human confirmation if:

- local provider installation cannot complete;
- Tesseract cannot OCR a real image fixture;
- implementation requires a cloud provider instead of local open-source provider;
- OCR success depends on fixture preloaded expected text;
- public payload leaks local paths, secrets, or raw tracebacks;
- provider-disabled fallback regresses;
- OCR implementation requires broad changes to legacy `data_service.py` or source registry semantics.

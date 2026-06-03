# V2.5 Phase 36 Acceptance Plan: Provider-Specific Closure

> Generated from repository analysis.
> Closure accepts only providers actually configured and tested in this environment.

## 1. Accepted Provider Matrix

Expected local acceptance:

| Capability | Provider | Accepted claim |
| --- | --- | --- |
| OCR | Tesseract 5.5.2 | Real image OCR artifact |
| PDF rasterizer | Poppler `pdftoppm` 26.04.0 | Rasterizer available; invalid PDF returns structured failure |
| TTS/audio | espeak-ng 1.52.0 | Real WAV audio artifact |
| PPTX export | local OpenXML writer | Real `.pptx` zip package |

Unsupported/unaccepted claims:

- cloud OCR;
- cloud TTS;
- advanced PPTX rendering fidelity;
- scanned PDF success fixture beyond structured rasterizer behavior.

## 2. Required Tests

Closure focused suite:

```bash
PYTHONPATH=backend python3 -m pytest backend/tests/test_research_notebook_v25_phase36_provider_closure.py -q
```

Full V2.5 provider-specific suite:

```bash
PYTHONPATH=backend python3 -m pytest backend/tests/test_research_notebook_v25_phase36_provider_closure.py backend/tests/test_research_notebook_v25_phase35_pptx_export.py backend/tests/test_research_notebook_v25_phase34_tts_provider.py backend/tests/test_research_notebook_v25_phase33_ocr_provider.py backend/tests/test_research_notebook_v25_phase32_provider_safety.py backend/tests/test_research_notebook_v25_backend_contract.py backend/tests/test_research_notebook_v25_real_input_acceptance.py -q
```

Broader guard:

```bash
PYTHONPATH=backend python3 -m pytest backend/tests/test_research_notebook_v25_phase36_provider_closure.py backend/tests/test_research_notebook_v25_phase35_pptx_export.py backend/tests/test_research_notebook_v25_phase34_tts_provider.py backend/tests/test_research_notebook_v25_phase33_ocr_provider.py backend/tests/test_research_notebook_v25_phase32_provider_safety.py backend/tests/test_research_notebook_v25_backend_contract.py backend/tests/test_research_notebook_v25_real_input_acceptance.py backend/tests/test_target_http_source_preview.py backend/tests/test_target_http_url_sources.py backend/tests/test_target_http_studio_artifacts.py backend/tests/test_public_surface_guard.py -q
```

Broader data_service regression:

```bash
PYTHONPATH=backend python3 -m pytest backend/tests/test_research_notebook_v25_phase36_provider_closure.py backend/tests/test_research_notebook_v25_phase35_pptx_export.py backend/tests/test_research_notebook_v25_phase34_tts_provider.py backend/tests/test_research_notebook_v25_phase33_ocr_provider.py backend/tests/test_research_notebook_v25_phase32_provider_safety.py backend/tests/test_research_notebook_v25_backend_contract.py backend/tests/test_research_notebook_v25_real_input_acceptance.py backend/tests/test_data_service_api.py backend/tests/test_session_ingest_query_build_contract_plan.py -q
```

Static checks:

```bash
python3 -m py_compile backend/tests/test_research_notebook_v25_phase36_provider_closure.py
git diff --check -- backend/tests/test_research_notebook_v25_phase36_provider_closure.py docs/V2.x/V2_5_PHASE_36_DEVELOPMENT_PLAN.md docs/V2.x/V2_5_PHASE_36_ACCEPTANCE_PLAN.md docs/V2.x/V2_5_PHASE_36_AUDIT_REPORT.md
```

## 3. Exit Criteria

V2.5 provider-specific closure passes only if:

- closure focused suite passes;
- full provider-specific suite passes;
- broader guard passes;
- broader data_service regression passes;
- PRD/spec review finds no major deviation;
- false-acceptance review has no fatal or major open finding.

# V2.5 Phase 42 Acceptance Plan: Full PRD Closure Audit

## 1. Coverage Matrix Requirements

Every row in `V2_5_FULL_PRD_COVERAGE_MATRIX.md` must include:

```text
prd_item_id_or_api_row
architecture_item
capability_area
endpoint_or_artifact
provider_dependency
implementation_status
acceptance_status
evidence
fallback_behavior
public_security_check_result
open_question
owner
```

## 2. Accepted Status Rules

- `accepted`: implemented and verified with real or deterministic contract evidence.
- `conditionally accepted`: contract accepted with explicit limitation.
- `provider unavailable`: provider-dependent item cannot be accepted because usable provider is unavailable or not selected.
- `not implemented`: required item is not built.
- `out of scope`: explicitly excluded from V2.5 closure.

## 3. Required Final Regressions

Run:

```text
PYTHONPATH=backend python3 -m pytest backend/tests/test_research_notebook_v25_phase39_minimax_tts_provider.py -q
PYTHONPATH=backend python3 -m pytest backend/tests/test_research_notebook_v25_phase37_scanned_pdf_ocr.py -q
PYTHONPATH=backend python3 -m pytest backend/tests/test_research_notebook_v25_phase36_provider_closure.py -q
PYTHONPATH=backend python3 -m pytest backend/tests/test_research_notebook_v25_backend_contract.py backend/tests/test_research_notebook_v25_real_input_acceptance.py -q
```

Add Phase 40 and Phase 41 focused tests when those phases are implemented.

Current required final command set:

```text
PYTHONPATH=backend python3 -m pytest backend/tests/test_research_notebook_v25_phase41_download_contract.py -q
PYTHONPATH=backend python3 -m pytest backend/tests/test_research_notebook_v25_phase39_minimax_tts_provider.py -q
PYTHONPATH=backend python3 -m pytest backend/tests/test_research_notebook_v25_phase37_scanned_pdf_ocr.py -q
PYTHONPATH=backend python3 -m pytest backend/tests/test_research_notebook_v25_phase38_provider_adapter_hardening.py -q
PYTHONPATH=backend python3 -m pytest backend/tests/test_research_notebook_v25_phase36_provider_closure.py -q
PYTHONPATH=backend python3 -m pytest backend/tests/test_research_notebook_v25_phase35_pptx_export.py -q
PYTHONPATH=backend python3 -m pytest backend/tests/test_research_notebook_v25_phase34_tts_provider.py -q
PYTHONPATH=backend python3 -m pytest backend/tests/test_research_notebook_v25_backend_contract.py backend/tests/test_research_notebook_v25_real_input_acceptance.py -q
```

## 4. False-Green Rejection

Reject closure if:

- cloud OCR is accepted without provider-enabled evidence;
- direct streaming is accepted without route behavior evidence;
- mock-only tests are used for accepted provider-backed claims;
- skipped tests are counted as pass;
- public output leaks local paths or secrets;
- coverage matrix rows lack evidence.

# V2.5 Phase 41 Acceptance Plan: Artifact Download Contract Closure

## 1. Descriptor-Only Acceptance

Descriptor-only is accepted only if:

- decision record states descriptor-only is the V2.5 contract;
- audio WAV descriptor includes `artifact://` ref, MIME type, size, sha256, duration;
- PPTX descriptor includes `artifact://` ref, MIME type, size, sha256;
- descriptor values match stored binary files;
- JSON/Markdown descriptors do not expose local paths;
- missing artifact, unsupported format, and unavailable binary return structured errors.

## 2. Direct Stream Status

Direct stream is **out of scope for V2.5** under the selected descriptor-only contract.

If a later product/API decision reopens direct stream, it can be accepted only if:

- route behavior is implemented and documented;
- auth/access checks are defined;
- `content-type`, `content-length`, `content-disposition`, range support yes/no, expiry semantics, and errors are tested;
- public output does not expose local paths.

V2.5 false-green rule: descriptor-only behavior must never be described as direct stream support.

## 3. Required Tests

Focused test file to create during implementation:

```text
backend/tests/test_research_notebook_v25_phase41_download_contract.py
```

Regression:

```text
PYTHONPATH=backend python3 -m pytest backend/tests/test_research_notebook_v25_phase39_minimax_tts_provider.py -q
PYTHONPATH=backend python3 -m pytest backend/tests/test_research_notebook_v25_phase35_pptx_export.py -q
PYTHONPATH=backend python3 -m pytest backend/tests/test_research_notebook_v25_phase36_provider_closure.py -q
PYTHONPATH=backend python3 -m pytest backend/tests/test_research_notebook_v25_backend_contract.py backend/tests/test_research_notebook_v25_real_input_acceptance.py -q
```

## 4. False-Green Rejection

Reject the phase if:

- descriptor-only is claimed as direct stream;
- a local filesystem path is returned as URL;
- binary descriptor sha256/size does not match disk;
- missing/expired/unauthorized cases are unstructured.

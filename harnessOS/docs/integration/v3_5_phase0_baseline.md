# V3.5-0 Baseline

baseline_commit: `ebbeb8a4`
baseline_date: `2026-05-11`
python_env: `.venv/bin/python Python 3.12.13`
pytest_command: `./.venv/bin/python -m pytest tests/test_v3_5_contract_inventory.py tests/test_v3_5_scaffolding.py -q`
pytest_result: `Phase0 targeted: 9 passed, 5 warnings in 0.12s; default tests: 215 passed, 3 skipped, 6 warnings in 54.78s`
skipped_tests: `3 skipped in default tests`
warnings: `Existing Pydantic deprecation warnings from core/schemas and one LangGraph pending deprecation warning in tests/test_api_runs.py. System python3 lacks pytest, so validation used the repository .venv.`
external_e2e_excluded: `Meeting/Knowledge real external-service E2E is excluded from Phase0 default acceptance.`
drawio_validation: `xmllint passed for docs/design/V3.5/v3_5_current_gap_analysis.drawio and docs/design/V3.5/diagrams/01_v3_5_application_adaptation_layer_baseline.drawio`

Phase0 does not change supported public API. Phase0 does not make SDK usable. Phase0 does not make external app ready.

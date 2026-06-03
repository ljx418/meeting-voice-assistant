# V5-2 Test Matrix

文档状态：V5-2 implementation planning。

## 1. Focused Tests To Add During Implementation

```text
tests/test_v5_2_provider_profile_model.py
tests/test_v5_2_credential_lifecycle_model.py
tests/test_v5_2_credential_scope_guard.py
tests/test_v5_2_provider_smoke_validation.py
tests/test_v5_2_provider_invocation_evidence.py
tests/test_v5_2_secret_redaction.py
tests/test_v5_2_no_false_green.py
```

## 2. Required Test Coverage

```text
provider profile strict schema rejects unknown fields
provider profile requires tenant/workspace/project/app binding
credential reference never returns raw secret
credential issue requires user_confirmed=true
credential rotate requires user_confirmed=true
credential revoke requires user_confirmed=true
source=agent cannot mutate credential lifecycle
cross-tenant credential action denied
same-tenant wrong workspace denied
same-workspace wrong app denied
provider smoke records redacted evidence
provider invocation evidence includes provider/model/profile refs
logs/errors/evidence/HTML do not leak token/secret/raw payload
claim guard blocks false production claims
```

## 3. Regression Commands

```bash
./.venv/bin/python -m pytest tests/test_v5_2_*.py -q
./.venv/bin/python -m pytest tests/test_v5_1_tenant_boundary.py -q
./.venv/bin/python -m pytest tests/test_v4_u9_final_acceptance.py -q
./.venv/bin/python scripts/v4_unified_reality_check_audit.py
xmllint --noout docs/design/V5.x/v5_current_gap_analysis.drawio
xmllint --noout docs/design/V4.x/v4_x_headless_current_gap_analysis.drawio
```

## 4. Stop Conditions

```text
test uses fake secret and claims production secret lifecycle
provider smoke leaks raw prompt or raw file content
provider profile lacks tenant/workspace/app binding
source=agent can rotate/revoke credentials
rotation/revocation has no evidence
```


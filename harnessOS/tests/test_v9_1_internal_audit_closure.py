from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


V9_ROOT = Path("docs/design/V9.x")
AUDIT_ROOT = V9_ROOT / "evidence" / "v9-1-internal-independent-audit"


def test_v9_1_internal_independent_audit_closes_current_loop_without_runtime_approval() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "tools.v9.generate_internal_audit_closure"],
        check=False,
        text=True,
        capture_output=True,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    data = json.loads((AUDIT_ROOT / "internal-audit-data.json").read_text(encoding="utf-8"))

    assert data["status"] == "PASS"
    assert data["audit_type"] == "internal_independent_closure"
    assert data["runtime_implementation_allowed"] is False
    assert data["v9_2_limited_runtime_slice_complete"] is True
    assert data["v9_2_runtime_implementation_allowed"] is True
    assert data["v9_3_runtime_implementation_allowed"] is False
    assert data["v9_4_runtime_implementation_allowed"] is False
    assert data["external_audit_deferred"] is True
    assert all(check["status"] == "PASS" for check in data["checks"])
    assert any("V9-3 orchestration runtime" in item for item in data["remaining_blockers"])

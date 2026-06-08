from __future__ import annotations

import json
from pathlib import Path

from core.auth.tenant_boundary import IdentityContext
from core.governance.v9_7_production_governance import build_v9_7_governance_fixture, write_v9_7_evidence


OUT_DIR = Path("docs/design/V9.x/evidence/v9-7-production-governance")


def make_context() -> IdentityContext:
    return IdentityContext(
        tenant_id="tenant_v9_7",
        workspace_id="workspace_v9_7",
        project_id="project_v9_7",
        app_id="app_v9_7",
        actor_type="human_user",
        actor_id="user_v9_7_reviewer",
        user_id="user_v9_7_reviewer",
        service_account_id="service_account_v9_7",
        request_id="request_v9_7",
        correlation_id="correlation_v9_7",
    )


def main() -> int:
    acceptance = write_v9_7_evidence(build_v9_7_governance_fixture(make_context()), OUT_DIR)
    print(json.dumps({"status": acceptance["status"], "output": str(OUT_DIR / "index.html")}, ensure_ascii=False, indent=2))
    return 0 if acceptance["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())

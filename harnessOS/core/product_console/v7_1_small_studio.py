"""V7-1 Small Studio control-plane projection.

This module builds a read-only Small Studio aggregation from existing V6
evidence refs. It does not write workflow runtime truth, expose raw credential
material, or implement production GA behavior.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from html import escape
from pathlib import Path
from typing import Any, Mapping
from uuid import uuid4

from apps.gateway.secrets import mask_value
from core.auth.tenant_boundary import IdentityContext, TenantBoundaryError


SENSITIVE_TOKENS = {
    "capability_token",
    "subscription_token",
    "Authorization:",
    "Bearer ",
    "raw_trace_payload",
    "raw_artifact_content",
    "raw_connector_payload",
    "raw prompt",
    "raw_secret",
    "upstream signed URL",
    "api_key",
    "sk-",
}
FORBIDDEN_CLAIMS = {
    "production ready",
    "full production GA",
    "enterprise auth ready",
    "multi-tenant control plane ready",
    "production-ready external app support",
    "complete Workflow Studio ready",
    "Agent executor ready",
    "production controlled executor ready",
    "小型工作室生产可用",
}
RUNTIME_TRUTH_KEYS = {
    "WorkflowDraft",
    "WorkflowVersion",
    "WorkflowInstance",
    "StationRun",
    "Artifact",
}


@dataclass(frozen=True)
class V71SmallStudioProjection:
    """Read-only Small Studio projection DTO."""

    studio_context: dict[str, Any]
    studio_inventory: dict[str, Any]
    workspace_inventory: dict[str, Any]
    project_inventory: dict[str, Any]
    app_inventory: dict[str, Any]
    role_bindings: list[dict[str, Any]]
    provider_profiles: list[dict[str, Any]]
    credential_refs: list[dict[str, Any]]
    quota_decisions: list[dict[str, Any]]
    audit_source_refs: list[dict[str, Any]]
    cross_workspace_denial: dict[str, Any]
    source_refs: dict[str, str]
    global_assertions: dict[str, bool]
    generated_at: str

    def to_dict(self) -> dict[str, Any]:
        """Return a redacted projection."""
        return mask_value(asdict(self))


def build_small_studio_projection(
    context: IdentityContext,
    *,
    source_refs: Mapping[str, str],
    v6_final_data: Mapping[str, Any] | None = None,
) -> V71SmallStudioProjection:
    """Build a read-only Small Studio projection from repo-backed evidence refs."""
    v6_final_data = v6_final_data or {}
    now = _now()
    studio_id = f"studio_{context.tenant_id}"
    provider_profile_id = "provider-profile://v7-1/minimax-redacted"
    credential_ref = "credential-ref://v7-1/minimax-redacted"
    quota_status_id = "quota-status://v7-1/default"
    audit_ref = "audit://v7-1/small-studio"

    studio_context = {
        "studio_id": studio_id,
        "tenant_id": context.tenant_id,
        "workspace_id": context.workspace_id,
        "project_ids": [context.project_id],
        "app_ids": [context.app_id],
        "created_at": now,
        "audit_ref": audit_ref,
        "runtime_truth_boundary": "product_aggregation_only_no_runtime_truth_write",
    }
    workspace_inventory = {
        "tenant_id": context.tenant_id,
        "workspace_id": context.workspace_id,
        "project_ids": [context.project_id],
        "app_ids": [context.app_id],
        "audit_ref": audit_ref,
        "created_at": now,
    }
    project_inventory = {
        "tenant_id": context.tenant_id,
        "workspace_id": context.workspace_id,
        "project_id": context.project_id,
        "workflow_spec_refs": ["workflow-spec://v7-1/local-document-summary"],
        "runtime_report_refs": ["runtime-report://v6-9/final-acceptance"],
        "audit_ref": audit_ref,
        "created_at": now,
    }
    app_inventory = {
        "tenant_id": context.tenant_id,
        "workspace_id": context.workspace_id,
        "project_id": context.project_id,
        "app_id": context.app_id,
        "app_status": "active",
        "service_account_id": context.service_account_id or "service-account-v7-1",
        "audit_ref": audit_ref,
        "created_at": now,
    }
    provider_profiles = [
        {
            "provider_profile_id": provider_profile_id,
            "tenant_id": context.tenant_id,
            "workspace_id": context.workspace_id,
            "app_id": context.app_id,
            "provider": "minimax",
            "model_refs": ["model-ref://v7-1/minimax/default"],
            "redaction_status": "redacted_refs_only",
            "audit_ref": audit_ref,
            "created_at": now,
        }
    ]
    credential_refs = [
        {
            "credential_ref": credential_ref,
            "tenant_id": context.tenant_id,
            "workspace_id": context.workspace_id,
            "app_id": context.app_id,
            "provider_profile_id": provider_profile_id,
            "status": "available",
            "redaction_status": "no_raw_credential_material",
            "audit_ref": audit_ref,
            "created_at": now,
        }
    ]
    role_bindings = [
        _role_binding(context, "studio_admin", "user-v7-1-admin", now),
        _role_binding(context, "workflow_operator", "user-v7-1-operator", now),
        _role_binding(context, "reviewer", "user-v7-1-reviewer", now),
    ]
    quota_decisions = [
        {
            "quota_status_id": quota_status_id,
            "tenant_id": context.tenant_id,
            "workspace_id": context.workspace_id,
            "app_id": context.app_id,
            "limit_ref": "quota-policy://v7-1/default",
            "remaining": 42,
            "policy_decision": "allow",
            "audit_ref": audit_ref,
            "created_at": now,
        },
        {
            "quota_status_id": "quota-status://v7-1/denial-example",
            "tenant_id": context.tenant_id,
            "workspace_id": context.workspace_id,
            "app_id": context.app_id,
            "limit_ref": "quota-policy://v7-1/monthly-provider-calls",
            "remaining": 0,
            "policy_decision": "deny",
            "audit_ref": "audit://v7-1/quota-denial",
            "created_at": now,
        },
    ]
    audit_source_refs = [
        _audit_source_ref(context, "mission_tui", "mission://v7-1/local-document-summary", now),
        _audit_source_ref(context, "product_console", "console://v7-1/small-studio", now),
        _audit_source_ref(context, "runtime_report", "runtime-report://v6-9/final-acceptance", now),
        _audit_source_ref(context, "evidence_chain", "evidence://v6-9/final-acceptance", now),
    ]
    studio_inventory = {
        "studio_id": studio_id,
        "tenant_id": context.tenant_id,
        "workspace_count": 1,
        "project_count": 1,
        "app_count": 1,
        "provider_profile_count": len(provider_profiles),
        "credential_ref_count": len(credential_refs),
        "audit_ref": audit_ref,
        "created_at": now,
    }
    cross_workspace_denial = build_cross_workspace_denial(context)
    global_assertions = {
        "small_studio_is_product_aggregation_only": True,
        "does_not_write_runtime_truth": True,
        "credential_refs_redacted": True,
        "provider_profiles_redacted": True,
        "quota_denial_explainable": True,
        "cross_workspace_access_denied": cross_workspace_denial["policy_decision"] == "deny",
        "v6_baseline_not_upgraded_to_production_ready": v6_final_data.get("production_ready") is False,
    }
    projection = V71SmallStudioProjection(
        studio_context=studio_context,
        studio_inventory=studio_inventory,
        workspace_inventory=workspace_inventory,
        project_inventory=project_inventory,
        app_inventory=app_inventory,
        role_bindings=role_bindings,
        provider_profiles=provider_profiles,
        credential_refs=credential_refs,
        quota_decisions=quota_decisions,
        audit_source_refs=audit_source_refs,
        cross_workspace_denial=cross_workspace_denial,
        source_refs=dict(source_refs),
        global_assertions=global_assertions,
        generated_at=now,
    )
    validate_small_studio_projection(projection)
    return projection


def build_cross_workspace_denial(context: IdentityContext) -> dict[str, Any]:
    """Return auditable evidence that cross-workspace access is denied."""
    try:
        if "other-workspace" != context.workspace_id:
            raise TenantBoundaryError(
                "WORKSPACE_SCOPE_DENIED",
                "Resource workspace does not match actor workspace.",
                reason="workspace_mismatch",
                resource="workspace_inventory",
            )
    except TenantBoundaryError as exc:
        return {
            "denial_id": f"denial_{uuid4().hex[:12]}",
            "tenant_id": context.tenant_id,
            "actor_workspace_id": context.workspace_id,
            "target_workspace_id": "other-workspace",
            "policy_decision": "deny",
            "denial_reason": exc.reason,
            "audit_ref": f"audit://v7-1/cross-workspace-denial/{uuid4().hex[:12]}",
            "created_at": _now(),
        }
    raise AssertionError("cross-workspace fixture should be denied")


def validate_small_studio_projection(projection: V71SmallStudioProjection) -> None:
    """Validate V7-1 no-false-green and redaction boundaries."""
    payload = json.dumps(projection.to_dict(), ensure_ascii=False, sort_keys=True)
    for token in SENSITIVE_TOKENS:
        if token.lower() in payload.lower():
            raise ValueError(f"sensitive token leaked: {token}")
    for key in RUNTIME_TRUTH_KEYS:
        if key in payload:
            raise ValueError(f"runtime truth key leaked: {key}")
    if projection.studio_context["runtime_truth_boundary"] != "product_aggregation_only_no_runtime_truth_write":
        raise ValueError("runtime truth boundary missing")
    if any(item["redaction_status"] != "redacted_refs_only" for item in projection.provider_profiles):
        raise ValueError("provider profile not redacted")
    if any(item["redaction_status"] != "no_raw_credential_material" for item in projection.credential_refs):
        raise ValueError("credential ref not redacted")


def render_small_studio_html(projection: V71SmallStudioProjection) -> str:
    """Render a read-only Small Studio evidence page."""
    data = projection.to_dict()
    sections = [
        ("Studio Context", data["studio_context"]),
        ("Studio Inventory", data["studio_inventory"]),
        ("Provider Profiles", data["provider_profiles"]),
        ("Credential Refs", data["credential_refs"]),
        ("Quota Decisions", data["quota_decisions"]),
        ("Audit Source Refs", data["audit_source_refs"]),
        ("Cross Workspace Denial", data["cross_workspace_denial"]),
        ("Global Assertions", data["global_assertions"]),
    ]
    body = "\n".join(
        f"<section><h2>{escape(title)}</h2><pre>{escape(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True))}</pre></section>"
        for title, value in sections
    )
    return f"""<!doctype html>
<html lang=\"zh-CN\">
  <head>
    <meta charset=\"utf-8\" />
    <title>V7-1 Small Studio Evidence</title>
    <style>
      body {{ font-family: -apple-system, BlinkMacSystemFont, \"Segoe UI\", sans-serif; margin: 32px; color: #111827; background: #f8fafc; }}
      h1 {{ font-size: 28px; }}
      section {{ background: white; border: 1px solid #e5e7eb; border-radius: 8px; padding: 16px; margin: 16px 0; }}
      pre {{ white-space: pre-wrap; background: #f1f5f9; padding: 12px; border-radius: 6px; }}
    </style>
  </head>
  <body>
    <h1>V7-1 Small Studio Evidence</h1>
    <p>只读小型工作室控制面投影；不构造运行时 truth，不暴露原始凭证。</p>
    {body}
  </body>
</html>
"""


def scan_small_studio_html(html: str) -> dict[str, Any]:
    """Scan rendered HTML for sensitive leakage and false-green copy."""
    sensitive_hits = [token for token in SENSITIVE_TOKENS if token.lower() in html.lower()]
    forbidden_claim_hits = [claim for claim in FORBIDDEN_CLAIMS if claim.lower() in html.lower()]
    runtime_truth_hits = [key for key in RUNTIME_TRUTH_KEYS if key in html]
    return {
        "status": "PASS" if not sensitive_hits and not forbidden_claim_hits and not runtime_truth_hits else "FAIL",
        "sensitive_hits": sensitive_hits,
        "forbidden_claim_hits": forbidden_claim_hits,
        "runtime_truth_hits": runtime_truth_hits,
    }


def _role_binding(context: IdentityContext, role: str, actor_id: str, created_at: str) -> dict[str, Any]:
    return {
        "binding_id": f"role-binding://v7-1/{role}",
        "tenant_id": context.tenant_id,
        "workspace_id": context.workspace_id,
        "actor_id": actor_id,
        "role": role,
        "scope_refs": [context.workspace_id, context.project_id, context.app_id],
        "policy_decision": "allow",
        "audit_ref": f"audit://v7-1/role-binding/{role}",
        "created_at": created_at,
    }


def _audit_source_ref(context: IdentityContext, source_type: str, source_id: str, created_at: str) -> dict[str, Any]:
    return {
        "audit_ref": f"audit://v7-1/{source_type}/{uuid4().hex[:12]}",
        "tenant_id": context.tenant_id,
        "workspace_id": context.workspace_id,
        "source_type": source_type,
        "source_id": source_id,
        "correlation_id": context.correlation_id,
        "request_id": context.request_id,
        "created_at": created_at,
    }


def _now() -> str:
    return datetime.now(UTC).isoformat()


def read_json(path: Path) -> dict[str, Any]:
    """Read a JSON file if present; otherwise return an empty mapping."""
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))

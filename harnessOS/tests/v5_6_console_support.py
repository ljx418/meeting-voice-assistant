from __future__ import annotations

from core.auth.tenant_boundary import IdentityContext, ResourceRef
from core.product_console.thin_web_console import build_manual_confirmation, build_thin_web_console_state


def make_context(*, actor_type: str = "human_user", actor_id: str = "user_v5_6") -> IdentityContext:
    return IdentityContext(
        tenant_id="tenant_v5",
        workspace_id="workspace_v5",
        project_id="project_v5",
        app_id="app_v5",
        actor_type=actor_type,
        actor_id=actor_id,
        user_id=actor_id if actor_type == "human_user" else None,
        service_account_id="svc_v5_6" if actor_type == "service_account" else None,
        agent_id="agent_v5_6" if actor_type == "agent" else None,
        session_id="session_v5_6" if actor_type == "agent" else None,
        request_id="request_v5_6",
        correlation_id="correlation_v5_6",
    )


def make_target(context: IdentityContext | None = None) -> ResourceRef:
    context = context or make_context()
    return ResourceRef(
        resource_type="audit_export",
        resource_id="audit_export_v5_6",
        tenant_id=context.tenant_id,
        workspace_id=context.workspace_id,
        project_id=context.project_id,
        app_id=context.app_id,
        owner_ref=context.actor_id,
        workflow_instance_id="workflow_instance_v5_6",
    )


def make_state():
    context = make_context()
    confirmation = build_manual_confirmation(
        context,
        operation="context.update",
        source="user",
        user_confirmed=True,
        target=make_target(context),
    )
    return build_thin_web_console_state(
        context,
        runtime_result={
            "workflow_instance_id": "workflow_instance_v5_6",
            "status": "completed",
            "nodes": [{"station_id": "folder_scan", "status": "completed"}],
            "artifacts": [{"artifact_id": "summary"}],
        },
        evidence_chain={
            "proposal_id": "proposal_v5_6",
            "handoff_id": "handoff_v5_6",
            "operation_type": "workflow.instance.start",
            "policy_decision": "allow",
            "runtime_result_ref": {"workflow_instance_id": "workflow_instance_v5_6"},
            "redaction_status": "redacted",
        },
        audit_export={
            "export_id": "audit_export_v5_6",
            "readonly": True,
            "allowed_actions": ["view", "export", "open_evidence"],
            "redaction_status": "redacted",
        },
        external_apps=[
            {
                "registration": {"app_registration_id": "app_v5_6", "status": "active"},
                "sdk": {"browser_allowed_paths": ["/bff/v5/console"]},
            }
        ],
        manual_confirmation=confirmation,
        source_refs={
            "runtime_result": "runtime-result.json",
            "evidence_chain": "evidence.json",
            "audit_export": "audit-export.json",
            "external_app": "external-apps.json",
        },
    )

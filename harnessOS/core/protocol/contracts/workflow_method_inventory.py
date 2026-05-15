"""V3.6 workflow runtime method inventory.

non-runtime contract metadata only; no handler registration; no behavior change
"""

from __future__ import annotations

from typing import Any, Dict, List

WorkflowMethodEntry = Dict[str, Any]

FAMILY = "workflow_runtime"
INTRODUCED_IN = "V3.6"


def _entry(
    method: str,
    capability: str,
    planned_phase: str,
    *,
    status: str = "planned",
    handler_ref: str | None = None,
) -> WorkflowMethodEntry:
    return {
        "method": method,
        "surface": "optional",
        "status": status,
        "capability": capability,
        "stability": "beta" if status == "implemented" else "draft",
        "planned_phase": planned_phase,
        "handler_ref": handler_ref,
        "forbidden_reason": None,
        "family": FAMILY,
        "introduced_in": INTRODUCED_IN,
    }


WORKFLOW_METHOD_INVENTORY: List[WorkflowMethodEntry] = [
    _entry("workflow.template.create", "workflows.write", "V3.6-B", status="implemented", handler_ref="apps.gateway.service.GatewayService.workflow_template_create"),
    _entry("workflow.template.get", "workflows.read", "V3.6-B", status="implemented", handler_ref="apps.gateway.service.GatewayService.workflow_template_get"),
    _entry("workflow.template.list", "workflows.read", "V3.6-B", status="implemented", handler_ref="apps.gateway.service.GatewayService.workflow_template_list"),
    _entry("workflow.template.update_draft", "workflows.write", "V3.6-B", status="implemented", handler_ref="apps.gateway.service.GatewayService.workflow_template_update_draft"),
    _entry("workflow.template.publish", "workflow_versions.publish", "V3.6-B", status="implemented", handler_ref="apps.gateway.service.GatewayService.workflow_template_publish"),
    _entry("workflow.template.archive", "workflows.write", "V3.6-B", status="implemented", handler_ref="apps.gateway.service.GatewayService.workflow_template_archive"),
    _entry("workflow.version.get", "workflows.read", "V3.6-B", status="implemented", handler_ref="apps.gateway.service.GatewayService.workflow_version_get"),
    _entry("workflow.version.list", "workflows.read", "V3.6-B", status="implemented", handler_ref="apps.gateway.service.GatewayService.workflow_version_list"),
    _entry("workflow.instance.start", "workflows.execute", "V3.6-C", status="implemented", handler_ref="apps.gateway.service.GatewayService.workflow_instance_start"),
    _entry("workflow.instance.get", "workflows.read", "V3.6-C", status="implemented", handler_ref="apps.gateway.service.GatewayService.workflow_instance_get"),
    _entry("workflow.instance.list", "workflows.read", "V3.6-C", status="implemented", handler_ref="apps.gateway.service.GatewayService.workflow_instance_list"),
    _entry("workflow.instance.pause", "workflows.execute", "V3.6-C", status="implemented", handler_ref="apps.gateway.service.GatewayService.workflow_instance_pause"),
    _entry("workflow.instance.resume", "workflows.execute", "V3.6-C", status="implemented", handler_ref="apps.gateway.service.GatewayService.workflow_instance_resume"),
    _entry("workflow.instance.cancel", "workflows.execute", "V3.6-C", status="implemented", handler_ref="apps.gateway.service.GatewayService.workflow_instance_cancel"),
    _entry("workflow.instance.retry", "workflows.execute", "V3.6-C", status="implemented", handler_ref="apps.gateway.service.GatewayService.workflow_instance_retry"),
    _entry("workflow.instance.status", "workflows.read", "V3.6-C", status="implemented", handler_ref="apps.gateway.service.GatewayService.workflow_instance_status"),
    _entry("station.run.get", "stations.read", "V3.6-C", status="implemented", handler_ref="apps.gateway.service.GatewayService.station_run_get"),
    _entry("station.run.list", "stations.read", "V3.6-C", status="implemented", handler_ref="apps.gateway.service.GatewayService.station_run_list"),
    _entry("station.rerun", "stations.execute", "V3.6-C", status="implemented", handler_ref="apps.gateway.service.GatewayService.station_rerun"),
    _entry("station.output.list", "stations.read", "V3.6-G", status="implemented", handler_ref="apps.gateway.service.GatewayService.station_output_list"),
    _entry("quality.evaluation.create", "quality.write", "V3.6-F", status="implemented", handler_ref="apps.gateway.service.GatewayService.quality_evaluation_create"),
    _entry("quality.evaluation.get", "quality.read", "V3.6-F", status="implemented", handler_ref="apps.gateway.service.GatewayService.quality_evaluation_get"),
    _entry("quality.evaluation.list", "quality.read", "V3.6-F", status="implemented", handler_ref="apps.gateway.service.GatewayService.quality_evaluation_list"),
    _entry("quality.evaluation.attach", "quality.write", "V3.6-F", status="implemented", handler_ref="apps.gateway.service.GatewayService.quality_evaluation_attach"),
    _entry("workflow.board.get", "board.read", "V3.6-G", status="implemented", handler_ref="apps.gateway.service.GatewayService.workflow_board_get"),
    _entry("business.event.emit", "business_events.write", "V3.6-H", status="implemented", handler_ref="apps.gateway.service.GatewayService.business_event_emit"),
    _entry("workflow.context.get", "workflow_context.read", "V3.6-H", status="implemented", handler_ref="apps.gateway.service.GatewayService.workflow_context_get"),
    _entry("workflow.context.update", "workflow_context.write", "V3.6-H", status="implemented", handler_ref="apps.gateway.service.GatewayService.workflow_context_update"),
    _entry("business.event.bind", "workflow_context.write", "V3.6-H", status="implemented", handler_ref="apps.gateway.service.GatewayService.business_event_bind"),
    _entry("workflow.patch.propose", "workflow_patches.write", "V3.6-I", status="implemented", handler_ref="apps.gateway.service.GatewayService.workflow_patch_propose"),
    _entry("workflow.patch.diff", "workflow_patches.read", "V3.6-I", status="implemented", handler_ref="apps.gateway.service.GatewayService.workflow_patch_diff"),
    _entry("workflow.patch.apply", "workflow_patches.write", "V3.6-I", status="implemented", handler_ref="apps.gateway.service.GatewayService.workflow_patch_apply"),
    _entry("workflow.patch.reject", "workflow_patches.write", "V3.6-I", status="implemented", handler_ref="apps.gateway.service.GatewayService.workflow_patch_reject"),
    _entry("workflow.draft.save", "workflows.write", "V3.6-B", status="implemented", handler_ref="apps.gateway.service.GatewayService.workflow_draft_save"),
]

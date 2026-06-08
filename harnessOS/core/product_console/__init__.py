"""Product console primitives."""

from core.product_console.v9_6_workflow_studio import (
    V96ManualConfirmation,
    V96StudioPanel,
    V96WorkflowDiffProposal,
    V96WorkflowStudioError,
    V96WorkflowStudioState,
    browser_route_decision,
    build_manual_confirmation,
    build_workflow_diff_proposal,
    build_workflow_studio_state,
    render_workflow_studio_html,
    scan_rendered_html,
    validate_workflow_studio_state,
    write_v9_6_evidence,
)

__all__ = [
    "V96ManualConfirmation",
    "V96StudioPanel",
    "V96WorkflowDiffProposal",
    "V96WorkflowStudioError",
    "V96WorkflowStudioState",
    "browser_route_decision",
    "build_manual_confirmation",
    "build_workflow_diff_proposal",
    "build_workflow_studio_state",
    "render_workflow_studio_html",
    "scan_rendered_html",
    "validate_workflow_studio_state",
    "write_v9_6_evidence",
]

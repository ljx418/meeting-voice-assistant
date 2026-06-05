from __future__ import annotations

import json
import xml.etree.ElementTree as ET
from pathlib import Path


V7_DIR = Path("docs/design/V7.x")
SCHEMA_DIR = V7_DIR / "schemas"
EVIDENCE_DIR = V7_DIR / "evidence" / "v7-0-planning-hardening"


SMALL_STUDIO_SCHEMAS = [
    "StudioContext.schema.json",
    "StudioInventory.schema.json",
    "WorkspaceInventory.schema.json",
    "ProjectInventory.schema.json",
    "AppInventory.schema.json",
    "StudioRoleBinding.schema.json",
    "ProviderProfileProjection.schema.json",
    "CredentialRefProjection.schema.json",
    "QuotaStatusProjection.schema.json",
    "AuditSourceRefProjection.schema.json",
]

MISSION_TUI_SCHEMAS = [
    "MissionTuiState.schema.json",
    "MissionInputEvent.schema.json",
    "ExperienceStateTimeline.schema.json",
    "AvailableAction.schema.json",
    "ForbiddenActionReason.schema.json",
    "EvidenceLink.schema.json",
    "BlueprintLink.schema.json",
    "RuntimeReportLink.schema.json",
    "WorkflowExperienceLinkContract.schema.json",
]


def _load_schema(name: str) -> dict:
    return json.loads((SCHEMA_DIR / name).read_text(encoding="utf-8"))


def test_v7_0_canonical_documents_and_contracts_exist() -> None:
    required = [
        "00_README.md",
        "v7_target_prd.md",
        "v7_target_architecture.md",
        "v7_current_gap_analysis.md",
        "v7_current_gap_analysis.drawio",
        "v7_development_and_acceptance_plan.md",
        "v7_acceptance_gate_matrix.md",
        "v7_no_false_green_claim_guard.md",
        "v7_planning_audit_for_chatgpt.md",
        "v7_v6_baseline_evidence.md",
        "v7_0_planning_gate.md",
        "v7_0_contracts_and_test_matrix.md",
    ]
    missing = [name for name in required if not (V7_DIR / name).exists()]
    assert missing == []


def test_v7_0_all_schema_files_parse_and_are_strict() -> None:
    required = [
        "v7_common_defs.schema.json",
        "V7EvidencePackage.schema.json",
        *SMALL_STUDIO_SCHEMAS,
        *MISSION_TUI_SCHEMAS,
    ]
    missing = [name for name in required if not (SCHEMA_DIR / name).exists()]
    assert missing == []

    for name in required:
        schema = _load_schema(name)
        assert schema["$schema"] == "https://json-schema.org/draft/2020-12/schema"
        if name != "v7_common_defs.schema.json":
            assert schema["additionalProperties"] is False
            assert schema["required"]


def test_v7_0_small_studio_schema_boundaries() -> None:
    studio_context = _load_schema("StudioContext.schema.json")
    credential_ref = _load_schema("CredentialRefProjection.schema.json")
    provider_profile = _load_schema("ProviderProfileProjection.schema.json")

    assert "runtime_truth_boundary" in studio_context["required"]
    assert studio_context["properties"]["runtime_truth_boundary"]["const"] == "product_aggregation_only_no_runtime_truth_write"
    assert credential_ref["properties"]["redaction_status"]["const"] == "no_raw_credential_material"
    assert provider_profile["properties"]["redaction_status"]["const"] == "redacted_refs_only"


def test_v7_0_mission_tui_contract_blocks_agent_execution() -> None:
    available_action = _load_schema("AvailableAction.schema.json")
    mission_state = _load_schema("MissionTuiState.schema.json")

    assert available_action["properties"]["agent_executable"]["const"] is False
    assert "agent" not in available_action["properties"]["source"]["enum"]
    assert "AwaitingConfirmation" in mission_state["properties"]["current_state"]["enum"]
    assert "UserConfirmed" in mission_state["properties"]["current_state"]["enum"]


def test_v7_0_link_contracts_are_readonly_or_visualization_only() -> None:
    evidence_link = _load_schema("EvidenceLink.schema.json")
    blueprint_link = _load_schema("BlueprintLink.schema.json")
    runtime_link = _load_schema("RuntimeReportLink.schema.json")
    link_contract = _load_schema("WorkflowExperienceLinkContract.schema.json")

    assert evidence_link["properties"]["readonly"]["const"] is True
    assert blueprint_link["properties"]["visualization_only"]["const"] is True
    assert runtime_link["properties"]["readonly"]["const"] is True
    assert link_contract["properties"]["runtime_truth_boundary"]["const"] == "links_are_read_model_refs_not_runtime_truth"


def test_v7_0_evidence_package_is_complete_and_blocks_implementation() -> None:
    data = json.loads((EVIDENCE_DIR / "acceptance-data.json").read_text(encoding="utf-8"))

    assert data["stage_id"] == "V7-0"
    assert data["status"] == "PASS"
    assert data["evidence_scope"] == "planning_gate"
    assert data["implementation_started"] is False
    assert data["v7_1_implementation_allowed"] is False
    assert data["v7_2_implementation_allowed"] is False
    assert data["v7_3_implementation_allowed"] is False
    assert data["proceed_decision"] == "proceed_to_v7_1_pre_implementation_review"


def test_v7_0_claim_guard_has_required_terms() -> None:
    guard = (V7_DIR / "v7_no_false_green_claim_guard.md").read_text(encoding="utf-8")
    required_terms = [
        "production ready",
        "full production GA",
        "complete Workflow Studio ready",
        "Agent executor ready",
        "production controlled executor ready",
        "production-ready external app support",
        "distributed multi-Agent runtime ready",
        "autonomous workflow editing ready",
        "小型工作室生产可用",
        "TUI 工作流工作台已完成",
    ]
    missing = [term for term in required_terms if term not in guard]
    assert missing == []


def test_v7_stage_status_reflects_final_acceptance() -> None:
    readme = (V7_DIR / "00_README.md").read_text(encoding="utf-8")
    plan = (V7_DIR / "v7_development_and_acceptance_plan.md").read_text(encoding="utf-8")
    acceptance = (V7_DIR / "v7_acceptance_gate_matrix.md").read_text(encoding="utf-8")

    assert "current_stage: V7-2 complete / ready for review" in readme
    assert "| V7-1 | COMPLETE / READY FOR REVIEW |" in readme
    assert "| V7-2 | COMPLETE / READY FOR REVIEW |" in readme
    assert "| V7-3 | COMPLETE / READY FOR REVIEW |" in readme
    assert "| V7-4 | COMPLETE / READY FOR REVIEW |" in readme
    assert "complete / ready for review" in plan
    assert "V7-3 PASS requires" in plan
    assert "V7-0 Contract Gate" in acceptance


def test_v7_0_drawio_xml_valid() -> None:
    ET.parse(V7_DIR / "v7_current_gap_analysis.drawio")

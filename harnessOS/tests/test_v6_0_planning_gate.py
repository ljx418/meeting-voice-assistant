import json
import xml.etree.ElementTree as ET
from pathlib import Path


V6_DIR = Path("docs/design/V6.x")
EVIDENCE_DIR = V6_DIR / "evidence" / "v6-0-planning-gate"


def test_v6_0_canonical_documents_exist() -> None:
    required = [
        "00_README.md",
        "v6_target_prd.md",
        "v6_target_architecture.md",
        "v6_current_gap_analysis.md",
        "v6_current_gap_analysis.drawio",
        "v6_development_and_acceptance_plan.md",
        "v6_acceptance_gate_matrix.md",
        "v6_milestone_roadmap.md",
        "v6_no_false_green_claim_guard.md",
        "v6_planning_audit_for_chatgpt.md",
        "v6_0_production_pilot_planning_completion_note.md",
    ]

    missing = [name for name in required if not (V6_DIR / name).exists()]
    assert missing == []


def test_v6_0_drawio_atlas_has_required_pages() -> None:
    tree = ET.parse(V6_DIR / "v6_current_gap_analysis.drawio")
    pages = [diagram.attrib["name"] for diagram in tree.getroot().findall("diagram")]

    assert pages == [
        "01 阅读指南",
        "02 当前架构与目标架构差异",
        "03 V6 目标架构平面",
        "04 功能规格矩阵",
        "05 开发及验收流程",
        "06 项目里程碑",
        "07 验收门槛",
        "08 出门条件与停止条件",
    ]


def test_v6_0_evidence_package_is_complete() -> None:
    required = [
        "index.html",
        "acceptance-data.json",
        "result-summary.md",
        "claims-scan.md",
    ]
    missing = [name for name in required if not (EVIDENCE_DIR / name).exists()]
    assert missing == []

    data = json.loads((EVIDENCE_DIR / "acceptance-data.json").read_text(encoding="utf-8"))
    assert data["stage"] == "V6-0"
    assert data["status"] == "PASS"
    assert data["evidence_scope"] == "planning_gate"
    assert data["implementation_started"] is False
    assert data["v6_1_implementation_started"] is False
    assert data["human_risk_decision_required"] is False


def test_v6_0_status_does_not_start_v6_1() -> None:
    plan = (V6_DIR / "v6_development_and_acceptance_plan.md").read_text(encoding="utf-8")
    assert "| V6-0 | Production Pilot Planning Gate | complete / ready for review |" in plan
    assert "| V6-1 | Identity And Tenant Control Plane | complete / ready for review |" in plan
    assert "| V6-5 | Governed Agent Execution Intent Pilot | complete / ready for review |" in plan
    assert "| V6-6 | Production External App Onboarding | complete / ready for review |" in plan
    assert "| V6-7 | Distributed Runtime Productization | complete / ready for review |" in plan
    readme = (V6_DIR / "00_README.md").read_text(encoding="utf-8")
    assert "V6-1 complete: production identity and tenant boundary pilot slice ready for review." in readme
    assert "V6-2 complete: production credential and provider lifecycle pilot slice ready for review." in readme
    assert "V6-3 complete: production observability and audit export pilot slice ready for review." in readme
    assert "V6-4 complete: limited production controlled executor pilot slice ready for review." in readme
    assert "V6-5 complete: governed Agent execution intent pilot gate ready for review." in readme
    assert "V6-6 complete: production external app onboarding pilot slice ready for review." in readme
    assert "V6-7 complete: distributed multi-Agent runtime productization pilot slice ready for review." in readme
    assert "V6-8 complete: product console pilot slice ready for review." in readme
    assert "V6 complete: production pilot baseline ready for review." in readme


def test_v6_0_forbidden_claims_are_guarded() -> None:
    forbidden_claims = [
        "complete Workflow Studio ready",
        "complete AgentTalkWindow ready",
        "Agent executor ready",
        "controlled executor ready",
        "production controlled executor ready",
        "production-ready external app support",
        "full multi-Agent orchestration ready",
        "distributed multi-Agent runtime ready",
        "autonomous workflow editing ready",
    ]
    safe_context_markers = [
        "Forbidden",
        "Non-Goals",
        "No False Green",
        "does not prove",
        "does not mean",
        "不得声明",
        "不得改写",
        "不证明",
        "不默认证明",
        "not ",
        "Still Forbidden",
        "forbidden",
        "不允许",
        "不能",
    ]

    for path in V6_DIR.glob("*.md"):
        lines = path.read_text(encoding="utf-8").splitlines()
        for line_number, line in enumerate(lines, start=1):
            for claim in forbidden_claims:
                if claim in line:
                    context = "\n".join(lines[max(0, line_number - 16) : line_number + 2])
                    assert any(marker in context for marker in safe_context_markers), f"{path}:{line_number}: {line}"

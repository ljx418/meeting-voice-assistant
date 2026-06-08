from __future__ import annotations

import json
import xml.etree.ElementTree as ET
from pathlib import Path


ROOT = Path("docs/design/V9.x/evidence/v9-user-scenario-video-workflow-e2e")
DATA_PATH = ROOT / "raw/video-workflow-e2e.json"
QUALITY_PATH = ROOT / "raw/quality-agent-report.json"
DRAWIO_PATH = ROOT / "workflow-agent-state.drawio"


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _repo_path(evidence_path: str) -> Path:
    return Path("docs/design/V9.x") / evidence_path


def test_v9_video_workflow_e2e_evidence_is_runtime_backed_and_provider_backed() -> None:
    data = _load_json(DATA_PATH)

    assert data["status"] == "PASS"
    assert data["runtime_backed"] is True
    assert data["evidence_scope"] == "real_provider_backed_runtime_fixture"
    assert data["provider_ref"] == "provider-ref://minimax/image-generation"
    assert data["provider_invocation_ref"].startswith("provider-invocation-ref://v9/video-e2e/")
    assert data["provider_request_body_stored"] is False
    assert data["provider_response_body_stored"] is False
    assert data["prompt_material_stored"] is False
    assert data["credential_material_stored"] is False
    assert data["base64_stored"] is False
    assert data["source_agent_direct_mutation_denied"] is True
    assert data["agent_executor_ready"] is False
    assert data["full_multi_agent_orchestration_ready"] is False
    assert data["autonomous_coding_workflow_ready"] is False


def test_v9_video_workflow_storyboard_artifacts_and_real_tui_screenshots_exist() -> None:
    data = _load_json(DATA_PATH)

    assert len(data["storyboard_artifacts"]) == 4
    for artifact in data["storyboard_artifacts"]:
        image_path = _repo_path(artifact["path"])
        assert image_path.exists()
        assert image_path.stat().st_size == artifact["byte_size"]
        assert artifact["width"] == 1024
        assert artifact["height"] == 1024
        assert artifact["style_bible_id"] == data["style_bible_id"]
        assert artifact["character_bible_id"] == data["character_bible_id"]

    assert len(data["screenshots"]) >= 2
    for screenshot in data["screenshots"]:
        screenshot_path = _repo_path(screenshot["path"])
        assert screenshot["type"] == "real_mac_terminal_tui_screenshot"
        assert screenshot["source_evidence_ref"].startswith("evidence/v9-prd-ux-runtime-review/screenshots/")
        assert screenshot["sha256"]
        assert screenshot["byte_size"] > 0
        assert screenshot["bound_to_current_provider_invocation"] is False
        assert screenshot_path.exists()
        assert screenshot_path.stat().st_size == screenshot["byte_size"]


def test_v9_video_workflow_quality_agent_checks_real_tui_and_redaction_boundaries() -> None:
    quality = _load_json(QUALITY_PATH)
    data = _load_json(DATA_PATH)

    assert quality["status"] == "PASS"
    assert data["quality_agent_report"]["status"] == "PASS"
    expected_checks = {
        "storyboard_shot_count_is_four",
        "style_bible_consistent",
        "character_bible_consistent",
        "image_files_exist_and_nonempty",
        "forbidden_completion_claims_absent",
        "provider_payload_not_stored",
        "real_tui_screenshots_present",
        "source_agent_direct_mutation_denied",
    }
    assert expected_checks <= set(quality["checks"])
    for check_name in expected_checks:
        assert quality["checks"][check_name] == "PASS"
        assert data["quality_agent_report"]["checks"][check_name] == "PASS"
    assert quality["forbidden_claim_hits"] == []


def test_v9_video_workflow_agent_state_drawio_is_valid_xml() -> None:
    parsed = ET.parse(DRAWIO_PATH)

    assert parsed.getroot().tag == "mxfile"

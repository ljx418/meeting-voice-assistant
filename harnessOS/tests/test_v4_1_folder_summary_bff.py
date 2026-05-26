"""V4.1-A local folder summary BFF route tests."""

from __future__ import annotations

import json
from pathlib import Path

from fastapi.testclient import TestClient

from apps.api import create_app

from v4_0_reference_support import SCOPE_QUERY, assert_no_forbidden_text, build_gateway


FIXTURE_ROOT = Path("tests/fixtures/desktop/技术分享")


def _client(monkeypatch, tmp_path) -> TestClient:
    monkeypatch.setenv("HARNESS_V3_5_DEV_MODE", "1")
    return TestClient(create_app(gateway_service=build_gateway(tmp_path)))


def _authorize(client: TestClient) -> dict:
    return client.post(
        f"/bff/v4_1/folder-summary/authorize{SCOPE_QUERY}",
        json={"folder_path": "Desktop/技术分享", "user_confirmed": True, "source": "folder_input_inspector"},
    ).json()


def test_fixture_exists_for_desktop_folder_summary() -> None:
    assert (FIXTURE_ROOT / "AgentOS" / "01-架构.md").exists()
    assert (FIXTURE_ROOT / "AgentOS" / "02-工作流.md").exists()
    assert (FIXTURE_ROOT / "前端低代码" / "画布设计.md").exists()
    assert (FIXTURE_ROOT / "前端低代码" / "节点库.md").exists()
    assert (FIXTURE_ROOT / "项目复盘" / "周报.md").exists()
    assert (FIXTURE_ROOT / "未支持" / "test.pdf").exists()
    assert (FIXTURE_ROOT / "空文件夹").is_dir()


def test_authorize_and_debug_scan_do_not_generate_summary(monkeypatch, tmp_path) -> None:
    client = _client(monkeypatch, tmp_path)
    authorization = _authorize(client)

    scan = client.post(
        f"/bff/v4_1/folder-summary/debug-scan{SCOPE_QUERY}",
        json={"authorization_id": authorization["authorization_id"]},
    ).json()

    assert authorization["status"] == "authorized"
    assert scan["total_file_count"] == 6
    assert scan["markdown_file_count"] == 5
    assert scan["child_folder_count"] == 5
    assert scan["unsupported_file_count"] == 1
    assert scan["unsupported_files"] == ["未支持/test.pdf"]
    assert scan["empty_folders"] == ["空文件夹"]
    assert "summary" not in json.dumps(scan, ensure_ascii=False).lower()
    assert_no_forbidden_text({"authorization": authorization, "scan": scan})


def test_folder_summary_proposal_requires_user_confirmed_apply_publish_run(monkeypatch, tmp_path) -> None:
    client = _client(monkeypatch, tmp_path)
    authorization = _authorize(client)
    proposal = client.post(
        f"/bff/v4_1/folder-summary/proposals{SCOPE_QUERY}",
        json={"folder_path": "Desktop/技术分享", "source": "workflow_console"},
    ).json()

    assert proposal["status"] == "proposed"
    assert [node["station_id"] for node in proposal["nodes"]] == [
        "folder_input",
        "folder_scan",
        "markdown_filter",
        "markdown_parse",
        "folder_group",
        "per_folder_summary",
        "overview_summary",
        "quality_check",
        "artifact_publish",
    ]

    denied = client.post(
        f"/bff/v4_1/folder-summary/proposals/{proposal['proposal_id']}/apply{SCOPE_QUERY}",
        json={"user_confirmed": True, "source": "agent"},
    ).json()
    assert denied["error"]["code"] == "METHOD_FORBIDDEN"

    applied = client.post(
        f"/bff/v4_1/folder-summary/proposals/{proposal['proposal_id']}/apply{SCOPE_QUERY}",
        json={"user_confirmed": True, "source": "editing_panel", "authorization_id": authorization["authorization_id"]},
    ).json()
    assert applied["status"] == "applied"
    assert applied["resource"]["draft_revision"] == 2

    published = client.post(
        f"/bff/v4_1/folder-summary/proposals/{proposal['proposal_id']}/publish{SCOPE_QUERY}",
        json={"user_confirmed": True, "source": "editing_panel"},
    ).json()
    assert published["status"] == "published"

    run = client.post(
        f"/bff/v4_1/folder-summary/proposals/{proposal['proposal_id']}/start-local-workflow{SCOPE_QUERY}",
        json={"user_confirmed": True, "source": "run_panel", "authorization_id": authorization["authorization_id"]},
    ).json()
    assert run["status"] == "completed"
    assert [node["station_id"] for node in run["nodes"]] == [node["station_id"] for node in proposal["nodes"]]
    assert {artifact["name"] for artifact in run["artifacts"]} == {
        "AgentOS_总结.md",
        "前端低代码_总结.md",
        "项目复盘_总结.md",
        "总览总结.md",
        "quality_report.json",
    }
    assert run["quality_report"]["unsupported_files"] == ["未支持/test.pdf"]
    assert run["quality_report"]["empty_folders"] == ["空文件夹"]
    assert_no_forbidden_text({"proposal": proposal, "run": run})


def test_folder_summary_artifacts_have_required_sections_and_are_recoverable(monkeypatch, tmp_path) -> None:
    client = _client(monkeypatch, tmp_path)
    authorization = _authorize(client)
    proposal = client.post(
        f"/bff/v4_1/folder-summary/proposals{SCOPE_QUERY}",
        json={"folder_path": "Desktop/技术分享", "source": "workflow_console"},
    ).json()
    proposal_id = proposal["proposal_id"]
    client.post(f"/bff/v4_1/folder-summary/proposals/{proposal_id}/apply{SCOPE_QUERY}", json={"user_confirmed": True, "source": "editing_panel"})
    client.post(f"/bff/v4_1/folder-summary/proposals/{proposal_id}/publish{SCOPE_QUERY}", json={"user_confirmed": True, "source": "editing_panel"})
    run = client.post(
        f"/bff/v4_1/folder-summary/proposals/{proposal_id}/start-local-workflow{SCOPE_QUERY}",
        json={"user_confirmed": True, "source": "run_panel", "authorization_id": authorization["authorization_id"]},
    ).json()

    recovered = client.get(f"/bff/v4_1/folder-summary/instances/{run['workflow_instance_id']}{SCOPE_QUERY}").json()
    artifacts = client.get(f"/bff/v4_1/folder-summary/instances/{run['workflow_instance_id']}/artifacts{SCOPE_QUERY}").json()
    quality = client.get(f"/bff/v4_1/folder-summary/instances/{run['workflow_instance_id']}/quality-report{SCOPE_QUERY}").json()

    assert recovered["workflow_instance_id"] == run["workflow_instance_id"]
    assert quality["status"] == "passed"
    summary = next(item for item in artifacts if item["name"] == "AgentOS_总结.md")
    for section in ("内容概览", "核心主题", "关键知识点", "重要文件列表", "引用文件"):
        assert section in summary["content"]
    assert_no_forbidden_text({"recovered": recovered, "artifacts": artifacts, "quality": quality})


def test_folder_summary_blocks_unauthorized_and_disallowed_paths(monkeypatch, tmp_path) -> None:
    client = _client(monkeypatch, tmp_path)
    unauthorized = client.post(
        f"/bff/v4_1/folder-summary/debug-scan{SCOPE_QUERY}",
        json={"authorization_id": "missing"},
    ).json()
    assert unauthorized["error"]["code"] == "AUTH_FORBIDDEN"

    disallowed = client.post(
        f"/bff/v4_1/folder-summary/authorize{SCOPE_QUERY}",
        json={"folder_path": "/", "user_confirmed": True, "source": "folder_input_inspector"},
    ).json()
    assert disallowed["error"]["code"] == "INVALID_PARAMS"


def test_folder_summary_failure_rerun_preserves_attempt_history(monkeypatch, tmp_path) -> None:
    client = _client(monkeypatch, tmp_path)
    authorization = client.post(
        f"/bff/v4_1/folder-summary/authorize{SCOPE_QUERY}",
        json={"folder_path": "tests/fixtures/desktop/技术分享_损坏", "user_confirmed": True, "source": "folder_input_inspector"},
    ).json()
    proposal = client.post(
        f"/bff/v4_1/folder-summary/proposals{SCOPE_QUERY}",
        json={"folder_path": "tests/fixtures/desktop/技术分享_损坏", "source": "workflow_console"},
    ).json()
    proposal_id = proposal["proposal_id"]
    client.post(f"/bff/v4_1/folder-summary/proposals/{proposal_id}/apply{SCOPE_QUERY}", json={"user_confirmed": True, "source": "editing_panel", "authorization_id": authorization["authorization_id"]})
    client.post(f"/bff/v4_1/folder-summary/proposals/{proposal_id}/publish{SCOPE_QUERY}", json={"user_confirmed": True, "source": "editing_panel"})
    failed = client.post(
        f"/bff/v4_1/folder-summary/proposals/{proposal_id}/start-local-workflow{SCOPE_QUERY}",
        json={"user_confirmed": True, "source": "run_panel", "authorization_id": authorization["authorization_id"]},
    ).json()

    parse_node = next(node for node in failed["nodes"] if node["station_id"] == "markdown_parse")
    assert failed["status"] == "failed"
    assert parse_node["status"] == "failed"
    assert "Markdown parse failed" in parse_node["error"]

    denied = client.post(
        f"/bff/v4_1/folder-summary/instances/{failed['workflow_instance_id']}/rerun-node{SCOPE_QUERY}",
        json={"station_id": "markdown_parse", "user_confirmed": True, "source": "agent"},
    ).json()
    assert denied["error"]["code"] == "METHOD_FORBIDDEN"

    rerun = client.post(
        f"/bff/v4_1/folder-summary/instances/{failed['workflow_instance_id']}/rerun-node{SCOPE_QUERY}",
        json={"station_id": "markdown_parse", "user_confirmed": True, "source": "run_panel"},
    ).json()
    recovered_parse_node = next(node for node in rerun["nodes"] if node["station_id"] == "markdown_parse")
    assert rerun["status"] == "completed"
    assert [attempt["status"] for attempt in recovered_parse_node["attempts"]] == ["failed", "completed"]
    assert "Markdown parse failed" in recovered_parse_node["attempts"][0]["error"]
    assert rerun["quality_report"]["status"] == "passed"
    assert_no_forbidden_text(rerun)


def test_folder_summary_governance_evidence_chain_uses_real_operations(monkeypatch, tmp_path) -> None:
    client = _client(monkeypatch, tmp_path)
    authorization = _authorize(client)
    proposal = client.post(
        f"/bff/v4_1/folder-summary/proposals{SCOPE_QUERY}",
        json={"folder_path": "Desktop/技术分享", "source": "workflow_console"},
    ).json()
    proposal_id = proposal["proposal_id"]
    apply_result = client.post(
        f"/bff/v4_1/folder-summary/proposals/{proposal_id}/apply{SCOPE_QUERY}",
        json={"user_confirmed": True, "source": "editing_panel", "authorization_id": authorization["authorization_id"]},
    ).json()
    publish_result = client.post(
        f"/bff/v4_1/folder-summary/proposals/{proposal_id}/publish{SCOPE_QUERY}",
        json={"user_confirmed": True, "source": "editing_panel"},
    ).json()
    run = client.post(
        f"/bff/v4_1/folder-summary/proposals/{proposal_id}/start-local-workflow{SCOPE_QUERY}",
        json={"user_confirmed": True, "source": "run_panel", "authorization_id": authorization["authorization_id"]},
    ).json()
    patch = client.post(
        f"/bff/v4_1/folder-summary/instances/{run['workflow_instance_id']}/agent-debug-proposal{SCOPE_QUERY}",
        json={"requested_change": "empty_folder_placeholder_summary"},
    ).json()
    evidence = client.get(
        f"/bff/v4_1/folder-summary/instances/{run['workflow_instance_id']}/operation-evidence{SCOPE_QUERY}"
    ).json()
    review = client.get(
        f"/bff/v4_1/folder-summary/instances/{run['workflow_instance_id']}/governance-review{SCOPE_QUERY}"
    ).json()

    operations = {item["operation"] for item in evidence}
    assert apply_result["evidence"]["user_confirmed"] is True
    assert publish_result["evidence"]["user_confirmed"] is True
    assert patch["status"] == "proposed"
    assert {
        "workflow.folder_summary.apply",
        "workflow.folder_summary.publish",
        "workflow.folder_summary.run",
        "workflow.folder_summary.agent_debug_fix_proposal",
    }.issubset(operations)
    assert review["summary"]["evidence_count"] == len(evidence)
    assert all(item["redaction_status"] == "redacted" for item in evidence)
    assert_no_forbidden_text({"evidence": evidence, "review": review})

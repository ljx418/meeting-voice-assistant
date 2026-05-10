from __future__ import annotations

import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from core.packs import DomainPackManifest, PackRegistry, build_default_pack_registry


def test_default_pack_registry_loads_active_and_stub_packs():
    registry = build_default_pack_registry()

    packs = registry.list_packs()
    names = {pack["name"] for pack in packs}

    assert names == {"meeting", "knowledge", "investment", "interview", "video_studio"}
    assert {pack["name"] for pack in registry.list_packs(status="active")} == {
        "meeting",
        "knowledge",
        "video_studio",
    }
    assert {pack["name"] for pack in registry.list_packs(status="stub")} == {
        "investment",
        "interview",
    }


def test_pack_registry_resolves_pack_by_domain_and_workflow():
    registry = build_default_pack_registry()

    meeting = registry.get_pack("meeting")
    knowledge = registry.get_workflow_pack("knowledge.workflow")

    assert meeting is not None
    assert meeting.domain == "meeting"
    assert meeting.status == "active"
    assert "meeting.workflow" in meeting.workflows
    assert knowledge is not None
    assert knowledge.name == "knowledge"


def test_pack_registry_evaluates_default_pack_assembly():
    registry = build_default_pack_registry()

    assemblies = {
        assembly.pack_name: assembly
        for assembly in registry.list_assemblies(
            supported_workflows={"meeting.workflow", "knowledge.workflow", "video.workflow"},
            available_connectors={
                "meeting_voice_mcp",
                "funasr_mcp",
                "local.knowledge",
                "data_service_mcp",
                "remote_comfyui",
            },
                available_connector_capabilities={
                    "funasr_mcp": {
                        "capabilities": {"audio.transcribe"},
                        "tools": {"funasr_recognize_file"},
                    },
                    "meeting_voice_mcp": {
                        "capabilities": {"meeting.analyze", "minutes.generate"},
                        "tools": {
                            "meeting_analyze_text",
                            "meeting_process_file",
                            "meeting_build_minutes",
                        },
                    },
                    "data_service_mcp": {
                        "capabilities": {
                            "knowledge.lifecycle",
                            "knowledge.source",
                            "knowledge.build",
                            "knowledge.query",
                            "knowledge.summarize",
                            "knowledge.citation",
                        },
                        "tools": {
                            "knowledge_workspace_create",
                        "knowledge_workspace_list",
                        "knowledge_workspace_describe",
                        "knowledge_source_import",
                        "knowledge_source_list",
                        "knowledge_source_remove",
                        "knowledge_build_start",
                        "knowledge_build_status",
                        "knowledge_build_cancel",
                        "knowledge_workspace_archive",
                        "knowledge_ingest_v2",
                        "knowledge_query_v2",
                        "knowledge_quality_summary_v2",
                        "knowledge_correction_plan_v2",
                        "knowledge_quality_feedback_v2",
                        "knowledge_correction_rules_v2",
                        "knowledge_review_correction_rule_v2",
                        "knowledge_query",
                        "knowledge_quality_summary",
                        "knowledge_quality_feedback",
                        "knowledge_correction_rules",
                        "knowledge_review_correction_rule",
                        "knowledge_correction_plan",
                    },
                    "resources": {
                        "data_service://summary",
                        "data_service://layout",
                        "data_service://build-status",
                        "data_service://quality-report",
                    },
                },
                "remote_comfyui": {"modes": {"txt2img", "txt2video", "image_to_video"}},
            },
            available_policy_bundles={
                "meeting.default",
                "meeting.standard",
                "knowledge.default",
                "knowledge.standard",
                "video.planning",
            },
        )
    }

    assert assemblies["meeting"].status == "assembled"
    assert assemblies["meeting"].app_id == "meeting"
    assert assemblies["meeting"].conflicts == ()
    assert assemblies["meeting"].registered_workflows == ("meeting.workflow",)
    assert assemblies["meeting"].manifest_schema_version == "1"
    assert assemblies["meeting"].workflow_dsl["meeting.workflow"]["steps"][0]["id"] == "transcribe"
    assert assemblies["meeting"].skill_refs == ("meeting-minutes", "action-items")
    assert assemblies["meeting"].policy_bundles == ("meeting.default",)
    assert assemblies["meeting"].connector_refs == ("meeting_voice_mcp", "funasr_mcp")
    assert "audio.transcribe" in assemblies["meeting"].connector_capabilities["funasr_mcp"]["capabilities"]
    assert "funasr_recognize_file" in assemblies["meeting"].connector_capabilities["funasr_mcp"]["tools"]
    assert "meeting.analyze" in assemblies["meeting"].connector_capabilities["meeting_voice_mcp"]["capabilities"]
    assert "meeting_process_file" in assemblies["meeting"].connector_capabilities["meeting_voice_mcp"]["tools"]
    assert assemblies["meeting"].artifact_schemas["minutes"]["parents"] == ["result"]
    meeting_manifest = registry.get_pack("meeting")
    assert meeting_manifest is not None
    assert "validation_audio_dir" not in meeting_manifest.metadata
    assert assemblies["knowledge"].status == "assembled"
    assert assemblies["knowledge"].workflow_dsl["knowledge.workflow"]["entrypoint"] == (
        "packs.knowledge.workflow:KnowledgeWorkflow"
    )
    assert assemblies["knowledge"].policy_bundles == ("knowledge.default",)
    assert assemblies["knowledge"].connector_refs == ("local.knowledge", "data_service_mcp")
    assert assemblies["knowledge"].workflow_templates["knowledge.lifecycle"]["kind"] == "typed_dag"
    assert assemblies["knowledge"].agents[0]["agent_id"] == "knowledge.curator"
    assert assemblies["knowledge"].workflow_templates["knowledge.lifecycle"]["nodes"][0]["type"] == "connector"
    assert "knowledge.lifecycle" in assemblies["knowledge"].connector_capabilities["data_service_mcp"]["capabilities"]
    assert "knowledge_workspace_archive" in assemblies["knowledge"].connector_capabilities["data_service_mcp"]["tools"]
    assert "knowledge_query_v2" in assemblies["knowledge"].connector_capabilities["data_service_mcp"]["tools"]
    assert assemblies["knowledge"].artifact_schemas["source_reference"]["lineage"] == "root"
    assert assemblies["knowledge"].artifact_schemas["citation_bundle"]["parents"] == ["brief"]
    assert assemblies["investment"].status == "stub"
    assert assemblies["video_studio"].status == "assembled"
    assert assemblies["video_studio"].registered_workflows == ("video.workflow",)
    assert assemblies["video_studio"].workflow_templates["video.pipeline"]["kind"] == "multi_agent_typed_dag"
    assert {agent["agent_id"] for agent in assemblies["video_studio"].agents} >= {"studio.lead", "qa.publisher"}
    assert assemblies["video_studio"].workflow_templates["video.pipeline"]["nodes"][1]["type"] == "agent"


def test_pack_registry_marks_active_pack_blocked_when_connector_missing():
    registry = PackRegistry(
        [
            DomainPackManifest(
                name="demo",
                version="0.1.0",
                domain="demo",
                status="active",
                workflows=("demo.workflow",),
                connectors=("missing.connector",),
            )
        ]
    )

    assembly = registry.evaluate_assembly(
        "demo",
        supported_workflows={"demo.workflow"},
        available_connectors=set(),
        available_policy_bundles=set(),
    )

    assert assembly.status == "blocked"
    assert assembly.missing_dependencies == ("connector:missing.connector",)
    assert assembly.to_dict()["blocked_reason"] == "Pack is blocked by missing or disabled connectors."


def test_pack_registry_marks_active_pack_blocked_when_policy_bundle_missing():
    registry = PackRegistry(
        [
            DomainPackManifest(
                name="demo",
                version="0.1.0",
                domain="demo",
                status="active",
                workflows=("demo.workflow",),
                policy_bundles=("demo.policy",),
            )
        ]
    )

    assembly = registry.evaluate_assembly(
        "demo",
        supported_workflows={"demo.workflow"},
        available_connectors=set(),
        available_policy_bundles=set(),
    )

    assert assembly.status == "degraded"
    assert assembly.missing_dependencies == ("policy_bundle:demo.policy",)
    assert assembly.to_dict()["blocked_reason"] == "Pack is degraded by missing policy bundles."


def test_pack_registry_marks_active_pack_blocked_when_schema_version_incompatible():
    registry = PackRegistry(
        [
            DomainPackManifest(
                name="demo",
                version="0.1.0",
                domain="demo",
                manifest_schema_version="99",
                status="active",
                workflows=("demo.workflow",),
            )
        ]
    )

    assembly = registry.evaluate_assembly(
        "demo",
        supported_workflows={"demo.workflow"},
        available_connectors=set(),
        available_policy_bundles=set(),
        compatible_manifest_schema_versions={"1"},
    )

    assert assembly.status == "blocked"
    assert assembly.missing_dependencies == ("manifest_schema:99",)


def test_pack_registry_marks_active_pack_blocked_when_connector_capability_missing():
    registry = PackRegistry(
        [
            DomainPackManifest(
                name="demo",
                version="0.1.0",
                domain="demo",
                status="active",
                workflows=("demo.workflow",),
                connectors=("demo.connector",),
                connector_capabilities={"demo.connector": {"tools": ["required_tool"]}},
            )
        ]
    )

    assembly = registry.evaluate_assembly(
        "demo",
        supported_workflows={"demo.workflow"},
        available_connectors={"demo.connector"},
        available_connector_capabilities={"demo.connector": {"tools": {"other_tool"}}},
        available_policy_bundles=set(),
    )

    assert assembly.status == "degraded"
    assert assembly.missing_dependencies == ("connector_capability:demo.connector:tools:required_tool",)
    assert (
        assembly.to_dict()["blocked_reason"]
        == "Pack is degraded by missing non-blocking connector capabilities."
    )


def test_pack_registry_surfaces_conflicts_for_undeclared_artifact_schema():
    registry = PackRegistry(
        [
            DomainPackManifest(
                name="demo",
                version="0.1.0",
                domain="demo",
                status="active",
                workflows=("demo.workflow",),
                artifact_kinds=("result",),
                artifact_schemas={"preview": {"mime": "application/json"}},
            )
        ]
    )

    assembly = registry.evaluate_assembly(
        "demo",
        supported_workflows={"demo.workflow"},
        available_connectors=set(),
        available_policy_bundles=set(),
    )

    assert assembly.status == "blocked"
    assert assembly.conflicts == ("artifact_schema:preview:undeclared_kind",)
    assert "artifact_schema:preview:undeclared_kind" in assembly.to_dict()["conflicts"]
    assert assembly.to_dict()["blocked_reason"] == "Pack has assembly conflicts."


def test_pack_registry_surfaces_precise_blocked_reason_for_dependencies_and_conflicts():
    registry = PackRegistry(
        [
            DomainPackManifest(
                name="demo",
                version="0.1.0",
                domain="demo",
                status="active",
                workflows=("demo.workflow",),
                connectors=("missing.connector",),
                artifact_kinds=("result",),
                artifact_schemas={"preview": {"mime": "application/json"}},
            )
        ]
    )

    assembly = registry.evaluate_assembly(
        "demo",
        supported_workflows={"demo.workflow"},
        available_connectors=set(),
        available_policy_bundles=set(),
    )

    assert assembly.status == "blocked"
    assert assembly.to_dict()["blocked_reason"] == "Pack has blocked assembly dependencies and conflicts."


def test_pack_registry_rejects_duplicate_pack_name() -> None:
    first = DomainPackManifest(name="demo", version="0.1.0", domain="demo-a", workflows=("demo.a",))
    second = DomainPackManifest(name="demo", version="0.2.0", domain="demo-b", workflows=("demo.b",))

    with pytest.raises(ValueError, match="pack_name=demo"):
        PackRegistry([first, second])


def test_pack_registry_rejects_duplicate_domain() -> None:
    first = DomainPackManifest(name="demo_a", version="0.1.0", domain="demo", workflows=("demo.a",))
    second = DomainPackManifest(name="demo_b", version="0.2.0", domain="demo", workflows=("demo.b",))

    with pytest.raises(ValueError, match="domain=demo"):
        PackRegistry([first, second])


def test_pack_registry_rejects_duplicate_workflow_id() -> None:
    first = DomainPackManifest(name="demo_a", version="0.1.0", domain="demo-a", workflows=("shared.workflow",))
    second = DomainPackManifest(name="demo_b", version="0.2.0", domain="demo-b", workflows=("shared.workflow",))

    with pytest.raises(ValueError, match="workflow_id=shared.workflow"):
        PackRegistry([first, second])


def test_pack_registry_load_from_paths_rejects_conflicting_external_packs(tmp_path) -> None:
    root_a = tmp_path / "packs-a"
    root_b = tmp_path / "packs-b"
    for root, version in ((root_a, "0.1.0"), (root_b, "0.2.0")):
        pack_dir = root / "demo"
        pack_dir.mkdir(parents=True)
        (pack_dir / "manifest.json").write_text(
            (
                "{\n"
                '  "name": "demo",\n'
                f'  "version": "{version}",\n'
                '  "manifest_schema_version": "1",\n'
                '  "domain": "demo",\n'
                '  "description": "Conflict test",\n'
                '  "status": "active",\n'
                '  "workflows": ["demo.workflow"],\n'
                '  "metadata": {"target_version": "3.0"}\n'
                "}\n"
            ),
            encoding="utf-8",
        )

    with pytest.raises(ValueError, match="Pack registry conflict"):
        PackRegistry.load_from_paths([root_a, root_b])


def test_pack_registry_blocks_pack_when_app_profile_does_not_enable_required_connector() -> None:
    registry = PackRegistry(
        [
            DomainPackManifest(
                name="demo",
                version="0.1.0",
                domain="demo",
                status="active",
                workflows=("demo.workflow",),
                connectors=("demo.connector",),
            )
        ]
    )

    assembly = registry.evaluate_assembly(
        "demo",
        supported_workflows={"demo.workflow"},
        available_connectors={"demo.connector"},
        app_enabled_connectors_by_domain={"demo": set()},
        available_policy_bundles=set(),
    )

    assert assembly.status == "blocked"
    assert assembly.missing_dependencies == ("app_profile_connector:demo.connector",)
    assert "Add connector demo.connector to the matching AppProfile." in assembly.to_dict()["next_actions"]


def test_pack_registry_blocks_pack_when_connector_is_only_enabled_in_app_profile() -> None:
    registry = PackRegistry(
        [
            DomainPackManifest(
                name="demo",
                version="0.1.0",
                domain="demo",
                status="active",
                workflows=("demo.workflow",),
                connectors=("demo.connector",),
            )
        ]
    )

    assembly = registry.evaluate_assembly(
        "demo",
        supported_workflows={"demo.workflow"},
        available_connectors=set(),
        app_enabled_connectors_by_domain={"demo": {"demo.connector"}},
        available_policy_bundles=set(),
    )

    assert assembly.status == "blocked"
    assert assembly.missing_dependencies == ("connector:demo.connector",)


def test_pack_registry_marks_external_pack_blocked_when_target_version_incompatible(tmp_path) -> None:
    manifest_path = tmp_path / "external" / "demo" / "manifest.json"
    manifest_path.parent.mkdir(parents=True)
    registry = PackRegistry(
        [
            DomainPackManifest(
                name="demo",
                version="0.1.0",
                domain="demo",
                status="active",
                workflows=("demo.workflow",),
                metadata={"target_version": "2.9"},
                manifest_path=str(manifest_path),
            )
        ]
    )

    assembly = registry.evaluate_assembly(
        "demo",
        supported_workflows={"demo.workflow"},
        available_connectors=set(),
        app_enabled_connectors_by_domain={"demo": set()},
        available_policy_bundles=set(),
    )

    assert assembly.status == "blocked"
    assert assembly.missing_dependencies == ("target_version:2.9",)
    assert assembly.to_dict()["blocked_reason"] == "Pack is blocked by an incompatible external pack target_version."
    assert assembly.to_dict()["next_actions"] == [
        "Align external pack target_version to 3.0 (current 2.9)."
    ]


def test_pack_registry_marks_external_pack_degraded_when_target_version_missing(tmp_path) -> None:
    manifest_path = tmp_path / "external" / "demo" / "manifest.json"
    manifest_path.parent.mkdir(parents=True)
    registry = PackRegistry(
        [
            DomainPackManifest(
                name="demo",
                version="0.1.0",
                domain="demo",
                status="active",
                workflows=("demo.workflow",),
                manifest_path=str(manifest_path),
            )
        ]
    )

    assembly = registry.evaluate_assembly(
        "demo",
        supported_workflows={"demo.workflow"},
        available_connectors=set(),
        app_enabled_connectors_by_domain={"demo": set()},
        available_policy_bundles=set(),
    )

    assert assembly.status == "degraded"
    assert assembly.missing_dependencies == ("target_version:missing",)
    assert assembly.to_dict()["blocked_reason"] == "Pack is degraded because metadata.target_version is not declared."
    assert assembly.to_dict()["next_actions"] == [
        "Declare metadata.target_version=3.0 for the external pack."
    ]


def test_pack_registry_lists_agent_contracts():
    registry = build_default_pack_registry()

    knowledge_agents = registry.list_agents(domain="knowledge")
    fetched = registry.get_agent("knowledge.curator")

    assert [agent["agent_id"] for agent in knowledge_agents] == [
        "knowledge.curator",
        "knowledge.quality_reviewer",
    ]
    assert fetched is not None
    assert fetched["domain"] == "knowledge"
    assert fetched["pack_name"] == "knowledge"

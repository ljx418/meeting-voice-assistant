from __future__ import annotations

"""PhaseA frozen baseline tests for multi-app scope and namespace isolation."""

import pytest

from apps.gateway.artifacts import ArtifactError, ArtifactRegistry
from apps.gateway.protocol import RpcRequest
from apps.gateway.service import GatewayService
from core.apps import AppProfile, AppRegistry, build_default_app_registry, resolve_scope_context
from core.packs import build_default_pack_registry
from core.protocol import ArtifactRecord, JobRecord, SessionRecord, ThreadRecord
from core.services import CoreAppService
from core.stores import CoreSQLiteStore


def test_default_app_registry_contains_v3_profiles() -> None:
    registry = build_default_app_registry()

    profiles = {profile["app_id"]: profile for profile in registry.list_profiles()}

    assert set(profiles) == {"meeting", "knowledge", "interview", "investment", "video_studio"}
    assert profiles["meeting"]["connector_refs"] == ["meeting_voice_mcp", "funasr_mcp"]
    assert profiles["knowledge"]["connector_refs"] == ["local.knowledge", "data_service_mcp"]
    assert profiles["knowledge"]["default_pack"] == "knowledge"


def test_default_pack_registry_loads_external_pack_roots(tmp_path, monkeypatch) -> None:
    external_root = tmp_path / "external-packs"
    pack_dir = external_root / "custom_pack"
    pack_dir.mkdir(parents=True)
    (pack_dir / "manifest.json").write_text(
        """
{
  "name": "custom_pack",
  "version": "0.1.0",
  "manifest_schema_version": "1",
  "domain": "custom",
  "description": "External test pack",
  "status": "active",
  "workflows": [],
  "metadata": {"external": true, "target_version": "3.0"}
}
""".strip()
        + "\n",
        encoding="utf-8",
    )
    monkeypatch.setenv("HARNESS_PACK_PATHS", str(external_root))

    registry = build_default_pack_registry()

    pack = registry.get_pack("custom_pack")
    assert pack is not None
    assert pack.domain == "custom"
    assert pack.metadata["external"] is True


def test_default_pack_registry_loads_pack_paths_from_app_registry(tmp_path) -> None:
    external_root = tmp_path / "profile-packs"
    pack_dir = external_root / "profile_pack"
    pack_dir.mkdir(parents=True)
    (pack_dir / "manifest.json").write_text(
        """
{
  "name": "profile_pack",
  "version": "0.1.0",
  "manifest_schema_version": "1",
  "domain": "profile_pack",
  "description": "Profile path test pack",
  "status": "active",
  "workflows": [],
  "connectors": ["profile.connector"],
  "metadata": {"target_version": "3.0"}
}
""".strip()
        + "\n",
        encoding="utf-8",
    )
    registry = AppRegistry(
        [
            AppProfile(
                app_id="profile_pack",
                display_name="Profile Pack",
                domain="profile_pack",
                default_pack="profile_pack",
                connector_refs=("profile.connector",),
                pack_paths=(str(external_root),),
            )
        ]
    )

    pack_registry = build_default_pack_registry(app_registry=registry)

    pack = pack_registry.get_pack("profile_pack")
    assert pack is not None
    assert pack.domain == "profile_pack"


def test_core_store_scope_filters_isolate_records(tmp_path) -> None:
    store = CoreSQLiteStore(tmp_path / "core.sqlite3")
    meeting_session = store.save_session(SessionRecord(session_id="sess_meeting", app_id="meeting"))
    knowledge_session = store.save_session(SessionRecord(session_id="sess_knowledge", app_id="knowledge"))
    meeting_thread = store.save_thread(
        ThreadRecord(session_id=meeting_session.session_id, app_id="meeting", domain="meeting")
    )
    knowledge_thread = store.save_thread(
        ThreadRecord(session_id=knowledge_session.session_id, app_id="knowledge", domain="knowledge")
    )
    meeting_artifact = store.save_artifact(
        ArtifactRecord(
            app_id="meeting",
            domain="meeting",
            kind="minutes",
            owner_session_id=meeting_session.session_id,
            owner_thread_id=meeting_thread.thread_id,
            uri="file:///tmp/minutes.md",
        )
    )
    knowledge_artifact = store.save_artifact(
        ArtifactRecord(
            app_id="knowledge",
            domain="knowledge",
            kind="brief",
            owner_session_id=knowledge_session.session_id,
            owner_thread_id=knowledge_thread.thread_id,
            uri="file:///tmp/brief.md",
        )
    )
    meeting_job = store.save_job(
        JobRecord(app_id="meeting", workflow_id="meeting.workflow", domain="meeting", status="completed")
    )
    knowledge_job = store.save_job(
        JobRecord(app_id="knowledge", workflow_id="knowledge.workflow", domain="knowledge", status="completed")
    )

    assert [record.session_id for record in store.list_sessions(app_id="meeting")] == ["sess_meeting"]
    assert [record.thread_id for record in store.list_threads(app_id="meeting")] == [meeting_thread.thread_id]
    assert [record.thread_id for record in store.list_threads(app_id="knowledge")] == [knowledge_thread.thread_id]
    assert [record.artifact_id for record in store.list_artifacts(app_id="meeting")] == [
        meeting_artifact.artifact_id
    ]
    assert [record.artifact_id for record in store.list_artifacts(app_id="knowledge")] == [
        knowledge_artifact.artifact_id
    ]
    assert [record.job_id for record in store.list_jobs(app_id="meeting")] == [meeting_job.job_id]
    assert [record.job_id for record in store.list_jobs(app_id="knowledge")] == [knowledge_job.job_id]


def test_scope_context_uses_profile_defaults_and_nested_scope_precedence() -> None:
    registry = AppRegistry(
        [
            AppProfile(
                app_id="knowledge",
                display_name="个人知识库",
                domain="knowledge",
                default_pack="knowledge",
                default_project_id="project_default",
                default_workspace_id="workspace_default",
            )
        ]
    )

    resolved = resolve_scope_context({"app_id": "knowledge"}, app_registry=registry)
    assert resolved.app_id == "knowledge"
    assert resolved.project_id == "project_default"
    assert resolved.workspace_id == "workspace_default"

    nested = resolve_scope_context(
        {
            "app_id": "meeting",
            "project_id": "top_project",
            "scope": {
                "app_id": "knowledge",
                "workspace_id": "workspace_nested",
            },
        },
        app_registry=registry,
    )
    assert nested.app_id == "knowledge"
    assert nested.project_id == "top_project"
    assert nested.workspace_id == "workspace_nested"

    explicit = resolve_scope_context(
        {
            "scope": {
                "app_id": "knowledge",
                "project_id": "project_nested",
                "workspace_id": "workspace_nested",
            }
        },
        app_registry=registry,
        project_id="project_explicit",
    )
    assert explicit.project_id == "project_explicit"
    assert explicit.workspace_id == "workspace_nested"


@pytest.mark.parametrize(
    ("params", "message"),
    [
        ({"scope": "knowledge"}, "scope must be an object when provided"),
        ({"scope": {"app_id": 1}}, "scope values must be strings when provided"),
    ],
)
def test_scope_context_rejects_invalid_scope_payloads(params, message) -> None:
    with pytest.raises(ValueError, match=message):
        resolve_scope_context(params)


def test_core_service_records_gateway_event_scope(tmp_path) -> None:
    store = CoreSQLiteStore(tmp_path / "core.sqlite3")
    service = CoreAppService(store=store)
    event = type(
        "Event",
        (),
        {
            "session_id": "sess_scope",
            "turn_id": "turn_scope",
            "type": "turn.started",
            "item_id": "item_scope",
            "data": {
                "input": "hello",
                "domain": "meeting",
                "trace_id": "trace_scope",
                "app_id": "meeting",
                "project_id": "project_a",
                "workspace_id": "workspace_a",
            },
            "model_dump": lambda self, **_kwargs: {},
        },
    )()

    service.record_gateway_event(event)

    session = service.get_session("sess_scope")
    thread = service.list_threads(app_id="meeting", project_id="project_a", workspace_id="workspace_a")[0]
    turn = service.get_turn("turn_scope")
    item = service.list_items(turn_id="turn_scope", app_id="meeting", project_id="project_a")[0]

    assert session.app_id == "meeting"
    assert thread.workspace_id == "workspace_a"
    assert turn.project_id == "project_a"
    assert item.app_id == "meeting"


def test_artifact_registry_blocks_large_and_video_inline_reads(tmp_path) -> None:
    registry = ArtifactRegistry(root=tmp_path / "artifacts", allowed_roots=[tmp_path])
    large_file = tmp_path / "large.txt"
    large_file.write_text("x" * (1024 * 1024 + 1), encoding="utf-8")
    video_file = tmp_path / "clip.mp4"
    video_file.write_bytes(b"fake")

    large = registry.register_file(str(large_file), domain="knowledge", kind="brief")
    video = registry.register_file(str(video_file), domain="video_studio", kind="render")

    with pytest.raises(ArtifactError):
        registry.read_artifact(large["artifact_id"])
    with pytest.raises(ArtifactError):
        registry.read_artifact(video["artifact_id"])
    assert registry.read_metadata(video["artifact_id"])["artifact"]["artifact_id"] == video["artifact_id"]


@pytest.mark.asyncio
async def test_gateway_app_profile_and_external_artifact_rpc(tmp_path) -> None:
    service = GatewayService(artifact_registry=ArtifactRegistry(root=tmp_path / "artifacts", allowed_roots=[tmp_path]))

    apps = await service.handle_rpc(RpcRequest(id="1", method="app.list", params={}))
    assert apps.result["count"] == 5

    registered = await service.handle_rpc(
        RpcRequest(
            id="2",
            method="artifact.register_external",
            params={
                "app_id": "video_studio",
                "external_asset_uri": "file:///external/render.mp4",
                "domain": "video_studio",
                "kind": "render",
                "mime": "video/mp4",
                "thumbnail_uri": "file:///external/thumb.jpg",
            },
        )
    )

    artifact = registered.result["artifact"]
    assert artifact["app_id"] == "video_studio"
    assert artifact["external_asset_uri"] == "file:///external/render.mp4"

    metadata = await service.handle_rpc(
        RpcRequest(
            id="3",
            method="artifact.read_metadata",
            params={"artifact_id": artifact["artifact_id"], "app_id": "video_studio"},
        )
    )
    assert metadata.result["artifact"]["thumbnail_uri"] == "file:///external/thumb.jpg"

    listed = await service.handle_rpc(
        RpcRequest(id="4", method="artifact.list", params={"app_id": "video_studio"})
    )
    assert listed.result["count"] == 1
    assert listed.result["artifacts"][0]["artifact_id"] == artifact["artifact_id"]

from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from apps.gateway.artifacts import ArtifactRegistry
from apps.gateway.artifacts import ArtifactError
from apps.gateway.protocol import RpcRequest
from apps.gateway.runtime import GatewayRuntimePool
from apps.gateway.service import GatewayService
from apps.gateway.storage import GatewaySessionStore
from core.stores import CoreSQLiteStore


def test_artifact_registry_register_list_get_read(tmp_path):
    registry = ArtifactRegistry(tmp_path / "artifacts")
    minutes = tmp_path / "minutes.md"
    minutes.write_text("# Minutes\n\n会议纪要", encoding="utf-8")

    record = registry.register_file(
        str(minutes),
        session_id="sess_demo",
        turn_id="turn_demo",
        domain="meeting",
        kind="minutes",
    )

    assert record["artifact_id"].startswith("art_")
    assert record["mime"] == "text/markdown"
    assert registry.get_artifact(record["artifact_id"])["path"] == str(minutes.resolve())
    assert registry.list_artifacts(session_id="sess_demo")[0]["kind"] == "minutes"
    assert "会议纪要" in registry.read_artifact(record["artifact_id"])["content"]


def test_artifact_gateway_rpc_register_list_get_read(tmp_path):
    analysis = tmp_path / "analysis.json"
    analysis.write_text(json.dumps({"theme": "测试会议"}, ensure_ascii=False), encoding="utf-8")

    async def run():
        service = GatewayService(artifact_registry=ArtifactRegistry(tmp_path / "artifacts"))
        registered = await service.handle_rpc(
            RpcRequest(
                id="a1",
                method="artifact.register",
                params={
                    "path": str(analysis),
                    "session_id": "sess_demo",
                    "turn_id": "turn_demo",
                    "domain": "meeting",
                    "kind": "analysis",
                },
            )
        )
        assert registered.error is None
        artifact_id = registered.result["artifact"]["artifact_id"]

        listed = await service.handle_rpc(
            RpcRequest(id="a2", method="artifact.list", params={"session_id": "sess_demo"})
        )
        assert listed.error is None
        assert listed.result["count"] == 1
        assert listed.result["artifacts"][0]["artifact_id"] == artifact_id

        fetched = await service.handle_rpc(
            RpcRequest(id="a3", method="artifact.get", params={"artifact_id": artifact_id})
        )
        assert fetched.error is None
        assert fetched.result["artifact"]["kind"] == "analysis"

        read = await service.handle_rpc(
            RpcRequest(id="a4", method="artifact.read", params={"artifact_id": artifact_id})
        )
        assert read.error is None
        assert read.result["content"]["theme"] == "测试会议"

    asyncio.run(run())


def test_artifact_gateway_scope_blocks_cross_app_get_and_read(tmp_path):
    analysis = tmp_path / "analysis.json"
    analysis.write_text(json.dumps({"theme": "测试会议"}, ensure_ascii=False), encoding="utf-8")

    async def run():
        service = GatewayService(artifact_registry=ArtifactRegistry(tmp_path / "artifacts"))
        registered = await service.handle_rpc(
            RpcRequest(
                id="a1",
                method="artifact.register",
                params={
                    "path": str(analysis),
                    "session_id": "sess_demo",
                    "turn_id": "turn_demo",
                    "domain": "meeting",
                    "kind": "analysis",
                    "scope": {"app_id": "knowledge", "workspace_id": "workspace_k"},
                },
            )
        )
        assert registered.error is None
        artifact_id = registered.result["artifact"]["artifact_id"]

        denied_get = await service.handle_rpc(
            RpcRequest(id="a2", method="artifact.get", params={"artifact_id": artifact_id, "app_id": "meeting"})
        )
        assert denied_get.error is not None
        assert denied_get.error.code == "SCOPE_MISMATCH"

        denied_read = await service.handle_rpc(
            RpcRequest(id="a3", method="artifact.read", params={"artifact_id": artifact_id, "app_id": "meeting"})
        )
        assert denied_read.error is not None
        assert denied_read.error.code == "SCOPE_MISMATCH"

        allowed = await service.handle_rpc(
            RpcRequest(
                id="a4",
                method="artifact.read",
                params={
                    "artifact_id": artifact_id,
                    "scope": {"app_id": "knowledge", "workspace_id": "workspace_k"},
                },
            )
        )
        assert allowed.error is None
        assert allowed.result["artifact"]["app_id"] == "knowledge"

    asyncio.run(run())


def test_artifact_registry_rejects_out_of_allowed_roots(tmp_path):
    registry = ArtifactRegistry(tmp_path / "artifacts", allowed_roots=[tmp_path / "allowed"])
    outside = tmp_path.parent / f"outside_{tmp_path.name}.txt"
    outside.write_text("outside", encoding="utf-8")

    try:
        try:
            registry.register_file(str(outside), session_id="sess_demo", kind="note")
        except ArtifactError as exc:
            assert "outside allowed roots" in str(exc)
        else:
            raise AssertionError("out-of-root artifact registration should fail")
    finally:
        outside.unlink(missing_ok=True)


def test_artifact_registry_blocks_audio_image_and_binary_inline_reads(tmp_path):
    registry = ArtifactRegistry(tmp_path / "artifacts", allowed_roots=[tmp_path])
    audio = tmp_path / "clip.mp3"
    image = tmp_path / "preview.png"
    binary = tmp_path / "blob.bin"
    audio.write_bytes(b"ID3demo")
    image.write_bytes(b"\x89PNG\r\n\x1a\n")
    binary.write_bytes(b"\x00\x01\x02")

    audio_record = registry.register_file(str(audio), session_id="sess_demo", kind="audio")
    image_record = registry.register_file(str(image), session_id="sess_demo", kind="preview")
    binary_record = registry.register_file(str(binary), session_id="sess_demo", kind="payload")

    with pytest.raises(ArtifactError, match="Audio artifacts cannot be read inline"):
        registry.read_artifact(audio_record["artifact_id"])
    with pytest.raises(ArtifactError, match="Image artifacts cannot be read inline"):
        registry.read_artifact(image_record["artifact_id"])
    with pytest.raises(ArtifactError, match="Binary artifacts cannot be read inline"):
        registry.read_artifact(binary_record["artifact_id"])


def test_artifact_read_rpc_returns_blocked_error_data_and_trace(tmp_path):
    video = tmp_path / "clip.mp4"
    video.write_bytes(b"fake")

    async def run():
        registry = ArtifactRegistry(tmp_path / "artifacts", allowed_roots=[tmp_path])
        pool = GatewayRuntimePool(
            store=GatewaySessionStore(tmp_path / "sessions"),
            artifact_registry=registry,
            core_store=CoreSQLiteStore(tmp_path / "core.sqlite3"),
        )
        service = GatewayService(pool)
        registered = await service.handle_rpc(
            RpcRequest(
                id="a1",
                method="artifact.register",
                params={"path": str(video), "session_id": "sess_demo", "domain": "meeting", "kind": "recording"},
            )
        )
        artifact_id = registered.result["artifact"]["artifact_id"]

        read = await service.handle_rpc(RpcRequest(id="a2", method="artifact.read", params={"artifact_id": artifact_id}))

        assert read.error is not None
        assert read.error.code == "ARTIFACT_READ_BLOCKED"
        assert read.error.data["reason"] == "media"
        assert read.error.data["artifact"]["artifact_id"] == artifact_id
        assert read.error.data["suggested_method"] == "artifact.read_metadata"
        traces = service.core_service.list_trace_records(
            trace_id=read.error.data["trace_id"],
            event_type="artifact.read",
        )
        assert traces
        assert traces[-1].status == "blocked"

    asyncio.run(run())


def test_artifact_read_rpc_blocks_invalid_utf8_as_binary(tmp_path):
    payload = tmp_path / "payload.txt"
    payload.write_bytes(b"\xff\xfe\x00\x01")

    async def run():
        registry = ArtifactRegistry(tmp_path / "artifacts", allowed_roots=[tmp_path])
        pool = GatewayRuntimePool(
            store=GatewaySessionStore(tmp_path / "sessions"),
            artifact_registry=registry,
            core_store=CoreSQLiteStore(tmp_path / "core.sqlite3"),
        )
        service = GatewayService(pool)
        registered = await service.handle_rpc(
            RpcRequest(
                id="a1",
                method="artifact.register",
                params={"path": str(payload), "session_id": "sess_demo", "domain": "meeting", "kind": "payload"},
            )
        )
        artifact_id = registered.result["artifact"]["artifact_id"]

        read = await service.handle_rpc(RpcRequest(id="a2", method="artifact.read", params={"artifact_id": artifact_id}))

        assert read.error is not None
        assert read.error.code == "ARTIFACT_READ_BLOCKED"
        assert read.error.data["reason"] == "binary"
        assert read.error.data["suggested_method"] == "artifact.read_metadata"
        traces = service.core_service.list_trace_records(
            trace_id=read.error.data["trace_id"],
            event_type="artifact.read",
        )
        assert traces[-1].status == "blocked"

    asyncio.run(run())


def test_artifact_lineage_rpc_enforces_scope_for_filters_and_anchor(tmp_path):
    meeting_root = tmp_path / "meeting.json"
    meeting_child = tmp_path / "meeting_child.json"
    knowledge_root = tmp_path / "knowledge.json"
    knowledge_child = tmp_path / "knowledge_child.json"
    for path in (meeting_root, meeting_child, knowledge_root, knowledge_child):
        path.write_text(json.dumps({"name": path.stem}), encoding="utf-8")

    async def run():
        registry = ArtifactRegistry(tmp_path / "artifacts", allowed_roots=[tmp_path])
        pool = GatewayRuntimePool(
            store=GatewaySessionStore(tmp_path / "sessions"),
            artifact_registry=registry,
            core_store=CoreSQLiteStore(tmp_path / "core.sqlite3"),
        )
        service = GatewayService(pool)
        meeting_parent = await service.handle_rpc(
            RpcRequest(
                id="m1",
                method="artifact.register",
                params={
                    "path": str(meeting_root),
                    "session_id": "sess_lineage",
                    "domain": "meeting",
                    "kind": "root",
                    "scope": {"app_id": "meeting", "workspace_id": "workspace_m"},
                },
            )
        )
        meeting_parent_id = meeting_parent.result["artifact"]["artifact_id"]
        meeting_leaf = await service.handle_rpc(
            RpcRequest(
                id="m2",
                method="artifact.register",
                params={
                    "path": str(meeting_child),
                    "session_id": "sess_lineage",
                    "domain": "meeting",
                    "kind": "leaf",
                    "metadata": {"parent_artifact_ids": [meeting_parent_id]},
                    "scope": {"app_id": "meeting", "workspace_id": "workspace_m"},
                },
            )
        )
        knowledge_parent = await service.handle_rpc(
            RpcRequest(
                id="k1",
                method="artifact.register",
                params={
                    "path": str(knowledge_root),
                    "session_id": "sess_lineage",
                    "domain": "knowledge",
                    "kind": "root",
                    "scope": {"app_id": "knowledge", "workspace_id": "workspace_k"},
                },
            )
        )
        knowledge_parent_id = knowledge_parent.result["artifact"]["artifact_id"]
        knowledge_leaf = await service.handle_rpc(
            RpcRequest(
                id="k2",
                method="artifact.register",
                params={
                    "path": str(knowledge_child),
                    "session_id": "sess_lineage",
                    "domain": "knowledge",
                    "kind": "leaf",
                    "metadata": {"parent_artifact_ids": [knowledge_parent_id]},
                    "scope": {"app_id": "knowledge", "workspace_id": "workspace_k"},
                },
            )
        )
        knowledge_leaf_id = knowledge_leaf.result["artifact"]["artifact_id"]

        lineage = await service.handle_rpc(
            RpcRequest(
                id="lineage",
                method="artifact.lineage",
                params={
                    "session_id": "sess_lineage",
                    "scope": {"app_id": "meeting", "workspace_id": "workspace_m"},
                },
            )
        )
        assert lineage.error is None
        assert {item["artifact_id"] for item in lineage.result["artifacts"]} == {
            meeting_parent_id,
            meeting_leaf.result["artifact"]["artifact_id"],
        }

        denied = await service.handle_rpc(
            RpcRequest(
                id="denied",
                method="artifact.lineage",
                params={
                    "artifact_id": knowledge_leaf_id,
                    "scope": {"app_id": "meeting", "workspace_id": "workspace_m"},
                },
            )
        )
        assert denied.error is not None
        assert denied.error.code == "SCOPE_MISMATCH"

        all_scope = await service.handle_rpc(
            RpcRequest(
                id="all",
                method="artifact.lineage",
                params={"session_id": "sess_lineage", "scope_mode": "all"},
            )
        )
        assert all_scope.error is None
        assert all_scope.result["count"] == 4

    asyncio.run(run())

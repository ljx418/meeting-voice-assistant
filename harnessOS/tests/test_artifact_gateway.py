from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from apps.gateway.artifacts import ArtifactRegistry
from apps.gateway.artifacts import ArtifactError
from apps.gateway.protocol import RpcRequest
from apps.gateway.service import GatewayService


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
        assert denied_get.error.code == "INVALID_PARAMS"

        denied_read = await service.handle_rpc(
            RpcRequest(id="a3", method="artifact.read", params={"artifact_id": artifact_id, "app_id": "meeting"})
        )
        assert denied_read.error is not None
        assert denied_read.error.code == "INVALID_PARAMS"

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

from __future__ import annotations

from apps.gateway.protocol import RpcRequest

from tests.knowledge_phase_e_helpers import build_knowledge_service, run_async, run_knowledge_turn


def test_knowledge_scope_isolated_from_meeting_queries(tmp_path):
    async def run():
        service = build_knowledge_service(tmp_path)
        session_id, _ = await run_knowledge_turn(service, workspace_id="workspace_k")

        denied_lineage = await service.handle_rpc(
            RpcRequest(
                id="meeting-lineage",
                method="artifact.lineage",
                params={"session_id": session_id, "domain": "knowledge", "app_id": "meeting"},
            )
        )
        assert denied_lineage.error is None
        assert denied_lineage.result["count"] == 0

        allowed_lineage = await service.handle_rpc(
            RpcRequest(
                id="knowledge-lineage",
                method="artifact.lineage",
                params={"session_id": session_id, "domain": "knowledge", "app_id": "knowledge"},
            )
        )
        assert allowed_lineage.error is None
        assert allowed_lineage.result["count"] >= 4

    run_async(run())


def test_knowledge_workspace_scope_filters_artifacts(tmp_path):
    async def run():
        service = build_knowledge_service(tmp_path)
        await run_knowledge_turn(service, workspace_id="workspace_a", user_input="检索知识库 A")
        await run_knowledge_turn(service, workspace_id="workspace_b", user_input="检索知识库 B")

        workspace_a = await service.handle_rpc(
            RpcRequest(
                id="workspace-a",
                method="artifact.lineage",
                params={"domain": "knowledge", "app_id": "knowledge", "workspace_id": "workspace_a"},
            )
        )
        workspace_b = await service.handle_rpc(
            RpcRequest(
                id="workspace-b",
                method="artifact.lineage",
                params={"domain": "knowledge", "app_id": "knowledge", "workspace_id": "workspace_b"},
            )
        )

        assert workspace_a.error is None
        assert workspace_b.error is None
        assert workspace_a.result["count"] == workspace_b.result["count"]
        assert {
            artifact["workspace_id"] for artifact in workspace_a.result["artifacts"]
        } == {"workspace_a"}
        assert {
            artifact["workspace_id"] for artifact in workspace_b.result["artifacts"]
        } == {"workspace_b"}

    run_async(run())

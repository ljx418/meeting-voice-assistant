from __future__ import annotations

from apps.gateway.protocol import RpcRequest

from tests.knowledge_phase_e_helpers import build_knowledge_service, run_async, run_knowledge_turn


def test_knowledge_lineage_contains_standard_roots_leaves_and_edges(tmp_path):
    async def run():
        service = build_knowledge_service(tmp_path)
        session_id, _ = await run_knowledge_turn(service)
        response = await service.handle_rpc(
            RpcRequest(
                id="lineage",
                method="artifact.lineage",
                params={"session_id": session_id, "domain": "knowledge", "app_id": "knowledge"},
            )
        )

        assert response.error is None
        lineage = response.result
        by_kind = {artifact["kind"]: artifact for artifact in lineage["artifacts"]}
        assert {"source_reference", "note", "brief", "citation_bundle"}.issubset(by_kind)
        assert by_kind["source_reference"]["artifact_id"] in lineage["roots"]
        assert by_kind["citation_bundle"]["artifact_id"] in lineage["leaves"]
        edges = {(edge["source_artifact_id"], edge["target_artifact_id"]) for edge in lineage["edges"]}
        assert (by_kind["source_reference"]["artifact_id"], by_kind["note"]["artifact_id"]) in edges
        assert (by_kind["source_reference"]["artifact_id"], by_kind["brief"]["artifact_id"]) in edges
        assert (by_kind["brief"]["artifact_id"], by_kind["citation_bundle"]["artifact_id"]) in edges

    run_async(run())


def test_connector_result_cannot_replace_standard_knowledge_artifacts(tmp_path):
    async def run():
        service = build_knowledge_service(tmp_path)
        session_id, _ = await run_knowledge_turn(service)
        response = await service.handle_rpc(
            RpcRequest(
                id="lineage",
                method="artifact.lineage",
                params={"session_id": session_id, "domain": "knowledge", "app_id": "knowledge"},
            )
        )
        kinds = [artifact["kind"] for artifact in response.result["artifacts"]]

        assert kinds.count("connector_result") == 1
        for kind in ("source_reference", "note", "brief", "citation_bundle"):
            assert kind in kinds

    run_async(run())

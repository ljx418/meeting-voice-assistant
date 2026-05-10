from __future__ import annotations

from apps.gateway.protocol import RpcRequest

from tests.knowledge_phase_e_helpers import build_knowledge_service, run_async, run_knowledge_turn


def test_knowledge_workflow_registers_standard_artifact_set(tmp_path):
    async def run():
        service = build_knowledge_service(tmp_path)
        session_id, result = await run_knowledge_turn(service)
        completed = result["events"][-1]["data"]
        records = completed["artifact_records"]

        assert set(records) == {"source_reference", "note", "brief", "citation_bundle"}
        assert all(record["app_id"] == "knowledge" for record in records.values())
        assert all(record["workspace_id"] == "workspace_knowledge" for record in records.values())
        assert records["note"]["metadata"]["source_artifact_id"] == records["source_reference"]["artifact_id"]
        assert records["brief"]["metadata"]["source_artifact_id"] == records["source_reference"]["artifact_id"]
        assert records["citation_bundle"]["metadata"]["source_artifact_id"] == records["brief"]["artifact_id"]

        jobs = await service.handle_rpc(
            RpcRequest(id="jobs", method="job.list", params={"session_id": session_id, "app_id": "knowledge"})
        )
        assert jobs.error is None
        workflow_jobs = [job for job in jobs.result["jobs"] if job["workflow_id"] == "knowledge.workflow"]
        assert workflow_jobs
        assert set(workflow_jobs[-1]["artifact_ids"]) == {
            record["artifact_id"] for record in records.values()
        }

    run_async(run())


def test_knowledge_workflow_uses_data_service_connector_result_as_supporting_artifact(tmp_path):
    async def run():
        service = build_knowledge_service(tmp_path)
        session_id, _ = await run_knowledge_turn(service)
        lineage = await service.handle_rpc(
            RpcRequest(
                id="lineage",
                method="artifact.lineage",
                params={"session_id": session_id, "domain": "knowledge", "app_id": "knowledge"},
            )
        )

        assert lineage.error is None
        kinds = {artifact["kind"] for artifact in lineage.result["artifacts"]}
        assert {"source_reference", "note", "brief", "citation_bundle"}.issubset(kinds)
        assert "connector_result" in kinds

    run_async(run())

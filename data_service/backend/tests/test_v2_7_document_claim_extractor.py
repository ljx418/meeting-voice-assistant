from __future__ import annotations

from data_service.code_assets.architecture.service import ArchitectureService

from test_v2_7_document_registry import _prepare


def test_v27_phase50_claim_extractor_regression_for_phase51(tmp_path, monkeypatch):
    _client, _workspace_root, workspace, workspace_id, codebase_id, snapshot_id, _repo = _prepare(tmp_path, monkeypatch)
    service = ArchitectureService(workspace, workspace_id=workspace_id)
    service.build_document_registry(codebase_id, snapshot_id=snapshot_id)

    payload = service.build_document_claims(codebase_id)
    labels = {item["label"] for item in payload["claims"]}
    claim_ids = {item["claim_id"] for item in payload["claims"]}

    assert "Document Asset Registry registers project architecture documents." in labels
    assert "Acceptance: every accepted claim has document evidence." in labels
    assert any(item["claim_type"] == "acceptance_gate" for item in payload["claims"])
    assert any(item["source_block_type"] == "table_row" for item in payload["claims"])
    assert all(item["from_claim_id"] in claim_ids and item["to_claim_id"] in claim_ids for item in payload["relations"])

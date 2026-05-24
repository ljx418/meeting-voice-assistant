from fastapi.testclient import TestClient

from app.main import app
from test_target_http_evidence_spans import _first_query_evidence
from test_target_http_source_preview import _assert_no_internal_paths, _create_workspace, _import_typed_text_source


def _setup_client(tmp_path, monkeypatch):
    root = tmp_path / "managed"
    monkeypatch.setenv("DATA_SERVICE_WORKSPACE_ROOT", str(root))
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_WORKSPACE_ROOTS", str(tmp_path))
    return TestClient(app)


def test_v11s3_markdown_query_evidence_resolves_document_unit_and_evidence_span(tmp_path, monkeypatch):
    client = _setup_client(tmp_path, monkeypatch)
    workspace_id = _create_workspace(client, "RN S3 Markdown Evidence")
    source_id = _import_typed_text_source(
        client,
        workspace_id,
        source_type="markdown",
        title="Markdown evidence",
        content="# Queue Notes\n\nQueue backpressure protects workers.",
    )

    evidence = _first_query_evidence(client, workspace_id, query="queue backpressure")
    assert evidence["source_id"] == source_id
    assert evidence["unit_id"].startswith("unit_")
    assert evidence["evidence_id"].startswith("ev_")

    unit = client.get(f"/api/workspaces/{workspace_id}/sources/{source_id}/units/{evidence['unit_id']}")
    assert unit.status_code == 200
    assert unit.json()["data"]["unit"]["content_type"] == "text/markdown"

    span = client.get(
        f"/api/workspaces/{workspace_id}/sources/{source_id}/units/{evidence['unit_id']}/evidence/{evidence['evidence_id']}"
    )
    assert span.status_code == 200
    payload = span.json()
    evidence_span = payload["data"]["evidence_span"]
    assert evidence_span["source_id"] == source_id
    assert evidence_span["unit_id"] == evidence["unit_id"]
    assert evidence_span["evidence_id"] == evidence["evidence_id"]
    assert evidence_span["offset_basis"] == "normalized_text"
    assert evidence_span["offset_range"] == "half_open"
    assert evidence_span["text_basis"] == "document_unit_text"
    _assert_no_internal_paths(payload)


def test_v11s3_json_query_evidence_resolves_json_node_unit_and_evidence_span(tmp_path, monkeypatch):
    client = _setup_client(tmp_path, monkeypatch)
    workspace_id = _create_workspace(client, "RN S3 JSON Evidence")
    source_id = _import_typed_text_source(
        client,
        workspace_id,
        source_type="json",
        title="JSON evidence",
        content='{"summary":"Queue backpressure protects workers","decision":"ship"}',
    )

    evidence = _first_query_evidence(client, workspace_id, query="queue backpressure")
    assert evidence["source_id"] == source_id
    assert evidence["unit_id"].startswith("unit_")
    assert evidence["evidence_id"].startswith("ev_")

    unit = client.get(f"/api/workspaces/{workspace_id}/sources/{source_id}/units/{evidence['unit_id']}")
    assert unit.status_code == 200
    unit_payload = unit.json()
    assert unit_payload["data"]["unit"]["unit_type"] == "json_node"
    assert unit_payload["data"]["unit"]["json_path"] == "$.summary"

    span = client.get(
        f"/api/workspaces/{workspace_id}/sources/{source_id}/units/{evidence['unit_id']}/evidence/{evidence['evidence_id']}"
    )
    assert span.status_code == 200
    payload = span.json()
    evidence_span = payload["data"]["evidence_span"]
    assert evidence_span["source_id"] == source_id
    assert evidence_span["unit_id"] == evidence["unit_id"]
    assert evidence_span["evidence_id"] == evidence["evidence_id"]
    assert evidence_span["offset_basis"] == "normalized_text"
    assert evidence_span["offset_range"] == "half_open"
    assert evidence_span["text_basis"] == "document_unit_text"
    _assert_no_internal_paths(unit_payload)
    _assert_no_internal_paths(payload)

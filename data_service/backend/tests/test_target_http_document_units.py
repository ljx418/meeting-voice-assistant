from pathlib import Path
from urllib.parse import quote

from fastapi.testclient import TestClient

from app.main import app
from test_target_http_source_preview import (
    _assert_no_internal_paths,
    _create_workspace,
    _import_text_source,
    _import_typed_text_source,
    _patch_pdf_extractor,
)


def _setup_client(tmp_path, monkeypatch):
    root = tmp_path / "managed"
    monkeypatch.setenv("DATA_SERVICE_WORKSPACE_ROOT", str(root))
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_WORKSPACE_ROOTS", str(tmp_path))
    return TestClient(app)


def test_v11cbe_document_units_routes_exposed_without_compatibility_route():
    routes = {(method, route.path) for route in app.routes for method in getattr(route, "methods", set())}
    assert ("GET", "/api/workspaces/{workspace_id}/sources/{source_id}/units") in routes
    assert ("GET", "/api/workspaces/{workspace_id}/sources/{source_id}/units/{unit_id}") in routes
    assert all("/api/v1/knowledge" not in path or "unit" not in path for _, path in routes)


def test_v11cbe_document_unit_list_and_detail_success(tmp_path, monkeypatch):
    client = _setup_client(tmp_path, monkeypatch)
    workspace_id = _create_workspace(client, "RN Document Units")
    source_id = _import_text_source(
        client,
        workspace_id,
        content="Overview paragraph.\n\nSecond section explains queue backpressure.",
    )

    response = client.get(f"/api/workspaces/{workspace_id}/sources/{source_id}/units")
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    units = payload["data"]["units"]
    assert units["source_id"] == source_id
    assert units["limit"] == 50
    assert units["has_more"] is False
    assert units["next_cursor"] is None
    assert len(units["items"]) == 2
    first = units["items"][0]
    assert first["unit_id"].startswith("unit_")
    assert first["source_id"] == source_id
    assert first["unit_type"] == "section"
    assert first["content_type"] == "text/plain"
    assert first["order_index"] == 0
    assert first["preview_available"] is True
    assert first["artifact_ref"] == f"unit://{source_id}/{first['unit_id']}"
    assert first["preview_truncated"] is False
    assert first["preview_size_bytes"] >= len("Overview")
    assert first["max_preview_size_bytes"] == 50000
    _assert_no_internal_paths(payload)

    detail = client.get(f"/api/workspaces/{workspace_id}/sources/{source_id}/units/{first['unit_id']}")
    assert detail.status_code == 200
    assert detail.json()["data"]["unit"] == first
    _assert_no_internal_paths(detail.json())


def test_v11s3_document_units_for_markdown_and_json_sources(tmp_path, monkeypatch):
    client = _setup_client(tmp_path, monkeypatch)
    workspace_id = _create_workspace(client, "RN S3 Units")
    markdown_source_id = _import_typed_text_source(
        client,
        workspace_id,
        source_type="markdown",
        title="Markdown source",
        content="# Overview\n\nQueues absorb burst traffic.",
    )
    json_source_id = _import_typed_text_source(
        client,
        workspace_id,
        source_type="json",
        title="JSON source",
        content='{"summary":"Queues absorb burst traffic","risk":{"level":"low"}}',
    )

    markdown_response = client.get(f"/api/workspaces/{workspace_id}/sources/{markdown_source_id}/units")
    assert markdown_response.status_code == 200
    markdown_units = markdown_response.json()["data"]["units"]["items"]
    assert len(markdown_units) == 2
    assert markdown_units[0]["source_id"] == markdown_source_id
    assert markdown_units[0]["unit_type"] == "section"
    assert markdown_units[0]["content_type"] == "text/markdown"
    assert "# Overview" in markdown_units[0]["text_preview"]
    _assert_no_internal_paths(markdown_response.json())

    json_response = client.get(f"/api/workspaces/{workspace_id}/sources/{json_source_id}/units")
    assert json_response.status_code == 200
    json_units = json_response.json()["data"]["units"]["items"]
    assert [unit["json_path"] for unit in json_units] == ["$.summary", "$.risk"]
    assert all(unit["unit_type"] == "json_node" for unit in json_units)
    assert all(unit["content_type"] == "text/plain" for unit in json_units)
    assert "Queues absorb burst traffic" in json_units[0]["text_preview"]
    detail = client.get(f"/api/workspaces/{workspace_id}/sources/{json_source_id}/units/{json_units[0]['unit_id']}")
    assert detail.status_code == 200
    assert detail.json()["data"]["unit"]["json_path"] == "$.summary"
    _assert_no_internal_paths(json_response.json())
    _assert_no_internal_paths(detail.json())


def test_v14c_document_units_for_text_pdf_source(tmp_path, monkeypatch):
    root = tmp_path / "managed"
    source_root = tmp_path / "sources"
    source_root.mkdir()
    monkeypatch.setenv("DATA_SERVICE_WORKSPACE_ROOT", str(root))
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_WORKSPACE_ROOTS", str(tmp_path))
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_SOURCE_ROOTS", str(source_root))
    _patch_pdf_extractor(
        monkeypatch,
        [
            "AI digital humans use speech synthesis and real-time rendering.",
            "Enterprise deployments require evidence-backed risk controls.",
        ],
    )

    client = TestClient(app)
    workspace_id = _create_workspace(client, "RN V1.4 PDF Units")
    pdf = source_root / "digital-human.pdf"
    pdf.write_bytes(b"%PDF-1.7\nfake text pdf fixture\n")
    imported = client.post(f"/api/workspaces/{workspace_id}/sources", json={"paths": [str(pdf)]})
    assert imported.status_code == 200
    source_id = imported.json()["data"]["sources"][0]["source_id"]

    response = client.get(f"/api/workspaces/{workspace_id}/sources/{source_id}/units")
    assert response.status_code == 200
    payload = response.json()
    units = payload["data"]["units"]["items"]
    assert len(units) == 2
    assert [unit["unit_type"] for unit in units] == ["page", "page"]
    assert [unit["page_no"] for unit in units] == [1, 2]
    assert all(unit["content_type"] == "text/plain" for unit in units)
    assert "AI digital humans" in units[0]["text_preview"]
    assert "risk controls" in units[1]["text_preview"]
    _assert_no_internal_paths(payload)

    detail = client.get(f"/api/workspaces/{workspace_id}/sources/{source_id}/units/{units[0]['unit_id']}")
    assert detail.status_code == 200
    assert detail.json()["data"]["unit"]["page_no"] == 1
    _assert_no_internal_paths(detail.json())


def test_v11cbe_document_unit_pagination_is_deterministic_and_non_overlapping(tmp_path, monkeypatch):
    client = _setup_client(tmp_path, monkeypatch)
    workspace_id = _create_workspace(client, "RN Unit Pagination")
    source_id = _import_text_source(client, workspace_id, content="A.\n\nB.\n\nC.")

    first_page = client.get(f"/api/workspaces/{workspace_id}/sources/{source_id}/units", params={"limit": 1})
    assert first_page.status_code == 200
    first_units = first_page.json()["data"]["units"]
    assert len(first_units["items"]) == 1
    assert first_units["has_more"] is True
    assert first_units["next_cursor"]

    second_page = client.get(
        f"/api/workspaces/{workspace_id}/sources/{source_id}/units",
        params={"limit": 1, "cursor": first_units["next_cursor"]},
    )
    assert second_page.status_code == 200
    second_units = second_page.json()["data"]["units"]
    assert len(second_units["items"]) == 1
    assert first_units["items"][0]["unit_id"] != second_units["items"][0]["unit_id"]

    repeat = client.get(f"/api/workspaces/{workspace_id}/sources/{source_id}/units")
    assert repeat.status_code == 200
    repeat_items = repeat.json()["data"]["units"]["items"]
    assert [item["unit_id"] for item in repeat_items] == [item["unit_id"] for item in sorted(repeat_items, key=lambda item: (item["order_index"], item["unit_id"]))]

    invalid = client.get(f"/api/workspaces/{workspace_id}/sources/{source_id}/units", params={"cursor": "bad-cursor"})
    assert invalid.status_code == 422
    assert "VALIDATION_ERROR" in invalid.json()["detail"]


def test_v11cbe_document_unit_error_semantics(tmp_path, monkeypatch):
    client = _setup_client(tmp_path, monkeypatch)
    workspace_id = _create_workspace(client, "RN Unit Errors")
    source_a = _import_text_source(client, workspace_id, title="A", content="Unit A.")
    source_b = _import_text_source(client, workspace_id, title="B", content="Unit B.")
    unit_a = client.get(f"/api/workspaces/{workspace_id}/sources/{source_a}/units").json()["data"]["units"]["items"][0]

    unknown_source = client.get(f"/api/workspaces/{workspace_id}/sources/src_0000000000000000/units")
    assert unknown_source.status_code == 404
    assert "SOURCE_NOT_FOUND" in unknown_source.json()["detail"]

    unknown_unit = client.get(f"/api/workspaces/{workspace_id}/sources/{source_a}/units/unit_0000000000000000")
    assert unknown_unit.status_code == 404
    assert "UNIT_NOT_FOUND" in unknown_unit.json()["detail"]

    cross_source = client.get(f"/api/workspaces/{workspace_id}/sources/{source_b}/units/{unit_a['unit_id']}")
    assert cross_source.status_code == 404
    assert "UNIT_NOT_FOUND" in cross_source.json()["detail"]

    artifact_ref = quote(f"unit:{source_a}:{unit_a['unit_id']}", safe="")
    artifact = client.get(f"/api/workspaces/{workspace_id}/sources/{source_a}/units/{artifact_ref}")
    assert artifact.status_code == 422
    assert "VALIDATION_ERROR" in artifact.json()["detail"]

    slug = client.get(f"/api/workspaces/{workspace_id}/sources/{source_a}/units/source-src-architecture-notes")
    assert slug.status_code == 422
    assert "VALIDATION_ERROR" in slug.json()["detail"]


def test_v11cbe_document_units_unsupported_type_response(tmp_path, monkeypatch):
    root = tmp_path / "managed"
    source_root = tmp_path / "sources"
    source_root.mkdir()
    monkeypatch.setenv("DATA_SERVICE_WORKSPACE_ROOT", str(root))
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_WORKSPACE_ROOTS", str(tmp_path))
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_SOURCE_ROOTS", str(source_root))

    client = TestClient(app)
    workspace_id = _create_workspace(client, "RN Unit Unsupported")
    video = source_root / "clip.mp4"
    video.write_bytes(b"not really a video")
    imported = client.post(f"/api/workspaces/{workspace_id}/sources", json={"paths": [str(video)]})
    assert imported.status_code == 200
    source_id = imported.json()["data"]["sources"][0]["source_id"]

    response = client.get(f"/api/workspaces/{workspace_id}/sources/{source_id}/units")
    assert response.status_code == 200
    units = response.json()["data"]["units"]
    assert units == {
        "source_id": source_id,
        "items": [],
        "next_cursor": None,
        "limit": 50,
        "has_more": False,
        "unsupported_reason": "source_type_not_supported",
    }
    assert response.json()["next_actions"] == ["source_type_not_supported"]
    _assert_no_internal_paths(response.json())


def test_v11cbe_source_preview_does_not_return_units_by_default(tmp_path, monkeypatch):
    client = _setup_client(tmp_path, monkeypatch)
    workspace_id = _create_workspace(client, "RN Preview No Units")
    source_id = _import_text_source(client, workspace_id, content="A.\n\nB.")

    response = client.get(f"/api/workspaces/{workspace_id}/sources/{source_id}/preview")
    assert response.status_code == 200
    preview = response.json()["data"]["preview"]
    assert "units" not in preview
    assert "unit_id" not in preview



def test_v11cbe_document_unit_routes_are_in_openapi_schema():
    schema = app.openapi()
    paths = schema["paths"]
    assert "/api/workspaces/{workspace_id}/sources/{source_id}/units" in paths
    assert "/api/workspaces/{workspace_id}/sources/{source_id}/units/{unit_id}" in paths

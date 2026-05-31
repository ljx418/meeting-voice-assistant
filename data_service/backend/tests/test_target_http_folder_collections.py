from fastapi.testclient import TestClient

from app.main import app
from test_target_http_source_preview import _assert_no_internal_paths, _create_workspace


def _setup_client(tmp_path, monkeypatch):
    workspace_root = tmp_path / "managed"
    source_root = tmp_path / "authorized"
    source_root.mkdir()
    monkeypatch.setenv("DATA_SERVICE_WORKSPACE_ROOT", str(workspace_root))
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_WORKSPACE_ROOTS", str(tmp_path))
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_SOURCE_ROOTS", str(source_root))
    return TestClient(app), source_root


def _write_fixture_tree(root):
    tech = root / "tech-share"
    (tech / "frontend").mkdir(parents=True)
    (tech / "backend").mkdir()
    (tech / ".git").mkdir()
    (tech / "node_modules").mkdir()
    (tech / "dist").mkdir()
    (tech / ".hidden").mkdir()
    (tech / "frontend" / "notes.md").write_text("# Frontend\n\nReact workflow notes.", encoding="utf-8")
    (tech / "backend" / "summary.txt").write_text("Backend contract notes.", encoding="utf-8")
    (tech / "slides.pptx").write_bytes(b"pptx")
    (tech / "doc.docx").write_bytes(b"docx")
    (tech / "video.mp4").write_bytes(b"video")
    (tech / "image.png").write_bytes(b"\x89PNG")
    (tech / ".env").write_text("SECRET=not-for-fixture", encoding="utf-8")
    (tech / ".hidden" / "secret.md").write_text("hidden", encoding="utf-8")
    (tech / "node_modules" / "package.md").write_text("ignored", encoding="utf-8")
    (tech / "dist" / "bundle.txt").write_text("ignored", encoding="utf-8")
    try:
        (tech / "linked-notes.md").symlink_to(tech / "frontend" / "notes.md")
    except OSError:
        pass
    return tech


def test_v13b_folder_collection_dry_run_manifest_success(tmp_path, monkeypatch):
    client, source_root = _setup_client(tmp_path, monkeypatch)
    tech = _write_fixture_tree(source_root)
    workspace_id = _create_workspace(client, "RN V1.3 Folder Scan")

    response = client.post(
        f"/api/workspaces/{workspace_id}/folder-collections/scan",
        json={
            "authorized_root": str(tech),
            "permission_grant_id": "grant_test_folder_scan",
            "dry_run": True,
            "recursive": True,
            "include_extensions": [".md", ".txt"],
            "exclude_globs": ["**/*.tmp"],
            "max_depth": 8,
            "follow_symlinks": False,
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert payload["next_actions"] == ["review_folder_manifest", "confirm_folder_permission_before_extract"]
    collection = payload["data"]["collection"]
    permission_grant = payload["data"]["permission_grant"]
    assert collection["workspace_id"] == workspace_id
    assert collection["root_label"] == "tech-share"
    assert permission_grant == {
        "permission_grant_id": "grant_test_folder_scan",
        "workspace_id": workspace_id,
        "root_label": "tech-share",
        "scopes": ["scan"],
        "status": "active",
        "created_at": permission_grant["created_at"],
        "expires_at": None,
    }

    folders = {item["relative_path"]: item for item in collection["folders"]}
    assert "." in folders
    assert "frontend" in folders
    assert "backend" in folders
    assert folders["."]["child_folder_count"] >= 2
    assert all(not item["relative_path"].startswith("/") for item in collection["folders"])

    files = {item["relative_path"]: item for item in collection["files"]}
    assert set(files) == {"backend/summary.txt", "frontend/notes.md"}
    assert files["frontend/notes.md"]["extraction_status"] == "skipped"
    assert "text_preview" not in files["frontend/notes.md"]

    skipped = {(item["relative_path"], item["skipped_reason"]) for item in collection["skipped_files"]}
    assert ("slides.pptx", "unsupported_extension") in skipped
    assert ("doc.docx", "unsupported_extension") in skipped
    assert ("video.mp4", "unsupported_extension") in skipped
    assert ("image.png", "unsupported_extension") in skipped
    assert (".env", "hidden_file") in skipped
    assert (".git", "excluded_dir") in skipped
    assert ("node_modules", "excluded_dir") in skipped
    assert ("dist", "excluded_dir") in skipped
    assert (".hidden", "hidden_dir") in skipped
    assert any(reason == "symlink_skipped" for _, reason in skipped)
    _assert_no_internal_paths(payload)


def test_v13b_folder_collection_rejects_extract_symlink_and_unsupported_extensions(tmp_path, monkeypatch):
    client, source_root = _setup_client(tmp_path, monkeypatch)
    tech = _write_fixture_tree(source_root)
    workspace_id = _create_workspace(client, "RN V1.3 Folder Guardrails")

    extract = client.post(
        f"/api/workspaces/{workspace_id}/folder-collections/scan",
        json={"authorized_root": str(tech), "permission_grant_id": "grant_extract", "dry_run": False},
    )
    assert extract.status_code == 422
    assert "VALIDATION_ERROR" in extract.json()["detail"]

    symlink = client.post(
        f"/api/workspaces/{workspace_id}/folder-collections/scan",
        json={"authorized_root": str(tech), "permission_grant_id": "grant_symlink", "follow_symlinks": True},
    )
    assert symlink.status_code == 422
    assert "VALIDATION_ERROR" in symlink.json()["detail"]

    unsupported = client.post(
        f"/api/workspaces/{workspace_id}/folder-collections/scan",
        json={"authorized_root": str(tech), "permission_grant_id": "grant_json", "include_extensions": [".json"]},
    )
    assert unsupported.status_code == 422
    assert "VALIDATION_ERROR" in unsupported.json()["detail"]


def test_v13b_folder_collection_rejects_unauthorized_root(tmp_path, monkeypatch):
    client, _source_root = _setup_client(tmp_path, monkeypatch)
    workspace_id = _create_workspace(client, "RN V1.3 Folder Auth")
    unauthorized = tmp_path / "outside"
    unauthorized.mkdir()
    (unauthorized / "notes.md").write_text("outside", encoding="utf-8")

    response = client.post(
        f"/api/workspaces/{workspace_id}/folder-collections/scan",
        json={"authorized_root": str(unauthorized), "permission_grant_id": "grant_outside"},
    )

    assert response.status_code == 422
    assert "VALIDATION_ERROR" in response.json()["detail"]


def test_v13b_folder_collection_route_exposed_without_knowledge_feature_route():
    routes = {(method, route.path) for route in app.routes for method in getattr(route, "methods", set())}
    assert ("POST", "/api/workspaces/{workspace_id}/folder-collections/scan") in routes
    assert all("/api/v1/knowledge" not in path or "folder-collections" not in path for _, path in routes)

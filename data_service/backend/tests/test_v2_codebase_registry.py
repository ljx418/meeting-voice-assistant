from pathlib import Path

from data_service.code_assets.artifacts import codebase_json_path
from data_service.code_assets.registry import CodebaseRegistry


def test_v2_codebase_registry_import_duplicate_archive_and_no_source_registry(tmp_path, monkeypatch):
    repo_root = Path(__file__).resolve().parents[2]
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_CODEBASE_ROOTS", str(repo_root))

    registry = CodebaseRegistry(workspace, workspace_id="workspace")
    first = registry.import_codebase(path=str(repo_root), metadata={"purpose": "phase1"})
    asset = first["asset"]

    assert first["created"] is True
    assert asset.codebase_id == "codebase_data_service"
    assert asset.status == "active"
    assert asset.metadata == {"purpose": "phase1"}
    assert codebase_json_path(workspace, asset.codebase_id).exists()
    assert not (workspace / "lifecycle" / "sources.json").exists()

    duplicate = registry.import_codebase(path=str(repo_root))
    assert duplicate["created"] is False
    assert duplicate["asset"].codebase_id == asset.codebase_id

    archived = registry.archive(asset.codebase_id, reason="phase complete")
    assert archived.status == "archived"
    assert archived.archive_reason == "phase complete"
    assert registry.list_codebases() == []
    assert [item.codebase_id for item in registry.list_codebases(include_archived=True)] == [asset.codebase_id]


def test_v2_codebase_registry_blocks_disallowed_path_and_id_conflict(tmp_path, monkeypatch):
    repo_root = Path(__file__).resolve().parents[2]
    other_root = tmp_path / "other"
    other_root.mkdir()
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_CODEBASE_ROOTS", str(repo_root))

    registry = CodebaseRegistry(workspace, workspace_id="workspace")
    registry.import_codebase(path=str(repo_root), codebase_id="codebase-main")

    try:
        registry.import_codebase(path=str(other_root), codebase_id="other")
    except ValueError as exc:
        assert str(exc) == "CODEBASE_PATH_NOT_ALLOWED"
    else:
        raise AssertionError("Expected disallowed root to be blocked")

    monkeypatch.setenv("DATA_SERVICE_ALLOWED_CODEBASE_ROOTS", f"{repo_root}:{other_root}")
    try:
        registry.import_codebase(path=str(other_root), codebase_id="codebase-main")
    except ValueError as exc:
        assert str(exc) == "CODEBASE_ID_CONFLICT"
    else:
        raise AssertionError("Expected codebase_id conflict to be blocked")

import json
from pathlib import Path


def test_v2_codebase_cli_import_real_repo(tmp_path, monkeypatch, capsys):
    from data_service.__main__ import knowledge_main

    repo_root = Path(__file__).resolve().parents[2]
    workspace_root = tmp_path / "managed"
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_WORKSPACE_ROOTS", str(tmp_path))
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_CODEBASE_ROOTS", str(repo_root))

    result = knowledge_main(
        [
            "code",
            "import",
            "--workspace-root",
            str(workspace_root),
            "--workspace-id",
            "phase1-cli",
            "--path",
            str(repo_root),
            "--metadata-json",
            '{"caller":"cli"}',
        ]
    )
    assert result == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["status"] == "ok"
    assert payload["workspace_id"] == "phase1-cli"
    assert payload["data"]["codebase"]["codebase_id"] == "codebase_data_service"
    assert payload["data"]["codebase"]["metadata"] == {"caller": "cli"}
    assert "root_path" not in json.dumps(payload)
    assert (workspace_root / "phase1-cli" / "assets" / "codebase" / "codebase_data_service" / "codebase.json").exists()

    assert knowledge_main(["code", "list", "--workspace-root", str(workspace_root), "--workspace-id", "phase1-cli"]) == 0
    listed = json.loads(capsys.readouterr().out)
    assert [item["codebase_id"] for item in listed["data"]["items"]] == ["codebase_data_service"]

    assert (
        knowledge_main(
            [
                "code",
                "describe",
                "--workspace-root",
                str(workspace_root),
                "--workspace-id",
                "phase1-cli",
                "--codebase-id",
                "codebase_data_service",
            ]
        )
        == 0
    )
    described = json.loads(capsys.readouterr().out)
    assert described["data"]["codebase"]["codebase_id"] == "codebase_data_service"

    assert (
        knowledge_main(
            [
                "code",
                "archive",
                "--workspace-root",
                str(workspace_root),
                "--workspace-id",
                "phase1-cli",
                "--codebase-id",
                "codebase_data_service",
                "--reason",
                "done",
            ]
        )
        == 0
    )
    archived = json.loads(capsys.readouterr().out)
    assert archived["data"]["codebase"]["status"] == "archived"
    assert archived["data"]["codebase"]["archive_reason"] == "done"

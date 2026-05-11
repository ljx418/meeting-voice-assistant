"""V3.5-0 scaffold tests."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

SCAFFOLD_DIRS = [
    "sdk",
    "sdk/python",
    "sdk/python/harnessos_client",
    "sdk/typescript",
    "templates",
    "templates/bff",
    "templates/bff/fastapi_minimal",
    "templates/bff/fastapi",
    "templates/bff/node",
    "templates/pack",
    "templates/connector",
    "examples/reference_app",
    "docs/integration",
]


def test_scaffold_dirs_exist_and_have_readme() -> None:
    for relative in SCAFFOLD_DIRS:
        path = ROOT / relative
        assert path.is_dir(), relative
        assert (path / "README.md").is_file(), relative


def test_scaffold_dirs_are_readme_or_scaffold_only() -> None:
    allowed = {"README.md", ".gitkeep"}
    for relative in SCAFFOLD_DIRS:
        directory_allowed = set(allowed)
        if relative == "docs/integration":
            directory_allowed.add("v3_5_phase0_baseline.md")
            directory_allowed.add("sdk_contract.md")
            directory_allowed.add("bff_minimal_smoke.md")
        if relative == "sdk/python/harnessos_client":
            directory_allowed.update(
                {
                    "__init__.py",
                    "client.py",
                    "async_client.py",
                    "models.py",
                    "errors.py",
                    "transport.py",
                    "protocol_snapshot.py",
                }
            )
        if relative == "templates/bff/fastapi_minimal":
            directory_allowed.update(
                {
                    "app.py",
                    "config.example.json",
                    "denylist.py",
                    "event_proxy.py",
                    "requirements.txt",
                    "scope_binding.py",
                }
            )
        files = {path.name for path in (ROOT / relative).iterdir() if path.is_file()}
        assert files <= directory_allowed, f"{relative}: {files - directory_allowed}"


def test_python_sdk_is_importable_after_v3_5_d_but_typescript_remains_scaffold_only() -> None:
    import sys

    package_dir = ROOT / "sdk/python/harnessos_client"
    assert (package_dir / "__init__.py").exists()
    assert (package_dir / "client.py").exists()
    sys.path.insert(0, str(ROOT / "sdk/python"))
    try:
        import harnessos_client
    finally:
        sys.path.remove(str(ROOT / "sdk/python"))
    assert "HarnessOSClient" in harnessos_client.__all__
    assert "MeetingClient" not in harnessos_client.__all__
    assert "KnowledgeClient" not in harnessos_client.__all__
    assert not (ROOT / "sdk/typescript/src").exists()


def test_phase0_baseline_doc_has_required_fields() -> None:
    baseline = ROOT / "docs/integration/v3_5_phase0_baseline.md"
    text = baseline.read_text(encoding="utf-8")
    for field in [
        "baseline_commit",
        "baseline_date",
        "python_env",
        "pytest_command",
        "pytest_result",
        "skipped_tests",
        "warnings",
        "external_e2e_excluded",
        "drawio_validation",
    ]:
        assert field in text

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
            directory_allowed.add("workflow_runtime_contract.md")
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
        if relative == "sdk/typescript":
            directory_allowed.update(
                {
                    "package.json",
                    "package-lock.json",
                    "tsconfig.json",
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
        if relative == "templates/bff/fastapi":
            directory_allowed.update(
                {
                    ".env.example",
                    "app.py",
                    "capability_policy.py",
                    "config.example.json",
                    "errors.py",
                    "event_proxy.py",
                    "harnessos.py",
                    "identity.py",
                    "rpc_proxy.py",
                    "scope_binding.py",
                    "security.py",
                    "settings.py",
                }
            )
        if relative == "templates/pack":
            directory_allowed.add("manifest.json")
        if relative == "templates/connector":
            directory_allowed.update({"descriptor.json", "health.py", "tools.py"})
        files = {path.name for path in (ROOT / relative).iterdir() if path.is_file()}
        assert files <= directory_allowed, f"{relative}: {files - directory_allowed}"


def test_python_and_typescript_sdks_are_importable_at_their_current_phases() -> None:
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
    assert (ROOT / "sdk/typescript/src/index.ts").exists()
    assert (ROOT / "sdk/typescript/src/react/index.ts").exists()
    assert not (ROOT / "sdk/typescript/src/hooks.ts").exists()


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

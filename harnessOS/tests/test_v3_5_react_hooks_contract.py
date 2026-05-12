"""V3.5-E2 React hooks contract tests."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TS_SDK = ROOT / "sdk/typescript"
SRC = TS_SDK / "src"
REACT_SRC = SRC / "react"

FORBIDDEN_IMPORTS = (
    "apps/",
    "apps.",
    "core/",
    "core.",
    "GatewayService",
    "RuntimeAdapter",
    "METHOD_SCHEMAS",
)

FORBIDDEN_HOOKS = {
    "useMeetingMinutes",
    "useKnowledgeSearch",
    "useMeetingWorkflow",
    "useDocumentIngest",
    "useGenerateVideo",
    "useAnalyzePortfolio",
}


def test_react_hooks_have_no_server_internal_imports() -> None:
    for path in REACT_SRC.glob("*.ts"):
        text = path.read_text(encoding="utf-8")
        assert not any(item in text for item in FORBIDDEN_IMPORTS), path


def test_core_typescript_sdk_import_does_not_require_react() -> None:
    index = (SRC / "index.ts").read_text(encoding="utf-8")
    assert "react" not in index.lower()
    assert "./react" not in index


def test_react_hooks_public_surface_excludes_business_hooks() -> None:
    index = (REACT_SRC / "index.ts").read_text(encoding="utf-8")
    for name in FORBIDDEN_HOOKS:
        assert name not in index
    for required in (
        "useHarnessSession",
        "useTurn",
        "useEvents",
        "useArtifacts",
        "useJobs",
        "useApprovals",
    ):
        assert required in index


def test_react_package_boundary_and_peer_dependency() -> None:
    package = json.loads((TS_SDK / "package.json").read_text(encoding="utf-8"))
    assert package["exports"]["."]["import"] == "./dist/index.js"
    assert package["exports"]["./react"]["import"] == "./dist/react/index.js"
    assert "react" in package["peerDependencies"]


def test_react_hooks_only_use_typescript_sdk_public_surface() -> None:
    allowed_relative_imports = {
        "../client.js",
        "../events.js",
        "../models.js",
        "./types.js",
        "./useApprovals.js",
        "./useArtifacts.js",
        "./useEvents.js",
        "./useHarnessSession.js",
        "./useJobs.js",
        "./useTurn.js",
    }
    for path in REACT_SRC.glob("*.ts"):
        text = path.read_text(encoding="utf-8")
        for line in text.splitlines():
            if " from " not in line:
                continue
            if '"react"' in line:
                continue
            imported = line.rsplit(" from ", 1)[1].strip().strip(";").strip('"')
            assert imported in allowed_relative_imports, (path, imported)


def test_v3_5_docs_mark_e2_as_current_phase() -> None:
    readme = (ROOT / "docs/design/V3.5/00_README.md").read_text(encoding="utf-8")
    gap = (ROOT / "docs/design/V3.5/v3_5_current_gap_analysis.md").read_text(encoding="utf-8")
    assert "V3.5-E2 React Hooks" in readme
    assert "V3.5-E2 React Hooks" in gap

"""V4.0 frontend boundary tests.

These tests intentionally scan only frontend surfaces. Backend routes and SDK
transport internals are allowed to call /v1/rpc and are covered elsewhere.
"""

from __future__ import annotations

from pathlib import Path


SCAN_ROOTS = [
    Path("apps/workflow-console"),
    Path("apps/web/src"),
    Path("examples/reference_app/frontend"),
]

IGNORED_DIRS = {
    "node_modules",
    "dist",
    "build",
    ".next",
    ".vite",
    "coverage",
    "__tests__",
    "e2e",
    "dist-test",
}

SOURCE_SUFFIXES = {
    ".ts",
    ".tsx",
    ".js",
    ".jsx",
    ".vue",
    ".svelte",
    ".md",
}


FORBIDDEN_SNIPPETS = (
    "import core/",
    'from "core/',
    "from 'core/",
    "import apps.gateway",
    'from "apps.gateway',
    "from 'apps.gateway",
    "WorkflowStore",
    "ArtifactRegistry",
    "ApprovalStore",
    "approval.approve(",
    "approval.reject(",
    "/approval.approve",
    "/approval.reject",
    "workflow.invoke",
    "workflow.observe",
    "workflow.review",
    'method: "workflow.instance.start"',
    'method: "approval.respond"',
    'method: "workflow.context.update"',
    'method: "business.event.emit"',
    'method: "quality.evaluation.create"',
    'method: "quality.evaluation.attach"',
    'method: "workflow.template.publish"',
    'method: "workflow.draft.save"',
    'method: "artifact.read"',
)


FORBIDDEN_DIRECT_TRANSPORTS = (
    "fetch('/v1/rpc'",
    'fetch("/v1/rpc"',
    "fetch(`/v1/rpc",
    "fetch('/v1/events/subscribe'",
    'fetch("/v1/events/subscribe"',
    "fetch(`/v1/events/subscribe",
    "new EventSource('/v1/events/subscribe'",
    'new EventSource("/v1/events/subscribe"',
    "new EventSource(`/v1/events/subscribe",
)


def _frontend_files() -> list[Path]:
    files: list[Path] = []
    for root in SCAN_ROOTS:
        if not root.exists():
            continue
        for path in root.rglob("*"):
            if not path.is_file() or path.suffix not in SOURCE_SUFFIXES:
                continue
            if any(part in IGNORED_DIRS for part in path.parts):
                continue
            files.append(path)
    return files


def test_v4_0_frontend_scan_scope_is_limited() -> None:
    files = _frontend_files()
    assert all(not str(path).startswith("core/") for path in files)
    assert all(not str(path).startswith("apps/gateway/") for path in files)
    assert all("sdk/typescript" not in str(path) for path in files)


def test_v4_0_frontend_does_not_import_server_internals() -> None:
    offenders: list[tuple[str, str]] = []
    for path in _frontend_files():
        text = path.read_text(encoding="utf-8", errors="ignore")
        for snippet in FORBIDDEN_SNIPPETS:
            if snippet in text:
                offenders.append((str(path), snippet))
    assert offenders == []


def test_v4_0_frontend_uses_bff_or_sdk_not_direct_production_transport() -> None:
    offenders: list[tuple[str, str]] = []
    for path in _frontend_files():
        text = path.read_text(encoding="utf-8", errors="ignore")
        for snippet in FORBIDDEN_DIRECT_TRANSPORTS:
            if snippet in text:
                offenders.append((str(path), snippet))
    assert offenders == []

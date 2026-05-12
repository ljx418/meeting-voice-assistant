"""V3.5-E1 TypeScript SDK contract tests."""

from __future__ import annotations

import re
from pathlib import Path

from core.protocol.schemas.methods import METHOD_SCHEMAS


ROOT = Path(__file__).resolve().parents[1]
TS_SDK = ROOT / "sdk/typescript"
SRC = TS_SDK / "src"


FORBIDDEN_IMPORTS = (
    "apps/",
    "apps.",
    "core/",
    "core.",
    "GatewayService",
    "RuntimeAdapter",
    "METHOD_SCHEMAS",
)

FORBIDDEN_PUBLIC_NAMES = {
    "MeetingClient",
    "KnowledgeClient",
    "generateMinutes",
    "ingestDocument",
    "runMeetingWorkflow",
    "generateVideo",
    "analyzePortfolio",
    "processRecording",
    "searchKnowledgeBase",
}


def test_typescript_sdk_has_no_server_internal_imports() -> None:
    for path in SRC.glob("*.ts"):
        text = path.read_text(encoding="utf-8")
        assert not any(item in text for item in FORBIDDEN_IMPORTS), path


def test_typescript_public_api_surface_excludes_business_wrappers() -> None:
    index = (SRC / "index.ts").read_text(encoding="utf-8")
    for name in FORBIDDEN_PUBLIC_NAMES:
        assert name not in index
    for required in (
        "HarnessOSClient",
        "Scope",
        "RpcError",
        "CapabilityToken",
        "EventSubscription",
        "JsonRpcTransport",
    ):
        assert required in index


def test_typescript_protocol_snapshot_matches_server_default_runtime_surface() -> None:
    snapshot = (SRC / "protocolSnapshot.ts").read_text(encoding="utf-8")
    ts_methods = set(re.findall(r'"([a-z_]+\.[a-z_]+)"', snapshot.split("FORBIDDEN_PATTERNS", 1)[0]))
    server_methods = {
        schema["method"]
        for schema in METHOD_SCHEMAS
        if schema["sdk_exposure"] == "default" and schema["runtime_handler"] is True
    }
    assert ts_methods == server_methods


def test_typescript_sdk_package_scripts_exist() -> None:
    package = (TS_SDK / "package.json").read_text(encoding="utf-8")
    assert '"build": "tsc -p tsconfig.json"' in package
    assert '"test": "npm run build && node --test tests/*.test.mjs"' in package

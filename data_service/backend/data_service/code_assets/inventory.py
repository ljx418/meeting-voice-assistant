"""Public surface inventory artifacts for V2 codebase assets."""

from __future__ import annotations

import ast
import hashlib
import json
import re
from pathlib import Path
from typing import Any

from data_service.mcp_common import now, read_json, write_json
from .artifacts import (
    inventory_alignment_path,
    inventory_capabilities_path,
    inventory_summary_path,
    inventory_surfaces_path,
    read_jsonl,
    snapshot_files_path,
    snapshot_json_path,
    write_jsonl,
)
from .registry import CodebaseRegistry
from .snapshot import CodebaseSnapshotService


INVENTORY_SCHEMA_VERSION = "v2.0"
HTTP_METHODS = {"get", "post", "put", "patch", "delete", "head", "options"}
CLI_SOURCE_FILES = {
    "backend/data_service/__main__.py",
    "backend/data_service/cli_code.py",
    "backend/data_service/cli_code_devwiki.py",
    "backend/data_service/cli_code_graph.py",
    "backend/data_service/cli_code_quality.py",
}
FRONTEND_EXTENSIONS = {".vue", ".ts", ".tsx", ".js", ".jsx"}
INTERNAL_SCHEMA_FIELDS = {
    "artifact_physical_path",
    "cache_path",
    "debug_paths",
    "filesystem_path",
    "graphrag_cache_path",
    "internal_path",
    "local_path",
    "physical_path",
    "root_path",
    "workspace_path",
}
GOLDEN_HTTP = {
    "POST /api/workspaces/{workspace_id}/codebases",
    "POST /api/workspaces/{workspace_id}/codebases/{codebase_id}/snapshots",
    "POST /api/workspaces/{workspace_id}/codebases/{codebase_id}/quality/feedback",
    "POST /api/workspaces/{workspace_id}/sources",
    "POST /api/workspaces/{workspace_id}/build/start",
    "POST /api/workspaces/{workspace_id}/query",
    "GET /api/workspaces/{workspace_id}/graph/neighbors",
    "POST /api/v1/knowledge/query",
}
GOLDEN_MCP = {
    "knowledge_codebase_import",
    "knowledge_codebase_snapshot",
    "knowledge_code_quality_feedback",
    "knowledge_source_import",
    "knowledge_build_start",
    "knowledge_query_v2",
    "knowledge_quality_summary",
    "knowledge_graph_neighbors",
}
GOLDEN_CLI = {
    "knowledge code import",
    "knowledge code snapshot",
    "knowledge code quality feedback",
    "knowledge source import",
    "knowledge build start",
    "knowledge query",
    "knowledge quality summary",
    "knowledge graph neighbors",
}
GOLDEN_CAPABILITIES = {
    "agent_context_pack",
    "codebase_import",
    "codebase_snapshot",
    "project_overview",
    "source_import",
    "query",
    "build",
    "quality",
    "graph",
    "source_trace",
}


class CodebaseInventoryService:
    def __init__(self, workspace: Path, *, workspace_id: str) -> None:
        self.workspace = workspace
        self.workspace_id = workspace_id
        self.registry = CodebaseRegistry(workspace, workspace_id=workspace_id)
        self.snapshots = CodebaseSnapshotService(workspace, workspace_id=workspace_id)

    def build_inventory(self, codebase_id: str, *, snapshot_id: str | None = None) -> dict[str, Any]:
        asset = self.registry.describe(codebase_id)
        if asset.status != "active":
            raise ValueError("CODEBASE_NOT_ACTIVE")
        resolved_snapshot_id = snapshot_id or self._latest_snapshot_id(codebase_id)
        snapshot = self.snapshots.read_snapshot(codebase_id, resolved_snapshot_id)
        files = read_jsonl(snapshot_files_path(self.workspace, codebase_id, resolved_snapshot_id))
        root = Path(asset.root_path).expanduser().resolve()
        included_files = [row for row in files if row.get("included") and isinstance(row.get("path"), str)]

        surfaces: list[dict[str, Any]] = []
        surfaces.extend(_extract_http_surfaces(root, included_files, self.workspace_id, codebase_id, resolved_snapshot_id))
        surfaces.extend(_extract_mcp_surfaces(root, included_files, self.workspace_id, codebase_id, resolved_snapshot_id))
        surfaces.extend(_extract_cli_surfaces(root, included_files, self.workspace_id, codebase_id, resolved_snapshot_id))
        surfaces.extend(_extract_frontend_surfaces(root, included_files, self.workspace_id, codebase_id, resolved_snapshot_id))
        surfaces = _dedupe_surfaces(surfaces)

        capabilities = _build_capabilities(surfaces, self.workspace_id, codebase_id, resolved_snapshot_id)
        alignment = _build_alignment(capabilities, surfaces, self.workspace_id, codebase_id, resolved_snapshot_id)
        summary = _build_summary(
            surfaces,
            capabilities,
            alignment,
            self.workspace_id,
            codebase_id,
            resolved_snapshot_id,
        )
        refs = inventory_artifact_refs(codebase_id, resolved_snapshot_id)
        summary["artifact_refs"] = refs
        alignment["artifact_refs"] = refs

        write_jsonl(inventory_surfaces_path(self.workspace, codebase_id, resolved_snapshot_id), surfaces)
        write_jsonl(inventory_capabilities_path(self.workspace, codebase_id, resolved_snapshot_id), capabilities)
        write_json(inventory_alignment_path(self.workspace, codebase_id, resolved_snapshot_id), alignment)
        write_json(inventory_summary_path(self.workspace, codebase_id, resolved_snapshot_id), summary)
        return {
            "summary": summary,
            "surfaces": surfaces,
            "capabilities": capabilities,
            "alignment_matrix": alignment,
        }

    def read_inventory(self, codebase_id: str, *, snapshot_id: str | None = None) -> dict[str, Any]:
        resolved_snapshot_id = snapshot_id or self._latest_snapshot_id(codebase_id)
        self.registry.describe(codebase_id)
        summary = read_json(inventory_summary_path(self.workspace, codebase_id, resolved_snapshot_id), None)
        if not summary:
            raise FileNotFoundError("INVENTORY_NOT_FOUND")
        return {
            "summary": summary,
            "surfaces": read_jsonl(inventory_surfaces_path(self.workspace, codebase_id, resolved_snapshot_id)),
            "capabilities": read_jsonl(inventory_capabilities_path(self.workspace, codebase_id, resolved_snapshot_id)),
            "alignment_matrix": read_json(inventory_alignment_path(self.workspace, codebase_id, resolved_snapshot_id), {}),
        }

    def read_surfaces(self, codebase_id: str, *, snapshot_id: str | None = None, surface_type: str | None = None) -> list[dict[str, Any]]:
        inventory = self.read_inventory(codebase_id, snapshot_id=snapshot_id)
        surfaces = inventory["surfaces"]
        if surface_type:
            allowed = {row["surface_type"] for row in surfaces}
            if surface_type not in allowed:
                raise ValueError("INVALID_SURFACE_TYPE")
            surfaces = [row for row in surfaces if row.get("surface_type") == surface_type]
        return surfaces

    def read_capabilities(self, codebase_id: str, *, snapshot_id: str | None = None) -> list[dict[str, Any]]:
        return self.read_inventory(codebase_id, snapshot_id=snapshot_id)["capabilities"]

    def _latest_snapshot_id(self, codebase_id: str) -> str:
        snapshots = self.snapshots.list_snapshots(codebase_id, limit=1)
        if not snapshots:
            raise FileNotFoundError("SNAPSHOT_NOT_FOUND")
        return str(snapshots[0]["snapshot_id"])


def inventory_artifact_refs(codebase_id: str, snapshot_id: str) -> list[dict[str, str]]:
    return [
        {"type": "inventory_surfaces", "artifact_ref": f"inventory-surfaces://{codebase_id}/{snapshot_id}"},
        {"type": "inventory_capabilities", "artifact_ref": f"inventory-capabilities://{codebase_id}/{snapshot_id}"},
        {"type": "inventory_alignment", "artifact_ref": f"inventory-alignment://{codebase_id}/{snapshot_id}"},
        {"type": "inventory_summary", "artifact_ref": f"inventory-summary://{codebase_id}/{snapshot_id}"},
    ]


def public_inventory_payload(inventory: dict[str, Any]) -> dict[str, Any]:
    summary = inventory["summary"]
    return {
        "schema_version": summary.get("schema_version"),
        "workspace_id": summary.get("workspace_id"),
        "codebase_id": summary.get("codebase_id"),
        "snapshot_id": summary.get("snapshot_id"),
        "summary": summary,
        "surfaces": [_public_surface_payload(surface) for surface in inventory["surfaces"]],
        "capabilities": inventory["capabilities"],
        "alignment_matrix": inventory["alignment_matrix"],
    }


def _public_surface_payload(surface: dict[str, Any]) -> dict[str, Any]:
    payload = dict(surface)
    input_schema = payload.get("input_schema")
    if isinstance(input_schema, dict):
        payload["input_schema"] = _schema_as_field_list(input_schema)
    return payload


def _extract_http_surfaces(
    root: Path,
    files: list[dict[str, Any]],
    workspace_id: str,
    codebase_id: str,
    snapshot_id: str,
) -> list[dict[str, Any]]:
    surfaces: list[dict[str, Any]] = []
    for record in files:
        rel = str(record["path"])
        if not rel.startswith("backend/app/api/") or not rel.endswith(".py"):
            continue
        path = root / rel
        text = _read_text(path)
        if text is None:
            continue
        try:
            tree = ast.parse(text)
        except SyntaxError:
            continue
        router_prefixes = _router_prefixes(tree)
        for node in ast.walk(tree):
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            for decorator in node.decorator_list:
                route = _route_decorator(decorator)
                if route is None:
                    continue
                router_name, method, route_path = route
                local_prefix = router_prefixes.get(router_name, "")
                mount_prefix = _mount_prefix_for(rel, router_name)
                full_path = _join_paths(mount_prefix, local_prefix, route_path)
                stability = "legacy" if full_path.startswith("/api/v1/knowledge") else "target" if full_path.startswith("/api/workspaces") or full_path == "/api/workspaces" else "internal"
                key = f"{method.upper()} {full_path}"
                surfaces.append(
                    _surface(
                        workspace_id,
                        codebase_id,
                        snapshot_id,
                        surface_id=f"http:{method.upper()}:{full_path}",
                        surface_type="http_api",
                        name=key,
                        capability_id=normalize_capability(key),
                        stability=stability,
                        source_file=rel,
                        line_range=[decorator.lineno, getattr(node, "end_lineno", node.lineno)],
                        handler=node.name,
                        method=method.upper(),
                route_path=full_path,
                extractor="fastapi_ast",
                        confidence=1.0,
                    )
                )
    return surfaces


def _extract_mcp_surfaces(
    root: Path,
    files: list[dict[str, Any]],
    workspace_id: str,
    codebase_id: str,
    snapshot_id: str,
) -> list[dict[str, Any]]:
    source_index = _source_index(root, files)
    surfaces = []
    for spec in _mcp_specs_from_source_index(source_index):
        name = str(spec.get("name") or "")
        source_file = str(spec.get("source_file") or "")
        line_no = int(spec.get("line") or 0)
        line_range = [line_no, line_no] if source_file and line_no else None
        unresolved = None if line_range else "tool_spec_source_line_not_found"
        surfaces.append(
            _surface(
                workspace_id,
                codebase_id,
                snapshot_id,
                surface_id=f"mcp:{name}",
                surface_type="mcp_tool",
                name=name,
                capability_id=normalize_capability(name),
                stability="target" if name.startswith("knowledge_") else "internal",
                source_file=source_file,
                line_range=line_range,
                tool_name=name,
                input_schema=_public_schema(spec.get("inputSchema")),
                output_schema={"type": "object", "envelope": True},
                extractor="mcp_tool_registry",
                confidence=1.0 if line_range else 0.7,
                unresolved_reason=unresolved,
            )
        )
    return surfaces


def _mcp_specs_from_source_index(source_index: dict[str, list[str]]) -> list[dict[str, Any]]:
    specs: list[dict[str, Any]] = []
    seen: set[str] = set()
    for rel, lines in sorted(source_index.items()):
        if _is_test_like_path(rel):
            continue
        lower_rel = rel.lower()
        text = "\n".join(lines)
        if "TOOL_SPECS" not in text and "inputSchema" not in text:
            continue
        if "mcp" not in lower_rel and "tool" not in lower_rel:
            continue
        try:
            tree = ast.parse(text, filename=rel)
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            if not isinstance(node, ast.Dict):
                continue
            name = ""
            input_schema: Any = {}
            description = ""
            for key_node, value_node in zip(node.keys, node.values):
                if not isinstance(key_node, ast.Constant) or not isinstance(key_node.value, str):
                    continue
                key = key_node.value
                if key == "name" and isinstance(value_node, ast.Constant) and isinstance(value_node.value, str):
                    name = value_node.value
                elif key == "inputSchema":
                    try:
                        input_schema = ast.literal_eval(value_node)
                    except (ValueError, SyntaxError):
                        input_schema = {}
                elif key == "description" and isinstance(value_node, ast.Constant) and isinstance(value_node.value, str):
                    description = value_node.value
            if not name or name in seen:
                continue
            seen.add(name)
            specs.append(
                {
                    "name": name,
                    "description": description,
                    "inputSchema": input_schema,
                    "source_file": rel,
                    "line": getattr(node, "lineno", None),
                }
            )
    return specs


def _is_test_like_path(path: str) -> bool:
    parts = Path(path).parts
    return any(part in {"test", "tests"} or part.startswith("test_") for part in parts)


def _extract_cli_surfaces(
    root: Path,
    files: list[dict[str, Any]],
    workspace_id: str,
    codebase_id: str,
    snapshot_id: str,
) -> list[dict[str, Any]]:
    surfaces: list[dict[str, Any]] = []
    commands: dict[str, tuple[str, int]] = {}
    for record in files:
        rel = str(record["path"])
        if rel not in CLI_SOURCE_FILES:
            continue
        path = root / rel
        text = _read_text(path)
        if text is None:
            continue
        commands.update(_cli_commands_from_source(rel, text))
    for command, evidence in sorted(commands.items()):
        source_file, line = evidence
        surfaces.append(
            _surface(
                workspace_id,
                codebase_id,
                snapshot_id,
                surface_id=f"cli:{command}",
                surface_type="cli_command",
                name=command,
                capability_id=normalize_capability(command),
                stability="target",
                source_file=source_file,
                line_range=[line, line],
                command=command,
                extractor="argparse_source",
                confidence=0.9,
            )
        )
    return surfaces


def _extract_frontend_surfaces(
    root: Path,
    files: list[dict[str, Any]],
    workspace_id: str,
    codebase_id: str,
    snapshot_id: str,
) -> list[dict[str, Any]]:
    surfaces: list[dict[str, Any]] = []
    for record in files:
        rel = str(record["path"])
        if not rel.startswith("frontend/") or Path(rel).suffix not in FRONTEND_EXTENSIONS:
            continue
        text = _read_text(root / rel)
        if text is None:
            continue
        if "/api/" in text or rel.endswith(".vue"):
            line = _first_interesting_line(text, "/api/") or 1
            surfaces.append(
                _surface(
                    workspace_id,
                    codebase_id,
                    snapshot_id,
                    surface_id=f"frontend:{rel}",
                    surface_type="frontend_page" if rel.endswith(".vue") else "api_client_call",
                    name=rel,
                    capability_id=normalize_capability(rel),
                    stability="best_effort",
                    source_file=rel,
                    line_range=[line, line],
                    extractor="frontend_static_best_effort",
                    confidence=0.5,
                    unresolved_reason="best_effort_frontend_inventory",
                )
            )
    return surfaces


def _build_capabilities(
    surfaces: list[dict[str, Any]],
    workspace_id: str,
    codebase_id: str,
    snapshot_id: str,
) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = {}
    for surface in surfaces:
        grouped.setdefault(str(surface.get("capability_id") or "unresolved"), []).append(surface)
    capabilities: list[dict[str, Any]] = []
    for capability_id, items in sorted(grouped.items()):
        interfaces: dict[str, list[str]] = {}
        unresolved = []
        for item in items:
            interface = _interface_for_surface_type(str(item.get("surface_type") or ""))
            interfaces.setdefault(interface, []).append(str(item["surface_id"]))
            if item.get("unresolved_reason"):
                unresolved.append(str(item["surface_id"]))
        surface_counts = {key: len(value) for key, value in sorted(interfaces.items())}
        capability = {
            "schema_version": INVENTORY_SCHEMA_VERSION,
            "workspace_id": workspace_id,
            "codebase_id": codebase_id,
            "snapshot_id": snapshot_id,
            "capability_id": capability_id,
            "name": capability_id.replace("_", " ").title(),
            "surface_ids": sorted(item["surface_id"] for item in items),
            "surface_counts": surface_counts,
            "interfaces": {key: sorted(value) for key, value in sorted(interfaces.items())},
            "missing_interfaces": sorted(set(["http", "mcp", "cli"]) - set(interfaces)),
            "unresolved_surface_ids": sorted(unresolved),
            "confidence": min(float(item.get("confidence") or 0.0) for item in items) if items else 0.0,
        }
        capabilities.append(capability)
    return capabilities


def _build_alignment(
    capabilities: list[dict[str, Any]],
    surfaces: list[dict[str, Any]],
    workspace_id: str,
    codebase_id: str,
    snapshot_id: str,
) -> dict[str, Any]:
    rows = {}
    for capability in capabilities:
        interfaces = capability.get("interfaces") or {}
        rows[capability["capability_id"]] = {
            "http": interfaces.get("http", []),
            "mcp": interfaces.get("mcp", []),
            "cli": interfaces.get("cli", []),
            "frontend": interfaces.get("frontend", []),
            "missing_interfaces": capability.get("missing_interfaces", []),
            "unresolved_surface_ids": capability.get("unresolved_surface_ids", []),
        }
    return {
        "schema_version": INVENTORY_SCHEMA_VERSION,
        "workspace_id": workspace_id,
        "codebase_id": codebase_id,
        "snapshot_id": snapshot_id,
        "created_at": now(),
        "capabilities": rows,
        "surface_count": len(surfaces),
        "capability_count": len(capabilities),
    }


def _build_summary(
    surfaces: list[dict[str, Any]],
    capabilities: list[dict[str, Any]],
    alignment: dict[str, Any],
    workspace_id: str,
    codebase_id: str,
    snapshot_id: str,
) -> dict[str, Any]:
    counts: dict[str, int] = {}
    for surface in surfaces:
        kind = str(surface.get("surface_type") or "unknown")
        counts[kind] = counts.get(kind, 0) + 1
    unresolved = [surface for surface in surfaces if surface.get("unresolved_reason") or surface.get("capability_id") == "unresolved"]
    golden_checks = _golden_checks(surfaces, capabilities)
    return {
        "schema_version": INVENTORY_SCHEMA_VERSION,
        "workspace_id": workspace_id,
        "codebase_id": codebase_id,
        "snapshot_id": snapshot_id,
        "created_at": now(),
        "surface_counts": dict(sorted(counts.items())),
        "surface_count": len(surfaces),
        "capability_count": len(capabilities),
        "unresolved_count": len(unresolved),
        "unresolved_ratio": (len(unresolved) / len(surfaces)) if surfaces else 1.0,
        "golden_checks": golden_checks,
        "alignment_capability_count": len(alignment.get("capabilities", {})),
    }


def _golden_checks(surfaces: list[dict[str, Any]], capabilities: list[dict[str, Any]]) -> dict[str, Any]:
    http = {f"{row.get('method')} {row.get('route_path')}" for row in surfaces if row.get("surface_type") == "http_api"}
    mcp = {str(row.get("tool_name")) for row in surfaces if row.get("surface_type") == "mcp_tool"}
    cli = {str(row.get("command")) for row in surfaces if row.get("surface_type") == "cli_command"}
    capability_ids = {str(row.get("capability_id")) for row in capabilities}
    return {
        "http": _check_set(GOLDEN_HTTP, http),
        "mcp": _check_set(GOLDEN_MCP, mcp),
        "cli": _check_set(GOLDEN_CLI, cli),
        "capabilities": _check_set(GOLDEN_CAPABILITIES, capability_ids),
    }


def _check_set(expected: set[str], actual: set[str]) -> dict[str, Any]:
    missing = sorted(expected - actual)
    return {"passed": not missing, "missing": missing}


def normalize_capability(value: str) -> str:
    text = value.lower().replace("_v2", "").replace("knowledge_", "").replace(":", " ")
    text = text.replace("-", " ").replace("_", " ")
    if "agent context pack" in text or "context pack" in text or "context packs" in text:
        return "agent_context_pack"
    if "devwiki" in text:
        return "devwiki"
    if "project overview" in text or "code overview" in text or "/overview" in text:
        return "project_overview"
    if any(token in text for token in ["codebase import", "codebases", "code import"]) and "snapshot" not in text:
        return "codebase_import"
    if "codebase snapshot" in text or "snapshots" in text or "code snapshot" in text:
        return "codebase_snapshot"
    if "source trace" in text or "trace source" in text:
        return "source_trace"
    if "source import" in text or "/sources" in text or " source " in f" {text} ":
        return "source_import"
    if "query" in text:
        return "query"
    if "build" in text:
        return "build"
    if "quality" in text or "correction" in text or "low signal" in text:
        return "quality"
    if "graph" in text or "graphrag" in text or "neighbors" in text or "community" in text:
        return "graph"
    if "session" in text:
        return "session"
    if "distill" in text:
        return "distill"
    if "workspace" in text:
        return "workspace"
    if "capabilities" in text:
        return "capabilities"
    return "unresolved"


def _surface(
    workspace_id: str,
    codebase_id: str,
    snapshot_id: str,
    *,
    surface_id: str,
    surface_type: str,
    name: str,
    capability_id: str,
    stability: str,
    source_file: str,
    line_range: list[int] | None,
    handler: str | None = None,
    method: str | None = None,
    route_path: str | None = None,
    tool_name: str | None = None,
    command: str | None = None,
    input_schema: Any = None,
    output_schema: Any = None,
    extractor: str,
    confidence: float,
    unresolved_reason: str | None = None,
) -> dict[str, Any]:
    return {
        "schema_version": INVENTORY_SCHEMA_VERSION,
        "workspace_id": workspace_id,
        "codebase_id": codebase_id,
        "snapshot_id": snapshot_id,
        "surface_id": surface_id,
        "surface_type": surface_type,
        "name": name,
        "capability_id": capability_id,
        "stability": stability,
        "source_file": source_file,
        "line_range": line_range,
        "handler": handler,
        "method": method,
        "route_path": route_path,
        "tool_name": tool_name,
        "command": command,
        "input_schema": input_schema,
        "output_schema": output_schema,
        "extractor": extractor,
        "confidence": confidence,
        "unresolved_reason": unresolved_reason,
    }


def _public_schema(value: Any) -> Any:
    if isinstance(value, dict):
        cleaned = {}
        for key, item in value.items():
            if key in INTERNAL_SCHEMA_FIELDS:
                continue
            if key == "properties" and isinstance(item, dict):
                cleaned[key] = {
                    prop: _public_schema(prop_schema)
                    for prop, prop_schema in item.items()
                    if prop not in INTERNAL_SCHEMA_FIELDS
                }
            else:
                cleaned[key] = _public_schema(item)
        return cleaned
    if isinstance(value, list):
        return [_public_schema(item) for item in value]
    return value


def _schema_as_field_list(schema: dict[str, Any]) -> dict[str, Any]:
    properties = schema.get("properties") if isinstance(schema.get("properties"), dict) else {}
    result = {
        "type": schema.get("type", "object"),
        "fields": [
            {"name": str(name), "schema": _public_schema(field_schema)}
            for name, field_schema in sorted(properties.items())
            if str(name) not in INTERNAL_SCHEMA_FIELDS
        ],
    }
    if isinstance(schema.get("required"), list):
        result["required"] = [str(item) for item in schema["required"] if str(item) not in INTERNAL_SCHEMA_FIELDS]
    return result


def _router_prefixes(tree: ast.AST) -> dict[str, str]:
    prefixes = {}
    for node in ast.walk(tree):
        if not isinstance(node, ast.Assign):
            continue
        if not isinstance(node.value, ast.Call):
            continue
        func = node.value.func
        if not ((isinstance(func, ast.Name) and func.id == "APIRouter") or (isinstance(func, ast.Attribute) and func.attr == "APIRouter")):
            continue
        prefix = ""
        for keyword in node.value.keywords:
            if keyword.arg == "prefix" and isinstance(keyword.value, ast.Constant) and isinstance(keyword.value.value, str):
                prefix = keyword.value.value
        for target in node.targets:
            if isinstance(target, ast.Name):
                prefixes[target.id] = prefix
    return prefixes


def _route_decorator(decorator: ast.AST) -> tuple[str, str, str] | None:
    if not isinstance(decorator, ast.Call) or not isinstance(decorator.func, ast.Attribute):
        return None
    method = decorator.func.attr
    if method not in HTTP_METHODS:
        return None
    if not isinstance(decorator.func.value, ast.Name):
        return None
    router_name = decorator.func.value.id
    if not decorator.args or not isinstance(decorator.args[0], ast.Constant) or not isinstance(decorator.args[0].value, str):
        return None
    return router_name, method, decorator.args[0].value


def _mount_prefix_for(rel: str, router_name: str) -> str:
    if rel == "backend/app/api/v1/data_service.py" and router_name == "router":
        return "/api/v1"
    if rel == "backend/app/api/v1/health.py":
        return "/api/v1"
    return "/api"


def _join_paths(*parts: str) -> str:
    path = ""
    for part in parts:
        if not part:
            continue
        if part == "/":
            continue
        path = f"{path.rstrip('/')}/{part.strip('/')}" if path else f"/{part.strip('/')}"
    return path or "/"


def _source_index(root: Path, files: list[dict[str, Any]]) -> dict[str, list[str]]:
    index = {}
    for record in files:
        rel = str(record["path"])
        if not rel.endswith(".py"):
            continue
        text = _read_text(root / rel)
        if text is not None:
            index[rel] = text.splitlines()
    return index


def _find_text_line(source_index: dict[str, list[str]], needle: str) -> tuple[str, int] | None:
    for rel, lines in sorted(source_index.items()):
        for idx, line in enumerate(lines, start=1):
            if needle in line:
                return rel, idx
    return None


def _cli_commands_from_source(rel: str, text: str) -> dict[str, tuple[str, int]]:
    commands: dict[str, tuple[str, int]] = {}
    var_paths: dict[str, list[str]] = {"subparsers": ["knowledge"], "code_subparsers": ["knowledge", "code"]}
    subparser_re = re.compile(r"(\w+)\s*=\s*(\w+)\.add_parser\(\"([^\"]+)\"")
    add_subparsers_re = re.compile(r"(\w+)\s*=\s*(\w+)\.add_subparsers")
    for line_no, line in enumerate(text.splitlines(), start=1):
        match = subparser_re.search(line)
        if match:
            var_name, parent_var, token = match.groups()
            parent_path = var_paths.get(parent_var, ["knowledge"])
            path = [*parent_path, token]
            var_paths[var_name] = path
            commands[" ".join(path)] = (rel, line_no)
            continue
        match = add_subparsers_re.search(line)
        if match:
            var_name, parent_var = match.groups()
            if parent_var in var_paths:
                var_paths[var_name] = var_paths[parent_var]
    return commands


def _dedupe_surfaces(surfaces: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_id: dict[str, dict[str, Any]] = {}
    for surface in surfaces:
        by_id.setdefault(str(surface["surface_id"]), surface)
    return [by_id[key] for key in sorted(by_id)]


def _interface_for_surface_type(surface_type: str) -> str:
    if surface_type == "http_api":
        return "http"
    if surface_type == "mcp_tool":
        return "mcp"
    if surface_type == "cli_command":
        return "cli"
    if surface_type in {"frontend_page", "api_client_call"}:
        return "frontend"
    return "other"


def _first_interesting_line(text: str, needle: str) -> int | None:
    for idx, line in enumerate(text.splitlines(), start=1):
        if needle in line:
            return idx
    return None


def _read_text(path: Path) -> str | None:
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return None

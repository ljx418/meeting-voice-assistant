"""V2.10 generic architecture pattern evidence adapters."""

from __future__ import annotations

import ast
import hashlib
import html
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "v2.10"
ACCEPTED_CONFIDENCE_MIN = 0.85
RUNTIME_ENABLED_DEFAULT = False
HTML_VIEW_ID = "architecture_pattern_evidence_report.html"
MERMAID_VIEW_ID = "architecture_pattern_adapter_map.mmd"


BUILT_IN_ADAPTERS: list[dict[str, Any]] = [
    {
        "adapter_id": "python_registry_assignment",
        "adapter_type": "registry_assignment",
        "language": "python",
        "file_globs": ["**/*.py"],
        "match_strategy": "ast_assignment",
        "confidence_policy": {"accepted_min": ACCEPTED_CONFIDENCE_MIN, "candidate_min": 0.4},
        "unsupported_claims": ["runtime_call", "data_flow", "control_flow"],
    },
    {
        "adapter_id": "python_decorator_registration",
        "adapter_type": "decorator_registration",
        "language": "python",
        "file_globs": ["**/*.py"],
        "match_strategy": "ast_decorator",
        "confidence_policy": {"accepted_min": ACCEPTED_CONFIDENCE_MIN, "candidate_min": 0.4},
        "unsupported_claims": ["runtime_call", "data_flow", "control_flow"],
    },
    {
        "adapter_id": "python_class_inheritance",
        "adapter_type": "class_inheritance",
        "language": "python",
        "file_globs": ["**/*.py"],
        "match_strategy": "ast_class_base",
        "confidence_policy": {"accepted_min": ACCEPTED_CONFIDENCE_MIN, "candidate_min": 0.4},
        "unsupported_claims": ["runtime_call", "data_flow", "control_flow"],
    },
    {
        "adapter_id": "python_factory_call",
        "adapter_type": "factory_call",
        "language": "python",
        "file_globs": ["**/*.py"],
        "match_strategy": "ast_call",
        "confidence_policy": {"accepted_min": ACCEPTED_CONFIDENCE_MIN, "candidate_min": 0.4},
        "unsupported_claims": ["runtime_call", "data_flow", "control_flow"],
    },
    {
        "adapter_id": "cli_parser_registration",
        "adapter_type": "cli_parser",
        "language": "python",
        "file_globs": ["**/*.py"],
        "match_strategy": "ast_cli_parser",
        "confidence_policy": {"accepted_min": ACCEPTED_CONFIDENCE_MIN, "candidate_min": 0.4},
        "unsupported_claims": ["runtime_call", "data_flow", "control_flow"],
    },
    {
        "adapter_id": "tui_command_table",
        "adapter_type": "tui_command_table",
        "language": "python",
        "file_globs": ["**/*.py"],
        "match_strategy": "ast_command_table",
        "confidence_policy": {"accepted_min": ACCEPTED_CONFIDENCE_MIN, "candidate_min": 0.4},
        "unsupported_claims": ["runtime_call", "data_flow", "control_flow"],
    },
    {
        "adapter_id": "workflow_manifest",
        "adapter_type": "manifest",
        "language": "json_yaml_toml",
        "file_globs": ["**/*workflow*.json", "**/*workflow*.yaml", "**/*workflow*.yml", "**/*workflow*.toml"],
        "match_strategy": "manifest_candidate",
        "confidence_policy": {"accepted_min": ACCEPTED_CONFIDENCE_MIN, "candidate_min": 0.4},
        "unsupported_claims": ["runtime_call", "data_flow", "control_flow"],
    },
    {
        "adapter_id": "agent_worker_registry",
        "adapter_type": "agent_registry",
        "language": "python",
        "file_globs": ["**/*.py"],
        "match_strategy": "ast_assignment",
        "confidence_policy": {"accepted_min": ACCEPTED_CONFIDENCE_MIN, "candidate_min": 0.4},
        "unsupported_claims": ["runtime_call", "data_flow", "control_flow"],
    },
    {
        "adapter_id": "adapter_catalog",
        "adapter_type": "adapter_catalog",
        "language": "python",
        "file_globs": ["**/*.py"],
        "match_strategy": "ast_assignment",
        "confidence_policy": {"accepted_min": ACCEPTED_CONFIDENCE_MIN, "candidate_min": 0.4},
        "unsupported_claims": ["runtime_call", "data_flow", "control_flow"],
    },
    {
        "adapter_id": "external_app_registry",
        "adapter_type": "external_app_registry",
        "language": "python",
        "file_globs": ["**/*.py"],
        "match_strategy": "ast_assignment",
        "confidence_policy": {"accepted_min": ACCEPTED_CONFIDENCE_MIN, "candidate_min": 0.4},
        "unsupported_claims": ["runtime_call", "data_flow", "control_flow"],
    },
    {
        "adapter_id": "architecture_manifest",
        "adapter_type": "architecture_manifest",
        "language": "json_yaml_toml",
        "file_globs": ["architecture.patterns.json", "docs/architecture.patterns.json", "**/architecture.manifest.json"],
        "match_strategy": "manifest_candidate",
        "confidence_policy": {"accepted_min": ACCEPTED_CONFIDENCE_MIN, "candidate_min": 0.4},
        "unsupported_claims": ["runtime_call", "data_flow", "control_flow"],
    },
    {
        "adapter_id": "runtime_introspection_candidate",
        "adapter_type": "runtime_candidate",
        "language": "command_json",
        "file_globs": [],
        "match_strategy": "disabled_by_default",
        "confidence_policy": {"accepted_min": ACCEPTED_CONFIDENCE_MIN, "candidate_min": 0.4},
        "unsupported_claims": ["runtime_call", "data_flow", "control_flow"],
        "enabled": RUNTIME_ENABLED_DEFAULT,
    },
]


GENERIC_NAME_HINTS = (
    "registry",
    "registries",
    "handlers",
    "commands",
    "workflows",
    "workers",
    "adapters",
    "providers",
    "plugins",
    "tools",
    "routes",
    "entrypoints",
)


def build_pattern_evidence_v2(
    *,
    workspace_id: str,
    codebase_id: str,
    snapshot_id: str,
    repo_root: Path,
    files: list[dict[str, Any]],
    symbols: list[dict[str, Any]],
    document_claims: list[dict[str, Any]] | None = None,
    runtime_enabled: bool = False,
    artifact_refs: list[dict[str, str]],
) -> dict[str, Any]:
    registry = _registry_payload(workspace_id, codebase_id, snapshot_id, runtime_enabled=runtime_enabled)
    python_files = _python_files(files)
    attempts: list[dict[str, Any]] = []
    bindings: list[dict[str, Any]] = []
    lookups: list[dict[str, Any]] = []
    blockers: list[dict[str, Any]] = []
    parsed_python: list[dict[str, Any]] = []
    global_definition_candidates: dict[str, list[dict[str, Any]]] = {}
    for item in python_files:
        path = str(item.get("path") or item.get("repo_relative_path") or "")
        full_path = repo_root / path
        try:
            source = full_path.read_text(encoding="utf-8", errors="ignore")
            tree = ast.parse(source)
        except SyntaxError as exc:
            attempts.append(_attempt(workspace_id, codebase_id, snapshot_id, "python_registry_assignment", path, "blocked", "PYTHON_PARSE_ERROR"))
            blockers.append(_blocker(workspace_id, codebase_id, snapshot_id, "PYTHON_PARSE_ERROR", path, [], str(exc)))
            continue
        except OSError as exc:
            attempts.append(_attempt(workspace_id, codebase_id, snapshot_id, "python_registry_assignment", path, "blocked", "SOURCE_FILE_UNREADABLE"))
            blockers.append(_blocker(workspace_id, codebase_id, snapshot_id, "SOURCE_FILE_UNREADABLE", path, [], str(exc)))
            continue
        module_defs = _module_definitions(path, tree)
        parsed_python.append({"path": path, "tree": tree, "module_defs": module_defs})
        for name, definition in module_defs.items():
            global_definition_candidates.setdefault(name, []).append(definition)
    unique_global_defs = {name: definitions[0] for name, definitions in global_definition_candidates.items() if len(definitions) == 1}
    for parsed in parsed_python:
        path = str(parsed["path"])
        tree = parsed["tree"]
        module_defs = {**unique_global_defs, **parsed["module_defs"]}
        for adapter in _active_python_adapters(registry):
            adapter_id = str(adapter["adapter_id"])
            extractor = _python_extractor(adapter_id)
            candidates = extractor(path, tree)
            attempts.append(_attempt(workspace_id, codebase_id, snapshot_id, adapter_id, path, "matched" if candidates else "no_match", "candidate_count=%d" % len(candidates)))
            for candidate in candidates:
                binding, lookup = _bind_candidate(
                    workspace_id=workspace_id,
                    codebase_id=codebase_id,
                    snapshot_id=snapshot_id,
                    repo_root=repo_root,
                    candidate={**candidate, "adapter_id": adapter_id, "confidence_policy": adapter.get("confidence_policy", {})},
                    module_defs=module_defs,
                    symbols=symbols,
                )
                bindings.append(binding)
                if lookup:
                    lookups.append(lookup)
                if binding["status"] != "accepted":
                    blockers.append(_blocker_from_binding(binding))
    manifest_candidates, manifest_attempts, manifest_blockers = _manifest_candidates(workspace_id, codebase_id, snapshot_id, repo_root, files, bindings)
    attempts.extend(manifest_attempts)
    blockers.extend(manifest_blockers)
    runtime_candidates = [_runtime_candidate(workspace_id, codebase_id, snapshot_id, enabled=runtime_enabled)]
    doc_code = _match_document_claims(workspace_id, codebase_id, snapshot_id, document_claims or [], bindings)
    accepted = [item for item in bindings if item["status"] == "accepted"]
    status_counts = Counter(str(item.get("status") or "unknown") for item in bindings)
    adapter_counts = Counter(str(item.get("adapter_id") or "unknown") for item in accepted)
    blocker_counts = Counter(str(item.get("code") or "UNKNOWN") for item in blockers)
    summary = {
        "schema_version": SCHEMA_VERSION,
        "workspace_id": workspace_id,
        "codebase_id": codebase_id,
        "snapshot_id": snapshot_id,
        "adapter_count": len(registry["adapters"]),
        "attempt_count": len(attempts),
        "binding_count": len(bindings),
        "accepted_evidence_count": len(accepted),
        "needs_review_count": int(status_counts.get("needs_review", 0)),
        "blocked_count": int(status_counts.get("blocked", 0)),
        "adapter_accepted_counts": dict(sorted(adapter_counts.items())),
        "blocker_counts": dict(sorted(blocker_counts.items())),
        "truth_sample_count": min(20, len(accepted)),
        "truth_sample_passed_count": min(20, len(accepted)),
        "runtime_enabled": runtime_enabled,
        "evidence_status": "accepted_evidence_available" if accepted else "structured_blocker",
    }
    report = _report_payload(workspace_id, codebase_id, snapshot_id, summary, registry, attempts, bindings, blockers, doc_code, artifact_refs)
    views = {
        HTML_VIEW_ID: {"content_type": "text/html", "content": render_pattern_evidence_html(report)},
        MERMAID_VIEW_ID: {"content_type": "text/mermaid", "content": render_pattern_evidence_mermaid(report)},
    }
    return {
        "schema_version": SCHEMA_VERSION,
        "workspace_id": workspace_id,
        "codebase_id": codebase_id,
        "snapshot_id": snapshot_id,
        "registry": registry,
        "attempts": attempts,
        "bindings": bindings,
        "definition_lookups": lookups,
        "doc_code_evidence_v3": doc_code,
        "manifest_candidates": manifest_candidates,
        "runtime_candidates": runtime_candidates,
        "blockers": blockers,
        "summary": summary,
        "report": report,
        "views": views,
        "artifact_refs": artifact_refs,
        "created_at": _now(),
    }


def public_pattern_evidence_payload(payload: dict[str, Any], artifact_refs: list[dict[str, str]]) -> dict[str, Any]:
    summary = dict(payload.get("summary") or {})
    return {
        "schema_version": SCHEMA_VERSION,
        "summary": summary,
        "registry": payload.get("registry", {}),
        "attempts": list(payload.get("attempts", []))[:500],
        "accepted_evidence": [item for item in payload.get("bindings", []) if item.get("status") == "accepted"][:240],
        "needs_review": [item for item in payload.get("bindings", []) if item.get("status") == "needs_review"][:160],
        "blockers": list(payload.get("blockers", []))[:240],
        "doc_code_evidence_v3": list(payload.get("doc_code_evidence_v3", []))[:240],
        "artifact_refs": artifact_refs,
    }


def public_pattern_blockers_payload(payload: dict[str, Any], artifact_refs: list[dict[str, str]]) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "summary": payload.get("summary", {}),
        "blockers": list(payload.get("blockers", []))[:500],
        "artifact_refs": artifact_refs,
    }


def public_pattern_view_payload(view: dict[str, Any], artifact_refs: list[dict[str, str]]) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "codebase_id": view.get("codebase_id"),
        "snapshot_id": view.get("snapshot_id"),
        "view_id": view.get("view_id"),
        "content_type": view.get("content_type"),
        "content": view.get("content") or "",
        "artifact_refs": artifact_refs,
    }


def render_pattern_evidence_html(report: dict[str, Any]) -> str:
    summary = report.get("summary", {})
    sections = []
    sections.append("<h1>V2.10 Pattern Evidence Report</h1>")
    sections.append("<section><h2>Summary</h2><ul>")
    for key in ("adapter_count", "attempt_count", "binding_count", "accepted_evidence_count", "needs_review_count", "blocked_count"):
        sections.append(f"<li>{html.escape(key)}: {html.escape(str(summary.get(key, 0)))}</li>")
    sections.append("</ul></section>")
    sections.append("<section><h2>Accepted Evidence</h2><table><tr><th>Adapter</th><th>Label</th><th>Path</th><th>Lines</th></tr>")
    for item in report.get("accepted_evidence", [])[:120]:
        sections.append(
            "<tr>"
            f"<td>{html.escape(str(item.get('adapter_id') or ''))}</td>"
            f"<td>{html.escape(str(item.get('label') or ''))}</td>"
            f"<td>{html.escape(str(item.get('source_path') or ''))}</td>"
            f"<td>{html.escape(str(item.get('definition_line_range') or item.get('line_range') or []))}</td>"
            "</tr>"
        )
    sections.append("</table></section>")
    sections.append("<section><h2>Blockers</h2><table><tr><th>Code</th><th>Path</th><th>Reason</th></tr>")
    for item in report.get("blockers", [])[:160]:
        sections.append(
            "<tr>"
            f"<td>{html.escape(str(item.get('code') or ''))}</td>"
            f"<td>{html.escape(str(item.get('source_path') or ''))}</td>"
            f"<td>{html.escape(str(item.get('reason') or ''))}</td>"
            "</tr>"
        )
    sections.append("</table></section>")
    return "<!doctype html><html><head><meta charset=\"utf-8\"><title>V2.10 Pattern Evidence</title></head><body>" + "".join(sections) + "</body></html>"


def render_pattern_evidence_mermaid(report: dict[str, Any]) -> str:
    lines = ["flowchart LR"]
    lines.append("  root[\"V2.10 Pattern Evidence\"]")
    for adapter, count in sorted((report.get("summary", {}).get("adapter_accepted_counts") or {}).items()):
        node_id = _safe_node_id(adapter)
        label = _escape_mermaid_label(f"{adapter}: {count}")
        lines.append(f"  root --> {node_id}[\"{label}\"]")
    if len(lines) == 1:
        lines.append("  root --> no_evidence[\"No accepted evidence\"]")
    return "\n".join(lines) + "\n"


def _registry_payload(workspace_id: str, codebase_id: str, snapshot_id: str, *, runtime_enabled: bool) -> dict[str, Any]:
    adapters = []
    for adapter in BUILT_IN_ADAPTERS:
        item = dict(adapter)
        if item["adapter_id"] == "runtime_introspection_candidate":
            item["enabled"] = runtime_enabled
            item["status"] = "enabled" if runtime_enabled else "disabled"
        else:
            item["enabled"] = True
            item["status"] = "enabled"
        adapters.append(item)
    return {
        "schema_version": SCHEMA_VERSION,
        "workspace_id": workspace_id,
        "codebase_id": codebase_id,
        "snapshot_id": snapshot_id,
        "adapters": adapters,
        "created_at": _now(),
    }


def _python_files(files: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [item for item in files if str(item.get("path") or item.get("repo_relative_path") or "").endswith(".py")]


def _module_definitions(path: str, tree: ast.AST) -> dict[str, dict[str, Any]]:
    defs: dict[str, dict[str, Any]] = {}
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            defs[node.name] = {"path": path, "line_range": [int(node.lineno), int(getattr(node, "end_lineno", node.lineno))], "kind": node.__class__.__name__.lower()}
    return defs


def _extract_registry_assignments(path: str, tree: ast.AST) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for node in ast.walk(tree):
        if not isinstance(node, (ast.Assign, ast.AnnAssign)):
            continue
        targets = list(node.targets) if isinstance(node, ast.Assign) else [node.target]
        target_names = [_name(target) for target in targets if _name(target)]
        if not any(_is_registry_name(name) for name in target_names):
            continue
        value = node.value
        if isinstance(value, ast.Dict):
            for key, val in zip(value.keys, value.values):
                label = _literal_text(key)
                symbol = _name(val)
                if label:
                    rows.append(_candidate(path, "registry_key_to_definition", label, symbol, [node.lineno, getattr(node, "end_lineno", node.lineno)]))
        elif isinstance(value, (ast.List, ast.Tuple, ast.Set)):
            for elt in value.elts:
                symbol = _name(elt)
                if symbol:
                    rows.append(_candidate(path, "registry_item_to_definition", symbol, symbol, [node.lineno, getattr(node, "end_lineno", node.lineno)]))
        else:
            rows.append(_candidate(path, "dynamic_registry", ",".join(target_names), None, [node.lineno, getattr(node, "end_lineno", node.lineno)], status_hint="needs_review"))
    return rows


def _extract_decorators(path: str, tree: ast.AST) -> list[dict[str, Any]]:
    rows = []
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) or not node.decorator_list:
            continue
        for deco in node.decorator_list:
            name = _call_name(deco)
            if name and any(hint in name.lower() for hint in ("route", "tool", "command", "register", "handler")):
                rows.append(_candidate(path, "decorator_to_definition", node.name, node.name, [getattr(deco, "lineno", node.lineno), getattr(node, "end_lineno", node.lineno)]))
    return rows


def _extract_class_inheritance(path: str, tree: ast.AST) -> list[dict[str, Any]]:
    rows = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.bases:
            base_names = [_name(base) for base in node.bases if _name(base)]
            if any(_is_architecture_base(name) for name in base_names):
                rows.append(_candidate(path, "class_inheritance_to_definition", node.name, node.name, [node.lineno, getattr(node, "end_lineno", node.lineno)]))
    return rows


def _extract_factory_calls(path: str, tree: ast.AST) -> list[dict[str, Any]]:
    rows = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        name = _call_name(node)
        if not name or not any(hint in name.lower() for hint in ("register", "add_", "include_", "factory", "bind")):
            continue
        label = _literal_text(node.args[0]) if node.args else name
        symbol = None
        for arg in list(node.args[1:]) + [kw.value for kw in node.keywords]:
            symbol = _name(arg)
            if symbol:
                break
        rows.append(_candidate(path, "factory_call_to_definition", label or name, symbol, [node.lineno, getattr(node, "end_lineno", node.lineno)], status_hint=None if symbol else "needs_review"))
    return rows


def _extract_cli_registrations(path: str, tree: ast.AST) -> list[dict[str, Any]]:
    rows = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            name = _call_name(node)
            if name and ("add_parser" in name or "add_subparser" in name):
                label = _literal_text(node.args[0]) if node.args else name
                rows.append(_candidate(path, "cli_parser_registration", label or name, None, [node.lineno, getattr(node, "end_lineno", node.lineno)], status_hint="needs_review"))
    return rows


def _extract_command_tables(path: str, tree: ast.AST) -> list[dict[str, Any]]:
    rows = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Assign):
            continue
        names = [_name(target) for target in node.targets]
        if not any(name and ("command" in name.lower() or "keybinding" in name.lower()) for name in names):
            continue
        if isinstance(node.value, ast.Dict):
            for key, val in zip(node.value.keys, node.value.values):
                label = _literal_text(key)
                symbol = _name(val)
                if label:
                    rows.append(_candidate(path, "command_table_to_definition", label, symbol, [node.lineno, getattr(node, "end_lineno", node.lineno)], status_hint=None if symbol else "needs_review"))
    return rows


def _python_extractor(adapter_id: str):
    return {
        "python_registry_assignment": _extract_registry_assignments,
        "agent_worker_registry": _extract_registry_assignments,
        "adapter_catalog": _extract_registry_assignments,
        "external_app_registry": _extract_registry_assignments,
        "python_decorator_registration": _extract_decorators,
        "python_class_inheritance": _extract_class_inheritance,
        "python_factory_call": _extract_factory_calls,
        "cli_parser_registration": _extract_cli_registrations,
        "tui_command_table": _extract_command_tables,
    }[adapter_id]


def _active_python_adapters(registry: dict[str, Any]) -> list[dict[str, Any]]:
    supported = set(_supported_python_adapter_ids())
    return [
        adapter
        for adapter in registry.get("adapters", [])
        if adapter.get("adapter_id") in supported
        and adapter.get("status") == "enabled"
        and adapter.get("language") == "python"
    ]


def _supported_python_adapter_ids() -> tuple[str, ...]:
    return (
        "python_registry_assignment",
        "agent_worker_registry",
        "adapter_catalog",
        "external_app_registry",
        "python_decorator_registration",
        "python_class_inheritance",
        "python_factory_call",
        "cli_parser_registration",
        "tui_command_table",
    )


def _bind_candidate(*, workspace_id: str, codebase_id: str, snapshot_id: str, repo_root: Path, candidate: dict[str, Any], module_defs: dict[str, dict[str, Any]], symbols: list[dict[str, Any]]) -> tuple[dict[str, Any], dict[str, Any] | None]:
    source_path = str(candidate["source_path"])
    symbol_name = candidate.get("symbol_name")
    definition = module_defs.get(str(symbol_name or "")) or _symbol_definition(symbols, source_path, symbol_name)
    lookup = None
    needs_review = []
    status = "accepted"
    confidence = 0.9
    definition_path = source_path
    definition_line_range = list(candidate.get("line_range") or [])
    if definition:
        definition_path = str(definition.get("path") or source_path)
        definition_line_range = list(definition.get("line_range") or definition_line_range)
        lookup = _lookup_result(workspace_id, codebase_id, snapshot_id, source_path, symbol_name, definition_path, definition_line_range, "resolved")
    elif candidate.get("status_hint") == "needs_review":
        status = "needs_review"
        confidence = 0.55
        needs_review.append({"code": "DYNAMIC_REGISTRY_UNRESOLVED", "reason": "Candidate uses dynamic or computed expression."})
        lookup = _lookup_result(workspace_id, codebase_id, snapshot_id, source_path, symbol_name, "", [], "unresolved")
    elif symbol_name:
        status = "needs_review"
        confidence = 0.6
        needs_review.append({"code": "DEFINITION_LOOKUP_UNAVAILABLE", "reason": "Symbol could not be resolved by local AST definitions."})
        lookup = _lookup_result(workspace_id, codebase_id, snapshot_id, source_path, symbol_name, "", [], "unresolved")
    else:
        status = "needs_review"
        confidence = 0.5
        needs_review.append({"code": "MANIFEST_BINDING_MISSING", "reason": "Candidate has no statically resolvable symbol."})
    truth_check = _truth_check(repo_root, definition_path, definition_line_range)
    if truth_check != "passed":
        status = "needs_review" if status != "blocked" else status
        confidence = min(confidence, 0.55)
        needs_review.append({"code": "LINE_RANGE_INVALID", "reason": "Definition line range could not be truth checked."})
    binding_id = _stable_id("binding", codebase_id, snapshot_id, candidate.get("adapter_id"), source_path, str(candidate.get("line_range")), str(symbol_name), str(definition_line_range))
    return {
        "schema_version": SCHEMA_VERSION,
        "workspace_id": workspace_id,
        "codebase_id": codebase_id,
        "snapshot_id": snapshot_id,
        "binding_id": binding_id,
        "surface_id": _stable_id("surface", candidate.get("adapter_id"), candidate.get("label"), source_path),
        "surface_type": str(candidate.get("binding_type") or "architecture_pattern"),
        "binding_type": str(candidate.get("binding_type") or "pattern_to_definition"),
        "label": str(candidate.get("label") or symbol_name or ""),
        "source_path": source_path,
        "line_range": list(candidate.get("line_range") or []),
        "definition_path": definition_path,
        "definition_line_range": definition_line_range,
        "symbol_id": _stable_id("symbol", definition_path, symbol_name or candidate.get("label")),
        "adapter_id": str(candidate.get("adapter_id") or ""),
        "confidence": confidence,
        "status": status,
        "truth_check": truth_check,
        "evidence_refs": [_evidence_ref(definition_path, definition_line_range, binding_id)] if status == "accepted" else [],
        "needs_review": needs_review,
        "unsupported_claims": ["runtime_call", "data_flow", "control_flow"],
    }, lookup


def _match_document_claims(workspace_id: str, codebase_id: str, snapshot_id: str, claims: list[dict[str, Any]], bindings: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows = []
    accepted = [item for item in bindings if item.get("status") == "accepted"]
    for claim in claims[:500]:
        claim_text = " ".join(str(claim.get(key) or "") for key in ("label", "text", "normalized_label", "claim_type")).lower()
        best = None
        for binding in accepted:
            label = str(binding.get("label") or "").lower()
            if label and label in claim_text:
                best = binding
                break
        if best:
            status = "matched"
            strategy = "adapter_binding"
            confidence = 0.86
            code_refs = list(best.get("evidence_refs") or [])
            needs_review = []
        else:
            status = "missing_code_evidence"
            strategy = "token_overlap_only"
            confidence = 0.45
            code_refs = []
            needs_review = [{"code": "CODE_EVIDENCE_MISSING", "reason": "No accepted V2.10 binding matched this document claim."}]
        rows.append(
            {
                "schema_version": SCHEMA_VERSION,
                "workspace_id": workspace_id,
                "codebase_id": codebase_id,
                "snapshot_id": snapshot_id,
                "match_id": _stable_id("doc-code-v3", codebase_id, snapshot_id, claim.get("claim_id"), best.get("binding_id") if best else ""),
                "doc_claim_id": claim.get("claim_id") or claim.get("doc_id") or _stable_id("claim", str(claim)),
                "binding_id": best.get("binding_id") if best else None,
                "status": status,
                "match_strategy": strategy,
                "confidence": confidence,
                "document_evidence_refs": list(claim.get("evidence_refs") or claim.get("evidence") or []),
                "code_evidence_refs": code_refs,
                "needs_review": needs_review,
                "blockers": [],
            }
        )
    documented_binding_ids = {row.get("binding_id") for row in rows if row.get("binding_id")}
    for binding in accepted:
        if binding["binding_id"] not in documented_binding_ids:
            rows.append(
                {
                    "schema_version": SCHEMA_VERSION,
                    "workspace_id": workspace_id,
                    "codebase_id": codebase_id,
                    "snapshot_id": snapshot_id,
                    "match_id": _stable_id("code-not-documented", binding["binding_id"]),
                    "doc_claim_id": None,
                    "binding_id": binding["binding_id"],
                    "status": "code_not_documented",
                    "match_strategy": "adapter_binding",
                    "confidence": 0.8,
                    "document_evidence_refs": [],
                    "code_evidence_refs": list(binding.get("evidence_refs") or []),
                    "needs_review": [{"code": "DOCUMENTATION_MISSING", "reason": "Accepted code pattern has no matching document claim."}],
                    "blockers": [],
                }
            )
    return rows


def _manifest_candidates(workspace_id: str, codebase_id: str, snapshot_id: str, repo_root: Path, files: list[dict[str, Any]], bindings: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    candidates = []
    attempts = []
    blockers = []
    binding_paths = {str(item.get("definition_path") or item.get("source_path") or "") for item in bindings if item.get("status") == "accepted"}
    for item in files:
        path = str(item.get("path") or item.get("repo_relative_path") or "")
        if not _looks_manifest(path):
            continue
        attempts.append(_attempt(workspace_id, codebase_id, snapshot_id, "architecture_manifest", path, "matched", "manifest_candidate"))
        status = "candidate"
        binding_id = None
        needs_review = [{"code": "MANIFEST_BINDING_MISSING", "reason": "Manifest candidate is not accepted until statically bound to code."}]
        try:
            text = (repo_root / path).read_text(encoding="utf-8", errors="ignore")
        except OSError:
            text = ""
        for binding in bindings:
            if str(binding.get("definition_path") or "") in text or str(binding.get("source_path") or "") in text:
                status = "bound" if binding.get("status") == "accepted" else "candidate"
                binding_id = binding.get("binding_id")
                needs_review = [] if status == "bound" else needs_review
                break
        if status != "bound" and path not in binding_paths:
            blockers.append(_blocker(workspace_id, codebase_id, snapshot_id, "MANIFEST_BINDING_MISSING", path, [], "Manifest candidate lacks static code binding."))
        candidates.append(
            {
                "schema_version": SCHEMA_VERSION,
                "candidate_id": _stable_id("manifest", codebase_id, snapshot_id, path),
                "manifest_path": path,
                "surface_id": _stable_id("manifest-surface", path),
                "declared_symbol": None,
                "declared_path": None,
                "status": status,
                "binding_id": binding_id,
                "needs_review": needs_review,
            }
        )
    if not attempts:
        attempts.append(_attempt(workspace_id, codebase_id, snapshot_id, "architecture_manifest", "", "no_match", "no_manifest_files"))
    return candidates, attempts, blockers


def _runtime_candidate(workspace_id: str, codebase_id: str, snapshot_id: str, *, enabled: bool) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "candidate_id": _stable_id("runtime", codebase_id, snapshot_id, str(enabled)),
        "command_id": "runtime_introspection_disabled",
        "enabled": enabled,
        "status": "disabled" if not enabled else "candidate",
        "raw_output_stored": False,
        "surface_candidates": [],
        "needs_review": [] if enabled else [{"code": "ARCHITECTURE_RUNTIME_INTROSPECTION_DISABLED", "reason": "Runtime introspection is disabled by default."}],
    }


def _report_payload(workspace_id: str, codebase_id: str, snapshot_id: str, summary: dict[str, Any], registry: dict[str, Any], attempts: list[dict[str, Any]], bindings: list[dict[str, Any]], blockers: list[dict[str, Any]], doc_code: list[dict[str, Any]], artifact_refs: list[dict[str, str]]) -> dict[str, Any]:
    accepted = [item for item in bindings if item.get("status") == "accepted"]
    return {
        "report_id": _stable_id("pattern-report", codebase_id, snapshot_id),
        "schema_version": SCHEMA_VERSION,
        "workspace_id": workspace_id,
        "codebase_id": codebase_id,
        "snapshot_id": snapshot_id,
        "summary": summary,
        "sections": [
            {"section_id": "adapter_coverage", "title": "Adapter Coverage", "artifact_refs": artifact_refs, "needs_review": []},
            {"section_id": "accepted_evidence", "title": "Accepted Evidence", "artifact_refs": artifact_refs, "needs_review": []},
            {"section_id": "blocker_board", "title": "Blocker Board", "artifact_refs": artifact_refs, "needs_review": []},
            {"section_id": "doc_code_evidence_v3", "title": "Document-Code Evidence v3", "artifact_refs": artifact_refs, "needs_review": []},
        ],
        "adapters": registry.get("adapters", []),
        "attempts": attempts[:500],
        "accepted_evidence": accepted[:500],
        "blockers": blockers[:500],
        "doc_code_evidence_v3": doc_code[:500],
        "views": {"html": f"architecture/v2_10/views/{HTML_VIEW_ID}", "mermaid": f"architecture/v2_10/views/{MERMAID_VIEW_ID}"},
        "artifact_refs": artifact_refs,
    }


def _candidate(path: str, binding_type: str, label: str | None, symbol_name: str | None, line_range: list[int], *, status_hint: str | None = None) -> dict[str, Any]:
    return {"source_path": path, "binding_type": binding_type, "label": label or symbol_name or "", "symbol_name": symbol_name, "line_range": line_range, "status_hint": status_hint}


def _attempt(workspace_id: str, codebase_id: str, snapshot_id: str, adapter_id: str, path: str, status: str, reason: str) -> dict[str, Any]:
    return {
        "attempt_id": _stable_id("attempt", codebase_id, snapshot_id, adapter_id, path, status, reason),
        "adapter_id": adapter_id,
        "workspace_id": workspace_id,
        "codebase_id": codebase_id,
        "snapshot_id": snapshot_id,
        "path": path,
        "status": status,
        "reason": reason,
        "created_at": _now(),
    }


def _blocker(workspace_id: str, codebase_id: str, snapshot_id: str, code: str, path: str, line_range: list[int], reason: str) -> dict[str, Any]:
    return {
        "blocker_id": _stable_id("blocker", codebase_id, snapshot_id, code, path, str(line_range), reason),
        "schema_version": SCHEMA_VERSION,
        "workspace_id": workspace_id,
        "codebase_id": codebase_id,
        "snapshot_id": snapshot_id,
        "code": code,
        "source_path": path,
        "line_range": line_range,
        "reason": reason,
    }


def _blocker_from_binding(binding: dict[str, Any]) -> dict[str, Any]:
    review = (binding.get("needs_review") or [{"code": "NEEDS_REVIEW", "reason": "Binding needs review."}])[0]
    return _blocker(binding["workspace_id"], binding["codebase_id"], binding["snapshot_id"], str(review.get("code")), str(binding.get("source_path") or ""), list(binding.get("line_range") or []), str(review.get("reason") or ""))


def _lookup_result(workspace_id: str, codebase_id: str, snapshot_id: str, source_path: str, symbol_name: str | None, definition_path: str, definition_line_range: list[int], status: str) -> dict[str, Any]:
    resolved = status == "resolved"
    return {
        "lookup_id": _stable_id("lookup", codebase_id, snapshot_id, source_path, symbol_name, definition_path, str(definition_line_range), status),
        "provider": "ast_import_resolver",
        "provider_status": "available" if resolved else "partial",
        "request": {"source_path": source_path, "symbol_name": symbol_name, "import_statement": None},
        "result": {"status": status, "definition_path": definition_path, "definition_line_range": definition_line_range, "confidence": 0.9 if resolved else 0.45},
        "error": None if resolved else {"code": "DEFINITION_LOOKUP_UNAVAILABLE", "message": "Definition was not resolved by local AST lookup.", "retryable": False},
    }


def _symbol_definition(symbols: list[dict[str, Any]], source_path: str, symbol_name: str | None) -> dict[str, Any] | None:
    if not symbol_name:
        return None
    for item in symbols:
        if str(item.get("name") or "").split(".")[-1] == symbol_name:
            return {"path": str(item.get("path") or source_path), "line_range": list(item.get("line_range") or [])}
    return None


def _truth_check(repo_root: Path, path: str, line_range: list[int]) -> str:
    if not path or _looks_absolute(path):
        return "failed"
    if not line_range or len(line_range) != 2 or int(line_range[0]) <= 0 or int(line_range[1]) < int(line_range[0]):
        return "failed"
    try:
        with (repo_root / path).open("r", encoding="utf-8", errors="ignore") as fh:
            for index, _line in enumerate(fh, start=1):
                if index >= int(line_range[1]):
                    return "passed"
    except OSError:
        return "failed"
    return "failed"


def _evidence_ref(path: str, line_range: list[int], evidence_id: str) -> str:
    if not line_range:
        return f"code://{path}#{evidence_id}"
    return f"code://{path}#L{line_range[0]}-L{line_range[1]}:{evidence_id}"


def _name(node: ast.AST | None) -> str | None:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        base = _name(node.value)
        return f"{base}.{node.attr}" if base else node.attr
    if isinstance(node, ast.Call):
        return _call_name(node)
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    return None


def _call_name(node: ast.AST | None) -> str | None:
    if isinstance(node, ast.Call):
        return _name(node.func)
    return _name(node)


def _literal_text(node: ast.AST | None) -> str | None:
    if isinstance(node, ast.Constant):
        return str(node.value)
    return _name(node)


def _is_registry_name(name: str) -> bool:
    lowered = name.lower()
    return any(hint in lowered for hint in GENERIC_NAME_HINTS)


def _is_architecture_base(name: str) -> bool:
    lowered = name.lower()
    return any(hint in lowered for hint in ("workflow", "worker", "adapter", "provider", "handler", "tool", "command", "service", "plugin"))


def _looks_manifest(path: str) -> bool:
    lowered = path.lower()
    return lowered.endswith((".json", ".yaml", ".yml", ".toml")) and any(hint in lowered for hint in ("architecture", "workflow", "adapter", "manifest", "catalog", "registry"))


def _looks_absolute(path: str) -> bool:
    return path.startswith("/") or (len(path) > 2 and path[1:3] == ":\\")


def _safe_node_id(value: str) -> str:
    digest = hashlib.sha256(value.encode("utf-8")).hexdigest()[:10]
    return f"n_{digest}"


def _escape_mermaid_label(value: str) -> str:
    return value.replace('"', "'").replace("\n", " ")[:80]


def _stable_id(*parts: Any) -> str:
    return hashlib.sha256("::".join(str(part) for part in parts).encode("utf-8")).hexdigest()[:24]


def _now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

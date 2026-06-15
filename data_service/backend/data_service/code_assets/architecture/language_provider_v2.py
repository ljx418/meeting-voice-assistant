"""V2.40 multi-language provider contract.

The module emits provider-backed facts only. It intentionally avoids claiming
full call graph, data flow, type inference, or runtime topology.
"""

from __future__ import annotations

import ast
import hashlib
import re
from pathlib import Path
from typing import Any

from data_service.mcp_common import now

from ..artifacts import architecture_dir, read_jsonl, write_jsonl


SCHEMA_VERSION = "v2.40_language_provider"
TS_JS_EXTENSIONS = {".js", ".jsx", ".ts", ".tsx", ".vue"}
IMPORT_RE = re.compile(r"^[^\S\n]*import[^\S\n]+(?:[^'\"]+[^\S\n]+from[^\S\n]+)?[\"']([^\"']+)[\"']", re.MULTILINE)
REQUIRE_RE = re.compile(r"require\([\"']([^\"']+)[\"']\)")
EXPORT_RE = re.compile(r"^[^\S\n]*export[^\S\n]+(?:default[^\S\n]+)?(?:(?:class|function|const|let|var|interface|type)[^\S\n]+)?([A-Za-z_$][A-Za-z0-9_$]*)", re.MULTILINE)


def build_language_provider_artifacts(
    *,
    workspace: Path,
    workspace_id: str,
    codebase_id: str,
    snapshot_id: str,
    root: Path,
    files: list[dict[str, Any]],
) -> dict[str, Any]:
    included = [item for item in files if item.get("included") and isinstance(item.get("path"), str)]
    provider_status: list[dict[str, Any]] = []
    symbol_facts: list[dict[str, Any]] = []
    reference_facts: list[dict[str, Any]] = []

    python_files = [item for item in included if str(item.get("path", "")).endswith(".py")]
    ts_js_files = [item for item in included if Path(str(item.get("path", ""))).suffix.lower() in TS_JS_EXTENSIONS]

    py_symbols, py_refs, py_warnings = _extract_python_facts(workspace_id, codebase_id, snapshot_id, root, python_files)
    symbol_facts.extend(py_symbols)
    reference_facts.extend(py_refs)
    provider_status.append(_provider_status(workspace_id, codebase_id, snapshot_id, "python", "ast", "accepted", file_count=len(python_files), fact_count=len(py_symbols) + len(py_refs), warnings=py_warnings))

    ts_symbols, ts_refs = _extract_ts_js_baseline(workspace_id, codebase_id, snapshot_id, root, ts_js_files)
    if ts_js_files:
        symbol_facts.extend(ts_symbols)
        reference_facts.extend(ts_refs)
        provider_status.append(_provider_status(workspace_id, codebase_id, snapshot_id, "typescript/javascript", "baseline_lexical", "accepted", file_count=len(ts_js_files), fact_count=len(ts_symbols) + len(ts_refs), warnings=[]))
    else:
        provider_status.append(_provider_status(workspace_id, codebase_id, snapshot_id, "typescript/javascript", "baseline_lexical", "unsupported_language", file_count=0, fact_count=0, warnings=[]))

    provider_status.append(_provider_status(workspace_id, codebase_id, snapshot_id, "multi", "tree_sitter", "provider_unavailable", file_count=0, fact_count=0, warnings=[], error={"code": "PROVIDER_UNAVAILABLE", "message": "tree-sitter provider is not configured.", "retryable": False}))
    provider_status.append(_provider_status(workspace_id, codebase_id, snapshot_id, "multi", "lsp", "provider_unavailable", file_count=0, fact_count=0, warnings=[], error={"code": "PROVIDER_UNAVAILABLE", "message": "LSP provider is not configured.", "retryable": False}))

    symbol_facts = _dedupe(symbol_facts, "fact_id")
    reference_facts = _dedupe(reference_facts, "fact_id")
    write_jsonl(language_provider_status_path(workspace, codebase_id), provider_status)
    write_jsonl(symbol_facts_path(workspace, codebase_id), symbol_facts)
    write_jsonl(reference_facts_path(workspace, codebase_id), reference_facts)

    return {
        "schema_version": SCHEMA_VERSION,
        "workspace_id": workspace_id,
        "codebase_id": codebase_id,
        "snapshot_id": snapshot_id,
        "provider_status": provider_status,
        "symbol_facts": symbol_facts,
        "reference_facts": reference_facts,
        "summary": {
            "provider_count": len(provider_status),
            "accepted_provider_count": sum(1 for item in provider_status if item["status"] == "accepted"),
            "symbol_fact_count": len(symbol_facts),
            "reference_fact_count": len(reference_facts),
            "provider_unavailable_count": sum(1 for item in provider_status if item["status"] == "provider_unavailable"),
        },
        "artifact_refs": language_provider_artifact_refs(codebase_id),
        "created_at": now(),
    }


def read_language_provider_artifacts(workspace: Path, codebase_id: str) -> dict[str, Any]:
    provider_status = read_jsonl(language_provider_status_path(workspace, codebase_id))
    symbol_facts = read_jsonl(symbol_facts_path(workspace, codebase_id))
    reference_facts = read_jsonl(reference_facts_path(workspace, codebase_id))
    if not provider_status:
        raise FileNotFoundError("ARCHITECTURE_LANGUAGE_PROVIDERS_NOT_BUILT")
    snapshot_id = ""
    for collection in (provider_status, symbol_facts, reference_facts):
        if collection:
            snapshot_id = str(collection[0].get("snapshot_id") or "")
            break
    return {
        "schema_version": SCHEMA_VERSION,
        "codebase_id": codebase_id,
        "snapshot_id": snapshot_id,
        "provider_status": provider_status,
        "symbol_facts": symbol_facts,
        "reference_facts": reference_facts,
        "summary": {
            "provider_count": len(provider_status),
            "accepted_provider_count": sum(1 for item in provider_status if item.get("status") == "accepted"),
            "symbol_fact_count": len(symbol_facts),
            "reference_fact_count": len(reference_facts),
            "provider_unavailable_count": sum(1 for item in provider_status if item.get("status") == "provider_unavailable"),
        },
        "artifact_refs": language_provider_artifact_refs(codebase_id),
    }


def public_language_provider_payload(payload: dict[str, Any], *, limit: int = 50) -> dict[str, Any]:
    symbol_facts = list(payload.get("symbol_facts") or [])
    reference_facts = list(payload.get("reference_facts") or [])
    return {
        "schema_version": payload.get("schema_version", SCHEMA_VERSION),
        "workspace_id": payload.get("workspace_id"),
        "codebase_id": payload.get("codebase_id"),
        "snapshot_id": payload.get("snapshot_id"),
        "provider_status": list(payload.get("provider_status") or []),
        "summary": payload.get("summary", {}),
        "symbol_facts": {
            "total": len(symbol_facts),
            "sample": symbol_facts[:limit],
            "truncated": len(symbol_facts) > limit,
        },
        "reference_facts": {
            "total": len(reference_facts),
            "sample": reference_facts[:limit],
            "truncated": len(reference_facts) > limit,
        },
        "artifact_refs": payload.get("artifact_refs") or language_provider_artifact_refs(str(payload.get("codebase_id") or "")),
    }


def language_provider_artifact_refs(codebase_id: str) -> list[dict[str, str]]:
    return [
        {"type": "language_provider_status", "artifact_ref": f"architecture-v2-40://{codebase_id}/language_provider_status.jsonl"},
        {"type": "symbol_facts", "artifact_ref": f"architecture-v2-40://{codebase_id}/symbol_facts.jsonl"},
        {"type": "reference_facts", "artifact_ref": f"architecture-v2-40://{codebase_id}/reference_facts.jsonl"},
    ]


def language_provider_status_path(workspace: Path, codebase_id: str) -> Path:
    return _v240_dir(workspace, codebase_id) / "language_provider_status.jsonl"


def symbol_facts_path(workspace: Path, codebase_id: str) -> Path:
    return _v240_dir(workspace, codebase_id) / "symbol_facts.jsonl"


def reference_facts_path(workspace: Path, codebase_id: str) -> Path:
    return _v240_dir(workspace, codebase_id) / "reference_facts.jsonl"


def _v240_dir(workspace: Path, codebase_id: str) -> Path:
    return architecture_dir(workspace, codebase_id) / "v2_40"


def _extract_python_facts(workspace_id: str, codebase_id: str, snapshot_id: str, root: Path, files: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    symbols: list[dict[str, Any]] = []
    refs: list[dict[str, Any]] = []
    warnings: list[dict[str, Any]] = []
    for item in files:
        rel = str(item["path"])
        text = _read_text(root / rel)
        if text is None:
            continue
        try:
            tree = ast.parse(text)
        except SyntaxError as exc:
            warnings.append({"code": "PYTHON_SYNTAX_ERROR", "path": rel, "line": exc.lineno or 1})
            continue
        module_name = rel[:-3].replace("/", ".")
        symbols.append(_symbol(workspace_id, codebase_id, snapshot_id, rel, "module", module_name, [1, max(1, len(text.splitlines()))], "ast", 1.0))
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                symbols.append(_symbol(workspace_id, codebase_id, snapshot_id, rel, "function", f"{module_name}.{node.name}", _line_range(node), "ast", 1.0))
            elif isinstance(node, ast.ClassDef):
                symbols.append(_symbol(workspace_id, codebase_id, snapshot_id, rel, "class", f"{module_name}.{node.name}", _line_range(node), "ast", 1.0))
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    refs.append(_reference(workspace_id, codebase_id, snapshot_id, rel, "import", alias.name, [node.lineno, node.lineno], "ast", 1.0))
            elif isinstance(node, ast.ImportFrom):
                target = ".".join(part for part in [node.module or "", ",".join(alias.name for alias in node.names)] if part)
                refs.append(_reference(workspace_id, codebase_id, snapshot_id, rel, "import", target, [node.lineno, node.lineno], "ast", 1.0))
    return symbols, refs, warnings


def _extract_ts_js_baseline(workspace_id: str, codebase_id: str, snapshot_id: str, root: Path, files: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    symbols: list[dict[str, Any]] = []
    refs: list[dict[str, Any]] = []
    for item in files:
        rel = str(item["path"])
        text = _read_text(root / rel)
        if text is None:
            continue
        language = _language_for(rel)
        for match in EXPORT_RE.finditer(text):
            exported = match.group(1)
            if exported:
                line = _line_of(text, match.start(1))
                symbols.append(_symbol(workspace_id, codebase_id, snapshot_id, rel, "export", exported, [line, line], "baseline_lexical", 0.72, language=language, needs_review=True))
        imports: dict[str, int] = {}
        for regex in (IMPORT_RE, REQUIRE_RE):
            for match in regex.finditer(text):
                imported = match.group(1)
                imports.setdefault(imported, match.start(1))
        for imported, first_index in sorted(imports.items()):
            line = _line_of(text, first_index)
            refs.append(_reference(workspace_id, codebase_id, snapshot_id, rel, "import", imported, [line, line], "baseline_lexical", 0.78, language=language, needs_review=True))
    return symbols, refs


def _symbol(workspace_id: str, codebase_id: str, snapshot_id: str, path: str, kind: str, qualified_name: str, line_range: list[int], provider: str, confidence: float, *, language: str = "python", needs_review: bool = False) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "artifact_type": "symbol_fact",
        "fact_id": _fact_id("symbol", codebase_id, path, kind, qualified_name, line_range, provider),
        "workspace_id": workspace_id,
        "codebase_id": codebase_id,
        "snapshot_id": snapshot_id,
        "kind": kind,
        "language": language,
        "qualified_name": qualified_name,
        "path": path,
        "line_range": line_range,
        "provider": provider,
        "confidence": confidence,
        "needs_review": needs_review,
        "evidence_refs": [{"type": "file_line", "path": path, "line_range": line_range}],
    }


def _reference(workspace_id: str, codebase_id: str, snapshot_id: str, path: str, kind: str, target: str, line_range: list[int], provider: str, confidence: float, *, language: str = "python", needs_review: bool = False) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "artifact_type": "reference_fact",
        "fact_id": _fact_id("reference", codebase_id, path, kind, target, line_range, provider),
        "workspace_id": workspace_id,
        "codebase_id": codebase_id,
        "snapshot_id": snapshot_id,
        "kind": kind,
        "language": language,
        "target": target,
        "path": path,
        "line_range": line_range,
        "provider": provider,
        "confidence": confidence,
        "needs_review": needs_review,
        "evidence_refs": [{"type": "file_line", "path": path, "line_range": line_range}],
    }


def _provider_status(workspace_id: str, codebase_id: str, snapshot_id: str, language: str, provider: str, status: str, *, file_count: int, fact_count: int, warnings: list[dict[str, Any]], error: dict[str, Any] | None = None) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "artifact_type": "language_provider_status",
        "workspace_id": workspace_id,
        "codebase_id": codebase_id,
        "snapshot_id": snapshot_id,
        "language": language,
        "provider": provider,
        "status": status,
        "file_count": file_count,
        "fact_count": fact_count,
        "warnings": warnings,
        "error": error,
        "created_at": now(),
    }


def _read_text(path: Path) -> str | None:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None


def _line_range(node: ast.AST) -> list[int]:
    start = int(getattr(node, "lineno", 1) or 1)
    end = int(getattr(node, "end_lineno", start) or start)
    return [start, max(start, end)]


def _line_of(text: str, index: int) -> int:
    if index < 0:
        return 1
    return text.count("\n", 0, index) + 1


def _language_for(path: str) -> str:
    suffix = Path(path).suffix.lower()
    if suffix in {".ts", ".tsx", ".vue"}:
        return "typescript"
    return "javascript"


def _fact_id(*parts: Any) -> str:
    raw = "::".join(str(part) for part in parts)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:24]


def _dedupe(items: list[dict[str, Any]], key: str) -> list[dict[str, Any]]:
    seen: set[str] = set()
    out: list[dict[str, Any]] = []
    for item in items:
        value = str(item.get(key) or "")
        if not value or value in seen:
            continue
        seen.add(value)
        out.append(item)
    return out

"""Python symbol index artifacts for V2 codebase assets."""

from __future__ import annotations

import ast
import hashlib
from pathlib import Path
from typing import Any

from data_service.mcp_common import now, read_json, write_json

from .artifacts import (
    imports_path,
    read_jsonl,
    snapshot_files_path,
    symbol_summary_path,
    symbols_path,
    write_jsonl,
)
from .registry import CodebaseRegistry
from .snapshot import CodebaseSnapshotService


SYMBOL_SCHEMA_VERSION = "v2.0"
PYTHON_EXTENSION = ".py"
GOLDEN_SYMBOLS = {
    "backend.data_service.code_assets.inventory.CodebaseInventoryService",
    "backend.data_service.cli_code.run_code_command",
    "backend.app.api.v1.code_assets.build_codebase_inventory",
    "backend.data_service.mcp_code_tools.handle_code_tool",
}
GOLDEN_IMPORT = (
    "backend.data_service.mcp_code_tools",
    "backend.data_service.code_assets.inventory",
)


class CodebaseSymbolIndexService:
    def __init__(self, workspace: Path, *, workspace_id: str) -> None:
        self.workspace = workspace
        self.workspace_id = workspace_id
        self.registry = CodebaseRegistry(workspace, workspace_id=workspace_id)
        self.snapshots = CodebaseSnapshotService(workspace, workspace_id=workspace_id)

    def build_symbol_index(self, codebase_id: str, *, snapshot_id: str | None = None) -> dict[str, Any]:
        asset = self.registry.describe(codebase_id)
        if asset.status != "active":
            raise ValueError("CODEBASE_NOT_ACTIVE")
        resolved_snapshot_id = snapshot_id or self._latest_snapshot_id(codebase_id)
        self.snapshots.read_snapshot(codebase_id, resolved_snapshot_id)
        files = read_jsonl(snapshot_files_path(self.workspace, codebase_id, resolved_snapshot_id))
        root = Path(asset.root_path).expanduser().resolve()
        python_files = [row for row in files if row.get("included") and str(row.get("path") or "").endswith(PYTHON_EXTENSION)]

        symbols: list[dict[str, Any]] = []
        imports: list[dict[str, Any]] = []
        warnings: list[dict[str, Any]] = []
        parsed_file_count = 0
        for record in python_files:
            rel = str(record["path"])
            path = root / rel
            text = _read_text(path)
            if text is None:
                warnings.append(_warning(rel, "READ_FAILED", "Unable to read Python file"))
                continue
            module = _module_name(rel)
            module_symbol = _symbol(
                self.workspace_id,
                codebase_id,
                resolved_snapshot_id,
                kind="module",
                name=module.rsplit(".", 1)[-1],
                qualified_name=module,
                module=module,
                path=rel,
                line_range=[1, max(1, len(text.splitlines()))],
                signature="",
                docstring=None,
                decorators=[],
                visibility="public",
                parent_symbol_id=None,
            )
            symbols.append(module_symbol)
            try:
                tree = ast.parse(text)
            except SyntaxError as exc:
                warnings.append(_warning(rel, "SYNTAX_ERROR", str(exc), line=exc.lineno))
                continue
            parsed_file_count += 1
            extracted_symbols, extracted_imports = _extract_from_tree(
                tree,
                workspace_id=self.workspace_id,
                codebase_id=codebase_id,
                snapshot_id=resolved_snapshot_id,
                module=module,
                path=rel,
            )
            symbols.extend(extracted_symbols)
            imports.extend(extracted_imports)

        symbols = _dedupe_symbols(symbols)
        imports = _dedupe_imports(imports)
        summary = _build_summary(
            self.workspace_id,
            codebase_id,
            resolved_snapshot_id,
            symbols,
            imports,
            python_file_count=len(python_files),
            parsed_file_count=parsed_file_count,
            warnings=warnings,
        )
        refs = symbol_artifact_refs(codebase_id, resolved_snapshot_id)
        summary["artifact_refs"] = refs

        write_jsonl(symbols_path(self.workspace, codebase_id, resolved_snapshot_id), symbols)
        write_jsonl(imports_path(self.workspace, codebase_id, resolved_snapshot_id), imports)
        write_json(symbol_summary_path(self.workspace, codebase_id, resolved_snapshot_id), summary)
        return {"summary": summary, "symbols": symbols, "imports": imports}

    def read_symbol_index(self, codebase_id: str, *, snapshot_id: str | None = None) -> dict[str, Any]:
        resolved_snapshot_id = snapshot_id or self._latest_snapshot_id(codebase_id)
        self.registry.describe(codebase_id)
        summary = read_json(symbol_summary_path(self.workspace, codebase_id, resolved_snapshot_id), None)
        if not summary:
            raise FileNotFoundError("SYMBOL_INDEX_NOT_FOUND")
        return {
            "summary": summary,
            "symbols": read_jsonl(symbols_path(self.workspace, codebase_id, resolved_snapshot_id)),
            "imports": read_jsonl(imports_path(self.workspace, codebase_id, resolved_snapshot_id)),
        }

    def read_symbols(
        self,
        codebase_id: str,
        *,
        snapshot_id: str | None = None,
        kind: str | None = None,
        query: str | None = None,
        limit: int = 50,
    ) -> list[dict[str, Any]]:
        items = list(self.read_symbol_index(codebase_id, snapshot_id=snapshot_id)["symbols"])
        if kind:
            items = [item for item in items if item.get("kind") == kind]
        if query:
            needle = query.lower()
            items = [
                item
                for item in items
                if needle in str(item.get("qualified_name") or "").lower()
                or needle in str(item.get("name") or "").lower()
                or needle in str(item.get("signature") or "").lower()
            ]
        return items[: max(1, min(int(limit or 50), 200))]

    def read_imports(self, codebase_id: str, *, snapshot_id: str | None = None) -> list[dict[str, Any]]:
        return list(self.read_symbol_index(codebase_id, snapshot_id=snapshot_id)["imports"])

    def read_symbol(self, codebase_id: str, symbol_id: str, *, snapshot_id: str | None = None) -> dict[str, Any]:
        for symbol in self.read_symbol_index(codebase_id, snapshot_id=snapshot_id)["symbols"]:
            if symbol.get("symbol_id") == symbol_id:
                return symbol
        raise FileNotFoundError("SYMBOL_NOT_FOUND")

    def _latest_snapshot_id(self, codebase_id: str) -> str:
        snapshots = self.snapshots.list_snapshots(codebase_id, limit=1)
        if not snapshots:
            raise FileNotFoundError("SNAPSHOT_NOT_FOUND")
        return str(snapshots[0]["snapshot_id"])


def symbol_artifact_refs(codebase_id: str, snapshot_id: str) -> list[dict[str, str]]:
    return [
        {"type": "symbols", "artifact_ref": f"symbols://{codebase_id}/{snapshot_id}"},
        {"type": "imports", "artifact_ref": f"imports://{codebase_id}/{snapshot_id}"},
        {"type": "symbol_summary", "artifact_ref": f"symbol-summary://{codebase_id}/{snapshot_id}"},
    ]


def public_symbol_index_payload(index: dict[str, Any]) -> dict[str, Any]:
    summary = index["summary"]
    return {
        "schema_version": summary.get("schema_version"),
        "workspace_id": summary.get("workspace_id"),
        "codebase_id": summary.get("codebase_id"),
        "snapshot_id": summary.get("snapshot_id"),
        "summary": summary,
        "symbols": [public_symbol_payload(item) for item in index["symbols"]],
        "imports": [public_import_payload(item) for item in index["imports"]],
    }


def public_symbol_payload(symbol: dict[str, Any]) -> dict[str, Any]:
    payload = dict(symbol)
    payload["source_file"] = payload.pop("path", None)
    return payload


def public_import_payload(item: dict[str, Any]) -> dict[str, Any]:
    payload = dict(item)
    payload["source_file"] = payload.pop("path", None)
    return payload


def _extract_from_tree(
    tree: ast.AST,
    *,
    workspace_id: str,
    codebase_id: str,
    snapshot_id: str,
    module: str,
    path: str,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    symbols: list[dict[str, Any]] = []
    imports: list[dict[str, Any]] = []
    parents: list[tuple[str, str, str | None]] = []

    def visit_body(nodes: list[ast.stmt]) -> None:
        for node in nodes:
            if isinstance(node, ast.ClassDef):
                qualified_name = _qualname(module, parents, node.name)
                symbol = _symbol(
                    workspace_id,
                    codebase_id,
                    snapshot_id,
                    kind="class",
                    name=node.name,
                    qualified_name=qualified_name,
                    module=module,
                    path=path,
                    line_range=_line_range(node),
                    signature=node.name,
                    docstring=ast.get_docstring(node),
                    decorators=_decorators(node.decorator_list),
                    visibility=_visibility(node.name),
                    parent_symbol_id=parents[-1][2] if parents else None,
                )
                symbols.append(symbol)
                parents.append(("class", node.name, symbol["symbol_id"]))
                visit_body(list(node.body))
                parents.pop()
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                kind = "method" if parents and parents[-1][0] == "class" else "function"
                qualified_name = _qualname(module, parents, node.name)
                symbol = _symbol(
                    workspace_id,
                    codebase_id,
                    snapshot_id,
                    kind=kind,
                    name=node.name,
                    qualified_name=qualified_name,
                    module=module,
                    path=path,
                    line_range=_line_range(node),
                    signature=_signature(node),
                    docstring=ast.get_docstring(node),
                    decorators=_decorators(node.decorator_list),
                    visibility=_visibility(node.name),
                    parent_symbol_id=parents[-1][2] if parents else None,
                )
                symbols.append(symbol)
                parents.append(("function", node.name, symbol["symbol_id"]))
                visit_body(list(node.body))
                parents.pop()
            elif isinstance(node, ast.Import):
                imports.extend(_imports_from_import(node, workspace_id, codebase_id, snapshot_id, module, path))
            elif isinstance(node, ast.ImportFrom):
                imports.extend(_imports_from_import_from(node, workspace_id, codebase_id, snapshot_id, module, path))

    visit_body(list(getattr(tree, "body", [])))
    return symbols, imports


def _symbol(
    workspace_id: str,
    codebase_id: str,
    snapshot_id: str,
    *,
    kind: str,
    name: str,
    qualified_name: str,
    module: str,
    path: str,
    line_range: list[int],
    signature: str,
    docstring: str | None,
    decorators: list[str],
    visibility: str,
    parent_symbol_id: str | None,
) -> dict[str, Any]:
    return {
        "schema_version": SYMBOL_SCHEMA_VERSION,
        "workspace_id": workspace_id,
        "codebase_id": codebase_id,
        "snapshot_id": snapshot_id,
        "symbol_id": f"py:{kind}:{qualified_name}",
        "kind": kind,
        "name": name,
        "qualified_name": qualified_name,
        "module": module,
        "path": path,
        "line_range": line_range,
        "signature": signature,
        "docstring": docstring,
        "decorators": decorators,
        "visibility": visibility,
        "parent_symbol_id": parent_symbol_id,
        "collision_resolved": False,
        "extractor": "python_ast",
        "confidence": 1.0,
    }


def _imports_from_import(
    node: ast.Import,
    workspace_id: str,
    codebase_id: str,
    snapshot_id: str,
    module: str,
    path: str,
) -> list[dict[str, Any]]:
    rows = []
    for alias in node.names:
        rows.append(
            _import_row(
                workspace_id,
                codebase_id,
                snapshot_id,
                from_module=module,
                to_module=alias.name,
                import_type="import",
                name=alias.name,
                alias=alias.asname,
                path=path,
                line_range=_line_range(node),
            )
        )
    return rows


def _imports_from_import_from(
    node: ast.ImportFrom,
    workspace_id: str,
    codebase_id: str,
    snapshot_id: str,
    module: str,
    path: str,
) -> list[dict[str, Any]]:
    rows = []
    import_type = "relative_import" if node.level else "from_import"
    base = _resolve_from_import_module(module, node)
    for alias in node.names:
        to_module = base.rstrip(".")
        rows.append(
            _import_row(
                workspace_id,
                codebase_id,
                snapshot_id,
                from_module=module,
                to_module=to_module,
                import_type=import_type,
                name=alias.name,
                alias=alias.asname,
                path=path,
                line_range=_line_range(node),
            )
        )
    return rows


def _import_row(
    workspace_id: str,
    codebase_id: str,
    snapshot_id: str,
    *,
    from_module: str,
    to_module: str,
    import_type: str,
    name: str,
    alias: str | None,
    path: str,
    line_range: list[int],
) -> dict[str, Any]:
    raw_id = f"{from_module}:{to_module}:{name}:{alias or ''}:{line_range[0]}"
    digest = hashlib.sha256(raw_id.encode("utf-8")).hexdigest()[:12]
    return {
        "schema_version": SYMBOL_SCHEMA_VERSION,
        "workspace_id": workspace_id,
        "codebase_id": codebase_id,
        "snapshot_id": snapshot_id,
        "import_id": f"pyimport:{digest}",
        "from_module": from_module,
        "to_module": to_module,
        "import_type": import_type,
        "name": name,
        "alias": alias,
        "path": path,
        "line_range": line_range,
        "extractor": "python_ast",
        "confidence": 1.0,
    }


def _build_summary(
    workspace_id: str,
    codebase_id: str,
    snapshot_id: str,
    symbols: list[dict[str, Any]],
    imports: list[dict[str, Any]],
    *,
    python_file_count: int,
    parsed_file_count: int,
    warnings: list[dict[str, Any]],
) -> dict[str, Any]:
    symbols_by_kind: dict[str, int] = {}
    for symbol in symbols:
        kind = str(symbol.get("kind") or "unknown")
        symbols_by_kind[kind] = symbols_by_kind.get(kind, 0) + 1
    qualified_names = {str(symbol.get("qualified_name")) for symbol in symbols}
    import_pairs = {(str(item.get("from_module")), str(item.get("to_module"))) for item in imports}
    return {
        "schema_version": SYMBOL_SCHEMA_VERSION,
        "workspace_id": workspace_id,
        "codebase_id": codebase_id,
        "snapshot_id": snapshot_id,
        "created_at": now(),
        "symbol_count": len(symbols),
        "import_count": len(imports),
        "symbols_by_kind": dict(sorted(symbols_by_kind.items())),
        "python_file_count": python_file_count,
        "parsed_file_count": parsed_file_count,
        "syntax_error_count": sum(1 for warning in warnings if warning.get("code") == "SYNTAX_ERROR"),
        "warnings": warnings[:50],
        "golden_checks": {
            "symbols": _check_set(GOLDEN_SYMBOLS, qualified_names),
            "imports": {"passed": GOLDEN_IMPORT in import_pairs, "missing": [] if GOLDEN_IMPORT in import_pairs else [list(GOLDEN_IMPORT)]},
        },
    }


def _dedupe_symbols(symbols: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: dict[str, int] = {}
    result = []
    for symbol in symbols:
        symbol_id = str(symbol["symbol_id"])
        if symbol_id in seen:
            seen[symbol_id] += 1
            digest = hashlib.sha256(f"{symbol['path']}:{symbol['line_range']}:{seen[symbol_id]}".encode("utf-8")).hexdigest()[:8]
            symbol = dict(symbol)
            symbol["symbol_id"] = f"{symbol_id}:{digest}"
            symbol["collision_resolved"] = True
        else:
            seen[symbol_id] = 0
        result.append(symbol)
    return sorted(result, key=lambda item: (str(item.get("path")), int((item.get("line_range") or [0])[0]), str(item.get("symbol_id"))))


def _dedupe_imports(imports: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_id = {str(item["import_id"]): item for item in imports}
    return [by_id[key] for key in sorted(by_id)]


def _module_name(rel: str) -> str:
    path = Path(rel)
    without_suffix = path.with_suffix("")
    parts = list(without_suffix.parts)
    if parts and parts[-1] == "__init__":
        parts = parts[:-1]
    return ".".join(parts)


def _resolve_from_import_module(current_module: str, node: ast.ImportFrom) -> str:
    if not node.level:
        return str(node.module or "")
    package_parts = current_module.split(".")[:-1]
    ascend = max(int(node.level or 0) - 1, 0)
    if ascend:
        package_parts = package_parts[:-ascend]
    module_parts = str(node.module or "").split(".") if node.module else []
    return ".".join([*package_parts, *[part for part in module_parts if part]])


def _qualname(module: str, parents: list[tuple[str, str, str | None]], name: str) -> str:
    segments = [module]
    for kind, parent_name, _symbol_id in parents:
        if kind == "function":
            segments.extend([parent_name, "<locals>"])
        else:
            segments.append(parent_name)
    segments.append(name)
    return ".".join(segments)


def _signature(node: ast.FunctionDef | ast.AsyncFunctionDef) -> str:
    args = ast.unparse(node.args) if hasattr(ast, "unparse") else ""
    prefix = "async " if isinstance(node, ast.AsyncFunctionDef) else ""
    result = f"{prefix}{node.name}({args})"
    if node.returns is not None and hasattr(ast, "unparse"):
        result += f" -> {ast.unparse(node.returns)}"
    return result


def _decorators(decorators: list[ast.expr]) -> list[str]:
    return [_expr_name(item) for item in decorators if _expr_name(item)]


def _expr_name(node: ast.AST) -> str:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        base = _expr_name(node.value)
        return f"{base}.{node.attr}" if base else node.attr
    if isinstance(node, ast.Call):
        return _expr_name(node.func)
    if hasattr(ast, "unparse"):
        try:
            return ast.unparse(node)
        except Exception:
            return ""
    return ""


def _visibility(name: str) -> str:
    if name.startswith("__") and not name.endswith("__"):
        return "private"
    if name.startswith("_") and not (name.startswith("__") and name.endswith("__")):
        return "internal"
    return "public"


def _line_range(node: ast.AST) -> list[int]:
    start = int(getattr(node, "lineno", 1) or 1)
    end = int(getattr(node, "end_lineno", start) or start)
    return [start, max(start, end)]


def _warning(path: str, code: str, message: str, *, line: int | None = None) -> dict[str, Any]:
    return {"path": path, "code": code, "message": message, "line": line}


def _check_set(expected: set[str], actual: set[str]) -> dict[str, Any]:
    missing = sorted(expected - actual)
    return {"passed": not missing, "missing": missing}


def _read_text(path: Path) -> str | None:
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return None

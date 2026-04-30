"""LLMWiki CLI 工具"""
import argparse
import logging
import os
import shutil
import sqlite3
import sys
from pathlib import Path
from typing import List, Optional

from .config import LLMWikiConfig
from .engine import WikiEngine

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("llmwiki.cli")


def cmd_ingest(args) -> int:
    """导入文件或目录"""
    engine = WikiEngine(config=LLMWikiConfig.from_env())

    paths = args.paths if hasattr(args, "paths") else [args.path]
    result = engine.ingest(paths)

    print(f"\n=== Ingest Results ===")
    print(f"Success: {result['success']}")
    print(f"Failed: {result['failed']}")
    print(f"Pages created: {len(result['pages'])}")
    print(f"Sources processed: {len(result.get('sources', []))}")

    if result["pages"]:
        print(f"\nPage slugs:")
        for slug in result["pages"]:
            print(f"  - {slug}")

    if result["errors"]:
        print(f"\nErrors ({len(result['errors'])}):")
        for err in result["errors"]:
            print(f"  - {err['file']}: {err['error']}")

    return 0 if result["failed"] == 0 else 1


def cmd_search(args) -> int:
    """搜索 wiki"""
    engine = WikiEngine(config=LLMWikiConfig.from_env())

    result = engine.search(
        query=args.query,
        top_k=args.top_k,
        scope=args.scope,
    )

    print(f"\n=== Search Results for: {args.query} ===")
    print(f"Scope: {args.scope}, top_k: {args.top_k}")

    if result["pages"]:
        print(f"\n--- Pages ({len(result['pages'])}) ---")
        for i, page in enumerate(result["pages"], 1):
            print(f"\n{i}. {page['title']}")
            print(f"   Score: {page['score']:.3f}")
            print(f"   Slug: {page['result_id']}")
            print(f"   Snippet: {page['snippet'][:150]}...")

    if result["passages"]:
        print(f"\n--- Passages ({len(result['passages'])}) ---")
        for i, passage in enumerate(result["passages"][:10], 1):
            print(f"\n{i}. {passage['title']}")
            print(f"   Score: {passage['score']:.3f}")
            print(f"   Snippet: {passage['snippet'][:200]}...")

    if not result["pages"] and not result["passages"]:
        print("\nNo results found.")

    return 0


def cmd_read_page(args) -> int:
    """读取页面"""
    engine = WikiEngine(config=LLMWikiConfig.from_env())

    result = engine.read_page(args.slug)

    if result["page"] is None:
        print(f"Page not found: {args.slug}")
        return 1

    page = result["page"]

    print(f"\n=== Page: {page['title']} ===")
    print(f"Slug: {page['slug']}")
    print(f"Kind: {page['kind']}")
    print(f"Summary: {page['summary'] or 'N/A'}")
    print(f"\n--- Body ---")
    print(page["body_md"])

    if result["sources"]:
        print(f"\n--- Sources ({len(result['sources'])}) ---")
        for src in result["sources"]:
            print(f"  - {src['title']} ({src['source_type']})")

    if result["citations"]:
        print(f"\n--- Citations ({len(result['citations'])}) ---")
        for cit in result["citations"]:
            print(f"  - [[{cit.get('slug', '?')}]]")

    if result.get("backlinks"):
        print(f"\n--- Backlinks ({len(result['backlinks'])}) ---")
        for bl in result["backlinks"]:
            print(f"  - [{bl['slug']}] {bl['title']}")

    return 0


def cmd_summary(args) -> int:
    """读取当前 workspace summary"""
    config = LLMWikiConfig.from_env()
    if not config.summary_path.exists():
        print(f"Summary file not found: {config.summary_path}")
        return 1
    print(config.summary_path.read_text(encoding="utf-8"))
    return 0


def cmd_rebuild(args) -> int:
    """重建索引"""
    engine = WikiEngine(config=LLMWikiConfig.from_env())

    result = engine.rebuild(
        source_id=args.source_id,
        page_slug=args.page_slug,
        all=args.all,
    )

    print(f"\n=== Rebuild Results ===")
    print(f"Rebuilt: {result['rebuilt']}")

    if result["errors"]:
        print(f"\nErrors:")
        for err in result["errors"]:
            print(f"  - {err}")

    return 0 if not result["errors"] else 1


def cmd_list_pages(args) -> int:
    """列出所有页面"""
    engine = WikiEngine(config=LLMWikiConfig.from_env())

    pages = engine.list_pages(limit=args.limit)

    print(f"\n=== Pages ({len(pages)}) ===")
    if not pages:
        print("No pages found.")
        return 0

    for page in pages:
        updated = page.get("updated_at", "N/A")
        if updated and len(updated) > 10:
            updated = updated[:10]
        print(f"  [{page['kind']}] {page['title']} (slug: {page['slug']}, updated: {updated})")

    return 0


def cmd_doctor(args) -> int:
    """系统健康检查"""
    config = LLMWikiConfig.from_env()
    issues: list = []
    warnings: list = []

    print("\n=== LLMWiki Doctor ===\n")

    # 1. 工作空间
    print("[1/8] Checking workspace...")
    try:
        config.workspace_path.mkdir(parents=True, exist_ok=True)
        print(f"  Workspace: OK ({config.workspace_path})")
        config_file = LLMWikiConfig.find_workspace_config()
        if config_file:
            print(f"  Workspace config: {config_file}")
        else:
            print("  Workspace config: using current directory")
    except Exception as e:
        issues.append(f"Workspace: {e}")
        print(f"  Workspace: FAIL - {e}")

    # 2. SQLite / FTS5 可用性
    print("[2/8] Checking SQLite + FTS5...")
    try:
        conn = sqlite3.connect(":memory:")
        cursor = conn.cursor()
        cursor.execute("CREATE VIRTUAL TABLE t USING fts5(a)")
        cursor.execute("INSERT INTO t VALUES ('test')")
        cursor.execute("SELECT * FROM t WHERE t MATCH 'test'")
        conn.close()
        print("  SQLite + FTS5: OK")
    except Exception as e:
        issues.append(f"SQLite/FTS5: {e}")
        print(f"  SQLite + FTS5: FAIL - {e}")

    # 3. 可选依赖状态
    print("[3/8] Checking optional dependencies...")

    # pypdf
    try:
        import pypdf  # noqa: F401
        print("  pypdf: OK")
    except ImportError:
        warnings.append("pypdf not installed - PDF support disabled")
        print("  pypdf: not installed (optional)")

    # 4. vault 目录
    print("[4/8] Checking vault directory...")
    vault_path = config.vault_path
    if vault_path.exists():
        print(f"  Vault directory: OK ({vault_path})")
    else:
        try:
            vault_path.mkdir(parents=True, exist_ok=True)
            print(f"  Vault directory: Created ({vault_path})")
        except Exception as e:
            issues.append(f"Cannot create vault directory: {e}")
            print(f"  Vault directory: FAIL - {e}")

    # 5. .ppt 转换器可用性
    print("[5/8] Checking .ppt converter (soffice)...")
    soffice = shutil.which("soffice")
    if soffice:
        print(f"  soffice: OK ({soffice})")
    else:
        warnings.append("soffice not found - .ppt to .pptx conversion disabled")
        print("  soffice: not found (optional, for .ppt support)")

    # 6. 数据库可写性
    print("[6/8] Checking database writability...")
    db_path = config.db_path
    try:
        db_path.parent.mkdir(parents=True, exist_ok=True)
        test_conn = sqlite3.connect(str(db_path), timeout=5)
        cursor = test_conn.cursor()
        cursor.execute("SELECT count(*) FROM sqlite_master")
        test_conn.close()
        print(f"  Database: OK ({db_path})")
    except Exception as e:
        issues.append(f"Database not writable: {e}")
        print(f"  Database: FAIL - {e}")

    # 7. 提取器注册检查
    print("[7/8] Checking extractors...")
    try:
        from .extractors import EXTRACTORS
        print(f"  Extractors registered: {len(EXTRACTORS)}")
        for name, cls in EXTRACTORS.items():
            print(f"    - {name}")
    except Exception as e:
        issues.append(f"Extractor registration: {e}")
        print(f"  Extractors: FAIL - {e}")

    print("[8/8] Checking LLM compiler configuration...")
    try:
        print(f"  Provider: {config.llm_provider}")
        print(f"  Model: {config.llm_model}")
        print(f"  Compile on ingest: {config.compile_on_ingest}")
        print(f"  Raw snapshot output: {config.vault_path}")
        print(f"  Readable docs output: {config.readable_docs_dir}")
        print(f"  Normalized output: {config.normalized_output_dir}")
        print(f"  Markdown output: {config.markdown_output_dir}")
        print(f"  Summary output: {config.summary_path}")
        if config.llm_provider == "null":
            print("  LLM API: disabled (local fallback mode)")
        elif not config.llm_api_base:
            warnings.append("LLM API base is not configured")
            print("  LLM API: missing base URL")
        elif not config.llm_api_key_env:
            warnings.append("LLM API key env var name is not configured")
            print("  LLM API key env: missing")
        elif not os.getenv(config.llm_api_key_env):
            warnings.append(f"LLM API key env var is unset: {config.llm_api_key_env}")
            print(f"  LLM API key env: unset ({config.llm_api_key_env})")
        else:
            print(f"  LLM API: configured ({config.llm_api_base})")
            print(f"  LLM API key env: {config.llm_api_key_env}")
    except Exception as e:
        issues.append(f"LLM configuration: {e}")
        print(f"  LLM compiler config: FAIL - {e}")

    # 总结
    print("\n=== Summary ===")
    if not issues and not warnings:
        print("All checks passed.")
        return 0
    if issues:
        print(f"Issues ({len(issues)}):")
        for issue in issues:
            print(f"  - {issue}")
    if warnings:
        print(f"Warnings ({len(warnings)}):")
        for warning in warnings:
            print(f"  - {warning}")

    return 0 if not issues else 1


def cmd_workspace(args) -> int:
    """查看或设置工作空间"""
    start_dir = Path.cwd()

    if args.reset:
        removed = LLMWikiConfig.clear_workspace(start_dir=start_dir)
        config = LLMWikiConfig.from_env()
        if removed:
            print(f"Workspace config removed: {removed}")
        else:
            print("No workspace config file found. Using current directory.")
        print(f"Active workspace: {config.workspace_path}")
        print(f"Database path: {config.db_path}")
        print(f"Vault path: {config.vault_path}")
        print(f"Readable docs path: {config.readable_docs_dir}")
        print(f"Normalized path: {config.normalized_output_dir}")
        print(f"Markdown path: {config.markdown_output_dir}")
        print(f"Summary path: {config.summary_path}")
        return 0

    if args.path:
        config_path = LLMWikiConfig.set_workspace(args.path, start_dir=start_dir)
        config = LLMWikiConfig.from_env()
        config.ensure_directories()
        print(f"Workspace updated: {config.workspace_path}")
        print(f"Workspace config: {config_path}")
        print(f"Database path: {config.db_path}")
        print(f"Vault path: {config.vault_path}")
        print(f"Readable docs path: {config.readable_docs_dir}")
        print(f"Normalized path: {config.normalized_output_dir}")
        print(f"Markdown path: {config.markdown_output_dir}")
        print(f"Summary path: {config.summary_path}")
        return 0

    config = LLMWikiConfig.from_env()
    config_file = LLMWikiConfig.find_workspace_config(start_dir)
    print(f"Active workspace: {config.workspace_path}")
    if config_file:
        print(f"Workspace config: {config_file}")
    else:
        print("Workspace config: using current directory")
    print(f"Database path: {config.db_path}")
    print(f"Vault path: {config.vault_path}")
    print(f"Readable docs path: {config.readable_docs_dir}")
    print(f"Normalized path: {config.normalized_output_dir}")
    print(f"Markdown path: {config.markdown_output_dir}")
    print(f"Summary path: {config.summary_path}")
    return 0


def main(argv: Optional[List[str]] = None) -> int:
    """CLI 主入口"""
    parser = argparse.ArgumentParser(
        prog="llmwiki",
        description="LLMWiki - Local Knowledge Module",
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # ingest
    ingest_parser = subparsers.add_parser("ingest", help="Ingest files or directories")
    ingest_parser.add_argument(
        "paths",
        nargs="+",
        help="File or directory paths to ingest",
    )
    ingest_parser.set_defaults(func=cmd_ingest)

    # search
    search_parser = subparsers.add_parser("search", help="Search the wiki")
    search_parser.add_argument("query", help="Search query")
    search_parser.add_argument("--top-k", type=int, default=8, help="Number of results (default: 8)")
    search_parser.add_argument(
        "--scope",
        choices=["pages", "passages", "hybrid"],
        default="hybrid",
        help="Search scope (default: hybrid)",
    )
    search_parser.set_defaults(func=cmd_search)

    # read-page
    read_parser = subparsers.add_parser("read-page", help="Read a page")
    read_parser.add_argument("slug", help="Page slug")
    read_parser.set_defaults(func=cmd_read_page)

    # summary
    summary_parser = subparsers.add_parser("summary", help="Read the current workspace summary")
    summary_parser.set_defaults(func=cmd_summary)

    # rebuild
    rebuild_parser = subparsers.add_parser("rebuild", help="Rebuild index")
    rebuild_parser.add_argument("--source-id", help="Rebuild only pages from this source")
    rebuild_parser.add_argument("--page-slug", help="Rebuild only this page")
    rebuild_parser.add_argument("--all", action="store_true", help="Rebuild all FTS indexes")
    rebuild_parser.set_defaults(func=cmd_rebuild)

    # list-pages
    list_parser = subparsers.add_parser("list-pages", help="List all pages")
    list_parser.add_argument("--limit", type=int, default=100, help="Max pages to show (default: 100)")
    list_parser.set_defaults(func=cmd_list_pages)

    # doctor
    doctor_parser = subparsers.add_parser("doctor", help="Run system health checks")
    doctor_parser.set_defaults(func=cmd_doctor)

    # workspace
    workspace_parser = subparsers.add_parser("workspace", help="Show or set the active workspace")
    workspace_parser.add_argument(
        "path",
        nargs="?",
        help="Persist workspace to this path; defaults to showing the current workspace",
    )
    workspace_parser.add_argument(
        "--reset",
        action="store_true",
        help="Remove the persisted workspace override and fall back to the current directory",
    )
    workspace_parser.set_defaults(func=cmd_workspace)

    args = parser.parse_args(argv)

    if args.command is None:
        parser.print_help()
        return 1

    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())

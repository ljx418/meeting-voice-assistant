"""LLMWiki MCP Server - stdio transport

MCP server for LLMWiki that exposes wiki capabilities via the Model Context Protocol.
This server provides resources and tools for interacting with the wiki system.

Usage:
    python -m llmwiki.mcp_stdio

Configuration in .mcp.json:
{
    "mcpServers": {
        "llmwiki": {
            "command": "python",
            "args": ["-m", "llmwiki.mcp_stdio"]
        }
    }
}
"""
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

# MCP imports
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    Resource,
    TextResourceContents,
    Tool,
    TextContent,
)

# LLMWiki imports
from .config import LLMWikiConfig
from .dotenv_support import load_llmwiki_dotenv
from .engine import WikiEngine
from .storage import Storage
from .search.fts import FTS5Search


# Server instance
server = Server("llmwiki")
load_llmwiki_dotenv()

# Global state (initialized in main)
_config: Optional[LLMWikiConfig] = None
_storage: Optional[Storage] = None
_fts: Optional[FTS5Search] = None
_engine: Optional[WikiEngine] = None


def _get_storage() -> Storage:
    """Get or initialize storage."""
    global _storage
    if _storage is None:
        config = _config or LLMWikiConfig.from_env()
        _storage = Storage(config)
        _storage.init_db()
    return _storage


def _get_fts() -> FTS5Search:
    """Get or initialize FTS search."""
    global _fts
    if _fts is None:
        config = _config or LLMWikiConfig.from_env()
        _fts = FTS5Search(config.db_path)
    return _fts


def _get_engine() -> WikiEngine:
    """Get or initialize engine."""
    global _engine
    if _engine is None:
        config = _config or LLMWikiConfig.from_env()
        _engine = WikiEngine(config)
    return _engine


# ========== Resources ==========

@server.list_resources()
async def list_resources() -> List[Resource]:
    """List available resources."""
    resources = [
        # Index resource
        Resource(
            uri="llmwiki://index",
            name="Wiki Index",
            description="System statistics including source count, page count, and recent ingest info",
            mimeType="application/json",
        ),
    ]

    # Add page resources from storage
    try:
        storage = _get_storage()
        pages = storage.list_pages(limit=100)
        for page in pages:
            resources.append(Resource(
                uri=f"llmwiki://page/{page.slug}",
                name=f"Page: {page.title or page.slug}",
                description=f"Wiki page: {page.slug} ({page.kind.value if hasattr(page.kind, 'value') else page.kind})",
                mimeType="text/markdown",
            ))
    except Exception as e:
        print(f"[llmwiki MCP] Error listing pages for resources: {e}", file=sys.stderr)

    # Add source resources
    try:
        storage = _get_storage()
        sources = storage.list_sources(limit=50)
        for source in sources:
            resources.append(Resource(
                uri=f"llmwiki://source/{source.source_id}",
                name=f"Source: {source.title or source.source_id}",
                description=f"Source file: {source.original_path or 'unknown'} ({source.source_type.value if hasattr(source.source_type, 'value') else source.source_type})",
                mimeType="application/json",
            ))
    except Exception as e:
        print(f"[llmwiki MCP] Error listing sources for resources: {e}", file=sys.stderr)

    # Add conversation resources
    try:
        storage = _get_storage()
        with storage.get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT conversation_id, title FROM conversations ORDER BY created_at DESC LIMIT 50")
            for row in cursor.fetchall():
                resources.append(Resource(
                    uri=f"llmwiki://conversation/{row['conversation_id']}",
                    name=f"Conversation: {row['title'] or row['conversation_id'][:8]}",
                    description=f"Conversation: {row['conversation_id']}",
                    mimeType="application/json",
                ))
    except Exception as e:
        print(f"[llmwiki MCP] Error listing conversations for resources: {e}", file=sys.stderr)

    return resources


@server.read_resource()
async def read_resource(uri: str) -> TextResourceContents:
    """Read a resource by URI."""
    if uri == "llmwiki://index":
        return _read_index()
    elif uri.startswith("llmwiki://page/"):
        slug = uri[len("llmwiki://page/"):]
        return _read_page(slug)
    elif uri.startswith("llmwiki://source/"):
        source_id = uri[len("llmwiki://source/"):]
        return _read_source(source_id)
    elif uri.startswith("llmwiki://conversation/"):
        conversation_id = uri[len("llmwiki://conversation/"):]
        return _read_conversation(conversation_id)
    else:
        raise ValueError(f"Unknown resource URI: {uri}")


def _read_index() -> TextResourceContents:
    """Read the index resource."""
    storage = _get_storage()

    # Get stats
    source_count = 0
    page_count = 0
    recent_ingest = None

    try:
        sources = storage.list_sources(limit=1000)
        source_count = len(sources)
    except Exception as e:
        print(f"[llmwiki MCP] Error counting sources: {e}", file=sys.stderr)

    try:
        pages = storage.list_pages(limit=1000)
        page_count = len(pages)
    except Exception as e:
        print(f"[llmwiki MCP] Error counting pages: {e}", file=sys.stderr)

    try:
        with storage.get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT run_id, source_ids, status, started_at, completed_at,
                       pages_created, passages_created, error_message
                FROM ingest_runs
                ORDER BY started_at DESC
                LIMIT 1
            """)
            row = cursor.fetchone()
            if row:
                recent_ingest = {
                    "run_id": row["run_id"],
                    "source_ids": json.loads(row["source_ids"]),
                    "status": row["status"],
                    "started_at": row["started_at"],
                    "completed_at": row["completed_at"],
                    "pages_created": row["pages_created"],
                    "passages_created": row["passages_created"],
                    "error_message": row["error_message"],
                }
    except Exception as e:
        print(f"[llmwiki MCP] Error getting recent ingest: {e}", file=sys.stderr)

    data = {
        "role": {
            "system": "LLMWiki",
            "purpose": "Collect, normalize, and compile scattered files and chat-like materials into readable local wiki artifacts.",
            "complements": "GraphRAG can act as the heavy-knowledge substrate for dense, structured assets; LLMWiki remains the lighter collection and compilation layer.",
        },
        "layers": {
            "row": "External raw sources managed outside llmwiki; tracked via row manifest and copied snapshots.",
            "llmwiki": "Workspace artifacts including raw snapshots, readable rewrites, normalized outputs, pages, and state DB.",
            "summary": "Current workspace status summary file for operators and agents.",
        },
        "paths": {
            "workspace": str((_config or LLMWikiConfig.from_env()).workspace_path),
            "raw": str((_config or LLMWikiConfig.from_env()).vault_path),
            "readable": str((_config or LLMWikiConfig.from_env()).readable_docs_dir),
            "normalized": str((_config or LLMWikiConfig.from_env()).normalized_output_dir),
            "pages": str((_config or LLMWikiConfig.from_env()).markdown_output_dir),
            "summary": str((_config or LLMWikiConfig.from_env()).summary_path),
            "db": str((_config or LLMWikiConfig.from_env()).db_path),
        },
        "source_count": source_count,
        "page_count": page_count,
        "compiler": {
            "provider": (_config or LLMWikiConfig.from_env()).llm_provider,
            "model": (_config or LLMWikiConfig.from_env()).llm_model,
            "markdown_output_dir": str((_config or LLMWikiConfig.from_env()).markdown_output_dir),
        },
        "recent_ingest": recent_ingest,
    }

    return TextResourceContents(
        uri="llmwiki://index",
        mimeType="application/json",
        text=json.dumps(data, indent=2),
    )


def _read_page(slug: str) -> TextResourceContents:
    """Read a wiki page resource."""
    storage = _get_storage()
    page = storage.get_page(slug)

    if page is None:
        return TextResourceContents(
            uri=f"llmwiki://page/{slug}",
            mimeType="text/plain",
            text=f"Page not found: {slug}",
        )

    # Get metadata
    kind_str = page.kind.value if hasattr(page.kind, 'value') else str(page.kind)
    updated_str = page.updated_at.isoformat() if page.updated_at else None

    # Build metadata header
    meta = {
        "slug": page.slug,
        "title": page.title,
        "kind": kind_str,
        "summary": page.summary,
        "version": page.version,
        "updated_at": updated_str,
        "source_ids": page.source_ids,
        "link_slugs": page.link_slugs,
        "markdown_path": getattr(page, "markdown_path", None),
        "compile_status": getattr(page, "compile_status", None),
        "compiled_by_model": getattr(page, "compiled_by_model", None),
        "meta": page.meta_json,
    }

    page_body = page.body_md
    if getattr(page, "markdown_path", None):
        try:
            page_body = Path(page.markdown_path).read_text(encoding="utf-8")
        except OSError:
            pass

    # Return as markdown with YAML frontmatter
    content = f"""---
slug: {page.slug}
title: {page.title}
kind: {kind_str}
summary: {page.summary or ''}
version: {page.version}
updated_at: {updated_str or ''}
source_ids: {json.dumps(page.source_ids)}
link_slugs: {json.dumps(page.link_slugs)}
markdown_path: {getattr(page, "markdown_path", "") or ''}
compile_status: {getattr(page, "compile_status", "") or ''}
compiled_by_model: {getattr(page, "compiled_by_model", "") or ''}
---

{page_body}
"""

    return TextResourceContents(
        uri=f"llmwiki://page/{slug}",
        mimeType="text/markdown",
        text=content,
    )


def _read_source(source_id: str) -> TextResourceContents:
    """Read a source resource."""
    storage = _get_storage()
    source = storage.get_source(source_id)

    if source is None:
        return TextResourceContents(
            uri=f"llmwiki://source/{source_id}",
            mimeType="text/plain",
            text=f"Source not found: {source_id}",
        )

    # Get passages for this source
    passages = []
    try:
        with storage.get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT passage_id, text, locator, order_index
                FROM passages
                WHERE source_id = ?
                ORDER BY order_index
            """, (source_id,))
            for row in cursor.fetchall():
                passages.append({
                    "passage_id": row["passage_id"],
                    "text": row["text"],
                    "locator": json.loads(row["locator"]) if row["locator"] else {},
                    "order_index": row["order_index"],
                })
    except Exception as e:
        print(f"[llmwiki MCP] Error getting passages for source: {e}", file=sys.stderr)

    source_type_str = source.source_type.value if hasattr(source.source_type, 'value') else str(source.source_type)
    status_str = source.status.value if hasattr(source.status, 'value') else str(source.status)

    data = {
        "source_id": source.source_id,
        "source_type": source_type_str,
        "authority": source.authority,
        "original_path": source.original_path,
        "stored_path": source.stored_path,
        "sha256": source.sha256,
        "title": source.title,
        "mime": source.mime,
        "created_at": source.created_at.isoformat() if source.created_at else None,
        "updated_at": source.updated_at.isoformat() if source.updated_at else None,
        "extractor_name": source.extractor_name,
        "extractor_version": source.extractor_version,
        "status": status_str,
        "meta": source.meta_json,
        "passages": passages,
        "passage_count": len(passages),
    }

    return TextResourceContents(
        uri=f"llmwiki://source/{source_id}",
        mimeType="application/json",
        text=json.dumps(data, indent=2),
    )


def _read_conversation(conversation_id: str) -> TextResourceContents:
    """Read a conversation resource."""
    storage = _get_storage()

    conversation = None
    turns: List[Dict[str, Any]] = []

    try:
        with storage.get_conn() as conn:
            cursor = conn.cursor()

            # Get conversation
            cursor.execute("""
                SELECT conversation_id, source_id, title, participants, created_at, updated_at, meta_json
                FROM conversations
                WHERE conversation_id = ?
            """, (conversation_id,))
            row = cursor.fetchone()

            if row:
                conversation = {
                    "conversation_id": row["conversation_id"],
                    "source_id": row["source_id"],
                    "title": row["title"],
                    "participants": json.loads(row["participants"]) if row["participants"] else [],
                    "created_at": row["created_at"],
                    "updated_at": row["updated_at"],
                    "meta": json.loads(row["meta_json"]) if row["meta_json"] else {},
                }

            # Get turns
            if conversation:
                cursor.execute("""
                    SELECT turn_id, role, content_text, timestamp, order_index, meta_json
                    FROM turns
                    WHERE conversation_id = ?
                    ORDER BY order_index
                """, (conversation_id,))
                for row in cursor.fetchall():
                    turns.append({
                        "turn_id": row["turn_id"],
                        "role": row["role"],
                        "content_text": row["content_text"],
                        "timestamp": row["timestamp"],
                        "order_index": row["order_index"],
                        "meta": json.loads(row["meta_json"]) if row["meta_json"] else {},
                    })
    except Exception as e:
        print(f"[llmwiki MCP] Error reading conversation: {e}", file=sys.stderr)

    if conversation is None:
        return TextResourceContents(
            uri=f"llmwiki://conversation/{conversation_id}",
            mimeType="text/plain",
            text=f"Conversation not found: {conversation_id}",
        )

    data = {
        "conversation": conversation,
        "turns": turns,
        "turn_count": len(turns),
    }

    return TextResourceContents(
        uri=f"llmwiki://conversation/{conversation_id}",
        mimeType="application/json",
        text=json.dumps(data, indent=2),
    )


# ========== Tools ==========

@server.list_tools()
async def list_tools() -> List[Tool]:
    """List available tools."""
    return [
        Tool(
            name="wiki_search",
            description="Search the wiki for pages and passages",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query text",
                    },
                    "top_k": {
                        "type": "integer",
                        "description": "Maximum number of results to return (default: 10)",
                        "default": 10,
                    },
                },
                "required": ["query"],
            },
        ),
        Tool(
            name="wiki_read_page",
            description="Read a wiki page by slug",
            inputSchema={
                "type": "object",
                "properties": {
                    "slug": {
                        "type": "string",
                        "description": "Page slug",
                    },
                },
                "required": ["slug"],
            },
        ),
        Tool(
            name="wiki_ingest",
            description="Ingest files into the wiki",
            inputSchema={
                "type": "object",
                "properties": {
                    "paths": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of file paths to ingest",
                    },
                },
                "required": ["paths"],
            },
        ),
        Tool(
            name="wiki_rebuild",
            description="Rebuild wiki pages",
            inputSchema={
                "type": "object",
                "properties": {
                    "source_id": {
                        "type": "string",
                        "description": "Source ID to rebuild pages for",
                    },
                    "page_slug": {
                        "type": "string",
                        "description": "Specific page slug to rebuild",
                    },
                    "all": {
                        "type": "boolean",
                        "description": "Rebuild all pages",
                        "default": False,
                    },
                },
            },
        ),
        Tool(
            name="wiki_list_pages",
            description="List wiki pages",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of pages to return",
                        "default": 100,
                    },
                    "offset": {
                        "type": "integer",
                        "description": "Offset for pagination",
                        "default": 0,
                    },
                },
            },
        ),
        Tool(
            name="wiki_list_recent",
            description="List recently updated pages",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of pages to return",
                        "default": 20,
                    },
                },
            },
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> TextContent:
    """Call a tool by name with arguments."""
    try:
        if name == "wiki_search":
            return await _wiki_search(
                query=arguments["query"],
                top_k=arguments.get("top_k", 10),
            )
        elif name == "wiki_read_page":
            return await _wiki_read_page(slug=arguments["slug"])
        elif name == "wiki_ingest":
            return await _wiki_ingest(paths=arguments["paths"])
        elif name == "wiki_rebuild":
            return await _wiki_rebuild(
                source_id=arguments.get("source_id"),
                page_slug=arguments.get("page_slug"),
                all_flag=arguments.get("all", False),
            )
        elif name == "wiki_list_pages":
            return await _wiki_list_pages(
                limit=arguments.get("limit", 100),
                offset=arguments.get("offset", 0),
            )
        elif name == "wiki_list_recent":
            return await _wiki_list_recent(limit=arguments.get("limit", 20))
        else:
            raise ValueError(f"Unknown tool: {name}")
    except Exception as e:
        print(f"[llmwiki MCP] Tool error: {name}: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        return TextContent(type="text", text=json.dumps({"error": str(e)}, indent=2))


async def _wiki_search(query: str, top_k: int = 10) -> TextContent:
    """Search the wiki."""
    engine = _get_engine()
    output = engine.search(query=query, top_k=top_k, scope="hybrid")
    return TextContent(type="text", text=json.dumps(output, indent=2))


async def _wiki_read_page(slug: str) -> TextContent:
    """Read a wiki page."""
    engine = _get_engine()
    result = engine.read_page(slug)
    page = result["page"]
    if page is None:
        return TextContent(type="text", text=json.dumps({"error": f"Page not found: {slug}"}, indent=2))
    return TextContent(type="text", text=json.dumps(result, indent=2))


async def _wiki_ingest(paths: List[str]) -> TextContent:
    """Ingest files into the wiki."""
    engine = _get_engine()
    output = engine.ingest(paths)
    return TextContent(type="text", text=json.dumps(output, indent=2))


async def _wiki_rebuild(
    source_id: Optional[str] = None,
    page_slug: Optional[str] = None,
    all_flag: bool = False,
) -> TextContent:
    """Rebuild wiki pages."""
    engine = _get_engine()
    output = engine.rebuild(source_id=source_id, page_slug=page_slug, all=all_flag)
    return TextContent(type="text", text=json.dumps(output, indent=2))


async def _wiki_list_pages(limit: int = 100, offset: int = 0) -> TextContent:
    """List wiki pages."""
    storage = _get_storage()
    pages = storage.list_pages(limit=limit, offset=offset)

    output = {
        "pages": [
            {
                "slug": p.slug,
                "title": p.title,
                "kind": p.kind.value if hasattr(p.kind, 'value') else str(p.kind),
                "summary": p.summary,
                "version": p.version,
                "updated_at": p.updated_at.isoformat() if p.updated_at else None,
                "source_count": len(p.source_ids),
            }
            for p in pages
        ],
        "count": len(pages),
        "limit": limit,
        "offset": offset,
    }

    return TextContent(type="text", text=json.dumps(output, indent=2))


async def _wiki_list_recent(limit: int = 20) -> TextContent:
    """List recently updated pages."""
    storage = _get_storage()
    pages = storage.list_pages(limit=limit)

    # Sort by updated_at (already sorted DESC in list_pages)
    output = {
        "pages": [
            {
                "slug": p.slug,
                "title": p.title,
                "kind": p.kind.value if hasattr(p.kind, 'value') else str(p.kind),
                "updated_at": p.updated_at.isoformat() if p.updated_at else None,
            }
            for p in pages[:limit]
        ],
        "count": min(len(pages), limit),
    }

    return TextContent(type="text", text=json.dumps(output, indent=2))


# ========== Main ==========

async def main():
    """Main entry point for the MCP server."""
    global _config

    # Initialize config from environment
    _config = LLMWikiConfig.from_env()
    _config.ensure_directories()

    print(f"[llmwiki MCP] Starting server with db_path={_config.db_path}", file=sys.stderr)

    # Initialize storage and FTS
    try:
        _get_storage()
        _get_fts()
        print(f"[llmwiki MCP] Storage and FTS initialized", file=sys.stderr)
    except Exception as e:
        print(f"[llmwiki MCP] Warning: Could not initialize storage: {e}", file=sys.stderr)

    # Run server with stdio
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())

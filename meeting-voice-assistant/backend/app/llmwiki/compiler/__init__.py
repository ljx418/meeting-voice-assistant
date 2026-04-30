"""LLMWiki 编译器模块

负责从原始文档生成 Wiki 页面，包括:
- classifier: 主题分类器
- page_builder: 页面构建器
- merger: 页面合并器
- linker: 链接器
"""

from .classifier import (
    classify,
    classify_by_content,
    classify_by_filename,
    detect_language,
    extract_keywords,
    generate_slug,
    normalize_title,
)
from .linker import AliasResolver, LinkBuilder, Linker
from .llm_compiler import CompileResult, WikiCompiler
from .merger import (
    detect_duplicate_pages,
    merge_multiple_pages,
    merge_wiki_pages,
)
from .page_builder import (
    build_conversation_note,
    build_index,
    build_source_note,
    build_topic,
)

__all__ = [
    # classifier
    "classify",
    "classify_by_filename",
    "classify_by_content",
    "extract_keywords",
    "generate_slug",
    "normalize_title",
    "detect_language",
    # page_builder
    "build_source_note",
    "build_topic",
    "build_conversation_note",
    "build_index",
    # merger
    "merge_wiki_pages",
    "merge_multiple_pages",
    "detect_duplicate_pages",
    # linker
    "AliasResolver",
    "LinkBuilder",
    "Linker",
    "WikiCompiler",
    "CompileResult",
]

"""LLMWiki 搜索模块

包含:
- fts: FTS5 全文搜索
- ranker: 结果排序
- cjk: 中文分词支持
"""

from .cjk import extract_cjk_terms, extract_cjk_terms_for_query, is_cjk_char
from .fts import FTS5Search, SearchResult, SearchResponse
from .ranker import (
    ResultRanker,
    SearchResultMerger,
    RankedResult,
    compute_final_score,
)

__all__ = [
    # CJK
    "extract_cjk_terms",
    "extract_cjk_terms_for_query",
    "is_cjk_char",
    # FTS
    "FTS5Search",
    "SearchResult",
    "SearchResponse",
    # Ranker
    "ResultRanker",
    "SearchResultMerger",
    "RankedResult",
    "compute_final_score",
]

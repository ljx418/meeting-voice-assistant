"""LLMWiki 搜索层 - 结果排序"""
import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set

from .fts import SearchResult, SearchResponse


# 来源权重 - 主文档来源优先于聊天来源
SOURCE_WEIGHTS = {
    "file": 1.0,       # 文件来源最高
    "url": 0.9,        # URL 来源次之
    "text": 0.8,       # 文本输入
    "conversation": 0.6,  # 聊天记录最低
}


@dataclass
class RankedResult:
    """排序后的结果"""
    result_id: str
    result_type: str  # "page" 或 "passage"
    title: str
    snippet: str
    score: float
    page_score: float = 0.0
    passage_score: float = 0.0
    title_match: bool = False
    exact_topic_match: bool = False
    source_weight: float = 1.0
    meta: Dict[str, Any] = field(default_factory=dict)


class ResultRanker:
    """搜索结果排序器"""

    def __init__(
        self,
        title_boost: float = 3.0,
        exact_match_boost: float = 2.0,
        source_weights: Optional[Dict[str, float]] = None,
    ):
        """初始化排序器

        Args:
            title_boost: 标题命中加权倍数
            exact_match_boost: 精确 topic 命中加权倍数
            source_weights: 来源权重映射
        """
        self.title_boost = title_boost
        self.exact_match_boost = exact_match_boost
        self.source_weights = source_weights or SOURCE_WEIGHTS

    def rank_hybrid_results(
        self,
        response: SearchResponse,
        topic_page_slugs: Optional[Set[str]] = None,
        source_types: Optional[Dict[str, str]] = None,
    ) -> List[RankedResult]:
        """混合排序 page 和 passage 结果

        Args:
            response: 搜索响应
            topic_page_slugs: 主题页面 slug 集合（用于精确匹配加权）
            source_types: source_id -> source_type 映射

        Returns:
            排序后的结果列表
        """
        if topic_page_slugs is None:
            topic_page_slugs = set()

        all_results: List[RankedResult] = []

        # 处理 page 结果
        for page in response.pages:
            ranked = self._rank_page_result(
                page,
                topic_page_slugs,
                source_types or {},
            )
            all_results.append(ranked)

        # 处理 passage 结果
        for passage in response.passages:
            ranked = self._rank_passage_result(
                passage,
                topic_page_slugs,
                source_types or {},
            )
            all_results.append(ranked)

        # 按综合分数排序
        all_results.sort(key=lambda x: x.score, reverse=True)

        return all_results

    def _rank_page_result(
        self,
        result: SearchResult,
        topic_page_slugs: Set[str],
        source_types: Dict[str, str],
    ) -> RankedResult:
        """对页面结果排序

        Args:
            result: 搜索结果
            topic_page_slugs: 主题页面 slug 集合
            source_types: 来源类型映射

        Returns:
            排序后的结果
        """
        base_score = result.score

        # 获取来源权重
        source_id = result.meta.get("source_id", "")
        source_type = source_types.get(source_id, "file")
        source_weight = self.source_weights.get(source_type, 1.0)

        # 检查是否为 topic 页面
        is_topic_page = result.result_id in topic_page_slugs

        # 检查标题匹配
        title_lower = result.title.lower()
        query_lower = result.meta.get("query", "").lower()
        title_match = bool(query_lower and query_lower in title_lower)

        # 计算精确 topic 匹配
        exact_topic_match = is_topic_page and title_match

        # 综合分数计算
        score = base_score * source_weight

        if title_match:
            score *= self.title_boost

        if exact_topic_match:
            score *= self.exact_match_boost

        return RankedResult(
            result_id=result.result_id,
            result_type=result.result_type,
            title=result.title,
            snippet=result.snippet,
            score=score,
            page_score=base_score,
            title_match=title_match,
            exact_topic_match=exact_topic_match,
            source_weight=source_weight,
            meta=result.meta,
        )

    def _rank_passage_result(
        self,
        result: SearchResult,
        topic_page_slugs: Set[str],
        source_types: Dict[str, str],
    ) -> RankedResult:
        """对段落结果排序

        Args:
            result: 搜索结果
            topic_page_slugs: 主题页面 slug 集合
            source_types: 来源类型映射

        Returns:
            排序后的结果
        """
        base_score = result.score

        # 获取来源权重
        source_id = result.meta.get("source_id", "")
        source_type = source_types.get(source_id, "file")
        source_weight = self.source_weights.get(source_type, 1.0)

        # passage 本身权重较低
        passage_weight = 0.5

        # 检查是否为 topic 相关
        passage_id = result.meta.get("passage_id", "")
        is_from_topic = any(
            slug in result.meta.get("source_id", "")
            for slug in topic_page_slugs
        )

        # 综合分数计算
        score = base_score * source_weight * passage_weight

        if is_from_topic:
            score *= 1.5  # 来自 topic 的 passage 加权

        return RankedResult(
            result_id=result.result_id,
            result_type=result.result_type,
            title=result.title,
            snippet=result.snippet,
            score=score,
            passage_score=base_score,
            source_weight=source_weight,
            meta=result.meta,
        )

    def rerank_by_diversity(
        self,
        results: List[RankedResult],
        max_per_type: int = 3,
    ) -> List[RankedResult]:
        """多样性重排 - 限制每种类型的结果数量

        Args:
            results: 排序后的结果
            max_per_type: 每种类型最多结果数

        Returns:
            多样性排序后的结果
        """
        type_counts: Dict[str, int] = {}
        diversified: List[RankedResult] = []

        for result in results:
            rtype = result.result_type
            count = type_counts.get(rtype, 0)

            if count < max_per_type:
                diversified.append(result)
                type_counts[rtype] = count + 1

        return diversified


class SearchResultMerger:
    """搜索结果合并器"""

    def merge_responses(
        self,
        responses: List[SearchResponse],
        max_results: int = 20,
    ) -> SearchResponse:
        """合并多个搜索响应

        Args:
            responses: 搜索响应列表
            max_results: 最大结果数

        Returns:
            合并后的响应
        """
        all_pages: Dict[str, SearchResult] = {}
        all_passages: Dict[str, SearchResult] = {}

        for response in responses:
            for page in response.pages:
                if page.result_id not in all_pages:
                    all_pages[page.result_id] = page
                elif page.score > all_pages[page.result_id].score:
                    all_pages[page.result_id] = page

            for passage in response.passages:
                if passage.result_id not in all_passages:
                    all_passages[passage.result_id] = passage
                elif passage.score > all_passages[passage.result_id].score:
                    all_passages[passage.result_id] = passage

        # 按分数排序
        sorted_pages = sorted(
            all_pages.values(),
            key=lambda x: x.score,
            reverse=True,
        )[:max_results]

        sorted_passages = sorted(
            all_passages.values(),
            key=lambda x: x.score,
            reverse=True,
        )[:max_results * 2]

        return SearchResponse(
            query=responses[0].query if responses else "",
            pages=sorted_pages,
            passages=sorted_passages,
            total_pages=len(sorted_pages),
            total_passages=len(sorted_passages),
        )

    def deduplicate_results(
        self,
        results: List[RankedResult],
    ) -> List[RankedResult]:
        """去重结果

        基于 result_id 和高度相似的内容去重

        Args:
            results: 结果列表

        Returns:
            去重后的结果
        """
        seen_ids: Set[str] = set()
        seen_snippets: Set[str] = set()
        deduplicated: List[RankedResult] = []

        for result in results:
            # 按 ID 去重
            if result.result_id in seen_ids:
                continue

            # 按 snippet 近似去重（取前100字符）
            snippet_sig = result.snippet[:100].lower()
            if snippet_sig in seen_snippets:
                continue

            seen_ids.add(result.result_id)
            seen_snippets.add(snippet_sig)
            deduplicated.append(result)

        return deduplicated


def compute_final_score(
    page_score: float,
    passage_score: float,
    title_match_boost: float = 3.0,
    exact_topic_boost: float = 2.0,
    source_weight: float = 1.0,
    is_topic_page: bool = False,
    title_match: bool = False,
) -> float:
    """计算最终综合分数

    Args:
        page_score: 页面命中分数
        passage_score: 段落命中分数
        title_match_boost: 标题匹配加权
        exact_topic_boost: 精确 topic 匹配加权
        source_weight: 来源权重
        is_topic_page: 是否为 topic 页面
        title_match: 是否标题匹配

    Returns:
        综合分数
    """
    # 基础分数取 page 和 passage 中的较高值
    base_score = max(page_score, passage_score * 0.5)

    # 应用来源权重
    score = base_score * source_weight

    # 标题匹配加权
    if title_match:
        score *= title_match_boost

    # 精确 topic 匹配
    if is_topic_page and title_match:
        score *= exact_topic_boost

    return score

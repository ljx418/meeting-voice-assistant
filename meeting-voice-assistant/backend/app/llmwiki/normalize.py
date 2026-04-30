"""标准化与分段模块"""
import re
from typing import List, Optional

from .models import NormalizedSection, Passage, generate_id
from .search.cjk import extract_cjk_terms


def estimate_tokens(text: str) -> int:
    """
    估算 token 数量
    简单估算：中文按字符，英文按单词
    """
    # 中文字符
    cjk_chars = len(re.findall(r'[\u4e00-\u9fff\u3400-\u4dbf\uf900-\ufaff]', text))
    # 英文单词
    english_words = len(re.findall(r'[a-zA-Z]+', text))
    # 其他字符
    other = len(text) - cjk_chars - english_words

    # 估算：中文每个字符约 1.5 token，英文每个单词约 1.3 token
    return int(cjk_chars * 1.5 + english_words * 1.3 + other * 0.5)


def split_into_passages(
    section: NormalizedSection,
    max_chars: int = 1200,
    min_chars: int = 800,
    overlap_chars: int = 120,
    cjk_mode: str = "bigram"
) -> List[Passage]:
    """
    将 NormalizedSection 切分为 Passage

    Args:
        section: 标准化章节
        max_chars: 最大字符数
        min_chars: 最小字符数
        overlap_chars: 重叠字符数
        cjk_mode: CJK n-gram 模式 ("bigram" | "trigram")

    Returns:
        Passage 列表
    """
    text = section.text
    if not text or len(text) < min_chars:
        # 文本太短，直接作为单个 passage
        return [_create_passage(section, text, 0, cjk_mode)]

    passages = []
    start = 0
    order_index = 0

    while start < len(text):
        end = start + max_chars

        # 如果不是最后一段，需要在重叠区域内寻找合适的断点
        if end < len(text):
            # 寻找断点：句号、换行、段落分隔
            breakpoint = _find_breakpoint(text, start, end, overlap_chars)
            if breakpoint is None:
                # 没有找到合适断点，强制在 max_chars 处切断
                breakpoint = end
        else:
            breakpoint = len(text)

        # 提取段落文本
        passage_text = text[start:breakpoint].strip()
        if passage_text:
            passage = _create_passage(section, passage_text, order_index, cjk_mode)
            passages.append(passage)
            order_index += 1

        # 移动起始位置（考虑重叠）
        if breakpoint >= len(text):
            break
        start = breakpoint - overlap_chars

        # 避免死循环
        if start <= (breakpoint - overlap_chars) and order_index > 0:
            start = breakpoint

    return passages


def _create_passage(
    section: NormalizedSection,
    text: str,
    order_index: int,
    cjk_mode: str
) -> Passage:
    """创建 Passage 对象"""
    cjk_terms = extract_cjk_terms(text, mode=cjk_mode)
    token_count = estimate_tokens(text)

    # 继承并更新 locator
    locator = section.locator.copy()
    if "kind" in locator:
        # 添加 passage 级别的位置信息
        locator["passage_order"] = order_index

    return Passage(
        passage_id=generate_id(),
        source_id=section.source_id,
        section_id=section.section_id,
        text=text,
        cjk_terms=cjk_terms,
        token_count_est=token_count,
        locator=locator,
        order_index=order_index
    )


def _find_breakpoint(text: str, start: int, end: int, overlap_chars: int) -> Optional[int]:
    """
    在 [end - overlap_chars, end) 范围内寻找合适的断点

    优先断点顺序：
    1. 句号 + 换行（句尾）
    2. 句号（常规断句）
    3. 换行
    4. 段落标记（双换行）
    5. 分号、冒号（次级断句）
    """
    search_start = max(start, end - overlap_chars)
    search_region = text[search_start:end]

    # 1. 句号 + 换行
    match = re.search(r'。\s*\n', search_region)
    if match:
        return search_start + match.end()

    # 2. 句号
    match = re.search(r'。', search_region)
    if match:
        return search_start + match.end()

    # 3. 感叹号、问号
    match = re.search(r'[!?]', search_region)
    if match:
        return search_start + match.end()

    # 4. 换行
    match = re.search(r'\n', search_region)
    if match:
        return search_start + match.end()

    # 5. 分号、逗号（英文）
    match = re.search(r'[;,]', search_region)
    if match:
        return search_start + match.end()

    # 6. 冒号（中文冒号更常见）
    match = re.search(r'：', search_region)
    if match:
        return search_start + match.end()

    return None


def normalize_sections(
    sections: List[NormalizedSection],
    max_chars: int = 1200,
    min_chars: int = 800,
    overlap_chars: int = 120,
    cjk_mode: str = "bigram"
) -> List[Passage]:
    """
    批量标准化 sections 并切分为 passages

    Args:
        sections: NormalizedSection 列表
        max_chars: 最大字符数
        min_chars: 最小字符数
        overlap_chars: 重叠字符数
        cjk_mode: CJK n-gram 模式

    Returns:
        Passage 列表
    """
    all_passages = []

    for section in sections:
        passages = split_into_passages(
            section,
            max_chars=max_chars,
            min_chars=min_chars,
            overlap_chars=overlap_chars,
            cjk_mode=cjk_mode
        )
        all_passages.extend(passages)

    return all_passages

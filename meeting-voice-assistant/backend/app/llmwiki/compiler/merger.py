"""LLMWiki 编译器 - 页面合并器"""
from datetime import datetime
from typing import Dict, List, Optional, Set, Tuple

from ..models import PageKind, WikiPage


def merge_wiki_pages(
    existing: WikiPage,
    incoming: WikiPage,
    strategy: str = "append",
) -> WikiPage:
    """合并两个同名的 WikiPage

    增量 merge 策略：
    - append: 追加新内容到 body_md
    - replace: 完全替换
    - merge-body: 智能合并 body 内容

    Args:
        existing: 已存在的页面
        incoming: 新页面
        strategy: 合并策略

    Returns:
        合并后的 WikiPage
    """
    if strategy == "replace":
        return _merge_replace(existing, incoming)
    elif strategy == "merge-body":
        return _merge_body(existing, incoming)
    else:  # append
        return _merge_append(existing, incoming)


def _merge_replace(existing: WikiPage, incoming: WikiPage) -> WikiPage:
    """完全替换策略"""
    return WikiPage(
        slug=existing.slug,
        title=incoming.title or existing.title,
        kind=existing.kind,
        summary=incoming.summary or existing.summary,
        body_md=incoming.body_md,
        source_ids=_merge_source_ids(existing.source_ids, incoming.source_ids),
        link_slugs=_merge_link_slugs(existing.link_slugs, incoming.link_slugs),
        version=existing.version + 1,
        updated_at=datetime.utcnow(),
        meta_json=incoming.meta_json or existing.meta_json,
    )


def _merge_append(existing: WikiPage, incoming: WikiPage) -> WikiPage:
    """追加策略 - 将新内容追加到现有内容"""
    # 添加分隔符和内容
    separator = "\n\n---\n\n## Updated Content\n\n"
    new_body = existing.body_md + separator + incoming.body_md

    return WikiPage(
        slug=existing.slug,
        title=incoming.title or existing.title,
        kind=existing.kind,
        summary=incoming.summary or existing.summary or existing.summary,
        body_md=new_body,
        source_ids=_merge_source_ids(existing.source_ids, incoming.source_ids),
        link_slugs=_merge_link_slugs(existing.link_slugs, incoming.link_slugs),
        version=existing.version + 1,
        updated_at=datetime.utcnow(),
        meta_json=_merge_meta(existing.meta_json, incoming.meta_json),
    )


def _merge_body(existing: WikiPage, incoming: WikiPage) -> WikiPage:
    """智能合并 body - 保留现有结构，合并新内容"""
    existing_sections = _parse_markdown_sections(existing.body_md)
    incoming_sections = _parse_markdown_sections(incoming.body_md)

    # 合并相同标题的 section 内容
    merged_sections = _merge_sections(existing_sections, incoming_sections)

    # 重建 body
    body_md = _rebuild_markdown(merged_sections)

    return WikiPage(
        slug=existing.slug,
        title=incoming.title or existing.title,
        kind=existing.kind,
        summary=incoming.summary or existing.summary,
        body_md=body_md,
        source_ids=_merge_source_ids(existing.source_ids, incoming.source_ids),
        link_slugs=_merge_link_slugs(existing.link_slugs, incoming.link_slugs),
        version=existing.version + 1,
        updated_at=datetime.utcnow(),
        meta_json=_merge_meta(existing.meta_json, incoming.meta_json),
    )


def merge_multiple_pages(pages: List[WikiPage], primary_slug: str) -> WikiPage:
    """合并多个页面到一个主页面

    Args:
        pages: 要合并的页面列表
        primary_slug: 主页面 slug

    Returns:
        合并后的页面
    """
    if not pages:
        raise ValueError("No pages to merge")

    # 找到主页面
    primary = next((p for p in pages if p.slug == primary_slug), pages[0])
    others = [p for p in pages if p.slug != primary_slug]

    if not others:
        return primary

    # 合并所有来源
    all_source_ids = primary.source_ids.copy()
    all_link_slugs = set(primary.link_slugs)

    for page in others:
        all_source_ids.extend(page.source_ids)
        all_link_slugs.update(page.link_slugs)

    # 合并 meta
    merged_meta = primary.meta_json.copy()
    for page in others:
        merged_meta = _merge_meta(merged_meta, page.meta_json)

    # 合并 body
    body_parts = [primary.body_md]
    for page in others:
        body_parts.append(f"\n\n---\n\n## From: {page.title}\n\n{page.body_md}")

    return WikiPage(
        slug=primary.slug,
        title=primary.title,
        kind=primary.kind,
        summary=primary.summary or (others[0].summary if others else None),
        body_md="\n".join(body_parts),
        source_ids=list(set(all_source_ids)),
        link_slugs=list(all_link_slugs),
        version=primary.version + 1,
        updated_at=datetime.utcnow(),
        meta_json=merged_meta,
    )


def _merge_source_ids(existing: List[str], incoming: List[str]) -> List[str]:
    """合并 source_ids，去重"""
    combined = list(existing)
    for sid in incoming:
        if sid not in combined:
            combined.append(sid)
    return combined


def _merge_link_slugs(existing: List[str], incoming: List[str]) -> List[str]:
    """合并 link_slugs，去重"""
    combined = set(existing)
    combined.update(incoming)
    return list(combined)


def _merge_meta(existing: dict, incoming: dict) -> dict:
    """合并 meta_json"""
    merged = existing.copy()
    for key, value in (incoming or {}).items():
        if key not in merged:
            merged[key] = value
        elif isinstance(value, (int, float)) and isinstance(merged[key], (int, float)):
            # 数值型合并（相加）
            merged[key] = merged[key] + value
        elif isinstance(value, list) and isinstance(merged[key], list):
            # 列表合并
            merged[key] = merged[key] + value
        # 否则保留原值
    return merged


def _parse_markdown_sections(markdown: str) -> List[Dict[str, str]]:
    """解析 Markdown 为 section 列表

    Returns:
        [(level, title, content), ...]
        level: 1-6 表示标题级别
    """
    import re

    sections = []
    lines = markdown.split("\n")
    current_title = None
    current_level = 0
    current_content = []

    for line in lines:
        # 匹配标题
        match = re.match(r'^(#{1,6})\s+(.+)$', line)
        if match:
            # 保存之前的 section
            if current_title is not None:
                sections.append({
                    "level": current_level,
                    "title": current_title,
                    "content": "\n".join(current_content).strip(),
                })

            current_level = len(match.group(1))
            current_title = match.group(2)
            current_content = []
        else:
            current_content.append(line)

    # 保存最后一个 section
    if current_title is not None:
        sections.append({
            "level": current_level,
            "title": current_title,
            "content": "\n".join(current_content).strip(),
        })

    return sections


def _merge_sections(
    existing: List[Dict[str, str]],
    incoming: List[Dict[str, str]],
) -> List[Dict[str, str]]:
    """合并两个 section 列表"""
    # 按标题索引 existing sections
    existing_index = {s["title"]: s for s in existing}

    merged = list(existing)

    for inc_section in incoming:
        title = inc_section["title"]
        if title in existing_index:
            # 合并同名 section
            existing_idx = next(i for i, s in enumerate(merged) if s["title"] == title)
            existing_content = merged[existing_idx]["content"]
            merged[existing_idx]["content"] = f"{existing_content}\n\n---\n\n{inc_section['content']}"
        else:
            # 添加新 section
            merged.append(inc_section)

    return merged


def _rebuild_markdown(sections: List[Dict[str, str]]) -> str:
    """从 sections 重建 Markdown"""
    lines = []
    for section in sections:
        level = section["level"]
        title = section["title"]
        content = section["content"]

        lines.append(f"{'#' * level} {title}")
        if content:
            lines.append(content)
        lines.append("")

    return "\n".join(lines)


def detect_duplicate_pages(pages: List[WikiPage], threshold: float = 0.8) -> List[Tuple[str, str]]:
    """检测可能的重复页面

    Args:
        pages: 页面列表
        threshold: 相似度阈值 (0-1)

    Returns:
        [(slug1, slug2), ...] 可能的重复对
    """
    duplicates = []

    for i, page1 in enumerate(pages):
        for page2 in pages[i + 1:]:
            if _pages_similar(page1, page2, threshold):
                duplicates.append((page1.slug, page2.slug))

    return duplicates


def _pages_similar(page1: WikiPage, page2: WikiPage, threshold: float) -> bool:
    """判断两个页面是否相似"""
    # 1. 标题完全相同
    if page1.title == page2.title:
        return True

    # 2. slug 相似
    if _slug_similar(page1.slug, page2.slug):
        return True

    # 3. summary 相似度
    if page1.summary and page2.summary:
        similarity = _text_similarity(page1.summary, page2.summary)
        if similarity >= threshold:
            return True

    return False


def _slug_similar(slug1: str, slug2: str) -> bool:
    """判断 slug 是否相似"""
    import re

    # 移除常见前缀后缀
    def normalize(s):
        s = re.sub(r'^(source|topic|conversation|index)-?', '', s)
        s = re.sub(r'-?\d+$', '', s)
        return s.lower()

    return normalize(slug1) == normalize(slug2)


def _text_similarity(text1: str, text2: str) -> float:
    """计算文本相似度（简单 Jaccard）"""
    words1 = set(text1.lower().split())
    words2 = set(text2.lower().split())

    if not words1 or not words2:
        return 0.0

    intersection = words1 & words2
    union = words1 | words2

    return len(intersection) / len(union)

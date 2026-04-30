"""LLMWiki 编译器 - 页面构建器"""
import hashlib
from datetime import datetime
from typing import Any, Dict, List, Optional

from ..models import (
    Conversation,
    NormalizedSection,
    PageKind,
    Passage,
    SourceRecord,
    Turn,
    WikiPage,
)


def generate_id_from_text(text: str) -> str:
    """从文本生成短 ID"""
    return hashlib.md5(text.encode()).hexdigest()[:8]


def build_source_note(
    source: SourceRecord,
    sections: List[NormalizedSection],
    passages: List[Passage],
    summary: Optional[str] = None,
) -> WikiPage:
    """构建 source_note 页面

    source_note 包含:
    - 文件信息 (path, type, size, created)
    - 摘要 (LLM 生成或自动提取)
    - 章节结构 (heading outline)
    - 关键摘录 (key excerpts)

    Args:
        source: 源记录
        sections: 规范化章节列表
        passages: 段落列表
        summary: 摘要文本

    Returns:
        WikiPage 对象
    """
    # 生成 slug
    slug_base = source.title or source.original_path or "source"
    # 清理 slug
    slug = slug_base.lower().replace(" ", "-")
    slug = "".join(c if c.isalnum() or c in "-_" else "" for c in slug)
    slug = f"source-{slug[:50]}"

    # 构建章节结构
    chapter_structure = _build_chapter_structure(sections)

    # 提取关键摘录
    key_excerpts = _extract_key_excerpts(passages, max_excerpts=5)

    # 构建 body
    body_parts = []

    # 获取类型字符串（兼容 Enum 和普通字符串）
    source_type_str = source.source_type.value if hasattr(source.source_type, 'value') else str(source.source_type)

    # 文件信息
    body_parts.append("## File Information\n")
    body_parts.append(f"- **Path**: `{source.original_path or 'N/A'}`")
    body_parts.append(f"- **Type**: {source_type_str}")
    body_parts.append(f"- **MIME**: {source.mime or 'N/A'}")
    if source.stored_path:
        body_parts.append(f"- **Stored**: `{source.stored_path}`")
    if source.created_at:
        body_parts.append(f"- **Created**: {source.created_at.isoformat() if isinstance(source.created_at, datetime) else source.created_at}")
    body_parts.append("")

    # 摘要
    if summary:
        body_parts.append("## Summary\n")
        body_parts.append(summary)
        body_parts.append("")

    # 章节结构
    if chapter_structure:
        body_parts.append("## Structure\n")
        body_parts.append(chapter_structure)
        body_parts.append("")

    # 关键摘录
    if key_excerpts:
        body_parts.append("## Key Excerpts\n")
        for i, excerpt in enumerate(key_excerpts, 1):
            body_parts.append(f"{i}. > {excerpt}")
        body_parts.append("")

    body_md = "\n".join(body_parts)

    # 获取 kind 字符串
    kind_str = PageKind.SOURCE_NOTE.value if hasattr(PageKind, 'SOURCE_NOTE') else 'source_note'

    return WikiPage(
        slug=slug,
        title=f"Source: {source.title or 'Untitled'}",
        kind=PageKind.SOURCE_NOTE,
        summary=summary,
        body_md=body_md,
        source_ids=[source.source_id],
        meta_json={
            "source_type": source_type_str,
            "section_count": len(sections),
            "passage_count": len(passages),
        },
    )


def build_topic(
    title: str,
    topic_slug: str,
    source_ids: List[str],
    passages: List[Passage],
    summary: Optional[str] = None,
    facts: Optional[List[str]] = None,
    examples: Optional[List[str]] = None,
    open_questions: Optional[List[str]] = None,
    related_topics: Optional[List[str]] = None,
    citations: Optional[List[Dict[str, str]]] = None,
    source_signals: Optional[List[str]] = None,
) -> WikiPage:
    """构建 topic 页面

    topic 包含:
    - TL;DR (一句话总结)
    - Facts (关键事实)
    - Key Ideas (核心观点)
    - Examples (实例)
    - Open Questions (待解决问题)
    - Related Pages (相关页面)
    - Citations (引用来源)

    Args:
        title: 主题标题
        topic_slug: URL slug
        source_ids: 关联的源 ID 列表
        passages: 相关段落
        summary: 摘要/TL;DR
        facts: 关键事实列表
        examples: 实例列表
        open_questions: 待解决问题列表
        related_topics: 相关主题 slug 列表
        citations: 引用列表
        source_signals: 标题级或弱证据 source 信号

    Returns:
        WikiPage 对象
    """
    body_parts = []

    # Overview
    if summary:
        body_parts.append("## Overview\n")
        body_parts.append(summary)
        body_parts.append("")

    # Source Signals
    if source_signals:
        body_parts.append("## Source Signals\n")
        for signal in _deduplicate_texts(source_signals):
            body_parts.append(f"- {signal}")
        body_parts.append("")

    # Evidence Notes
    signal_keys = {_normalize_signal_text(signal) for signal in (source_signals or [])}
    evidence_notes = _deduplicate_texts([
        p.text for p in passages[:10]
        if p.text and _normalize_signal_text(p.text) not in signal_keys
    ])
    if evidence_notes:
        body_parts.append("## Evidence Notes\n")
        for idea in evidence_notes:
            body_parts.append(f"- {idea}")
        body_parts.append("")

    # Facts
    if facts:
        body_parts.append("## Facts\n")
        for fact in facts:
            body_parts.append(f"- {fact}")
        body_parts.append("")

    # Examples
    if examples:
        body_parts.append("## Examples\n")
        for i, example in enumerate(examples, 1):
            body_parts.append(f"{i}. {example}")
        body_parts.append("")

    # Open Questions
    if open_questions:
        body_parts.append("## Open Questions\n")
        for i, q in enumerate(open_questions, 1):
            body_parts.append(f"{i}. {q}")
        body_parts.append("")

    # Related Topics
    if related_topics:
        body_parts.append("## Related Topics\n")
        for rt in related_topics:
            body_parts.append(f"- [[{rt}]]")
        body_parts.append("")

    # Citations
    if citations:
        body_parts.append("## Citations\n")
        for cit in citations:
            label = cit.get("label", "Source")
            locator = cit.get("locator", "")
            excerpt = cit.get("excerpt", "")
            body_parts.append(f"- [{label}]({locator}): {excerpt[:100]}...")
        body_parts.append("")

    body_md = "\n".join(body_parts)

    return WikiPage(
        slug=topic_slug,
        title=title,
        kind=PageKind.TOPIC,  # Use TOPIC instead of ARTICLE
        summary=summary,
        body_md=body_md,
        source_ids=source_ids,
        link_slugs=related_topics or [],
        meta_json={
            "passage_count": len(passages),
            "fact_count": len(facts) if facts else 0,
            "example_count": len(examples) if examples else 0,
            "source_signal_count": len(source_signals) if source_signals else 0,
        },
    )


def build_conversation_note(
    conversation: Conversation,
    turns: List[Turn],
    summary: Optional[str] = None,
    key_turns: Optional[List[Turn]] = None,
    related_topics: Optional[List[str]] = None,
) -> WikiPage:
    """构建 conversation_note 页面

    conversation_note 包含:
    - 会话摘要
    - 关键 turn (highlight reel)
    - 相关主题

    Args:
        conversation: 对话对象
        turns: 对话回合列表
        summary: 会话摘要
        key_turns: 关键回合（自动或手动选择）
        related_topics: 相关主题 slug 列表

    Returns:
        WikiPage 对象
    """
    slug = f"conversation-{conversation.conversation_id[:8]}"

    body_parts = []

    # 会话信息
    body_parts.append("## Conversation Info\n")
    if conversation.title:
        body_parts.append(f"- **Title**: {conversation.title}")
    if conversation.participants:
        body_parts.append(f"- **Participants**: {', '.join(conversation.participants)}")
    if conversation.created_at:
        body_parts.append(f"- **Date**: {conversation.created_at.isoformat() if isinstance(conversation.created_at, datetime) else conversation.created_at}")
    body_parts.append(f"- **Turns**: {len(turns)}")
    body_parts.append("")

    # 摘要
    if summary:
        body_parts.append("## Summary\n")
        body_parts.append(summary)
        body_parts.append("")

    # 关键回合
    if key_turns:
        body_parts.append("## Key Turns\n")
        for i, turn in enumerate(key_turns, 1):
            role = turn.role.upper()
            content = turn.content_text[:300] + ("..." if len(turn.content_text) > 300 else "")
            body_parts.append(f"### {i}. [{role}]\n")
            body_parts.append(content)
            body_parts.append("")
        body_parts.append("")

    # 相关主题
    if related_topics:
        body_parts.append("## Related Topics\n")
        for rt in related_topics:
            body_parts.append(f"- [[{rt}]]")
        body_parts.append("")

    body_md = "\n".join(body_parts)

    return WikiPage(
        slug=slug,
        title=f"Conversation: {conversation.title or 'Untitled'}",
        kind=PageKind.CONVERSATION_NOTE,
        summary=summary,
        body_md=body_md,
        source_ids=[conversation.source_id] if conversation.source_id else [],
        link_slugs=related_topics or [],
        meta_json={
            "conversation_id": conversation.conversation_id,
            "turn_count": len(turns),
            "participant_count": len(conversation.participants),
        },
    )


def build_index(
    title: str,
    index_slug: str,
    pages: List[WikiPage],
    recent_pages: Optional[List[WikiPage]] = None,
    by_type: Optional[Dict[str, List[WikiPage]]] = None,
) -> WikiPage:
    """构建 index 页面

    index 包含:
    - 总索引
    - 最近导入
    - 按类型索引

    Args:
        title: 索引标题
        index_slug: URL slug
        pages: 所有页面列表
        recent_pages: 最近页面列表
        by_type: 按类型分组的页面

    Returns:
        WikiPage 对象
    """
    body_parts = []

    # 总统计
    body_parts.append(f"## Overview\n")
    body_parts.append(f"- **Total Pages**: {len(pages)}")
    body_parts.append("")

    # 最近导入
    if recent_pages:
        body_parts.append("## Recent Pages\n")
        for page in recent_pages[:10]:
            date_str = page.updated_at.isoformat() if isinstance(page.updated_at, datetime) else str(page.updated_at)
            body_parts.append(f"- [[{page.title}]] ({page.kind.value}, {date_str[:10]})")
        body_parts.append("")

    # 按类型索引
    if by_type:
        body_parts.append("## By Type\n")
        for type_name, type_pages in by_type.items():
            body_parts.append(f"### {type_name} ({len(type_pages)})\n")
            for page in type_pages:
                body_parts.append(f"- [[{page.title}]]")
            body_parts.append("")

    body_md = "\n".join(body_parts)

    return WikiPage(
        slug=index_slug,
        title=title,
        kind=PageKind.INDEX,
        summary=f"Index of {len(pages)} pages",
        body_md=body_md,
        meta_json={
            "total_pages": len(pages),
            "recent_count": len(recent_pages) if recent_pages else 0,
            "type_count": len(by_type) if by_type else 0,
        },
    )


def _build_chapter_structure(sections: List[NormalizedSection]) -> str:
    """从章节列表构建结构化大纲"""
    if not sections:
        return ""

    lines = []
    current_h1 = None
    current_h2 = None

    for section in sections:
        title = section.title or "Untitled"
        indent = "  "

        # 获取 kind 值（兼容 Enum 和字符串）
        kind_val = section.kind.value if hasattr(section.kind, 'value') else str(section.kind)

        if kind_val in ("chapter", "heading", "HEADING"):
            current_h1 = title
            current_h2 = None
            lines.append(f"1. **{title}**")
        elif kind_val in ("section", "SECTION") and current_h1:
            current_h2 = title
            lines.append(f"{indent}1. {title}")
        elif kind_val in ("paragraph", "PARAGRAPH") and (current_h1 or current_h2):
            # 简短描述
            preview = section.text[:60] + ("..." if len(section.text) > 60 else "")
            lines.append(f"{indent}{indent}- {preview}")

    return "\n".join(lines)


def _extract_key_excerpts(passages: List[Passage], max_excerpts: int = 5) -> List[str]:
    """从段落中提取关键摘录"""
    if not passages:
        return []

    # 简单策略：选择较长的、有代表性的段落
    sorted_passages = sorted(passages, key=lambda p: len(p.text), reverse=True)

    excerpts = []
    seen_texts = set()

    for passage in sorted_passages:
        text = passage.text.strip()
        # 去重（相似文本）
        if text not in seen_texts and len(text) > 20:
            excerpts.append(text[:200] + ("..." if len(text) > 200 else ""))
            seen_texts.add(text)
            if len(excerpts) >= max_excerpts:
                break

    return excerpts


def _deduplicate_texts(texts: List[str]) -> List[str]:
    """去重相似文本"""
    if not texts:
        return []

    unique = []
    seen_sigs = set()

    for text in texts:
        # 使用前50字符作为签名
        sig = text[:50].lower().strip()
        if sig and sig not in seen_sigs:
            unique.append(text)
            seen_sigs.add(sig)

    return unique


def _normalize_signal_text(text: str) -> str:
    text = (text or "").strip().lower()
    return "".join(ch for ch in text if ch.isalnum() or "\u4e00" <= ch <= "\u9fff")

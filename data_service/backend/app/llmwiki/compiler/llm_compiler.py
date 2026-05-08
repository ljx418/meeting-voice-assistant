"""LLM-backed wiki compilation with local fallback."""
import json
import re
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Union

from ..llm_client import LLMClientError, build_llm_client
from ..models import PageKind, Passage, SourceRecord, WikiPage
from .classifier import classify, extract_keywords, generate_slug
from .page_builder import build_topic


@dataclass
class CompileResult:
    """Compilation outcome with fallback metadata."""

    page: WikiPage
    used_llm: bool
    error: Optional[str] = None


class WikiCompiler:
    """Compile wiki pages from raw sources."""

    def __init__(self, config):
        self.config = config
        self.client = build_llm_client(config)

    def compile_source_page(
        self,
        source: SourceRecord,
        sections,
        passages: Sequence[Passage],
    ) -> CompileResult:
        cleaned_passages = self._clean_passages(passages)
        cleaned_sections = self._clean_sections(sections)
        outline = self._derive_source_outline(source, cleaned_sections, cleaned_passages)
        fallback_page = self._build_structured_source_page(source, cleaned_sections, cleaned_passages, outline)
        fallback_page.compiled_at = datetime.utcnow()

        if not self.client.is_enabled():
            fallback_page.compile_status = "disabled"
            fallback_page.compile_error = "LLM provider disabled"
            return CompileResult(page=fallback_page, used_llm=False, error="LLM provider disabled")

        prompt = self._build_source_prompt(source, cleaned_sections, cleaned_passages)
        try:
            response = self.client.complete_json(
                "You compile source material into concise Markdown wiki pages. Return JSON only.",
                prompt,
            )
            payload = json.loads(response.text)
            page = WikiPage(
                slug=fallback_page.slug,
                title=payload.get("title") or fallback_page.title,
                kind=PageKind.SOURCE_NOTE,
                summary=payload.get("summary") or fallback_page.summary,
                body_md=payload.get("body_md") or fallback_page.body_md,
                source_ids=[source.source_id],
                link_slugs=payload.get("related_topics") or [],
                updated_at=datetime.utcnow(),
                compiled_at=datetime.utcnow(),
                compile_status="success",
                compiled_by_model=self.client.model_name(),
                meta_json={
                    **fallback_page.meta_json,
                    "llm_keywords": payload.get("keywords") or [],
                    "source_outline": outline,
                },
            )
            return CompileResult(page=page, used_llm=True)
        except (LLMClientError, json.JSONDecodeError, TypeError, ValueError) as exc:
            fallback_page.compile_status = "fallback"
            fallback_page.compile_error = str(exc)
            fallback_page.compiled_at = datetime.utcnow()
            return CompileResult(page=fallback_page, used_llm=False, error=str(exc))

    def compile_topic_pages(
        self,
        sources: Sequence[SourceRecord],
        passages_by_source: Dict[str, List[Passage]],
    ) -> List[CompileResult]:
        topic_groups: Dict[str, List[SourceRecord]] = defaultdict(list)
        for source in sources:
            content = "\n".join(self._sanitize_text(p.text) for p in passages_by_source.get(source.source_id, [])[:6])
            topic_slug = self._group_topic_slug(source, content)
            topic_groups[topic_slug].append(source)

        results: List[CompileResult] = []
        for topic_slug, topic_sources in topic_groups.items():
            passages: List[Passage] = []
            for source in topic_sources:
                passages.extend(passages_by_source.get(source.source_id, [])[:4])
            results.append(self._compile_single_topic(topic_slug, topic_sources, passages))
        return results

    def _group_topic_slug(self, source: SourceRecord, content: str) -> str:
        semantic_slug = self._semantic_topic_slug(source.title or "", content)
        if semantic_slug:
            return semantic_slug
        topic_slug, matched_topics = classify(source.title or "", content, source.original_path)
        normalized_title_slug = self._title_group_slug(source.title or "")
        if normalized_title_slug:
            return normalized_title_slug
        if topic_slug != "general":
            return topic_slug
        if matched_topics:
            return matched_topics[0]
        return self._refine_topic_slug(topic_slug, source, content)

    def _compile_single_topic(
        self,
        topic_slug: str,
        sources: Sequence[SourceRecord],
        passages: Sequence[Passage],
    ) -> CompileResult:
        topic_title = self._topic_title_from_sources(topic_slug, sources, passages)
        source_ids = [source.source_id for source in sources]
        cleaned_passages = self._clean_passages(passages)
        topic_outline = self._derive_topic_outline(topic_title, sources, cleaned_passages)
        fallback_page = build_topic(
            title=topic_title,
            topic_slug=topic_slug,
            source_ids=source_ids,
            passages=list(cleaned_passages[:10]),
            summary=topic_outline["summary"],
            facts=topic_outline["facts"],
            examples=topic_outline["examples"],
            open_questions=topic_outline["open_questions"],
            related_topics=topic_outline["related_topics"],
            source_signals=topic_outline["source_signals"],
            citations=[
                {
                    "label": source.title or source.source_id,
                    "locator": source.original_path or "",
                    "excerpt": cleaned_passages[idx].text[:120] if idx < len(cleaned_passages) else "",
                }
                for idx, source in enumerate(sources[:5])
            ],
        )
        fallback_page.compiled_at = datetime.utcnow()

        if not cleaned_passages or not self.client.is_enabled():
            fallback_page.compile_status = "disabled" if not self.client.is_enabled() else "fallback"
            fallback_page.compile_error = None if cleaned_passages else "No passages"
            return CompileResult(page=fallback_page, used_llm=False, error=None if cleaned_passages else "No passages")

        prompt = self._build_topic_prompt(topic_slug, sources, cleaned_passages)
        try:
            response = self.client.complete_json(
                "You compile multiple sources into a topic wiki page. Return JSON only.",
                prompt,
            )
            payload = json.loads(response.text)
            page = WikiPage(
                slug=topic_slug,
                title=payload.get("title") or topic_title,
                kind=PageKind.TOPIC,
                summary=payload.get("summary") or fallback_page.summary,
                body_md=payload.get("body_md") or fallback_page.body_md,
                source_ids=source_ids,
                link_slugs=payload.get("related_topics") or [],
                updated_at=datetime.utcnow(),
                compiled_at=datetime.utcnow(),
                compile_status="success",
                compiled_by_model=self.client.model_name(),
                meta_json={
                    "source_count": len(source_ids),
                    "keywords": payload.get("keywords") or extract_keywords(" ".join(p.text for p in cleaned_passages[:10])),
                    "topic_outline": topic_outline,
                },
            )
            return CompileResult(page=page, used_llm=True)
        except (LLMClientError, json.JSONDecodeError, TypeError, ValueError) as exc:
            fallback_page.compile_status = "fallback"
            fallback_page.compile_error = str(exc)
            fallback_page.compiled_at = datetime.utcnow()
            return CompileResult(page=fallback_page, used_llm=False, error=str(exc))

    def write_markdown_page(self, page: WikiPage) -> Path:
        """Persist a compiled page as markdown."""

        pages_dir = self.config.markdown_output_dir
        pages_dir.mkdir(parents=True, exist_ok=True)
        path = pages_dir / f"{page.slug}.md"
        header = [
            f"# {page.title}",
            "",
            f"- kind: {page.kind.value if hasattr(page.kind, 'value') else page.kind}",
            f"- sources: {', '.join(page.source_ids) if page.source_ids else ''}",
            "",
        ]
        path.write_text("\n".join(header) + page.body_md.strip() + "\n", encoding="utf-8")
        return path

    def _build_source_prompt(self, source: SourceRecord, sections, passages: Sequence[Passage]) -> str:
        outline = self._derive_source_outline(source, sections, passages)
        section_text = "\n".join(
            f"- {section.title or 'section'}: {self._sanitize_text(section.text)[:280]}"
            for section in sections[:12]
        )
        excerpt_text = "\n".join(f"- {self._sanitize_text(passage.text)[:280]}" for passage in passages[:8])
        return (
            "Return JSON with keys: title, summary, body_md, related_topics, keywords.\n"
            f"Source title: {source.title}\n"
            f"Source path: {source.original_path}\n"
            f"Question hint: {outline['question']}\n"
            f"Conclusion hint: {outline['core_conclusion']}\n"
            f"Actionable steps hint: {' | '.join(outline['steps'])}\n"
            f"Risk hint: {' | '.join(outline['risks'])}\n"
            f"Sections:\n{section_text}\n"
            f"Passages:\n{excerpt_text}\n"
            "Ignore UUIDs, timestamps, bookkeeping fields, and storage metadata.\n"
            "body_md should be concise markdown with sections Question, Core Conclusion, Actionable Steps, Risks and Limits, Evidence, Related Topics."
        )

    def _build_topic_prompt(
        self,
        topic_slug: str,
        sources: Sequence[SourceRecord],
        passages: Sequence[Passage],
    ) -> str:
        topic_title = self._topic_title_from_sources(topic_slug, sources, passages)
        topic_outline = self._derive_topic_outline(topic_title, sources, passages)
        source_text = "\n".join(f"- {source.title}: {source.original_path}" for source in sources[:12])
        excerpt_text = "\n".join(f"- {self._sanitize_text(passage.text)[:280]}" for passage in passages[:12])
        return (
            "Return JSON with keys: title, summary, body_md, related_topics, keywords.\n"
            f"Topic slug: {topic_slug}\n"
            f"Topic title hint: {topic_title}\n"
            f"Summary hint: {topic_outline['summary']}\n"
            f"Common facts hint: {' | '.join(topic_outline['facts'])}\n"
            f"Open questions hint: {' | '.join(topic_outline['open_questions'])}\n"
            f"Sources:\n{source_text}\n"
            f"Evidence:\n{excerpt_text}\n"
            "Ignore UUIDs, timestamps, bookkeeping fields, and storage metadata.\n"
            "body_md should be concise markdown with sections TL;DR, Common Questions, Key Conclusions, Actionable Guidance, Examples, Open Questions, Citations."
        )

    def _clean_sections(self, sections) -> List:
        cleaned = []
        for section in sections:
            section.text = self._sanitize_text(section.text)
            cleaned.append(section)
        return cleaned

    def _clean_passages(self, passages: Sequence[Passage]) -> List[Passage]:
        cleaned: List[Passage] = []
        for passage in passages:
            passage.text = self._sanitize_text(passage.text)
            if passage.text:
                cleaned.append(passage)
        return cleaned or list(passages)

    def _sanitize_text(self, text: str) -> str:
        text = text or ""
        text = re.sub(r"\b[0-9a-f]{8}-[0-9a-f-]{27}\b", "", text, flags=re.IGNORECASE)
        text = re.sub(r"\b[0-9a-f]{16,64}\b", "", text, flags=re.IGNORECASE)
        text = re.sub(r"\b\d{4}-\d{2}-\d{2}T[0-9:.+\-Z]+\b", "", text)
        text = re.sub(r"(?m)^\s*(conversation_id|inserted_at|updated_at|created_at|id|parent|children)\s*[:=].*$", "", text)
        text = re.sub(r"\n{3,}", "\n\n", text)
        return text.strip()

    def _refine_topic_slug(self, topic_slug: str, source: SourceRecord, content: str) -> str:
        if topic_slug != "general":
            return topic_slug
        title = (source.title or "").strip()
        if title:
            title_slug = generate_slug(title)
            if title_slug and title_slug != "untitled":
                return title_slug[:80]
        keywords = extract_keywords(content, top_n=3)
        if keywords:
            return generate_slug("-".join(keywords[:2])) or "general"
        return "general"

    def _clean_display_title(self, title: str) -> str:
        title = (title or "").strip()
        if not title:
            return ""
        title = re.sub(r"^(source|conversation)\s*:\s*", "", title, flags=re.IGNORECASE)
        title = re.sub(r"^tmp[_\-\s]+", "", title, flags=re.IGNORECASE)
        title = re.sub(r"\bconversation[_\-\s]*id\b", "", title, flags=re.IGNORECASE)
        title = re.sub(r"\bsource[_\-\s]*id\b", "", title, flags=re.IGNORECASE)
        title = re.sub(r"\b(废弃于\d{8}|已废弃|归档|临时)\b", "", title)
        title = re.sub(r"\b\d{4}年\d{1,2}月\d{1,2}日?\b", "", title)
        title = re.sub(r"\b[0-9a-f]{8}-[0-9a-f-]{27}\b", "", title, flags=re.IGNORECASE)
        title = re.sub(r"[_.]+", " ", title)
        title = re.sub(r"[（(].*?[)）]", "", title)
        title = re.sub(r"\s+", " ", title).strip(" -_:.")
        return title

    def _is_meaningful_display_title(self, title: str) -> bool:
        title = self._strip_question_scaffold(self._clean_display_title(title))
        if not title:
            return False
        lowered = title.lower()
        if lowered in {"untitled", "source", "conversation", "conversation id"}:
            return False
        if re.search(r"(?i)\bconversation\b", lowered):
            return False
        if re.fullmatch(r"[0-9a-f]{8,}", lowered):
            return False
        if re.fullmatch(r"conversation(?:\s+\d+)?", lowered):
            return False
        compact = re.sub(r"\s+", "", title)
        if len(compact) < 3 and not re.fullmatch(r"[\u4e00-\u9fff]{2}", compact):
            return False
        return True

    def _display_title_from_question(self, question: str) -> str:
        question = self._clean_display_title(question).strip("？? ")
        if not question:
            return ""
        question = self._strip_question_scaffold(question).strip("？? ")
        return question

    def _display_title_for_source(self, source: SourceRecord, outline: Dict[str, Union[List[str], str]]) -> str:
        for candidate in (
            source.title,
            outline.get("question") if isinstance(outline, dict) else "",
            Path(source.original_path).stem if source.original_path else "",
        ):
            if candidate == outline.get("question"):
                cleaned = self._display_title_from_question(str(candidate or ""))
            else:
                cleaned = self._clean_display_title(str(candidate or ""))
            if self._is_meaningful_display_title(cleaned):
                return cleaned
        return "Untitled Source"

    def _build_structured_source_page(self, source: SourceRecord, sections, passages: Sequence[Passage], outline: Dict[str, Union[List[str], str]]) -> WikiPage:
        slug = generate_slug(source.title or source.original_path or "source")
        slug = f"source-{slug[:50]}-{source.source_id[:8]}"
        is_secondary_chat = source.authority == "SECONDARY_CHAT"
        source_title = self._display_title_for_source(source, outline)
        body_parts = [
            "## Question",
            "",
            outline["question"] or "未识别出明确问题。",
            "",
            "## Core Conclusion",
            "",
            outline["core_conclusion"] or "暂无明确结论，建议回看原文。",
            "",
        ]
        if outline.get("source_signals"):
            body_parts.extend(["## Source Signals", ""])
            body_parts.extend(f"- {signal}" for signal in outline["source_signals"])
            body_parts.append("")
        if outline["steps"]:
            body_parts.extend(["## Actionable Steps", ""])
            body_parts.extend(f"{idx}. {step}" for idx, step in enumerate(outline["steps"], 1))
            body_parts.append("")
        if outline["key_points"]:
            body_parts.extend(["## Unverified Notes" if is_secondary_chat else "## Key Points", ""])
            body_parts.extend(f"- {point}" for point in outline["key_points"])
            body_parts.append("")
        if is_secondary_chat:
            body_parts.extend([
                "## Verification Status",
                "",
                "- This page is derived from chat material and should be treated as secondary guidance until corroborated by primary documents.",
                "",
            ])
        if outline["risks"]:
            body_parts.extend(["## Risks and Limits", ""])
            body_parts.extend(f"- {risk}" for risk in outline["risks"])
            body_parts.append("")
        if passages:
            signal_keys = {
                re.sub(r"\W+", "", self._clean_display_title(signal)).lower()
                for signal in outline.get("source_signals", [])
            }
            evidence_items: List[str] = []
            for excerpt in passages[:5]:
                excerpt_key = re.sub(r"\W+", "", self._clean_display_title(excerpt.text)).lower()
                if excerpt_key and excerpt_key in signal_keys:
                    continue
                snippet = self._prefer_summary_sentence(excerpt.text, max_len=220) or excerpt.text[:220]
                if snippet:
                    evidence_items.append(snippet)
            if evidence_items:
                body_parts.extend(["## Evidence", ""])
                body_parts.extend(f"- {item}" for item in self._dedupe_strings(evidence_items))
                body_parts.append("")
        source_context: List[str] = []
        if source.original_path:
            source_context.append(f"- Path: `{source.original_path}`")
        if outline["keywords"]:
            source_context.append(f"- Keywords: {', '.join(outline['keywords'])}")
        if source_context:
            body_parts.extend(["## Source Context", ""])
            body_parts.extend(source_context)
            body_parts.append("")
        return WikiPage(
            slug=slug,
            title=source_title,
            kind=PageKind.SOURCE_NOTE,
            summary=outline["summary"],
            body_md="\n".join(body_parts).strip() + "\n",
            source_ids=[source.source_id],
            link_slugs=[],
            updated_at=datetime.utcnow(),
            compiled_at=datetime.utcnow(),
            compile_status="fallback",
            meta_json={
                "source_type": source.source_type.value if hasattr(source.source_type, "value") else str(source.source_type),
                "authority": source.authority,
                "section_count": len(sections),
                "passage_count": len(passages),
                "source_outline": outline,
            },
        )

    def _derive_source_outline(self, source: SourceRecord, sections, passages: Sequence[Passage]) -> Dict[str, Union[List[str], str]]:
        combined_text = "\n\n".join(self._sanitize_text(getattr(section, "text", "")) for section in sections[:24])
        source_titles = self._dedupe_strings([
            self._clean_display_title(source.title or "")
            for source in [source]
            if self._is_meaningful_display_title(source.title or "")
        ])
        question = (
            self._extract_markdown_section(combined_text, "Question")
            or self._extract_markdown_section(combined_text, "问题")
            or self._first_question(passages)
            or source.title
            or ""
        )
        conclusion = (
            self._extract_markdown_section(combined_text, "Core Conclusion")
            or self._extract_markdown_section(combined_text, "结论")
            or self._extract_markdown_section(combined_text, "摘要")
            or self._best_statement(passages)
        )
        if self._is_title_signal(conclusion, source_titles):
            conclusion = ""
        steps = self._collect_bullets(
            self._extract_markdown_section(combined_text, "Actionable Steps")
            or self._extract_markdown_section(combined_text, "操作步骤")
            or self._extract_markdown_section(combined_text, "步骤")
        )
        if not steps:
            steps = self._extract_steps_from_passages(passages)
        risks = self._collect_risks(combined_text, passages)
        key_points = [
            point for point in self._collect_key_points(passages, question, conclusion)
            if not self._is_title_signal(point, source_titles)
        ]
        keywords = extract_keywords(" ".join([source.title or "", combined_text]), top_n=6)
        summary = conclusion or (key_points[0] if key_points else "")
        return {
            "question": question.strip(),
            "core_conclusion": conclusion.strip(),
            "summary": summary.strip(),
            "steps": steps[:6],
            "risks": risks[:5],
            "key_points": key_points[:6],
            "keywords": keywords[:6],
            "source_signals": source_titles[:5],
        }

    def _derive_topic_outline(self, topic_title: str, sources: Sequence[SourceRecord], passages: Sequence[Passage]) -> Dict[str, Union[List[str], str]]:
        has_primary = any(source.authority == "PRIMARY_DOC" for source in sources)
        source_titles = self._dedupe_strings([
            self._clean_display_title(source.title or "")
            for source in sources
            if self._is_meaningful_display_title(source.title or "")
        ])
        fact_candidates = [
            self._prefer_summary_sentence(passage.text, max_len=180)
            for passage in passages[:10]
            if not self._is_title_signal(passage.text, source_titles)
        ]
        facts = self._dedupe_strings([candidate for candidate in fact_candidates if candidate])[:5] if has_primary else []
        examples = self._dedupe_strings(
            [
                self._prefer_summary_sentence(p.text, max_len=180) or p.text[:180]
                for p in passages
                if re.search(r"(?i)\b(example|例如|比如|案例)\b", p.text)
            ]
        )[:4]
        open_questions = self._dedupe_strings(
            [match.strip() for passage in passages[:10] for match in re.findall(r"[^。！？?\n]{4,80}[？?]", passage.text)]
        )[:4]
        related_topics = self._dedupe_strings(
            [self._semantic_topic_slug(source.title or "", " ".join(p.text for p in passages[:3])) for source in sources]
        )
        topic_slug = generate_slug(topic_title)
        related_topics = [
            slug for slug in related_topics
            if slug and slug != topic_slug and slug not in {"general", "source", "conversation"}
        ]
        summary = ""
        if facts:
            summary = facts[0]
        elif source_titles:
            source_count = len(source_titles)
            summary = f"Collected source material about {topic_title} from {source_count} source{'s' if source_count != 1 else ''}."
        return {
            "summary": summary,
            "facts": facts,
            "examples": examples,
            "open_questions": open_questions,
            "related_topics": related_topics[:6],
            "source_signals": source_titles[:8],
            "has_primary": has_primary,
        }

    def _is_title_signal(self, text: str, source_titles: Sequence[str]) -> bool:
        cleaned = self._clean_display_title(text)
        if not cleaned:
            return True
        compact = re.sub(r"\s+", "", cleaned).lower()
        if not compact:
            return True
        for title in source_titles:
            title_compact = re.sub(r"\s+", "", self._clean_display_title(title)).lower()
            if compact == title_compact:
                return True
        return False

    def _extract_markdown_section(self, text: str, heading: str) -> str:
        if not text:
            return ""
        pattern = rf"(?ims)^##\s+{re.escape(heading)}\s*$\n(.*?)(?=^##\s+|\Z)"
        match = re.search(pattern, text)
        return match.group(1).strip() if match else ""

    def _first_question(self, passages: Sequence[Passage]) -> str:
        for passage in passages[:8]:
            questions = re.findall(r"[^。！？\n]{4,120}[？?]", passage.text)
            if questions:
                return questions[0].strip()
        return ""

    def _best_statement(self, passages: Sequence[Passage]) -> str:
        for passage in passages[:8]:
            lines = [
                self._clean_candidate_line(line)
                for line in passage.text.splitlines()
                if len(line.strip()) > 12
            ]
            for line in lines:
                if line and "?" not in line and "？" not in line and not self._looks_like_step(line):
                    return line[:220]
        return ""

    def _collect_bullets(self, text: str) -> List[str]:
        if not text:
            return []
        bullets: List[str] = []
        for line in text.splitlines():
            cleaned = re.sub(r"^\s*(?:[-*]|\d+[.)])\s*", "", line).strip()
            if cleaned:
                bullets.append(cleaned)
        return self._dedupe_strings(bullets)

    def _extract_steps_from_passages(self, passages: Sequence[Passage]) -> List[str]:
        steps: List[str] = []
        for passage in passages[:8]:
            for line in passage.text.splitlines():
                cleaned = self._clean_candidate_line(line)
                if cleaned and self._looks_like_step(cleaned):
                    steps.append(cleaned[:160])
        return self._dedupe_strings(steps)

    def _collect_risks(self, combined_text: str, passages: Sequence[Passage]) -> List[str]:
        candidates: List[str] = []
        scan_texts = [combined_text] + [passage.text for passage in passages[:8]]
        for text in scan_texts:
            for line in text.splitlines():
                cleaned = line.strip("-* 0123456789. ")
                if cleaned and re.search(r"(?i)(风险|限制|注意|报错|失败|无法|不能|missing|error|unsupported|not supported)", cleaned):
                    candidates.append(cleaned[:180])
        return self._dedupe_strings(candidates)

    def _collect_key_points(self, passages: Sequence[Passage], question: str, conclusion: str) -> List[str]:
        points: List[str] = []
        for passage in passages[:10]:
            for line in passage.text.splitlines():
                cleaned = self._clean_candidate_line(line)
                if not cleaned or len(cleaned) < 8:
                    continue
                if cleaned == question or cleaned == conclusion or self._looks_like_step(cleaned):
                    continue
                points.append(cleaned[:180])
        return self._dedupe_strings(points)

    def _dedupe_strings(self, values: Sequence[str]) -> List[str]:
        seen = set()
        deduped: List[str] = []
        for value in values:
            normalized = re.sub(r"\s+", " ", (value or "").strip().lower())
            if not normalized or normalized in seen:
                continue
            seen.add(normalized)
            deduped.append((value or "").strip())
        return deduped

    def _clean_candidate_line(self, text: str) -> str:
        cleaned = re.sub(r"^\s*(?:[-*]|\d+[.)])\s*", "", text or "").strip()
        cleaned = re.sub(r"^\[(user|assistant|system|unknown)\]\s*:\s*", "", cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r"\s+", " ", cleaned).strip(" -:")
        if self._looks_noisy_line(cleaned):
            return ""
        return cleaned

    def _looks_noisy_line(self, text: str) -> bool:
        if not text:
            return True
        lowered = text.lower()
        if lowered in {"n/a", "none", "null"}:
            return True
        if re.search(r"(?i)\b(conversation id|created at|updated at|metadata|source details|sections|passages|keywords)\b", text):
            return True
        if re.search(r"(?i)^(path|locator|role|turn)\s*:", text):
            return True
        if re.fullmatch(r"[A-Za-z0-9/_\-.]{16,}", text):
            return True
        return False

    def _looks_like_step(self, text: str) -> bool:
        return bool(re.match(r"(?i)(step\s*\d+|先|然后|接着|最后|安装|配置|运行|执行|打开|设置|检查|确认|创建|启动|重启)", text or ""))

    def _prefer_summary_sentence(self, text: str, max_len: int = 180) -> str:
        for segment in re.split(r"(?<=[。！？.!?])\s+|\n+", text or ""):
            candidate = self._clean_candidate_line(segment)
            if not candidate or len(candidate) < 12:
                continue
            if "?" in candidate or "？" in candidate or self._looks_like_step(candidate):
                continue
            return candidate[:max_len]
        return ""

    def _semantic_topic_slug(self, title: str, content: str) -> Optional[str]:
        title = self._strip_question_scaffold(title)
        anchor = self._extract_topic_anchor(title, content)
        if not anchor:
            return None
        return generate_slug(anchor)

    def _strip_question_scaffold(self, title: str) -> str:
        title = (title or "").strip()
        title = re.sub(r"^(怎么|如何|为什么|是否|能否|可否|请问|想知道|求问)\s*", "", title)
        title = re.sub(r"\s*(怎么办|怎么做|是什么|有哪些|步骤|方法|教程|案例|总结|实践)$", "", title)
        return title.strip(" -_")

    def _extract_topic_anchor(self, title: str, content: str) -> Optional[str]:
        title = self._clean_display_title(title)
        special_anchor = self._extract_special_topic_anchor(title)
        if special_anchor:
            return special_anchor
        product_anchor = self._extract_product_anchor(title)
        if product_anchor:
            return product_anchor
        title_tokens = re.findall(r"[A-Za-z][A-Za-z0-9.+_-]{1,}|[\u4e00-\u9fff]{2,16}", title)
        filtered_title = [
            token for token in title_tokens
            if not self._is_generic_topic_token(token) and not self._is_fragment_topic_token(token, title)
        ]
        if filtered_title:
            return filtered_title[0]
        keywords = extract_keywords(f"{title} {content}", top_n=8)
        for keyword in keywords:
            if not self._is_generic_topic_token(keyword) and not self._is_fragment_topic_token(keyword, title):
                return keyword
        return None

    def _extract_special_topic_anchor(self, title: str) -> Optional[str]:
        compact = re.sub(r"\s+", "", title or "")
        if not compact:
            return None
        english_term = re.search(r"(?i)\bclarificationon([a-z][a-z0-9.+_-]{2,})term\b", compact)
        if english_term:
            return english_term.group(1)
        anchors = [
            ("退休资金", "退休资金"),
            ("管培生", "管培生"),
            ("云南菜", "云南菜"),
            ("车企", "车企"),
            ("智能卡片", "智能卡片"),
            ("香农极限", "香农极限"),
            ("端午节", "端午节"),
        ]
        for marker, anchor in anchors:
            if marker in compact:
                return anchor
        return None

    def _extract_product_anchor(self, title: str) -> Optional[str]:
        title = (title or "").strip()
        if not title:
            return None
        compact = re.sub(r"\s+", "", title)
        if "税前工资" in compact:
            return "税前工资"
        if "等额本息" in compact and "月供" in compact:
            return "等额本息月供"
        known = re.search(
            r"(?i)(VSCode|TypeScript|Python|OpenClaw|ClaudeCode|ComfyUI|Cursor|DeepSeek|Hermes|Bose|Excel|VBA|LMM|CN\d+[A-Z]?)",
            title,
        )
        if known:
            token = known.group(1)
            prefix = title[:known.start()].strip()
            if prefix and re.fullmatch(r"[\u4e00-\u9fff]{1,8}", prefix):
                cleaned_prefix = re.sub(r"^(怎么安装|如何安装|怎么配置|如何配置|已安装|安装|配置|使用|免费|检查|确认|验证|搭建|运行|生成)", "", prefix)
                if cleaned_prefix and not self._is_generic_topic_token(cleaned_prefix):
                    return f"{cleaned_prefix}{token}"
            return token
        mixed = re.search(r"([\u4e00-\u9fff]{1,8})([A-Za-z]{1,8}\d+[A-Za-z0-9]*|\d+[A-Za-z]{1,8}[A-Za-z0-9]*)", compact)
        if mixed:
            prefix = mixed.group(1)
            token = mixed.group(2)
            if not self._is_generic_topic_token(prefix):
                return f"{prefix}{token}"
        ai_phrase = re.search(r"(?i)(AI|HR)([\u4e00-\u9fff]{2,8})", compact)
        if ai_phrase:
            suffix = ai_phrase.group(2)
            if not self._is_generic_topic_token(suffix):
                return f"{ai_phrase.group(1).upper()}{suffix}"
        return None

    def _is_generic_topic_token(self, token: str) -> bool:
        token = token.strip().lower()
        if not token or token.isdigit():
            return True
        generic = {
            "问题", "步骤", "方法", "教程", "案例", "实践", "总结", "记录", "回复", "回答",
            "安装", "配置", "使用", "报错", "错误", "解决", "问题排查", "question", "answer",
            "免费", "助手", "已安装", "选项验证", "指南", "说明", "解析", "分析", "计算",
            "步骤", "流程", "工具", "推荐", "建议", "查询", "验证", "背景介绍",
            "user", "seeks", "clarification", "on", "term", "steps", "guide", "tutorial",
            "setup", "install", "error", "config",
        }
        return token in generic

    def _is_fragment_topic_token(self, token: str, title: str) -> bool:
        token = (token or "").strip()
        if not token:
            return True
        if re.fullmatch(r"(万贷款|税后|免费|已安装|助手|用户|问题|分析|解析)", token, flags=re.IGNORECASE):
            return True
        if re.search(r"\d", title) and re.fullmatch(r"[\u4e00-\u9fff]{1,4}", token):
            if token in {"万贷款", "税后", "公里续航", "元以上", "岁停止", "岁工作"}:
                return True
        if re.fullmatch(r"[A-Za-z]{2,}", token):
            return token.lower() in {
                "user", "seeks", "clarification", "on", "term", "request", "response",
                "guide", "setup", "config", "error",
            }
        return False

    def _title_group_slug(self, title: str) -> Optional[str]:
        title = (title or "").strip()
        if not title:
            return None
        title = re.sub(r"^tmp[_\-\s]+", "", title, flags=re.IGNORECASE)
        title = re.sub(r"\b(废弃于\d{8}|\d{4}年\d{1,2}月\d{1,2}日?)\b", "", title)
        title = re.sub(r"[（(].*?[)）]", "", title)
        title = re.sub(r"\s+", " ", title).strip()
        if re.fullmatch(r"[\u4e00-\u9fffA-Za-z0-9 ]+", title):
            slug = generate_slug(title)
            return slug if slug and slug != "untitled" else None
        tokens = [t for t in re.findall(r"[A-Za-z][A-Za-z0-9]+|[\u4e00-\u9fff]{2,20}", title) if len(t) > 1]
        if not tokens:
            return None
        normalized = "-".join(tokens[:4])
        slug = generate_slug(normalized)
        return slug if slug and slug != "untitled" else None

    def _topic_title_from_sources(
        self,
        topic_slug: str,
        sources: Sequence[SourceRecord],
        passages: Sequence[Passage],
    ) -> str:
        meaningful_titles = [
            self._clean_display_title(source.title or "")
            for source in sources
            if self._is_meaningful_display_title(source.title or "")
        ]
        if meaningful_titles:
            candidate = meaningful_titles[0]
            anchor = self._extract_topic_anchor(candidate, " ".join(p.text for p in passages[:4]))
            if anchor and self._should_prefer_topic_anchor(candidate, anchor):
                return anchor
            common = self._common_title_tokens(meaningful_titles)
            if common:
                return common
            if len(meaningful_titles) > 1 and self._looks_like_task_title(candidate):
                slug_title = self._display_title_from_slug(topic_slug)
                if self._is_meaningful_display_title(slug_title):
                    return slug_title
            return candidate
        keywords = extract_keywords(" ".join(p.text for p in passages[:12]), top_n=4)
        if keywords:
            return " / ".join(keywords[:2])
        return self._display_title_from_slug(topic_slug)

    def _common_title_tokens(self, titles: Sequence[str]) -> Optional[str]:
        token_lists = []
        for title in titles:
            tokens = [
                t for t in re.findall(r"[A-Za-z][A-Za-z0-9.+_-]{1,}|[\u4e00-\u9fff]{2,16}", title)
                if len(t) > 1 and not self._is_generic_topic_token(t) and not self._is_fragment_topic_token(t, title)
            ]
            if tokens:
                token_lists.append(tokens)
        if not token_lists:
            return None
        common = set(token_lists[0])
        for tokens in token_lists[1:]:
            common &= set(tokens)
        if not common:
            return None
        ordered = [token for token in token_lists[0] if token in common]
        if not ordered:
            return None
        return " ".join(ordered[:4])

    def _looks_like_task_title(self, title: str) -> bool:
        title = (title or "").strip()
        if not title:
            return False
        return bool(re.search(r"(?i)(怎么|如何|安装|配置|使用|报错|解决|说明|教程|步骤|指南|问答)", title))

    def _should_prefer_topic_anchor(self, title: str, anchor: str) -> bool:
        title = self._clean_display_title(title)
        anchor = (anchor or "").strip()
        if not title or not anchor or anchor == title:
            return False
        if re.search(r"[A-Za-z0-9]", anchor):
            return True
        if self._looks_like_task_title(title):
            return True
        return bool(re.search(r"(推荐|建议|指南|解析|分析|计算|查询|验证|背景介绍|问题排查|代码示例|工具)", title))

    def _display_title_from_slug(self, topic_slug: str) -> str:
        text = (topic_slug or "").replace("-", " ").replace("_", " ").strip()
        if not text:
            return "Untitled"
        if re.search(r"[A-Za-z]", text) and not re.search(r"[\u4e00-\u9fff]", text):
            return " ".join(part.capitalize() for part in text.split())
        return text

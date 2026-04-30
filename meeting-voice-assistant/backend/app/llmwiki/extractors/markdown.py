"""Markdown 抽取器"""
import re
from pathlib import Path
from typing import List, Optional

from ..models import NormalizedSection, SectionKind, generate_id
from .base import BaseExtractor, ExtractionResult
from . import register_extractor


@register_extractor
class MarkdownExtractor(BaseExtractor):
    """Markdown 文件抽取器"""

    VERSION = "1.0"

    # Markdown 标题级别
    HEADING_PATTERN = re.compile(r'^(#{1,6})\s+(.+)$')

    @staticmethod
    def supports(file_path: str) -> bool:
        return Path(file_path).suffix.lower() in (".md", ".markdown")

    def extract(self, file_path: str) -> ExtractionResult:
        """抽取 Markdown 文件内容"""
        try:
            path = Path(file_path)
            with open(path, encoding="utf-8") as f:
                lines = f.readlines()

            sections = self._parse_lines(lines)
            return ExtractionResult(sections=sections, status="success")
        except Exception as e:
            return ExtractionResult(sections=[], status="error", error=str(e))

    def _parse_lines(self, lines: List[str]) -> List[NormalizedSection]:
        """解析 Markdown 行，提取章节"""
        sections = []
        heading_path = []
        current_section_lines = []
        current_heading = None
        section_start_line = 0

        def flush_paragraph(lines_list: List[str], start: int, title: Optional[str], path: List[str]) -> Optional[NormalizedSection]:
            text = "".join(lines_list).strip()
            if not text:
                return None
            # 找到结束行（去除已处理的标题行）
            end = start + len(lines_list) - 1
            return NormalizedSection(
                section_id=generate_id(),
                source_id="",
                kind=SectionKind.PARAGRAPH.value if not title else SectionKind.HEADING.value,
                title=title,
                text=text,
                locator={
                    "kind": "lines",
                    "start": start,
                    "end": end,
                    "heading_path": path.copy()
                },
                order_index=len(sections)
            )

        for i, line in enumerate(lines):
            line_num = i + 1
            heading_match = self.HEADING_PATTERN.match(line.rstrip())

            if heading_match:
                # 先flush之前的段落
                if current_section_lines:
                    section = flush_paragraph(current_section_lines, section_start_line, current_heading, heading_path[:-1] if heading_path else [])
                    if section:
                        sections.append(section)
                    current_section_lines = []

                level = len(heading_match.group(1))
                heading_text = heading_match.group(2).strip()

                # 更新 heading_path
                while len(heading_path) >= level:
                    heading_path.pop()
                if heading_text:
                    heading_path.append(heading_text)

                current_heading = heading_text
                section_start_line = line_num
                current_section_lines = [line]
            else:
                current_section_lines.append(line)

        # flush 最后一个段落
        if current_section_lines:
            section = flush_paragraph(current_section_lines, section_start_line, current_heading, heading_path if heading_path else [])
            if section:
                sections.append(section)

        return sections

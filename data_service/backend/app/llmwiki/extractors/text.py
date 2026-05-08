"""纯文本抽取器"""
from pathlib import Path
from typing import List

from ..models import NormalizedSection, SectionKind, generate_id
from .base import BaseExtractor, ExtractionResult
from . import register_extractor


@register_extractor
class TextExtractor(BaseExtractor):
    """纯文本文件抽取器"""

    VERSION = "1.0"

    @staticmethod
    def supports(file_path: str) -> bool:
        return Path(file_path).suffix.lower() in (".txt", ".text")

    def extract(self, file_path: str) -> ExtractionResult:
        """抽取纯文本文件"""
        try:
            path = Path(file_path)
            with open(path, encoding="utf-8") as f:
                content = f.read()

            # 按段落分割
            paragraphs = self._split_paragraphs(content)
            sections = []

            for i, para in enumerate(paragraphs):
                if para.strip():
                    sections.append(NormalizedSection(
                        section_id=generate_id(),
                        source_id="",
                        kind=SectionKind.PARAGRAPH.value,
                        text=para.strip(),
                        locator={
                            "kind": "lines",
                            "start": i + 1,
                            "end": i + 1
                        },
                        order_index=i
                    ))

            return ExtractionResult(sections=sections, status="success")
        except Exception as e:
            return ExtractionResult(sections=[], status="error", error=str(e))
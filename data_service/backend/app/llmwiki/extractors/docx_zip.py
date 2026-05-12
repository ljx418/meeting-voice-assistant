"""DOCX extractor using the Open XML package directly."""

import re
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import List

from ..models import NormalizedSection, SectionKind, generate_id
from .base import BaseExtractor, ExtractionResult
from . import register_extractor


@register_extractor
class DocxExtractor(BaseExtractor):
    """Extract paragraphs from DOCX files without an external runtime dependency."""

    VERSION = "1.0"

    NS = {
        "w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main",
    }

    @staticmethod
    def supports(file_path: str) -> bool:
        return Path(file_path).suffix.lower() == ".docx"

    def extract(self, file_path: str) -> ExtractionResult:
        try:
            path = Path(file_path)
            with zipfile.ZipFile(path, "r") as zf:
                document_xml = zf.read("word/document.xml")
            sections = self._parse_document(document_xml)
            return ExtractionResult(sections=sections, status="success")
        except KeyError:
            return ExtractionResult(sections=[], status="error", error="DOCX missing word/document.xml")
        except Exception as exc:
            return ExtractionResult(sections=[], status="error", error=str(exc))

    def _parse_document(self, document_xml: bytes) -> List[NormalizedSection]:
        root = ET.fromstring(document_xml)
        sections: List[NormalizedSection] = []
        for index, paragraph in enumerate(root.findall(".//w:p", self.NS), start=1):
            text = self._paragraph_text(paragraph)
            if not text:
                continue
            title = text if self._looks_like_heading(paragraph, text) else None
            sections.append(
                NormalizedSection(
                    section_id=generate_id(),
                    source_id="",
                    kind=SectionKind.HEADING.value if title else SectionKind.PARAGRAPH.value,
                    title=title,
                    text=text,
                    locator={"kind": "docx_paragraph", "paragraph": index},
                    order_index=len(sections),
                )
            )
        return sections

    def _paragraph_text(self, paragraph: ET.Element) -> str:
        parts = []
        for text_node in paragraph.findall(".//w:t", self.NS):
            if text_node.text:
                parts.append(text_node.text)
        return re.sub(r"\s+", " ", "".join(parts)).strip()

    def _looks_like_heading(self, paragraph: ET.Element, text: str) -> bool:
        style = paragraph.find(".//w:pStyle", self.NS)
        style_value = ""
        if style is not None:
            style_value = str(style.attrib.get(f"{{{self.NS['w']}}}val") or "").lower()
        return style_value.startswith("heading") or (len(text) <= 80 and text.endswith(("方案", "计划", "总结", "规范")))

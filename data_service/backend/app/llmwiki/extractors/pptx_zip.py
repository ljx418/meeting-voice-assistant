"""PPTX 抽取器 (使用 zipfile + xml.etree.ElementTree)"""
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import List, Optional, Tuple

from ..models import NormalizedSection, SectionKind, generate_id
from .base import BaseExtractor, ExtractionResult
from . import register_extractor


@register_extractor
class PptxExtractor(BaseExtractor):
    """PPTX 文件抽取器"""

    VERSION = "1.0"

    # 命名空间
    NS = {
        "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
        "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
        "p": "http://schemas.openxmlformats.org/presentationml/2006/main",
    }

    @staticmethod
    def supports(file_path: str) -> bool:
        return Path(file_path).suffix.lower() == ".pptx"

    def extract(self, file_path: str) -> ExtractionResult:
        """抽取 PPTX 文件内容"""
        try:
            path = Path(file_path)
            sections = []

            with zipfile.ZipFile(path, "r") as zf:
                # 获取所有幻灯片文件
                slide_files = sorted([
                    name for name in zf.namelist()
                    if name.startswith("ppt/slides/slide") and name.endswith(".xml")
                ])

                for slide_path in slide_files:
                    slide_num = int(slide_path.split("slide")[-1].replace(".xml", ""))
                    slide_content = zf.read(slide_path)

                    # 解析幻灯片
                    slide_data = self._parse_slide(slide_content, slide_num)
                    if slide_data:
                        sections.append(slide_data)

            return ExtractionResult(sections=sections, status="success")
        except Exception as e:
            return ExtractionResult(sections=[], status="error", error=str(e))

    def _parse_slide(self, slide_xml: bytes, slide_num: int) -> Optional[NormalizedSection]:
        """解析单个幻灯片"""
        try:
            root = ET.fromstring(slide_xml)

            # 提取标题
            title = self._extract_title(root)

            # 提取正文内容
            body_parts = self._extract_body(root)

            # 提取备注
            notes = self._extract_notes(slide_num)

            # 构建文本
            text_parts = []
            if body_parts:
                text_parts.extend(body_parts)
            if notes:
                text_parts.append(f"[Notes]: {notes}")

            if not text_parts:
                return None

            text = "\n".join(text_parts)

            return NormalizedSection(
                section_id=generate_id(),
                source_id="",
                kind=SectionKind.SLIDE.value,
                title=title or f"Slide {slide_num}",
                text=text,
                locator={
                    "kind": "slide",
                    "slide": slide_num
                },
                order_index=slide_num,
                meta_json={"title": title, "notes": notes}
            )
        except Exception:
            return None

    def _extract_title(self, root: ET.Element) -> Optional[str]:
        """提取标题"""
        # 查找标题形状
        for shape in root.iter("{http://schemas.openxmlformats.org/presentationml/2006/main}sp"):
            # 检查是否是标题
            for nvsp in shape.iter("{http://schemas.openxmlformats.org/presentationml/2006/main}nvsp"):
                pass
            # 查找文本
            for t in shape.iter("{http://schemas.openxmlformats.org/drawingml/2006/main}t"):
                if t.text:
                    return t.text.strip()
        return None

    def _extract_body(self, root: ET.Element) -> List[str]:
        """提取正文内容"""
        parts = []
        current_bullet_level = 0

        for shape in root.iter("{http://schemas.openxmlformats.org/presentationml/2006/main}sp"):
            # 跳过标题形状（已单独处理）
            shape_id = shape.get("{http://schemas.openxmlformats.org/presentationml/2006/main}idx")

            for t in shape.iter("{http://schemas.openxmlformats.org/drawingml/2006/main}t"):
                if t.text and t.text.strip():
                    # 检测 bullet level
                    pPr = t.getparent().getparent() if t.getparent() is not None else None
                    if pPr is not None:
                        lvl = pPr.get("lvl")
                        if lvl:
                            current_bullet_level = int(lvl)

                    # 添加适当的缩进
                    indent = "  " * current_bullet_level
                    parts.append(f"{indent}{t.text.strip()}")

        return parts

    def _extract_notes(self, slide_num: int) -> Optional[str]:
        """提取备注（需要读取 notesSlides 文件）"""
        # notes 文件名格式: ppt/notesSlides/notesSlide1.xml
        # 注意：notes 可能不存在
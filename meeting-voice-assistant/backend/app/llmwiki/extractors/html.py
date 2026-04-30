"""HTML 抽取器"""
import re
from pathlib import Path
from typing import List, Optional

from ..models import NormalizedSection, SectionKind, generate_id
from .base import BaseExtractor, ExtractionResult
from . import register_extractor


@register_extractor
class HtmlExtractor(BaseExtractor):
    """HTML 文件抽取器"""

    VERSION = "1.0"

    # 移除脚本和样式标签及其内容
    SCRIPT_STYLE_PATTERN = re.compile(
        r'<(script|style|noscript|noembed)[^>]*>.*?</\1>',
        re.DOTALL | re.IGNORECASE
    )

    # 标题标签
    HEADING_TAGS = {"h1": 1, "h2": 2, "h3": 3, "h4": 4, "h5": 5, "h6": 6}

    @staticmethod
    def supports(file_path: str) -> bool:
        return Path(file_path).suffix.lower() in (".html", ".htm")

    def extract(self, file_path: str) -> ExtractionResult:
        """抽取 HTML 文件内容"""
        try:
            path = Path(file_path)
            with open(path, encoding="utf-8") as f:
                html_content = f.read()

            # 预处理：移除脚本和样式
            clean_html = self.SCRIPT_STYLE_PATTERN.sub("", html_content)

            # 解析文本
            text_content = self._extract_text(clean_html)

            # 生成 sections
            sections = self._create_sections(text_content)

            return ExtractionResult(sections=sections, status="success")
        except Exception as e:
            return ExtractionResult(sections=[], status="error", error=str(e))

    def _extract_text(self, html: str) -> List[dict]:
        """提取文本内容及其结构信息"""
        # 简单实现：移除 HTML 标签，保留标题结构
        text_parts = []

        # 分割处理
        current_text = []
        current_heading = None
        heading_path = []

        # 分割标签
        tag_pattern = re.compile(r'<(/?)(\w+)[^>]*>', re.IGNORECASE)

        lines = html.split('\n')
        for line in lines:
            line = line.strip()
            if not line:
                continue

            # 检查是否包含标题
            heading_match = re.match(r'<h([1-6])[^>]*>(.*?)</h\1>', line, re.IGNORECASE | re.DOTALL)
            if heading_match:
                level = int(heading_match.group(1))
                text = self._strip_tags(heading_match.group(2)).strip()

                # 保存之前的段落
                if current_text:
                    text_parts.append({
                        "type": "paragraph",
                        "text": " ".join(current_text),
                        "heading": current_heading,
                        "heading_path": heading_path.copy()
                    })
                    current_text = []

                # 更新 heading_path
                while len(heading_path) >= level:
                    heading_path.pop()
                if text:
                    heading_path.append(text)
                    current_heading = text

                text_parts.append({
                    "type": f"h{level}",
                    "text": text,
                    "level": level,
                    "heading_path": heading_path.copy()
                })
            else:
                # 提取文本
                text = self._strip_tags(line).strip()
                if text:
                    current_text.append(text)

        # 保存最后一段
        if current_text:
            text_parts.append({
                "type": "paragraph",
                "text": " ".join(current_text),
                "heading": current_heading,
                "heading_path": heading_path.copy()
            })

        return text_parts

    def _strip_tags(self, html: str) -> str:
        """移除 HTML 标签"""
        return re.sub(r'<[^>]+>', '', html).strip()

    def _create_sections(self, text_parts: List[dict]) -> List[NormalizedSection]:
        """从解析结果创建 sections"""
        sections = []
        order_index = 0

        for part in text_parts:
            text = part.get("text", "").strip()
            if not text:
                continue

            kind = Section
"""CSV 文件抽取器"""
import csv
from io import StringIO
from pathlib import Path
from typing import List

from ..models import NormalizedSection, SectionKind, generate_id
from .base import BaseExtractor, ExtractionResult
from . import register_extractor


@register_extractor
class CsvExtractor(BaseExtractor):
    """CSV 文件抽取器"""

    VERSION = "1.0"

    @staticmethod
    def supports(file_path: str) -> bool:
        return Path(file_path).suffix.lower() == ".csv"

    def extract(self, file_path: str) -> ExtractionResult:
        """抽取 CSV 文件内容"""
        try:
            path = Path(file_path)
            with open(path, encoding="utf-8") as f:
                content = f.read()

            sections = self._parse_csv(content)
            return ExtractionResult(sections=sections, status="success")
        except Exception as e:
            return ExtractionResult(sections=[], status="error", error=str(e))

    def _parse_csv(self, content: str) -> List[NormalizedSection]:
        """解析 CSV 内容"""
        sections = []
        reader = csv.reader(StringIO(content))
        rows = list(reader)

        if not rows:
            return sections

        # 第一行作为 header
        headers = rows[0] if rows else []

        # 创建表头 section
        if headers:
            sections.append(NormalizedSection(
                section_id=generate_id(),
                source_id="",
                kind=SectionKind.TABLE.value,
                title="CSV Header",
                text=", ".join(headers),
                locator={
                    "kind": "row_range",
                    "start": 1,
                    "end": 1
                },
                order_index=len(sections)
            ))

        # 数据行按批次处理
        data_rows = rows[1:]
        batch_size = 100  # 每 100 行为一个 section

        for batch_start in range(0, len(data_rows), batch_size):
            batch_end = min(batch_start + batch_size, len(data_rows))
            batch = data_rows[batch_start:batch_end]

            # 将行转换为文本
            row_texts = []
            for row in batch:
                row_texts.append(", ".join(row))

            section_text = "\n".join(row_texts)

            sections.append(NormalizedSection(
                section_id=generate_id(),
                source_id="",
                kind=SectionKind.TABLE.value,
                title=f"Rows {batch_start + 2}-{batch_end + 1}",
                text=section_text,
                locator={
                    "kind": "row_range",
                    "start": batch_start + 2,  # +2 because header is row 1, data starts at row 2
                    "end": batch_end + 1
                },
                order_index=len(sections)
            ))

        return sections

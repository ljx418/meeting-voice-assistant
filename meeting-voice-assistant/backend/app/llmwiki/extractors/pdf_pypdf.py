"""PDF 抽取器 (使用 pypdf)"""
from pathlib import Path

from ..models import NormalizedSection, SectionKind, generate_id
from .base import BaseExtractor, ExtractionResult
from . import register_extractor


@register_extractor
class PdfPypdfExtractor(BaseExtractor):
    """使用 pypdf 提取数字型 PDF 文本"""

    VERSION = "1.0"

    @staticmethod
    def supports(file_path: str) -> bool:
        return Path(file_path).suffix.lower() == ".pdf"

    def extract(self, file_path: str) -> ExtractionResult:
        """抽取 PDF 文件内容"""
        try:
            import pypdf
        except ImportError:
            return ExtractionResult(
                sections=[],
                status="error",
                error="pypdf not installed. Install with: pip install pypdf"
            )

        try:
            path = Path(file_path)
            reader = pypdf.PdfReader(path)

            if reader.is_encrypted:
                try:
                    reader.decrypt("")
                except Exception:
                    return ExtractionResult(
                        sections=[],
                        status="error",
                        error="PDF is encrypted and cannot be decrypted"
                    )

            sections = []
            for page_num, page in enumerate(reader.pages):
                text = page.extract_text()

                if text and text.strip():
                    sections.append(NormalizedSection(
                        section_id=generate_id(),
                        source_id="",
                        kind=SectionKind.PARAGRAPH.value,
                        title=f"Page {page_num + 1}",
                        text=text.strip(),
                        locator={
                            "kind": "pdf_page",
                            "page": page_num + 1
                        },
                        order_index=page_num
                    ))

            if not sections:
                return ExtractionResult(
                    sections=[],
                    status="unsupported",
                    error="SCANNED_OR_UNSUPPORTED_PDF: No extractable text found. This appears to be a scanned PDF."
                )

            return ExtractionResult(sections=sections, status="success")
        except Exception as e:
            return ExtractionResult(sections=[], status="error", error=str(e))

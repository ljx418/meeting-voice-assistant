"""Legacy PPT 抽取器"""
import subprocess
import tempfile
from pathlib import Path
from typing import Optional

from ..models import NormalizedSection, generate_id
from .base import BaseExtractor, ExtractionResult
from . import register_extractor


@register_extractor
class PptLegacyExtractor(BaseExtractor):
    """Legacy .ppt 文件抽取器（通过 soffice 转换）"""

    VERSION = "1.0"

    # 状态常量
    UNSUPPORTED_LEGACY_PPT = "UNSUPPORTED_LEGACY_PPT"

    @staticmethod
    def supports(file_path: str) -> bool:
        return Path(file_path).suffix.lower() == ".ppt"

    def extract(self, file_path: str) -> ExtractionResult:
        """尝试转换并提取 .ppt 文件"""
        # 检查 soffice 是否可用
        soffice_path = self._find_soffice()
        if not soffice_path:
            return ExtractionResult(
                sections=[],
                status="unsupported",
                error=f"{self.UNSUPPORTED_LEGACY_PPT}: LibreOffice (soffice) not found. Cannot convert .ppt to .pptx."
            )

        try:
            # 创建临时目录
            with tempfile.TemporaryDirectory() as tmpdir:
                input_path = Path(file_path)
                output_pptx = Path(tmpdir) / f"{input_path.stem}.pptx"

                # 转换命令
                cmd = [
                    str(soffice_path),
                    "--headless",
                    "--convert-to", "pptx",
                    "--outdir", tmpdir,
                    str(input_path.absolute())
                ]

                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=60
                )

                if result.returncode != 0:
                    return ExtractionResult(
                        sections=[],
                        status="error",
                        error=f"soffice conversion failed: {result.stderr}"
                    )

                # 检查输出文件
                if not output_pptx.exists():
                    return ExtractionResult(
                        sections=[],
                        status="error",
                        error=f"soffice did not produce expected output: {output_pptx}"
                    )

                # 使用 pptx 抽取器处理
                from .pptx_zip import PptxExtractor
                return PptxExtractor().extract(str(output_pptx))

        except subprocess.TimeoutExpired:
            return ExtractionResult(
                sections=[],
                status="error",
                error=f"{self.UNSUPPORTED_LEGACY_PPT}: soffice conversion timed out"
            )
        except Exception as e:
            return ExtractionResult(
                sections=[],
                status="error",
                error=str(e)
            )

    def _find_soffice(self) -> Optional[Path]:
        """查找 soffice 可执行文件"""
        import shutil

        # 检查常见路径
        common_paths = [
            "/Applications/LibreOffice.app/Contents/MacOS/soffice",
            "/usr/bin/soffice",
            "/usr/local/bin/soffice",
        ]

        for path in common_paths:
            if Path(path).exists():
                return Path(path)

        # 使用 shutil.which
        soffice = shutil.which("soffice")
        if soffice:
            return Path(soffice)

        return None

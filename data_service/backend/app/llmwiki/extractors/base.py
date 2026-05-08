"""抽取器基类"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Optional, List

if TYPE_CHECKING:
    from ..models import NormalizedSection


@dataclass
class ExtractionResult:
    """抽取结果"""
    sections: List["NormalizedSection"] = field(default_factory=list)
    status: str = "success"  # "success" | "unsupported" | "error"
    error: Optional[str] = None


class BaseExtractor(ABC):
    """抽取器基类"""

    VERSION = "1.0"

    @abstractmethod
    def extract(self, file_path: str) -> ExtractionResult:
        """抽取文件内容"""
        pass

    @staticmethod
    def supports(file_path: str) -> bool:
        """检查是否支持该文件"""
        return False

    def get_version(self) -> str:
        """获取抽取器版本"""
        return self.VERSION

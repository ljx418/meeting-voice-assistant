"""LLMWiki 抽取器"""
from .base import BaseExtractor, ExtractionResult

# 导出所有抽取器
EXTRACTORS = {}


def register_extractor(extractor_class):
    """注册抽取器"""
    EXTRACTORS[extractor_class.__name__] = extractor_class
    return extractor_class


def get_extractor(file_path: str):
    """根据文件路径获取合适的抽取器"""
    for extractor_class in EXTRACTORS.values():
        if extractor_class.supports(file_path):
            return extractor_class()
    return None


def _register_all_extractors():
    """自动注册所有抽取器"""
    # 导入所有抽取器模块以触发 @register_extractor 装饰器
    from . import markdown, text, html, csvfile, jsonfile, yamlfile, docx_zip, pdf_pypdf, pptx_zip, ppt_legacy


# 立即注册所有抽取器
_register_all_extractors()


__all__ = ["BaseExtractor", "ExtractionResult", "register_extractor", "get_extractor", "EXTRACTORS"]

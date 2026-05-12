"""YAML file extractor."""

from pathlib import Path
from typing import Any, Dict, List

import yaml

from ..models import NormalizedSection, SectionKind, generate_id
from .base import BaseExtractor, ExtractionResult
from . import register_extractor


@register_extractor
class YamlExtractor(BaseExtractor):
    """Extract structured YAML leaves as normalized sections."""

    VERSION = "1.0"

    @staticmethod
    def supports(file_path: str) -> bool:
        return Path(file_path).suffix.lower() in {".yaml", ".yml"}

    def extract(self, file_path: str) -> ExtractionResult:
        try:
            path = Path(file_path)
            with open(path, encoding="utf-8") as handle:
                data = yaml.safe_load(handle)
            sections = self._parse_node(data, path.stem)
            for index, section in enumerate(sections):
                section.order_index = index
            return ExtractionResult(sections=sections, status="success")
        except yaml.YAMLError as exc:
            return ExtractionResult(sections=[], status="error", error=f"Invalid YAML: {exc}")
        except Exception as exc:
            return ExtractionResult(sections=[], status="error", error=str(exc))

    def _parse_node(self, node: Any, path: str) -> List[NormalizedSection]:
        if isinstance(node, dict):
            return self._parse_dict(node, path)
        if isinstance(node, list):
            return self._parse_list(node, path)
        if node is None:
            return []
        return [self._section(path, str(node), path)]

    def _parse_dict(self, node: Dict[Any, Any], parent: str) -> List[NormalizedSection]:
        sections: List[NormalizedSection] = []
        for key, value in node.items():
            key_text = str(key)
            child_path = f"{parent}.{key_text}" if parent else key_text
            if isinstance(value, (dict, list)):
                sections.extend(self._parse_node(value, child_path))
            elif value is not None:
                sections.append(self._section(key_text, str(value), child_path))
        return sections

    def _parse_list(self, node: List[Any], parent: str) -> List[NormalizedSection]:
        sections: List[NormalizedSection] = []
        for index, value in enumerate(node):
            child_path = f"{parent}[{index}]"
            if isinstance(value, (dict, list)):
                sections.extend(self._parse_node(value, child_path))
            elif value is not None:
                sections.append(self._section(parent, str(value), child_path))
        return sections

    def _section(self, title: str, text: str, path: str) -> NormalizedSection:
        return NormalizedSection(
            section_id=generate_id(),
            source_id="",
            kind=SectionKind.PARAGRAPH.value,
            title=title,
            text=text,
            locator={"kind": "yaml_path", "path": path},
            order_index=0,
        )

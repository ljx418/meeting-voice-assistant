from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any

@dataclass
class CallToolResult:
    content: list = field(default_factory=list)
    isError: bool = False

@dataclass
class ReadResourceResult:
    contents: list = field(default_factory=list)

__all__ = ["CallToolResult", "ReadResourceResult"]

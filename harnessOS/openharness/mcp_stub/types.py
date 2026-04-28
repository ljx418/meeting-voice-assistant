"""Stub for mcp.types module."""
from dataclasses import dataclass
from typing import Any, List, Optional

@dataclass
class TextContent:
    type: str = "text"
    text: str = ""

@dataclass
class ImageContent:
    type: str = "image"
    data: str = ""
    mimeType: str = "image/png"

@dataclass
class CallToolResult:
    content: List[Any] = None
    structuredContent: Optional[dict] = None

@dataclass
class ReadResourceResult:
    contents: List[Any] = None

@dataclass
class Resource:
    uri: str = ""
    name: Optional[str] = None
    description: Optional[str] = ""
    mimeType: Optional[str] = None

@dataclass
class ResourceTemplate:
    uriTemplate: str = ""
    name: Optional[str] = None
    description: Optional[str] = ""
    mimeType: Optional[str] = None

@dataclass
class Tool:
    name: str = ""
    description: str = ""
    inputSchema: dict = None

__all__ = [
    "TextContent",
    "ImageContent",
    "CallToolResult",
    "ReadResourceResult",
    "Resource",
    "ResourceTemplate",
    "Tool",
]

"""
Base tool implementations for harnessOS.
"""

from abc import ABC, abstractmethod
from typing import Any, TypeVar

T = TypeVar("T", bound=Any)


class BaseTool(ABC):
    """Base class for harnessOS tools."""

    name: str = ""
    description: str = ""

    @abstractmethod
    def execute(self, **kwargs) -> str:
        """Execute the tool with given arguments.

        Returns:
            String result of tool execution
        """
        pass

    def __repr__(self) -> str:
        return f"<Tool: {self.name}>"

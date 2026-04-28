"""
Output renderer for CLI responses.
"""

from typing import Any


def render_response(response: dict[str, Any]) -> None:
    """Render agent response to console."""
    status = response.get("status", "unknown")
    content = response.get("content", "")

    if status == "success":
        print(f"\n[OK] {content}")
    elif status == "error":
        print(f"\n[ERROR] {content}")
    else:
        print(f"\n[{status.upper()}] {content}")


def render_tool_call(tool_name: str, args: dict[str, Any]) -> None:
    """Render tool call indication."""
    print(f"\n[Calling tool: {tool_name}]")
    for key, value in args.items():
        if len(str(value)) > 100:
            print(f"  {key}: {str(value)[:100]}...")
        else:
            print(f"  {key}: {value}")


def render_streaming_chunk(chunk: str) -> None:
    """Render streaming response chunk."""
    print(chunk, end="", flush=True)

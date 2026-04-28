#!/usr/bin/env python3
"""Direct test of OpenHarness agent flow without TUI."""

import os
import sys
import asyncio

# Setup paths
_project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _project_root)
_openharness_src = os.path.join(_project_root, "examples", "open-harness", "src")
sys.path.insert(0, _openharness_src)

# Map mcp stub
_mcp_stub_parent = os.path.join(_project_root, "openharness")
if _mcp_stub_parent not in sys.path:
    sys.path.insert(0, _mcp_stub_parent)
import mcp_stub
sys.modules['mcp'] = mcp_stub

# Load .env
from dotenv import load_dotenv
load_dotenv(os.path.join(_project_root, ".env"))

async def test_agent_flow():
    """Test the full agent flow with handle_line."""
    from openharness.ui.runtime import build_runtime, start_runtime, handle_line

    print("=" * 60)
    print("OpenHarness Full Agent Flow Test")
    print("=" * 60)
    print(f"MODEL: {os.getenv('OPENHARNESS_MODEL')}")
    print(f"BASE_URL: {os.getenv('OPENHARNESS_BASE_URL')}")
    print()

    # Build runtime bundle
    bundle = await build_runtime(
        cwd=_project_root,
        model=os.getenv("OPENHARNESS_MODEL"),
        base_url=os.getenv("OPENHARNESS_BASE_URL"),
        api_key=os.getenv("ANTHROPIC_API_KEY"),
    )
    await start_runtime(bundle)
    print(f"Runtime started. Session: {bundle.session_id[:8]}...")

    # Collect events
    events_received = []

    async def print_system(message: str):
        print(f"[SYSTEM] {message}")

    async def render_event(event):
        events_received.append(event)
        event_type = type(event).__name__
        if hasattr(event, 'text'):
            print(f"[EVENT] {event_type}: {event.text[:100]}...")
        else:
            print(f"[EVENT] {event_type}")

    async def clear_output():
        pass

    # Send a test message
    print("\n" + "-" * 60)
    print("Sending: 你好")
    print("-" * 60)

    should_continue = await handle_line(
        bundle,
        "你好",
        print_system=print_system,
        render_event=render_event,
        clear_output=clear_output,
    )

    print("\n" + "=" * 60)
    print(f"handle_line returned: {should_continue}")
    print(f"Total events received: {len(events_received)}")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(test_agent_flow())
#!/usr/bin/env python3
"""Debug TUI flow - replicate exactly what TUI does."""

import os
import sys

_project_root = '/Users/Zhuanz/Desktop/workspace/harnessOS'
sys.path.insert(0, _project_root)

# Setup like cli/main.py does
_openharness_src = os.path.join(_project_root, "examples", "open-harness", "src")
sys.path.insert(0, _openharness_src)

# Add mcp_stub parent to path so we can import mcp_stub
sys.path.insert(0, os.path.join(_project_root, 'openharness'))

# Load .env
from dotenv import load_dotenv
load_dotenv(os.path.join(_project_root, ".env"))

# Map mcp to stub
import mcp_stub
sys.modules['mcp'] = mcp_stub

# Now import openharness and map it
import openharness
sys.modules['harnessOS.openharness'] = openharness

async def debug_tui_flow():
    print("=" * 60)
    print("Debug TUI Flow")
    print("=" * 60)

    model = os.getenv('OPENHARNESS_MODEL')
    base_url = os.getenv('OPENHARNESS_BASE_URL')
    api_key = os.getenv('ANTHROPIC_API_KEY')

    print(f"Config:")
    print(f"  model: {model}")
    print(f"  base_url: {base_url}")
    print(f"  api_key: {api_key[:20]}..." if api_key else "  api_key: None")

    # Build runtime like on_mount does
    from openharness.ui.runtime import build_runtime, start_runtime

    bundle = await build_runtime(
        cwd=_project_root,
        model=model,
        base_url=base_url,
        api_key=api_key,
    )
    await start_runtime(bundle)

    print(f"\nBundle created:")
    print(f"  engine._api_client: {bundle.engine._api_client}")
    print(f"  engine._api_client type: {type(bundle.engine._api_client)}")
    print(f"  engine._model: {bundle.engine._model}")

    # Check the api_client's base_url
    api_client = bundle.engine._api_client
    if hasattr(api_client, 'base_url'):
        print(f"  api_client.base_url: {api_client.base_url}")
    elif hasattr(api_client, '_base_url'):
        print(f"  api_client._base_url: {api_client._base_url}")
    else:
        attrs = [a for a in dir(api_client) if 'url' in a.lower() or 'base' in a.lower()]
        print(f"  api_client URL-related attrs: {attrs}")

    # Now simulate what _process_line does
    from openharness.ui.runtime import handle_line

    events = []
    async def render_event(event):
        events.append(event)
        print(f"  [RENDER_EVENT] {type(event).__name__}")
        if hasattr(event, 'text'):
            print(f"    text: {event.text[:80]}...")

    async def print_system(msg):
        print(f"  [SYSTEM] {msg}")

    async def clear_output():
        pass

    print(f"\nCalling handle_line with '你好'...")
    result = await handle_line(
        bundle,
        "你好",
        print_system=print_system,
        render_event=render_event,
        clear_output=clear_output,
    )

    print(f"\nhandle_line returned: {result}")
    print(f"Events received: {len(events)}")

    if not events:
        print("\n!!! No events received - this is the bug !!!")
        print("Let me check the engine directly...")

        # Check if engine.submit_message works directly
        print("\nDirect engine.submit_message test:")
        count = 0
        async for event in bundle.engine.submit_message("你好"):
            count += 1
            print(f"  [DIRECT] {type(event).__name__}")
            if count > 5:
                print("  ...")
                break
        if count == 0:
            print("  NO EVENTS AT ALL!")

if __name__ == "__main__":
    import asyncio
    asyncio.run(debug_tui_flow())
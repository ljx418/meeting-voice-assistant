#!/usr/bin/env python3
"""Direct test of OpenHarness agent without TUI."""

import os
import sys
import asyncio

# Setup paths
_project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _project_root)
_openharness_src = os.path.join(_project_root, "examples", "open-harness", "src")
sys.path.insert(0, _openharness_src)

# Load .env
from dotenv import load_dotenv
load_dotenv(os.path.join(_project_root, ".env"))

async def test_api():
    """Test the API client."""
    print("=" * 50)
    print("OpenHarness Agent Test")
    print("=" * 50)
    print(f"API_KEY: {os.getenv('ANTHROPIC_API_KEY', '')[:20]}...")
    print(f"MODEL: {os.getenv('OPENHARNESS_MODEL')}")
    print(f"FORMAT: {os.getenv('OPENHARNESS_API_FORMAT')}")
    print(f"BASE_URL: {os.getenv('OPENHARNESS_BASE_URL')}")
    print()

    from openharness.api.client import AsyncAnthropic

    client = AsyncAnthropic()
    print(f"Client created: {client}")

    # Simple test message
    messages = [{"role": "user", "content": "Hello, respond briefly."}]
    response = await client.messages.create(
        model=os.getenv("OPENHARNESS_MODEL", "MiniMax-M2.7"),
        messages=messages,
        max_tokens=100
    )
    print(f"\nResponse received:")
    print(f"  Model: {response.model}")

    # Handle different content types
    for block in response.content:
        if hasattr(block, 'text'):
            print(f"  Text: {block.text[:200]}")
        elif hasattr(block, 'thinking'):
            print(f"  Thinking: {block.thinking[:100]}...")

if __name__ == "__main__":
    asyncio.run(test_api())
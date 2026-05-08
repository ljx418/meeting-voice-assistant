"""Quick startup test - mimics python -m harnessOS.cli.main --oh without TUI."""
import sys, os

_project_root = os.path.dirname(os.path.abspath(__file__))
_workspace_root = os.path.dirname(_project_root)
# Need workspace parent so that "harnessOS" is importable as a package
sys.path.insert(0, _workspace_root)
sys.path.insert(0, _project_root)

# Load .env
_dotenv_path = os.path.join(_project_root, ".env")
if os.path.isfile(_dotenv_path):
    from dotenv import load_dotenv
    load_dotenv(_dotenv_path)
_openharness_src = os.path.join(_project_root, "examples", "open-harness", "src")
if _openharness_src not in sys.path:
    sys.path.insert(0, _openharness_src)

import openharness as _oh
sys.modules["harnessOS.openharness"] = _oh

print("Step 1: Testing import chain...")
try:
    from cli.tui.textual_app import OpenHarnessTerminalApp
    print("  OK - OpenHarnessTerminalApp imported")
except Exception as e:
    print(f"  FAIL - {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("Step 2: Testing build_runtime (this validates API key)...")
import asyncio

async def run_startup_check():
    from cli.tui.runtime import build_runtime

    try:
        bundle = await build_runtime(
            api_key=os.getenv("ANTHROPIC_API_KEY") or os.getenv("DEEPSEEK_API_KEY"),
            cwd=os.getcwd(),
        )
        print(f"  OK - Runtime built: model={bundle.app_state.get().model}")
        print(f"  Tools: {len(bundle.tool_registry.list_tools())} loaded")
        await bundle.mcp_manager.close()
    except SystemExit as e:
        print(f"  FAIL - SystemExit({e.code}): likely auth failure or missing API key")
        print(f"  ANTHROPIC_API_KEY={'set' if os.getenv('ANTHROPIC_API_KEY') else 'NOT SET'}")
    except Exception as e:
        print(f"  FAIL - {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()

asyncio.run(run_startup_check())
print("\nIf all pass above, the TUI is healthy. Run in Terminal.app/iTerm2 for full UI.")

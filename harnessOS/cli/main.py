"""
harnessOS CLI main entry point.
"""

import os
import sys
import warnings

warnings.filterwarnings(
    "ignore",
    message=r"urllib3 v2 only supports OpenSSL 1\.1\.1\+.*",
    category=Warning,
    module=r"urllib3(\.|$)",
)

# Add project root and open-harness src to path for imports
_project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _project_root)

# Load .env from project root before any settings resolution
_dotenv_path = os.path.join(_project_root, ".env")
if os.path.isfile(_dotenv_path):
    from dotenv import load_dotenv
    load_dotenv(_dotenv_path)
# Ensure openharness can be imported from examples/open-harness/src
_openharness_src = os.path.join(_project_root, "examples", "open-harness", "src")
if _openharness_src not in sys.path:
    sys.path.insert(0, _openharness_src)

# Add stubs for Python 3.10+ dependencies
_mcp_stub = os.path.join(_project_root, "openharness", "mcp_stub")
if _mcp_stub not in sys.path:
    sys.path.insert(0, _mcp_stub)

# Map harnessOS.openharness to the original OpenHarness source.
# This allows migrated code (cli/tui/*) to import from harnessOS.openharness.*
# while actually resolving to the complete original source in examples/.
import openharness as _oh
sys.modules["harnessOS.openharness"] = _oh


def _alias_openharness_submodules() -> None:
    """Keep migrated harnessOS.openharness imports identical to openharness.

    Some migrated TUI modules import event classes through
    ``harnessOS.openharness.*`` while the runtime imports them through
    ``openharness.*``. Without explicit submodule aliases Python loads the same
    file twice under different names, so ``isinstance`` checks fail and streamed
    assistant events are silently ignored by the renderer.
    """
    import importlib

    submodules = (
        "api.client",
        "api.openai_client",
        "config.settings",
        "engine.messages",
        "engine.query_engine",
        "engine.stream_events",
        "tasks",
        "ui.runtime",
    )
    for name in submodules:
        try:
            module = importlib.import_module(f"openharness.{name}")
        except ModuleNotFoundError:
            continue
        sys.modules[f"harnessOS.openharness.{name}"] = module


_alias_openharness_submodules()


def main():
    """Main CLI entry point."""
    argv = sys.argv[1:]
    # Check for --oh / --openharness flag to launch OpenHarness TUI
    if "--oh" in argv or "--openharness" in argv:
        # Remove the flag from argv to avoid interfering with app parsing
        sys.argv = [arg for arg in sys.argv if arg not in ("--oh", "--openharness")]
        _run_openharness_tui()
        return

    if argv and argv[0] == "run":
        raise SystemExit(_run_headless(argv[1:]))

    print("harnessOS Phase 0 Shell")
    print("=" * 40)

    # Check for an OpenAI-compatible API key. The project currently supports
    # both harnessOS-style and migrated OpenHarness-style environment names.
    api_key = (
        os.getenv("DEEPSEEK_API_KEY")
        or os.getenv("MINIMAX_API_KEY")
        or os.getenv("OPENAI_API_KEY")
        or os.getenv("OPENHARNESS_API_KEY")
        or os.getenv("ANTHROPIC_API_KEY")
    )
    if not api_key:
        print("Warning: no LLM API key set. Using mock mode.")
        print("Set DEEPSEEK_API_KEY, MINIMAX_API_KEY, OPENAI_API_KEY, or OPENHARNESS_API_KEY.")
        print()

    from cli.session import CLISession
    from cli.renderer import render_response

    session = CLISession()
    print(f"Session started: {session.session_id[:8]}...")
    print("Type 'exit' or 'quit' to end session\n")

    while True:
        try:
            user_input = input(">>> ").strip()
            if user_input.lower() in ("exit", "quit"):
                print("Ending session...")
                break
            if not user_input:
                continue

            response = session.run(user_input)
            render_response(response)
            print()

        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"Error: {e}")

    print("Goodbye!")


def _run_headless(argv: list[str]) -> int:
    """Run one prompt through the local gateway and print only assistant text."""
    import argparse
    import asyncio
    import json

    parser = argparse.ArgumentParser(
        prog="harness run",
        description="Run one harnessOS prompt without launching the TUI.",
    )
    parser.add_argument("prompt", nargs="*", help="Prompt text to submit")
    parser.add_argument("--model", help="Override model for this temporary session")
    parser.add_argument("--domain", help="Optional domain hint, e.g. meeting/interview/knowledge")
    parser.add_argument("--json", action="store_true", help="Print the full turn result as JSON")
    args = parser.parse_args(argv)

    prompt = " ".join(args.prompt).strip()
    if not prompt and not sys.stdin.isatty():
        prompt = sys.stdin.read().strip()
    if not prompt:
        parser.error("prompt is required")

    async def _run() -> tuple[int, str]:
        from apps.gateway.service import GatewayService

        service = GatewayService()
        await service.initialize({})
        session = await service.session_start({"model": args.model} if args.model else {})
        session_id = str(session["session_id"])
        try:
            result = await service.turn_start(
                {
                    "session_id": session_id,
                    "input": prompt,
                    "domain": args.domain,
                }
            )
        finally:
            await service.session_close({"session_id": session_id})

        failed_events = [
            event for event in result.get("events", [])
            if event.get("type") == "turn.failed"
        ]
        if failed_events:
            message = failed_events[-1].get("data", {}).get("message", "turn failed")
            return 1, str(message)
        if args.json:
            return 0, json.dumps(result, ensure_ascii=False, indent=2)
        return 0, str(result.get("final_text", ""))

    try:
        code, output = asyncio.run(_run())
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        return 1

    if code == 0:
        if output:
            print(output)
    else:
        print(output, file=sys.stderr)
    return code


def _run_openharness_tui():
    """Launch OpenHarness Textual TUI."""
    import traceback

    # Log any import/startup errors before TUI takes over the terminal
    try:
        from cli.tui.textual_app import OpenHarnessTerminalApp

        app = OpenHarnessTerminalApp(
            model=os.getenv("OPENHARNESS_MODEL"),
            base_url=os.getenv("OPENHARNESS_BASE_URL"),
            api_key=os.getenv("ANTHROPIC_API_KEY"),
        )
        app.run()
    except BaseException:
        # Write error to stderr and a log file so it's visible after TUI exits
        tb = traceback.format_exc()
        sys.stderr.write(f"\n[TUI ERROR]\n{tb}\n")
        sys.stderr.flush()
        # Also write to a file in case stderr is captured by the TUI
        log_path = os.path.join(_project_root, "tui_error.log")
        with open(log_path, "w") as f:
            f.write(tb)
        print(f"\nError log saved to: {log_path}")
        raise


if __name__ == "__main__":
    main()

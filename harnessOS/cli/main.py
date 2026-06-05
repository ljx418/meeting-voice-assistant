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

    if argv and argv[0] == "tui":
        raise SystemExit(_run_mission_tui(argv[1:]))

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


def _run_mission_tui(argv: list[str]) -> int:
    """Render the Mission TUI or run explicit V7/V8 local Markdown workflow paths."""
    import argparse
    import json
    from pathlib import Path

    parser = argparse.ArgumentParser(
        prog="harness tui",
        description="Render an explainable Mission TUI state or run explicit V7-3/V8 local Markdown workflow paths.",
    )
    parser.add_argument("goal", nargs="*", help="Natural-language mission goal")
    parser.add_argument("--json", action="store_true", help="Print the Mission TUI state as JSON")
    parser.add_argument("--run", action="store_true", help="Run the V7-3 supported local Markdown workflow")
    parser.add_argument("--v8-station-agent", action="store_true", help="Run the V8 station-agent local Markdown workflow pilot")
    parser.add_argument("--v8-terminal-worker", action="store_true", help="Run the V8-6 controlled terminal worker pilot")
    parser.add_argument("--v8-project-workflow", action="store_true", help="Run the V8-7 bounded multi-Agent project workflow pilot")
    parser.add_argument("--v8-agent-tui", action="store_true", help="Render the V8-8 read-only Agent explainability TUI evidence")
    parser.add_argument("--v8-final-framework", action="store_true", help="Render the V8-9 final acceptance framework without issuing final claim")
    parser.add_argument("--user-confirmed", action="store_true", help="Confirm the durable workflow or high-risk controlled worker run")
    parser.add_argument("--path", default="tests/fixtures/desktop/技术分享", help="Authorized local Markdown folder path")
    parser.add_argument("--evidence-dir", help="Output directory for V7-3 evidence package")
    args = parser.parse_args(argv)

    goal = " ".join(args.goal).strip()
    if not goal and not sys.stdin.isatty():
        goal = sys.stdin.read().strip()
    if not goal:
        parser.error("goal is required")

    try:
        if args.v8_agent_tui:
            from core.product_console.v8_agent_explainability_tui import write_v8_8_agent_explainability_evidence

            output_dir = Path(args.evidence_dir) if args.evidence_dir else None
            kwargs = {}
            if output_dir is not None:
                kwargs["output_dir"] = output_dir
            state = write_v8_8_agent_explainability_evidence(**kwargs)
            acceptance = {
                "status": state.status,
                "evidence_scope": state.evidence_scope,
                "panel_count": len(state.panels),
                "readonly": state.readonly,
            }
            if args.json:
                print(json.dumps(acceptance, ensure_ascii=False, indent=2, sort_keys=True))
            else:
                print(f"V8-8 status: {acceptance['status']}")
                print(f"evidence_scope: {acceptance['evidence_scope']}")
                print(f"panel_count: {acceptance['panel_count']}")
                print(f"readonly: {str(acceptance['readonly']).lower()}")
            return 0 if state.status == "PASS" else 2

        if args.v8_final_framework:
            from core.product_console.v8_final_acceptance import write_v8_9_final_acceptance_framework

            output_dir = Path(args.evidence_dir) if args.evidence_dir else None
            result = write_v8_9_final_acceptance_framework(output_dir) if output_dir is not None else write_v8_9_final_acceptance_framework()
            if args.json:
                print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
            else:
                print(f"V8-9 status: {result['status']}")
                print(f"final_claim_allowed: {str(result['final_claim_allowed']).lower()}")
                print(f"blockers: {len(result['blockers'])}")
            return 0 if result["status"] == "PASS" else 2

        if args.run or args.v8_station_agent or args.v8_terminal_worker or args.v8_project_workflow:
            if not args.user_confirmed:
                parser.error("--run requires --user-confirmed")
            if args.v8_project_workflow:
                from core.product_console.v8_7_multi_agent_project_workflow import (
                    V87ProjectWorkflowConfig,
                    run_v8_7_multi_agent_project_workflow,
                )

                output_dir = Path(args.evidence_dir) if args.evidence_dir else None
                config_kwargs = {
                    "goal": goal,
                    "user_confirmed": True,
                }
                if output_dir is not None:
                    config_kwargs["evidence_dir"] = output_dir
                result = run_v8_7_multi_agent_project_workflow(V87ProjectWorkflowConfig(**config_kwargs))
                if args.json:
                    print(json.dumps(result["acceptance"], ensure_ascii=False, indent=2, sort_keys=True))
                else:
                    print(f"V8-7 status: {result['acceptance']['status']}")
                    print(f"evidence_scope: {result['acceptance']['evidence_scope']}")
                    print(f"station_count: {result['acceptance']['station_count']}")
                    print(f"agent_descriptor_count: {result['acceptance']['agent_descriptor_count']}")
                    print(f"implementation_agent_uses_handoff_not_direct_shell: {result['acceptance']['implementation_agent_uses_handoff_not_direct_shell']}")
                    print(f"source_agent_mutation_denied: {result['acceptance']['source_agent_mutation_denied']}")
                return 0 if result["acceptance"]["status"] == "PASS" else 2

            if args.v8_terminal_worker:
                from core.terminal_workers import V86ControlledTerminalWorkerConfig, run_v8_6_controlled_terminal_worker_pilot

                output_dir = Path(args.evidence_dir) if args.evidence_dir else None
                config_kwargs = {"user_confirmed": True}
                if output_dir is not None:
                    config_kwargs["evidence_dir"] = output_dir
                result = run_v8_6_controlled_terminal_worker_pilot(V86ControlledTerminalWorkerConfig(**config_kwargs))
                if args.json:
                    print(json.dumps(result["acceptance"], ensure_ascii=False, indent=2, sort_keys=True))
                else:
                    print(f"V8-6 status: {result['acceptance']['status']}")
                    print(f"evidence_scope: {result['acceptance']['evidence_scope']}")
                    print(f"worker_type: {result['acceptance']['worker_type']}")
                    print(f"workspace_scope_guard: {result['acceptance']['workspace_scope_guard']}")
                    print(f"command_allowlist: {result['acceptance']['command_allowlist']}")
                    print(f"source_agent_mutation_denied: {result['acceptance']['source_agent_mutation_denied']}")
                return 0 if result["acceptance"]["status"] == "PASS" else 2

            if args.v8_station_agent:
                from core.product_console.v8_station_agent_workflow import V8StationAgentRunConfig, run_v8_station_agent_workflow

                output_dir = Path(args.evidence_dir) if args.evidence_dir else None
                config_kwargs = {
                    "goal": goal,
                    "requested_path": args.path,
                    "user_confirmed": True,
                }
                if output_dir is not None:
                    config_kwargs["output_dir"] = output_dir
                result = run_v8_station_agent_workflow(V8StationAgentRunConfig(**config_kwargs))
                if args.json:
                    print(json.dumps(result["acceptance"], ensure_ascii=False, indent=2, sort_keys=True))
                else:
                    print(f"V8 status: {result['acceptance']['status']}")
                    print(f"evidence_scope: {result['acceptance']['evidence_scope']}")
                    print(f"station_count: {result['acceptance']['station_count']}")
                    print(f"agent_descriptor_count: {result['acceptance']['agent_descriptor_count']}")
                    print(f"source_agent_mutation_denied: {result['acceptance']['source_agent_mutation_denied']}")
                return 0 if result["acceptance"]["status"] == "PASS" else 2

            from core.product_console.v7_3_workflow_run import V73RunConfig, run_v7_3_workflow

            output_dir = Path(args.evidence_dir) if args.evidence_dir else None
            config_kwargs = {
                "goal": goal,
                "requested_path": args.path,
                "user_confirmed": True,
            }
            if output_dir is not None:
                config_kwargs["output_dir"] = output_dir
            result = run_v7_3_workflow(V73RunConfig(**config_kwargs))
            if args.json:
                print(json.dumps(result["acceptance"], ensure_ascii=False, indent=2, sort_keys=True))
            else:
                print(f"V7-3 status: {result['acceptance']['status']}")
                print(f"evidence_scope: {result['acceptance']['evidence_scope']}")
                print(f"scanner_actual_read_count: {result['acceptance']['scanner_actual_read_count']}")
                print(f"provider_invocation_count: {result['acceptance']['provider_invocation_count']}")
            return 0 if result["acceptance"]["status"] == "PASS" else 2

        from core.product_console.v7_2_mission_tui import build_mission_tui_state, render_mission_tui_text

        state = build_mission_tui_state(goal)
        if args.json:
            print(json.dumps(state.to_dict(), ensure_ascii=False, indent=2, sort_keys=True))
        else:
            print(render_mission_tui_text(state), end="")
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        return 1
    return 0


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

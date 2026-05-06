# AGENTS.md

This project was previously developed with Claude Code. The original project
instructions are preserved in `CLAUDE.md`; agents working in this repository
must treat that file as the source of truth for coding standards, task flow,
architecture notes, and team conventions.

## Required Startup Context

1. Read `TASKS.md` before starting implementation work.
2. Read `CLAUDE.md` for project conventions and architecture constraints.
3. Prefer the architecture documents under `docs/`, especially:
   - `docs/design/V3.0/00_README.md`
   - `docs/design/V3.0/v3_development_plan_multi_app_core.md`
   - `docs/design/V3.0/v3_current_gap_analysis.md`
   - `docs/architecture/CURRENT-STATUS_v3.md`
4. Keep code comments, variable names, and commit messages in English.
5. Keep user-facing UI copy in Simplified Chinese.

## Current Development Focus

The current project direction is CLI-first backend iteration on top of a
Codex-style app-server boundary and OpenHarness-compatible runtime ideas.
For narrow development tasks, prefer extending the existing CLI/runtime path
before adding new product surfaces.

## Important Compatibility Note

The repository still contains Claude/OpenHarness naming in several files. Do
not remove those compatibility paths unless the replacement is implemented and
verified end to end.

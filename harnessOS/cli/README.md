# harnessOS CLI

Interactive shell for harnessOS Phase 0.

## Quick Start

```bash
# From project root
python3 -m cli.main

# From the workspace parent
python3 -m harnessOS.cli.main

# Or directly
python3 cli/main.py
```

## Headless Run

Use `run` when you want a plain terminal/script invocation instead of the TUI or REPL:

```bash
python3 -m harnessOS.cli.main run "你好"
python3 -m harnessOS.cli.main run --json "你好"
```

After installing the package, the console script is:

```bash
harness run "你好"
```

## Environment

Set your LLM API key:
```bash
export DEEPSEEK_API_KEY="your-key"
```

The CLI also reads OpenAI-compatible migrated settings such as
`OPENHARNESS_MODEL`, `OPENHARNESS_BASE_URL`, and `ANTHROPIC_API_KEY`.

Without an API key, the CLI runs in mock/demo mode.

## Available Tools

### Workspace Tools
- `workspace_ls(directory='.')` - List files in workspace
- `workspace_read_file(file_path='path')` - Read file contents
- `workspace_write_file(file_path='path', content='text')` - Write to file

### Knowledge Base
- `kb_search(query='text')` - Search knowledge base
- `kb_ingest(document='text')` - Add document to knowledge base

### Artifacts
- `artifact_save(name='name', content='text')` - Save output as artifact

## Exit

Type `exit` or `quit` to end the session.

"""Bridge for openharness.ui - re-exports from examples/open-harness/src/openharness/ui/."""
import sys
import os
from importlib import import_module

# Ensure examples/open-harness/src is in path BEFORE any openharness imports
_project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
_openharness_src = os.path.join(_project_root, "examples", "open-harness", "src")
_openharness_ui_src = os.path.join(_openharness_src, "openharness", "ui")
_mcp_stub = os.path.join(_project_root, "openharness", "mcp_stub")

for p in [_openharness_src, _mcp_stub]:
    if p not in sys.path:
        sys.path.insert(0, p)

if os.path.isdir(_openharness_ui_src) and _openharness_ui_src not in __path__:
    __path__.insert(0, _openharness_ui_src)

# Map 'mcp' to our stub package via sys.modules
# This must happen BEFORE openharness.ui is imported
if 'mcp' not in sys.modules:
    import mcp_stub
    sys.modules['mcp'] = mcp_stub

# Now do the imports
from openharness.ui.app import run_repl, run_print_mode
from openharness.ui import runtime
from openharness.ui import textual_app

__all__ = ["run_repl", "run_print_mode", "runtime", "textual_app"]

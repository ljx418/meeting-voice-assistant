"""Shared dotenv loading for llmwiki CLI usage."""
from pathlib import Path

from dotenv import load_dotenv


def load_llmwiki_dotenv() -> None:
    """Load project dotenv files if they exist."""

    module_dir = Path(__file__).resolve().parent
    backend_dir = module_dir.parent.parent
    candidates = [
        backend_dir / ".env",
        backend_dir / ".env.example",
        backend_dir / "app" / ".env",
        backend_dir / "app" / ".env.example",
    ]
    for candidate in candidates:
        if candidate.exists():
            load_dotenv(candidate, override=False)
